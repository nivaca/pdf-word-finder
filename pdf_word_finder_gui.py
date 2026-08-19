#!/usr/bin/env python3
"""
pdf_word_finder_gui.py — interfaz gráfica sencilla para pdf_word_finder.py.

Versión 1.0
© Nicolás Vaughan 2026. Distribuido bajo licencia MIT (véase LICENSE).

No duplica nada del programa de línea de órdenes: importa
«pdf_word_finder.py» y reutiliza sus funciones (extracción del texto, normalización, construcción
de patrones, formato de las páginas). Cualquier corrección hecha allí se
refleja aquí sin tocar este archivo.

Solo requiere tkinter, que viene con Python. En Linux, si falta:
    sudo apt install python3-tk
"""

from __future__ import annotations

import csv
import os
import queue
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# --------------------------------------------------------------------------
# Carga del programa de línea de órdenes
# --------------------------------------------------------------------------
# Ambos archivos viven en la misma carpeta, de modo que basta importarlo. Es
# importante que sea una importación corriente y no una carga por ruta: así
# PyInstaller la ve al analizar el código y empaqueta el núcleo —y con él
# pypdf— sin necesidad de declararlos a mano (véase el README, §11).

try:
    import pdf_word_finder as núcleo
except ImportError as exc:  # sin el núcleo no hay nada que hacer
    _raíz = tk.Tk()
    _raíz.withdraw()
    messagebox.showerror(
        "pdf-word-finder",
        f"No se encontró «pdf_word_finder.py».\n\n"
        f"Debe estar en la misma carpeta que esta interfaz.\n\n{exc}")
    sys.exit(1)


# --------------------------------------------------------------------------
# Búsqueda (se ejecuta en un hilo aparte)
# --------------------------------------------------------------------------


class ErrorDeBúsqueda(Exception):
    pass


_caché: dict[tuple, tuple] = {}


def extraer_con_caché(ruta: str):
    """Evita releer el PDF cuando solo cambian las opciones de búsqueda."""
    clave = (ruta, os.path.getmtime(ruta))
    if clave not in _caché:
        _caché.clear()  # un PDF a la vez basta
        _caché[clave] = núcleo.extract_pages(ruta)
    return _caché[clave]


def buscar(ruta: str, términos: list[str], op: dict) -> dict:
    """Ejecuta la búsqueda y devuelve todo lo necesario para el informe.

    Las funciones del núcleo terminan el programa con sys.exit() cuando algo
    falla, lo cual es correcto en la línea de órdenes pero cerraría la
    ventana sin explicación. Aquí se captura SystemExit y se convierte en un
    error normal, que la interfaz muestra en un cuadro de diálogo.
    """
    try:
        textos, rótulos, hay_rótulos = extraer_con_caché(ruta)
    except SystemExit as exc:
        raise ErrorDeBúsqueda(str(exc) or "No se pudo abrir el PDF.") from None
    except Exception as exc:
        raise ErrorDeBúsqueda(f"No se pudo abrir el PDF: {exc}") from None

    páginas = [núcleo.normalise(t, not op["no_dehyphenate"],
                                op["ignore_accents"]) for t in textos]

    patrones = {}
    for t in términos:
        try:
            patrones[t] = núcleo.build_pattern(
                t, as_regex=op["regex"], substring=op["substring"],
                case_sensitive=op["case_sensitive"],
                ignore_accents=op["ignore_accents"],
                regex_word=op["regex_word"])
        except SystemExit as exc:
            raise ErrorDeBúsqueda(str(exc)) from None

    resultados: dict[str, list] = {t: [] for t in términos}
    for i, página in enumerate(páginas):
        for término, patrón in patrones.items():
            apariciones = list(patrón.finditer(página))
            if not apariciones:
                continue
            fragmentos = []
            if op["context"]:
                w = op["context_width"]
                for m in apariciones:
                    a = max(0, m.start() - w)
                    b = min(len(página), m.end() + w)
                    fragmentos.append(("…" if a else "") + página[a:b].strip()
                                      + ("…" if b < len(página) else ""))
            resultados[término].append(
                (i + 1, rótulos[i], len(apariciones), fragmentos))

    vacías = sum(1 for p in páginas if not p.strip())
    return {"resultados": resultados, "términos": términos,
            "hay_rótulos": hay_rótulos, "vacías": vacías,
            "total_páginas": len(páginas), "show_logical": op["show_logical"],
            "detailed": op["detailed"] or op["context"],
            "alphabetical": op["alphabetical"]}


