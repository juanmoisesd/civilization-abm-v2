"""
build_pdf.py  —  Genera manuscript.pdf desde manuscript.md
Ejecutar desde civilization-abm-v2/:
    python paper/build_pdf.py

Requiere pandoc + una distribución LaTeX (MiKTeX o TeX Live).
  Instalar pandoc : https://pandoc.org/installing.html
  Instalar MiKTeX : https://miktex.org/download  (opción recomendada en Windows)

Si pandoc no está instalado, el script genera manuscript.tex que puedes
compilar manualmente con:  pdflatex paper/manuscript.tex
"""

import re
import subprocess
import sys
from pathlib import Path

PAPER_DIR = Path(__file__).parent
MD_PATH   = PAPER_DIR / "manuscript.md"
TEX_PATH  = PAPER_DIR / "manuscript.tex"
PDF_PATH  = PAPER_DIR / "manuscript.pdf"

# ─────────────────────────────────────────────────────────────────────────────
# 1. Intentar pandoc primero (más fácil)
# ─────────────────────────────────────────────────────────────────────────────

PANDOC_CMD = [
    "pandoc", str(MD_PATH),
    "--output", str(PDF_PATH),
    "--pdf-engine=xelatex",
    "--standalone",
    "--variable=geometry:margin=2.5cm",
    "--variable=fontsize:12pt",
    "--variable=linestretch:2",
    "--variable=mainfont:Times New Roman",
    "--variable=sansfont:Arial",
    "--variable=monofont:Courier New",
    "--variable=lang:en",
    "--variable=papersize:a4",
    "--variable=colorlinks:true",
    "--variable=linkcolor:black",
    "--variable=urlcolor:blue",
    "--highlight-style=tango",
    "--toc=false",
    # Filtrar cabecera de metadatos del draft
    "--metadata=title:Civilization-ABM v2 - Paper 2",
]


def try_pandoc() -> bool:
    try:
        r = subprocess.run(PANDOC_CMD, capture_output=True, text=True, timeout=120)
        if r.returncode == 0:
            print(f"[OK] PDF generado con pandoc → {PDF_PATH}")
            return True
        else:
            print("[!] pandoc falló:")
            print(r.stderr[:2000])
            return False
    except FileNotFoundError:
        print("[!] pandoc no encontrado.")
        return False
    except Exception as e:
        print(f"[!] Error pandoc: {e}")
        return False


# ─────────────────────────────────────────────────────────────────────────────
# 2. Fallback: generar .tex manualmente y compilar con pdflatex
# ─────────────────────────────────────────────────────────────────────────────

LATEX_HEADER = r"""\documentclass[12pt,a4paper]{article}

% Codificación y fuentes
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{times}
\usepackage{microtype}

% Matemáticas
\usepackage{amsmath,amssymb,amsthm}

% Tablas
\usepackage{booktabs,longtable,array,tabularx,multirow}

% Geometría y espaciado
\usepackage[margin=2.5cm, top=3cm, bottom=3cm]{geometry}
\usepackage{setspace}
\doublespacing
\setlength{\parindent}{0pt}
\setlength{\parskip}{8pt}

% Secciones sin numeración
\usepackage{titlesec}
\titleformat{\section}{\large\bfseries}{\thesection}{1em}{}
\titleformat{\subsection}{\normalsize\bfseries}{\thesubsection}{1em}{}
\titleformat{\subsubsection}{\normalsize\itshape}{\thesubsubsection}{1em}{}

% Hiperlinks
\usepackage[hidelinks, colorlinks=false]{hyperref}
\usepackage{url}
\urlstyle{same}

% Otros
\usepackage{graphicx}
\usepackage{xcolor}

% Datos del documento
\title{\textbf{Evolutionary Strategies, Spatial Resources, and\\
Institutional Collapse in an Agent-Based\\
Civilization Model: A World Bank--Calibrated\\
Simulation Study}}
\author{Juan Moisés de la Serna Tuya}
\date{}

\begin{document}
\maketitle
\thispagestyle{empty}
\newpage
"""

LATEX_FOOTER = r"""
\end{document}
"""


def escape_latex(s: str) -> str:
    """Escapa caracteres especiales de LaTeX en texto plano."""
    replacements = [
        ("\\", r"\textbackslash{}"),
        ("&",  r"\&"),
        ("%",  r"\%"),
        ("#",  r"\#"),
        ("_",  r"\_"),
        ("^",  r"\^{}"),
        ("{",  r"\{"),
        ("}",  r"\}"),
        ("~",  r"\textasciitilde{}"),
        ("<",  r"\textless{}"),
        (">",  r"\textgreater{}"),
        ("–",  "--"),
        ("—",  "---"),
        ("…",  r"\ldots{}"),
        ("\u00a0", "~"),       # non-breaking space
        ("≤",  r"$\leq$"),
        ("≥",  r"$\geq$"),
        ("≠",  r"$\neq$"),
        ("×",  r"$\times$"),
        ("→",  r"$\rightarrow$"),
        ("←",  r"$\leftarrow$"),
        ("±",  r"$\pm$"),
        ("∞",  r"$\infty$"),
    ]
    for src, dst in replacements:
        s = s.replace(src, dst)
    return s


