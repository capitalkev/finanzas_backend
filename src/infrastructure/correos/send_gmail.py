import base64
import logging
import os
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any

from fastapi import UploadFile
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import Resource, build  # type: ignore
from googleapiclient.errors import HttpError  # type: ignore

logger = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]

CORREOS_AGENTES = [
    "widad.naiza@capitalexpress.pe",
    "mariajose.astrain@capitalexpress.cl",
    "javiera.vera@capitalexpress.cl",
    "gianfranco.marcantonini@capitalexpress.cl",
    "kevin.tupac@unmsm.edu.pe"
]


class GmailService:
    def autenticar_gmail(self) -> Resource:
        token_path = os.path.join(os.path.dirname(__file__), "token.json")

        if not os.path.exists(token_path):
            raise FileNotFoundError(f"token.json not found at: {token_path}")

        creds: Credentials = Credentials.from_authorized_user_file(token_path, SCOPES)
        return build("gmail", "v1", credentials=creds)

    def enviar_email(
        self,
        pdfs: list[UploadFile],
        mails_verificacion: list[str],
    ) -> bool:
        try:
            service = self.autenticar_gmail()

            lista_destinatarios = CORREOS_AGENTES
            mensaje = MIMEMultipart()
            destinatarios = mails_verificacion if mails_verificacion is not None else []
            mensaje["to"] = ", ".join(destinatarios)
            cc_list = [*CORREOS_AGENTES]
            cc_final = list(set(cc_list))
            mensaje["cc"] = ", ".join(cc_final)
            mensaje["from"] = "me"
            mensaje["subject"] = "Confirmación de Facturas Negociables"
            cuerpo = self.create_html_body()
            mensaje.attach(MIMEText(cuerpo, "html"))

            if pdfs:
                for file in pdfs:
                    try:
                        file.file.seek(0)

                        contenido_pdf = file.file.read()

                        if not contenido_pdf:
                            logger.warning(f"Archivo vacío, omitiendo: {file.filename}")
                            continue
                        parte = MIMEBase("application", "octet-stream")
                        parte.set_payload(contenido_pdf)

                        encoders.encode_base64(parte)

                        filename_safe = file.filename
                        parte.add_header(
                            "Content-Disposition", "attachment", filename=filename_safe
                        )
                        mensaje.attach(parte)

                        logger.info(f"PDF adjuntado: {file.filename}")

                    except Exception:
                        logger.exception(
                            "Error al adjuntar %s",
                            getattr(file, "filename", "(sin nombre)"),
                        )

            resultado = self.enviar_mensaje_gmail(service, mensaje)
            if resultado:
                mensaje_id = resultado["id"]
                thread_id = resultado.get("threadId")
                logger.info(
                    f"Correo enviado a {len(lista_destinatarios)} destinatario(s). ID: {mensaje_id}"
                )
                logger.debug("Thread ID: %s", thread_id)
                return True
            logger.warning("No se pudo enviar el correo")
            return False

        except Exception:
            logger.exception("Error al enviar correo")
            return False

    def enviar_mensaje_gmail(
        self,
        service: Resource,
        message: MIMEMultipart,
        thread_id: str | None = None,
    ) -> dict[str, Any] | None:
        try:
            encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

            body: dict[str, Any] = {"raw": encoded_message}

            if thread_id:
                body["threadId"] = thread_id

            message_sent: dict[str, Any] = (
                service.users().messages().send(userId="me", body=body).execute()
            )

            return message_sent
        except HttpError:
            logger.warning(
                "Error Gmail API (HttpError) al enviar mensaje", exc_info=True
            )
            return None
        except Exception:
            logger.exception("Error inesperado enviando mensaje vía Gmail API")
            return None

    def create_html_body(self, data_frontend: dict, operation_id: str) -> str:
        """
        Crea el cuerpo HTML del correo procesando la estructura anidada de deudores y documentos.
        """

        # 4. Construir el mensaje final
        mensaje_html = """
        <!DOCTYPE html>
        <html lang="es">
        <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: Arial, Helvetica, sans-serif; font-size: 13px; color: #000; }}
            .container {{ max-width: 800px; }}
            p, li {{ line-height: 1.5; }}
            .disclaimer {{ font-style: italic; font-size: 11px; color: #555; margin-top: 25px; border-top: 1px solid #ccc; padding-top: 10px; }}
        </style>
        </head>
        <body>
        <div class="container">
        <p>Estimados,</p>
            <p>Gracias por confiar en Capital Express</p>
        </div>
        </body>
        </html>
        """
        return mensaje_html
