# O que mudou no `script.sql` (versão simplificada, 03/11/2026)

O script foi reescrito para usar **só os comandos vistos em aula**. As 21 tabelas, as 168 colunas, as chaves primárias, as 22 chaves estrangeiras, os 12 UNIQUE, a massa de dados e os códigos das 50 consultas (J01–J06, U01–U05, D01–D04, G01–G20, A01–A15) **continuam os mesmos**.

## Comandos usados agora

| Parte do script | Comandos |
|---|---|
| Estrutura | `DROP DATABASE IF EXISTS`, `CREATE DATABASE`, `USE`, `CREATE TABLE`, `PRIMARY KEY`, `FOREIGN KEY ... REFERENCES`, `NOT NULL`, `UNIQUE`, `CHECK`, `DEFAULT`, `AUTO_INCREMENT` |
| Carga | `INSERT INTO ... VALUES` |
| Consultas | `SELECT`, `JOIN`, `LEFT JOIN`, `WHERE`, `AND`/`OR`, `BETWEEN`, `LIKE`, `IN (lista)`, `IS NULL`, `DISTINCT`, `ORDER BY`, `GROUP BY` com `COUNT` e `SUM` |
| Alteração | `UPDATE ... SET ... WHERE`, `DELETE FROM ... WHERE` |

`SUM` (soma) é da mesma família do `COUNT` e aparece nos totais em reais (faturamento, despesas, a receber, total e pago dos orçamentos) e na soma de minutos da G20. As contas simples (`+`, `-`, `*`, `/`) aparecem em três consultas, para calcular percentual ou ticket médio.

## Comandos que saíram e como foram substituídos

| Saiu | Onde era usado | Como ficou |
|---|---|---|
| Variáveis `SET @DATA_REF`, `@PROX_UTIL`, `@ID_U01`... | Data de "hoje" e IDs calculados antes de cada UPDATE/DELETE | As datas e os IDs estão escritos direto no comando (ex.: `WHERE ID_CONSULTA = 978`). O comentário de cada um explica qual registro é. |
| Funções de data (`DATE()`, `DATE_FORMAT`, `DATEDIFF`, `DATE_ADD`, `TIMESTAMPDIFF`, `DAYOFWEEK`, `LAST_DAY`, `TIME()`) | Filtros por dia ou mês, idade, dias em atraso | `BETWEEN` com as datas escritas (ex.: `BETWEEN '2026-09-01 00:00:00' AND '2026-09-30 23:59:59'`). Os KPIs mensais usam setembro/2026, o último mês fechado; para outro mês, basta trocar as datas. |
| Subconsulta (`SELECT` dentro de outro) e `EXISTS`/`NOT EXISTS` | J02, J03, D02, D04, G15, G16, A05, A06, A14 | `JOIN` comum, ou `LEFT JOIN` + `WHERE ... IS NULL` para achar "o que não tem" (ex.: consulta de convênio sem guia). |
| `NOT IN` | A10 | `IN` com a lista das situações em aberto (a confirmar, confirmada, em atendimento) |
| `CASE WHEN` | Rótulos como "VENCIDA", "ATRASADA", "MESMA SALA" | A consulta mostra a coluna original (data, sala, dentista) e o comentário diz como ler. |
| `HAVING` | A11 (dois orçamentos no mesmo mês) | A tabela ORCAMENTO ligada a ela mesma (o1 e o2) com `JOIN`. |
| `WITH` (CTE) e `WITH RECURSIVE` | G08, G14, G15, G18, G20, A13 | G08, G14 e G18 viraram duas ou três consultas menores com o mesmo código, marcadas "(1/2)", "(2/2)", e o comentário diz como somar as partes; G15, G20 e A13 viraram uma consulta simples. |
| `UNION ALL` | A06 (três tipos de erro numa só lista) | Duas consultas separadas: A06 (1/2) e A06 (2/2). |
| `COALESCE`, `ROUND`, `CONCAT_WS`, `GROUP_CONCAT`, `GREATEST`, `LEAST`, `LIMIT` | Formatação do resultado | Removidos: o resultado mostra o valor puro (ex.: um procedimento por linha em vez de todos juntos numa célula). |
| `REGEXP_LIKE` em 13 CHECK de formato (CPF, CEP, telefone, CRO, dente) | Conferir se o texto só tem números | Saíram. O tamanho da coluna (`CHAR(11)`, `CHAR(8)`, `VARCHAR(11)`) continua limitando o dado. |
| `CHECK` com funções de data (dia útil e horário da consulta) | `CK_CONSULTA_DIA_UTIL`, `CK_CONSULTA_HORARIO` | Saíram. O horário de cada sala continua no `CK_SALA_HORARIO`, e a auditoria A09 procura consulta na Sala 01 pela manhã. |
| `CHECK ((A IS NULL) = (B IS NULL))` | 5 CHECK de "os dois juntos ou nenhum" | Reescritos com `AND`/`OR`: `(A IS NULL AND B IS NULL) OR (A IS NOT NULL AND B IS NOT NULL)`. Mesma regra, escrita do jeito visto em aula. |
| `ON DELETE CASCADE` | Telefones e itens de orçamento | Saiu. Para apagar o paciente duplicado (D04), o script apaga antes os telefones dele. |
| `CREATE INDEX` (3 índices na CONSULTA) | Desempenho | Saíram. As PKs e FKs já têm índice no MySQL, e o volume da clínica é pequeno. |
| `SET NAMES`, `COLLATE`, `ENGINE = InnoDB`, `SET SQL_SAFE_UPDATES` | Configuração | Saíram: são o padrão do MySQL 8. Como todo UPDATE e DELETE usa a chave no `WHERE`, o *safe update mode* do Workbench não bloqueia. |
| `DEFAULT (CURRENT_DATE)` em `DT_CADASTRO` | Data de cadastro automática | Saiu; a data é informada no INSERT. Ficou só o `DEFAULT CURRENT_TIMESTAMP` em `DT_HR_REGISTRO`, que é o que resolve o P01 (registro automático do agendamento). |

