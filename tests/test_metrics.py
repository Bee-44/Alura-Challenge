"""Pruebas de src/metrics.py sobre DataFrames sintéticos."""

import pandas as pd
import pytest

from src.metrics import (
    desempeno_por_mindset,
    detectar_patrones,
    filtrar_periodo,
    pnl_total,
    profit_factor,
    resumen,
    total_operaciones,
    win_rate,
)


@pytest.fixture
def df_mixto() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "fecha": pd.to_datetime(
                ["2025-09-01", "2025-09-15", "2025-10-01", "2025-10-15"]
            ),
            "activo": ["AAPL", "TSLA", "NVDA", "MSFT"],
            "direccion": ["long", "short", "long", "long"],
            "precio_entrada": [100.0, 200.0, 50.0, 300.0],
            "precio_salida": [110.0, 190.0, 45.0, 290.0],
            "cantidad": [10, 5, 10, 2],
            "pnl": [100.0, 50.0, -50.0, -20.0],
            "estado_emocional": ["Calm", "Calm", "FOMO", "Anxious"],
            "notas": ["", "", "", ""],
        }
    )


@pytest.fixture
def df_vacio() -> pd.DataFrame:
    columnas = [
        "fecha",
        "activo",
        "direccion",
        "precio_entrada",
        "precio_salida",
        "cantidad",
        "pnl",
        "estado_emocional",
        "notas",
    ]
    return pd.DataFrame(columns=columnas)


@pytest.fixture
def df_sin_perdidas() -> pd.DataFrame:
    return pd.DataFrame({"pnl": [10.0, 20.0, 30.0]})


@pytest.fixture
def df_todas_perdidas() -> pd.DataFrame:
    return pd.DataFrame({"pnl": [-10.0, -20.0, -30.0]})


def test_win_rate(df_mixto):
    assert win_rate(df_mixto) == 50.0


def test_win_rate_df_vacio(df_vacio):
    assert win_rate(df_vacio) == 0.0


def test_pnl_total(df_mixto):
    assert pnl_total(df_mixto) == 80.0


def test_profit_factor(df_mixto):
    assert profit_factor(df_mixto) == pytest.approx(150 / 70)


def test_profit_factor_sin_perdidas(df_sin_perdidas):
    assert profit_factor(df_sin_perdidas) == float("inf")


def test_profit_factor_todas_perdidas(df_todas_perdidas):
    assert profit_factor(df_todas_perdidas) == 0.0


def test_total_operaciones(df_mixto):
    assert total_operaciones(df_mixto) == 4


def test_total_operaciones_df_vacio(df_vacio):
    assert total_operaciones(df_vacio) == 0


def test_desempeno_por_mindset(df_mixto):
    resultado = desempeno_por_mindset(df_mixto)
    fila_calm = resultado[resultado["estado_emocional"] == "Calm"].iloc[0]
    assert fila_calm["n_operaciones"] == 2
    assert fila_calm["win_rate"] == 100.0
    assert fila_calm["pnl_total"] == 150.0


def test_filtrar_periodo(df_mixto):
    filtrado = filtrar_periodo(df_mixto, "2025-10-01", "2025-10-31")
    assert len(filtrado) == 2
    assert set(filtrado["activo"]) == {"NVDA", "MSFT"}


def test_detectar_patrones(df_mixto):
    patrones = detectar_patrones(df_mixto)
    assert patrones["racha_tipo"] == "perdedora"
    assert patrones["racha_longitud"] == 2
    assert patrones["mindset_peor_pnl"] == "FOMO"
    assert patrones["activo_mas_rentable"] == "AAPL"
    assert patrones["activo_menos_rentable"] == "NVDA"


def test_detectar_patrones_df_vacio(df_vacio):
    patrones = detectar_patrones(df_vacio)
    assert patrones["racha_tipo"] is None
    assert patrones["racha_longitud"] == 0
    assert patrones["mindset_peor_pnl"] is None
    assert patrones["activo_mas_rentable"] is None
    assert patrones["activo_menos_rentable"] is None


def test_resumen(df_mixto):
    r = resumen(df_mixto)
    assert r["win_rate"] == 50.0
    assert r["pnl_total"] == 80.0
    assert r["total_operaciones"] == 4
    assert r["profit_factor"] == pytest.approx(150 / 70)
