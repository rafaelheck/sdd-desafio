"""Testes da CLI `calcular` (T-020, T-021)."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

from src import cli

_RAIZ = Path(__file__).resolve().parent.parent


def test_cli_gera_saida(caminho_exemplo, tmp_path):
    saida = tmp_path / "resultado.json"
    codigo = cli.main(["--input", str(caminho_exemplo), "--output", str(saida)])
    assert codigo == 0
    dados = json.loads(saida.read_text(encoding="utf-8"))
    assert dados["em_viagem"] is False
    assert dados["total_reembolso_geral"] == 585.43


def test_cli_em_viagem(caminho_exemplo, tmp_path):
    saida = tmp_path / "resultado.json"
    codigo = cli.main(
        ["--input", str(caminho_exemplo), "--output", str(saida), "--em-viagem"]
    )
    assert codigo == 0
    dados = json.loads(saida.read_text(encoding="utf-8"))
    assert dados["em_viagem"] is True


def test_cli_exit_code_input_inexistente(tmp_path, capsys):
    saida = tmp_path / "resultado.json"
    codigo = cli.main(
        ["--input", str(tmp_path / "nao-existe.json"), "--output", str(saida)]
    )
    assert codigo == 1
    assert not saida.exists()
    assert capsys.readouterr().err  # mensagem em stderr


def test_cli_falta_argumento_exit_2(caminho_exemplo):
    with pytest.raises(SystemExit) as exc:
        cli.main(["--input", str(caminho_exemplo)])  # falta --output
    assert exc.value.code == 2


def test_python_m_src(caminho_exemplo, tmp_path):
    saida = tmp_path / "resultado.json"
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "src",
            "--input",
            str(caminho_exemplo),
            "--output",
            str(saida),
        ],
        cwd=_RAIZ,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr
    dados = json.loads(saida.read_text(encoding="utf-8"))
    assert dados["total_reembolso_geral"] == 585.43
