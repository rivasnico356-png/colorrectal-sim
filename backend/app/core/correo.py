"""IE-05: envío de correos.

Orden de uso:
1. API de Brevo por HTTPS (BREVO_API_KEY): el plan gratuito de Render bloquea los puertos SMTP (25, 465 y 587) desde
   septiembre de 2025, así que en el enlace público el correo sale por HTTPS.
2. SMTP seguro con STARTTLS (SMTP_SERVIDOR), para instalaciones propias.
3. Sin ninguno configurado, el mensaje se guarda en memoria para desarrollo y pruebas y no sale de la máquina.
"""
import logging
import smtplib
import ssl
from email.message import EmailMessage

import httpx

from app.core.config import get_settings

buzon_desarrollo: list[EmailMessage] = []
registro = logging.getLogger("colorrectal.correo")
URL_BREVO = "https://api.brevo.com/v3/smtp/email"


class ErrorCorreo(Exception):
    """El proveedor rechazó o no recibió el correo."""


def _por_brevo(clave: str, remitente: str, destino: str, asunto: str, cuerpo: str, cliente: httpx.Client | None = None) -> None:
    cuerpo_json = {"sender": {"name": "Colorrectal-Sim", "email": remitente}, "to": [{"email": destino}],
                   "subject": asunto, "textContent": cuerpo}
    c = cliente or httpx.Client(timeout=10)
    try:
        r = c.post(URL_BREVO, headers={"api-key": clave.strip(), "accept": "application/json"}, json=cuerpo_json)
    except httpx.HTTPError as exc:
        raise ErrorCorreo(f"Brevo no respondió: {exc}") from exc
    finally:
        if cliente is None:
            c.close()
    if r.status_code >= 400:
        # El mensaje del proveedor explica el rechazo (clave inválida, remitente sin verificar, límite diario).
        raise ErrorCorreo(f"Brevo HTTP {r.status_code}: {r.text[:300]}")


def enviar_correo(destino: str, asunto: str, cuerpo: str, cliente: httpx.Client | None = None) -> None:
    s = get_settings()
    if s.brevo_api_key:
        _por_brevo(s.brevo_api_key, s.smtp_remitente, destino, asunto, cuerpo, cliente)
        return
    msg = EmailMessage()
    msg["From"], msg["To"], msg["Subject"] = s.smtp_remitente, destino, asunto
    msg.set_content(cuerpo)
    if not s.smtp_servidor:
        buzon_desarrollo.append(msg)
        registro.warning("Correo no enviado: no hay BREVO_API_KEY ni SMTP_SERVIDOR configurados (asunto: %s).", asunto)
        return
    with smtplib.SMTP(s.smtp_servidor, s.smtp_puerto, timeout=10) as smtp:
        smtp.starttls(context=ssl.create_default_context())
        if s.smtp_usuario:
            smtp.login(s.smtp_usuario, s.smtp_contrasena)
        smtp.send_message(msg)
