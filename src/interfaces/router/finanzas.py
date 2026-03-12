from fastapi import APIRouter, Depends, File, UploadFile

from src.application import excel_extraction
from src.application.excel_extraction.extraction_excel import ExcelExtraction


router = APIRouter(prefix="/finanzas", tags=["finanzas"])

@router.post("/extract")
async def extract_excel(
    excel: UploadFile = File(...),
    fecha_ingreso_desde: str,
    excel_extraction = ExcelExtraction()
    ):
    
    excel_extraction.extract_data(excel.file, fecha_ingreso_desde)