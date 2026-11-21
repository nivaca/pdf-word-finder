"""Castellanización de los mensajes propios de argparse.

argparse toma sus cadenas de `gettext`, importadas en el módulo como `_` y
`ngettext`. Al sustituir esos nombres por una tabla propia, los rótulos
«usage:», «options:», «error:» etc. salen en español sin necesidad de
instalar catálogos .mo. Basta importar este módulo antes de crear el
analizador.
"""

import argparse

_ES = {
    "usage: ": "uso: ",
    "positional arguments": "argumentos posicionales",
    "options": "opciones",
    "optional arguments": "argumentos opcionales",
    "show this help message and exit": "muestra esta ayuda y termina",
    "show program's version number and exit":
        "muestra la versión del programa y termina",
    "%(prog)s: error: %(message)s\n": "%(prog)s: error: %(message)s\n",
    "the following arguments are required: %s":
        "faltan los siguientes argumentos: %s",
    "unrecognized arguments: %s": "argumentos no reconocidos: %s",
    "argument %(argument_name)s: %(message)s":
        "argumento %(argument_name)s: %(message)s",
    "invalid %(type)s value: %(value)r":
        "valor de tipo %(type)s no válido: %(value)r",
    "expected one argument": "se esperaba un argumento",
    "expected at most one argument": "se esperaba a lo sumo un argumento",
    "expected at least one argument": "se esperaba al menos un argumento",
    "ignored explicit argument %r": "se ignoró el argumento explícito %r",
    "not allowed with argument %s": "no se permite junto con el argumento %s",
    "one of the arguments %s is required":
        "se requiere alguno de los argumentos %s",
    "ambiguous option: %(option)s could match %(matches)s":
        "opción ambigua: %(option)s puede corresponder a %(matches)s",
    "unexpected option string: %s": "opción inesperada: %s",
    "cannot have multiple subparser arguments":
        "no puede haber varios argumentos de subanalizador",
    "no such option: %s": "no existe la opción: %s",
}

argparse._ = lambda s: _ES.get(s, s)  # type: ignore[attr-defined]
argparse.ngettext = (  # type: ignore[attr-defined]
    lambda sing, plur, n: _ES.get(sing if n == 1 else plur,
                                  sing if n == 1 else plur))
