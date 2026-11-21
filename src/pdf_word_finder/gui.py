"""
La interfaz gráfica de pdf-word-finder (tkinter).

© Nicolás Vaughan 2026. Distribuido bajo la licencia GNU GPL, versión 3 o
posterior (véase LICENSE).

No duplica nada del programa de línea de órdenes: la búsqueda, el informe y
la exportación son las mismas funciones del paquete, de modo que cualquier
corrección hecha allí se refleja aquí sin tocar este archivo.

Se abre con la orden `pdf-word-finder-gui` o, sin instalar el paquete, con
`python -m pdf_word_finder.gui` desde la carpeta src/.

Solo requiere tkinter, que viene con Python. En Linux, si falta:
    sudo apt install python3-tk      (Debian, Ubuntu)
    sudo dnf install python3-tkinter (Fedora)
"""

import os
import platform
import queue
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from . import __copyright__, __license__, __version__
from .extraction import Document, PdfError, extract_pages, load_pymupdf
from .patterns import PatternError
from .report import build_report, write_csv, write_txt
from .search import Options, Result, read_terms, search
from .text import plural

# --------------------------------------------------------------------------
# Búsqueda (se ejecuta en un hilo aparte)
# --------------------------------------------------------------------------


class SearchError(Exception):
    pass


_cache: dict[tuple[str, float], Document] = {}


def extract_cached(path: str) -> Document:
    """Evita releer el PDF cuando solo cambian las opciones de búsqueda."""
    key = (path, os.path.getmtime(path))
    if key not in _cache:
        _cache.clear()  # un PDF a la vez basta
        _cache[key] = extract_pages(path)
    return _cache[key]


def run_search(path: str, terms: list[str], opts: Options) -> Result:
    """La búsqueda, con los errores convertidos en SearchError, que la
    interfaz muestra en un cuadro de diálogo."""
    try:
        doc = extract_cached(path)
    except PdfError as exc:
        raise SearchError(str(exc)) from None
    except Exception as exc:
        raise SearchError(f"No se pudo abrir el PDF: {exc}") from None
    try:
        return search(doc, terms, opts)
    except PatternError as exc:
        raise SearchError(str(exc)) from None


