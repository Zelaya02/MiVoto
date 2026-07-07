import smtplib
import socket
from email.message import EmailMessage
from flask import current_app

def enviar_email(destinatario, asunto, cuerpo_html):
    config = current_app.config
    servidor = config.get('MAIL_SERVER')
    puerto = config.get('MAIL_PORT')
    use_tls = config.get('MAIL_USE_TLS', True)
    usuario = config.get('MAIL_USERNAME')
    password = config.get('MAIL_PASSWORD')
    from_addr = config.get('MAIL_FROM', usuario)

    if not usuario or not password:
        current_app.logger.warning('MAIL_USERNAME/MAIL_PASSWORD no configurados — no se envio el correo')
        return False

    msg = EmailMessage()
    msg['Subject'] = asunto
    msg['From'] = from_addr
    msg['To'] = destinatario
    msg.set_content(cuerpo_html, subtype='html')

    try:
        with smtplib.SMTP(servidor, puerto, timeout=10) as smtp:
            smtp.starttls() if use_tls else None
            smtp.login(usuario, password)
            smtp.send_message(msg)
        return True
    except socket.timeout:
        current_app.logger.error(f'Timeout conectando a SMTP {servidor}:{puerto}')
        return False
    except smtplib.SMTPAuthenticationError:
        current_app.logger.error('Error de autenticacion SMTP — verifica MAIL_USERNAME/MAIL_PASSWORD')
        return False
    except Exception as e:
        current_app.logger.error(f'Error enviando email a {destinatario}: {e}')
        return False
