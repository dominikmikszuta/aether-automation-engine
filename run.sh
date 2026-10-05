#!/bin/bash
set -e
cd "$(dirname "$0")"
export PYTHONPATH="$(pwd):$PYTHONPATH"
python -m aether.cli "$@"
