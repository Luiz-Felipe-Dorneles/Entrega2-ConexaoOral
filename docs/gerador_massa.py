#!/usr/bin/env python3
"""
Gerador da massa de dados fictícia — Conexão Oral (Entrega 2).

Gera os INSERT INTO do banco conexao_oral e os grava em docs/script.sql,
entre os marcadores "-- [INICIO MASSA]" e "-- [FIM MASSA]".

Uso:  python3 docs/gerador_massa.py

Todos os nomes, CPFs, telefones, endereços e valores são inventados
(semente fixa: o resultado é sempre o mesmo). Os volumes seguem os
números do levantamento (README, seções 1.1 e 4):
  - ~12 atendimentos por dia na Sala 02 (ortodontia) e ~4 na Sala 01 (HOF 3 por
    tarde, endodontia 2 por semana, demais 1 por mês) — o levantamento diz 17
    por dia (12 + 5), mas as médias por especialidade somam ~16;
  - ortodontia ~78% dos atendimentos, HOF ~18%, demais ~4%;
  - 80% particular e 20% convênio (~72 guias por mês);
  - ~15 faltas e cancelamentos por mês; 12 a 15 pacientes novos por mês;
  - ~15 receitas, ~10 radiografias e ~3 peças protéticas por mês;
  - teste biológico da autoclave toda semana.
Período: 03/08/2026 a 27/11/2026 (12 semanas de histórico, o dia da
visita, 26/10/2026, e cinco semanas de agenda futura — um ciclo de
retorno da ortodontia), só em dias úteis.
"""
import datetime as dt
import os
import random
import re
from decimal import Decimal

random.seed(2026)

D = dt.date
DT = dt.datetime
DATA_REF = D(2026, 10, 26)
AGORA = DT(2026, 10, 26, 13, 0)
INICIO = D(2026, 8, 3)
FIM = D(2026, 11, 27)
FERIADOS = {D(2026, 9, 7), D(2026, 10, 12), D(2026, 11, 2), D(2026, 11, 20)}


def pascoa(ano):
    a, b, c = ano % 19, ano // 100, ano % 100
    d, e = b // 4, b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = c // 4, c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    mes = (h + l - 7 * m + 114) // 31
    dia = ((h + l - 7 * m + 114) % 31) + 1
    return D(ano, mes, dia)


def feriado(d):
    """Feriados nacionais + 9 de Julho (a clínica fecha em todos)."""
    fixos = {(1, 1), (4, 21), (5, 1), (7, 9), (9, 7), (10, 12), (11, 2), (11, 15), (12, 25)}
    if d.year >= 2024:
        fixos.add((11, 20))
    return (d.month, d.day) in fixos or d == pascoa(d.year) - dt.timedelta(days=2)


def util(d):
    """O próprio dia, se for dia útil sem feriado; senão o próximo dia útil."""
    while d.weekday() >= 5 or feriado(d):
        d += dt.timedelta(days=1)
    return d


def util_antes(d):
    """O próprio dia, se for dia útil sem feriado; senão o dia útil anterior."""
    while d.weekday() >= 5 or feriado(d):
        d -= dt.timedelta(days=1)
    return d


def dias_uteis(a, b):
    d = a
    while d <= b:
        if d.weekday() < 5 and d not in FERIADOS:
            yield d
        d += dt.timedelta(days=1)


UTEIS = list(dias_uteis(INICIO, FIM))


def proximo_util(d, n=1):
    while n > 0:
        d += dt.timedelta(days=1)
        if d.weekday() < 5 and d not in FERIADOS:
            n -= 1
    return d


def util_anterior(d):
    d -= dt.timedelta(days=1)
    while d.weekday() >= 5 or d in FERIADOS:
        d -= dt.timedelta(days=1)
    return d


def hm(h, m):
    return dt.time(h, m)


def at(d, t):
    return DT.combine(d, t)


def money(x):
    return Decimal(str(round(x, 2))).quantize(Decimal("0.01"))


# ------------------------------------------------------------------ tabelas
TAB = {}          # nome -> (colunas, linhas)
ORDEM = []


def tabela(nome, colunas):
    TAB[nome] = (colunas, [])
    ORDEM.append(nome)


def ins(nome, **kw):
    cols, rows = TAB[nome]
    rows.append([kw.get(c) for c in cols])
    return kw


for nome, cols in [
    ("ESPECIALIDADE", "ID_ESPECIALIDADE NM_ESPECIALIDADE"),
    ("DENTISTA", "ID_DENTISTA ID_ESPECIALIDADE NM_DENTISTA ID_CRO DT_NASCIMENTO NR_TELEFONE DS_EMAIL DS_CHAVE_PIX DS_LOGRADOURO NR_ENDERECO DS_COMPLEMENTO NM_BAIRRO CD_CEP TP_VINCULO IN_ATIVO"),
    ("FUNCIONARIO", "ID_FUNCIONARIO NM_FUNCIONARIO TP_FUNCAO DT_NASCIMENTO TP_SEXO NR_TELEFONE DS_LOGRADOURO NR_ENDERECO DS_COMPLEMENTO NM_BAIRRO CD_CEP NM_BANCO NR_AGENCIA NR_CONTA DT_ADMISSAO DT_DESLIGAMENTO"),
    ("SALA", "ID_SALA NM_SALA HR_ABERTURA HR_FECHAMENTO"),
    ("CONVENIO", "ID_CONVENIO NM_CONVENIO IN_ATIVO"),
    ("PACIENTE", "ID_PACIENTE NM_PACIENTE DT_NASCIMENTO TP_SEXO ID_CPF ID_RG DS_PROFISSAO TP_ESTADO_CIVIL DS_LOGRADOURO NR_ENDERECO DS_COMPLEMENTO NM_BAIRRO CD_CEP DS_EMAIL ID_CONVENIO NR_CARTEIRINHA NM_RESPONSAVEL_LEGAL DT_CADASTRO"),
    ("TELEFONE_PACIENTE", "ID_PACIENTE NR_ORDEM NR_TELEFONE"),
    ("ANAMNESE", "ID_PACIENTE DT_PREENCHIMENTO TP_ASSINANTE DS_ARQUIVO_DIGITALIZADO IN_BEM_DE_SAUDE IN_TRATAMENTO_MEDICO IN_ALERGIA_MEDICAMENTO IN_DOENCA_GRAVE IN_USA_MEDICAMENTO IN_DIFICULDADE_ABRIR_BOCA QT_ESCOVACOES_DIA IN_DESMAIOS IN_REACAO_ANESTESICO IN_USOU_APARELHO IN_GRAVIDA_AMAMENTANDO IN_DIABETES IN_HIPERTENSAO IN_HEPATITE IN_PROBLEMA_RESPIRATORIO IN_PROBLEMA_CARDIACO IN_COMPLICACAO_TRATAMENTO DS_OBSERVACOES"),
    ("PROCEDIMENTO", "ID_PROCEDIMENTO ID_ESPECIALIDADE NM_PROCEDIMENTO TP_PROCEDIMENTO IN_ATIVO"),
    ("ORCAMENTO", "ID_ORCAMENTO ID_PACIENTE DT_ORCAMENTO DS_ORCAMENTO TP_SITUACAO"),
    ("ITEM_ORCAMENTO", "ID_ORCAMENTO NR_ITEM ID_PROCEDIMENTO CD_DENTE VL_ITEM"),
    ("PAGAMENTO", "ID_PAGAMENTO ID_ORCAMENTO DT_PAGAMENTO VL_PAGAMENTO TP_FORMA_PAGAMENTO QT_PARCELAS"),
    ("CONSULTA", "ID_CONSULTA ID_PACIENTE ID_DENTISTA ID_SALA DT_HR_INICIO QT_DURACAO_MIN TP_ATENDIMENTO TP_SITUACAO TP_MOTIVO_CANCELAMENTO DT_HR_REGISTRO DT_HR_CONFIRMACAO DS_OBSERVACAO TP_ATESTADO QT_DIAS_ATESTADO DS_CID_ATESTADO"),
    ("PROCEDIMENTO_REALIZADO", "ID_CONSULTA ID_PROCEDIMENTO CD_DENTE DS_OBSERVACAO"),
    ("GUIA", "ID_GUIA ID_CONSULTA DT_EMISSAO DT_HR_ASSINATURA DT_ENVIO VL_GUIA DT_RECEBIMENTO"),
    ("MEDICAMENTO", "ID_MEDICAMENTO NM_MEDICAMENTO DS_DOSAGEM DS_ORIENTACAO IN_CONTROLADO"),
    ("RECEITUARIO", "ID_CONSULTA ID_MEDICAMENTO"),
    ("LABORATORIO", "ID_LABORATORIO NM_LABORATORIO NR_WHATSAPP QT_DIAS_PRAZO"),
    ("PEDIDO_LABORATORIO", "ID_PEDIDO ID_CONSULTA ID_LABORATORIO TP_PEDIDO DS_PECA CD_DENTE DT_ENVIO DT_PREVISTA DT_CHEGADA"),
    ("TESTE_AUTOCLAVE", "ID_TESTE ID_FUNCIONARIO DT_TESTE TP_RESULTADO DS_OBSERVACAO"),
    ("DESPESA", "ID_DESPESA DS_TITULO TP_CATEGORIA VL_DESPESA DT_VENCIMENTO DT_PAGAMENTO TP_FORMA_PAGAMENTO DS_DESPESA ID_DENTISTA"),
]:
    tabela(nome, cols.split())

# ------------------------------------------------------------- dados base
NOMES_F = ["Ana", "Beatriz", "Camila", "Daniela", "Eduarda", "Fernanda", "Gabriela", "Helena", "Isabela", "Juliana",
           "Larissa", "Mariana", "Natália", "Patrícia", "Renata", "Sabrina", "Tatiane", "Vanessa", "Yasmin", "Aline",
           "Bruna", "Carolina", "Débora", "Elaine", "Flávia", "Giovana", "Heloísa", "Ingrid", "Jéssica", "Karina",
           "Letícia", "Lívia", "Manuela", "Nicole", "Paula", "Rafaela", "Sofia", "Valéria", "Alice", "Laura"]
NOMES_M = ["André", "Bruno", "Caio", "Diego", "Eduardo", "Felipe", "Gustavo", "Henrique", "Igor", "João",
           "Lucas", "Marcelo", "Nicolas", "Otávio", "Pedro", "Rafael", "Samuel", "Thiago", "Vinícius", "Wagner",
           "Arthur", "Bernardo", "Daniel", "Enzo", "Fábio", "Gabriel", "Heitor", "Leonardo", "Matheus", "Murilo",
           "Paulo", "Ricardo", "Rodrigo", "Sérgio", "Tiago", "Davi", "Miguel", "Lorenzo", "Renan", "Alexandre"]
SOBRENOMES = ["Silva", "Santos", "Oliveira", "Souza", "Rodrigues", "Ferreira", "Alves", "Pereira", "Lima", "Gomes",
              "Costa", "Ribeiro", "Martins", "Carvalho", "Almeida", "Lopes", "Soares", "Fernandes", "Vieira", "Barbosa",
              "Rocha", "Dias", "Nascimento", "Andrade", "Moreira", "Nunes", "Marques", "Machado", "Mendes", "Freitas",
              "Cardoso", "Ramos", "Gonçalves", "Santana", "Teixeira", "Moura", "Pinto", "Araújo", "Correia", "Batista"]
