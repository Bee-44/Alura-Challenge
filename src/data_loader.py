"""Carga, validación y escritura del journal de operaciones (CSV)."""

from pathlib import Path

import pandas as pd

COLUMNAS = [
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

DIRECCIONES = ("long", "short")
MINDSETS = ("Calm", "Anxious", "Confident", "FOMO")

_COLUMNAS_NUMERICAS = ["precio_entrada", "precio_salida", "cantidad", "pnl"]


def calcular_pnl(entrada: float, salida: float, cantidad: float, direccion: str) -> float:
    """Calcula el PnL de una operación según dirección long/short."""
    signo = 1 if direccion == "long" else -1
    return (salida - entrada) * cantidad * signo


def _validar_columnas(df: pd.DataFrame) -> None:
    faltantes = [c for c in COLUMNAS if c not in df.columns]
    if faltantes:
        raise ValueError(f"Faltan columnas requeridas: {faltantes}")


def _validar_valores(df: pd.DataFrame) -> None:
    direcciones_invalidas = set(df["direccion"].unique()) - set(DIRECCIONES)
    if direcciones_invalidas:
        raise ValueError(
            f"Valores inválidos en 'direccion': {direcciones_invalidas}. "
            f"Permitidos: {DIRECCIONES}"
        )

    mindsets_invalidos = set(df["estado_emocional"].unique()) - set(MINDSETS)
    if mindsets_invalidos:
        raise ValueError(
            f"Valores inválidos en 'estado_emocional': {mindsets_invalidos}. "
            f"Permitidos: {MINDSETS}"
        )


def cargar_journal(ruta: Path) -> pd.DataFrame:
    """Lee el CSV del journal, valida su esquema y castea tipos.

    Lanza ValueError con un mensaje descriptivo si el CSV no cumple el
    esquema esperado (columnas faltantes o valores fuera de los permitidos).
    """
    df = pd.read_csv(ruta)
    _validar_columnas(df)

    df["fecha"] = pd.to_datetime(df["fecha"])
    for columna in _COLUMNAS_NUMERICAS:
        df[columna] = pd.to_numeric(df[columna])

    _validar_valores(df)

    return df


def agregar_operacion(ruta: Path, operacion: dict) -> pd.DataFrame:
    """Valida una operación nueva y la añade al CSV del journal.

    `operacion` debe traer todas las claves de COLUMNAS. Devuelve el
    DataFrame completo ya actualizado.
    """
    faltantes = [c for c in COLUMNAS if c not in operacion]
    if faltantes:
        raise ValueError(f"Faltan campos en la operación: {faltantes}")

    if operacion["direccion"] not in DIRECCIONES:
        raise ValueError(
            f"Dirección inválida: {operacion['direccion']!r}. Permitidas: {DIRECCIONES}"
        )
    if operacion["estado_emocional"] not in MINDSETS:
        raise ValueError(
            f"Estado emocional inválido: {operacion['estado_emocional']!r}. "
            f"Permitidos: {MINDSETS}"
        )

    fila = pd.DataFrame([operacion], columns=COLUMNAS)
    fila.to_csv(ruta, mode="a", header=False, index=False)

    return cargar_journal(ruta)


if __name__ == "__main__":
    df = cargar_journal(Path("data/sample_journal.csv"))
    print(df.dtypes)
    print(f"\n{len(df)} operaciones cargadas.")
