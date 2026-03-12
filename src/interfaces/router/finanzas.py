# src/interfaces/router/finanzas.py
import os
from fastapi import APIRouter, File, UploadFile, Form, BackgroundTasks
from fastapi.responses import FileResponse

from src.application.operacion_finanzas.operacion_finanzas import RobotOperacion
from src.infrastructure.excel_extraction.extraction_excel import ExcelExtraction

router = APIRouter(prefix="/finanzas", tags=["finanzas"])

def cleanup_files(zip_path: str, output_dir: str = "output_cartas_cesion"):
    """Elimina el zip y los pdfs generados después de enviarlos para no saturar el servidor"""
    if os.path.exists(zip_path):
        os.remove(zip_path)
    if os.path.exists(output_dir):
        for file in os.listdir(output_dir):
            os.remove(os.path.join(output_dir, file))
        os.rmdir(output_dir)

@router.post("/extract")
async def extract_excel(
    background_tasks: BackgroundTasks,
    excel: UploadFile = File(...),
    fecha_ingreso_desde: str = Form(...),
):
    excel_extraction = ExcelExtraction()
    
    zip_path = excel_extraction.extract_data(excel.file, fecha_ingreso_desde)
    
    background_tasks.add_task(cleanup_files, zip_path)

    return FileResponse(
        path=zip_path, 
        filename="cartas_cesion.zip", 
        media_type="application/zip"
    )
    

@router.post("/enviar-cartas")
async def enviar_cartas(
    action: RobotOperacion = RobotOperacion(),
    pdfs: list[UploadFile] = File(...),
    correos_frontend: list[str] = Form(...),
):
    return action.execute(
        pdf_files=pdfs,
        correos=correos_frontend,)