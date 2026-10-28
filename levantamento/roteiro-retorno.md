# Roteiro da visita de retorno — Conexão Oral

A entrevista e a validação foram concluídas em 26/10/2026. Esta visita de retorno serve para três coisas: **cumprir o que falta para a comprovação**, **fechar os poucos pontos "a levantar"** e **conferir números que a massa de dados usa como premissa**. Quase nenhum item muda a estrutura do banco. Os que mudariam estão marcados com **(estrutura)** e já têm a solução descrita no README (seção 1.2, "O que deixou de ser tabela"). Se alguma resposta mudar um número, o grupo ajusta a massa (`docs/gerador_massa.py`) e o texto do README.

> Lembrete do esqueleto: a entrevista deve ser feita **com o responsável, no ambiente da organização**, e comprovada com foto. Na correção da E1, o professor apontou que a entrevista tinha sido feita com o próprio integrante. Por isso, o ideal é que a conversa abaixo seja feita **com a Dra. Cristiane, na clínica**, com pelo menos um integrante além do Guilherme.

## 1. Comprovação (obrigatório)

- [ ] Foto da entrevista no local, com a Dra. Cristiane e os integrantes presentes (JPG ou PNG, para `evidencias/entrevista.jpg`).
- [ ] Foto final do grupo com a entrevistada.
- [ ] Anotar data, horário, duração, integrantes presentes e quem perguntou, anotou e fotografou (README, "Relato da entrevista").
- [ ] Telefone da Dra. Cristiane (ou confirmar que o contato é o telefone da clínica).
- [ ] Confirmar que nenhuma foto mostra paciente ou tela com dado pessoal.
- [ ] Opcional: fotos da fachada/recepção, das salas, da ficha de anamnese em branco, de uma guia em branco e do caderno da autoclave (sem dados).

## 2. Pontos ainda "a levantar"

| # | Pergunta | Onde entra no trabalho |
|---|---|---|
| 1 | Em que dias e horários atende cada dentista? Em que sala? (Os quatro que atendem cerca de uma vez por mês vêm em dia fixo ou sob demanda?) | Hoje a massa supõe ortodontia todos os dias na Sala 02 e HOF todas as tardes na Sala 01. Se houver escala fixa, pode virar tabela própria. |
| 2 | Uma receita pode ter mais de um medicamento? A mesma consulta pode gerar duas receitas separadas? **(estrutura)** | O modelo já aceita vários medicamentos por consulta (RECEITUARIO). Se houver duas receitas separadas na mesma consulta, a receita volta a ser tabela. |
| 3 | Existe pagamento com entrada, fiado ou desconto à vista? Dá recibo? | RN14 e tabela PAGAMENTO. |
| 4 | Peça protética tem garantia? Quem paga um refazimento? | Regras da peça (seção 1.1 do README). |
| 5 | Quais dados do responsável legal ficam na ficha da criança (só o nome, ou também CPF e telefone)? Quando o pai ou a mãe também é paciente, a clínica precisa ligar a ficha da criança ao cadastro dele? Qual a relação (pai, mãe, tutor)? **(estrutura)** | Hoje o modelo guarda só o nome do responsável. Se precisar da ligação, ela volta como FK opcional para PACIENTE. |
| 6 | Quando o sócio lança uma conta que ainda vai vencer, a data de pagamento fica vazia ou já vai preenchida? | No banco, DT_PAGAMENTO vazia = conta em aberto (G17). |
| 7 | Quem pode cancelar consulta, dar desconto, alterar preço e remarcar? | Seção 6 do dicionário (permissões). |
| 8 | Dois pacientes podem ser marcados no mesmo horário com o mesmo dentista ou na mesma sala? | Auditoria A08 (uma cadeira por sala). |
| 9 | Há algo que nunca pode acontecer na clínica (uma regra que a Dra. considere inegociável)? | Regras de negócio. |
| 10 | Quais desses indicadores seriam úteis e que meta faria sentido? (taxa de faltas, confirmação na véspera, faturamento por especialidade, a receber dos convênios, ocupação das salas) | Metas da seção 1.6 (hoje são propostas do grupo). |
| 11 | Quais situações aparecem na lista de orçamentos do sistema, além de "Em aberto"? | O modelo supõe EM ABERTO, APROVADO, CONCLUIDO e REPROVADO. |
| 12 | O crédito pode ser à vista (1x), ou só em 3x e 6x? | Hoje o CHECK só aceita 3 ou 6 no crédito, como o levantamento disse. |
| 13 | O caderno da autoclave anota o resultado do teste (aprovado/reprovado) e o que se fez quando reprovou? | Tabela TESTE_AUTOCLAVE. |
| 14 | O número da carteirinha pode se repetir dentro do mesmo convênio? | UQ_PACIENTE_CARTEIRINHA. |
| 15 | A mesma consulta pode ter mais de um atestado? Já foi dado atestado para consulta em que o paciente não foi atendido? No atestado de presença, a hora inicial e final é a do agendamento ou a da chegada e saída reais? No atestado de dias, a data pode ser diferente do dia da consulta? **(estrutura)** | CK_CONSULTA_ATESTADO (hoje: no máximo um, só em consulta finalizada). Se houver mais de um, o atestado volta a ser tabela. |
| 16 | Algum paciente já trocou de convênio? A guia antiga precisa continuar mostrando o convênio antigo? **(estrutura)** | Hoje o convênio da guia vem do cadastro do paciente (README 1.4). Se precisar, a FK do convênio volta para a guia. |
| 17 | O sócio quer saber quanto custou cada peça, somando as idas ao laboratório? **(estrutura)** | Hoje a despesa de laboratório cita o número do pedido na descrição. Se quiser, volta a ligação da despesa com o pedido. |
| 18 | A avaliação da radiografia tem data própria, diferente do dia do exame? | Hoje fica a avaliação (PROCEDIMENTO_REALIZADO.DS_OBSERVACAO), sem data. |

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
