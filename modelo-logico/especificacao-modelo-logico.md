# Especificação do modelo lógico (para desenhar no brModelo)

> Gerada a partir do próprio `docs/script.sql`, para que diagrama e script não se contradigam. [`modelo_logico.png`](modelo_logico.png) é o diagrama da entrega, na notação do brModelo e com a mesma disposição do DER ([`modelo_logico.svg`](modelo_logico.svg): mesma imagem em vetor).

![Modelo lógico](modelo_logico.png)

**21 tabelas, 168 colunas, 22 chaves estrangeiras.** NOT NULL, UNIQUE, CHECK e DEFAULT não aparecem no diagrama do brModelo: estão no dicionário de dados e no script.

## Notação (esqueleto, seção 2)

- Tabela = retângulo com o nome no topo e uma linha por coluna (nome e tipo).
- Chave dourada = **PK**; chave prateada = **FK**; as duas = coluna que é PK e FK.
- Ligação = linha entre a tabela da FK e a tabela referenciada, com (mín, máx) em cada ponta.

## De onde veio cada tabela

| Tabela | Origem no DER |
|---|---|
| ESPECIALIDADE | entidade ESPECIALIDADE |
| DENTISTA | entidade DENTISTA (R01 → FK) |
| FUNCIONARIO | entidade FUNCIONARIO (compostos decompostos) |
| SALA | entidade SALA |
| CONVENIO | entidade CONVENIO |
| PACIENTE | entidade PACIENTE (R03 → FK + NR_CARTEIRINHA; RESPONSAVEL_LEGAL decomposto) |
| TELEFONE_PACIENTE | atributo multivalorado TELEFONE (1,2) |
| ANAMNESE | entidade fraca ANAMNESE (R04, 1:1) |
| PROCEDIMENTO | entidade PROCEDIMENTO (R02 → FK) |
| ORCAMENTO | entidade ORCAMENTO (R08 → FK) |
| ITEM_ORCAMENTO | entidade fraca ITEM_ORCAMENTO (R09, R10) |
| PAGAMENTO | entidade PAGAMENTO (R11 → FK) |
| CONSULTA | entidade CONSULTA (R05, R06, R07 → FKs; ATESTADO decomposto) |
| PROCEDIMENTO_REALIZADO | entidade associativa (realiza) |
| GUIA | entidade GUIA (R12, 1:1; R18 → FK) |
| MEDICAMENTO | entidade MEDICAMENTO |
| RECEITUARIO | relacionamento N:N R13 (receita) |
| LABORATORIO | entidade LABORATORIO |
| PEDIDO_LABORATORIO | entidade PEDIDO_LABORATORIO (R14, R15 → FKs) |
| TESTE_AUTOCLAVE | entidade TESTE_AUTOCLAVE (R17 → FK) |
| DESPESA | entidade DESPESA (R16 → FK) |

18 entidades + 1 entidade associativa + 1 multivalorado + 1 N:N = **21 tabelas**.

## Tabelas e colunas

### ESPECIALIDADE

| Coluna | Tipo | Chave | Nulo? |
|---|---|---|---|
| ID_ESPECIALIDADE | INT | PK | não |
| NM_ESPECIALIDADE | VARCHAR(40) |  | não |

### DENTISTA

| Coluna | Tipo | Chave | Nulo? |
|---|---|---|---|
| ID_DENTISTA | INT | PK | não |
| ID_ESPECIALIDADE | INT | FK | não |
| NM_DENTISTA | VARCHAR(100) |  | não |
| ID_CRO | VARCHAR(10) |  | não |
| DT_NASCIMENTO | DATE |  | não |
| NR_TELEFONE | VARCHAR(11) |  | não |
| DS_EMAIL | VARCHAR(100) |  | sim |
| DS_CHAVE_PIX | VARCHAR(100) |  | não |
| DS_LOGRADOURO | VARCHAR(100) |  | não |
| NR_ENDERECO | VARCHAR(10) |  | não |
| DS_COMPLEMENTO | VARCHAR(40) |  | sim |
| NM_BAIRRO | VARCHAR(60) |  | não |
| CD_CEP | CHAR(8) |  | não |
| TP_VINCULO | VARCHAR(12) |  | não |
| IN_ATIVO | BOOLEAN |  | não |

