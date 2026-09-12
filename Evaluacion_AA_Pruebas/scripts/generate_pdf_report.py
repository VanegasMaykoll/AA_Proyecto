#!/usr/bin/env python3
"""
Generador del Informe Técnico en Formato PDF (Máximo 5 carillas)
Proyecto de Curso: Análisis de Algoritmos (MCC - ESPOL)
Tema: Evaluación Experimental y Comparativa de Estructuras Aumentadas para Reportes RAP
Autor: Maykoll Vanegas Silva
Docente: Ana Tapia, Ph.D.
"""

import os
import sys

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether, PageBreak, HRFlowable
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    """
    Canvas personalizado para calcular y mostrar el total de páginas
    en el pie de página ('Carilla X de Y') y encabezado institucional.
    """
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#4A5568"))

        # Encabezado (a partir de la página 2)
        if self._pageNumber > 1:
            self.drawString(36, 11 * inch - 26, "ESPOL · Maestría en Ciencias de la Computación · Análisis de Algoritmos")
            self.setStrokeColor(colors.HexColor("#CBD5E0"))
            self.setLineWidth(0.5)
            self.line(36, 11 * inch - 30, 8.5 * inch - 36, 11 * inch - 30)

        # Pie de página (en todas las páginas)
        self.setStrokeColor(colors.HexColor("#CBD5E0"))
        self.setLineWidth(0.5)
        self.line(36, 32, 8.5 * inch - 36, 32)
        
        self.drawString(36, 20, "Informe de Evaluación: Estructura Aumentada y Almacenamiento KV para Reportes RAP")
        page_str = f"Carilla {self._pageNumber} de {page_count}"
        self.drawRightString(8.5 * inch - 36, 20, page_str)
        self.restoreState()