RUAS = ["Rua das Acácias", "Rua dos Ipês", "Rua Projetada Um", "Avenida das Palmeiras", "Rua do Bosque",
        "Rua das Camélias", "Rua dos Jasmins", "Travessa da Paz", "Rua Esperança", "Rua das Hortênsias",
        "Rua Três Marias", "Avenida Central", "Rua das Orquídeas", "Rua da Harmonia", "Rua Boa Vista",
        "Rua dos Girassóis", "Rua Primavera", "Rua do Sol", "Rua das Violetas", "Rua Nova Aurora"]
BAIRROS = ["Cidade Mãe do Céu", "Tatuapé", "Vila Formosa", "Mooca", "Água Rasa", "Vila Carrão", "Penha",
           "Belém", "Jardim Anália Franco", "Vila Prudente", "Vila Matilde", "Aricanduva"]
PROFISSOES = ["Professora", "Engenheiro", "Analista administrativo", "Vendedor", "Enfermeira", "Autônomo",
              "Comerciante", "Advogada", "Motorista", "Auxiliar administrativo", "Contador", "Designer",
              "Técnico de informática", "Cabeleireira", "Aposentado", "Arquiteta", "Farmacêutica", "Do lar"]

CPFS = set()


def cpf():
    while True:
        n = [random.randint(0, 9) for _ in range(9)]
        if len(set(n)) == 1:
            continue
        s = sum((10 - i) * n[i] for i in range(9))
        n.append((s * 10 % 11) % 10)
        s = sum((11 - i) * n[i] for i in range(10))
        n.append((s * 10 % 11) % 10)
        c = "".join(map(str, n))
        if c not in CPFS:
            CPFS.add(c)
            return c


def celular():
    return "119" + "".join(str(random.randint(0, 9)) for _ in range(8))


def fixo():
    return "112" + "".join(str(random.randint(0, 9)) for _ in range(7))


def cep():
    return "03" + "".join(str(random.randint(0, 9)) for _ in range(6))


def nome_pessoa(sexo, sobrenome=None):
    pn = random.choice(NOMES_F if sexo == "F" else NOMES_M)
    s1 = random.choice(SOBRENOMES)
    s2 = sobrenome or random.choice(SOBRENOMES)
    while s2 == s1:
        s2 = random.choice(SOBRENOMES)
    return f"{pn} {s1} {s2}"


def sem_acento(s):
    t = str.maketrans("áàãâéêíóôõúçÁÀÃÂÉÊÍÓÔÕÚÇ", "aaaaeeiooouc" + "AAAAEEIOOOUC")
    return s.translate(t)


def email(nome, n):
    p = sem_acento(nome).lower().split()
    return f"{p[0]}.{p[-1]}{n}@exemplo.com.br"


def endereco():
    return dict(DS_LOGRADOURO=random.choice(RUAS), NR_ENDERECO=str(random.randint(10, 2400)),
                DS_COMPLEMENTO=random.choice([None, None, None, f"Apto {random.randint(11, 184)}", "Casa 2", f"Bloco {random.choice('ABC')}"]),
                NM_BAIRRO=random.choice(BAIRROS), CD_CEP=cep())


# ------------------------------------------------- cadastros fixos
ESPEC = ["Ortodontia", "Endodontia", "Implantodontia", "Harmonização orofacial (HOF)", "Prótese", "Periodontia", "Dentística"]
ORTO, ENDO, IMPL, HOF, PROT, PERIO, DENT = range(1, 8)
for i, e in enumerate(ESPEC, 1):
    ins("ESPECIALIDADE", ID_ESPECIALIDADE=i, NM_ESPECIALIDADE=e)

DENTISTAS = {}
crolist = random.sample(range(40000, 140000), 7)
for i in range(1, 8):
    sexo = random.choice("FM") if i != HOF else "F"
    nome = ("Dra. " if sexo == "F" else "Dr. ") + nome_pessoa(sexo)
    DENTISTAS[i] = nome
    ins("DENTISTA", ID_DENTISTA=i, ID_ESPECIALIDADE=i, NM_DENTISTA=nome, ID_CRO=str(crolist[i - 1]),
        DT_NASCIMENTO=D(random.randint(1972, 1993), random.randint(1, 12), random.randint(1, 28)),
        NR_TELEFONE=celular(), DS_EMAIL=None if i == PERIO else email(nome.split(" ", 1)[1], i),
        DS_CHAVE_PIX=celular() if i % 2 else email(nome.split(" ", 1)[1], 70 + i),
        TP_VINCULO="PROPRIETARIA" if i == HOF else "AUTONOMO", IN_ATIVO=True, **endereco())

FUNC = {}
for fid, func, sexo, adm, desl in [
    (1, "RECEPCIONISTA", "F", D(2019, 3, 11), None),
    (2, "AUXILIAR DE DENTISTA", "F", D(2021, 6, 1), None),
    (3, "AUXILIAR DE LIMPEZA", "F", D(2022, 2, 7), None),
    (4, "AUXILIAR DE DENTISTA", "M", D(2020, 9, 14), D(2026, 9, 15)),
]:
    FUNC[fid] = nome_pessoa(sexo)
    ins("FUNCIONARIO", ID_FUNCIONARIO=fid, NM_FUNCIONARIO=FUNC[fid], TP_FUNCAO=func,
        DT_NASCIMENTO=D(random.randint(1975, 2001), random.randint(1, 12), random.randint(1, 28)), TP_SEXO=sexo,
        NR_TELEFONE=celular(), NM_BANCO=random.choice(["Banco do Brasil", "Caixa", "Itaú", "Bradesco", "Nubank"]),
        NR_AGENCIA=str(random.randint(1000, 9999)), NR_CONTA=f"{random.randint(10000, 999999)}-{random.randint(0, 9)}",
        DT_ADMISSAO=adm, DT_DESLIGAMENTO=desl, **endereco())

ins("SALA", ID_SALA=1, NM_SALA="Sala 01", HR_ABERTURA=hm(14, 0), HR_FECHAMENTO=hm(18, 0))
ins("SALA", ID_SALA=2, NM_SALA="Sala 02", HR_ABERTURA=hm(8, 0), HR_FECHAMENTO=hm(18, 0))

CONV = ["Porto Seguro", "Hapvida", "SulAmérica", "Dentalpar", "MetLife"]
for i, c in enumerate(CONV, 1):
    ins("CONVENIO", ID_CONVENIO=i, NM_CONVENIO=c, IN_ATIVO=True)
VL_GUIA_ORTO = {1: 85, 2: 55, 3: 80, 4: 60, 5: 75}       # valor fictício pago por manutenção
PESO_CONV = [35, 30, 15, 10, 10]

PROC = {}
pid = 0
# procedimentos que usam a peça que voltou do laboratório (base da auditoria A04)
PROVA_PECA = {"Instalação de contenção", "Instalação de aparelho móvel", "Instalação de coroa sobre implante",
              "Prova de prótese", "Instalação de prótese", "Cimentação de facetas"}
for esp, nomes in [
    (ORTO, ["Manutenção ortodôntica", "Instalação de aparelho ortodôntico", "Moldagem para contenção",
            "Instalação de contenção", "Moldagem para aparelho móvel", "Instalação de aparelho móvel"]),
    (ENDO, ["Tratamento endodôntico", "Abertura coronária e pulpectomia", "Instrumentação de canais", "Obturação de canais"]),
    (IMPL, ["Implante dentário", "Coroa sobre implante", "Instalação de implante", "Reabertura e moldagem de implante",
            "Instalação de coroa sobre implante", "Controle de implante"]),
    (HOF, ["Toxina botulínica", "Preenchimento labial", "Bioestimulador de colágeno", "Preenchimento de olheiras",
           "Rinomodelação", "Retorno de HOF"]),
    (PROT, ["Prótese protocolo", "Moldagem para prótese", "Prova de prótese", "Instalação de prótese", "Ajuste de prótese"]),
    (PERIO, ["Tratamento periodontal completo", "Raspagem e alisamento radicular", "Manutenção periodontal"]),
    (DENT, ["Faceta em porcelana", "Preparo e moldagem para facetas", "Cimentação de facetas", "Controle de dentística"]),
]:
    for n in nomes:
        pid += 1
        PROC[n] = pid
        ins("PROCEDIMENTO", ID_PROCEDIMENTO=pid, ID_ESPECIALIDADE=esp, NM_PROCEDIMENTO=n,
            TP_PROCEDIMENTO="PROVA_PECA" if n in PROVA_PECA else "CLINICO", IN_ATIVO=True)
pid += 1
ins("PROCEDIMENTO", ID_PROCEDIMENTO=pid, ID_ESPECIALIDADE=ORTO, NM_PROCEDIMENTO="Documentação ortodôntica (descontinuado)",
    TP_PROCEDIMENTO="CLINICO", IN_ATIVO=False)
# Radiografia: procedimento de apoio, feito pela auxiliar para qualquer especialidade.
for n in ["Radiografia periapical", "Radiografia panorâmica"]:
    pid += 1
    PROC[n] = pid
    ins("PROCEDIMENTO", ID_PROCEDIMENTO=pid, ID_ESPECIALIDADE=None, NM_PROCEDIMENTO=n, TP_PROCEDIMENTO="RADIOGRAFIA", IN_ATIVO=True)

MEDS = [
    ("Dipirona 500 mg", "1 comprimido", "Tomar a cada 6 horas em caso de dor, por até 3 dias.", False),
    ("Paracetamol 750 mg", "1 comprimido", "Tomar a cada 6 horas em caso de dor, por até 3 dias.", False),
    ("Ibuprofeno 600 mg", "1 comprimido", "Tomar a cada 8 horas, após as refeições, por 3 dias.", False),
    ("Nimesulida 100 mg", "1 comprimido", "Tomar a cada 12 horas, após as refeições, por 3 dias.", False),
    ("Amoxicilina 500 mg", "1 cápsula", "Tomar a cada 8 horas por 7 dias, sem interromper.", False),
    ("Azitromicina 500 mg", "1 comprimido", "Tomar 1 vez ao dia por 3 dias.", False),
    ("Dexametasona 4 mg", "1 comprimido", "Tomar 1 vez ao dia por 3 dias.", False),
    ("Digluconato de clorexidina 0,12%", "15 ml", "Bochechar por 1 minuto, 2 vezes ao dia, por 7 dias.", False),
    ("Paracetamol 500 mg + codeína 30 mg", "1 comprimido", "Tomar a cada 6 horas em caso de dor intensa, por até 3 dias.", True),
    ("Tramadol 50 mg", "1 cápsula", "Tomar a cada 8 horas em caso de dor intensa, por até 3 dias.", True),
    ("Ácido tranexâmico 250 mg", "2 comprimidos", "Tomar a cada 8 horas por 2 dias.", False),
    ("Benzocaína gel 20%", "aplicação local", "Aplicar na região dolorida até 4 vezes ao dia.", False),
]
for i, (n, dsg, ori, ctrl) in enumerate(MEDS, 1):
    ins("MEDICAMENTO", ID_MEDICAMENTO=i, NM_MEDICAMENTO=n, DS_DOSAGEM=dsg, DS_ORIENTACAO=ori, IN_CONTROLADO=ctrl)

ins("LABORATORIO", ID_LABORATORIO=1, NM_LABORATORIO="Laboratório Inove", NR_WHATSAPP=celular(), QT_DIAS_PRAZO=7)
ins("LABORATORIO", ID_LABORATORIO=2, NM_LABORATORIO="Laboratório Wilson", NR_WHATSAPP=celular(), QT_DIAS_PRAZO=7)