### FUNCIONARIO

| Coluna | Tipo | Chave | Nulo? |
|---|---|---|---|
| ID_FUNCIONARIO | INT | PK | não |
| NM_FUNCIONARIO | VARCHAR(100) |  | não |
| TP_FUNCAO | VARCHAR(20) |  | não |
| DT_NASCIMENTO | DATE |  | não |
| TP_SEXO | CHAR(1) |  | não |
| NR_TELEFONE | VARCHAR(11) |  | não |
| DS_LOGRADOURO | VARCHAR(100) |  | não |
| NR_ENDERECO | VARCHAR(10) |  | não |
| DS_COMPLEMENTO | VARCHAR(40) |  | sim |
| NM_BAIRRO | VARCHAR(60) |  | não |
| CD_CEP | CHAR(8) |  | não |
| NM_BANCO | VARCHAR(40) |  | não |
| NR_AGENCIA | VARCHAR(6) |  | não |
| NR_CONTA | VARCHAR(15) |  | não |
| DT_ADMISSAO | DATE |  | não |
| DT_DESLIGAMENTO | DATE |  | sim |

### SALA

| Coluna | Tipo | Chave | Nulo? |
|---|---|---|---|
| ID_SALA | INT | PK | não |
| NM_SALA | VARCHAR(20) |  | não |
| HR_ABERTURA | TIME |  | não |
| HR_FECHAMENTO | TIME |  | não |

### CONVENIO

| Coluna | Tipo | Chave | Nulo? |
|---|---|---|---|
| ID_CONVENIO | INT | PK | não |
| NM_CONVENIO | VARCHAR(40) |  | não |
| IN_ATIVO | BOOLEAN |  | não |

### PACIENTE

| Coluna | Tipo | Chave | Nulo? |
|---|---|---|---|
| ID_PACIENTE | INT | PK | não |
| NM_PACIENTE | VARCHAR(100) |  | não |
| DT_NASCIMENTO | DATE |  | não |
| TP_SEXO | CHAR(1) |  | não |
| ID_CPF | CHAR(11) |  | não |
| ID_RG | VARCHAR(14) |  | não |
| DS_PROFISSAO | VARCHAR(60) |  | não |
| TP_ESTADO_CIVIL | VARCHAR(15) |  | não |
| DS_LOGRADOURO | VARCHAR(100) |  | não |
| NR_ENDERECO | VARCHAR(10) |  | não |
| DS_COMPLEMENTO | VARCHAR(40) |  | sim |
| NM_BAIRRO | VARCHAR(60) |  | não |
| CD_CEP | CHAR(8) |  | não |
| DS_EMAIL | VARCHAR(100) |  | não |
| ID_CONVENIO | INT | FK | sim |
| NR_CARTEIRINHA | VARCHAR(20) |  | sim |
| NM_RESPONSAVEL_LEGAL | VARCHAR(100) |  | sim |
| ID_CPF_RESPONSAVEL | CHAR(11) |  | sim |
| DT_CADASTRO | DATE |  | não |

### TELEFONE_PACIENTE

| Coluna | Tipo | Chave | Nulo? |
|---|---|---|---|
| ID_PACIENTE | INT | PK + FK | não |
| NR_ORDEM | TINYINT | PK | não |
| NR_TELEFONE | VARCHAR(11) |  | não |

### ANAMNESE

