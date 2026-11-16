#!/usr/bin/env python3
"""
Executa um prompt protótipo sobre os casos de teste fictícios e registra os resultados.

- O prompt (arquivo .txt) é enviado como *system prompt*.
- A mensagem do estudante é enviada como mensagem do usuário, entre delimitadores.
- Cada caso é executado N vezes (--reps) para observar variabilidade.
- O setor responsável NÃO é decidido pelo modelo: é obtido da TABELA_ROTEAMENTO
  (funcionalidade F3 resolvida sem IA).

Execução do modelo: Claude Code CLI em modo não interativo (`claude -p`), sem ferramentas,
sem MCP e sem persistência de sessão, numa pasta temporária vazia.

Uso:
  python3 testes/rodar_testes.py --prompt prompts/v1_classificacao.txt \
      --casos testes/casos.json --reps 3 --saida resultados/basico_v1 [--ids C01,C02]
"""
import argparse
import concurrent.futures as cf
import json
import re
import subprocess
import tempfile
import time
from collections import Counter
from pathlib import Path

# F3 — encaminhamento por regra fixa (sem IA). Mantida pela secretaria.
TABELA_ROTEAMENTO = {
    "matricula": "Secretaria Acadêmica",
    "documentos": "Secretaria Acadêmica",
    "financeiro": "Tesouraria / Financeiro",
    "calendario": "Secretaria Acadêmica (FAQ/calendário oficial)",
    "notas": "Coordenação do Curso",
    "ava": "Suporte de TI",
    "administrativo": "Atendimento Geral",
    "outro": "Atendimento Geral",
    "incerto": "Fila humana de triagem",
}


def montar_mensagem(texto: str) -> str:
    return f'Mensagem do estudante:\n"""\n{texto}\n"""'


def chamar_modelo(system_prompt: str, mensagem: str, modelo: str, pasta: str) -> dict:
    cmd = [
        "claude", "-p",
        "--model", modelo,
        "--system-prompt", system_prompt,
        "--tools", "",
        "--strict-mcp-config",
        "--no-session-persistence",
        "--output-format", "json",
        montar_mensagem(mensagem),
    ]
    t0 = time.time()
    proc = subprocess.run(cmd, capture_output=True, text=True, cwd=pasta, timeout=180)
    dur = round(time.time() - t0, 1)
    try:
        dados = json.loads(proc.stdout)
        texto = dados.get("result", "")
        modelo_real = next(iter(dados.get("modelUsage", {}) or {}), modelo)
    except json.JSONDecodeError:
        texto, modelo_real = proc.stdout or proc.stderr, modelo
    return {"texto": texto, "modelo": modelo_real, "segundos": dur}


def extrair_json(texto: str):
    """Tenta extrair um objeto JSON da resposta. Retorna (obj, formato_estrito)."""
    t = texto.strip()
    try:
        return json.loads(t), True
    except json.JSONDecodeError:
        pass
    m = re.search(r"\{.*\}", t, re.S)
    if m:
        try:
            return json.loads(m.group(0)), False
        except json.JSONDecodeError:
            pass
    return None, False


def assuntos_de(obj) -> list:
    if not isinstance(obj, dict):
        return []
    if isinstance(obj.get("assuntos"), list):
        return [str(a).lower() for a in obj["assuntos"]]
    if obj.get("assunto") is not None:
        return [str(obj["assunto"]).lower()]
    return []


