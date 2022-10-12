from decimal import Decimal
from pprint import pprint

import requests
from bs4 import BeautifulSoup
from collections import namedtuple


Fatec = namedtuple("Fatec", ["id", "nome"])
MaiorMenorNota = namedtuple("MaiorMenorNota", ["maior", "menor"])
Classificado = namedtuple(
    "Classificado", ["classificacao", "nota", "id_fatec", "id_curso"]
)


def get_fatecs():
    fatecs = []
    resp = requests.get("https://www.vestibularfatec.com.br/classificacao/fatec.asp")

    soup = BeautifulSoup(resp.content, "html.parser")
    for option in soup.find_all("option")[1:]:
        fatecs.append(Fatec(int(option["value"]), option.text))

    return fatecs


Curso = namedtuple("Curso", ["id", "nome", "id_fatec"])


def get_cursos(id_fatec):
    cursos = []
    data = {"CodFatec": id_fatec}

    resp = requests.post(
        "https://www.vestibularfatec.com.br/classificacao/lista.asp", data=data
    )

    soup = BeautifulSoup(resp.content, "html.parser")

    for option in soup.find_all("option")[1:]:
        cursos.append(Curso(int(option["value"]), option.text, id_fatec))

    return cursos


def get_classificados(id_fatec, id_curso, opcao=1):

    classificados = []

    data = {"CodFatec": id_fatec, "CodEscolaCurso": id_curso, "o": opcao}

    resp = requests.post(
        "https://www.vestibularfatec.com.br/classificacao/lista.asp", data=data
    )

    soup = BeautifulSoup(resp.content, "html.parser")
    for linha in soup.find_all("tr")[1:]:
        # colunas = [x.text for x in linha.find_all('td')]
        colunas = linha.find_all("td")
        if colunas[-1].text == "CLASSIFICADO":
            nota = Decimal(colunas[3].text.replace(",", "."))
            classificados.append(
                Classificado(int(colunas[0].text), nota, id_fatec, id_curso)
            )

    return classificados


def get_maior_menor(classificados):
    return MaiorMenorNota(classificados[0].nota, classificados[-1].nota)


class Test01:
    def get_fatecs(self):
        fatecs = []
        resp = requests.get(
            "https://www.vestibularfatec.com.br/classificacao/fatec.asp"
        )

        soup = BeautifulSoup(resp.content, "html.parser")
        for option in soup.find_all("option")[1:]:
            fatecs.append((option["value"], option.text))

        pprint(fatecs)
        print(len(fatecs))
        return fatecs

    def get_cursos(self, fatec):
        cursos = []
        data = {"CodFatec": fatec}

        resp = requests.post(
            "https://www.vestibularfatec.com.br/classificacao/lista.asp", data=data
        )

        # pprint(resp.content)

        soup = BeautifulSoup(resp.content, "html.parser")
        for option in soup.find_all("option")[1:]:
            cursos.append((fatec, option["value"], option.text))

        pprint(cursos)
        print(len(cursos))
        return cursos

    def get_listas(self, fatec, curso):
        data = {"CodFatec": fatec, "CodEscolaCurso": curso}

        resp = requests.post(
            "https://www.vestibularfatec.com.br/classificacao/lista.asp", data=data
        )

        # pprint(resp.content)

    def get_classificados(self, fatec, curso, opcao):

        classificados = []

        data = {"CodFatec": fatec, "CodEscolaCurso": curso, "o": opcao}

        resp = requests.post(
            "https://www.vestibularfatec.com.br/classificacao/lista.asp", data=data
        )

        # print(resp.content)

        soup = BeautifulSoup(resp.content, "html.parser")
        for linha in soup.find_all("tr")[1:]:
            colunas = [x.text for x in linha.find_all("td")]
            classificados.append(colunas)

        pprint(classificados)
        print(len(classificados))
        return classificados

    def work(self):

        cursos = []

        classificados = []

        pprint("Pegando lista de Fatecs")
        fatecs = T.get_fatecs()

        print("Pegando lista de Cursos das Fatecs")
        for fatec_id, fatec_nome in fatecs[:4]:  ###SLICE PARA TESTES
            pprint(f"Cursos da {fatec_id}")
            cursos.extend(self.get_cursos(fatec_id))

        # pprint(cursos)
        # print(len(cursos))

        print("Pegando lista de Classificação")

        for fatec_id, curso_id, curso_nome in cursos[:4]:  ###SLICE PARA TESTES
            print(f"Classificados da {fatec_id}, {curso_id}")
            classificados.append(
                (fatec_id, curso_id, self.get_classificados(fatec_id, curso_id, 1))
            )

        for lista in classificados:
            print(f" # # # Curso: {lista[0:2]} - {lista[2]}")


if "__main__" == __name__:
    fatecs = get_fatecs()
    print(fatecs[0].nome)
    cursos = get_cursos(71)
    print(cursos)
    classificados = get_classificados(1, 1999)
    pprint(classificados)
    maior_menor = get_maior_menor(
        [
            Classificado(
                classificacao="1", nota=Decimal("100"), id_fatec=1, id_curso=1999
            ),
            Classificado(
                classificacao="2", nota=Decimal("99"), id_fatec=1, id_curso=1999
            ),
            Classificado(
                classificacao="3", nota=Decimal("98"), id_fatec=1, id_curso=1999
            ),
        ]
    )
    pprint(maior_menor)

# T = Test01()

# fatecs = T.get_fatecs()
# T.get_cursos(71)
# T.get_listas(71, 2437)
# T.get_classificados(71,2437, 1)

# T.work()
