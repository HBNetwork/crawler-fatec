from datetime import datetime
from decimal import Decimal
from unittest import mock

import pytest

from app import (
    Classificado,
    MaiorMenorNota,
    extrai_nome_fatec,
    extrai_nome_periodo,
    get_ano_semestre,
    get_maior_menor,
)


@pytest.mark.parametrize(
    "input, curso, periodo",
    [
        ("Ciência de Dados  (Noite)", "Ciência de Dados", "Noite"),
        (
            "Análise e Desenvolvimento de Sistemas  (Tarde)",
            "Análise e Desenvolvimento de Sistemas",
            "Tarde",
        ),
        ("Gestão Empresarial  (Manhã)", "Gestão Empresarial  (Manhã)", "Manhã"),
    ],
)
def test_extrai_nome_periodo(input, curso, periodo):

    assert curso, periodo == extrai_nome_periodo(input)


def test_maior_menor_lista_ordenda():

    classificados = [
        Classificado(
            classificacao=1, nota=Decimal("92.400"), id_fatec=3, id_curso=2319
        ),
        Classificado(
            classificacao=2, nota=Decimal("84.000"), id_fatec=3, id_curso=2319
        ),
        Classificado(
            classificacao=3, nota=Decimal("74.800"), id_fatec=3, id_curso=2319
        ),
    ]

    expected = MaiorMenorNota(maior=Decimal("92.400"), menor=Decimal("74.800"))

    assert expected == get_maior_menor(classificados)


@pytest.mark.parametrize(
    "input, nome_fatec",
    [
        ("Adamantina - Fatec Adamantina", "Fatec Adamantina"),
        (
            "Americana - Fatec Americana - Ministro Ralph Biasi",
            "Fatec Americana - Ministro Ralph Biasi",
        ),
        (
            "Araçatuba - Fatec Araçatuba - Prof. Fernando Amaral de Almeida Prado",
            "Fatec Araçatuba - Prof. Fernando Amaral de Almeida Prado",
        ),
    ],
)
def test_extrai_nome_fatec(input, nome_fatec):

    assert nome_fatec == extrai_nome_fatec(input)


def test_ano_semestre():

    with mock.patch("app.now", return_value=datetime(2021, 8, 1)):
        assert (2021, 2) == get_ano_semestre()

    with mock.patch("app.now", return_value=datetime(2022, 4, 1)):
        assert (2022, 1) == get_ano_semestre()
