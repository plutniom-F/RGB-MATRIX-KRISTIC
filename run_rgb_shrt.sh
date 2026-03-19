#!/usr/bin/env bash
# minimal wrapper: startet das Spiel mit der venv-Python unter sudo
exec sudo "${HOME}/rgbmatrix-venv/bin/python" \
     "${HOME}/ITP2-Projekt-3AHIT-GRP4/ausfuerbaredatas/rgb_matrix_games_afterdevin.py" "$@"