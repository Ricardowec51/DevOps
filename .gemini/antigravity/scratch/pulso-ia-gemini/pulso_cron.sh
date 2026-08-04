#!/bin/bash
# Wrapper para cron de PULSO a la IA.
# Uso:
#   pulso_cron.sh              → primer intento (sin notificación en fallo)
#   pulso_cron.sh --notify     → reintento (envía email si falla)
#   pulso_cron.sh --dry-run    → prueba sin generar docx ni enviar email

set -euo pipefail

BASE_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG="$BASE_DIR/logs/cron.log"
PYTHON="$BASE_DIR/.venv/bin/python3"

NOTIFY=0
DRY_RUN=0
for arg in "$@"; do
    case "$arg" in
        --notify)   NOTIFY=1 ;;
        --dry-run)  DRY_RUN=1 ;;
    esac
done

# Edición esperada: semana ISO de hace 7 días (misma lógica que el curator)
EDITION=$("$PYTHON" -c "import datetime; print((datetime.date.today() - datetime.timedelta(days=7)).isocalendar()[1])")
OUTPUT_FILE="$BASE_DIR/output/PULSO_a_la_IA_Edicion_${EDITION}.docx"
SENT_MARKER="$BASE_DIR/cache/edition_${EDITION}.sent"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] === pulso_cron.sh iniciado (edición esperada: ${EDITION}, dry-run: ${DRY_RUN}) ===" >> "$LOG"

# Si el email ya se envió (marcador escrito por send_email tras éxito real), no hacer nada
if [ "$DRY_RUN" -eq 0 ] && [ -f "$SENT_MARKER" ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Edición ${EDITION} ya enviada. Nada que hacer." >> "$LOG"
    exit 0
fi

cd "$BASE_DIR"

# Si el docx ya fue generado pero el email no se envió (p.ej. fallo SMTP previo),
# solo reintentar el envío en lugar de rehacer todo el pipeline.
if [ "$DRY_RUN" -eq 0 ] && [ -f "$OUTPUT_FILE" ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Docx de la edición ${EDITION} ya existe pero no se había enviado. Reintentando solo el envío..." >> "$LOG"
    set +e
    "$PYTHON" pulso_curator.py --send-only "$OUTPUT_FILE" "$EDITION" >> "$LOG" 2>&1
    EXIT_CODE=$?
    set -e

    if [ $EXIT_CODE -ne 0 ]; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] Reintento de envío falló con código ${EXIT_CODE}." >> "$LOG"
        if [ "$NOTIFY" -eq 1 ]; then
            echo "[$(date '+%Y-%m-%d %H:%M:%S')] Enviando email de alerta..." >> "$LOG"
            "$PYTHON" "$BASE_DIR/pulso_notify_fail.py" "$EDITION" >> "$LOG" 2>&1
        fi
        exit $EXIT_CODE
    fi
    exit 0
fi

# Ejecutar pipeline completo
CURATOR_ARGS=""
[ "$DRY_RUN" -eq 1 ] && CURATOR_ARGS="--dry-run"
set +e
"$PYTHON" pulso_curator.py $CURATOR_ARGS >> "$LOG" 2>&1
EXIT_CODE=$?
set -e

if [ $EXIT_CODE -ne 0 ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Pipeline falló con código ${EXIT_CODE}." >> "$LOG"
    if [ "$NOTIFY" -eq 1 ] && [ "$DRY_RUN" -eq 0 ]; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] Enviando email de alerta..." >> "$LOG"
        "$PYTHON" "$BASE_DIR/pulso_notify_fail.py" "$EDITION" >> "$LOG" 2>&1
    fi
    exit $EXIT_CODE
fi

exit 0
