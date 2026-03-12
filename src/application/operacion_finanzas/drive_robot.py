from typing import Any

from src.infrastructure.drive.drive import DriveService


class DriveOperacion:
    def __init__(self) -> None:
        self.drive = DriveService()

    def execute_primero(
        self,
        nombre_carpeta: str,
    ) -> dict[str, Any]:
        service = self.drive.get_drive_service()
        id_folder = self.drive.create_subfolder(
            service, nombre_carpeta, "1I6RgXVmcw8c9UF4dkSShjsFwpi2pPkG1"
        )
        return {
            "success": True,
            "folder_id": id_folder,
        }

    def execute_secundario(
        self,
        documentos: list[Any],
        carpeta_hijo: str,
    ) -> dict[str, Any]:
        service = self.drive.get_drive_service()
        return self.drive.upload_to_folder(service, documentos, carpeta_hijo)