# --------------------------------------------------------------- pacientes
PAC = {}          # id -> dict
CARTEIRINHAS = set()


def idade(nasc, ref=DATA_REF):
    return ref.year - nasc.year - ((ref.month, ref.day) < (nasc.month, nasc.day))


def novo_paciente(menor=False, adulto_min=18, cadastro=None, convenio=None, sexo=None, sobrenome=None, sem_ficha=False):
    pid = len(PAC) + 1
    sexo = sexo or random.choice("FFM")
    if menor:
        nasc = D(random.randint(2010, 2016), random.randint(1, 12), random.randint(1, 28))
    else:
        nasc = D(random.randint(1955, 2026 - adulto_min - 1), random.randint(1, 12), random.randint(1, 28))
    nome = nome_pessoa(sexo, sobrenome)
    if cadastro is None:
        cadastro = D(random.randint(max(2013, nasc.year + 6 if menor else 2013), 2026), random.randint(1, 12), random.randint(1, 28))
        if cadastro >= INICIO:
            cadastro = D(2026, random.randint(1, 6), random.randint(1, 28))
    cadastro = util(cadastro)
    carteirinha = None
    if convenio:
        while True:
            carteirinha = "".join(str(random.randint(0, 9)) for _ in range(random.choice([12, 15, 16])))
            if (convenio, carteirinha) not in CARTEIRINHAS:
                CARTEIRINHAS.add((convenio, carteirinha))
                break
    p = dict(ID_PACIENTE=pid, NM_PACIENTE=nome, DT_NASCIMENTO=nasc, TP_SEXO=sexo, ID_CPF=cpf(),
             ID_RG="".join(str(random.randint(0, 9)) for _ in range(9)),
             DS_PROFISSAO="Estudante" if menor or idade(nasc) < 21 else random.choice(PROFISSOES),
             TP_ESTADO_CIVIL="SOLTEIRO" if menor or idade(nasc) < 23 else random.choice(
                 ["SOLTEIRO", "CASADO", "CASADO", "DIVORCIADO", "UNIAO ESTAVEL", "VIUVO"]),
             DS_EMAIL=email(nome, pid), ID_CONVENIO=convenio, NR_CARTEIRINHA=carteirinha,
             NM_RESPONSAVEL_LEGAL=None, DT_CADASTRO=cadastro,
             menor=menor, sem_ficha=sem_ficha, **endereco())
    PAC[pid] = p
    return pid


# Adultos sem consulta no período (cadastros antigos) — alguns são pais
# de pacientes menores (responsável legal que também é paciente). Criados
# primeiro para que o responsável tenha ID menor que o do menor (a FK do
# autorrelacionamento é conferida linha a linha no INSERT).
INATIVOS = [novo_paciente(convenio=random.choices(range(1, 6), PESO_CONV)[0] if random.random() < 0.2 else None)
            for _ in range(110)]

# Ortodontia: 240 pacientes em retorno a cada 4 semanas (60 horários fixos
# por semana na Sala 02 x 4 semanas). ~30% por convênio (~70 guias/mês).
ORTO_PAC = []
for k in range(240):
    menor = random.random() < 0.42
    conv = random.choices(range(1, 6), PESO_CONV)[0] if random.random() < 0.30 else None
    ORTO_PAC.append(novo_paciente(menor=menor, convenio=conv, adulto_min=18))
# 3 cadastros antigos (2014) sem ficha digitalizada — inconsistência para A01
for pid in ORTO_PAC[5:8]:
    PAC[pid]["sem_ficha"] = True
    PAC[pid]["DT_CADASTRO"] = D(2014, random.randint(2, 11), random.randint(1, 28))
    PAC[pid]["menor"] = False
    PAC[pid]["DT_NASCIMENTO"] = D(random.randint(1980, 1995), 5, 10)
    PAC[pid]["DS_PROFISSAO"] = random.choice(PROFISSOES)
# 12 pacientes novos de ortodontia começam no período (cadastro na 1ª consulta)
ORTO_NOVOS = set(ORTO_PAC[220:232])

# Menores de ortodontia: o nome do responsável fica no cadastro do menor
# (como na ficha). Em 14 casos o responsável também é paciente da clínica.
menores_orto = [p for p in ORTO_PAC if PAC[p]["menor"] and not PAC[p]["sem_ficha"]]
for i, pid in enumerate(menores_orto):
    if i < 14:   # responsável também é paciente: mesmo sobrenome final
        resp = INATIVOS[i]
        PAC[resp]["menor"] = False
        sob = PAC[resp]["NM_PACIENTE"].split()[-1]
        partes = PAC[pid]["NM_PACIENTE"].split()
        PAC[pid]["NM_PACIENTE"] = " ".join(partes[:-1] + [sob])
        PAC[pid]["NM_RESPONSAVEL_LEGAL"] = PAC[resp]["NM_PACIENTE"]
    elif i == 14:
        pass     # menor sem responsável informado — inconsistência para A02
    else:
        sob = PAC[pid]["NM_PACIENTE"].split()[-1]
        PAC[pid]["NM_RESPONSAVEL_LEGAL"] = nome_pessoa(random.choice("FM"), sob)
MENOR_SEM_RESP = menores_orto[14]
MENOR_ASSINOU = menores_orto[20]   # ficha de menor assinada pelo próprio paciente (A02)

# Pacientes de HOF: parte já cadastrada, parte nova no período.
HOF_EXISTENTES = [novo_paciente(sexo=random.choice("FFFFM"), adulto_min=22) for _ in range(60)]
# Endodontia, implante, prótese, periodontia, dentística
ENDO_EXIST = [novo_paciente(adulto_min=20, convenio=(1 if k < 2 else None)) for k in range(4)]
P_IMPL = novo_paciente(adulto_min=40, cadastro=D(2025, 11, 4))
P_PROT = novo_paciente(adulto_min=60, cadastro=D(2024, 3, 18))
P_PERIO = novo_paciente(adulto_min=35, cadastro=D(2026, 7, 21))
P_DENT = novo_paciente(adulto_min=25, cadastro=D(2026, 7, 28), sexo="F")
DUPLICADO = None   # criado no fim (D04)

# --------------------------------------------------------------- agenda
CONS = []          # lista de dicts
OCUP = {}          # (dia, sala, hora) -> id consulta  (só para montar a agenda)


def nova_consulta(pac, dent, sala, inicio, tipo, dur=45, registro=None, obs=None):
    cid = len(CONS) + 1
    c = dict(ID_CONSULTA=cid, ID_PACIENTE=pac, ID_DENTISTA=dent, ID_SALA=sala, ID_ORCAMENTO=None,
             DT_HR_INICIO=inicio, QT_DURACAO_MIN=dur, TP_ATENDIMENTO=tipo, TP_SITUACAO="CONFIRMAR",
             TP_MOTIVO_CANCELAMENTO=None, DT_HR_REGISTRO=registro, DT_HR_CONFIRMACAO=None, DS_OBSERVACAO=obs,
             procs=[])
    CONS.append(c)
    OCUP.setdefault((inicio.date(), sala, inicio.time()), []).append(c)
    return c


def livre(d, sala, h):
    return all(x["TP_SITUACAO"] == "CANCELADA" for x in OCUP.get((d, sala, h), []))


def tipo_de(pac):
    return "CONVENIO" if PAC[pac]["ID_CONVENIO"] else "PARTICULAR"


SLOTS_S2 = [hm(8, 0), hm(8, 45), hm(9, 30), hm(10, 15), hm(11, 0), hm(11, 45),
            hm(13, 15), hm(14, 0), hm(14, 45), hm(15, 30), hm(16, 15), hm(17, 0)]
ENCAIXE_S2 = hm(12, 30)        # intervalo usado para encaixes e remarcações
SLOTS_S1 = [hm(14, 0), hm(14, 45), hm(15, 30), hm(16, 15), hm(17, 0)]

