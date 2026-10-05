# AETHER-QM: Quantum Meta Automation Engine

Version 26.0.0 | Python 3.10+ | MIT | Android + Linux | ARM64

Offline-first automation suite for constrained environments.

## Modules

    aether/
      __init__.py      Package init
      utils.py         Unicode safety, font detection
      pdf_engine.py    Unicode-safe PDF generation
      chat_ingest.py   ZIP to JSON to PDF
      portfolio.py     ATS-compliant portfolio builder
      backup.py        Folder mirror + ZIP snapshot
      cli.py           Command-line entry

## Install

    bash install.sh

## Usage

    bash run.sh portfolio --output ./out
    bash run.sh ingest --archive /path/to/archive.zip --output ./out
    bash run.sh backup --source ./out --destination ./backup

## Author

Dominik Mikszuta - dominik.mikszuta@outlook.com
