import logging
import time
from typing import Any

from typing_extensions import TypedDict

from src.application.operacion_finanzas.correo_robot import CorreoOperacion
from src.application.operacion_finanzas.drive_robot import DriveOperacion


class RobotOperacionResult(TypedDict):
    drive: dict[str, Any]
    drive_secundario: dict[str, Any]
    correo: str


class RobotOperacion:
    def __init__(
        self,
    ) -> None:
        self.correo = CorreoOperacion()
        self.drive = DriveOperacion()

    async def execute(
        self,
        pdf_files: list[Any],
        correos: list[str],
    ) -> RobotOperacionResult:

        for file in pdf_files:
            
            result = self.correo.execute(correos=correos, pdf=[file])
        
        
        drive = self.drive.execute_primero(nombre_carpeta=f"Cartas de cesión - {int(time.time())}")
        drive_s = self.drive.execute_secundario(
                documentos=pdf_files, carpeta_hijo=str(drive.get("folder_id"))
            )
        return {
                "drive": drive,
                "drive_secundario": drive_s,
                "correo": "Envío exitoso" if result else "Error en el envío",
                }