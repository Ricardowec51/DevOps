#!/usr/bin/env python3
"""Envío manual de una edición de PULSO a la IA como ADJUNTO por email.

Uso:
    python3 enviar_edicion_manual.py <NUM_EDICION> [ruta_docx]

Lee la config SMTP de config.yaml (email.*). Pensado para reenviar a mano una
edición que el pipeline generó pero no mandó con adjunto.
"""
import sys, ssl, smtplib, yaml
from pathlib import Path
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

BASE = Path(__file__).resolve().parent


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    edition = sys.argv[1]
    docx = Path(sys.argv[2]) if len(sys.argv) > 2 else BASE / "output" / f"PULSO_a_la_IA_Edicion_{edition}.docx"
    if not docx.exists():
        print(f"No existe el .docx: {docx}")
        sys.exit(1)

    ec = yaml.safe_load(open(BASE / "config.yaml"))["email"]
    today = datetime.now().strftime("%d/%m/%Y")

    msg = MIMEMultipart()
    msg["From"] = ec["from"]
    msg["To"] = ec["to"]
    msg["Subject"] = f"PULSO a la IA — Edición {edition} | {today}"
    body = (
        f"Estimado/a,\n\n"
        f"Adjunto encontrará la Edición {edition} de PULSO a la IA, su resumen semanal "
        f"de tendencias en Inteligencia Artificial para el sector ejecutivo.\n\n"
        f"—\nRicardo Wagner-Areco\nEMPRENDEDORES.LTD | emprendedores.ec\n"
    )
    msg.attach(MIMEText(body, "plain", "utf-8"))

    with open(docx, "rb") as f:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(f.read())
    encoders.encode_base64(part)
    part.add_header("Content-Disposition", f'attachment; filename="{docx.name}"')
    msg.attach(part)

    port = int(ec.get("smtp_port", 465))
    passwd = ec["smtp_password"].replace(" ", "")
    if port == 465:
        server = smtplib.SMTP_SSL(ec["smtp_host"], port, context=ssl.create_default_context())
    else:
        server = smtplib.SMTP(ec["smtp_host"], port)
        server.starttls(context=ssl.create_default_context())
    with server:
        server.login(ec.get("smtp_user", ec["from"]), passwd)
        server.sendmail(ec["from"], [ec["to"]], msg.as_string())
    print(f"Enviado: Edición {edition} → {ec['to']}  ({docx.name}, {docx.stat().st_size//1024} KB)")


if __name__ == "__main__":
    main()