| Coluna | Tipo | Chave | Nulo? |
|---|---|---|---|
| ID_PACIENTE | INT | PK + FK | não |
| DT_PREENCHIMENTO | DATE |  | não |
| TP_ASSINANTE | VARCHAR(11) |  | não |
| DS_ARQUIVO_DIGITALIZADO | VARCHAR(200) |  | não |
| IN_BEM_DE_SAUDE | BOOLEAN |  | não |
| IN_TRATAMENTO_MEDICO | BOOLEAN |  | não |
| IN_ALERGIA_MEDICAMENTO | BOOLEAN |  | não |
| IN_DOENCA_GRAVE | BOOLEAN |  | não |
| IN_USA_MEDICAMENTO | BOOLEAN |  | não |
| IN_DIFICULDADE_ABRIR_BOCA | BOOLEAN |  | não |
| QT_ESCOVACOES_DIA | TINYINT |  | não |
| IN_DESMAIOS | BOOLEAN |  | não |
| IN_REACAO_ANESTESICO | BOOLEAN |  | não |
| IN_USOU_APARELHO | BOOLEAN |  | não |
| IN_GRAVIDA_AMAMENTANDO | BOOLEAN |  | não |
| IN_DIABETES | BOOLEAN |  | não |
| IN_HIPERTENSAO | BOOLEAN |  | não |
| IN_HEPATITE | BOOLEAN |  | não |
| IN_PROBLEMA_RESPIRATORIO | BOOLEAN |  | não |
| IN_PROBLEMA_CARDIACO | BOOLEAN |  | não |
| IN_COMPLICACAO_TRATAMENTO | BOOLEAN |  | não |
| DS_OBSERVACOES | VARCHAR(500) |  | sim |

### PROCEDIMENTO

| Coluna | Tipo | Chave | Nulo? |
|---|---|---|---|
| ID_PROCEDIMENTO | INT | PK | não |
| ID_ESPECIALIDADE | INT | FK | sim |
| NM_PROCEDIMENTO | VARCHAR(80) |  | não |
| TP_PROCEDIMENTO | VARCHAR(11) |  | não |
| IN_ATIVO | BOOLEAN |  | não |

### ORCAMENTO

| Coluna | Tipo | Chave | Nulo? |
|---|---|---|---|
| ID_ORCAMENTO | INT | PK | não |
| ID_PACIENTE | INT | FK | não |
| DT_ORCAMENTO | DATE |  | não |
| DS_ORCAMENTO | VARCHAR(150) |  | não |
| TP_SITUACAO | VARCHAR(10) |  | não |

### ITEM_ORCAMENTO

| Coluna | Tipo | Chave | Nulo? |
|---|---|---|---|
| ID_ORCAMENTO | INT | PK + FK | não |
| NR_ITEM | TINYINT | PK | não |
| ID_PROCEDIMENTO | INT | FK | não |
| CD_DENTE | VARCHAR(3) |  | não |
| VL_ITEM | DECIMAL(10,2) |  | não |

### PAGAMENTO

| Coluna | Tipo | Chave | Nulo? |
|---|---|---|---|
| ID_PAGAMENTO | INT | PK | não |
| ID_ORCAMENTO | INT | FK | não |
| DT_PAGAMENTO | DATE |  | não |
| VL_PAGAMENTO | DECIMAL(10,2) |  | não |
| TP_FORMA_PAGAMENTO | VARCHAR(7) |  | não |
| QT_PARCELAS | TINYINT |  | não |
| IN_NOTA_FISCAL | BOOLEAN |  | não |

### CONSULTA

| Coluna | Tipo | Chave | Nulo? |
|---|---|---|---|
| ID_CONSULTA | INT | PK | não |
| ID_PACIENTE | INT | FK | não |
| ID_DENTISTA | INT | FK | não |
| ID_SALA | INT | FK | não |
| DT_HR_INICIO | DATETIME |  | não |
| QT_DURACAO_MIN | TINYINT |  | não |
| TP_ATENDIMENTO | VARCHAR(10) |  | não |
| TP_SITUACAO | VARCHAR(14) |  | não |
| TP_MOTIVO_CANCELAMENTO | VARCHAR(15) |  | sim |
| DT_HR_REGISTRO | DATETIME |  | não |
| DT_HR_CONFIRMACAO | DATETIME |  | sim |
| DS_OBSERVACAO | VARCHAR(300) |  | sim |
| TP_ATESTADO | VARCHAR(8) |  | sim |
| DT_ATESTADO | DATE |  | sim |
| QT_DIAS_ATESTADO | TINYINT |  | sim |
| DS_CID_ATESTADO | VARCHAR(100) |  | sim |

### PROCEDIMENTO_REALIZADO

