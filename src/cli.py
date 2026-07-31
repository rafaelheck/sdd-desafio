"""Interface de linha de comando `calcular` (DT-003, DT-003b).

`calcular` e um subcomando do argparse. Formas equivalentes (todas chamam `main`):
  - `python -m src.cli calcular --input ... --output ...`  (sem instalar; forma primaria)
  - `python -m src calcular --input ... --output ...`       (via pacote; `__main__` delega)
  - `calcular --input ... --output ...`                     (console script; wrapper `main_console`)

Liga leitura das 3 fontes (input, politica, cambio) -> pipeline -> escrita. Sem
regra de negocio na CLI. Exit codes: 0 sucesso, 1 erro irrecuperavel de entrada
(input/politica/cambio ausente ou inparseavel; topo invalido), 2 erro de uso
(subcomando `calcular` ausente ou argumento obrigatorio ausente; padrao do argparse).
Ver `contracts/cli-contract.md`.
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
        description="Motor de calculo de reembolso de despesas corporativas.",
    )
    sub = parser.add_subparsers(dest="comando", required=True)
    calcular = sub.add_parser(
        "calcular",
        help="calcula o reembolso de um arquivo de despesas",
        description="Calcula o reembolso de um arquivo de despesas.",
    )
    calcular.add_argument("--input", required=True, help="arquivo JSON de entrada")
    calcular.add_argument("--output", required=True, help="arquivo JSON de saida")
    calcular.add_argument(
        "--politica",
        default=str(_POLITICA_PADRAO),
        help="politica externa de categorias/limites por centro de custo (RN-015)",
    )
    calcular.add_argument(
        "--cambio",
        default=str(_CAMBIO_PADRAO),
        help="tabela de cambio: moeda_base + taxas por data (RN-018)",
    )
    return parser


def _executa_calcular(args: argparse.Namespace) -> int:
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


def main(argv: list[str] | None = None) -> int:
    """Ponto de entrada. Retorna o codigo de saida.

    `argv` deve comecar pelo subcomando (`["calcular", "--input", ...]`); a ausencia
    do subcomando e erro de uso do argparse (SystemExit codigo 2).
    """
    args = _parser().parse_args(argv)  # argparse sai com codigo 2 em erro de uso.
    # Ha um unico subcomando (`calcular`); `required=True` garante que args.comando existe.
    return _executa_calcular(args)


def main_console(argv: list[str] | None = None) -> int:
    """Wrapper do console script: injeta o subcomando `calcular`.

    Permite que a linha instalada siga com uma so palavra
    (`calcular --input ... --output ...`) enquanto `main` exige o subcomando.
    """
    if argv is None:
        argv = sys.argv[1:]
    return main(["calcular", *argv])


if __name__ == "__main__":
    sys.exit(main())
