"""Funciones puras de análisis de rendimiento sobre el DataFrame del journal."""

import pandas as pd


def win_rate(df: pd.DataFrame) -> float:
    """Porcentaje de operaciones con pnl positivo."""
    if len(df) == 0:
        return 0.0
    return (df["pnl"] > 0).sum() / len(df) * 100


def pnl_total(df: pd.DataFrame) -> float:
    """Suma de pnl de todas las operaciones."""
    return df["pnl"].sum()


def profit_factor(df: pd.DataFrame) -> float:
    """Ganancias brutas sobre pérdidas brutas. Si no hay pérdidas, devuelve inf."""
    ganancias = df.loc[df["pnl"] > 0, "pnl"].sum()
    perdidas = df.loc[df["pnl"] < 0, "pnl"].sum()
    if perdidas == 0:
        return float("inf")
    return ganancias / abs(perdidas)


def total_operaciones(df: pd.DataFrame) -> int:
    """Número total de operaciones registradas."""
    return len(df)


def desempeno_por_mindset(df: pd.DataFrame) -> pd.DataFrame:
    """Número de operaciones, win rate y pnl total agrupados por estado emocional."""
    return (
        df.groupby("estado_emocional")
        .apply(
            lambda g: pd.Series(
                {
                    "n_operaciones": len(g),
                    "win_rate": win_rate(g),
                    "pnl_total": pnl_total(g),
                }
            ),
            include_groups=False,
        )
        .reset_index()
    )


def filtrar_periodo(df: pd.DataFrame, inicio: str, fin: str) -> pd.DataFrame:
    """Filtra operaciones con fecha entre inicio y fin (inclusive), formato YYYY-MM-DD."""
    return df[(df["fecha"] >= inicio) & (df["fecha"] <= fin)]


def resumen(df: pd.DataFrame) -> dict:
    """Los 4 KPIs principales en una sola llamada."""
    return {
        "win_rate": win_rate(df),
        "pnl_total": pnl_total(df),
        "profit_factor": profit_factor(df),
        "total_operaciones": total_operaciones(df),
    }
