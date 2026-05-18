#!/usr/bin/env python3
"""Compile all .tex files under output/ into PDFs using pdflatex."""

import os
import subprocess
import sys
import glob
import shutil

ROOT = os.path.dirname(os.path.abspath(__file__))
OUTPUT_ROOT = os.path.join(ROOT, "output")
COMPILER = shutil.which("pdflatex") or shutil.which("xelatex") or shutil.which("lualatex")


def compile_tex(tex_path: str) -> bool:
    if not COMPILER:
        print("ERROR: No LaTeX compiler found.")
        print("  macOS:  brew install --cask mactex-no-gui")
        print("           (then run: eval \"$(/usr/libexec/path_helper)\")")
        print("  Ubuntu: sudo apt-get install texlive-full")
        print("  Windows: install MiKTeX from miktex.org")
        return False

    folder = os.path.dirname(tex_path)
    filename = os.path.basename(tex_path)
    rel = os.path.relpath(tex_path, ROOT)
    print(f"Compiling {rel} ...", end=" ", flush=True)

    cmd = [COMPILER, "-interaction=nonstopmode", "-output-directory", folder, filename]
    # Run twice to resolve cross-references
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=folder)
    subprocess.run(cmd, capture_output=True, text=True, cwd=folder)

    pdf_path = tex_path.replace(".tex", ".pdf")
    if os.path.exists(pdf_path):
        print("OK")
        for ext in [".aux", ".log", ".out", ".fls", ".fdb_latexmk"]:
            aux = tex_path.replace(".tex", ext)
            if os.path.exists(aux):
                os.remove(aux)
        return True
    else:
        print("FAILED")
        if result.stdout:
            print(result.stdout[-2000:])
        if result.stderr:
            print(result.stderr[-1000:])
        return False


def main():
    if not os.path.isdir(OUTPUT_ROOT):
        print("No output/ directory found. Ask the AI to generate your first CV.")
        sys.exit(1)

    tex_files = sorted(glob.glob(os.path.join(OUTPUT_ROOT, "**", "*.tex"), recursive=True))
    if not tex_files:
        print("No .tex files found under output/. Ask the AI to generate your CVs first.")
        sys.exit(1)

    results = []
    for tex in tex_files:
        ok = compile_tex(tex)
        results.append((tex, ok))

    print("\n--- Summary ---")
    all_ok = True
    for tex, ok in results:
        status = "OK  " if ok else "FAIL"
        print(f"  {status}  {os.path.relpath(tex, ROOT)}")
        if not ok:
            all_ok = False

    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
