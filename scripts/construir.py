#!/usr/bin/env python3
"""
construir.py — construye los ejecutables y los empaqueta para distribuir.

    python scripts/construir.py

Ejecuta PyInstaller con la receta packaging/pdf_word_finder.spec y comprime
la carpeta resultante, junto con LICENSE, los README y docs/, en

    dist/pdf-word-finder-SISTEMA-VERSIÓN.zip

donde SISTEMA es linux, win o macos. Usa el intérprete con que se lo llama,
que necesita PyInstaller y pypdf instalados:

    pip install pyinstaller "pypdf[crypto]"

PyInstaller no compila para otros sistemas: el paquete de Windows hay que
construirlo en Windows, y el de macOS en un Mac.

© Nicolás Vaughan 2026. Licencia GNU GPL v3 o posterior.
"""

import platform
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

RAÍZ = Path(__file__).resolve().parent.parent
RECETA = RAÍZ / "packaging" / "pdf_word_finder.spec"
DIST = RAÍZ / "dist"
BUILD = RAÍZ / "build"
ACOMPAÑANTES = ["LICENSE", "README.md", "README_en.md", "CHANGELOG.md",
                "CHANGELOG_es.md", "docs"]

if sys.version_info < (3, 14):
    sys.exit("se necesita Python 3.14 o posterior")


def versión() -> str:
    texto = (RAÍZ / "src" / "pdf_word_finder" / "__init__.py").read_text(
        encoding="utf-8")
    return re.search(r'^__version__\s*=\s*"([^"]+)"', texto, re.M).group(1)


def sistema() -> str:
    return {"Windows": "win", "Darwin": "macos"}.get(platform.system(),
                                                      "linux")


def comprimir(carpeta: Path, destino: Path) -> None:
    """Comprime `carpeta` en `destino`, con la carpeta como raíz.

    En macOS se usa ditto: el paquete .app contiene enlaces simbólicos que
    zipfile convertiría en copias, y la aplicación no abriría.
    """
    if sistema() == "macos":
        subprocess.run(["ditto", "-c", "-k", "--sequesterRsrc", "--keepParent",
                        str(carpeta), str(destino)], check=True)
        return
    with zipfile.ZipFile(destino, "w", zipfile.ZIP_DEFLATED) as zf:
        for ruta in sorted(carpeta.rglob("*")):
            nombre = ruta.relative_to(carpeta.parent)
            if ruta.is_symlink() or ruta.is_file():
                zf.write(ruta, nombre)
            elif ruta.is_dir():
                zf.write(ruta, f"{nombre}/")


def main() -> None:
    try:
        import PyInstaller  # noqa: F401
        import pypdf  # noqa: F401
    except ImportError as exc:
        sys.exit(f"error: falta {exc.name}. Instálelo con:\n"
                 f'    {sys.executable} -m pip install pyinstaller '
                 f'"pypdf[crypto]"')

    v = versión()
    print(f"pdf-word-finder {v}, para {sistema()}, con Python "
          f"{platform.python_version()}")

    subprocess.run([sys.executable, "-m", "PyInstaller", "--clean",
                    "--noconfirm", "--distpath", str(DIST), "--workpath",
                    str(BUILD), str(RECETA)], check=True, cwd=RAÍZ)

    carpeta = DIST / "pdf-word-finder"
    for nombre in ACOMPAÑANTES:
        origen = RAÍZ / nombre
        if origen.is_dir():
            shutil.copytree(origen, carpeta / nombre, dirs_exist_ok=True)
        else:
            shutil.copy2(origen, carpeta / nombre)

    destino = DIST / f"pdf-word-finder-{sistema()}-{v}.zip"
    destino.unlink(missing_ok=True)
    comprimir(carpeta, destino)
    print(f"\n{destino.relative_to(RAÍZ)} "
          f"({destino.stat().st_size / 1_000_000:.1f} MB)")


if __name__ == "__main__":
    main()
