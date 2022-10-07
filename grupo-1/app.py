from pprint import pprint

import requests
from bs4 import BeautifulSoup


class Test01:

    def get_fatecs(self):

        fatecs = []
        data = {

        }

        resp = requests.post(
            "https://www.vestibularfatec.com.br/classificacao/fatec.asp",
            data=data,
        )

        soup = BeautifulSoup(resp.content, 'html.parser')
        for option in soup.find_all('option')[1:]:
            fatecs.append((option['value'], option.text))

        pprint(fatecs)
        print(len(fatecs))
        return fatecs

    def get_cursos(self, fatec):
        cursos = []
        data = {
            'CodFatec': fatec
        }

        resp = requests.post(
            "https://www.vestibularfatec.com.br/classificacao/lista.asp",
            data=data,
        )

        #pprint(resp.content)

        soup = BeautifulSoup(resp.content, 'html.parser')
        for option in soup.find_all('option')[1:]:
            cursos.append((fatec, option['value'], option.text))

        pprint(cursos)
        print(len(cursos))
        return cursos

    def get_listas(self, fatec, curso):
        data = {
            'CodFatec': fatec,
            'CodEscolaCurso': curso,
        }

        resp = requests.post(
            "https://www.vestibularfatec.com.br/classificacao/lista.asp",
            data=data,
        )

        #pprint(resp.content)

    def get_classificados(self, fatec, curso, opcao):

        classificados = []

        data = {
            'CodFatec': fatec,
            'CodEscolaCurso': curso,
            'o': opcao
        }

        resp = requests.post(
            "https://www.vestibularfatec.com.br/classificacao/lista.asp",
            data=data,
        )

        #print(resp.content)

        soup = BeautifulSoup(resp.content, 'html.parser')
        for linha in soup.find_all('tr')[1:]:
            colunas = [x.text for x in linha.find_all('td')]
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

        #pprint(cursos)
        #print(len(cursos))

        print("Pegando lista de Classificação")

        for fatec_id, curso_id, curso_nome in cursos[:4]:  ###SLICE PARA TESTES
            print(f"Classificados da {fatec_id}, {curso_id}")
            classificados.append((fatec_id, curso_id, self.get_classificados(fatec_id, curso_id, 1)))

        for lista in classificados:
            print(f" # # # Curso: {lista[0:2]} - {lista[2]}")


T = Test01()

#fatecs = T.get_fatecs()#
#T.get_cursos(71)
#T.get_listas(71, 2437)
#T.get_classificados(71,2437, 1)

T.work()




