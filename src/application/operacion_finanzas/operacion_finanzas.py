from typing import Any
from typing_extensions import TypedDict

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
        pdf_files: list[Any],
        configuracion_envios: list[dict],
        nombre_carpeta: str
    ) -> RobotOperacionResult:

        files_by_name = {f.filename: f for f in pdf_files}
        envios_exitosos = True

        # 1. Enviar correos respetando la configuración del frontend
        for config in configuracion_envios:
            filename = config.get("filename")
            correos = config.get("correos", [])
            
            file_obj = files_by_name.get(filename)

            if file_obj and correos:
                # Se envía solo el PDF correspondiente a sus correos asignados
                result = self.correo.execute(correos=correos, pdf=[file_obj])
                if not result:
                    envios_exitosos = False

        # 2. Subir todos a Drive bajo la carpeta de la fecha
        drive = self.drive.execute_primero(nombre_carpeta=nombre_carpeta)
        drive_s = self.drive.execute_secundario(
            documentos=pdf_files, carpeta_hijo=str(drive.get("folder_id"))
        )

        return {
            "drive": drive,
            "drive_secundario": drive_s,
            "correo": "Proceso completado" if envios_exitosos else "Con errores",
        }