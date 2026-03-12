import io
from typing import Any

from src.infrastructure.correos.send_gmail import GmailService


class InMemoryFile:
    """Clase auxiliar para imitar la estructura de un UploadFile de FastAPI en memoria"""

    def __init__(self, filename: str, content: bytes):
        self.filename = filename
        self.file = io.BytesIO(content)


class CorreoOperacion:

    def __init__(self) -> None:
        self.correo = GmailService()

    def execute(
        self,
        correos: list,
        pdf: list[Any],
    ) -> bool:
            return self.correo.enviar_email(
            pdfs=pdf,
            mails_verificacion=correos,
        )