| Coluna | Tipo | Chave | Nulo? |
|---|---|---|---|
| ID_CONSULTA | INT | PK + FK | não |
| ID_PROCEDIMENTO | INT | PK + FK | não |
| CD_DENTE | VARCHAR(3) | PK | não |
| DS_OBSERVACAO | VARCHAR(500) |  | sim |

### GUIA

| Coluna | Tipo | Chave | Nulo? |
|---|---|---|---|
| ID_GUIA | INT | PK | não |
| ID_CONSULTA | INT | FK | não |
| ID_CONVENIO | INT | FK | não |
| DT_EMISSAO | DATE |  | não |
| DT_HR_ASSINATURA | DATETIME |  | sim |
| DT_ENVIO | DATE |  | sim |
| VL_GUIA | DECIMAL(10,2) |  | não |
| DT_RECEBIMENTO | DATE |  | sim |

### MEDICAMENTO

| Coluna | Tipo | Chave | Nulo? |
|---|---|---|---|
| ID_MEDICAMENTO | INT | PK | não |
| NM_MEDICAMENTO | VARCHAR(80) |  | não |
| DS_DOSAGEM | VARCHAR(60) |  | não |
| DS_ORIENTACAO | VARCHAR(200) |  | não |
| IN_CONTROLADO | BOOLEAN |  | não |

### RECEITUARIO

| Coluna | Tipo | Chave | Nulo? |
|---|---|---|---|
| ID_CONSULTA | INT | PK + FK | não |
| ID_MEDICAMENTO | INT | PK + FK | não |

### LABORATORIO

| Coluna | Tipo | Chave | Nulo? |
|---|---|---|---|
| ID_LABORATORIO | INT | PK | não |
| NM_LABORATORIO | VARCHAR(60) |  | não |
| NR_WHATSAPP | VARCHAR(11) |  | não |
| QT_DIAS_PRAZO | TINYINT |  | não |

### PEDIDO_LABORATORIO

| Coluna | Tipo | Chave | Nulo? |
|---|---|---|---|
| ID_PEDIDO | INT | PK | não |
| ID_CONSULTA | INT | FK | não |
| ID_LABORATORIO | INT | FK | não |
| TP_PEDIDO | VARCHAR(11) |  | não |
| DS_PECA | VARCHAR(100) |  | não |
| CD_DENTE | VARCHAR(3) |  | não |
| DT_ENVIO | DATE |  | não |
| DT_PREVISTA | DATE |  | não |
| DT_CHEGADA | DATE |  | sim |

### TESTE_AUTOCLAVE

| Coluna | Tipo | Chave | Nulo? |
|---|---|---|---|
| ID_TESTE | INT | PK | não |
| ID_FUNCIONARIO | INT | FK | não |
| DT_TESTE | DATE |  | não |
| TP_RESULTADO | VARCHAR(9) |  | não |
| DS_OBSERVACAO | VARCHAR(200) |  | sim |

### DESPESA

| Coluna | Tipo | Chave | Nulo? |
|---|---|---|---|
| ID_DESPESA | INT | PK | não |
| DS_TITULO | VARCHAR(80) |  | não |
| TP_CATEGORIA | VARCHAR(12) |  | não |
| VL_DESPESA | DECIMAL(10,2) |  | não |
| DT_VENCIMENTO | DATE |  | não |
| DT_PAGAMENTO | DATE |  | não |
| TP_FORMA_PAGAMENTO | VARCHAR(6) |  | não |
| DS_DESPESA | VARCHAR(200) |  | não |
| ID_DENTISTA | INT | FK | sim |

## Ligações (cardinalidades já convertidas)

Ponta da tabela referenciada = (1,1) se a FK é obrigatória, (0,1) se aceita nulo. Ponta da tabela da FK = (0,n), ou (0,1) quando a FK é única (1:1), ou o mínimo/máximo da regra de negócio ((1,n) nos itens do orçamento, (1,2) nos telefones).

