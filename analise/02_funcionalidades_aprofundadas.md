# 02 — Análise aprofundada das funcionalidades (nível Básico)

Para cada funcionalidade, as sete perguntas do enunciado.

---

## F1 — Classificar mensagens por assunto (+ F2 prioridade)

| Pergunta | Resposta |
|---|---|
| **Entrada** | Texto livre da mensagem do estudante (pode conter dados pessoais, erros de digitação, vários assuntos). |
| **Resultado esperado** | Um rótulo de assunto dentre uma lista fechada (matrícula, documentos, financeiro, calendário, notas, AVA, administrativo, outro) e uma prioridade (alta/média/baixa). |
| **LLM é adequado?** | **Provavelmente sim.** Classificar texto livre é uma tarefa de interpretação de linguagem em que LLMs são fortes e em que palavras-chave falham ("não consigo entrar" pode ser AVA ou matrícula; "boleto" pode aparecer numa mensagem cujo assunto real é trancamento). A saída é curta e verificável contra um gabarito. |
| **Erros possíveis** | (a) rótulo errado em mensagens ambíguas; (b) escolher só um assunto quando há dois; (c) "chutar" com confiança quando falta informação; (d) prioridade influenciada pelo tom (mensagem agressiva = urgente) em vez do conteúdo; (e) sair do formato; (f) obedecer instruções embutidas na mensagem (prompt injection); (g) respostas diferentes para a mesma entrada (variabilidade). |
| **Impacto dos erros** | **Baixo a moderado**, *se* houver humano na sequência: um erro de triagem atrasa o atendimento (mensagem vai para a fila errada) mas não decide nada. Vira **alto** se a classificação disparar ações automáticas (ex.: F5). Erro de prioridade pode atrasar casos urgentes (prova amanhã, prazo de recurso). |
| **Alternativa mais simples** | (1) Formulário/menu estruturado no portal em que o próprio estudante escolhe o assunto; (2) regras de palavras-chave. O formulário é forte para mensagens novas no portal, mas não resolve e-mails livres já recebidos nem estudantes que escolhem a opção errada. |
| **Revisão humana?** | **Sim, no início.** O atendente confirma ou corrige o rótulo sugerido (um clique). Casos de baixa confiança vão para fila humana sem sugestão. |

**Hipótese inicial (a ser testada):** F1 é candidata a "usar IA com revisão humana".

---

## F3 — Encaminhar ao setor responsável

| Pergunta | Resposta |
|---|---|
| **Entrada** | O assunto já identificado (por F1 ou pelo formulário). |
| **Resultado esperado** | O setor responsável (ex.: financeiro → Tesouraria; notas → Coordenação do curso; AVA → Suporte TI). |
| **LLM é adequado?** | **Não.** Uma vez conhecido o assunto, o setor é dado pelo organograma. Não há interpretação a fazer. |
| **Erros possíveis com LLM** | Inventar setores inexistentes; mapear o mesmo assunto para setores diferentes em execuções diferentes; desatualizar-se quando o organograma muda (o prompt precisa ser reeditado em vez de uma tabela). |
| **Impacto dos erros** | Moderado: mensagens perdidas ou circulando entre setores. |
| **Alternativa mais simples** | **Tabela de roteamento** (assunto → setor) mantida pela secretaria, aplicada por regra fixa no sistema de chamados. Determinística, auditável, custo zero, atualização imediata. |
| **Revisão humana?** | Não para o mapeamento em si. Humano mantém a tabela atualizada. |

**Hipótese inicial:** F3 → "usar solução não baseada em IA". O LLM, se usado, entrega apenas o *assunto*; o *setor* sai da tabela.

---

## F6 — Apoiar decisões sobre revisão de nota / benefício financeiro / medidas acadêmicas

| Pergunta | Resposta |
|---|---|
| **Entrada** | Pedido do estudante + (para decidir de fato) histórico acadêmico/financeiro, regulamento, prova corrigida, documentos comprobatórios. |
| **Resultado esperado** | Um parecer ou decisão: deferir/indeferir revisão, conceder/negar desconto, aplicar ou não uma medida. |
| **LLM é adequado?** | **Não para decidir nem para recomendar o mérito.** A decisão exige aplicar regulamento a fatos verificados, considerar documentos, ser explicável e ter um responsável identificável. LLMs não têm acesso confiável aos fatos, podem inventar justificativas plausíveis e não são responsabilizáveis. |
| **Erros possíveis** | Inventar regra ou precedente ("o regulamento permite 50% de desconto"); tratar estudantes de forma desigual conforme a escrita (viés de linguagem, de região, de escolaridade); ser manipulado por argumentação emocional ou injeção de instruções; produzir texto que *parece* decisão oficial. |
| **Impacto dos erros** | **Alto**: prejuízo financeiro, injustiça acadêmica, discriminação, questionamento jurídico (LGPD art. 20 — direito à revisão de decisões automatizadas), dano à reputação. |
| **Alternativa mais simples** | **Processo humano existente**, apoiado por *formulário estruturado* (campos obrigatórios: disciplina, avaliação, justificativa, anexos) e *checklist* do regulamento. Isso reduz o tempo do setor sem delegar o mérito. |
| **Revisão humana?** | A decisão **é** humana. No máximo o sistema pode encaminhar o pedido corretamente (F1/F3) e verificar se o formulário está completo. |

**Hipótese inicial:** F6 → "não implementar nas condições atuais" (como apoio decisório por LLM). A parte de *triagem* desses pedidos é coberta por F1/F3.

---

## Tratamento breve das demais

| Funcionalidade | Leitura inicial |
|---|---|
| **F2 – Prioridade** | Acoplada ao prompt de F1. Parte é regra (prazos do calendário: "prova amanhã", "último dia de rematrícula"), parte é interpretação. Risco de viés por tom. |
| **F4 – Rascunho de resposta** | Útil para economizar digitação, mas só é seguro com base de conhecimento oficial (FAQ, calendário, valores). Sem ela, o modelo tende a inventar datas e regras. Testado em experimento complementar no Intermediário. |
| **F5 – Envio automático** | Remove a revisão humana de F4. Mesmo uma taxa baixa de erro, multiplicada por milhares de mensagens/mês, gera dezenas de respostas erradas enviadas como oficiais. Perguntas realmente simples (datas, links) são melhor atendidas por FAQ/autoatendimento sem IA. |

## Primeiro prompt protótipo

Criado para **F1** (a funcionalidade aparentemente adequada): [`../prompts/v1_classificacao.txt`](../prompts/v1_classificacao.txt).
Resultados com 3 exemplos fictícios: [`../resultados/basico_v1.md`](../resultados/basico_v1.md).
