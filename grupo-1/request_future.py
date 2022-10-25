from pprint import pprint
from requests_futures.sessions import FuturesSession
from bs4 import BeautifulSoup
from datetime import datetime
import time

now = datetime.now
all_resps = []
# UTILS
def extrai_nome_fatec(nome_com_cidade):
    return "-".join(nome_com_cidade.split("-")[1:]).strip()


def get_ano_semestre():
    date_now = now()
    semestre = 1 if date_now.month <= 6 else 2
    ano = date_now.year
    return f"{ano}-{semestre}"


# PREPARAÇÕES
def create_urls_curso(fatecs):
    urls = []
    for fatec in fatecs:
        urls.append({
            "url": "https://www.vestibularfatec.com.br/classificacao/lista.asp",
            "data": {"CodFatec": fatec['id_fatec']},
            "hook": response_hook_cursos,
            "context": {"nome_fatec": fatec['nome_fatec']}
        })
    return urls


def parse_fatecs(content):
    # TODO SEPARAR
    # TODO Utilizar CSS Selector
    lista_fatecs = []
    soup = BeautifulSoup(content, "html.parser")
    # ano_semestre = get_ano_semestre()

    for option in soup.find_all("option")[1:5]:
        id_fatec = option["value"]
        nome_fatec = extrai_nome_fatec(option.text)
        lista_fatecs.append({"id_fatec": id_fatec, "nome_fatec": nome_fatec})
        # lista_fatecs.append(
        #     {
        #         "url": "https://www.vestibularfatec.com.br/classificacao/lista.asp",
        #         "data": {"CodFatec": id_fatec},
        #         "hook": response_hook_cursos,
        #         "context": {"nome_fatec": nome_fatec}
        #     }
        # )
        # lista_fatecs.append(
        #     {
        #         "url": "https://www.vestibularfatec.com.br/demanda/demanda.asp",
        #         "data": {"FATEC": nome_fatec, "ano-sem": ano_semestre},
        #         "hook": response_hook_demandas,
        #         "context": {"id_fatec": id_fatec}
        #     }
        # )
    return lista_fatecs


def prepara_curso(content, id_fatec):
    # TODO SEPARAR
    # TODO Utilizar CSS Selector
    cursos = []
    soup = BeautifulSoup(content, "html.parser")
    cursos_soup = soup.find_all("option")
    if cursos_soup:
        for option in cursos_soup[1:]:
            id_curso = int(option["value"])
            cursos.append(
                {
                    "url": "https://www.vestibularfatec.com.br/classificacao/lista.asp",
                    "data": {"CodFatec": id_fatec, "CodEscolaCurso": id_curso, "o": 1},
                    "hook": response_hook_classificacao,
                }
            )

    return cursos


# HOOKS
def response_hook_fatec(resp, *args, **kwargs):
    lista_fatecs = parse_fatecs(resp.content)
    # response_for_urls(lista_fatecs)
    resp.data = lista_fatecs
    return resp


# Fora do ar, em atualização.
# def response_hook_id_cursos(resp, *args, **kwargs):
#     all_resps.append(resp)
#     #TODO add parser

def response_hook_cursos(resp, *args, **kwargs):
    id_fatec = resp.request.body.split("=")[1]
    list_cursos = prepara_curso(resp.content, id_fatec)
    response_for_urls(list_cursos)


def response_hook_classificacao(resp, *args, **kwargs):
    #TODO add parser
    # parser_classificacao(resp.content)
    all_resps.append(resp)


def response_hook_demandas(resp, *args, **kwargs):
    #TODO add parser
    all_resps.append(resp)


# Parsers
# def parser_classificacao(content):
#     classificados = []
#     classificados_soup = content.find_all('tr')
#     if classificados_soup:
#         for linha in classificados_soup[1:]:
#             classificados.append(linha.find_all("td"))


#    return classificados
# REQUESTS
def response_for_urls(urls):
    """Asynchronously get response for many urls."""
    # TODO Da para usar a sessão ou context name para tratar errors HTTP?
    resps = None
    with FuturesSession(max_workers=75) as session:
        # futures = [
        #     session.post(
        #         url["url"], data=url.get("data"), hooks={"response": url.get("hook")}
        #     )
        #     for url in urls
        # ]
        futures = []
        for url in urls:
            future = session.post(
                url["url"], data=url.get("data"), hooks={"response": url.get("hook")}
            )
            futures.append(future)

        resps = [f.result().data for f in futures] 
        print('RESP')
        for resp in resps:
            pprint(resp)
            break
    return resps


def main_fatec():
    pass
    # call fatec.asp unidades-cursos

    # call lista.asp demanda.asp


if __name__ == "__main__":
    start = time.time()
    urls = [
        {
            "url": "https://www.vestibularfatec.com.br/classificacao/fatec.asp",
            "hook": response_hook_fatec,
        },
        # Fora do ar, em atualização.
        # {
        #     "url": "https://www.vestibularfatec.com.br/unidades-cursos/",
        #     "hook": response_hook_id_cursos,
        # },
    ]

    lista_fatec = response_for_urls(urls)
    urls_cursos = create_urls_curso(lista_fatec)
    cursos = response_for_urls(urls_cursos)
    
    print(f'DURAÇÃO: {time.time() - start} segundos')
    print(len(all_resps))
