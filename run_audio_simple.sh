#!/usr/bin/env bash
# Ein sehr einfaches Starter-Skript.
# Benutzt immer die feste venv-Python:
# /home/grp4/ITP2-Projekt-3AHIT-GRP4/audioo/.venv/bin/python
#
# Speichern als run_audio_simple.sh, ausführbar machen:
# chmod +x run_audio_simple.sh
# Aufruf:
# ./run_audio_simple.sh
#
set -euo pipefail

VENV_PY="/home/grp4/ITP2-Projekt-3AHIT-GRP4/audioo/.venv/bin/python"
BASE_DIR="/home/grp4/ITP2-Projekt-3AHIT-GRP4/audioo"

if [[ ! -x "$VENV_PY" ]]; then
  echo "ERROR: venv-Python nicht gefunden oder nicht ausführbar:"
  echo "  $VENV_PY"
  exit 1
fi

# Verwende immer audiomehrsensitiv.py (keine Auswahl mehr)
SCRIPT="$BASE_DIR/audiomehrsensitiv.py"

if [[ ! -f "$SCRIPT" ]]; then
  echo "Skript nicht gefunden: $SCRIPT"
  exit 1
fi

echo
echo "Sensitivity wählen:"
echo "  1) Weniger sensitiv (0.25)"
echo "  2) Normal (0.50)"
echo "  3) Mehr sensitiv (1.00)"
read -rp "Nummer (1-3): " SCHOICE
case "$SCHOICE" in
  1) SENS="0.25" ;;
  2) SENS="0.50" ;;
  3) SENS="1.00" ;;
  *) echo "Ungültig."; exit 1 ;;
esac

read -rp $'Edge-Effekt einschalten? (füllt Ränder bei lautem Signal) [y/N]: ' EDGE_ANS
EDGE_FLAG=""
if [[ "$EDGE_ANS" =~ ^([yY][eE]?[sS]?|[jJ]) ]]; then
  EDGE_FLAG="--edge"
fi

echo
read -rp $'Als root starten (sudo)? [Y/n]: ' ROOT_ANS

# Aufbau des Befehls als Array, EDGE_FLAG wird bei Bedarf angehängt
if [[ -z "$ROOT_ANS" || "$ROOT_ANS" =~ ^([yY][eE]?[sS]?|[jJ]) ]]; then
  RUN_CMD=( sudo "$VENV_PY" "$SCRIPT" --sensitivity "$SENS" )
else
  RUN_CMD=( "$VENV_PY" "$SCRIPT" --sensitivity "$SENS" )
fi

if [[ -n "$EDGE_FLAG" ]]; then
  RUN_CMD+=( "$EDGE_FLAG" )
fi

echo
echo "Starte: ${RUN_CMD[*]}"
exec "${RUN_CMD[@]}"