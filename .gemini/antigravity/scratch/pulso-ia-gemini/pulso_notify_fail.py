#!/usr/bin/env python3
"""Envía email de alerta cuando el pipeline de PULSO falla en el reintento."""
import smtplib
import sys
from email.mime.text import MIMEText
from pathlib import Path
import yaml
import datetime

BASE_DIR = Path(__file__).parent
cfg = yaml.safe_load((BASE_DIR / "config.yaml").read_text())
ec = cfg["email"]

edition = sys.argv[1] if len(sys.argv) > 1 else "desconocida"
motivo = sys.argv[2] if len(sys.argv) > 2 else ""
today = datetime.date.today().strftime("%d/%m/%Y")

if motivo == "codex-no-session":
    subject = f"⚠️ PULSO a la IA — Edición {edition}: Codex sin sesión ({today})"
    body = f"""Hola Ricardo,

El pipeline de PULSO a la IA NO pudo generar la Edición {edition} hoy ({today})
porque Codex CLI no tiene una sesión activa ("codex login status" falló). El
curador usa "codex exec", así que sin sesión no puede clasificar las noticias.

Para arreglarlo, en la Mac:
  codex login

Luego puedes generar la edición manualmente:
  cd {BASE_DIR}
  ./.venv/bin/python3 pulso_curator.py

Log: {BASE_DIR}/logs/cron.log

— Sistema automatizado PULSO a la IA
"""
else:
    subject = f"⚠️ PULSO a la IA — Edición {edition} NO enviada ({today})"
    body = f"""Hola Ricardo,

El pipeline de PULSO a la IA intentó generar la Edición {edition} dos veces hoy ({today}) y ambas fallaron.

Primera ejecución: 08:00 AM (cron semanal)
Segunda ejecución: 09:00 AM (reintento automático)
{f'Motivo reportado: {motivo}' if motivo else ''}
Revisa el log en:
  {BASE_DIR}/logs/cron.log

Puedes ejecutar manualmente:
  cd {BASE_DIR}
  ./.venv/bin/python3 pulso_curator.py

— Sistema automatizado PULSO a la IA
"""

msg = MIMEText(body)
msg["Subject"] = subject
msg["From"] = ec["from"]
msg["To"] = ec["to"]

with smtplib.SMTP_SSL(ec["smtp_host"], ec["smtp_port"]) as server:
    server.login(ec["smtp_user"], ec["smtp_password"].replace(" ", ""))
    server.sendmail(ec["from"], [ec["to"]], msg.as_string())

print(f"Email de alerta enviado para edición {edition}.")