def inline_format(s: str) -> str:
    """Convierte formato inline markdown a LaTeX."""
    # Preservar math inline $...$ antes de escapar
    # Extraer fragmentos de math inline temporalmente
    math_chunks: list[str] = []

    def save_math(m):
        math_chunks.append(m.group(0))
        return f"MATHPLACEHOLDER{len(math_chunks)-1}ENDMATH"

    s = re.sub(r"\$[^$\n]+\$", save_math, s)

    # Escapar texto plano
    s = escape_latex(s)

    # Restaurar math inline
    for i, chunk in enumerate(math_chunks):
        s = s.replace(f"MATHPLACEHOLDER{i}ENDMATH", chunk)

    # Bold **text** o __text__
    s = re.sub(r"\*\*(.+?)\*\*", r"\\textbf{\1}", s)
    s = re.sub(r"__(.+?)__",     r"\\textbf{\1}", s)

    # Italic *text* o _text_ (single)
    s = re.sub(r"\*([^*\n]+?)\*", r"\\textit{\1}", s)
    s = re.sub(r"_([^_\n]+?)_",   r"\\textit{\1}", s)

    # Inline code `text`
    s = re.sub(r"`([^`]+)`", lambda m: r"\texttt{" + m.group(1).replace("_", r"\_") + "}", s)

    # Links [text](url)
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)",
               lambda m: r"\href{" + m.group(2) + "}{" + m.group(1) + "}", s)

    # URLs sueltas https://...
    s = re.sub(r"(?<![{(])https?://\S+",
               lambda m: r"\url{" + m.group(0) + "}", s)

    return s


def parse_table(lines: list[str]) -> str:
    """Convierte tabla markdown a tabular LaTeX."""
    rows = []
    for line in lines:
        if line.startswith("|"):
            cells = [c.strip() for c in line.strip("|").split("|")]
            rows.append(cells)

    if not rows:
        return ""

    # Filtrar fila separadora (---|---)
    data_rows = [r for r in rows if not all(re.match(r"^[-: ]+$", c) for c in r)]
    if not data_rows:
        return ""

    ncols = max(len(r) for r in data_rows)
    col_spec = "|" + "|".join(["l"] * ncols) + "|"

    out = ["\\begin{center}",
           f"\\begin{{tabular}}{{{col_spec}}}",
           "\\hline"]

    for i, row in enumerate(data_rows):
        # Pad
        while len(row) < ncols:
            row.append("")
        cells = " & ".join(inline_format(c) for c in row)
        out.append(cells + " \\\\")
        out.append("\\hline")

    out += ["\\end{tabular}", "\\end{center}", ""]
    return "\n".join(out)


