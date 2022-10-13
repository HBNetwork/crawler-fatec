from collections import namedtuple
from datetime import datetime
from decimal import Decimal
from pprint import pprint

import requests
from bs4 import BeautifulSoup

# só assim eu consegui mockar o now para testar a função get_ano_semestre
now = datetime.now


Fatec = namedtuple("Fatec", ["id", "nome"])
MaiorMenorNota = namedtuple("MaiorMenorNota", ["maior", "menor"])
Curso = namedtuple("Curso", ["id", "id_interno", "nome", "periodo", "id_fatec"])
Classificado = namedtuple(
    "Classificado", ["classificacao", "nota", "id_fatec", "id_curso"]
)
Demanda = namedtuple(
    "Demanda", ["nome_curso", "periodo", "inscritos", "vagas", "demanda", "nome_fatec"]
)
Resultado = namedtuple(
    "Resultado",
    [
        "cod_curso",
        "cod_instituicao",
        "ano",
        "semestre",
        "periodo",
        "qtde_vagas",
        "qtde_inscrito",
        "demanda",
        "nota_corte",
        "nota_maxima",
    ],
)
# Campos da tabela
# cod_curso,cod_instituicao,ano,semestre,periodo,qtde_vagas,qtde_inscrito,demanda,nota_corte,nota_maxima
def make_table():
    rows = []
    fatecs = get_fatecs()
    ano, semestre = get_ano_semestre()
    ano_sem = f"{ano}{semestre}"
    id_cursos = get_id_cursos()
    for fatec in fatecs:
        print(fatec)
        demandas = get_demandas_curso(fatec.nome, ano_sem)

        cursos = join_id_cursos(id_cursos, get_cursos(fatec.id))

        for curso in cursos:
            print(curso)
            vagas = None
            inscritos = None
            demanda = None
            for demanda in demandas:
                if (
                    demanda.nome_curso == curso.nome
                    and demanda.periodo == curso.periodo
                ):
                    vagas = demanda.vagas
                    inscritos = demanda.inscritos
                    demanda = demanda.demanda
                    break
            classificacao = get_maior_menor(
                get_classificados(fatec.id, curso.id_interno)
            )
            rows.append(
                Resultado(
                    curso.id,
                    fatec.id,
                    ano,
                    semestre,
                    curso.periodo,
                    vagas,
                    inscritos,
                    demanda,
                    classificacao.menor,
                    classificacao.maior,
                )
            )
    return rows


def join_id_cursos(id_cursos, cursos):
    cursos_id_correto = []
    for curso in cursos:
        cursos_id_correto.append(
            Curso(
                id_cursos[curso.nome],
                curso.id_interno,
                curso.nome,
                curso.periodo,
                curso.id_fatec,
            )
        )
    return cursos_id_correto


def get_ano_semestre():
    date_now = now()
    semestre = 1 if date_now.month <= 6 else 2
    ano = date_now.year
    return ano, semestre


def extrai_nome_periodo(nome_com_periodo):
    nome, periodo = (nome_com_periodo.replace(")", "")).split("(")
    return nome.strip(), periodo


def extrai_nome_fatec(nome_com_cidade):
    return "-".join(nome_com_cidade.split("-")[1:]).strip()


def get_fatecs():
    fatecs = []
    resp = requests.get("https://www.vestibularfatec.com.br/classificacao/fatec.asp")

    soup = BeautifulSoup(resp.content, "html.parser")
    for option in soup.find_all("option")[1:]:
        fatecs.append(Fatec(int(option["value"]), extrai_nome_fatec(option.text)))

    return fatecs


def get_cursos(id_fatec):
    cursos = []
    data = {"CodFatec": id_fatec}

    resp = requests.post(
        "https://www.vestibularfatec.com.br/classificacao/lista.asp", data=data
    )

    soup = BeautifulSoup(resp.content, "html.parser")

    for option in soup.find_all("option")[1:]:
        nome, periodo = extrai_nome_periodo(option.text)
        cursos.append(Curso(None, int(option["value"]), nome, periodo, id_fatec))

    return cursos


def get_classificados(id_fatec, id_curso, opcao=1):

    classificados = []

    data = {"CodFatec": id_fatec, "CodEscolaCurso": id_curso, "o": opcao}

    resp = requests.post(
        "https://www.vestibularfatec.com.br/classificacao/lista.asp", data=data
    )

    soup = BeautifulSoup(resp.content, "html.parser")
    for linha in soup.find_all("tr")[1:]:
        colunas = linha.find_all("td")
        if colunas[-1].text == "CLASSIFICADO":
            nota = Decimal(colunas[3].text.replace(",", "."))
            classificados.append(
                Classificado(int(colunas[0].text), nota, id_fatec, id_curso)
            )

    return classificados


def get_maior_menor(classificados):
    """
    A lista de classificação precisa esttar ordenada
    """
    return MaiorMenorNota(classificados[0].nota, classificados[-1].nota)


def get_demandas_curso(nome_fatec, id_semestre):
    demandas = []
    data = {
        "FATEC": nome_fatec,
        "ano-sem": id_semestre,
    }
    resp = requests.post(
        "https://www.vestibularfatec.com.br/demanda/demanda.asp", data=data
    )

    soup = BeautifulSoup(resp.content, "html.parser")

    for linha in soup.find_all("tr")[1:]:
        colunas = linha.find_all("td")
        demanda = Decimal(colunas[4].text.replace(",", "."))
        demandas.append(
            Demanda(
                colunas[0].text,
                colunas[1].text,
                int(colunas[2].text),
                int(colunas[3].text),
                demanda,
                nome_fatec,
            )
        )

    return demandas


def get_id_cursos():
    cursos = {}
    resp = requests.get("https://www.vestibularfatec.com.br/unidades-cursos/")

    soup = BeautifulSoup(resp.content, "html.parser")
    lista_cursos = soup.find(id="cursos").find_all("a")
    for a in lista_cursos:
        id_curso = int(a["href"].split("=")[1])
        nome_curso = a.text.strip()
        cursos[nome_curso] = id_curso

    return cursos


if "__main__" == __name__:
    # fatecs = get_fatecs()
    # print([x.nome for x in fatecs])
    # cursos = get_id_cursos()
    # pprint(cursos)

    table = make_table()
    pprint(table)

    # cursos = get_cursos(71)
    # print(cursos)
    # classificados = get_classificados(1, 1999)
    # pprint(classificados)
    # maior_menor = get_maior_menor(
    #     [
    #         Classificado(
    #             classificacao="1", nota=Decimal("100"), id_fatec=1, id_curso=1999
    #         ),
    #         Classificado(
    #             classificacao="2", nota=Decimal("99"), id_fatec=1, id_curso=1999
    #         ),
    #         Classificado(
    #             classificacao="3", nota=Decimal("98"), id_fatec=1, id_curso=1999
    #         ),
    #     ]
    # )
    # pprint(maior_menor)
    # demandas = get_demandas_curso("Fatec Adamantina", "20222")
    # pprint(demandas)