## Números que mudaram

| Item | Antes | Agora |
|---|---|---|
| CHECK | 58 | 43 (saíram 15: 13 de formato e 2 de data/horário; 5 foram reescritos sem mudar a regra; 2 — CK_GUIA_DATAS e CK_CONSULTA_ATESTADO — perderam a parte que usava `DATE()`: "envio não antes da assinatura" e a data do atestado contra o dia da consulta) |
| Instruções do script | 139 | 127 (sem as variáveis `SET @`; algumas consultas viraram duas ou três partes) |
| Índices extras | 3 | 0 |
| `ON DELETE CASCADE` | 2 | 0 |
| UNIQUE, FK, tabelas, colunas, registros | 12, 22, 21, 168, 5.886 | iguais |

## Consultas que mudaram de jeito (não só de escrita)

| Código | Antes | Agora |
|---|---|---|
| J03 | Total, pago e saldo de cada orçamento numa consulta | Duas partes: (1/2) total de cada orçamento (soma dos itens); (2/2) pago de cada orçamento; saldo = total − pago |
| J04 | Procedimentos da guia juntos numa célula | Um procedimento por linha |
| G02, G04, G09, G13, G14, G15, G18, G19, G20 | Um resultado por mês | Resultado de setembro/2026 (último mês fechado); para outro mês, troque as datas |
| G03 | Quantidade por mês | Lista das consultas não registradas, com a data |
| G04 | Percentuais calculados | Quantidade por situação e motivo; a taxa é a divisão indicada no comentário |
| G06, G08, G10, G14, G18 | Uma consulta | Duas ou três partes "(1/2)", "(2/2)" |
| G10 | Atraso contra o prazo padrão do laboratório | Chegada até a data prevista (que pode ser renegociada, como na U03) |
| G15 | Pagamento rateado pelos itens do orçamento, por especialidade | Soma dos itens dos orçamentos pagos no mês, por especialidade |
| G20 | Ocupação em % com dias úteis calculados | Minutos atendidos por sala; os minutos disponíveis estão no comentário (21 dias úteis em setembro) |
| A02 | Idade calculada na data da ficha | Menor = nascido depois de 26/10/2008 (não confere mais a idade na data da ficha) |
| A05 | Pagamento até a consulta (180 dias ou mês) | Consulta de ortodontia particular em outubro sem orçamento aprovado no mês |
| A06 | Três casos numa lista | Dois casos em duas partes; o caso "convênio com pagamento particular no mesmo dia" saiu, porque dependia de função de data |
| A08 | Horários que se sobrepõem | Consultas com o mesmo horário de início na mesma sala ou com o mesmo dentista (o encaixe proposital da massa passou de 14h20 para 14h, no gerador) |
| A09 | Fora do horário de qualquer sala | Sala 01 pela manhã (com `LIKE` na hora) |
| A11 | `HAVING` por mês | Dois orçamentos de manutenção do mesmo paciente em outubro/2026 |
| A13 | Lista de semanas sem teste | Quantidade de testes por resultado em 12 semanas (o esperado é 12 aprovados) |

## O que precisa ser feito de novo

- **Rodar o script no MySQL Workbench** (banco vazio, executar tudo) e trocar o print `docs/teste_mysql.png`: o print de 30/10 é da versão anterior.
- Na apresentação, mostrar as consultas novas: os códigos são os mesmos, mas algumas têm duas partes.
