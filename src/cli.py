"""Interface de linha de comando `calcular` (DT-003, DT-003b).

Liga leitura das 3 fontes (input, politica, cambio) -> pipeline -> escrita. Sem
regra de negocio na CLI. Exit codes: 0 sucesso, 1 erro irrecuperavel de entrada
(input/politica/cambio ausente ou inparseavel; topo invalido), 2 erro de uso
(padrao do argparse). Ver `contracts/cli-contract.md`.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from src import calculo, io_json

# Arquivos empacotados, resolvidos relativos ao pacote `src` (DT-003b).
_INFO = Path(__file__).resolve().parent / "informacoes_externas"
_POLITICA_PADRAO = _INFO / "politica-v4.json"
_CAMBIO_PADRAO = _INFO / "cambio.json"


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="calcular",
        description="Motor de calculo de reembolso de despesas corporativas.",
    )
    parser.add_argument("--input", required=True, help="arquivo JSON de entrada")
    parser.add_argument("--output", required=True, help="arquivo JSON de saida")
    parser.add_argument(
        "--politica",
        default=str(_POLITICA_PADRAO),
        help="politica externa de categorias/limites por centro de custo (RN-015)",
    )
    parser.add_argument(
        "--cambio",
        default=str(_CAMBIO_PADRAO),
        help="tabela de cambio: moeda_base + taxas por data (RN-018)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Ponto de entrada. Retorna o codigo de saida."""
    args = _parser().parse_args(argv)  # argparse sai com codigo 2 em erro de uso.

    try:
        entrada = io_json.ler_entrada(args.input)
        politica = io_json.ler_politica(args.politica)
        cambio = io_json.ler_cambio(args.cambio)
    except io_json.ErroEntrada as erro:
        print(f"erro: {erro}", file=sys.stderr)
        return 1

    resultado = calculo.calcula(
        entrada.despesas_brutas,
        entrada.colaborador,
        entrada.periodo,
        politica,
        cambio,
    )
    io_json.escrever_saida(resultado, args.output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