def componer_informe(datos: dict) -> str:
    """Arma el mismo texto que imprime el programa de línea de órdenes.

    El formato lo compone el núcleo (build_report), no esta interfaz: así no
    hay dos versiones del informe que puedan divergir. Lo único que cambia
    es que aquí las notas se muestran junto al informe, mientras que en la
    consola van al canal de error para no ensuciar la salida.
    """
    informe, notas = núcleo.build_report(
        datos["términos"], datos["resultados"],
        has_labels=datos["hay_rótulos"], empty=datos["vacías"],
        total_pages=datos["total_páginas"],
        show_logical=datos["show_logical"],
        detailed=datos["detailed"],
        alphabetical=datos["alphabetical"])
    return "\n\n".join(p for p in (notas, informe) if p)


# --------------------------------------------------------------------------
# Interfaz
# --------------------------------------------------------------------------


class Aplicación(ttk.Frame):
    def __init__(self, raíz: tk.Tk):
        super().__init__(raíz, padding=10)
        self.raíz = raíz
        self.grid(sticky="nsew")
        raíz.columnconfigure(0, weight=1)
        raíz.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(4, weight=1)

        self.cola: queue.Queue = queue.Queue()
        self.últimos: dict | None = None
        self.buscando = False

        self._construir()
        self.raíz.after(100, self._revisar_cola)

    # -- construcción de los controles ------------------------------------

    def _construir(self) -> None:
        # --- archivo ---
        marco_archivo = ttk.LabelFrame(self, text="Archivo PDF", padding=8)
        marco_archivo.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        marco_archivo.columnconfigure(0, weight=1)

        self.var_ruta = tk.StringVar()
        ttk.Entry(marco_archivo, textvariable=self.var_ruta).grid(
            row=0, column=0, sticky="ew", padx=(0, 6))
        ttk.Button(marco_archivo, text="Examinar…",
                   command=self._elegir_archivo).grid(row=0, column=1)

        # --- términos ---
        marco_términos = ttk.LabelFrame(
            self, text="Términos (uno por renglón; «re:» para expresión "
                       "regular; «#» inicia un comentario)", padding=8)
        marco_términos.grid(row=1, column=0, sticky="ew", pady=(0, 8))
        marco_términos.columnconfigure(0, weight=1)

        self.txt_términos = tk.Text(marco_términos, height=5, wrap="none",
                                    undo=True, font="TkFixedFont")
        self.txt_términos.grid(row=0, column=0, sticky="ew")
        barra_t = ttk.Scrollbar(marco_términos, orient="vertical",
                                command=self.txt_términos.yview)
        barra_t.grid(row=0, column=1, sticky="ns")
        self.txt_términos.configure(yscrollcommand=barra_t.set)
        ttk.Button(marco_términos, text="Cargar lista…",
                   command=self._cargar_lista).grid(row=1, column=0,
                                                    sticky="w", pady=(6, 0))

        # --- opciones ---
        marco_op = ttk.LabelFrame(self, text="Opciones", padding=8)
        marco_op.grid(row=2, column=0, sticky="ew", pady=(0, 8))

        self.op = {
            "ignore_accents": tk.BooleanVar(value=True),
            "case_sensitive": tk.BooleanVar(value=False),
            "substring": tk.BooleanVar(value=False),
            "regex": tk.BooleanVar(value=False),
            "regex_word": tk.BooleanVar(value=False),
            "no_dehyphenate": tk.BooleanVar(value=False),
            "show_logical": tk.BooleanVar(value=False),
            "alphabetical": tk.BooleanVar(value=False),
            "detailed": tk.BooleanVar(value=False),
            "context": tk.BooleanVar(value=False),
        }
        etiquetas = [
            ("ignore_accents", "Ignorar tildes"),
            ("case_sensitive", "Distinguir mayúsculas"),
            ("substring", "Buscar dentro de palabras"),
            ("regex", "Todos los términos son expresiones regulares"),
            ("regex_word", "Delimitar las expresiones regulares"),
            ("no_dehyphenate", "Conservar la partición de renglón"),
            ("show_logical", "Mostrar también la página secuencial"),
            ("alphabetical", "Ordenar alfabéticamente"),
            ("detailed", "Informe detallado"),
            ("context", "Mostrar contexto (implica el informe detallado)"),
        ]
        for i, (clave, texto) in enumerate(etiquetas):
            ttk.Checkbutton(marco_op, text=texto, variable=self.op[clave]
                            ).grid(row=i // 2, column=i % 2, sticky="w",
                                   padx=(0, 16))

        marco_ancho = ttk.Frame(marco_op)
        marco_ancho.grid(row=6, column=0, columnspan=2, sticky="w",
                         pady=(6, 0))
        ttk.Label(marco_ancho, text="Ancho del contexto:").grid(row=0,
                                                                column=0)
        self.var_ancho = tk.IntVar(value=60)
        ttk.Spinbox(marco_ancho, from_=10, to=300, increment=10, width=6,
                    textvariable=self.var_ancho).grid(row=0, column=1,
                                                      padx=(6, 0))

        # --- botones ---
        marco_botones = ttk.Frame(self)
        marco_botones.grid(row=3, column=0, sticky="ew", pady=(0, 8))
        self.btn_buscar = ttk.Button(marco_botones, text="Buscar",
                                     command=self._buscar)
        self.btn_buscar.grid(row=0, column=0)
        self.btn_txt = ttk.Button(marco_botones, text="Guardar lista TXT…",
                                  command=self._guardar_txt, state="disabled")
        self.btn_txt.grid(row=0, column=1, padx=(6, 0))
        self.btn_csv = ttk.Button(marco_botones, text="Guardar CSV…",
                                  command=self._guardar_csv, state="disabled")
        self.btn_csv.grid(row=0, column=2, padx=(6, 0))
        ttk.Button(marco_botones, text="Copiar resultados",
                   command=self._copiar).grid(row=0, column=3, padx=(6, 0))
        ttk.Button(marco_botones, text="Limpiar",
                   command=self._limpiar).grid(row=0, column=4, padx=(6, 0))

        # --- resultados ---
        marco_res = ttk.LabelFrame(self, text="Resultados", padding=8)
        marco_res.grid(row=4, column=0, sticky="nsew", pady=(0, 8))
        marco_res.columnconfigure(0, weight=1)
        marco_res.rowconfigure(0, weight=1)

        # Monoespaciada: así la columna de números de página queda alineada.
        self.txt_res = tk.Text(marco_res, height=16, wrap="word",
                               state="disabled", font="TkFixedFont")
        self.txt_res.grid(row=0, column=0, sticky="nsew")
        barra_r = ttk.Scrollbar(marco_res, orient="vertical",
                                command=self.txt_res.yview)
        barra_r.grid(row=0, column=1, sticky="ns")
        self.txt_res.configure(yscrollcommand=barra_r.set)

        # --- barra de estado ---
        self.var_estado = tk.StringVar(
            value=f"pdf-word-finder {núcleo.__version__} — listo")
        ttk.Label(self, textvariable=self.var_estado,
                  relief="sunken", anchor="w").grid(row=5, column=0,
                                                    sticky="ew")

    # -- acciones ---------------------------------------------------------

    def _elegir_archivo(self) -> None:
        ruta = filedialog.askopenfilename(
            title="Seleccione un archivo PDF",
            filetypes=[("Archivos PDF", "*.pdf"), ("Todos", "*.*")])
        if ruta:
            self.var_ruta.set(ruta)

    def _cargar_lista(self) -> None:
        ruta = filedialog.askopenfilename(
            title="Seleccione un archivo de términos",
            filetypes=[("Texto", "*.txt"), ("Todos", "*.*")])
        if not ruta:
            return
        try:
            with open(ruta, encoding="utf-8") as fh:
                contenido = fh.read()
        except OSError as exc:
            messagebox.showerror("Error", f"No se pudo leer el archivo:\n{exc}")
            return
        actual = self.txt_términos.get("1.0", "end").strip()
        self.txt_términos.insert("end", ("\n" if actual else "") + contenido)

    def _términos(self) -> list[str]:
        términos = []
        for renglón in self.txt_términos.get("1.0", "end").splitlines():
            renglón = renglón.split("#", 1)[0].strip()
            if renglón:
                términos.append(renglón)
        return términos

    def _buscar(self) -> None:
        if self.buscando:
            return
        ruta = self.var_ruta.get().strip()
        if not ruta:
            messagebox.showwarning("Falta el archivo",
                                   "Seleccione primero un archivo PDF.")
            return
        términos = self._términos()
        if not términos:
            messagebox.showwarning("Faltan términos",
                                   "Escriba al menos un término de búsqueda.")
            return

        op = {c: v.get() for c, v in self.op.items()}
        op["context_width"] = self.var_ancho.get()

        self.buscando = True
        self.btn_buscar.configure(state="disabled")
        self.btn_csv.configure(state="disabled")
        self.btn_txt.configure(state="disabled")
        self.var_estado.set("Buscando… (los PDF extensos tardan un poco)")

        # La extracción de texto puede tomar varios segundos en un libro
        # entero; en un hilo aparte la ventana sigue respondiendo. tkinter no
        # es seguro entre hilos, así que el resultado vuelve por una cola y
        # se recoge desde el hilo principal.
        def tarea():
            try:
                self.cola.put(("ok", buscar(ruta, términos, op)))
            except ErrorDeBúsqueda as exc:
                self.cola.put(("error", str(exc)))
            except Exception as exc:  # red de seguridad
                self.cola.put(("error", f"Error inesperado: {exc}"))

        threading.Thread(target=tarea, daemon=True).start()

    def _revisar_cola(self) -> None:
        try:
            tipo, carga = self.cola.get_nowait()
        except queue.Empty:
            pass
        else:
            self.buscando = False
            self.btn_buscar.configure(state="normal")
            if tipo == "error":
                self.var_estado.set("Error")
                messagebox.showerror("Error", carga)
            else:
                self.últimos = carga
                self._mostrar(componer_informe(carga))
                total = sum(f[2] for filas in carga["resultados"].values()
                            for f in filas)
                páginas = len({f[0] for filas in carga["resultados"].values()
                               for f in filas})
                self.var_estado.set(
                    f"{total} "
                    f"{núcleo.plural(total, 'aparición', 'apariciones')} en "
                    f"{páginas} "
                    f"{núcleo.plural(páginas, 'página', 'páginas')} "
                    f"de {carga['total_páginas']}")
                estado = "normal" if total else "disabled"
                self.btn_csv.configure(state=estado)
                self.btn_txt.configure(state=estado)
        finally:
            self.raíz.after(100, self._revisar_cola)

    def _mostrar(self, texto: str) -> None:
        self.txt_res.configure(state="normal")
        self.txt_res.delete("1.0", "end")
        self.txt_res.insert("1.0", texto)
        self.txt_res.configure(state="disabled")

    def _copiar(self) -> None:
        texto = self.txt_res.get("1.0", "end").strip()
        if not texto:
            return
        self.raíz.clipboard_clear()
        self.raíz.clipboard_append(texto)
        self.var_estado.set("Resultados copiados al portapapeles")

    def _guardar_txt(self) -> None:
        if not self.últimos:
            return
        ruta = filedialog.asksaveasfilename(
            title="Guardar la lista alfabetizada", defaultextension=".txt",
            filetypes=[("Texto", "*.txt"), ("Todos", "*.*")])
        if not ruta:
            return
        try:
            n = núcleo.write_txt(ruta, self.últimos["términos"],
                                 self.últimos["resultados"],
                                 self.últimos["show_logical"])
        except OSError as exc:
            messagebox.showerror("Error", f"No se pudo escribir:\n{exc}")
            return
        self.var_estado.set(
            f"Lista de {n} {núcleo.plural(n, 'entrada', 'entradas')} "
            f"escrita en {ruta}")

    def _guardar_csv(self) -> None:
        if not self.últimos:
            return
        ruta = filedialog.asksaveasfilename(
            title="Guardar resultados", defaultextension=".csv",
            filetypes=[("CSV", "*.csv"), ("Todos", "*.*")])
        if not ruta:
            return
        try:
            with open(ruta, "w", newline="", encoding="utf-8") as fh:
                w = csv.writer(fh)
                w.writerow(["termino", "pagina_secuencial", "pagina_rotulada",
                            "apariciones", "contexto"])
                orden = sorted(self.últimos["términos"],
                               key=lambda t: núcleo.sort_key(
                                   núcleo.display_term(t)))
                for término in orden:
                    for lg, lb, c, frags in self.últimos["resultados"].get(
                            término, []):
                        w.writerow([núcleo.display_term(término), lg, lb, c,
                                    " | ".join(frags)])
        except OSError as exc:
            messagebox.showerror("Error", f"No se pudo escribir:\n{exc}")
            return
        self.var_estado.set(f"CSV escrito en {ruta}")

    def _limpiar(self) -> None:
        self.txt_términos.delete("1.0", "end")
        self._mostrar("")
        self.últimos = None
        self.btn_csv.configure(state="disabled")
        self.btn_txt.configure(state="disabled")
        self.var_estado.set(f"pdf-word-finder {núcleo.__version__} — listo")


def main() -> None:
    raíz = tk.Tk()
    raíz.title(f"pdf-word-finder {núcleo.__version__}")
    raíz.minsize(640, 700)
    try:  # tema más agradable donde esté disponible
        ttk.Style().theme_use("clam")
    except tk.TclError:
        pass
    Aplicación(raíz)
    raíz.mainloop()


if __name__ == "__main__":
    main()