def compose_report(result: Result, show_logical: bool, detailed: bool,
                   alphabetical: bool) -> str:
    """El mismo texto que imprime el programa de línea de órdenes. Lo único
    que cambia es que aquí las notas se muestran encima del informe,
    mientras que en la consola van al canal de error."""
    report, notes = build_report(result, show_logical=show_logical,
                                 detailed=detailed, alphabetical=alphabetical)
    return "\n\n".join(p for p in (notes, report) if p)


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
        self.últimos: Result | None = None
        self.show_logical = False
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
        self.btn_txt = ttk.Button(marco_botones, text="Guardar TXT…",
                                  command=self._guardar_txt, state="disabled")
        self.btn_txt.grid(row=0, column=1, padx=(6, 0))
        self.btn_csv = ttk.Button(marco_botones, text="Guardar CSV…",
                                  command=self._guardar_csv, state="disabled")
        self.btn_csv.grid(row=0, column=2, padx=(6, 0))
        ttk.Button(marco_botones, text="Copiar resultados",
                   command=self._copiar).grid(row=0, column=3, padx=(6, 0))
        ttk.Button(marco_botones, text="Limpiar",
                   command=self._limpiar).grid(row=0, column=4, padx=(6, 0))
        # La columna vacía se lleva el espacio sobrante y empuja el botón de
        # «Acerca de» contra el borde derecho, apartado de los de trabajo.
        marco_botones.columnconfigure(5, weight=1)
        ttk.Button(marco_botones, text="Acerca de…",
                   command=self._acerca_de).grid(row=0, column=6, sticky="e")

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
            value=f"pdf-word-finder {__version__} — listo")
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
        return read_terms(self.txt_términos.get("1.0", "end").splitlines())

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
        try:
            ancho = int(self.var_ancho.get())
        except (tk.TclError, ValueError):
            ancho = 60
        opciones = Options(
            regex=op["regex"], regex_word=op["regex_word"],
            substring=op["substring"], case_sensitive=op["case_sensitive"],
            ignore_accents=op["ignore_accents"],
            dehyphenate=not op["no_dehyphenate"],
            context_width=ancho if op["context"] else None)
        informe = {"show_logical": op["show_logical"],
                   "detailed": op["detailed"] or op["context"],
                   "alphabetical": op["alphabetical"]}

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
                resultado = run_search(ruta, términos, opciones)
                self.cola.put(("ok", (resultado, informe)))
            except SearchError as exc:
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
                resultado, informe = carga
                self.últimos = resultado
                self.show_logical = informe["show_logical"]
                self._mostrar(compose_report(resultado, **informe))
                total = resultado.total()
                páginas = resultado.pages_with_hits()
                self.var_estado.set(
                    f"{total} "
                    f"{plural(total, 'aparición', 'apariciones')} en "
                    f"{páginas} {plural(páginas, 'página', 'páginas')} "
                    f"de {resultado.total_pages}")
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

    def _datos_técnicos(self) -> str:
        """Lo que hace falta saber si algo va mal y hay que preguntar."""
        líneas = [f"Python {sys.version.split()[0]}",
                  f"Tcl/Tk {tk.TkVersion}"]
        try:
            import pypdf
            líneas.append(f"pypdf {pypdf.__version__}")
        except Exception:
            líneas.append("pypdf: no encontrado")
        # Se pregunta a la extracción, para que la ventana no pueda discrepar de
        # lo que el programa hace de veras al extraer el texto.
        mupdf = load_pymupdf()
        if mupdf is None:
            líneas.append("PyMuPDF: no instalado (se extrae con pypdf)")
        else:
            v = getattr(mupdf, "__version__", "") or ""
            if not v:  # en ediciones antiguas la versión vive en otro sitio
                try:
                    v = getattr(mupdf, "version", ("",))[0] or ""
                except Exception:
                    v = ""
            líneas.append(f"PyMuPDF {v}".strip() + " (extractor en uso)")
        if getattr(sys, "frozen", False):
            líneas.append("ejecutable autónomo (PyInstaller)")
        else:
            líneas.append("ejecutado desde el código fuente")
        líneas.append(f"sistema: {self._sistema()}")
        return "\n".join(líneas)

    @staticmethod
    def _sistema() -> str:
        s = platform.system()
        if s == "Darwin":
            nombre = f"macOS {platform.mac_ver()[0]}"
        elif s == "Windows":
            nombre = f"Windows {platform.release()}"
        else:
            nombre = f"{s} {platform.release().split('-')[0]}"
        return f"{nombre} ({platform.machine()})"

    def _acerca_de(self) -> None:
        v = tk.Toplevel(self)
        v.title("Acerca de pdf-word-finder")
        v.transient(self.winfo_toplevel())
        v.resizable(False, False)

        marco = ttk.Frame(v, padding=16)
        marco.grid(sticky="nsew")

        ttk.Label(marco, text="pdf-word-finder",
                  font=("TkDefaultFont", 14, "bold")).grid(sticky="w")
        ttk.Label(marco, text=f"Versión {__version__}").grid(
            sticky="w", pady=(2, 10))

        ttk.Label(
            marco, justify="left", wraplength=420,
            text="Busca palabras, frases o expresiones regulares en un PDF e "
                 "informa en qué páginas aparecen, distinguiendo la "
                 "numeración impresa de la secuencial del archivo.\n\n"
                 f"{__copyright__}\n"
                 f"Licencia {__license__}: puede usarse, modificarse y "
                 "distribuirse libremente, siempre que las versiones que se "
                 "distribuyan conserven esta misma licencia y vayan "
                 "acompañadas de su código fuente. Se entrega sin garantía "
                 "de ninguna clase.").grid(sticky="w")

        ttk.Separator(marco, orient="horizontal").grid(
            sticky="ew", pady=12)

        ttk.Label(marco, text="Datos técnicos",
                  font=("TkDefaultFont", 9, "bold")).grid(sticky="w")
        datos = self._datos_técnicos()
        ttk.Label(marco, text=datos, justify="left",
                  font="TkFixedFont").grid(sticky="w", pady=(4, 0))

        botones = ttk.Frame(marco)
        botones.grid(sticky="e", pady=(16, 0))
        ttk.Button(botones, text="Copiar datos técnicos",
                   command=lambda: self._al_portapapeles(datos)).grid(
                       row=0, column=0, padx=(0, 6))
        cerrar = ttk.Button(botones, text="Cerrar", command=v.destroy)
        cerrar.grid(row=0, column=1)

        v.bind("<Escape>", lambda _e: v.destroy())
        cerrar.focus_set()
        # Centrada sobre la ventana principal, no en un rincón de la pantalla.
        v.update_idletasks()
        raíz = self.winfo_toplevel()
        x = raíz.winfo_rootx() + (raíz.winfo_width() - v.winfo_width()) // 2
        y = raíz.winfo_rooty() + (raíz.winfo_height() - v.winfo_height()) // 3
        v.geometry(f"+{max(x, 0)}+{max(y, 0)}")
        v.grab_set()

    def _al_portapapeles(self, texto: str) -> None:
        self.clipboard_clear()
        self.clipboard_append(texto)
        self.var_estado.set("Datos técnicos copiados al portapapeles")

    def _guardar_txt(self) -> None:
        if not self.últimos:
            return
        ruta = filedialog.asksaveasfilename(
            title="Guardar la lista alfabetizada", defaultextension=".txt",
            filetypes=[("Texto", "*.txt"), ("Todos", "*.*")])
        if not ruta:
            return
        try:
            n = write_txt(ruta, self.últimos, self.show_logical)
        except OSError as exc:
            messagebox.showerror("Error", f"No se pudo escribir:\n{exc}")
            return
        self.var_estado.set(
            f"Lista de {n} {plural(n, 'entrada', 'entradas')} "
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
            write_csv(ruta, self.últimos)
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
        self.var_estado.set(f"pdf-word-finder {__version__} — listo")


def main() -> None:
    raíz = tk.Tk()
    raíz.title(f"pdf-word-finder {__version__}")
    raíz.minsize(640, 700)
    try:  # tema más agradable donde esté disponible
        ttk.Style().theme_use("clam")
    except tk.TclError:
        pass
    Aplicación(raíz)
    raíz.mainloop()


if __name__ == "__main__":
    main()
