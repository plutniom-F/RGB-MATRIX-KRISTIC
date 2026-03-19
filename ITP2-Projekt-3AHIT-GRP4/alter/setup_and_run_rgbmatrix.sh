#!/usr/bin/env bash
#
# setup_and_run_rgbmatrix.sh
#
# Erstellt/benutzt ein Python venv, baut das rpi-rgb-led-matrix Projekt,
# installiert die Python‑Bindings ins venv, testet den Import und startet
# anschließend das angegebene Spielskript mit der venv‑Python unter sudo.
#
# Verwendung (als normaler Nutzer, NICHT root):
#   chmod +x setup_and_run_rgbmatrix.sh
#   ./setup_and_run_rgbmatrix.sh
#
set -euo pipefail

# --- KONFIGURIEREN (falls nötig) ---
USER_HOME="${HOME}"
REPO_DIR="${USER_HOME}/rpi-rgb-led-matrix"   # Pfad zum rgb-matrix-Repo
VENV_DIR="${USER_HOME}/rgbmatrix-venv"        # Speicherort des venv
GAME_SCRIPT="${USER_HOME}/ITP2-Projekt-3AHIT-GRP4/ausfuerbaredatas/rgb_matrix_games_afterdevin.py"
PYTHON_BIN="python3"
MAKE_JOBS=4
APT_PACKAGES="python3-dev cython3 cmake build-essential git"
# ------------------------------------

echo
echo "CONFIG:"
echo "  repo:   ${REPO_DIR}"
echo "  venv:   ${VENV_DIR}"
echo "  script: ${GAME_SCRIPT}"
echo

# 1) Prüfen ob Repo existiert
if [ ! -d "${REPO_DIR}" ]; then
  echo "ERROR: Repository nicht gefunden: ${REPO_DIR}"
  exit 1
fi

# 2) Systemabhängigkeiten (fragt nach Passwort)
echo
echo "Installiere System-Abhängigkeiten (kann Passwort verlangen)..."
sudo apt update
sudo apt install -y ${APT_PACKAGES}

# 3) Repo-Besitz sicherstellen (vermeidet root-owned Dateien)
echo
echo "Setze Besitz des Repos auf $(whoami)..."
sudo chown -R "$(whoami)":"$(whoami)" "${REPO_DIR}"

# 4) venv anlegen falls nötig
if [ ! -d "${VENV_DIR}" ]; then
  echo
  echo "Erstelle virtualenv in ${VENV_DIR}..."
  ${PYTHON_BIN} -m venv "${VENV_DIR}"
else
  echo
  echo "Verwende vorhandenes virtualenv: ${VENV_DIR}"
fi

VENV_PY="${VENV_DIR}/bin/python"
VENV_PIP="${VENV_DIR}/bin/pip"

# 5) pip & Build-Tools im venv aktualisieren
echo
echo "Aktualisiere pip/tools im venv..."
"${VENV_PIP}" install --upgrade pip setuptools wheel
"${VENV_PIP}" install --upgrade cython cmake

# 6) Native Teile bauen (make)
echo
echo "Baue native Bibliothek (make -j${MAKE_JOBS})..."
cd "${REPO_DIR}"
make -j${MAKE_JOBS} || { echo "make fehlgeschlagen. Abbruch."; exit 1; }

# 7) Python-Bindings in venv installieren (kein sudo)
echo
echo "Installiere Python‑Bindings ins venv (editable)..."
"${VENV_PY}" -m pip install -e . || {
  echo "Editable-Install fehlgeschlagen, versuche nicht-editable..."
  "${VENV_PY}" -m pip install . || { echo "pip install . fehlgeschlagen. Abbruch."; exit 1; }
}

# 8) Import testen
echo
echo "Teste Import im venv..."
IMPORT_TEST=$("${VENV_PY}" - <<'PYCODE' || true
import sys
try:
    import rgbmatrix
    print("IMPORT_OK", getattr(rgbmatrix, "__file__", repr(rgbmatrix)))
except Exception as e:
    print("IMPORT_ERR", type(e).__name__, e)
    sys.exit(2)
PYCODE
)

echo "${IMPORT_TEST}"
if echo "${IMPORT_TEST}" | grep -q "IMPORT_OK"; then
  echo "Import erfolgreich."
else
  echo "Import fehlgeschlagen. Prüfe die Ausgabe oben."
  exit 1
fi

# 9) Spiel starten (sudo + venv-Python)
if [ -f "${GAME_SCRIPT}" ]; then
  echo
  echo "Alles installiert. Starte Spiel mit sudo und venv-Python."
  echo "Falls du später ohne sudo starten willst: activate venv und dann 'python ${GAME_SCRIPT}'"
  echo
  read -p "Enter zum Starten (oder Strg-C zum Abbrechen)..."
  sudo "${VENV_PY}" "${GAME_SCRIPT}"
else
  echo
  echo "Installation abgeschlossen, aber Spielskript nicht gefunden: ${GAME_SCRIPT}"
  echo "Starte manuell z.B.: sudo ${VENV_PY} /pfad/zu/rgb_matrix_games_afterdevin.py"
fi

exit 0