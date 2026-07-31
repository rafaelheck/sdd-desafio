"""Auditoria de rastreabilidade: toda RN-001..RN-020 tem teste (T-047).

Falha se alguma regra da spec 1.4 nao possuir ao menos um teste nomeado pela
convencao `test_rn_0NN_*` (CLAUDE.md: nenhuma regra sem teste). Um teste nomeado por
outra RN NAO conta pela regra que cobre — a convencao e o numero literal no nome.
"""

import re
from pathlib import Path

_DIR = Path(__file__).resolve().parent
_PADRAO = re.compile(r"def test_rn_(\d{3})")


def _rns_com_teste() -> set[int]:
    cobertas: set[int] = set()
    for arquivo in _DIR.glob("test_*.py"):
        for match in _PADRAO.finditer(arquivo.read_text(encoding="utf-8")):
            cobertas.add(int(match.group(1)))
    return cobertas


def test_todas_rns_tem_teste():
    esperadas = set(range(1, 21))  # RN-001..RN-020
    faltando = sorted(esperadas - _rns_com_teste())
    assert not faltando, f"RNs sem teste correspondente: {faltando}"
