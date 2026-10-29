# Roteiro da visita de retorno — Conexão Oral

A entrevista e a validação foram concluídas em 26/10/2026. Esta visita de retorno serve para três coisas: **cumprir o que falta para a comprovação**, **fechar os poucos pontos "a levantar"** e **conferir números que a massa de dados usa como premissa**. Os itens que mudaram a estrutura do banco estão indicados na última coluna da seção 2. Se alguma resposta mudar um número, o grupo ajusta a massa (`docs/gerador_massa.py`) e o texto do README.

> Lembrete do esqueleto: a entrevista deve ser feita **com o responsável, no ambiente da organização**, e comprovada com foto. Na correção da E1, o professor apontou que a entrevista tinha sido feita com o próprio integrante. Por isso, o ideal é que a conversa abaixo seja feita **com a Dra. Cristiane, na clínica**, com pelo menos um integrante além do Guilherme.

## 1. Comprovação (obrigatório)

- [ ] Foto da entrevista no local, com a Dra. Cristiane e os integrantes presentes (JPG ou PNG, para `evidencias/entrevista.jpg`). *Prevista para sexta, 30/10/2026.*
- [ ] Foto final do grupo com a entrevistada.
- [x] Anotar data, horário, duração, integrantes presentes e quem perguntou, anotou e fotografou (README, "Relato da entrevista"). *28/10/2026, 15h22, com a Dra. Cristiane, que respondeu; Guilherme Maurício perguntou, anotou e fotografou; falta a duração.*
- [x] Telefone da Dra. Cristiane (ou confirmar que o contato é o telefone da clínica). *(11) 96516-6080, publicação autorizada por ela.*
- [ ] Confirmar que nenhuma foto mostra paciente ou tela com dado pessoal.
- [ ] Opcional: fotos da fachada/recepção, das salas, da ficha de anamnese em branco, de uma guia em branco e do caderno da autoclave (sem dados).

## 2. Pontos que estavam "a levantar" — respondidos em 28 e 29/10/2026

As 18 perguntas foram respondidas pela Dra. Cristiane na visita de 28/10/2026, com registro em 28 e 29/10/2026 (levantamento, seção 12). A última coluna diz o que mudou no trabalho.

| # | Pergunta | Resposta | O que mudou no trabalho |
|---|---|---|---|
| 1 | Dias, horários e sala de cada dentista | Ortodontia seg–sex, 8h–18h, Sala 02; HOF 14h–18h, Sala 01; demais sob demanda, na Sala 01 liberada pela Dra. | Confirma a massa; não há escala a cadastrar. |
| 2 | Receita com vários medicamentos? Duas receitas na mesma consulta? | Vários medicamentos; no máximo uma receita por consulta. | Confirma RECEITUARIO como está. |
| 3 | Entrada, fiado, desconto, recibo | Sem entrada e sem fiado; 5% de desconto com nota fiscal; recibo só a pedido. | Novo IN_NOTA_FISCAL em PAGAMENTO; RN27. |
| 4 | Garantia da peça e refazimento | Garantia de 1 ano; o laboratório refaz sem custo. | Novo tipo REFAZIMENTO no pedido; RN28. |
| 5 | Dados do responsável legal; ligação com o cadastro do pai ou da mãe | Nome e CPF digitados no cadastro do menor; as fichas não são ligadas. | Novo ID_CPF_RESPONSAVEL; atributo composto RESPONSAVEL_LEGAL. |
| 6 | Data de pagamento de conta a vencer | Já vai preenchida no lançamento (data prevista). | DT_PAGAMENTO passa a ser obrigatória; conta a pagar = data depois de hoje, critério do grupo (G17). |
| 7 | Quem cancela, dá desconto, altera preço | Desconto e alteração de preço: só a Dra. Cristiane. Quem cancela não foi informado. | Dicionário §6. |
| 8 | Dois pacientes no mesmo horário (dentista ou sala) | O sistema permite, mas a clínica não faz. | RN11 deixa de ser suposição; A08 confere. |
| 9 | Regra inegociável | Nunca deixar de cobrar antes de o paciente entrar na sala. | RN07 marcada como inegociável. |
| 10 | Indicadores e metas | Confirmação na véspera e ocupação das salas não são usadas; nenhuma meta. | KPIs ficam como proposta do grupo. |
| 11 | Situações do orçamento | Em aberto, Aprovado, Finalizado e Cancelado. | CHECK do orçamento corrigido. |
| 12 | Crédito à vista? | Sim: débito, crédito 1x, crédito 3x ou 6x, e PIX. | CHECK do pagamento corrigido (RN14). |
| 13 | O que o caderno da autoclave anota | Data e etiquetas do teste biológico. | Resultado = leitura das etiquetas. |
| 14 | Carteirinha repete no mesmo convênio? | Não. | UQ_PACIENTE_CARTEIRINHA deixa de ser suposição. |
| 15 | Atestado: quantos, sem atendimento, hora, data | Um por consulta; nunca sem atendimento; hora do agendamento; no de dias a data pode ser posterior. | Novo DT_ATESTADO e CHECK ajustado (RN21). |
| 16 | Troca de convênio | Já aconteceu; o cadastro é atualizado e o antigo não fica guardado. | Convênio volta para a GUIA (R18, FK_GUIA_CONVENIO). |
| 17 | Custo por peça | Não é necessário; basta o total do laboratório. | Confirma o modelo. |
| 18 | Data da avaliação da radiografia | É a do sistema, a mesma do exame. | Confirma o modelo. |

## 3. Números para conferir

| Número usado | Valor no trabalho | Conferir com |
|---|---|---|
| Atendimentos por dia útil | 17 (12 na Sala 02, 5 na Sala 01) | Agenda de uma semana no Simples Dental |
| Faltas e cancelamentos | 15 por mês (~4%) | Relatório de cancelados do mês |
| Guias por mês | ~72 | Site de um dos convênios |
| Pagamentos particulares | ~286 atendimentos particulares por mês (calculados pelo grupo: 80% de 358); a massa gera ~180 pagamentos, porque um pagamento cobre o tratamento inteiro (HOF, endodontia) | Financeiro do Simples Dental |
| Faturamento | ~R$ 90 mil por mês | Financeiro do Simples Dental |
| Pacientes de ortodontia em retorno | ~270 | Agenda de um mês |
| Consultas confirmadas e não registradas (P01) | ~1 por semana | Recepcionista |

## 4. Para levar

- Este roteiro impresso e o [levantamento](levantamento.md) para a Dra. Cristiane ler de novo, se quiser.
- Celular para as fotos (sem fotografar telas com dados de pacientes).
