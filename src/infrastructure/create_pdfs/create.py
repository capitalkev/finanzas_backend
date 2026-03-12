import pandas as pd
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from src.infrastructure.formato.formato import (
    format_date_es,
    format_amount_es,
    normalize_currency,
)

CIUDAD = "San Isidro"
ALIADO_ESTRATEGICO = "PUERTO X PERU S.A.C."
FIRMA_NOMBRE = "Widad Naiza"
FIRMA_CARGO = "Ejecutiva de Cobranza"

CUENTAS_BCP = [
    ["Cuenta Corriente Soles BCP", "191-9283320-0-07"],
    ["Código Interbancario Soles BCP", "002 191 009283320007 51"],
    ["Cuenta Corriente Dólares BCP", "191-7394480-1-25"],
    ["Código Interbancario Dólares BCP", "002 191 007394480125 54"],
]

def build_carta_pdf(deudor: str, rows: pd.DataFrame, out_path: str):
    styles = getSampleStyleSheet()
    normal = styles["Normal"]
    normal.leading = 14

    title_style = ParagraphStyle(
        "title",
        parent=styles["Normal"],
        fontSize=11,
        leading=14,
        spaceAfter=6,
    )

    doc = SimpleDocTemplate(
        out_path,
        pagesize=A4,
        leftMargin=25 * mm,
        rightMargin=25 * mm,
        topMargin=20 * mm,
        bottomMargin=18 * mm,
    )

    story = []

    # Fecha (simple)
    hoy = datetime.now()
    fecha_es = hoy.strftime("%d de %B de %Y")
    meses = {
        "January": "enero",
        "February": "febrero",
        "March": "marzo",
        "April": "abril",
        "May": "mayo",
        "June": "junio",
        "July": "julio",
        "August": "agosto",
        "September": "septiembre",
        "October": "octubre",
        "November": "noviembre",
        "December": "diciembre",
    }
    for en, es in meses.items():
        fecha_es = fecha_es.replace(en, es)

    story.append(Paragraph(f"{CIUDAD}, {fecha_es}", title_style))
    story.append(Spacer(1, 6))

    story.append(Paragraph("Señores", normal))
    story.append(Paragraph(f"<b>{deudor}</b>", normal))
    story.append(Spacer(1, 10))

    story.append(Paragraph("Estimados señores:", normal))
    story.append(Spacer(1, 8))

    story.append(
        Paragraph(
            f"Por medio de la presente, les informamos que las siguientes facturas han sido cedidas a nuestro "
            f"aliado estratégico <b>{ALIADO_ESTRATEGICO}</b>:",
            normal,
        )
    )
    story.append(Spacer(1, 10))

    # Tabla 1 (desde Excel)
    table_header = [
        "Tipo de Documento",
        "N° de Documento",
        "Importe Total",
        "Vencimiento",
    ]
    table_data = [table_header]

    for _, r in rows.iterrows():
        numdoc = "" if pd.isna(r["numdoc"]) else str(r["numdoc"]).strip()
        moneda = normalize_currency(r["moneda"])
        monto = format_amount_es(r["monto_num"])
        venc = format_date_es(r["vencimiento"])

        table_data.append(["Factura", numdoc, f"{moneda} {monto}".strip(), venc])

    t1 = Table(table_data, colWidths=[45 * mm, 35 * mm, 45 * mm, 35 * mm])
    t1.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.8, colors.black),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                ("ALIGN", (1, 1), (1, -1), "CENTER"),
                ("ALIGN", (2, 1), (2, -1), "CENTER"),
                ("ALIGN", (3, 1), (3, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                ("TOPPADDING", (0, 0), (-1, 0), 8),
            ]
        )
    )
    story.append(t1)
    story.append(Spacer(1, 14))

    story.append(
        Paragraph(
            "Por lo antes indicado, les solicitamos que al vencimiento el pago sea efectuado a las respectivas "
            "cuentas bancarias del Banco de Crédito:",
            normal,
        )
    )
    story.append(Spacer(1, 10))

    # Tabla 2 fija (cuentas)
    t2_data = [["TIPO DE CUENTA", "NÚMERO DE CUENTA"]] + CUENTAS_BCP
    t2 = Table(t2_data, colWidths=[70 * mm, 90 * mm])
    t2.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.8, colors.black),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("ALIGN", (0, 0), (-1, 0), "LEFT"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
                ("TOPPADDING", (0, 0), (-1, 0), 6),
            ]
        )
    )
    story.append(t2)
    story.append(Spacer(1, 14))

    story.append(Paragraph("Quedamos atentos a cualquier consulta adicional.", normal))
    story.append(Spacer(1, 14))

    story.append(Paragraph("Atentamente,", normal))
    story.append(Spacer(1, 20))

    story.append(Paragraph("______________________________", normal))
    story.append(Paragraph(f"{FIRMA_NOMBRE}", normal))
    story.append(Paragraph(f"{FIRMA_CARGO}", normal))

    doc.build(story)