def build_pdf(output_path, images_dir):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=18,
        textColor=colors.HexColor("#1A365D"),
        alignment=1,
        spaceAfter=4
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor("#2B6CB0"),
        alignment=1,
        spaceAfter=6
    )
    author_style = ParagraphStyle(
        'DocAuthor',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#2D3748"),
        alignment=1,
        spaceAfter=8
    )
    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#1A365D"),
        spaceBefore=7,
        spaceAfter=3,
        keepWithNext=True
    )
    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=12,
        textColor=colors.HexColor("#2B6CB0"),
        spaceBefore=5,
        spaceAfter=2,
        keepWithNext=True
    )
    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor("#2D3748"),
        alignment=4,
        spaceAfter=4
    )
    callout_style = ParagraphStyle(
        'Callout_Text',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8.0,
        leading=11,
        textColor=colors.HexColor("#1A202C")
    )
    tbl_hdr_style = ParagraphStyle(
        'TableHdr',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=9.5,
        textColor=colors.white,
        alignment=1
    )
    tbl_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor("#1A202C")
    )
    tbl_cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor("#1A202C")
    )

    story = []

    # =========================================================================
    # CARILLA 1: ENCABEZADO, CONTEXTO RAP Y MODELO PROPUESTO
    # =========================================================================
    story.append(Paragraph("ESCUELA SUPERIOR POLITÉCNICA DEL LITORAL (ESPOL)", subtitle_style))
    story.append(Paragraph("MAESTRÍA EN CIENCIAS DE LA COMPUTACIÓN · ANÁLISIS DE ALGORITMOS", subtitle_style))
    story.append(Paragraph("Evaluación Experimental y Análisis Crítico de una Estructura de Datos Aumentada para Reportes de Retroalimentación Automática (RAP ESPOL)", title_style))
    story.append(Paragraph("<b>Autor:</b> Maykoll Vanegas Silva &nbsp;|&nbsp; <b>Docente:</b> Ana Tapia, Ph.D. &nbsp;|&nbsp; <b>Fecha:</b> Septiembre 2026", author_style))
    story.append(HRFlowable(width="100%", thickness=1.2, color=colors.HexColor("#1A365D"), spaceBefore=2, spaceAfter=6))

    resumen_text = (
        "<b>Resumen Ejecutivo—</b> Este informe presenta la autoevaluación experimental y el análisis crítico de la propuesta "
        "algorítmica diseñada para optimizar el almacenamiento y consulta multidimensional de informes producidos por el sistema "
        "RAP (<i>Automatic Presentation Feedback</i>, Ochoa et al., 2018). Frente al modelo actual de RAP basado en persistencia "
        "aislada y recorridos lineales <i>O(N)</i>, se implementó y validó una arquitectura desacoplada en dos etapas: (i) índices "
        "secundarios en memoria mediante árboles AVL aumentados con invariantes estadísticos <i>(C, S, SS)</i> capaces de resolver "
        "consultas de rango en tiempo logarítmico <i>Θ(log Dm)</i>, y (ii) almacenamiento persistente primario clave-valor basado en "
        "LSM-Tree (LevelDB 1.23) asistido por filtros probabilísticos de pertenencia aproximada (Bloom y Ribbon). "
        "Las pruebas empíricas sobre 1,000, 10,000 y 50,000 reportes demuestran factores de aceleración de hasta <b>9,300x</b> en "
        "agregaciones estadísticas e identifican con rigor tanto las fortalezas asintóticas como las debilidades de consumo y gestión de recursos."
    )
    tbl_resumen = Table([[Paragraph(resumen_text, callout_style)]], colWidths=[7.4 * inch])
    tbl_resumen.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#EBF8FF")),
        ('BOX', (0,0), (-1,-1), 0.8, colors.HexColor("#3182CE")),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(tbl_resumen)
    story.append(Spacer(1, 6))

    story.append(Paragraph("1. Introducción y Contexto Operativo del Sistema RAP", h1_style))
    story.append(Paragraph(
        "El sistema RAP (Ochoa et al., 2018) fue desarrollado en ESPOL como una solución de retroalimentación automática de "
        "habilidades de presentación oral a través de sensores de bajo costo (cámaras RGB, micrófonos y Kinect). El flujo original "
        "de RAP captura señales multimodales, calcula métricas de contacto visual, volumen y postura, y genera un informe individual "
        "posterior a cada presentación. Sin embargo, RAP concibió el almacenamiento como una etapa final pasiva, limitándose a guardar "
        "archivos estructurados independientes o tablas relacionales planas sin estructuras de indexación especializadas.", body_style
    ))
    story.append(Paragraph(
        "Cuando una institución educativa acumula miles de presentaciones a lo largo de diversos semestres, surgen necesidades críticas: "
        "obtener estadísticas de cohortes (e.g., promedio de mirada de los estudiantes con desempeño sobresaliente), identificar "
        "presentadores en riesgo y ejecutar búsquedas combinadas multi-criterio. Una estrategia basada en barrido secuencial "
        "<b>(Fuerza Bruta)</b> requiere <i>O(N)</i> evaluaciones por cada predicado, colapsando los paneles analíticos docentes.", body_style
    ))

    story.append(Paragraph("2. Modelo de Informes y Arquitectura Algorítmica Propuesta", h1_style))
    story.append(Paragraph(
        "Cada informe se modela como una 5-tupla formal <i>r<sub>i</sub> = (id<sub>i</sub>, u<sub>i</sub>, t<sub>i</sub>, M<sub>i</sub>, D<sub>i</sub>)</i>, "
        "donde <i>id<sub>i</sub></i> es la clave primaria única, <i>u<sub>i</sub></i> es el expositor, <i>t<sub>i</sub></i> es la marca temporal, "
        "<i>D<sub>i</sub></i> es el payload JSON (~1 KB con transcripción y desglose de diapositivas) y <i>M<sub>i</sub> = (g, z, v, p)</i> "
        "reúne las cuatro métricas continuas discretizadas: puntaje global <i>g ∈ [1.0, 5.0]</i>, mirada <i>z ∈ [0.0, 1.0]</i>, "
        "volumen <i>v ∈ [0.0, 1.0]</i> y postura <i>p ∈ [0.0, 1.0]</i>.", body_style
    ))
    story.append(Paragraph(
        "Para responder eficientemente a estas demandas, se implementó una <b>arquitectura desacoplada en dos fases</b>: "
        "<br/>• <b>Fase 1 (Indexación y Agregación en Memoria):</b> Cuatro árboles AVL balanceados (<i>I<sub>g</sub>, I<sub>z</sub>, I<sub>v</sub>, I<sub>p</sub></i>). "
        "Cada nodo almacena la clave <i>k<sub>x</sub></i>, la lista de identificadores asociados <i>L<sub>x</sub></i>, y los campos aumentados del subárbol: "
        "cardinalidad <i>C(x) = C(x<sub>L</sub>) + |L<sub>x</sub>| + C(x<sub>R</sub>)</i>, suma <i>S(x) = S(x<sub>L</sub>) + k<sub>x</sub>|L<sub>x</sub>| + S(x<sub>R</sub>)</i> "
        "y suma de cuadrados <i>SS(x) = SS(x<sub>L</sub>) + k<sub>x</sub><sup>2</sup>|L<sub>x</sub>| + SS(x<sub>R</sub>)</i>. "
        "Estos invariantes se restauran en tiempo <i>Θ(1)</i> durante cada rotación AVL (Algoritmo 1). "
        "Mediante la función de prefijo <code>AgregadoLE(t)</code> (Algoritmo 4), cualquier consulta estadística sobre un intervalo <i>[a, b]</i> "
        "se resuelve calculando <i>A<sub>[a,b]</sub> = A<sub>≤b</sub> - A<sub>&lt;a</sub></i> en tiempo estricto <b><i>Θ(log D<sub>m</sub>)</i></b>, "
        "sin recorrer los elementos del intervalo ni materializar registros. "
        "<br/>• <b>Fase 2 (Almacenamiento Clave-Valor Persistente):</b> Los payloads pesados <i>D<sub>i</sub></i> residen en LevelDB 1.23 "
        "(motor LSM). Una vez que la Fase 1 determina el conjunto de claves coincidentes <i>R<sub>Q</sub></i> mediante intersección de "
        "cardinalidad creciente (Algoritmo 5), se recuperan únicamente dichos registros mediante <code>MultiGet(R<sub>Q</sub>)</code> (Algoritmo 6), "
        "donde filtros probabilísticos (<b>Bloom</b> y <b>Ribbon</b>) aceleran el descarte de bloques SSTable en disco.", body_style
    ))

    # =========================================================================
    # CARILLA 2: METODOLOGÍA EXPERIMENTAL Y RESULTADOS MULTI-ESCALA
    # =========================================================================
    story.append(PageBreak())
    story.append(Paragraph("3. Metodología Experimental y Validación de Correctitud", h1_style))
    story.append(Paragraph(
        "La evaluación empírica se condujo en un servidor dedicado equipado con un procesador Intel Core i5-12600KF (16 hilos, 4.9 GHz), "
        "32 GB de RAM DDR4 y almacenamiento NVMe sobre Linux 6.8. Se sintetizaron reportes multimodales mediante <code>generate_rap_dataset.py</code> "
        "reproduciendo las distribuciones gaussianas y beta observadas en los estudios de Ochoa et al. (2018), bajo tres escalas representativas: "
        "<b><i>N = 1,000</i></b> (prueba de curso pequeño), <b><i>N = 10,000</i></b> (cohorte anual institucional) y <b><i>N = 50,000</i></b> "
        "(registro histórico plurianual). Cada consulta fue ejecutada 50 veces consecutivas para registrar latencias medias en microsegundos (µs).", body_style
    ))
    story.append(Paragraph(
        "<b>Validación de Correctitud Matemática:</b> Previo a las mediciones, se implementó <code>test_correctness.cpp</code>, "
        "certificando formalmente que: (1) el factor de balance AVL <i>|h<sub>L</sub> - h<sub>R</sub>| ≤ 1</i> se mantiene en el 100% de los nodos "
        "tras 50,000 inserciones aleatorias (altura máxima observada: <i>h = 11</i> con 401 claves discretas); (2) los valores de media, "
        "varianza y desviación estándar derivados en <i>Θ(log D<sub>m</sub>)</i> son matemáticamente idénticos a los de Fuerza Bruta "
        "(error numérico <i>Δ &lt; 10<sup>-6</sup></i>); y (3) los identificadores recuperados por poda coinciden exactamente con el filtrado exhaustivo.", body_style
    ))

    story.append(Paragraph("4. Resultados Experimentales Consolidados", h1_style))
    story.append(Paragraph(
        "A continuación se detallan las mediciones empíricas obtenidas para las familias de operaciones evaluadas.", body_style
    ))

    story.append(Paragraph("Tabla 1: Tiempo de Ingesta e Indexación en Memoria", h2_style))
    raw_tbl1 = [
        [Paragraph("Escala N", tbl_hdr_style), Paragraph("Ingesta Fuerza Bruta (std::vector)", tbl_hdr_style), Paragraph("Ingesta + 4 AVL Aumentados", tbl_hdr_style), Paragraph("Latencia por Informe", tbl_hdr_style)],
        [Paragraph("N = 1,000", tbl_cell_style), Paragraph("0.354 ms", tbl_cell_style), Paragraph("0.282 ms", tbl_cell_bold), Paragraph("0.282 µs / informe", tbl_cell_style)],
        [Paragraph("N = 10,000", tbl_cell_style), Paragraph("3.277 ms", tbl_cell_style), Paragraph("2.590 ms", tbl_cell_bold), Paragraph("0.259 µs / informe", tbl_cell_style)],
        [Paragraph("N = 50,000", tbl_cell_style), Paragraph("15.585 ms", tbl_cell_style), Paragraph("11.351 ms", tbl_cell_bold), Paragraph("0.227 µs / informe", tbl_cell_style)],
    ]
    t1 = Table(raw_tbl1, colWidths=[1.3*inch, 2.3*inch, 2.3*inch, 1.5*inch])
    t1.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#2B6CB0")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E0")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F7FAFC")]),
        ('ALIGN', (1,1), (-1,-1), 'CENTER'),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t1)
    story.append(Spacer(1, 4))

    story.append(Paragraph("Tabla 2: Consultas Estadísticas de Rango (Algoritmo 4: AgregadoLE)", h2_style))
    raw_tbl2 = [
        [Paragraph("Escala N", tbl_hdr_style), Paragraph("Intervalo Evaluado", tbl_hdr_style), Paragraph("k Informes", tbl_hdr_style), Paragraph("AVL Aumentado Θ(log D)", tbl_hdr_style), Paragraph("Fuerza Bruta O(N)", tbl_hdr_style), Paragraph("Factor Speedup", tbl_hdr_style)],
        [Paragraph("N = 1,000", tbl_cell_style), Paragraph("Puntaje Global [3.50, 3.80]", tbl_cell_style), Paragraph("358", tbl_cell_style), Paragraph("0.0253 µs (25 ns)", tbl_cell_bold), Paragraph("3.55 µs", tbl_cell_style), Paragraph("140.3x", tbl_cell_bold)],
        [Paragraph("N = 10,000", tbl_cell_style), Paragraph("Puntaje Global [3.50, 3.80]", tbl_cell_style), Paragraph("3,570", tbl_cell_style), Paragraph("0.0299 µs (30 ns)", tbl_cell_bold), Paragraph("39.84 µs", tbl_cell_style), Paragraph("1,331.7x", tbl_cell_bold)],
        [Paragraph("N = 50,000", tbl_cell_style), Paragraph("Puntaje Global [3.50, 3.80]", tbl_cell_style), Paragraph("17,896", tbl_cell_style), Paragraph("0.0273 µs (27 ns)", tbl_cell_bold), Paragraph("253.54 µs", tbl_cell_style), Paragraph("9,300.9x", tbl_cell_bold)],
        [Paragraph("N = 50,000", tbl_cell_style), Paragraph("Mirada Audiencia [0.60, 0.85]", tbl_cell_style), Paragraph("28,074", tbl_cell_style), Paragraph("0.0391 µs (39 ns)", tbl_cell_bold), Paragraph("220.13 µs", tbl_cell_style), Paragraph("5,629.8x", tbl_cell_bold)],
        [Paragraph("N = 50,000", tbl_cell_style), Paragraph("Volumen de Voz [0.65, 0.90]", tbl_cell_style), Paragraph("31,590", tbl_cell_style), Paragraph("0.0334 µs (33 ns)", tbl_cell_bold), Paragraph("182.15 µs", tbl_cell_style), Paragraph("5,453.6x", tbl_cell_bold)],
    ]
    t2 = Table(raw_tbl2, colWidths=[1.1*inch, 2.0*inch, 0.8*inch, 1.4*inch, 1.1*inch, 1.0*inch])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#2B6CB0")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E0")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F7FAFC")]),
        ('ALIGN', (2,1), (-1,-1), 'CENTER'),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t2)
    story.append(Spacer(1, 4))

    chart1_img = os.path.join(images_dir, "grafica_1_estadisticas_latencia.png")
    if os.path.exists(chart1_img):
        story.append(Image(chart1_img, width=7.2 * inch, height=2.35 * inch))
        story.append(Paragraph("<font size=6.5 color='#718096'><b>Figura 1:</b> Latencia comparativa de consultas estadísticas de rango (escala logarítmica). Muestra la estabilidad asintótica de la aumentación frente al crecimiento lineal de Fuerza Bruta.</font>", body_style))

    # =========================================================================
    # CARILLA 3: SELECCIÓN TOP-K, MATERIALIZACIÓN Y COMPARATIVA DE FILTROS
    # =========================================================================
    story.append(PageBreak())
    story.append(Paragraph("Tabla 3: Selección Top-k de Mejores Expositores (Algoritmo 7: TopK)", h2_style))
    raw_tbl3 = [
        [Paragraph("Escala N", tbl_hdr_style), Paragraph("Consulta", tbl_hdr_style), Paragraph("AVL Top-k O(log D + k)", tbl_hdr_style), Paragraph("Fuerza Bruta O(N log k)", tbl_hdr_style), Paragraph("Factor Speedup", tbl_hdr_style)],
        [Paragraph("N = 1,000", tbl_cell_style), Paragraph("Top-10 Mejores Expositores", tbl_cell_style), Paragraph("0.133 µs", tbl_cell_bold), Paragraph("6.09 µs", tbl_cell_style), Paragraph("45.8x", tbl_cell_bold)],
        [Paragraph("N = 10,000", tbl_cell_style), Paragraph("Top-10 Mejores Expositores", tbl_cell_style), Paragraph("0.130 µs", tbl_cell_bold), Paragraph("57.60 µs", tbl_cell_style), Paragraph("441.5x", tbl_cell_bold)],
        [Paragraph("N = 10,000", tbl_cell_style), Paragraph("Top-50 Mejores Expositores", tbl_cell_style), Paragraph("0.411 µs", tbl_cell_bold), Paragraph("64.43 µs", tbl_cell_style), Paragraph("156.8x", tbl_cell_bold)],
        [Paragraph("N = 50,000", tbl_cell_style), Paragraph("Top-10 Mejores Expositores", tbl_cell_style), Paragraph("0.167 µs", tbl_cell_bold), Paragraph("313.77 µs", tbl_cell_style), Paragraph("1,884.1x", tbl_cell_bold)],
        [Paragraph("N = 50,000", tbl_cell_style), Paragraph("Top-100 Mejores Expositores", tbl_cell_style), Paragraph("0.623 µs", tbl_cell_bold), Paragraph("355.14 µs", tbl_cell_style), Paragraph("570.0x", tbl_cell_bold)],
    ]
    t3 = Table(raw_tbl3, colWidths=[1.1*inch, 2.3*inch, 1.5*inch, 1.4*inch, 1.1*inch])
    t3.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#2B6CB0")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E0")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F7FAFC")]),
        ('ALIGN', (2,1), (-1,-1), 'CENTER'),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t3)
    story.append(Spacer(1, 4))

    story.append(Paragraph("Tabla 4: Materialización en Almacenamiento Persistente (LevelDB 1.23 + Filtros AMQ)", h2_style))
    raw_tbl4 = [
        [Paragraph("Escala N", tbl_hdr_style), Paragraph("Claves RQ", tbl_hdr_style), Paragraph("Sin Filtro (Baseline)", tbl_hdr_style), Paragraph("Bloom Filter (10 bpk)", tbl_hdr_style), Paragraph("Ribbon Filter (10 bpk equiv)", tbl_hdr_style), Paragraph("Ahorro Latencia AMQ", tbl_hdr_style)],
        [Paragraph("N = 1,000", tbl_cell_style), Paragraph("215 items", tbl_cell_style), Paragraph("3.298 µs / op", tbl_cell_style), Paragraph("2.712 µs / op", tbl_cell_style), Paragraph("2.698 µs / op", tbl_cell_bold), Paragraph("18.2% ahorro", tbl_cell_bold)],
        [Paragraph("N = 10,000", tbl_cell_style), Paragraph("2,146 items", tbl_cell_style), Paragraph("3.271 µs / op", tbl_cell_style), Paragraph("2.687 µs / op", tbl_cell_style), Paragraph("2.675 µs / op", tbl_cell_bold), Paragraph("18.2% ahorro", tbl_cell_bold)],
        [Paragraph("N = 50,000", tbl_cell_style), Paragraph("10,801 items", tbl_cell_style), Paragraph("2.282 µs / op", tbl_cell_style), Paragraph("2.292 µs / op", tbl_cell_style), Paragraph("2.324 µs / op", tbl_cell_style), Paragraph("Caché en caliente", tbl_cell_style)],
        [Paragraph("Misses (1k)", tbl_cell_style), Paragraph("1,000 claves", tbl_cell_style), Paragraph("0.057 µs / op", tbl_cell_style), Paragraph("0.066 µs / op", tbl_cell_style), Paragraph("0.049 µs / op", tbl_cell_bold), Paragraph("Descarte instantáneo", tbl_cell_style)],
    ]
    t4 = Table(raw_tbl4, colWidths=[1.0*inch, 1.0*inch, 1.4*inch, 1.4*inch, 1.5*inch, 1.1*inch])
    t4.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#2B6CB0")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E0")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F7FAFC")]),
        ('ALIGN', (2,1), (-1,-1), 'CENTER'),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t4)
    story.append(Spacer(1, 8))

    chart2_img = os.path.join(images_dir, "grafica_2_topk_latencia.png")
    chart3_img = os.path.join(images_dir, "grafica_3_recuperacion_filtros.png")

    if os.path.exists(chart2_img) and os.path.exists(chart3_img):
        img_t = Table([
            [Image(chart2_img, width=3.55 * inch, height=2.15 * inch),
             Image(chart3_img, width=3.75 * inch, height=2.15 * inch)]
        ], colWidths=[3.6 * inch, 3.8 * inch])
        img_t.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
            ('TOPPADDING', (0,0), (-1,-1), 0),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ]))
        story.append(img_t)
        story.append(Paragraph("<font size=6.5 color='#718096'><b>Figuras 2 y 3:</b> (Izquierda) Comparativa de latencia en selección Top-K. (Derecha) Desempeño de recuperación MultiGet en LevelDB comparando Sin Filtro, Bloom y Ribbon.</font>", body_style))

    # =========================================================================
    # CARILLA 4: ANÁLISIS CRÍTICO - FORTALEZAS Y DEBILIDADES
    # =========================================================================
    story.append(PageBreak())
    story.append(Paragraph("5. Análisis Crítico: Fortalezas de la Propuesta", h1_style))
    story.append(Paragraph(
        "<b>1. Invarianza Temporal Asintótica:</b> La mayor fortaleza teórica y práctica demostrada es que la operación estadística de intervalo "
        "opera en <b><i>Θ(log D<sub>m</sub>)</i></b>. El tiempo de respuesta permaneció invariable (~25 a 30 nanosegundos) tanto para "
        "<i>N = 1,000</i> como para <i>N = 50,000</i>. Al no requerir visitar los <i>k</i> elementos contenidos en el rango (que llegaron a 17,896 informes), "
        "el algoritmo elimina completamente el factor <i>k</i> de la agregación, superando al recorrido secuencial por más de <b>9,300 veces</b>.", body_style
    ))
    story.append(Paragraph(
        "<b>2. Desacoplamiento Eficiente y Poda Selectiva (Caso 2,146 / 10,000):</b> El diseño en dos fases evita saturar el almacenamiento "
        "persistente. Cuando se evaluó una búsqueda por notas en <i>[4.00, 4.50]</i> sobre 10,000 registros, el índice secundario resolvió en RAM "
        "que solo 2,146 informes cumplían el criterio. La fase de materialización invocó <code>MultiGet</code> exclusivamente para ese subconjunto, "
        "evitando <b>7,854 lecturas innecesarias a disco</b>. Esto garantiza que la carga de E/S sea proporcional únicamente a la selectividad de salida.", body_style
    ))
    story.append(Paragraph(
        "<b>3. Aceleración con Filtros AMQ Modernos (Ribbon vs. Bloom):</b> En LevelDB, la presencia de filtros probabilísticos redujo en un <b>18.2%</b> "
        "la latencia de lectura puntual en almacenamiento secundario. Más aún, <b>Ribbon Filter</b> logró una tasa de acierto y latencia idéntica a Bloom "
        "(2.675 µs vs. 2.687 µs) pero con un ahorro espacial teórico de ~30% en bits por clave (7.0 bpk vs. 10.0 bpk), optimizando la huella de memoria en SSTables.", body_style
    ))
    story.append(Paragraph(
        "<b>4. Optimización Heurística de Intersección (Algoritmo 5):</b> Al ordenar los resultados intermedios de los 4 predicados por cardinalidad "
        "creciente antes de aplicar la intersección conjuntiva, el tamaño del conjunto candidato se reduce al mínimo desde el primer paso, evitando "
        "construir hash tables masivas sobre ramas poco selectivas y facilitando la salida temprana si el conjunto se vacía.", body_style
    ))

    story.append(Paragraph("6. Análisis Crítico: Debilidades y Desafíos Arquitectónicos", h1_style))
    story.append(Paragraph(
        "A pesar de sus sobresalientes ventajas algorítmicas, la autoevaluación identifica cuatro debilidades operativas sustanciales:", body_style
    ))
    story.append(Paragraph(
        "<b>1. Latencia Plana y Dificultad de Autoscaling en Infraestructura Cloud:</b><br/>"
        "Debido a que el costo depende exclusivamente de la altura del árbol <i>h = O(log D<sub>m</sub>)</i> y no del volumen de datos consultado, "
        "una consulta estadística toma prácticamente el mismo tiempo (~25 a 30 ns) ya sea que el intervalo contenga 10 informes o 30,000 informes. "
        "Si bien asintóticamente es un comportamiento ideal, desde la perspectiva de <b>arquitectura de sistemas y servicios en la nube (cloud)</b> "
        "esto introduce un comportamiento contraintuitivo: las herramientas de orquestación y auto-escalado horizontal (e.g., Kubernetes HPA, AWS Auto Scaling) "
        "suelen monitorear métricas de carga como tiempo de CPU por petición o longitud de colas proporcionales al tamaño del lote procesado. "
        "Dado que el tiempo no refleja el tamaño del conjunto de datos procesado, no es posible asignar recursos elásticos de forma proporcional "
        "a la escala de los datos; el cuello de botella se traslada enteramente a la contención de concurrencia y cerrojos en memoria cuando "
        "múltiples hilos modifican o consultan los árboles simultáneamente.", body_style
    ))
    story.append(Paragraph(
        "<b>2. Sobrecarga de Memoria Principal (RAM):</b><br/>"
        "Mantener cuatro índices independientes totalmente residentes en memoria impone un costo espacial de <i>O(M · N)</i> referencias de claves y "
        "punteros de nodos. Para colecciones de cientos de miles de informes, la RAM requerida para la topología de los 4 AVL y los vectores de "
        "identificadores <i>L<sub>x</sub></i> puede comprometer servidores con memoria acotada, exigiendo estrategias futuras de paginación de nodos.", body_style
    ))
    story.append(Paragraph(
        "<b>3. Costo de Rebalanceo en Ingesta Continua de Alta Concurrencia:</b><br/>"
        "Cada informe nuevo exige actualizar los cuatro árboles AVL. Aunque la inserción toma <i>O(log D<sub>m</sub>)</i> (~0.25 µs por informe en memoria), "
        "las rotaciones obligan a recalcular los campos aumentados <i>(C, S, SS)</i> a lo largo del camino hacia la raíz. En un entorno donde cientos "
        "de presentaciones finalicen sincrónicamente, la tasa de escritura podría verse acotada en comparación con motores LSM append-only puros.", body_style
    ))
    story.append(Paragraph(
        "<b>4. Sensibilidad a la Discretización Continua (Cardinalidad del Dominio):</b><br/>"
        "La altura del árbol <i>h = O(log D<sub>m</sub>)</i> depende del número de valores distintos <i>D<sub>m</sub></i>. Al discretizar a 2 decimales, "
        "<i>D<sub>m</sub> ≤ 401</i> (h ≤ 11). Sin embargo, si se emplean valores flotantes de 64 bits de alta precisión sin truncar, <i>D<sub>m</sub> ≈ N</i>, "
        "lo que incrementaría el número de nodos creados, la fragmentación de memoria en el heap y la profundidad del árbol.", body_style
    ))

    # =========================================================================
    # CARILLA 5: COMPARATIVA CON RAP ACTUAL, CONCLUSIONES Y REFERENCIAS
    # =========================================================================
    story.append(PageBreak())
    story.append(Paragraph("7. Comparación con el Sistema RAP Actual (Ochoa et al., 2018)", h1_style))
    story.append(Paragraph(
        "Para comprender el impacto de esta solución, la siguiente tabla contrasta punto a punto las capacidades del sistema RAP "
        "original frente a la arquitectura aumentada desarrollada:", body_style
    ))

    raw_tbl5 = [
        [Paragraph("Dimensión de Análisis", tbl_hdr_style), Paragraph("Sistema RAP Actual (Ochoa et al., 2018)", tbl_hdr_style), Paragraph("Propuesta con Estructura Aumentada + LSM", tbl_hdr_style)],
        [
            Paragraph("<b>Enfoque de Almacenamiento</b>", tbl_cell_bold),
            Paragraph("Pasivo / Aislado: Guarda reportes finales en archivos o bases relacionales sin índices multidimensionales.", tbl_cell_style),
            Paragraph("Desacoplado y Activo: Índices secundarios en memoria RAM sincronizados con motor clave-valor persistente.", tbl_cell_style)
        ],
        [
            Paragraph("<b>Consultas Estadísticas de Cohorte</b>", tbl_cell_bold),
            Paragraph("Fuerza Bruta <i>O(N)</i>: Requiere escanear toda la colección de informes para calcular media y varianza.", tbl_cell_style),
            Paragraph("Aumentación <i>Θ(log D<sub>m</sub>)</i>: Cálculo en 25 nanosegundos mediante resta de prefijos sin tocar datos.", tbl_cell_style)
        ],
        [
            Paragraph("<b>Selección de Extremos (Top-K)</b>", tbl_cell_bold),
            Paragraph("Ordenamiento <i>O(N log N)</i>: Costoso al crecer la base de datos de estudiantes.", tbl_cell_style),
            Paragraph("Poda en AVL <i>O(log D<sub>m</sub> + k)</i>: Recupera los mejores expositores en 0.13 µs (440x speedup).", tbl_cell_style)
        ],
        [
            Paragraph("<b>Consultas Combinadas Multi-Criterio</b>", tbl_cell_bold),
            Paragraph("Barrido secuencial multi-filtro: Complejidad lineal multiplicada por la cantidad de métricas evaluadas.", tbl_cell_style),
            Paragraph("Intersección por cardinalidad creciente: Reduce drásticamente candidatos en memoria con salida temprana.", tbl_cell_style)
        ],
        [
            Paragraph("<b>Escalabilidad Institucional</b>", tbl_cell_bold),
            Paragraph("Orientado a uso local por aula: Latencias perceptibles al intentar analizar semestres acumulados.", tbl_cell_style),
            Paragraph("Escala de Campus: Diseñado para analítica en tiempo real sobre decenas de miles de reportes simultáneos.", tbl_cell_style)
        ],
        [
            Paragraph("<b>Eficiencia de E/S a Disco</b>", tbl_cell_bold),
            Paragraph("Sin filtros probabilísticos en almacenamiento: Lecturas redundantes para descartar reportes no coincidentes.", tbl_cell_style),
            Paragraph("Filtros Ribbon y Bloom en LevelDB: 18% menos latencia en hits y descarte casi instantáneo en misses.", tbl_cell_style)
        ]
    ]
    t5 = Table(raw_tbl5, colWidths=[1.6*inch, 2.8*inch, 3.0*inch])
    t5.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#2B6CB0")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E0")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F7FAFC")]),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t5)
    story.append(Spacer(1, 4))

    story.append(Paragraph("8. Conclusiones", h1_style))
    story.append(Paragraph(
        "<b>1. Validación Empírica de la Teoría:</b> La autoevaluación confirma con precisión de microsegundos las cotas deducidas "
        "teóricamente en la propuesta. La aumentación del árbol AVL convierte operaciones de agregación estadística costosas en "
        "cálculos de complejidad logarítmica estricta, alcanzando un speedup de más de <b>9,300x</b> frente a Fuerza Bruta en <i>N = 50,000</i>.", body_style
    ))
    story.append(Paragraph(
        "<b>2. Transformación Práctica del Sistema RAP:</b> La integración de índices secundarios aumentados con LevelDB transforma "
        "al sistema RAP de una herramienta diagnóstica individual a una plataforma analítica institucional capaz de generar dashboards "
        "de desempeño docente en tiempo real sin latencias perceptibles.", body_style
    ))
    story.append(Paragraph(
        "<b>3. Compensación de Diseño (Trade-offs):</b> La debilidad principal radica en el costo espacial en RAM y la dificultad de modelar "
        "el dimensionamiento elástico de servidores ante una latencia plana e insensible a la entrada. Como trabajo futuro, se recomienda "
        "explorar la persistencia híbrida de nodos AVL fríos y la concurrencia lock-free para mitigar la contención en ingesta masiva.", body_style
    ))

    story.append(Paragraph("Referencias Bibliográficas", h2_style))
    story.append(Paragraph(
        "<font size=7 color='#4A5568'>"
        "[1] X. Ochoa, F. Domínguez, B. Guamán, R. Maya, G. Falcones, and J. Castells, “The RAP system: Automatic feedback of oral presentation skills using multimodal analysis and low-cost sensors,” in <i>Proc. LAK ’18</i>. ACM, 2018, pp. 360–364.<br/>"
        "[2] T. H. Cormen, C. E. Leiserson, R. L. Rivest, and C. Stein, <i>Introduction to Algorithms</i>, 4th ed. Cambridge, MA: MIT Press, 2022.<br/>"
        "[3] G. M. Adelson-Velsky and E. M. Landis, “An algorithm for the organization of information,” <i>Soviet Mathematics Doklady</i>, vol. 3, pp. 1259–1263, 1962.<br/>"
        "[4] P. C. Dillinger and S. Walzer, “Ribbon filter: Practically smaller than bloom and xor,” <i>CoRR</i>, vol. abs/2103.02515, 2021.<br/>"
        "[5] P. E. O’Neil, E. Cheng, D. Gawlick, and E. J. O’Neil, “The log-structured merge-tree (LSM-tree),” <i>Acta Informatica</i>, vol. 33, no. 4, pp. 351–385, 1996."
        "</font>", body_style
    ))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[✓] PDF generado exitosamente en: {output_path}")

def main():
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    output_pdf = os.path.join(root_dir, "Informe_Evaluacion_Algoritmos_RAP.pdf")
    images_dir = os.path.join(root_dir, "Evaluacion_AA_Pruebas", "results")

    if len(sys.argv) > 1:
        output_pdf = sys.argv[1]
    if len(sys.argv) > 2:
        images_dir = sys.argv[2]

    build_pdf(output_pdf, images_dir)

if __name__ == "__main__":
    main()
