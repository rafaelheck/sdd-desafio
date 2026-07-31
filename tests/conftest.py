"""Fixtures compartilhadas dos testes."""

from pathlib import Path

import pytest

_RAIZ = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="session")
def caminho_exemplo() -> Path:
    """Caminho do input oficial `exemplos/despesas-exemplo.json`."""
    return _RAIZ / "exemplos" / "despesas-exemplo.json"
