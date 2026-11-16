# 01 — Fluxo atual e decomposição da proposta

> Nível Básico. Objetivo: entender o fluxo atual antes de escrever qualquer prompt e separar a proposta em atividades menores, cada uma com natureza e risco próprios.

## 1. Fluxo atual (como é hoje)

```
Estudante envia mensagem (e-mail / portal / chat)
        │
        ▼
Atendente lê a mensagem ──► identifica o assunto ──► avalia urgência
        │
        ▼
Encaminha ao setor responsável (Secretaria, Financeiro, Coordenação, Suporte TI…)
        │
        ├──► (alguns casos) prepara resposta inicial
        ▼
Setor analisa e decide (ex.: revisão de nota, desconto, segunda chamada)
        │
        ▼
Resposta final ao estudante
```

Gargalo declarado pela instituição: **tempo de atendimento** com milhares de mensagens por mês.
Observação importante: o gargalo está na *triagem* (ler, entender, encaminhar). A *decisão* (aprovar desconto, revisar nota) já é dos setores e segue regulamentos — acelerar a decisão não é o mesmo problema que acelerar a triagem.

## 2. Decomposição das atividades propostas

| # | Atividade proposta | Interpretação de linguagem | Geração de texto | Aplicação de regra | Consulta a informação | Decisão | Natureza predominante |
|---|---|:-:|:-:|:-:|:-:|:-:|---|
| F1 | Classificar mensagens por assunto | ●●● | – | ● | – | ● | Interpretação de linguagem |
| F2 | Identificar a prioridade | ●● | – | ●● | ● (prazos) | ●● | Interpretação + regra |
| F3 | Encaminhar ao setor responsável | – | – | ●●● | ● (organograma) | ● | Regra (assunto → setor) |
| F4 | Produzir rascunho de resposta | ●● | ●●● | ● | ●●● (regulamentos, calendário, valores) | ● | Geração + consulta |
| F5 | Enviar automaticamente respostas "simples" | ●● | ●● | ● | ●● | ●●● (dispensa humano) | Decisão de publicar sem revisão |
| F6 | Apoiar decisões sobre revisão de nota, benefício financeiro, medidas acadêmicas | ● | ● | ●●● (regulamento) | ●●● (histórico do aluno) | ●●● (alto impacto) | Decisão de alto impacto |

Legenda: ●●● predominante · ●● relevante · ● secundário · – irrelevante.

### Leitura da tabela

- **F1** é a atividade mais "linguística": mensagens livres, informais, com erros de digitação, gírias e mais de um assunto. É onde um LLM tem vantagem real sobre palavras-chave.
- **F3** quase não depende de linguagem: uma vez conhecido o assunto, o setor é dado por uma tabela fixa. Usar LLM aqui é adicionar custo e variabilidade sem ganho.
- **F4** parece adequada a LLM (gerar texto), mas depende de **informação factual da instituição** (datas, valores, regras) que o modelo não possui — risco de inventar.
- **F5** não é uma tarefa técnica nova, é a **remoção do humano** do F4. O risco é o de F4 multiplicado pela ausência de revisão.
- **F6** é decisão que afeta direitos do estudante (nota, dinheiro, sanção). Exige regulamento, histórico, explicabilidade e responsabilização — o oposto do que um LLM oferece.

## 3. Funcionalidades escolhidas para aprofundamento

| Perfil exigido pelo enunciado | Funcionalidade escolhida | Por quê |
|---|---|---|
| Aparentemente adequada a LLM | **F1 – Classificação por assunto** (com F2 – prioridade acoplada) | Entrada em linguagem natural, livre e ambígua; saída estruturada e verificável. |
| Resolvível de forma mais simples | **F3 – Encaminhamento ao setor** | É um mapeamento determinístico assunto → setor. |
| Decisão de impacto relevante | **F6 – Apoio a revisão de nota / benefício financeiro** | Afeta direitos e oportunidades do estudante. |

F4 e F5 são tratadas de forma mais breve, mas entram na recomendação final (F4 recebe um experimento complementar no nível Intermediário).

Análise detalhada: [`02_funcionalidades_aprofundadas.md`](02_funcionalidades_aprofundadas.md).
