"""Punto de entrada del ejecutable de consola (PyInstaller).

PyInstaller necesita un archivo que ejecutar, y los módulos del paquete no
sirven para eso: sus importaciones relativas fallan fuera del paquete.
"""

from pdf_word_finder.cli import main

main()
