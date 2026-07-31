"""Casca de I/O: leitura das 3 fontes e serializacao da saida (DT-001/DT-006/DT-008).

Le os JSON com `parse_float=Decimal` para nunca passar valores nem taxas por
`float`. Serializa a saida com acentos preservados (`ensure_ascii=False`), ordem de
chaves fixa e todo valor monetario com exatamente 2 casas decimais. A saida nao tem
mais `em_viagem` e as categorias sao dinamicas (spec 1.4).
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import date
from decimal import ROUND_HALF_UP, Decimal

from src.modelo import (
    Cambio,
    Colaborador,
    Periodo,
    Politica,
    Resultado,
    ResultadoCategoria,
    motivo_texto,
)
from src.politica import CASAS_DECIMAIS, cambio_de_dict, politica_de_dict


class ErroEntrada(Exception):
    """Erro irrecuperavel de entrada (arquivo inexistente, JSON de topo invalido,
    campos de topo ausentes) — aborta a execucao com codigo 1 (DT-006, RN-018)."""


@dataclass
class Entrada:
    """Contexto de entrada ja validado no nivel de topo."""

    colaborador: Colaborador
    periodo: Periodo
    despesas_brutas: list


# --------------------------------------------------------------------------- #
# Leitura
# --------------------------------------------------------------------------- #
def _carrega_json(caminho, rotulo: str) -> object:
    """Abre e parseia um JSON com `parse_float=Decimal`; erros viram `ErroEntrada`."""
    try:
        with open(caminho, encoding="utf-8") as arquivo:
            return json.load(arquivo, parse_float=Decimal)
    except FileNotFoundError as erro:
        raise ErroEntrada(f"{rotulo} nao encontrado: {caminho}") from erro
    except json.JSONDecodeError as erro:
        raise ErroEntrada(f"{rotulo} com JSON invalido: {erro}") from erro
    except OSError as erro:
        raise ErroEntrada(f"nao foi possivel ler {rotulo} ({caminho}): {erro}") from erro


def ler_entrada(caminho) -> Entrada:
    """Le e valida a estrutura de topo do input. Levanta `ErroEntrada` em erro
    irrecuperavel. Registros de despesa individuais NAO sao validados aqui — isso
    e responsabilidade do nucleo (RN-013). Nao ha mais campo de topo `em_viagem`."""
    dados = _carrega_json(caminho, "arquivo de entrada")

    if not isinstance(dados, dict):
        raise ErroEntrada("JSON de topo deve ser um objeto")

    colaborador = _le_colaborador(dados)
    periodo = _le_periodo(dados)

    despesas = dados.get("despesas")
    if not isinstance(despesas, list):
        raise ErroEntrada("campo 'despesas' ausente ou nao e uma lista")

    return Entrada(colaborador, periodo, despesas)


def ler_politica(caminho) -> Politica:
    """RN-015 — le `politica-v4.json` e constroi a `Politica`. Aborta se ausente ou
    inparseavel."""
    dados = _carrega_json(caminho, "arquivo de politica")
    if not isinstance(dados, dict):
        raise ErroEntrada("politica: JSON de topo deve ser um objeto")
    try:
        return politica_de_dict(dados)
    except (KeyError, TypeError, ValueError, ArithmeticError) as erro:
        raise ErroEntrada(f"politica mal formada: {erro}") from erro


def ler_cambio(caminho) -> Cambio:
    """RN-018 — le `cambio.json` e constroi o `Cambio`. Aborta se ausente ou
    inparseavel (sem o arquivo a `moeda_base` seria desconhecida)."""
    dados = _carrega_json(caminho, "arquivo de cambio")
    if not isinstance(dados, dict):
        raise ErroEntrada("cambio: JSON de topo deve ser um objeto")
    try:
        return cambio_de_dict(dados)
    except (KeyError, TypeError, ValueError, ArithmeticError, AttributeError) as erro:
        raise ErroEntrada(f"cambio mal formado: {erro}") from erro


def _le_colaborador(dados: dict) -> Colaborador:
    bruto = dados.get("colaborador")
    if not isinstance(bruto, dict):
        raise ErroEntrada("campo 'colaborador' ausente ou invalido")
    for campo in ("id", "nome", "centro_custo"):
        if not isinstance(bruto.get(campo), str):
            raise ErroEntrada(f"campo obrigatorio ausente: colaborador.{campo}")
    return Colaborador(
        id=bruto["id"], nome=bruto["nome"], centro_custo=bruto["centro_custo"]
    )


def _le_periodo(dados: dict) -> Periodo:
    bruto = dados.get("periodo")
    if not isinstance(bruto, dict):
        raise ErroEntrada("campo 'periodo' ausente ou invalido")
    for campo in ("competencia", "inicio", "fim"):
        if not isinstance(bruto.get(campo), str):
            raise ErroEntrada(f"campo obrigatorio ausente: periodo.{campo}")
    try:
        inicio = date.fromisoformat(bruto["inicio"])
        fim = date.fromisoformat(bruto["fim"])
    except ValueError as erro:
        raise ErroEntrada(f"periodo com data invalida: {erro}") from erro
    return Periodo(competencia=bruto["competencia"], inicio=inicio, fim=fim)


# --------------------------------------------------------------------------- #
# Serializacao
# --------------------------------------------------------------------------- #
# Sentinela (Private Use Area U+E000) para injetar numeros monetarios com 2 casas
# no JSON sem que o `json` os trate como texto. Definida via chr() para nao conter
# caractere invisivel no codigo-fonte.
_SENTINELA = chr(0xE000)
_PADRAO_MOEDA = re.compile(rf'"{_SENTINELA}(-?\d+\.\d{{2}}){_SENTINELA}"')


def _quantiza(valor: Decimal) -> Decimal:
    return valor.quantize(CASAS_DECIMAIS, ROUND_HALF_UP)


def _moeda_default(objeto):
    if isinstance(objeto, Decimal):
        return f"{_SENTINELA}{objeto:.2f}{_SENTINELA}"
    raise TypeError(f"tipo nao serializavel: {type(objeto).__name__}")


def serializa(resultado: Resultado) -> str:
    """Devolve o JSON do `Resultado` como texto (2 casas, acentos, ordem fixa)."""
    texto = json.dumps(
        _para_dict(resultado),
        ensure_ascii=False,
        indent=2,
        default=_moeda_default,
    )
    return _PADRAO_MOEDA.sub(r"\1", texto)


def escrever_saida(resultado: Resultado, caminho) -> None:
    """Escreve o `Resultado` serializado em `caminho` (UTF-8, com newline final)."""
    with open(caminho, "w", encoding="utf-8") as arquivo:
        arquivo.write(serializa(resultado) + "\n")


def _para_dict(resultado: Resultado) -> dict:
    return {
        "colaborador": {
            "id": resultado.colaborador.id,
            "nome": resultado.colaborador.nome,
            "centro_custo": resultado.colaborador.centro_custo,
        },
        "competencia": resultado.competencia,
        "periodo": {
            "inicio": resultado.periodo.inicio.isoformat(),
            "fim": resultado.periodo.fim.isoformat(),
        },
        "categorias": {
            cat: _categoria_dict(rc) for cat, rc in resultado.categorias.items()
        },
        "reprovadas_sem_categoria": [
            {
                "id": rep.id,
                "categoria_informada": rep.categoria_informada,
                "motivo": motivo_texto(rep.motivo),
            }
            for rep in resultado.reprovadas_sem_categoria
        ],
        "total_reembolso_geral": _quantiza(resultado.total_reembolso_geral),
    }


def _categoria_dict(categoria: ResultadoCategoria) -> dict:
    return {
        "total_despesas": _quantiza(categoria.total_despesas),
        "total_aceito": _quantiza(categoria.total_aceito),
        "total_reembolso": _quantiza(categoria.total_reembolso),
        "reprovadas": [
            {"id": rep.id, "motivo": motivo_texto(rep.motivo)}
            for rep in categoria.reprovadas
        ],
    }
