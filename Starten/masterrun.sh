#!/usr/bin/env bash
# Auswahl-Wrapper: starte entweder das Audio-Wrapper-Skript oder das RGB-Wrapper-Skript.
# Nach Beenden eines Skripts wirst du gefragt, ob das andere Skript gestartet werden soll
# oder ob du beenden willst.
#
# Pfade anpassen, falls deine Skripte woanders liegen.
AUDIO="/home/grp4/ITP2-Projekt-3AHIT-GRP4/audioo/run_audio_simple.sh"
RGB="/home/grp4/ITP2-Projekt-3AHIT-GRP4/run_rgb_shrt.sh"

set -euo pipefail

run_script() {
  local path="$1"
  if [[ ! -e "$path" ]]; then
    echo "FEHLER: Skript nicht gefunden: $path"
    return 2
  fi

  echo
  echo "Starte: $path"
  # Wenn ausführbar, direkt starten; sonst mit bash ausführen (so kehrt der Wrapper nach Ende zurück)
  if [[ -x "$path" ]]; then
    "$path"
  else
    bash "$path"
  fi
  local rc=$?
  echo "Skript beendet (Exit-Code: $rc)"
  return $rc
}

prompt_yesno() {
  # prompt_yesno "Frage..." default_yes?
  local prompt="$1"; shift
  local default_yes=${1:-false}
  local ans
  if $default_yes; then
    read -rp "$prompt [Y/n]: " ans
    [[ -z "$ans" || "$ans" =~ ^([yY][eE]?[sS]?|[jJ]) ]]
  else
    read -rp "$prompt [y/N]: " ans
    [[ "$ans" =~ ^([yY][eE]?[sS]?|[jJ]) ]]
  fi
}

main_menu() {
  while true; do
    echo
    echo "Was möchtest du starten?"
    echo "  1) Audio (run_audio_simple.sh)"
    echo "  2) RGB   (run_rgb_shrt.sh)"
    echo "  3) Beenden"
    read -rp "Nummer (1-3): " CHOICE
    case "$CHOICE" in
      1)
        run_script "$AUDIO"
        # nach Beenden: Frage, ob das andere Skript (RGB) gestartet werden soll
        if prompt_yesno "Möchtest du jetzt das andere Skript (RGB) starten?"; then
          run_script "$RGB"
        fi
        # Nach dem optionalen Start des anderen Skripts zurück zum Menü oder beenden
        if prompt_yesno "Zurück zum Menü?"; then
          continue
        else
          echo "Beende."
          exit 0
        fi
        ;;
      2)
        run_script "$RGB"
        # nach Beenden: Frage, ob das andere Skript (Audio) gestartet werden soll
        if prompt_yesno "Möchtest du jetzt das andere Skript (Audio) starten?"; then
          run_script "$AUDIO"
        fi
        if prompt_yesno "Zurück zum Menü?"; then
          continue
        else
          echo "Beende."
          exit 0
        fi
        ;;
      3)
        echo "Beende."
        exit 0
        ;;
      *)
        echo "Ungültige Auswahl."
        ;;
    esac
  done
}

# Prüfe auf Existenz (nur Warnung; run_script prüft vor Ausführung nochmal)
if [[ ! -e "$AUDIO" ]]; then
  echo "WARNUNG: Audio-Skript nicht gefunden: $AUDIO"
fi
if [[ ! -e "$RGB" ]]; then
  echo "WARNUNG: RGB-Skript nicht gefunden: $RGB"
fi

main_menu