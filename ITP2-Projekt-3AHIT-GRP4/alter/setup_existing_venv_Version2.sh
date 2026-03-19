#!/usr/bin/env bash
#
# setup_existing_venv.sh
#
# Verwende ein bereits existierendes virtualenv (keine Installation neuer Pakete).
# Führt in diesem venv `pip install -e .` im vorhandenen rpi-rgb-led-matrix Repo aus,
# testet den Import von `rgbmatrix` und startet anschließend das Spielskript mit
# dem venv-Python unter sudo (damit GPIO/Zugriff funktioniert).
#
# WICHTIG: Dieses Skript macht keine apt-/system‑Installationen und ändert keine
# Besitzrechte. Es erwartet, dass das Repo und das virtualenv bereits existieren.
#
# Verwendung:
#   1) Pfade oben ggf. anpassen
#   2) ausführbar machen: chmod +x setup_existing_venv.sh
#   3) ausführen als normaler Nutzer (NICHT sudo):
#        ./setup_existing_venv.sh
#
set -euo pipefail

# === Konfiguration (bei Bedarf anpassen) ===
VENV_DIR="${HOME}/rgbmatrix-venv"                             # vorhandenes venv
REPO_DIR="${HOME}/rpi-rgb-led-matrix"                         # vorhandenes repo (pyproject.toml)
GAME_SCRIPT="${HOME}/ITP2-Projekt-3AHIT-GRP4/ausfuerbaredatas/rgb_matrix_games_afterdevin.py"
# ==========================================

VENV_PY="${VENV_DIR}/bin/python"
VENV_PIP="${VENV_DIR}/bin/pip"

echo
echo "Benutze venv: ${VENV_DIR}"
echo "Repo:        ${REPO_DIR}"
echo "Game script: ${GAME_SCRIPT}"
echo

# Prüfen: venv existiert?
if [ ! -x "${VENV_PY}" ]; then
  echo "FEHLER: venv python nicht gefunden oder nicht ausführbar: ${VENV_PY}"
  echo "Bitte erstelle oder aktiviere das gewünschte venv manuell."
  exit 1
fi

# Prüfen: Repo existiert?
if [ ! -d "${REPO_DIR}" ]; then
  echo "FEHLER: Repo-Verzeichnis nicht gefunden: ${REPO_DIR}"
  exit 1
fi

# Wechsel ins Repo und installiere die Python‑Bindings INS venv (kein sudo!)
echo "Wechsle ins Repo: ${REPO_DIR}"
cd "${REPO_DIR}"

echo
echo "Installiere Python-Bindings in das vorhandene venv (keine System-Änderungen)..."
# Verwende explizit das venv-python, damit kein falsches pip benutzt wird.
# Editable-Install falls möglich; wenn das fehlschlägt, wird der Fehler ausgegeben.
"${VENV_PY}" -m pip install -e . || {
  echo
  echo "pip install -e . ist fehlgeschlagen. Ausgabe oben prüfen."
  echo "Wenn compile/build Fehler auftreten, zeige mir bitte die vollständige Fehlermeldung."
  exit 1
}

# Test: importieren
echo
echo "Teste Import: rgbmatrix"
IMPORT_TEST=$("${VENV_PY}" - <<'PY'
import sys
try:
    import rgbmatrix
    print("IMPORT_OK", getattr(rgbmatrix, "__file__", repr(rgbmatrix)))
except Exception as e:
    print("IMPORT_ERR", type(e).__name__, e)
    sys.exit(2)
PY
)

echo "${IMPORT_TEST}"
if ! echo "${IMPORT_TEST}" | grep -q "IMPORT_OK"; then
  echo
  echo "FEHLER: Import des Moduls 'rgbmatrix' ist fehlgeschlagen."
  echo "Bitte prüfe die pip-Install-Ausgabe oben oder sende mir die Fehlermeldung."
  exit 1
fi

# Spiel starten (mit sudo, aber venv-Python benutzen)
if [ ! -f "${GAME_SCRIPT}" ]; then
  echo
  echo "WARNUNG: Spielskript nicht gefunden: ${GAME_SCRIPT}"
  echo "Installation der Bindings ist abgeschlossen; starte dein Skript manuell:"
  echo "  sudo \"${VENV_PY}\" /voll/pfad/zu/rgb_matrix_games_afterdevin.py"
  exit 0
fi

echo
echo "Alles bereit. Das Spiel wird jetzt mit sudo und dem venv-Python gestartet."
echo "Wenn du das nicht möchtest, breche ab (STRG-C) und starte später manuell."
read -p "ENTER zum Starten oder STRG-C zum Abbrechen..."

# Starten (sudo, damit GPIO/Hardware funktioniert). Wir rufen direkt das venv-Python auf.
sudo "${VENV_PY}" "${GAME_SCRIPT}"