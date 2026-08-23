#!/usr/bin/env python3
"""
md_convert.py
=============

CLI para convertir archivos Markdown (.md) a HTML o EPUB, con soporte
para aplicar una hoja de estilos CSS personalizada y procesar archivos
individuales o carpetas completas.
Licencia: MIT
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List, Optional

import markdown
from ebooklib import epub


CSS_POR_DEFECTO = """
body { font-family: -apple-system, Helvetica, Arial, sans-serif; max-width: 800px;
       margin: 40px auto; padding: 0 20px; line-height: 1.6; color: #222; }
h1, h2, h3 { color: #111; }
code { background: #f4f4f4; padding: 2px 5px; border-radius: 4px; }
pre { background: #f4f4f4; padding: 12px; border-radius: 6px; overflow-x: auto; }
blockquote { border-left: 4px solid #ccc; margin: 0; padding-left: 16px; color: #555; }
"""


# --------------------------------------------------------------------------- #
# Utilidades
# --------------------------------------------------------------------------- #

def _leer_css(ruta_css: Optional[str]) -> str:
    """Lee un archivo CSS personalizado o devuelve el CSS por defecto."""
    if not ruta_css:
        return CSS_POR_DEFECTO

    path = Path(ruta_css)
    if not path.exists():
        raise FileNotFoundError(f"No se encontró el archivo CSS: '{path}'")
    return path.read_text(encoding="utf-8")


def _markdown_a_html_body(texto_md: str) -> str:
    """Convierte texto Markdown a un fragmento HTML (sin <html>/<body>)."""
    return markdown.markdown(
        texto_md, extensions=["extra", "toc", "fenced_code", "tables"]
    )


# --------------------------------------------------------------------------- #
# Conversión a HTML
# --------------------------------------------------------------------------- #

def convertir_a_html(ruta_md: Path, ruta_salida: Path, css: str) -> None:
    """Convierte un archivo .md individual a un archivo .html estilizado."""
    texto_md = ruta_md.read_text(encoding="utf-8")
    cuerpo_html = _markdown_a_html_body(texto_md)
    titulo = ruta_md.stem

    documento = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>{titulo}</title>
    <style>{css}</style>
</head>
<body>
{cuerpo_html}
</body>
</html>"""

    ruta_salida.parent.mkdir(parents=True, exist_ok=True)
    ruta_salida.write_text(documento, encoding="utf-8")
    print(f"✅ HTML generado: '{ruta_salida}'")


# --------------------------------------------------------------------------- #
# Conversión a EPUB
# --------------------------------------------------------------------------- #

def convertir_a_epub(ruta_md: Path, ruta_salida: Path, css: str) -> None:
    """Convierte un archivo .md individual a un libro electrónico .epub."""
    texto_md = ruta_md.read_text(encoding="utf-8")
    cuerpo_html = _markdown_a_html_body(texto_md)
    titulo = ruta_md.stem

    libro = epub.EpubBook()
    libro.set_identifier(f"md-convert-{titulo}")
    libro.set_title(titulo)
    libro.set_language("es")
    libro.add_author("Generado automáticamente")

    capitulo = epub.EpubHtml(title=titulo, file_name="contenido.xhtml", lang="es")
    capitulo.content = f"<h1>{titulo}</h1>{cuerpo_html}"
    libro.add_item(capitulo)

    estilo = epub.EpubItem(
        uid="estilo_base", file_name="estilo.css", media_type="text/css", content=css
    )
    libro.add_item(estilo)
    capitulo.add_item(estilo)

    libro.toc = (capitulo,)
    libro.add_item(epub.EpubNcx())
    libro.add_item(epub.EpubNav())
    libro.spine = ["nav", capitulo]

    ruta_salida.parent.mkdir(parents=True, exist_ok=True)
    epub.write_epub(str(ruta_salida), libro)
    print(f"✅ EPUB generado: '{ruta_salida}'")


# --------------------------------------------------------------------------- #
# Procesamiento de rutas (archivo o carpeta)
# --------------------------------------------------------------------------- #

def obtener_archivos_md(ruta_entrada: Path) -> List[Path]:
    """Devuelve la lista de archivos .md a procesar, dado un archivo o carpeta."""
    if not ruta_entrada.exists():
        raise FileNotFoundError(f"No se encontró la ruta de entrada: '{ruta_entrada}'")

    if ruta_entrada.is_file():
        if ruta_entrada.suffix.lower() != ".md":
            raise ValueError(f"El archivo '{ruta_entrada}' no tiene extensión .md")
        return [ruta_entrada]

    archivos = sorted(ruta_entrada.rglob("*.md"))
    if not archivos:
        raise ValueError(f"No se encontraron archivos .md en la carpeta '{ruta_entrada}'")
    return archivos


def procesar(ruta_entrada: str, ruta_salida_dir: str, formato: str, ruta_css: Optional[str]) -> None:
    """Procesa uno o varios archivos .md, convirtiéndolos al formato indicado."""
    entrada = Path(ruta_entrada)
    salida_dir = Path(ruta_salida_dir)
    css = _leer_css(ruta_css)

    archivos = obtener_archivos_md(entrada)
    extension_salida = "html" if formato == "html" else "epub"

    for archivo in archivos:
        ruta_salida = salida_dir / f"{archivo.stem}.{extension_salida}"
        try:
            if formato == "html":
                convertir_a_html(archivo, ruta_salida, css)
            else:
                convertir_a_epub(archivo, ruta_salida, css)
        except Exception as error:
            print(f"❌ Error al convertir '{archivo}': {error}", file=sys.stderr)


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #

def construir_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="md_convert.py",
        description="📖 Convierte archivos Markdown a HTML o EPUB con estilos personalizados.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("input", help="Archivo .md o carpeta con archivos .md")
    parser.add_argument(
        "-f", "--format", choices=["html", "epub"], default="html",
        help="Formato de salida"
    )
    parser.add_argument(
        "-o", "--output-dir", default="salida",
        help="Carpeta donde se guardarán los archivos generados"
    )
    parser.add_argument(
        "-s", "--css", default=None,
        help="Ruta a un archivo .css personalizado (opcional)"
    )
    return parser


def main() -> int:
    parser = construir_parser()
    args = parser.parse_args()

    try:
        procesar(args.input, args.output_dir, args.format, args.css)
    except FileNotFoundError as error:
        print(f"❌ Error: {error}", file=sys.stderr)
        return 1
    except ValueError as error:
        print(f"❌ Error de validación: {error}", file=sys.stderr)
        return 1
    except Exception as error:
        print(f"❌ Error inesperado: {error}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
