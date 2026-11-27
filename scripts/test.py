#!/usr/bin/env python3
"""
test.py — corre a la vez las pruebas de pdf-word-finder.

    python scripts/test.py [-j N] [-v] [NOMBRE ...]

Cada archivo de pruebas (tests/test_*.py) corre en un proceso de pytest
propio, tantos a la vez como procesadores tenga el computador (-j lo cambia),
primero los más lentos; así la suite tarda más o menos lo que su archivo más
lento, y no la suma de todos. Cada proceso tiene su carpeta personal, su
carpeta temporal de pytest y su carpeta de ejecución; los paquetes de pip
--user siguen visibles (PYTHONUSERBASE).

Los NOMBRE eligen qué correr: un archivo (test_cli) o un patrón (test_*e*).
Al final aparecen los archivos que fallaron, con su salida, y los totales;
-v muestra además cada archivo a medida que termina. El código de salida es
1 si falló alguna prueba. (pytest, a secas, las corre una tras otra.)

Necesita pytest y pypdf en el intérprete con que se lo llama:

    pip install -e ".[dev]"

© Nicolás Vaughan 2026. Licencia GNU GPL v3 o posterior.
"""

from __future__ import annotations

import argparse
import fnmatch
import os
import re
import shutil
import site
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

RAÍZ = Path(__file__).resolve().parent.parent
PRUEBAS = RAÍZ / "tests"
# Los que más tardan arrancan primero (los demás siguen en orden alfabético)
LENTOS = ("test_gui.py",)


def archivos(nombres: list[str]) -> list[Path]:
    """The test files to run, the slowest first."""
    hallados = sorted(PRUEBAS.glob("test_*.py"))
    if nombres:
        hallados = [p for p in hallados
                    if any(fnmatch.fnmatch(p.name, n) or fnmatch.fnmatch(p.stem, n)
                           for n in nombres)]

    def puesto(p: Path) -> int:
        return LENTOS.index(p.name) if p.name in LENTOS else len(LENTOS)

    return sorted(hallados, key=puesto)


def correr(ruta: Path, trabajo: Path, entorno: dict) -> tuple[Path, int, str, float]:
    """RUTA run by pytest in a process of its own: (path, exit status, output, seconds)."""
    propio = trabajo / ruta.stem
    for sub in ("home", "tmp", "run"):
        (propio / sub).mkdir(parents=True, exist_ok=True)
    (propio / "run").chmod(0o700)
    # HOME en Linux y macOS, USERPROFILE en Windows
    entorno = {**entorno, "HOME": str(propio / "home"),
               "USERPROFILE": str(propio / "home"),
               "XDG_RUNTIME_DIR": str(propio / "run")}
    inicio = time.time()
    hecho = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider",
                            f"--basetemp={propio / 'tmp'}", str(ruta)],
                           cwd=RAÍZ, env=entorno, stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT, text=True, errors="replace")
    return ruta, hecho.returncode, hecho.stdout, time.time() - inicio


def cuentas(salida: str) -> dict[str, int]:
    """{'passed': n, 'failed': n, ...} from pytest's summary: the last line
    that says how long it took."""
    líneas = [l for l in salida.splitlines() if re.search(r"\bin \d+(\.\d+)?s\b", l)]
    última = líneas[-1] if líneas else ""
    return {k: int(n) for n, k in
            re.findall(r"(\d+) (passed|failed|skipped|errors?)", última)}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="scripts/test.py",
        description="Corre las pruebas de pdf-word-finder, cada archivo en un "
                    "proceso propio, a la vez.")
    parser.add_argument("nombres", nargs="*", metavar="NOMBRE",
                        help="archivos o patrones que correr (por omisión, todos)")
    parser.add_argument("-j", "--jobs", type=int, default=os.cpu_count() or 2,
                        help="cuántos a la vez (por omisión, los procesadores)")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="mostrar cada archivo cuando termina")
    args = parser.parse_args(argv)
    pendientes = archivos(args.nombres)
    if not pendientes:
        print("scripts/test.py: ninguna prueba coincide con " + " ".join(args.nombres),
              file=sys.stderr)
        return 2
    trabajo = Path(tempfile.mkdtemp(prefix="pdf-word-finder-tests-"))
    inicio = time.time()
    fallidos: list[tuple[Path, str]] = []
    totales: dict[str, int] = {}
    try:
        with ThreadPoolExecutor(max(1, args.jobs)) as grupo:
            # Los paquetes de pip --user siguen visibles aunque HOME cambie
            entorno = {**os.environ, "PYTHONUSERBASE":
                       os.environ.get("PYTHONUSERBASE") or site.getuserbase()}
            tareas = [grupo.submit(correr, ruta, trabajo, entorno)
                      for ruta in pendientes]
            for n, tarea in enumerate(as_completed(tareas), 1):
                ruta, estado, salida, segundos = tarea.result()
                halladas = cuentas(salida)
                for k, v in halladas.items():
                    totales[k] = totales.get(k, 0) + v
                # (5: pytest no encontró pruebas en el archivo; no es un fallo)
                if estado not in (0, 5):
                    fallidos.append((ruta, salida))
                if args.verbose or estado not in (0, 5):
                    marca = "ok" if estado in (0, 5) else "FAILED"
                    print(f"[{n}/{len(pendientes)}] {ruta.name}: "
                          f"{halladas.get('passed', 0)} passed, {segundos:.1f}s, {marca}",
                          flush=True)
    finally:
        shutil.rmtree(trabajo, ignore_errors=True)
    for ruta, salida in fallidos:
        print(f"\n{'=' * 70}\n{ruta.name}\n{'=' * 70}\n{salida.rstrip()}")
    dicho = ", ".join(f"{v} {k}" for k, v in sorted(totales.items()))
    print(f"\n{dicho} ({len(pendientes)} files) in {time.time() - inicio:.1f}s: "
          + (f"FAILED ({len(fallidos)} files)" if fallidos else "OK"))
    return 1 if fallidos else 0


if __name__ == "__main__":
    sys.exit(main())