| Tabela com a FK | Coluna(s) | Card. nesta ponta | Tabela referenciada | Card. nesta ponta | Constraint |
|---|---|---|---|---|---|
| DENTISTA | ID_ESPECIALIDADE | (0,n) | ESPECIALIDADE (ID_ESPECIALIDADE) | (1,1) | FK_DENTISTA_ESPECIALIDADE |
| PACIENTE | ID_CONVENIO | (0,n) | CONVENIO (ID_CONVENIO) | (0,1) | FK_PACIENTE_CONVENIO |
| TELEFONE_PACIENTE | ID_PACIENTE | (1,2) | PACIENTE (ID_PACIENTE) | (1,1) | FK_TELEFONE_PACIENTE — ON DELETE CASCADE |
| ANAMNESE | ID_PACIENTE | (0,1) | PACIENTE (ID_PACIENTE) | (1,1) | FK_ANAMNESE_PACIENTE |
| PROCEDIMENTO | ID_ESPECIALIDADE | (0,n) | ESPECIALIDADE (ID_ESPECIALIDADE) | (0,1) | FK_PROCEDIMENTO_ESPECIALIDADE |
| ORCAMENTO | ID_PACIENTE | (0,n) | PACIENTE (ID_PACIENTE) | (1,1) | FK_ORCAMENTO_PACIENTE |
| ITEM_ORCAMENTO | ID_ORCAMENTO | (1,n) | ORCAMENTO (ID_ORCAMENTO) | (1,1) | FK_ITEM_ORCAMENTO_ORCAMENTO — ON DELETE CASCADE |
| ITEM_ORCAMENTO | ID_PROCEDIMENTO | (0,n) | PROCEDIMENTO (ID_PROCEDIMENTO) | (1,1) | FK_ITEM_ORCAMENTO_PROCEDIMENTO |
| PAGAMENTO | ID_ORCAMENTO | (0,n) | ORCAMENTO (ID_ORCAMENTO) | (1,1) | FK_PAGAMENTO_ORCAMENTO |
| CONSULTA | ID_PACIENTE | (0,n) | PACIENTE (ID_PACIENTE) | (1,1) | FK_CONSULTA_PACIENTE |
| CONSULTA | ID_DENTISTA | (0,n) | DENTISTA (ID_DENTISTA) | (1,1) | FK_CONSULTA_DENTISTA |
| CONSULTA | ID_SALA | (0,n) | SALA (ID_SALA) | (1,1) | FK_CONSULTA_SALA |
| PROCEDIMENTO_REALIZADO | ID_CONSULTA | (0,n) | CONSULTA (ID_CONSULTA) | (1,1) | FK_PROC_REALIZADO_CONSULTA |
| PROCEDIMENTO_REALIZADO | ID_PROCEDIMENTO | (0,n) | PROCEDIMENTO (ID_PROCEDIMENTO) | (1,1) | FK_PROC_REALIZADO_PROCEDIMENTO |
| GUIA | ID_CONSULTA | (0,1) | CONSULTA (ID_CONSULTA) | (1,1) | FK_GUIA_CONSULTA |
| GUIA | ID_CONVENIO | (0,n) | CONVENIO (ID_CONVENIO) | (1,1) | FK_GUIA_CONVENIO |
| RECEITUARIO | ID_CONSULTA | (0,n) | CONSULTA (ID_CONSULTA) | (1,1) | FK_RECEITUARIO_CONSULTA |
| RECEITUARIO | ID_MEDICAMENTO | (0,n) | MEDICAMENTO (ID_MEDICAMENTO) | (1,1) | FK_RECEITUARIO_MEDICAMENTO |
| PEDIDO_LABORATORIO | ID_CONSULTA | (0,n) | CONSULTA (ID_CONSULTA) | (1,1) | FK_PEDIDO_CONSULTA |
| PEDIDO_LABORATORIO | ID_LABORATORIO | (0,n) | LABORATORIO (ID_LABORATORIO) | (1,1) | FK_PEDIDO_LABORATORIO |
| TESTE_AUTOCLAVE | ID_FUNCIONARIO | (0,n) | FUNCIONARIO (ID_FUNCIONARIO) | (1,1) | FK_TESTE_FUNCIONARIO |
| DESPESA | ID_DENTISTA | (0,n) | DENTISTA (ID_DENTISTA) | (0,1) | FK_DESPESA_DENTISTA |
