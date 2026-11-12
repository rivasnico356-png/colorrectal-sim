"""IE-05: envío de correos por SMTP seguro (STARTTLS). Sin servidor configurado, el mensaje se guarda en
memoria para desarrollo y pruebas y no sale de la máquina."""
import smtplib
import ssl
from email.message import EmailMessage

from app.core.config import get_settings

buzon_desarrollo: list[EmailMessage] = []


def enviar_correo(destino: str, asunto: str, cuerpo: str) -> None:
    s = get_settings()
    msg = EmailMessage()
    msg["From"], msg["To"], msg["Subject"] = s.smtp_remitente, destino, asunto
    msg.set_content(cuerpo)
    if not s.smtp_servidor:
        buzon_desarrollo.append(msg)
        return
    with smtplib.SMTP(s.smtp_servidor, s.smtp_puerto, timeout=10) as smtp:
        smtp.starttls(context=ssl.create_default_context())
        if s.smtp_usuario:
            smtp.login(s.smtp_usuario, s.smtp_contrasena)
        smtp.send_message(msg)
