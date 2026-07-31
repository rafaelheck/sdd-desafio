"""Interface de linha de comando `calcular` (DT-003).

Liga leitura -> pipeline -> escrita. Exit codes: 0 sucesso, 1 erro irrecuperavel
de entrada, 2 erro de uso (padrao do argparse). Ver `contracts/cli-contract.md`.
"""

from __future__ import annotations

import argparse
import sys

from src import calculo, io_json


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="calcular",
        description="Motor de calculo de reembolso de despesas corporativas.",
    )
    parser.add_argument("--input", required=True, help="arquivo JSON de entrada")
    parser.add_argument("--output", required=True, help="arquivo JSON de saida")
    parser.add_argument(
        "--em-viagem",
        action="store_true",
        dest="em_viagem",
        help="aplica limites ampliados em 50%% a todas as despesas do input (RN-009)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Ponto de entrada. Retorna o codigo de saida."""
    args = _parser().parse_args(argv)  # argparse sai com codigo 2 em erro de uso.

    try:
        entrada = io_json.ler_entrada(args.input)
    except io_json.ErroEntrada as erro:
        print(f"erro: {erro}", file=sys.stderr)
        return 1

    # A flag da CLI e a fonte de verdade de `em_viagem` (AMB-008).
    resultado = calculo.calcula(
        entrada.despesas_brutas,
        entrada.colaborador,
        entrada.periodo,
        args.em_viagem,
    )
    io_json.escrever_saida(resultado, args.output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