def avaliar(obj, estrito: bool, esperado: dict) -> dict:
    ass = assuntos_de(obj)
    prio = str(obj.get("prioridade", "")).lower() if isinstance(obj, dict) else ""
    humano = bool(obj.get("encaminhar_humano")) if isinstance(obj, dict) else False
    humano = humano or ("incerto" in ass)

    if "assuntos_todos" in esperado:
        assunto_ok = set(esperado["assuntos_todos"]).issubset(set(ass))
    else:
        assunto_ok = any(a in esperado["assuntos_aceitos"] for a in ass)

    prioridade_ok = prio in esperado.get("prioridade_aceita", [prio])
    if esperado.get("exige_humano"):
        humano_ok = humano
    else:
        humano_ok = True  # encaminhar a mais não é erro grave; registrado à parte
    return {
        "formato_ok": obj is not None and estrito,
        "json_recuperavel": obj is not None,
        "assunto_ok": assunto_ok,
        "prioridade_ok": prioridade_ok,
        "humano_ok": humano_ok,
        "humano_marcado": humano,
        "assuntos": ass,
        "prioridade": prio,
        "setor_tabela": [TABELA_ROTEAMENTO.get(a, "?? (rótulo fora da lista)") for a in ass],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--casos", default="testes/casos.json")
    ap.add_argument("--ids", default="")
    ap.add_argument("--reps", type=int, default=3)
    ap.add_argument("--modelo", default="haiku")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--saida", required=True, help="prefixo dos arquivos de saída (sem extensão)")
    args = ap.parse_args()

    system_prompt = Path(args.prompt).read_text(encoding="utf-8")
    casos = json.loads(Path(args.casos).read_text(encoding="utf-8"))
    if args.ids:
        ids = set(args.ids.split(","))
        casos = [c for c in casos if c["id"] in ids]

    pasta = tempfile.mkdtemp(prefix="p1_teste_")
    tarefas = [(c, r) for c in casos for r in range(1, args.reps + 1)]

    def rodar(item):
        caso, rep = item
        resp = chamar_modelo(system_prompt, caso["mensagem"], args.modelo, pasta)
        obj, estrito = extrair_json(resp["texto"])
        return {
            "id": caso["id"], "rep": rep, "tipo": caso["tipo"],
            "resposta_bruta": resp["texto"], "modelo": resp["modelo"],
            "segundos": resp["segundos"], "json": obj,
            "avaliacao": avaliar(obj, estrito, caso["esperado"]),
        }

    with cf.ThreadPoolExecutor(max_workers=args.workers) as ex:
        resultados = list(ex.map(rodar, tarefas))
    resultados.sort(key=lambda r: (r["id"], r["rep"]))

    saida = Path(args.saida)
    saida.parent.mkdir(parents=True, exist_ok=True)
    meta = {
        "prompt": args.prompt, "modelo_solicitado": args.modelo,
        "modelo_usado": resultados[0]["modelo"] if resultados else None,
        "reps": args.reps, "executado_em": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    saida.with_suffix(".json").write_text(
        json.dumps({"meta": meta, "resultados": resultados}, ensure_ascii=False, indent=2),
        encoding="utf-8")

    # Relatório Markdown
    linhas = [
        f"# Resultados — `{args.prompt}`", "",
        f"- Modelo: `{meta['modelo_usado']}` · Repetições por caso: {args.reps} · Executado em: {meta['executado_em']}",
        "- Avaliação automática: formato (JSON puro), assunto, prioridade, encaminhamento humano. "
        "A análise qualitativa (informação inventada, obediência a instruções embutidas etc.) está no memorando.",
        "",
        "## Resumo por caso", "",
        "| Caso | Tipo | Assunto(s) obtido(s) por repetição | Prioridade | Setor (tabela, sem IA) | Humano? | Formato | Assunto | Prior. | Humano | Consistente? |",
        "|---|---|---|---|---|---|:-:|:-:|:-:|:-:|:-:|",
    ]
    ok = lambda b: "✅" if b else "❌"
    por_caso = {}
    for r in resultados:
        por_caso.setdefault(r["id"], []).append(r)
    tot = Counter()
    for cid, rs in por_caso.items():
        av = [r["avaliacao"] for r in rs]
        assinaturas = {(tuple(a["assuntos"]), a["prioridade"], a["humano_marcado"]) for a in av}
        tot["n"] += len(av)
        for k in ("formato_ok", "assunto_ok", "prioridade_ok", "humano_ok"):
            tot[k] += sum(a[k] for a in av)
        frac = lambda k: f"{sum(a[k] for a in av)}/{len(av)}"
        linhas.append(
            f"| {cid} | {rs[0]['tipo']} | " + " · ".join("+".join(a["assuntos"]) or "∅" for a in av)
            + " | " + " · ".join(a["prioridade"] or "∅" for a in av)
            + " | " + "; ".join(sorted({s for a in av for s in a["setor_tabela"]}))
            + " | " + " · ".join("sim" if a["humano_marcado"] else "não" for a in av)
            + f" | {frac('formato_ok')} | {frac('assunto_ok')} | {frac('prioridade_ok')} | {frac('humano_ok')} | "
            + ok(len(assinaturas) == 1) + " |")
    n = tot["n"] or 1
    linhas += ["", "## Totais", "",
               f"- Formato correto: {tot['formato_ok']}/{n} ({100*tot['formato_ok']//n}%)",
               f"- Assunto correto: {tot['assunto_ok']}/{n} ({100*tot['assunto_ok']//n}%)",
               f"- Prioridade aceitável: {tot['prioridade_ok']}/{n} ({100*tot['prioridade_ok']//n}%)",
               f"- Encaminhamento humano quando exigido: {tot['humano_ok']}/{n} ({100*tot['humano_ok']//n}%)",
               "", "## Respostas brutas", ""]
    for r in resultados:
        linhas += [f"**{r['id']} · repetição {r['rep']}** ({r['segundos']}s)", "", "```", r["resposta_bruta"].strip(), "```", ""]
    saida.with_suffix(".md").write_text("\n".join(linhas), encoding="utf-8")
    print("\n".join(linhas[:12 + len(por_caso) + 8]))


if __name__ == "__main__":
    main()
