from __future__ import annotations

import csv
import io
import sys
import urllib.parse
import urllib.request
from pathlib import Path


BASE_URL = "https://exoplanetarchive.ipac.caltech.edu/TAP/sync"
QUERY = "select * from ps where default_flag=1 order by pl_name"

# El CSV queda en la misma carpeta que este script: src/
OUTPUT_FILE = Path(__file__).resolve().parent / "exoplanets_ps_default.csv"


def descargar_csv() -> bytes:
    """Descarga la solución por defecto de cada exoplaneta confirmado."""
    params = urllib.parse.urlencode(
        {
            "query": QUERY,
            "format": "csv",
        }
    )
    url = f"{BASE_URL}?{params}"

    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Atlas-de-Exoplanetas-USACH/1.0",
            "Accept": "text/csv",
        },
    )

    with urllib.request.urlopen(request, timeout=120) as response:
        if response.status != 200:
            raise RuntimeError(f"NASA respondió con HTTP {response.status}")
        return response.read()


def validar_csv(data: bytes) -> int:
    """
    Verifica que la descarga parezca un CSV válido de la tabla PS
    y que solo contenga soluciones con default_flag = 1.
    """
    text = data.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))

    if not reader.fieldnames:
        raise ValueError("El archivo descargado no contiene encabezados.")

    columnas = set(reader.fieldnames)
    requeridas = {"pl_name", "default_flag", "discoverymethod"}

    faltantes = requeridas - columnas
    if faltantes:
        raise ValueError(
            "Faltan columnas esperadas en la descarga: "
            + ", ".join(sorted(faltantes))
        )

    filas = 0
    for row in reader:
        filas += 1
        flag = str(row.get("default_flag", "")).strip()

        if flag not in {"1", "1.0"}:
            raise ValueError(
                f"Se encontró una fila con default_flag={flag!r}; "
                "la descarga no corresponde al catálogo esperado."
            )

    if filas < 1000:
        raise ValueError(
            f"La descarga contiene solo {filas} filas; no se reemplazará el CSV."
        )

    return filas


def guardar_si_cambio(data: bytes) -> bool:
    """Reemplaza el CSV solo si el contenido realmente cambió."""
    if OUTPUT_FILE.exists() and OUTPUT_FILE.read_bytes() == data:
        return False

    temp_file = OUTPUT_FILE.with_suffix(".csv.tmp")
    temp_file.write_bytes(data)
    temp_file.replace(OUTPUT_FILE)
    return True


def main() -> int:
    try:
        print("Descargando catálogo actualizado desde NASA Exoplanet Archive...")
        data = descargar_csv()

        filas = validar_csv(data)
        cambio = guardar_si_cambio(data)

        print(f"Catálogo válido: {filas} exoplanetas.")

        if cambio:
            print(f"CSV actualizado: {OUTPUT_FILE}")
        else:
            print("No hay cambios respecto al CSV existente.")

        return 0

    except Exception as exc:
        print(f"ERROR: no se pudo actualizar el catálogo: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
