import json
from fastapi import APIRouter, File, UploadFile, Form, Depends

from src.application.operacion_finanzas.operacion_finanzas import RobotOperacion
from src.application.excel_extraction.extraction_usecase import ExtractionUseCase

from src.interfaces.dependencias.auth import require_roles
from src.domain.models import Rol

router = APIRouter(
    prefix="/finanzas",
    tags=["finanzas"],
    dependencies=[Depends(require_roles([Rol.ADMIN.value, Rol.FINANZAS.value]))],
)


@router.post("/extract")
async def extract_excel(
    excel: UploadFile = File(...),
    fecha_ingreso_desde: str = Form(...),
    usecase: ExtractionUseCase = Depends(),
):
    resultados = usecase.execute(excel.file, fecha_ingreso_desde)
    return {"data": resultados}


@router.post("/enviar-cartas")
async def enviar_cartas(
    pdfs: list[UploadFile] = File(...),
    datos_envio: str = Form(...),
    fecha_carpeta: str = Form(...),
    action: RobotOperacion = Depends(),
):
    config_envios = json.loads(datos_envio)

    resultado = await action.execute(
        pdf_files=pdfs, configuracion_envios=config_envios, fecha_carpeta=fecha_carpeta
    )
    return resultado
