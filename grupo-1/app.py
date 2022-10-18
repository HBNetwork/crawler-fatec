from collections import namedtuple
from datetime import datetime
from decimal import Decimal
from itertools import chain
from pdb import set_trace
from pprint import pprint
from multiprocessing import Pool
import time
from tkinter.ttk import Separator
import requests
from bs4 import BeautifulSoup
import csv

# só assim eu consegui mockar o now para testar a função get_ano_semestre
now = datetime.now


Fatec = namedtuple("Fatec", ["id", "nome"])
MaiorMenorNota = namedtuple("MaiorMenorNota", ["maior", "menor"])
Classificado = namedtuple(
    "Classificado", ["classificacao", "nota", "id_fatec", "id_curso"]
)
Curso = namedtuple(
    "Curso",
    [
        "id",
        "id_interno",
        "id_fatec",
        "nome",
        "ano_sem",
        "periodo",
        "qtde_vagas",
        "qtde_inscrito",
        "demanda",
        "maior_nota",
        "menor_nota",
        "nome_fatec",
    ],
)

def write_table(resultado):
    with open('resultado.csv', 'w', newline='') as f:
        field_names = [
        "cod_curso",
        "nome_curso",
        "cod_instituicao",
        "nome_instituicao"
        "ano",
        "semestre",
        "periodo",
        "qtde_vagas",
        "qtde_inscrito",
        "demanda",
        "nota_corte",
        "nota_maxima",
        ]

        writer = csv.writer(f, delimiter=';')
        writer.writerow(field_names)
        writer.writerows(resultado)

def make_table():

    fatecs = get_fatecs()
    ano, semestre = get_ano_semestre()
    ano_sem = f"{ano}{semestre}"
    id_cursos = get_id_cursos()
    with Pool(20) as pool:
        inicio = time.time()
        cursos = pool.starmap(get_cursos, [(fatec.id, fatec.nome, ano_sem) for fatec in fatecs])
        cursos = join_id_cursos(id_cursos, chain(*cursos))
        resultado = get_resultados(cursos)
        print(f'DURAÇÃO -> {time.time() - inicio} seg')
    write_table(resultado)
    return resultado

def get_resultados(cursos):
    resultado = []
    ano = cursos[0].ano_sem[:-1]
    semestre = cursos[0].ano_sem[-1:]
    for curso in cursos:
        resultado.append((
            curso.id,
            curso.nome,
            curso.id_fatec,
            curso.nome_fatec,
            ano,
            semestre,
            curso.periodo,
            curso.qtde_vagas,
            curso.qtde_inscrito,
            curso.demanda,
            curso.menor_nota,
            curso.maior_nota
        ))
    return resultado

def join_id_cursos(id_cursos, cursos):
    cursos_id_correto = []
    for curso in cursos:
        cursos_id_correto.append(
            Curso(
                id_cursos[curso.nome],
                curso.id_interno,
                curso.id_fatec,
                curso.nome,
                curso.ano_sem,
                curso.periodo,
                curso.qtde_vagas,
                curso.qtde_inscrito,
                curso.demanda,
                curso.maior_nota,
                curso.menor_nota,
                curso.nome_fatec
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
    return nome.strip(), periodo.strip()


def extrai_nome_fatec(nome_com_cidade):
    return "-".join(nome_com_cidade.split("-")[1:]).strip()


def get_fatecs():
    fatecs = []
    resp = requests.get("https://www.vestibularfatec.com.br/classificacao/fatec.asp")

    soup = BeautifulSoup(resp.content, "html.parser")
    for option in soup.find_all("option")[1:]:
        fatecs.append(Fatec(int(option["value"]), extrai_nome_fatec(option.text)))

    return fatecs


def get_cursos(id_fatec, nome_fatec, ano_sem):
    cursos = []
    data = {"CodFatec": id_fatec}
    resp = requests.post(
        "https://www.vestibularfatec.com.br/classificacao/lista.asp", data=data
    )
    demandas_lista = get_demandas_curso(nome_fatec, ano_sem)
    soup = BeautifulSoup(resp.content, "html.parser")
    cursos_soup = soup.find_all("option")
    if cursos_soup:

        for option in cursos_soup[1:]:
            id_curso = int(option["value"])
            nome, periodo = extrai_nome_periodo(option.text)
            classificacao = get_classificados(id_fatec, id_curso)
            nota = get_maior_menor(classificacao)
            demandas = demandas_lista.get((nome, periodo))
            #TODO: Adicionar notificação caso não exista demanda
            vagas = 0
            inscritos = 0 
            demanda = 0
            if demandas:
                vagas = demandas['vagas']
                inscritos = demandas['inscritos']
                demanda = demandas['demanda']

            cursos.append(
                Curso(
                    None,
                    id_curso,
                    id_fatec,
                    nome,
                    ano_sem,
                    periodo,
                    vagas,
                    inscritos,
                    demanda,
                    nota.maior,
                    nota.menor,
                    nome_fatec,
                )
            )

    return cursos


def get_classificados(id_fatec, id_curso, opcao=1):

    classificados = []

    data = {"CodFatec": id_fatec, "CodEscolaCurso": id_curso, "o": opcao}

    resp = requests.post(
        "https://www.vestibularfatec.com.br/classificacao/lista.asp", data=data
    )

    soup = BeautifulSoup(resp.content, "html.parser")
    classificados_soup = soup.find_all("tr")
    if classificados_soup:
        for linha in classificados_soup[1:]:
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
    maior_nota = 0
    menor_nota = 0
    if classificados:
        maior_nota = classificados[0].nota
        menor_nota = classificados[-1].nota

    return MaiorMenorNota(maior_nota, menor_nota)


def get_demandas_curso(nome_fatec, id_semestre):
    demandas = {}
    data = {
        "FATEC": nome_fatec,
        "ano-sem": id_semestre,
    }
    resp = requests.post(
        "https://www.vestibularfatec.com.br/demanda/demanda.asp", data=data
    )

    soup = BeautifulSoup(resp.content, "html.parser")
    cursos = soup.find_all("tr")
    if cursos:
        for linha in cursos[1:]:
            colunas = linha.find_all("td")
            demanda = Decimal(colunas[4].text.replace(",", "."))
            nome_curso = colunas[0].text
            periodo = colunas[1].text
            inscritos = int(colunas[2].text)
            vagas = int(colunas[3].text)
            demandas[(nome_curso.strip(), periodo.strip())] = {
                "inscritos": inscritos,
                "vagas": vagas,
                "demanda": demanda,
            }
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

    cursos = make_table()
    pprint('cursos quantidade -> ', len(cursos))