semana0 = INICIO - dt.timedelta(days=INICIO.weekday())
# Ortodontia: paciente k -> (semana mod 4, dia da semana, horário)
orto_slot = {}
for k, pid in enumerate(ORTO_PAC):
    orto_slot[pid] = (k // 60, (k % 60) // 12, SLOTS_S2[k % 12])
primeira_visita = {}
DESISTENTES = set(ORTO_PAC[30:33])     # saíram sem marcar o retorno (G16)
NO_FERIADO = []                        # retornos que caíram em feriado
for d in [INICIO + dt.timedelta(days=i) for i in range((FIM - INICIO).days + 1)]:
    if d.weekday() >= 5:
        continue
    w = (d - semana0).days // 7
    for pid in ORTO_PAC:
        wk, wd, hr = orto_slot[pid]
        if w % 4 != wk or d.weekday() != wd:
            continue
        if pid in ORTO_NOVOS and pid not in primeira_visita:
            # novos pacientes começam ao longo do período (~1 por semana)
            if d < INICIO + dt.timedelta(days=6 * (ORTO_PAC.index(pid) - 220)):
                continue
        if pid in DESISTENTES and d > DATA_REF:
            continue
        if d in FERIADOS:
            NO_FERIADO.append((pid, d))
            continue
        primeira_visita.setdefault(pid, d)
        nova_consulta(pid, ORTO, 2, at(d, hr), tipo_de(pid))
# Retorno que caiu em feriado: encaixe às 12:30 (intervalo da Sala 02) nos
# dias úteis seguintes, um por dia.
for pid, d in NO_FERIADO:
    if pid not in primeira_visita:
        continue
    d2 = proximo_util(d)
    while d2 <= FIM and not livre(d2, 2, ENCAIXE_S2):
        d2 = proximo_util(d2)
    if d2 <= FIM:
        c = nova_consulta(pid, ORTO, 2, at(d2, ENCAIXE_S2), tipo_de(pid),
                          obs="Retorno remarcado: a data original caiu em feriado.")
        c["feriado"] = d

# HOF: até 3 atendimentos por tarde na Sala 01; tratamento de 3 a 6 sessões.
TRAT = []          # tratamentos HOF/ENDO: dict(pac, dent, sessoes, feitas, prox, consultas, itens)
HOF_ITENS = [
    [("Toxina botulínica", 1500), ("Preenchimento labial", 1500)],
    [("Bioestimulador de colágeno", 3000)],
    [("Toxina botulínica", 1200), ("Preenchimento de olheiras", 1800)],
    [("Rinomodelação", 2400)],
    [("Preenchimento labial", 1600), ("Preenchimento de olheiras", 2000)],
    [("Toxina botulínica", 1400), ("Bioestimulador de colágeno", 2200)],
]
hof_pool = list(HOF_EXISTENTES)
random.shuffle(hof_pool)


def novo_trat_hof(d):
    # tratamento que começa na agenda futura: paciente já cadastrado
    if hof_pool and (random.random() < 0.65 or d > DATA_REF):
        pac = hof_pool.pop()
    else:
        pac = novo_paciente(sexo=random.choice("FFFFM"), adulto_min=22, cadastro=d)
        PAC[pac]["novo_em"] = d
    t = dict(pac=pac, dent=HOF, sessoes=random.choice([3, 4, 4, 5, 5, 6]), feitas=0, prox=d,
             consultas=[], itens=random.choice(HOF_ITENS), intervalo=(7, 14))
    TRAT.append(t)
    return t


endo_pool = list(ENDO_EXIST)

# Tratamentos de HOF já em andamento em 03/08 (começaram e foram pagos em julho).
for k in range(14):
    prev = random.randint(1, 3)
    TRAT.append(dict(pac=hof_pool.pop(), dent=HOF, sessoes=random.choice([4, 5, 6]), feitas=prev, prev=prev,
                     prox=INICIO + dt.timedelta(days=random.randint(0, 9)), consultas=[], itens=random.choice(HOF_ITENS),
                     intervalo=(7, 14), pre_data=D(2026, 7, random.randint(6, 31))))


def novo_trat_endo(d):
    if endo_pool or d > DATA_REF:
        if not endo_pool:
            endo_pool.append(random.choice(INATIVOS[40:]))
        pac = endo_pool.pop()
    else:
        pac = novo_paciente(adulto_min=20, cadastro=d, convenio=(2 if random.random() < 0.25 else None))
        PAC[pac]["novo_em"] = d
    dente = random.choice(["36", "46", "26", "16", "37", "47", "11", "21", "24", "14"])
    t = dict(pac=pac, dent=ENDO, sessoes=3, feitas=0, prox=d, consultas=[], dente=dente,
             itens=[("Tratamento endodôntico", 1500)], intervalo=(7, 7))
    TRAT.append(t)
    return t


# Atendimentos mensais das demais especialidades (datas fixas, Sala 01).
FIXOS = {
    D(2026, 8, 6): (P_PROT, PROT), D(2026, 9, 3): (P_PROT, PROT), D(2026, 10, 1): (P_PROT, PROT), D(2026, 10, 29): (P_PROT, PROT),
    D(2026, 8, 12): (P_IMPL, IMPL), D(2026, 9, 9): (P_IMPL, IMPL), D(2026, 10, 7): (P_IMPL, IMPL), D(2026, 11, 4): (P_IMPL, IMPL),
    D(2026, 8, 18): (P_PERIO, PERIO), D(2026, 9, 15): (P_PERIO, PERIO), D(2026, 10, 20): (P_PERIO, PERIO),
    D(2026, 8, 25): (P_DENT, DENT), D(2026, 9, 22): (P_DENT, DENT), D(2026, 10, 22): (P_DENT, DENT),
}
FIXO_CONS = {}
for d in UTEIS:
    livres = list(SLOTS_S1)
    if d in FIXOS:
        pac, dent = FIXOS[d]
        hr = livres.pop(0)
        c = nova_consulta(pac, dent, 1, at(d, hr), "PARTICULAR")
        c["fixo"] = True
        FIXO_CONS[(pac, d)] = c
    if d.weekday() in (1, 3):          # endodontia às terças e quintas
        pend = [t for t in TRAT if t["dent"] == ENDO and t["feitas"] < t["sessoes"] and t["prox"] <= d]
        t = pend[0] if pend else novo_trat_endo(d)
        hr = livres.pop()
        c = nova_consulta(t["pac"], ENDO, 1, at(d, hr), tipo_de(t["pac"]), dur=60)
        c["trat"] = t
        t["consultas"].append(c)
        t["feitas"] += 1
        t["prox"] = d + dt.timedelta(days=7)
    n_hof = 3
    for _ in range(n_hof):
        if not livres:
            break
        pend = [t for t in TRAT if t["dent"] == HOF and t["feitas"] < t["sessoes"] and t["prox"] <= d
                and all(c["DT_HR_INICIO"].date() != d for c in t["consultas"])]
        t = pend[0] if pend else novo_trat_hof(d)
        hr = livres.pop(0)
        c = nova_consulta(t["pac"], HOF, 1, at(d, hr), "PARTICULAR")
        c["trat"] = t
        t["consultas"].append(c)
        t["feitas"] += 1
        t["prox"] = d + dt.timedelta(days=random.randint(*t["intervalo"]))

# ---------------------------------------------------- situação de cada consulta
CONS.sort(key=lambda c: (c["DT_HR_INICIO"], c["ID_SALA"]))
for i, c in enumerate(CONS, 1):
    c["ID_CONSULTA"] = i


def registro_padrao(c):
    """Quando a consulta foi registrada: no retorno anterior (ortodontia)
    ou 2 a 15 dias antes; sempre em horário de expediente."""
    ini = c["DT_HR_INICIO"]
    if c["ID_DENTISTA"] == ORTO:
        base = ini.date() - dt.timedelta(days=28)
        t = (DT.combine(base, ini.time()) + dt.timedelta(minutes=50))
    else:
        base = ini.date() - dt.timedelta(days=random.randint(2, 15))
        t = DT.combine(base, dt.time(random.randint(9, 16), random.choice([5, 20, 35, 50])))
    return t


# Faltas e cancelamentos: 15 por mês (levantamento), sorteados entre as
# consultas já passadas (outubro proporcional aos dias até a data de referência).
CANCELAR = set()
for (ano, mes), qt in [((2026, 8), 15), ((2026, 9), 15), ((2026, 10), 13)]:
    elegiveis = [c for c in CONS if (c["DT_HR_INICIO"].year, c["DT_HR_INICIO"].month) == (ano, mes)
                 and c["DT_HR_INICIO"] < AGORA - dt.timedelta(hours=1) and c.get("trat") is None and not c.get("fixo")]
    CANCELAR |= {id(c) for c in random.sample(elegiveis, qt)}

canceladas_aviso = []
for c in CONS:
    ini = c["DT_HR_INICIO"]
    c["DT_HR_REGISTRO"] = registro_padrao(c)
    if PAC[c["ID_PACIENTE"]].get("novo_em") == ini.date() or (c["ID_PACIENTE"] in ORTO_NOVOS and primeira_visita.get(c["ID_PACIENTE"]) == ini.date()):
        c["DT_HR_REGISTRO"] = DT.combine(util_anterior(ini.date()) - dt.timedelta(days=random.randint(1, 6)), dt.time(10, 30))
    if c["DT_HR_REGISTRO"] >= DT.combine(DATA_REF, dt.time(0, 0)):
        # agendamento futuro: registrado em algum dia útil antes de hoje
        dia = DATA_REF
        for _ in range(random.randint(1, 8)):
            dia = util_anterior(dia)
        c["DT_HR_REGISTRO"] = DT.combine(dia, dt.time(random.randint(9, 17), random.choice([0, 15, 30, 45])))
    vespera = util_anterior(ini.date())
    conf = DT.combine(vespera, dt.time(random.randint(9, 16), random.randint(0, 59)))
    if conf < c["DT_HR_REGISTRO"]:
        conf = c["DT_HR_REGISTRO"] + dt.timedelta(minutes=10)
    if ini.date() > DATA_REF:
        # futuro: amanhã já confirmado em parte; demais a confirmar
        if vespera == DATA_REF and random.random() < 0.6:
            c["TP_SITUACAO"] = "CONFIRMADA"
            c["DT_HR_CONFIRMACAO"] = DT.combine(DATA_REF, dt.time(random.randint(9, 12), random.randint(0, 59)))
        continue
    if ini >= AGORA or ini + dt.timedelta(minutes=c["QT_DURACAO_MIN"]) > AGORA:
        # consulta em curso às 13h fica EM ATENDIMENTO; as seguintes, CONFIRMADA
        c["TP_SITUACAO"] = "CONFIRMADA" if ini >= AGORA else "EM ATENDIMENTO"
        c["DT_HR_CONFIRMACAO"] = conf
        continue
    r = random.random()
    if id(c) in CANCELAR:
        motivo = random.choices(["AVISO_PACIENTE", "SEM_CONFIRMACAO", "FALTA"], [45, 20, 35])[0]
        c["TP_SITUACAO"] = "CANCELADA"
        c["TP_MOTIVO_CANCELAMENTO"] = motivo
        if motivo == "FALTA":
            c["DT_HR_CONFIRMACAO"] = conf
            c["DS_OBSERVACAO"] = "Paciente não compareceu e não avisou."
        elif motivo == "AVISO_PACIENTE":
            c["DT_HR_CONFIRMACAO"] = conf if random.random() < 0.5 else None
            c["DS_OBSERVACAO"] = "Paciente avisou com 24 horas de antecedência; remarcado."
            canceladas_aviso.append(c)
        else:
            c["DS_OBSERVACAO"] = "Sem confirmação até o fim do dia anterior; paciente avisado."
        continue
    c["TP_SITUACAO"] = "FINALIZADO"
    c["DT_HR_CONFIRMACAO"] = conf if random.random() < 0.97 else None

# Remarcações (consulta nova) para quem avisou: horário de reserva da Sala 02
# no próximo dia útil livre (ortodontia) ou Sala 01 livre.
extra = []
for c in canceladas_aviso:
    d = c["DT_HR_INICIO"].date()
    for k in range(1, 8):
        d2 = proximo_util(d, k)
        if d2 > FIM:
            break
        if c["ID_DENTISTA"] == ORTO:
            hs = [h for h in SLOTS_S2 + [ENCAIXE_S2] if livre(d2, 2, h)]
            if not hs:
                continue
            n = nova_consulta(c["ID_PACIENTE"], ORTO, 2, at(d2, hs[-1]), c["TP_ATENDIMENTO"])
        else:
            livres = [h for h in SLOTS_S1 if livre(d2, 1, h)]
            if not livres:
                continue
            n = nova_consulta(c["ID_PACIENTE"], c["ID_DENTISTA"], 1, at(d2, livres[-1]), c["TP_ATENDIMENTO"])
        n["DT_HR_REGISTRO"] = DT.combine(d - dt.timedelta(days=1), dt.time(11, 15))
        n["DS_OBSERVACAO"] = "Remarcação de consulta cancelada com aviso."
        extra.append(n)
        break

# P01 — paciente compareceu, mas a consulta combinada não estava na agenda
# (~1 vez por semana): registrada na chegada como CANCELADA/SEM_REGISTRO e
# remarcada para a próxima data livre.
semanas_hist = {}
for d in UTEIS:
    if d < DATA_REF:
        semanas_hist.setdefault((d - semana0).days // 7, []).append(d)
for w in sorted(semanas_hist):
    d = random.choice(semanas_hist[w])
    pac = random.choice(ORTO_PAC[:220])
    hr = random.choice(SLOTS_S2[:6])
    chegada = at(d, hr)
    n = nova_consulta(pac, ORTO, 2, chegada, tipo_de(pac),
                      obs="Paciente compareceu dizendo ter confirmado por WhatsApp; consulta não estava na agenda. Remarcado.")
    n["TP_SITUACAO"] = "CANCELADA"
    n["TP_MOTIVO_CANCELAMENTO"] = "SEM_REGISTRO"
    n["DT_HR_REGISTRO"] = chegada - dt.timedelta(minutes=5)
    d2 = proximo_util(d)
    while not any(livre(d2, 2, h) for h in SLOTS_S2) and d2 < FIM:
        d2 = proximo_util(d2)
    hs = [h for h in SLOTS_S2 if livre(d2, 2, h)]
    if hs:
        r = nova_consulta(pac, ORTO, 2, at(d2, hs[-1]), tipo_de(pac),
                          obs="Remarcação: consulta combinada que não tinha sido registrada (P01).")
        r["DT_HR_REGISTRO"] = chegada
        extra.append(r)
    extra.append(n)

for n in extra:
    if n["TP_SITUACAO"] == "CANCELADA":
        continue
    ini = n["DT_HR_INICIO"]
    if ini.date() > DATA_REF:
        n["TP_SITUACAO"] = "CONFIRMAR"
    elif ini >= AGORA:
        n["TP_SITUACAO"] = "CONFIRMADA"
        n["DT_HR_CONFIRMACAO"] = max(n["DT_HR_REGISTRO"], DT.combine(util_anterior(ini.date()), dt.time(15, 0)))
    else:
        n["TP_SITUACAO"] = "FINALIZADO"
        n["DT_HR_CONFIRMACAO"] = max(n["DT_HR_REGISTRO"] + dt.timedelta(minutes=5),
                                     DT.combine(util_anterior(ini.date()), dt.time(15, 0)))
        if n["DT_HR_CONFIRMACAO"] > ini:
            n["DT_HR_CONFIRMACAO"] = n["DT_HR_REGISTRO"]

CONS.sort(key=lambda c: (c["DT_HR_INICIO"], c["ID_SALA"], c["TP_SITUACAO"] != "CANCELADA"))
for i, c in enumerate(CONS, 1):
    c["ID_CONSULTA"] = i

# --------------------------------------- orçamentos, pagamentos, procedimentos
ORC = []
PAGS = []


def novo_orc(pac, data, desc, itens, situacao):
    oid = len(ORC) + 1
    o = dict(ID_ORCAMENTO=oid, ID_PACIENTE=pac, DT_ORCAMENTO=data, DS_ORCAMENTO=desc, TP_SITUACAO=situacao, itens=itens)
    ORC.append(o)
    return o


def pagar(o, data, valor, forma=None, parcelas=None):
    # Formas do levantamento: débito, ou crédito em 3x ou 6x sem juros.
    if forma is None:
        if valor <= 300:
            forma = random.choices(["DEBITO", "CREDITO"], [80, 20])[0]
        else:
            forma = random.choices(["DEBITO", "CREDITO"], [15, 85])[0]
    if parcelas is None:
        parcelas = 1 if forma == "DEBITO" else (3 if valor <= 300 else random.choice([3, 6, 6]))
    PAGS.append(dict(ID_PAGAMENTO=len(PAGS) + 1, ID_ORCAMENTO=o["ID_ORCAMENTO"], DT_PAGAMENTO=data,
                     VL_PAGAMENTO=money(valor), TP_FORMA_PAGAMENTO=forma, QT_PARCELAS=parcelas))


MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]

# Tratamentos que começaram antes do período (pagos antes de agosto).
o_prot = novo_orc(P_PROT, D(2026, 6, 10), "Prótese protocolo superior", [("Prótese protocolo", "SUP", 40000)], "APROVADO")
pagar(o_prot, D(2026, 6, 10), 25000, "CREDITO", 6)
pagar(o_prot, D(2026, 6, 10), 15000, "CREDITO", 6)
o_impl = novo_orc(P_IMPL, D(2026, 7, 15), "Implante unitário — dente 46", [("Implante dentário", "46", 2000), ("Coroa sobre implante", "46", 1000)], "APROVADO")
pagar(o_impl, D(2026, 7, 15), 3000, "CREDITO", 6)
o_perio = novo_orc(P_PERIO, D(2026, 8, 18), "Tratamento periodontal", [("Tratamento periodontal completo", "GER", 5000)], "APROVADO")
o_dent = novo_orc(P_DENT, D(2026, 8, 25), "Facetas em porcelana — 11, 21 e 12", [("Faceta em porcelana", "11", 1500), ("Faceta em porcelana", "21", 1500), ("Faceta em porcelana", "12", 1500)], "APROVADO")
ORC_FIXO = {P_PROT: o_prot, P_IMPL: o_impl, P_PERIO: o_perio, P_DENT: o_dent}

PROCS_FIXOS = {
    (P_PROT, D(2026, 8, 6)): [("Moldagem para prótese", "SUP")],
    (P_PROT, D(2026, 9, 3)): [("Prova de prótese", "SUP")],
    (P_PROT, D(2026, 10, 1)): [("Instalação de prótese", "SUP")],
    (P_PROT, D(2026, 10, 29)): [("Ajuste de prótese", "SUP")],
    (P_IMPL, D(2026, 8, 12)): [("Instalação de implante", "46")],
    (P_IMPL, D(2026, 9, 9)): [("Reabertura e moldagem de implante", "46")],
    (P_IMPL, D(2026, 10, 7)): [("Instalação de coroa sobre implante", "46")],
    (P_IMPL, D(2026, 11, 4)): [("Controle de implante", "46")],
    (P_PERIO, D(2026, 8, 18)): [("Raspagem e alisamento radicular", "SUP")],
    (P_PERIO, D(2026, 9, 15)): [("Raspagem e alisamento radicular", "INF")],
    (P_PERIO, D(2026, 10, 20)): [("Manutenção periodontal", "GER")],
    (P_DENT, D(2026, 8, 25)): [("Preparo e moldagem para facetas", "11"), ("Preparo e moldagem para facetas", "21"), ("Preparo e moldagem para facetas", "12")],
    (P_DENT, D(2026, 9, 22)): [("Cimentação de facetas", "11"), ("Cimentação de facetas", "21"), ("Cimentação de facetas", "12")],
    (P_DENT, D(2026, 10, 22)): [("Controle de dentística", "GER")],
}

for t in TRAT:
    if t.get("prev"):
        pd = t["pre_data"]
        pd = util_antes(pd)
        itens = [(nm, "GER", v) for nm, v in t["itens"]]
        t["orc"] = novo_orc(t["pac"], pd, "Harmonização orofacial — " + ", ".join(i[0].lower() for i in itens), itens, "APROVADO")
        pagar(t["orc"], pd, sum(i[2] for i in itens))
orto_mes = {}        # (paciente, ano, mes) -> orçamento
sem_pagamento = []   # A05
for c in CONS:
    ini = c["DT_HR_INICIO"]
    d = ini.date()
    pac = c["ID_PACIENTE"]
    fin = c["TP_SITUACAO"] == "FINALIZADO"
    if c["ID_DENTISTA"] == ORTO:
        if fin:
            primeira = (pac in ORTO_NOVOS and primeira_visita.get(pac) == d)
            proc = "Instalação de aparelho ortodôntico" if primeira else "Manutenção ortodôntica"
            c["procs"] = [(proc, "GER" if primeira else "GER")]
            if c["TP_ATENDIMENTO"] == "PARTICULAR":
                chave = (pac, d.year, d.month)
                if chave in orto_mes:      # 2ª consulta no mês (remarcação) usa o mesmo orçamento
                    c["ID_ORCAMENTO"] = orto_mes[chave]["ID_ORCAMENTO"]
                else:
                    o = novo_orc(pac, d, f"Ortodontia — {MESES[d.month - 1]}/{d.year}",
                                 [("Manutenção ortodôntica", "GER", 180)], "CONCLUIDO")
                    orto_mes[chave] = o
                    c["ID_ORCAMENTO"] = o["ID_ORCAMENTO"]
                    pagar(o, d, 180)
        continue
    if c["ID_DENTISTA"] in (HOF, ENDO) and c.get("trat"):
        t = c["trat"]
        if not fin:
            continue
        n = [x for x in t["consultas"] if x["TP_SITUACAO"] == "FINALIZADO"].index(c) + t.get("prev", 0)
        if n == 0 and c["TP_ATENDIMENTO"] == "PARTICULAR":
            fator = 1 if c["ID_DENTISTA"] == ENDO else random.choice([0.9, 1.0, 1.0, 1.1])
            itens = [(nm, t.get("dente", "GER"), round(v * fator / 50) * 50) for nm, v in t["itens"]]
            desc = ("Tratamento endodôntico — dente " + t["dente"]) if c["ID_DENTISTA"] == ENDO else "Harmonização orofacial — " + ", ".join(i[0].lower() for i in itens)
            o = novo_orc(pac, d, desc, itens, "APROVADO")
            t["orc"] = o
            pagar(o, d, sum(i[2] for i in itens))
        if c["TP_ATENDIMENTO"] == "PARTICULAR":
            c["ID_ORCAMENTO"] = t["orc"]["ID_ORCAMENTO"]
        if c["ID_DENTISTA"] == ENDO:
            c["procs"] = [(["Abertura coronária e pulpectomia", "Instrumentação de canais", "Obturação de canais"][min(n, 2)], t["dente"])]
        else:
            nm = t["itens"][n % len(t["itens"])][0] if n < len(t["itens"]) else "Retorno de HOF"
            c["procs"] = [(nm, "GER")]
        continue
    if (pac, d) in PROCS_FIXOS and fin:
        c["procs"] = PROCS_FIXOS[(pac, d)]
        o = ORC_FIXO[pac]
        c["ID_ORCAMENTO"] = o["ID_ORCAMENTO"]
        if pac in (P_PERIO, P_DENT) and d in (D(2026, 8, 18), D(2026, 8, 25)):
            total = sum(i[2] for i in o["itens"])
            pagar(o, d, total, "CREDITO", 6)

# Situação final dos tratamentos de HOF/endodontia: CONCLUIDO quando todas as
# sessões já aconteceram até a data de referência.
for t in TRAT:
    if "orc" in t:
        feitas = [x for x in t["consultas"] if x["TP_SITUACAO"] == "FINALIZADO"]
        if len(feitas) + t.get("prev", 0) >= t["sessoes"] and feitas:
            t["orc"]["TP_SITUACAO"] = "CONCLUIDO"
            t["fim"] = feitas[-1]["DT_HR_INICIO"].date()
for o, fim in [(o_prot, D(2026, 10, 1)), (o_impl, D(2026, 10, 7)), (o_dent, D(2026, 9, 22))]:
    o["TP_SITUACAO"] = "CONCLUIDO"

# Orçamentos apresentados e não pagos (sem andamento): reprovados/em aberto.
for k in range(9):
    pac = random.choice(INATIVOS[20:] + HOF_EXISTENTES)
    d = random.choice([u for u in UTEIS if u <= DATA_REF])
    esc = random.choice([
        ("Implante unitário — dente 36", [("Implante dentário", "36", 2000), ("Coroa sobre implante", "36", 1000)]),
        ("Facetas em porcelana — 11 e 21", [("Faceta em porcelana", "11", 1500), ("Faceta em porcelana", "21", 1500)]),
        ("Harmonização orofacial — toxina botulínica", [("Toxina botulínica", "GER", 1500)]),
        ("Tratamento periodontal", [("Tratamento periodontal completo", "GER", 5000)]),
        ("Prótese protocolo inferior", [("Prótese protocolo", "INF", 40000)]),
    ])
    novo_orc(pac, d, esc[0], esc[1], "REPROVADO" if d < D(2026, 10, 10) else "EM ABERTO")

# Orçamento em aberto com dois itens (alvo do D02: paciente desiste de um item)
novo_orc(HOF_EXISTENTES[0], D(2026, 10, 19), "Facetas em porcelana — 11 e 21",
         [("Faceta em porcelana", "11", 1500), ("Faceta em porcelana", "21", 1500)], "EM ABERTO")

# ------------------------------------------------------- inconsistências
finalizadas = [c for c in CONS if c["TP_SITUACAO"] == "FINALIZADO"]
orto_part_out = [c for c in finalizadas if c["ID_DENTISTA"] == ORTO and c["TP_ATENDIMENTO"] == "PARTICULAR"
                 and D(2026, 10, 1) <= c["DT_HR_INICIO"].date() < DATA_REF and c["ID_ORCAMENTO"]]
# A05 — atendimento particular finalizado sem pagamento lançado (2 casos)
for c in orto_part_out[3:5]:
    o = next(o for o in ORC if o["ID_ORCAMENTO"] == c["ID_ORCAMENTO"])
    PAGS[:] = [p for p in PAGS if p["ID_ORCAMENTO"] != o["ID_ORCAMENTO"]]
    o["TP_SITUACAO"] = "EM ABERTO"
    c["DS_OBSERVACAO"] = None
# A11 — dois orçamentos de ortodontia do mesmo paciente no mesmo mês
c_dup = orto_part_out[10]
o_dup = novo_orc(c_dup["ID_PACIENTE"], c_dup["DT_HR_INICIO"].date(),
                 f"Ortodontia — {MESES[c_dup['DT_HR_INICIO'].month - 1]}/2026", [("Manutenção ortodôntica", "GER", 180)], "EM ABERTO")
# (A consulta ligada ao orçamento de outro paciente agora é barrada pela FK
#  composta CONSULTA (ID_ORCAMENTO, ID_PACIENTE) -> ORCAMENTO.)
# A10 — consultas passadas que ficaram como CONFIRMADA (sem desfecho)
for c in [c for c in finalizadas if c["DT_HR_INICIO"].date() in (D(2026, 10, 21), D(2026, 10, 22)) and c["ID_DENTISTA"] == ORTO
          and c["TP_ATENDIMENTO"] == "CONVENIO"][:2]:
    c["TP_SITUACAO"] = "CONFIRMADA"
    c["procs"] = []
# A09 — consulta de endodontia lançada na Sala 01 pela manhã (sala fechada)
c_fora = next(c for c in finalizadas if c["ID_DENTISTA"] == ENDO and c["DT_HR_INICIO"].date() == D(2026, 9, 24))
c_fora["DT_HR_INICIO"] = at(D(2026, 9, 24), hm(10, 0))
# A08 — encaixe sobreposto na Sala 01 (HOF às 14:00 e encaixe às 14:20)
hof_ref = next(c for c in finalizadas if c["ID_DENTISTA"] == HOF and c["DT_HR_INICIO"].date() == D(2026, 10, 14)
               and c["DT_HR_INICIO"].time() == hm(14, 0))
pac_encaixe = random.choice(HOF_EXISTENTES)
enc = nova_consulta(pac_encaixe, PERIO, 1, at(D(2026, 10, 14), hm(14, 20)), "PARTICULAR",
                    registro=at(D(2026, 10, 14), hm(14, 10)), obs="Encaixe para avaliação periodontal.")
enc["TP_SITUACAO"] = "FINALIZADO"
enc["DT_HR_CONFIRMACAO"] = at(D(2026, 10, 14), hm(14, 10))
o_enc = novo_orc(pac_encaixe, D(2026, 10, 14), "Avaliação periodontal", [("Manutenção periodontal", "GER", 250)], "CONCLUIDO")
pagar(o_enc, D(2026, 10, 14), 250, "DEBITO", 1)
enc["ID_ORCAMENTO"] = o_enc["ID_ORCAMENTO"]
enc["procs"] = [("Manutenção periodontal", "GER")]
# A04 — prova da prótese marcada antes de o ajuste voltar do laboratório
d_a04 = D(2026, 9, 8)
h_a04 = next(h for h in SLOTS_S1 if livre(d_a04, 1, h))
a04 = nova_consulta(P_PROT, PROT, 1, at(d_a04, h_a04), "PARTICULAR", registro=at(D(2026, 9, 4), hm(10, 30)),
                    obs="Prova da prótese marcada antes de o ajuste voltar do laboratório.")
a04["TP_SITUACAO"] = "FINALIZADO"
a04["DT_HR_CONFIRMACAO"] = at(D(2026, 9, 4), hm(16, 0))
a04["procs"] = [("Prova de prótese", "SUP")]

CONS.sort(key=lambda c: (c["DT_HR_INICIO"], c["ID_SALA"], c["TP_SITUACAO"] != "CANCELADA"))
for i, c in enumerate(CONS, 1):
    c["ID_CONSULTA"] = i
finalizadas = [c for c in CONS if c["TP_SITUACAO"] == "FINALIZADO"]

# --------------------------------------------------------------- guias
GUIAS = []
for c in CONS:
    if c["TP_ATENDIMENTO"] != "CONVENIO" or c["TP_SITUACAO"] not in ("FINALIZADO", "CONFIRMADA") or c["DT_HR_INICIO"] > AGORA:
        continue
    if c["TP_SITUACAO"] == "CONFIRMADA" and c["DT_HR_INICIO"].date() >= DATA_REF:
        continue
    pac = c["ID_PACIENTE"]
    conv = PAC[pac]["ID_CONVENIO"]
    ini = c["DT_HR_INICIO"]
    d = ini.date()
    valor = VL_GUIA_ORTO[conv] if c["ID_DENTISTA"] == ORTO else {1: 260, 2: 190}.get(conv, 220)
    if d >= D(2026, 10, 1) or random.random() < 0.88:
        ass = max(ini - dt.timedelta(minutes=random.randint(5, 25)), DT.combine(d, dt.time(8, 0)))
    else:   # P02 (antes da regra de outubro): paciente voltou depois para assinar
        ass = DT.combine(proximo_util(d, random.randint(2, 9)), dt.time(random.randint(9, 17), random.randint(0, 59)))
    envio = proximo_util(ass.date(), random.choice([0, 1, 1, 2])) if True else None
    if ass > AGORA:
        ass, envio = None, None
    elif envio and envio > DATA_REF:
        envio = None
    receb = None
    if envio:
        m = envio.month if envio.day < 15 else envio.month + 1
        prev = D(2026, m, 30) if m != 2 else D(2026, 2, 28)
        if prev <= DATA_REF:
            receb = prev
    GUIAS.append(dict(ID_GUIA=len(GUIAS) + 1, ID_CONSULTA=c["ID_CONSULTA"], ID_CONVENIO=conv, DT_EMISSAO=d,
                      DT_HR_ASSINATURA=ass, DT_ENVIO=envio, VL_GUIA=money(valor), DT_RECEBIMENTO=receb, cons=c))
# P02 histórico: duas guias de setembro que nunca foram assinadas
for g in [g for g in GUIAS if g["DT_EMISSAO"].month == 9][7:9]:
    g["DT_HR_ASSINATURA"] = None
    g["DT_ENVIO"] = None
    g["DT_RECEBIMENTO"] = None
# A03 — guia de outubro assinada depois do atendimento (contra a regra nova)
g = [g for g in GUIAS if g["DT_EMISSAO"] >= D(2026, 10, 5)][4]
g["DT_HR_ASSINATURA"] = DT.combine(proximo_util(g["DT_EMISSAO"], 2), dt.time(10, 40))
g["DT_ENVIO"] = proximo_util(g["DT_EMISSAO"], 2)
g["DT_RECEBIMENTO"] = None
# A06 — guia lançada por engano em consulta particular
c_g = [c for c in finalizadas if c["ID_DENTISTA"] == ORTO and c["TP_ATENDIMENTO"] == "PARTICULAR"
       and c["DT_HR_INICIO"].date() == D(2026, 9, 17)][0]
GUIAS.append(dict(ID_GUIA=len(GUIAS) + 1, ID_CONSULTA=c_g["ID_CONSULTA"], ID_CONVENIO=1, DT_EMISSAO=D(2026, 9, 17),
                  DT_HR_ASSINATURA=c_g["DT_HR_INICIO"], DT_ENVIO=D(2026, 9, 18),
                  VL_GUIA=money(85), DT_RECEBIMENTO=None, cons=c_g))

# A14 — paciente atendido por convênio cujo cadastro ficou sem convênio e
# carteirinha (dados apagados por engano na atualização do cadastro)
p_a14 = next(c["ID_PACIENTE"] for c in finalizadas if c["TP_ATENDIMENTO"] == "CONVENIO" and c["ID_DENTISTA"] == ORTO
             and c["DT_HR_INICIO"].date() >= D(2026, 10, 5))
PAC[p_a14]["ID_CONVENIO"] = None
PAC[p_a14]["NR_CARTEIRINHA"] = None

# --------------------------------------------------- peças protéticas
PECAS, ENVIOS = [], []


def cons_de(pac, d):
    return next(c for c in CONS if c["ID_PACIENTE"] == pac and c["DT_HR_INICIO"].date() == d and c["TP_SITUACAO"] != "CANCELADA")


def nova_peca(origem, lab, desc, dente, prova=None):
    p = dict(ID_PECA=len(PECAS) + 1, ID_CONSULTA_ORIGEM=origem["ID_CONSULTA"], ID_LABORATORIO=lab,
             ID_CONSULTA_PROVA=prova["ID_CONSULTA"] if prova else None, DS_PECA=desc, CD_DENTE=dente, origem=origem)
    PECAS.append(p)
    return p


def envio(p, tipo, d, chegada_dias, custo, uber=True):
    n = len([e for e in ENVIOS if e["ID_PECA"] == p["ID_PECA"]]) + 1
    ch = util(d + dt.timedelta(days=chegada_dias)) if chegada_dias is not None else None
    if ch and ch > DATA_REF:
        ch = None
    e = dict(ID_PECA=p["ID_PECA"], NR_ENVIO=n, TP_ENVIO=tipo, DT_ENVIO=d, DT_PREVISTA=d + dt.timedelta(days=7),
             DT_CHEGADA=ch, custo=custo, uber=uber)
    ENVIOS.append(e)
    return e


p = nova_peca(cons_de(P_PROT, D(2026, 8, 6)), 1, "Prótese protocolo superior", "SUP", cons_de(P_PROT, D(2026, 9, 3)))
envio(p, "CONFECCAO", D(2026, 8, 6), 7, 3500)
envio(p, "AJUSTE", D(2026, 9, 3), 6, 400)
p = nova_peca(cons_de(P_IMPL, D(2026, 9, 9)), 2, "Coroa sobre implante", "46", cons_de(P_IMPL, D(2026, 10, 7)))
envio(p, "CONFECCAO", D(2026, 9, 9), 6, 700, uber=False)
p = nova_peca(cons_de(P_DENT, D(2026, 8, 25)), 1, "Facetas em porcelana (11, 21 e 12)", "GER", cons_de(P_DENT, D(2026, 9, 22)))
envio(p, "CONFECCAO", D(2026, 8, 25), 7, 1800)
envio(p, "REFINAMENTO", D(2026, 9, 1), 5, 250)

# Contenções e aparelhos móveis de ortodontia (moldagem numa consulta,
# prova na consulta seguinte do paciente, depois da chegada).
orto_fin = [c for c in finalizadas if c["ID_DENTISTA"] == ORTO and c["TP_ATENDIMENTO"] == "PARTICULAR"]
alvos = [D(2026, 8, 11), D(2026, 8, 20), D(2026, 9, 1), D(2026, 9, 14), D(2026, 9, 28), D(2026, 10, 6), D(2026, 10, 21)]
for k, alvo in enumerate(alvos):
    c = next(c for c in orto_fin if c["DT_HR_INICIO"].date() >= alvo and not c.get("peca"))
    c["peca"] = True
    desc, mold = (("Contenção ortodôntica superior", "Moldagem para contenção") if k % 2 == 0
                  else ("Aparelho ortodôntico móvel", "Moldagem para aparelho móvel"))
    c["procs"] = c["procs"] + [(mold, "SUP")]
    seguinte = next((x for x in CONS if x["ID_PACIENTE"] == c["ID_PACIENTE"] and x["DT_HR_INICIO"] > c["DT_HR_INICIO"]
                     and x["TP_SITUACAO"] != "CANCELADA"), None)
    d = c["DT_HR_INICIO"].date()
    dias = random.choice([5, 6, 7])
    prova = seguinte if (seguinte and seguinte["DT_HR_INICIO"].date() >= d + dt.timedelta(days=dias) and alvo != D(2026, 10, 21)) else None
    p = nova_peca(c, k % 2 + 1, desc, "SUP", prova)
    envio(p, "CONFECCAO", d, None if alvo == D(2026, 10, 21) else dias, 250 if k % 2 == 0 else 350, uber=(k % 3 != 0))
    if prova and prova["TP_SITUACAO"] == "FINALIZADO":
        prova["procs"] = prova["procs"] + [("Instalação de contenção" if k % 2 == 0 else "Instalação de aparelho móvel", "SUP")]
# Cada ida ao laboratório vira um PEDIDO_LABORATORIO. O pedido de confecção
# nasce na consulta de moldagem; o de ajuste, na consulta de prova em que o
# ajuste foi pedido (ou, sem prova, na consulta de origem).
PEDIDOS = []
for e in sorted(ENVIOS, key=lambda e: (e["DT_ENVIO"], e["ID_PECA"], e["NR_ENVIO"])):
    pc = PECAS[e["ID_PECA"] - 1]
    cons = pc["origem"]
    if e["TP_ENVIO"] != "CONFECCAO" and pc["ID_CONSULTA_PROVA"]:
        cp = next(x for x in CONS if x["ID_CONSULTA"] == pc["ID_CONSULTA_PROVA"])
        if cp["DT_HR_INICIO"].date() == e["DT_ENVIO"]:
            cons = cp
    e["ID_PEDIDO"] = len(PEDIDOS) + 1
    PEDIDOS.append(dict(ID_PEDIDO=e["ID_PEDIDO"], ID_CONSULTA=cons["ID_CONSULTA"], ID_LABORATORIO=pc["ID_LABORATORIO"],
                        TP_PEDIDO=e["TP_ENVIO"], DS_PECA=pc["DS_PECA"], CD_DENTE=pc["CD_DENTE"], DT_ENVIO=e["DT_ENVIO"],
                        DT_PREVISTA=e["DT_PREVISTA"], DT_CHEGADA=e["DT_CHEGADA"]))

# ------------------------------------- receitas, radiografias e atestados
# Receita = medicamentos receitados na consulta (RECEITUARIO consulta x medicamento).
RECEITAS = set()
fin_hist = [c for c in finalizadas if c["DT_HR_INICIO"] < AGORA and c["TP_SITUACAO"] == "FINALIZADO"]


def receita(c, meds):
    for m in meds:
        RECEITAS.add((c["ID_CONSULTA"], m))


for c in fin_hist:
    if c["ID_DENTISTA"] == ENDO and c["procs"] and c["procs"][0][0].startswith("Abertura"):
        receita(c, random.choice([[3], [1, 8], [2], [9]]))
    elif c["ID_DENTISTA"] == IMPL and c["procs"] and c["procs"][0][0] == "Instalação de implante":
        receita(c, [5, 3, 8])
    elif c["ID_DENTISTA"] == PERIO and c["procs"] and c["procs"][0][0].startswith("Raspagem"):
        receita(c, [8, 1])
outros = [c for c in fin_hist if c["ID_DENTISTA"] in (ORTO, HOF)]
for c in random.sample(outros, 34):
    receita(c, random.choice([[1], [2], [3], [12], [1, 12], [4], [7], [10], [6]]))
# A07 — receita lançada numa consulta cancelada (falta)
c_falta = next(c for c in CONS if c["TP_MOTIVO_CANCELAMENTO"] == "FALTA" and c["DT_HR_INICIO"].month == 10)
receita(c_falta, [1])

# Radiografia (~10 por mês): procedimento realizado na consulta; a avaliação
# da Dra. fica na observação. As de 22 e 23/10 ainda não foram avaliadas.
cand_rx = [c for c in fin_hist if c["ID_DENTISTA"] in (ENDO, IMPL, PERIO)] + random.sample([c for c in fin_hist if c["ID_DENTISTA"] == ORTO], 16)
cand_rx = sorted(random.sample(cand_rx, 26), key=lambda c: c["DT_HR_INICIO"])
cand_rx += [c for c in fin_hist if c["ID_DENTISTA"] == ORTO and c["DT_HR_INICIO"].date() in (D(2026, 10, 22), D(2026, 10, 23))][:4]
for c in cand_rx:
    dente = c["procs"][0][1] if c["procs"] else "GER"
    nm = "Radiografia panorâmica" if dente in ("GER", "SUP", "INF") else "Radiografia periapical"
    dente = "GER" if nm == "Radiografia panorâmica" else dente
    av = None if c["DT_HR_INICIO"].date() >= D(2026, 10, 22) else "Avaliação: " + random.choice([
        "sem alterações periapicais.", "reabsorção óssea leve na região; acompanhar.", "canais bem obturados até o ápice.",
        "raízes paralelas, sem reabsorção radicular.", "implante osseointegrado, sem perda óssea.",
        "lesão periapical compatível com necrose pulpar."])
    c.setdefault("rx", []).append((nm, dente, av))

# Atestado (~7 por mês): no máximo um por consulta, guardado na própria consulta.
for c in random.sample(fin_hist, 22):
    if random.random() < 0.8:
        c["TP_ATESTADO"] = "PRESENCA"
    else:
        c["TP_ATESTADO"] = "DIAS"
        c["QT_DIAS_ATESTADO"] = random.choice([1, 1, 2, 3])
        c["DS_CID_ATESTADO"] = random.choice([None, "K04.0 — pulpite", "K08.1 — perda de dente por extração",
                                              "K05.3 — periodontite crônica"])

# ---------------------------------------------------- autoclave (semanal)
TESTES = []
d = D(2026, 8, 5)
while d <= DATA_REF:
    if d not in (D(2026, 9, 23),):        # A13 — semana sem teste anotado
        dia = d if d not in FERIADOS else proximo_util(d)
        func = 4 if dia < D(2026, 9, 15) and random.random() < 0.5 else 2
        if dia == D(2026, 8, 19):
            TESTES.append(dict(ID_TESTE=len(TESTES) + 1, ID_FUNCIONARIO=func, DT_TESTE=dia, TP_RESULTADO="REPROVADO",
                               DS_OBSERVACAO="Indicador biológico com crescimento; autoclave revisada e teste repetido."))
            TESTES.append(dict(ID_TESTE=len(TESTES) + 1, ID_FUNCIONARIO=func, DT_TESTE=dia + dt.timedelta(days=1),
                               TP_RESULTADO="APROVADO", DS_OBSERVACAO="Reteste após revisão."))
        else:
            TESTES.append(dict(ID_TESTE=len(TESTES) + 1, ID_FUNCIONARIO=func, DT_TESTE=dia, TP_RESULTADO="APROVADO", DS_OBSERVACAO=None))
    d += dt.timedelta(days=7)

# ---------------------------------------------------------------- despesas
DESP = []


def despesa(titulo, cat, valor, venc, forma, desc, pago=True, dent=None, pag_em=None):
    pg = None
    if pago:
        pg = util(pag_em or venc)
        if pg > DATA_REF:
            pg = None
    DESP.append(dict(ID_DESPESA=0, DS_TITULO=titulo, TP_CATEGORIA=cat, VL_DESPESA=money(valor), DT_VENCIMENTO=venc,
                     DT_PAGAMENTO=pg, TP_FORMA_PAGAMENTO=forma, DS_DESPESA=desc, ID_DENTISTA=dent))


def quinto_util(ano, mes):
    d = D(ano, mes, 1)
    n = 0
    while True:
        if d.weekday() < 5 and d not in FERIADOS:
            n += 1
            if n == 5:
                return d
        d += dt.timedelta(days=1)


receita_mes = {}
for p_ in PAGS:
    k = (p_["DT_PAGAMENTO"].year, p_["DT_PAGAMENTO"].month)
    receita_mes[k] = receita_mes.get(k, 0) + float(p_["VL_PAGAMENTO"])
for (ano, mes) in [(2026, 8), (2026, 9), (2026, 10), (2026, 11)]:
    nm = MESES[mes - 1]
    despesa(f"Condomínio — {nm}", "CONDOMINIO", 1250, D(ano, mes, 5), "BOLETO", "Taxa condominial da sala 26.")
    despesa(f"Internet — {nm}", "INTERNET", 149.90, D(ano, mes, 10), "BOLETO", "Plano de internet da clínica.")
    despesa(f"Água — {nm}", "AGUA", random.randint(105, 140), D(ano, mes, 15), "BOLETO", "Conta de água.",
            pago=not (mes == 10))       # conta de outubro vencida e não paga
    despesa(f"Luz — {nm}", "LUZ", random.randint(420, 520), D(ano, mes, 20), "BOLETO", "Conta de energia elétrica.")
    base = receita_mes.get((ano, mes - 1), 85000)
    despesa(f"Imposto — {nm}", "IMPOSTO", round(base * 0.06, 2), D(ano, mes, 20), "BOLETO", "Imposto sobre o faturamento do mês anterior.")
    venc = quinto_util(ano, mes)
    # o auxiliar desligado em 15/09 recebe agosto inteiro e meio mês de setembro
    ativos = [(1, 2300), (2, 2100), (3, 900)] + ([(4, 2100)] if mes <= 9 else [(4, 1050)] if mes == 10 else [])
    for fid, sal in ativos:
        despesa(f"Salário — {FUNC[fid].split()[0]} — {MESES[mes - 2]}", "SALARIO", sal, venc, "PIX",
                f"Pagamento do funcionário referente a {MESES[mes - 2]}.")
    despesa(f"Repasse ortodontia — {MESES[mes - 2]}", "REPASSE", 11500 + random.randint(-600, 600), venc, "PIX",
            f"Repasse mensal ao ortodontista referente a {MESES[mes - 2]} (valor combinado).", dent=ORTO)
    if mes <= 10:
        for _ in range(random.randint(2, 3)):
            dv = D(ano, mes, random.randint(3, 27))
            despesa("Insumos odontológicos", "INSUMOS", random.randint(380, 1600), dv, random.choice(["PIX", "BOLETO"]),
                    random.choice(["Luvas, máscaras e gorros.", "Anestésicos e agulhas.", "Resinas e materiais de moldagem.",
                                   "Material de esterilização (envelopes e indicadores).", "Fios e braquetes ortodônticos."]))
        despesa("Correios", "CORREIOS", random.randint(25, 48), D(ano, mes, random.randint(5, 25)), "PIX", "Envio de documentos.")
# Repasse no fim do tratamento (endodontia, implante, prótese, dentística)
for t in TRAT:
    if t["dent"] == ENDO and t.get("fim"):
        despesa("Repasse endodontia", "REPASSE", 600, proximo_util(t["fim"], 3), "PIX",
                f"Repasse ao endodontista: tratamento concluído em {t['fim']:%d/%m/%Y}.", dent=ENDO)
despesa("Repasse prótese", "REPASSE", 12000, D(2026, 10, 6), "PIX", "Repasse ao protesista: protocolo superior concluído.", dent=PROT)
despesa("Repasse implantodontia", "REPASSE", 1200, D(2026, 10, 13), "PIX", "Repasse ao implantodontista: implante unitário concluído.", dent=IMPL)
despesa("Repasse dentística", "REPASSE", 1800, D(2026, 9, 28), "PIX", "Repasse ao dentista de dentística: facetas concluídas.", dent=DENT)
# Laboratório (uma despesa por ida da peça) e Uber
for e in ENVIOS:
    p = PECAS[e["ID_PECA"] - 1]
    lab = "Inove" if p["ID_LABORATORIO"] == 1 else "Wilson"
    venc = e["DT_CHEGADA"] or e["DT_PREVISTA"]
    despesa(f"Laboratório {lab} — {p['DS_PECA'].lower()}", "LABORATORIO", e["custo"], venc, "PIX",
            f"{ {'CONFECCAO': 'Confecção', 'AJUSTE': 'Ajuste', 'REFINAMENTO': 'Refinamento'}[e['TP_ENVIO']] } da peça — pedido nº {e['ID_PEDIDO']}.", pago=e["DT_CHEGADA"] is not None)
    if e["uber"]:
        despesa("Uber — envio ao laboratório", "TRANSPORTE", random.randint(22, 36), e["DT_ENVIO"], "PIX",
                f"Envio da peça ao Laboratório {lab}.")
# D03 — conta de luz de outubro lançada em duplicidade (cópia não paga)
luz_out = next(x for x in DESP if x["DS_TITULO"] == "Luz — outubro")
despesa("Luz — outubro", "LUZ", float(luz_out["VL_DESPESA"]), D(2026, 10, 20), "BOLETO", luz_out["DS_DESPESA"], pago=False)
# Boleto de insumos vencido e ainda não pago (contas a pagar em atraso)
despesa("Insumos odontológicos", "INSUMOS", 742.50, D(2026, 10, 22), "BOLETO", "Resinas e materiais de moldagem.", pago=False)
DESP.sort(key=lambda x: (x["DT_VENCIMENTO"], x["TP_CATEGORIA"], x["DS_TITULO"]))
for i, x in enumerate(DESP, 1):
    x["ID_DESPESA"] = i

# Paciente cadastrado em duplicidade, sem histórico (alvo do D04).
orig = PAC[INATIVOS[60]]
DUPLICADO = novo_paciente(cadastro=D(2026, 10, 19))
PAC[DUPLICADO].update(NM_PACIENTE=orig["NM_PACIENTE"], DT_NASCIMENTO=orig["DT_NASCIMENTO"], TP_SEXO=orig["TP_SEXO"],
                       DS_EMAIL=orig["DS_EMAIL"].replace("@", ".dup@"), sem_ficha=True)

# --------------------------------------------------------------- pacientes
primeira_cons = {}
for c in CONS:
    primeira_cons.setdefault(c["ID_PACIENTE"], c["DT_HR_INICIO"])
primeira_ativa = {}
for c in CONS:
    if c["TP_SITUACAO"] != "CANCELADA":
        primeira_ativa.setdefault(c["ID_PACIENTE"], c)
for pid, p in PAC.items():
    novo = (pid in ORTO_NOVOS and pid in primeira_visita) or p.get("novo_em")
    if novo and pid in primeira_ativa:
        # paciente novo: cadastro feito no agendamento; ficha preenchida na
        # chegada, antes do 1º atendimento (RN01). Se o 1º atendimento ainda
        # não aconteceu, a ficha ainda não existe.
        c0 = primeira_ativa[pid]
        p["DT_CADASTRO"] = c0["DT_HR_REGISTRO"].date()
        p["ficha_em"] = c0["DT_HR_INICIO"].date()
        if c0["DT_HR_INICIO"] >= AGORA:
            p["sem_ficha"] = True
        continue
    if p["DT_CADASTRO"] < p["DT_NASCIMENTO"]:
        p["DT_CADASTRO"] = p["DT_NASCIMENTO"] + dt.timedelta(days=365 * 6)
    if pid in primeira_cons and p["DT_CADASTRO"] > primeira_cons[pid].date():
        p["DT_CADASTRO"] = primeira_cons[pid].date()
# Registro e confirmação só acontecem em dia útil (RP01): se a data caiu em
# fim de semana ou feriado, vale o dia útil anterior.
for c in CONS:
    r = c["DT_HR_REGISTRO"]
    if r.date() != util_antes(r.date()):
        c["DT_HR_REGISTRO"] = DT.combine(util_antes(r.date()), r.time())
    cf = c["DT_HR_CONFIRMACAO"]
    if cf and (cf.date() != util_antes(cf.date()) or cf < c["DT_HR_REGISTRO"]):
        c["DT_HR_CONFIRMACAO"] = max(c["DT_HR_REGISTRO"] + dt.timedelta(minutes=10),
                                     DT.combine(util_antes(cf.date()), cf.time()))
        if c["DT_HR_CONFIRMACAO"] > c["DT_HR_INICIO"]:
            c["DT_HR_CONFIRMACAO"] = c["DT_HR_REGISTRO"]
for pid, p in PAC.items():
    p["DT_CADASTRO"] = util_antes(p["DT_CADASTRO"])
for pid, p in PAC.items():
    ins("PACIENTE", **{k: v for k, v in p.items()})
    tels = [celular()] + ([random.choice([celular(), fixo()])] if random.random() < 0.35 else [])
    if pid == DUPLICADO:
        tels = [celular()]
    for k, t in enumerate(tels, 1):
        ins("TELEFONE_PACIENTE", ID_PACIENTE=pid, NR_ORDEM=k, NR_TELEFONE=t)
    if p.get("sem_ficha"):
        continue
    eh_menor = p["NM_RESPONSAVEL_LEGAL"] is not None or pid == MENOR_SEM_RESP
    mulher_fertil = p["TP_SEXO"] == "F" and 18 <= idade(p["DT_NASCIMENTO"]) <= 42
    f = lambda prob: random.random() < prob
    usa_med = f(0.22)
    obs = random.choice([None] * 6 + ["Alergia a dipirona.", "Usa losartana 50 mg.", "Asma controlada com bombinha.",
                                      "Alergia a penicilina.", "Usa metformina 850 mg.", "Ansiedade em tratamento odontológico."])
    ins("ANAMNESE", ID_PACIENTE=pid, DT_PREENCHIMENTO=p.get("ficha_em", p["DT_CADASTRO"]),
        TP_ASSINANTE="RESPONSAVEL" if idade(p["DT_NASCIMENTO"], p.get("ficha_em", p["DT_CADASTRO"])) < 18 and pid != MENOR_ASSINOU else "PACIENTE",
        DS_ARQUIVO_DIGITALIZADO=f"fichas/{p.get('ficha_em', p['DT_CADASTRO']):%Y}/anamnese_{pid:05d}.pdf",
        IN_BEM_DE_SAUDE=not f(0.08), IN_TRATAMENTO_MEDICO=f(0.12), IN_ALERGIA_MEDICAMENTO=f(0.10),
        IN_DOENCA_GRAVE=f(0.03), IN_USA_MEDICAMENTO=usa_med, IN_DIFICULDADE_ABRIR_BOCA=f(0.03),
        QT_ESCOVACOES_DIA=random.choice([1, 2, 2, 3, 3, 3]), IN_DESMAIOS=f(0.02), IN_REACAO_ANESTESICO=f(0.03),
        IN_USOU_APARELHO=(pid in ORTO_PAC) or f(0.2), IN_GRAVIDA_AMAMENTANDO=mulher_fertil and f(0.07),
        IN_DIABETES=(not eh_menor) and f(0.07), IN_HIPERTENSAO=(not eh_menor) and f(0.12), IN_HEPATITE=f(0.01),
        IN_PROBLEMA_RESPIRATORIO=f(0.06), IN_PROBLEMA_CARDIACO=(not eh_menor) and f(0.04),
        IN_COMPLICACAO_TRATAMENTO=f(0.03), DS_OBSERVACOES=obs)

for o in ORC:
    ins("ORCAMENTO", **o)
    for k, (nm, dente, v) in enumerate(o["itens"], 1):
        ins("ITEM_ORCAMENTO", ID_ORCAMENTO=o["ID_ORCAMENTO"], NR_ITEM=k, ID_PROCEDIMENTO=PROC[nm], CD_DENTE=dente, VL_ITEM=money(v))
PAGS.sort(key=lambda x: (x["DT_PAGAMENTO"], x["ID_PAGAMENTO"]))
for i, p_ in enumerate(PAGS, 1):
    p_["ID_PAGAMENTO"] = i
    ins("PAGAMENTO", **p_)
for c in CONS:
    ins("CONSULTA", **c)
    vistos = set()
    for nm, dente, obs in [(n, d, None) for n, d in c["procs"]] + c.get("rx", []):
        if (nm, dente) in vistos:
            continue
        vistos.add((nm, dente))
        ins("PROCEDIMENTO_REALIZADO", ID_CONSULTA=c["ID_CONSULTA"], ID_PROCEDIMENTO=PROC[nm], CD_DENTE=dente, DS_OBSERVACAO=obs)
for g in GUIAS:
    ins("GUIA", **g)
for c_id, m in sorted(RECEITAS):
    ins("RECEITUARIO", ID_CONSULTA=c_id, ID_MEDICAMENTO=m)
for pl in PEDIDOS:
    ins("PEDIDO_LABORATORIO", **pl)
for t in TESTES:
    ins("TESTE_AUTOCLAVE", **t)
for x in DESP:
    ins("DESPESA", **x)


# ------------------------------------------------------------------ saída
def lit(v):
    if v is None:
        return "NULL"
    if isinstance(v, bool):
        return "TRUE" if v else "FALSE"
    if isinstance(v, (int, Decimal)):
        return str(v)
    if isinstance(v, float):
        return f"{v:.2f}"
    if isinstance(v, DT):
        return f"'{v:%Y-%m-%d %H:%M:%S}'"
    if isinstance(v, D):
        return f"'{v:%Y-%m-%d}'"
    if isinstance(v, dt.time):
        return f"'{v:%H:%M:%S}'"
    return "'" + str(v).replace("\\", "\\\\").replace("'", "''") + "'"


linhas = []
total = 0
for nome in ORDEM:
    cols, rows = TAB[nome]
    total += len(rows)
    linhas.append(f"\n-- {nome}: {len(rows)} registros")
    for i in range(0, len(rows), 200):
        bloco = rows[i:i + 200]
        linhas.append(f"INSERT INTO {nome} ({', '.join(cols)}) VALUES")
        linhas.append(",\n".join("  (" + ", ".join(lit(v) for v in r) + ")" for r in bloco) + ";")
massa = "\n".join(linhas).strip()

aqui = os.path.dirname(os.path.abspath(__file__))
caminho = os.path.join(aqui, "script.sql")
txt = open(caminho, encoding="utf-8").read()
novo = re.sub(r"-- \[INICIO MASSA\].*?-- \[FIM MASSA\]",
              lambda m: "-- [INICIO MASSA]\n" + massa + "\n-- [FIM MASSA]", txt, flags=re.S)
open(caminho, "w", encoding="utf-8").write(novo)
print(f"{total} registros em {len(ORDEM)} tabelas")
for nome in ORDEM:
    print(f"  {nome:24s} {len(TAB[nome][1]):5d}")
