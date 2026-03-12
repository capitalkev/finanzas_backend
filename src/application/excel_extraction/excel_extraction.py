from src.infrastructure.excel_extraction.extraction_excel import ExcelExtraction

class ExtractionUseCase:
    def __init__(self):
        self.excel_service = ExcelExtraction()

    def execute(self, file_stream, fecha_ingreso_desde_str: str) -> list[dict]:
        return self.excel_service.extract_and_convert_to_base64(
            file_stream, 
            fecha_ingreso_desde_str
        )