"""Testes da CLI `calcular` (T-042/T-049), spec 1.4."""

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
    assert dados["total_reembolso_geral"] == 351.43


def test_cli_sem_em_viagem(caminho_exemplo, tmp_path):
    # Nao ha mais flag --em-viagem; a saida nao tem o campo em_viagem.
    saida = tmp_path / "resultado.json"
    codigo = cli.main(["--input", str(caminho_exemplo), "--output", str(saida)])
    assert codigo == 0
    dados = json.loads(saida.read_text(encoding="utf-8"))
    assert "em_viagem" not in dados


def test_cli_em_viagem_flag_rejeitada(caminho_exemplo, tmp_path):
    saida = tmp_path / "resultado.json"
    with pytest.raises(SystemExit) as exc:
        cli.main(["--input", str(caminho_exemplo), "--output", str(saida), "--em-viagem"])
    assert exc.value.code == 2  # argparse: argumento desconhecido


def test_cli_defaults_empacotados(caminho_envelope, tmp_path):
    # Sem --politica/--cambio usa os arquivos empacotados em src/informacoes_externas.
    saida = tmp_path / "resultado.json"
    codigo = cli.main(["--input", str(caminho_envelope), "--output", str(saida)])
    assert codigo == 0
    dados = json.loads(saida.read_text(encoding="utf-8"))
    assert dados["total_reembolso_geral"] == 1228.72


def test_cli_cambio_ausente_exit1(caminho_exemplo, tmp_path, capsys):
    saida = tmp_path / "resultado.json"
    codigo = cli.main(
        [
            "--input", str(caminho_exemplo),
            "--output", str(saida),
            "--cambio", str(tmp_path / "nao-existe.json"),
        ]
    )
    assert codigo == 1
    assert not saida.exists()
    assert capsys.readouterr().err


def test_cli_politica_ausente_exit1(caminho_exemplo, tmp_path):
    saida = tmp_path / "resultado.json"
    codigo = cli.main(
        [
            "--input", str(caminho_exemplo),
            "--output", str(saida),
            "--politica", str(tmp_path / "nao-existe.json"),
        ]
    )
    assert codigo == 1
    assert not saida.exists()


def test_cli_exit_code_input_inexistente(tmp_path, capsys):
    saida = tmp_path / "resultado.json"
    codigo = cli.main(["--input", str(tmp_path / "nao-existe.json"), "--output", str(saida)])
    assert codigo == 1
    assert not saida.exists()
    assert capsys.readouterr().err


def test_cli_falta_argumento_exit_2(caminho_exemplo):
    with pytest.raises(SystemExit) as exc:
        cli.main(["--input", str(caminho_exemplo)])  # falta --output
    assert exc.value.code == 2


def test_python_m_src(caminho_exemplo, tmp_path):
    saida = tmp_path / "resultado.json"
    proc = subprocess.run(
        [sys.executable, "-m", "src", "--input", str(caminho_exemplo), "--output", str(saida)],
        cwd=_RAIZ,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr
    dados = json.loads(saida.read_text(encoding="utf-8"))
    assert dados["total_reembolso_geral"] == 351.43
