"""Fixtures compartilhadas dos testes (spec 1.4)."""

from pathlib import Path

import pytest

from src import io_json

_RAIZ = Path(__file__).resolve().parent.parent
_INFO = _RAIZ / "src" / "informacoes_externas"


@pytest.fixture(scope="session")
def caminho_exemplo() -> Path:
    """Caminho do input `exemplos/despesas-exemplo.json` (CC-ENG-PLATAFORMA)."""
    return _RAIZ / "exemplos" / "despesas-exemplo.json"


@pytest.fixture(scope="session")
def caminho_envelope() -> Path:
    """Caminho do input `exemplos/despesas-envelope.json` (CC-COMERCIAL, moedas)."""
    return _RAIZ / "exemplos" / "despesas-envelope.json"


@pytest.fixture(scope="session")
def caminho_politica() -> Path:
    return _INFO / "politica-v4.json"


@pytest.fixture(scope="session")
def caminho_cambio() -> Path:
    return _INFO / "cambio.json"


@pytest.fixture(scope="session")
def politica_v4(caminho_politica):
    """`Politica` construida a partir do arquivo empacotado."""
    return io_json.ler_politica(caminho_politica)


@pytest.fixture(scope="session")
def cambio_real(caminho_cambio):
    """`Cambio` construido a partir do arquivo empacotado."""
    return io_json.ler_cambio(caminho_cambio)
