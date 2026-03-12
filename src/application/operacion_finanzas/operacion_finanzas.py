import logging
from typing import Any
from typing_extensions import TypedDict
from fastapi import UploadFile

from src.application.operacion_finanzas.correo_robot import CorreoOperacion
from src.application.operacion_finanzas.drive_robot import DriveOperacion

class RobotOperacionResult(TypedDict):
    drive: dict[str, Any]
    drive_secundario: dict[str, Any]
    correo: str

class RobotOperacion:
    def __init__(self) -> None:
        self.correo = CorreoOperacion()
        self.drive = DriveOperacion()

    async def execute(
        self,
        pdf_files: list[UploadFile],
        configuracion_envios: list[dict],
        fecha_carpeta: str
    ) -> RobotOperacionResult:

        # 1. Creamos un diccionario para buscar rápido los PDFs por su nombre
        files_by_name = {f.filename: f for f in pdf_files}
        envios_exitosos = True

        # 2. Iteramos sobre la configuración que mandó el frontend
        for config in configuracion_envios:
            filename = config.get("filename")
            correos = config.get("correos", [])
            
            file_obj = files_by_name.get(filename)

            # Si el archivo existe y tiene correos asignados, lo enviamos de forma aislada
            if file_obj and correos:
                result = self.correo.execute(correos=correos, pdf=[file_obj])
                if not result:
                    envios_exitosos = False

        # 3. Crear carpeta en Drive con el nombre de la fecha y subir los PDFs
        nombre_final_carpeta = f"Cartas de cesión - {fecha_carpeta}"
        drive = self.drive.execute_primero(nombre_carpeta=nombre_final_carpeta)
        
        drive_s = self.drive.execute_secundario(
            documentos=pdf_files, 
            carpeta_hijo=str(drive.get("folder_id"))
        )

        return {
            "drive": drive,
            "drive_secundario": drive_s,
            "correo": "Envío completado" if envios_exitosos else "Hubo errores en algunos correos",
        }