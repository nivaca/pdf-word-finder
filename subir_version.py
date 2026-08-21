#!/usr/bin/env python3
"""
subir_version.py — cambia el número de versión del proyecto.

    python subir_version.py 1.3        cambia la versión a 1.3
    python subir_version.py --mostrar  dice cuál es la versión actual
    python subir_version.py --revisar  comprueba que todo concuerde

El número vive en un solo sitio, `__version__` en pdf_word_finder.py, y de
ahí lo toman la interfaz gráfica (que muestra `núcleo.__version__`) y la
receta de PyInstaller (que lo lee del archivo al construir). Este programa
existe por el README, que sí menciona la cifra en varios lugares y no puede
deducirla de ninguna parte.

© Nicolás Vaughan 2026. Licencia MIT.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

RAÍZ = Path(__file__).parent.absolute()
NÚCLEO = RAÍZ / "pdf_word_finder.py"
LÉAME = RAÍZ / "README.md"

# Cada patrón lleva la versión en el grupo 1. Se anclan a su contexto en vez
# de sustituir la cifra suelta: un «1.2» perdido en cualquier renglón del
# README bien puede ser otra cosa, y estropearlo sería difícil de advertir.
PATRONES_LÉAME = [
    r"\*\*Versión (\d+\.\d+(?:\.\d+)?)\*\*",
    r"Versión \*\*(\d+\.\d+(?:\.\d+)?)\*\*",
    r"pdf-word-finder (\d+\.\d+(?:\.\d+)?) — ©",
    r'--title "pdf-word-finder (\d+\.\d+(?:\.\d+)?)"',
    r"git tag -a v?(\d+\.\d+(?:\.\d+)?) -m",
    r"git push origin v?(\d+\.\d+(?:\.\d+)?)",
    r"gh release create v?(\d+\.\d+(?:\.\d+)?)",
    r'--notes "Versión (\d+\.\d+(?:\.\d+)?)\."',
    r'-m "Versión (\d+\.\d+(?:\.\d+)?)"',
]

PATRÓN_NÚCLEO = r'^(__version__\s*=\s*")(\d+\.\d+(?:\.\d+)?)(")'


def versión_actual() -> str:
    m = re.search(PATRÓN_NÚCLEO, NÚCLEO.read_text(encoding="utf-8"), re.M)
    if not m:
        sys.exit(f"error: no se encontró __version__ en {NÚCLEO.name}")
    return m.group(2)


def revisar() -> int:
    """Comprueba que el README no se haya quedado atrás."""
    actual = versión_actual()
    texto = LÉAME.read_text(encoding="utf-8")
    desfasados = []
    for patrón in PATRONES_LÉAME:
        for m in re.finditer(patrón, texto):
            if m.group(1) != actual:
                renglón = texto[: m.start()].count("\n") + 1
                desfasados.append((renglón, m.group(0).strip()))

    print(f"versión del programa: {actual}")
    if not desfasados:
        print("el README concuerda")
        return 0
    print(f"\n{len(desfasados)} menciones desfasadas en el README:")
    for renglón, fragmento in desfasados:
        print(f"  línea {renglón}: {fragmento}")
    return 1


def subir(nueva: str) -> None:
    if not re.fullmatch(r"\d+\.\d+(?:\.\d+)?", nueva):
        sys.exit(f"error: «{nueva}» no parece un número de versión (1.3, 2.0.1…)")

    anterior = versión_actual()
    if anterior == nueva:
        print(f"ya está en {nueva}; no hay nada que hacer")
        return

    # --- el programa ---
    texto = NÚCLEO.read_text(encoding="utf-8")
    texto = re.sub(PATRÓN_NÚCLEO, lambda m: m.group(1) + nueva + m.group(3),
                   texto, count=1, flags=re.M)
    NÚCLEO.write_text(texto, encoding="utf-8")
    print(f"{NÚCLEO.name}: __version__ = \"{nueva}\"")

    # --- el README ---
    texto = LÉAME.read_text(encoding="utf-8")
    total = 0
    for patrón in PATRONES_LÉAME:
        def reemplazo(m: re.Match) -> str:
            nonlocal total
            total += 1
            # Se conserva lo que rodea a la cifra, incluida la «v» si la había.
            return m.group(0)[: m.start(1) - m.start()] + nueva + \
                m.group(0)[m.end(1) - m.start():]
        texto, _ = re.subn(patrón, reemplazo, texto)
    LÉAME.write_text(texto, encoding="utf-8")
    print(f"{LÉAME.name}: {total} menciones actualizadas")

    print(f"\n{anterior} → {nueva}")
    print("\nLa interfaz gráfica y la receta de PyInstaller lo toman solas.")
    print("Falta comprometer y etiquetar:")
    print(f'    git commit -am "Versión {nueva}"')
    print(f'    git tag -a {nueva} -m "Versión {nueva}"')
    print(f"    git push origin {nueva}")


def main() -> None:
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__.strip())
    elif args[0] == "--mostrar":
        print(versión_actual())
    elif args[0] == "--revisar":
        sys.exit(revisar())
    else:
        subir(args[0])


if __name__ == "__main__":
    main()
