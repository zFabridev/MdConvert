# 📖 MD Convert — Markdown a HTML/EPUB

CLI en Python que convierte tus notas en Markdown a documentos **HTML**
estilizados o **libros EPUB**, con soporte para CSS personalizado.

---

## ✨ Características

- 🌐 Convierte a **HTML** con estilos embebidos.
- 📚 Convierte a **EPUB** (ebook estándar) usando `ebooklib`.
- 🎨 Permite aplicar un archivo `.css` propio; si no se indica, usa un
  estilo por defecto limpio y legible.
- 📁 Procesa un **archivo individual** o **una carpeta completa** (recursivo).
- 🛡️ Manejo de errores para rutas inexistentes, extensiones incorrectas o
  carpetas sin archivos `.md`.

---

## 📦 Requisitos

- Python 3.8+
- `markdown>=3.5`
- `ebooklib>=0.18`

---

## 🚀 Instalación

```bash
cd p04-md-converter
python3 -m venv venv
source venv/bin/activate     # En Windows: venv\Scripts\activate
pip install -r requirements.txt
```

---

## 🖥️ Uso

### Convertir un archivo a HTML

```bash
python md_convert.py notas.md -f html -o salida
```

### Convertir un archivo a EPUB

```bash
python md_convert.py libro.md -f epub -o salida
```

### Convertir todos los .md de una carpeta

```bash
python md_convert.py ./mis_notas -f html -o salida
```

### Usar un CSS personalizado

```bash
python md_convert.py notas.md -f html -s estilos/mi_tema.css -o salida
```

### Ver ayuda

```bash
python md_convert.py --help
```

---

## 🗂️ Estructura

```
p04-md-converter/
├── md_convert.py
├── requirements.txt
└── README.md
```

## 📝 Licencia

MIT