def md_to_latex(md_text: str) -> str:
    """Convierte el markdown completo a cuerpo LaTeX."""
    lines = md_text.split("\n")
    out: list[str] = []

    i = 0
    in_list = False
    abstract_mode = False

    # Saltar cabecera de metadatos del draft (líneas 1-8)
    skip_meta = True

    while i < len(lines):
        line = lines[i]

        # ── Saltar metadatos del draft ──────────────────────────────────────
        if skip_meta:
            if line.startswith("**Target journal:**") or \
               line.startswith("**Format:**") or \
               line.startswith("**Submission") or \
               line.startswith("**Peer review:**") or \
               line.startswith("**Status:**") or \
               line.startswith("**Funding:**") or \
               line.startswith("*(8 keywords"):
                i += 1
                continue
            if line.strip() == "---" and i < 15:
                i += 1
                continue

        # ── Regla horizontal ────────────────────────────────────────────────
        if re.match(r"^---+\s*$", line):
            if in_list:
                out.append("\\end{itemize}")
                in_list = False
            out.append("\\vspace{4pt}\\noindent\\rule{\\textwidth}{0.4pt}\\vspace{4pt}")
            i += 1
            continue

        # ── Bloque de math display $$...$$  (puede ocupar varias líneas) ───
        if line.strip().startswith("$$"):
            if in_list:
                out.append("\\end{itemize}")
                in_list = False
            math_lines = [line.strip().lstrip("$")]
            i += 1
            while i < len(lines) and "$$" not in lines[i]:
                math_lines.append(lines[i])
                i += 1
            if i < len(lines):
                math_lines.append(lines[i].strip().rstrip("$"))
            i += 1
            math_body = "\n".join(l for l in math_lines if l.strip())
            out.append("\\begin{equation*}")
            out.append(math_body)
            out.append("\\end{equation*}")
            out.append("")
            continue

        # ── Tabla ────────────────────────────────────────────────────────────
        if line.startswith("|"):
            if in_list:
                out.append("\\end{itemize}")
                in_list = False
            table_lines = []
            while i < len(lines) and lines[i].startswith("|"):
                table_lines.append(lines[i])
                i += 1
            out.append(parse_table(table_lines))
            continue

        # ── Headings ─────────────────────────────────────────────────────────
        if line.startswith("# ") and not line.startswith("## "):
            if in_list:
                out.append("\\end{itemize}")
                in_list = False
            title = inline_format(line[2:].strip())
            # Primera heading es el título → ya en \maketitle, omitir
            if "Evolutionary Strategies" in line or "Civilization" in line:
                i += 1
                continue
            out.append(f"\n\\section*{{{title}}}")
            i += 1
            continue

        if line.startswith("## "):
            if in_list:
                out.append("\\end{itemize}")
                in_list = False
            title = inline_format(line[3:].strip())
            # Abstract: entorno especial
            if "Abstract" in title:
                out.append("\n\\begin{abstract}")
                abstract_mode = True
            else:
                if abstract_mode:
                    out.append("\\end{abstract}\n")
                    abstract_mode = False
                out.append(f"\n\\subsection*{{{title}}}")
            i += 1
            continue

        if line.startswith("### "):
            if in_list:
                out.append("\\end{itemize}")
                in_list = False
            title = inline_format(line[4:].strip())
            out.append(f"\n\\subsubsection*{{{title}}}")
            i += 1
            continue

        # ── Listas ───────────────────────────────────────────────────────────
        if re.match(r"^- ", line) or re.match(r"^\* ", line):
            if not in_list:
                out.append("\\begin{itemize}")
                in_list = True
            item = inline_format(line[2:].strip())
            out.append(f"  \\item {item}")
            i += 1
            continue
        else:
            if in_list and line.strip() == "":
                # Puede haber continuación
                if i + 1 < len(lines) and (lines[i+1].startswith("- ") or lines[i+1].startswith("* ")):
                    i += 1
                    continue
                else:
                    out.append("\\end{itemize}")
                    in_list = False

        # ── Párrafo vacío ────────────────────────────────────────────────────
        if line.strip() == "":
            if abstract_mode:
                out.append("")
            else:
                out.append("\n")
            i += 1
            continue

        # ── Keywords line ────────────────────────────────────────────────────
        if line.startswith("**Keywords:**"):
            kw = inline_format(line)
            out.append(f"\n\\noindent {kw}\n")
            i += 1
            continue

        # ── Texto normal ─────────────────────────────────────────────────────
        out.append(inline_format(line))
        i += 1

    if in_list:
        out.append("\\end{itemize}")
    if abstract_mode:
        out.append("\\end{abstract}")

    return "\n".join(out)


def build_latex_fallback() -> bool:
    """Genera .tex y compila con pdflatex."""
    print("[*] Generando archivo LaTeX...")
    md_text = MD_PATH.read_text(encoding="utf-8")
    body = md_to_latex(md_text)
    tex = LATEX_HEADER + body + LATEX_FOOTER
    TEX_PATH.write_text(tex, encoding="utf-8")
    print(f"[OK] LaTeX generado → {TEX_PATH}")

    # Intentar compilar
    for engine in ["pdflatex", "xelatex"]:
        try:
            print(f"[*] Compilando con {engine}...")
            r = subprocess.run(
                [engine, "-interaction=nonstopmode",
                 f"-output-directory={PAPER_DIR}", str(TEX_PATH)],
                capture_output=True, text=True, timeout=120
            )
            if r.returncode == 0:
                print(f"[OK] PDF generado con {engine} → {PDF_PATH}")
                # Segunda pasada para referencias cruzadas
                subprocess.run(
                    [engine, "-interaction=nonstopmode",
                     f"-output-directory={PAPER_DIR}", str(TEX_PATH)],
                    capture_output=True, timeout=120
                )
                return True
            else:
                print(f"[!] {engine} error (código {r.returncode})")
                # Mostrar últimas líneas del log
                log = r.stdout[-1500:] if r.stdout else r.stderr[-1500:]
                print(log)
        except FileNotFoundError:
            print(f"[!] {engine} no encontrado.")
        except Exception as e:
            print(f"[!] Error {engine}: {e}")

    print("\n[!] No se pudo compilar automáticamente.")
    print(f"    El archivo LaTeX está en: {TEX_PATH}")
    print("    Para compilar manualmente en PowerShell:")
    print(f"      pdflatex -output-directory paper paper\\manuscript.tex")
    print("\n    Si no tienes LaTeX instalado, instala MiKTeX:")
    print("      https://miktex.org/download")
    return False


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=== build_pdf.py — Civilization-ABM v2 ===\n")

    if not MD_PATH.exists():
        print(f"ERROR: no encontrado {MD_PATH}")
        sys.exit(1)

    success = try_pandoc()
    if not success:
        success = build_latex_fallback()

    if success:
        print(f"\nPDF listo: {PDF_PATH.resolve()}")
    else:
        print(f"\nTeX listo para compilar: {TEX_PATH.resolve()}")
        sys.exit(1)
