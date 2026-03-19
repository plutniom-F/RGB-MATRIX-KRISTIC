#!/usr/bin/env bash
# Minimal: use an existing venv, install bindings into it, test import, run game (with sudo)
set -e

VENV_DIR="${HOME}/rgbmatrix-venv"
REPO_DIR="${HOME}/rpi-rgb-led-matrix"
GAME_SCRIPT="${HOME}/ITP2-Projekt-3AHIT-GRP4/ausfuerbaredatas/rgb_matrix_games_afterdevin.py"

VENV_PY="${VENV_DIR}/bin/python"

[ -x "${VENV_PY}" ] || { echo "venv python not found: ${VENV_PY}"; exit 1; }
[ -d "${REPO_DIR}" ] || { echo "repo not found: ${REPO_DIR}"; exit 1; }

cd "${REPO_DIR}"
# install bindings into venv (no sudo)
"${VENV_PY}" -m pip install -e . 

# quick import test
"${VENV_PY}" - <<PY || { echo "import test failed"; exit 1; }
try:
    import rgbmatrix
    print("IMPORT_OK")
except Exception as e:
    print("IMPORT_ERR", e)
    raise
PY

[ -f "${GAME_SCRIPT}" ] || { echo "game script not found: ${GAME_SCRIPT}"; exit 1; }

# run with sudo but use venv python
sudo "${VENV_PY}" "${GAME_SCRIPT}"