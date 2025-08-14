import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from constants import SMTP_SERVER, SMTP_PORT, SMTP_USER, SMTP_PASS

def enviar_correo(destinatario, asunto, mensaje):
    msg = MIMEMultipart()
    msg["From"] = SMTP_USER
    msg["To"] = destinatario
    msg["Subject"] = asunto
    msg.attach(MIMEText(mensaje, "plain"))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
        return True
    except Exception as e:
        print("Error al enviar correo:", e)
        return False