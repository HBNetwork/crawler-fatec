from requests_futures.sessions import FuturesSession
from bs4 import BeautifulSoup
from datetime import datetime

now = datetime.now


def extrai_nome_fatec(nome_com_cidade):
    return "-".join(nome_com_cidade.split("-")[1:]).strip()


def get_ano_semestre():
    date_now = now()
    semestre = 1 if date_now.month <= 6 else 2
    ano = date_now.year
    return f"{ano}-{semestre}"


def prepara_demanda_classificacao(content):
    # TODO SEPARAR
    # TODO Utilizar CSS Selector
    lista_fatecs = []
    soup = BeautifulSoup(content, "html.parser")
    ano_semestre = get_ano_semestre()

    for option in soup.find_all("option")[1:]:
        id_fatec = option["value"]
        nome_fatec = extrai_nome_fatec(option.text)

        lista_fatecs.append(
            {
                "url": "https://www.vestibularfatec.com.br/classificacao/lista.asp",
                "data": {"CodFatec": id_fatec},
                "hook": response_hook_cursos,
            }
        )
        lista_fatecs.append(
            {
                "url": "https://www.vestibularfatec.com.br/demanda/demanda.asp",
                "data": {"FATEC": nome_fatec, "ano-sem": ano_semestre},
                "hook": response_hook_demandas,
            }
        )

    print(len(lista_fatecs))
    return lista_fatecs

def prepara_curso(content, id_fatec):
    # TODO SEPARAR
    # TODO Utilizar CSS Selector
    classificados = []

    data = {"CodFatec": id_fatec}

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
                    {
                        'url': 'https://www.vestibularfatec.com.br/classificacao/lista.asp',
                        'data': {"CodFatec": id_fatec, "CodEscolaCurso": id_curso, "o": 1}

                    }
                    # Classificado(int(colunas[0].text), nota, id_fatec, id_curso)
                )

    return classificados

def response_hook_fatec(resp, *args, **kwargs):
    print("FATEC ", resp.status_code, resp.url)
    lista_fatecs = prepara_demanda_classificacao(resp.content)
    response_for_urls(lista_fatecs[:1])


def response_hook_cursos(resp, *args, **kwargs):

    id_fatec = resp.request.body.split('=')[1]
    print("CURSOS ", resp.status_code, resp.url)
    list_cursos = prepara_classificacao(resp.content, id_fatec)



def response_hook_demandas(resp, *args, **kwargs):
    print("DEMANDAS ", resp.status_code, resp.url)
    # response_for_urls(demandas)


def response_for_urls(urls):
    """Asynchronously get response for many urls."""
    # TODO Da para usar a sessão ou context name para tratar errors HTTP?
    with FuturesSession() as session:
        futures = [
            session.post(
                url["url"],
                data=url.get("data"),
                hooks={"response": url.get("hook")},
            )
            for url in urls
        ]

    return (f.result() for f in futures)


def main_fatec():
    pass
    # call fatec.asp unidades-cursos

    # call lista.asp demanda.asp


if __name__ == "__main__":
    urls = [
        {
            "url": "https://www.vestibularfatec.com.br/classificacao/fatec.asp",
            "hook": response_hook_fatec,
        },
        {
            "url": "https://www.vestibularfatec.com.br/unidades-cursos/",
            "hook": response_hook_cursos,
        },
    ]

    print(list(response_for_urls(urls)))
