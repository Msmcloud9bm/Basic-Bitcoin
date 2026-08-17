#!/usr/bin/env bash
set -euo pipefail

# docs/generate_runbook_pdf.sh
# Local helper: converts docs/runbook_mainnet.md to a printable PDF using pandoc (runs locally; requires pandoc+LaTeX)
# Usage: ./docs/generate_runbook_pdf.sh

if ! command -v pandoc >/dev/null 2>&1; then
  echo "pandoc not found. Install pandoc and a LaTeX engine (eg. texlive)."; exit 1
fi

INPUT=docs/runbook_mainnet.md
OUT=docs/runbook_mainnet.pdf

pandoc "$INPUT" -o "$OUT" --pdf-engine=xelatex --toc

echo "Produced $OUT (printable runbook)."
