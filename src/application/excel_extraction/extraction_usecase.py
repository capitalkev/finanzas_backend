from src.infrastructure.excel_extraction.extraction_excel import ExcelExtractionService

class ExtractionUseCase:
    def __init__(self):
        self.excel_service = ExcelExtractionService()

    def execute(self, file_stream, fecha_ingreso_desde_str: str) -> list[dict]:
        # Aquí puedes agregar validaciones de negocio si fuera necesario
        return self.excel_service.extract_and_convert_to_base64(
            file_stream, 
            fecha_ingreso_desde_str
        )