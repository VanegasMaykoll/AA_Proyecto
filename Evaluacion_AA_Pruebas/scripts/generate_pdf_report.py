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
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable
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

        # Encabezado (a partir de la carilla 2)
        if self._pageNumber > 1:
            self.drawString(36, 11 * inch - 26, "ESPOL · Maestría en Ciencias de la Computación · Análisis de Algoritmos")
            self.setStrokeColor(colors.HexColor("#CBD5E0"))
            self.setLineWidth(0.5)
            self.line(36, 11 * inch - 30, 8.5 * inch - 36, 11 * inch - 30)

        # Pie de página (en todas las carillas)
        self.setStrokeColor(colors.HexColor("#CBD5E0"))
        self.setLineWidth(0.5)
        self.line(36, 30, 8.5 * inch - 36, 30)
        
        self.drawString(36, 19, "Informe de Evaluación: Estructura Aumentada y Almacenamiento KV para Reportes RAP")
        page_str = f"Carilla {self._pageNumber} de {page_count}"
        self.drawRightString(8.5 * inch - 36, 19, page_str)
        self.restoreState()

def build_pdf(output_path):
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
        fontSize=13.5,
        leading=16.5,
        textColor=colors.HexColor("#1A202C"),
        alignment=1,
        spaceAfter=3
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#4A5568"),
        alignment=1,
        spaceAfter=4
    )
    author_style = ParagraphStyle(
        'DocAuthor',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#2D3748"),
        alignment=1,
        spaceAfter=6
    )
    abstract_style = ParagraphStyle(
        'Abstract',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.0,
        leading=11,
        textColor=colors.HexColor("#2D3748"),
        alignment=4, # Justificado
        leftIndent=15,
        rightIndent=15,
        spaceAfter=8
    )
    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13,
        textColor=colors.HexColor("#1A202C"),
        spaceBefore=7,
        spaceAfter=3,
        keepWithNext=True
    )
    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#2D3748"),
        spaceBefore=5,
        spaceAfter=2,
        keepWithNext=True
    )
    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.0,
        leading=11.0,
        textColor=colors.HexColor("#2D3748"),
        alignment=4,
        spaceAfter=3.5
    )
    tbl_hdr_style = ParagraphStyle(
        'TableHdr',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.2,
        leading=9.0,
        textColor=colors.white,
        alignment=1
    )
    tbl_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.2,
        leading=9.0,
        textColor=colors.HexColor("#1A202C")
    )
    tbl_cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.2,
        leading=9.0,
        textColor=colors.HexColor("#1A202C")
    )

    story = []

    # =========================================================================
    # ENCABEZADO Y RESUMEN
    # =========================================================================
    story.append(Paragraph("ESCUELA SUPERIOR POLITÉCNICA DEL LITORAL · MAESTRÍA EN CIENCIAS DE LA COMPUTACIÓN", subtitle_style))
    story.append(Paragraph("Evaluación Experimental y Análisis Crítico de una Estructura Aumentada para Reportes RAP", title_style))
    story.append(Paragraph("<b>Autor:</b> Maykoll Vanegas Silva &nbsp;|&nbsp; <b>Docente:</b> Ana Tapia, Ph.D. &nbsp;|&nbsp; <b>Materia:</b> Análisis de Algoritmos", author_style))
    story.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor("#4A5568"), spaceBefore=1, spaceAfter=6))

    # Resumen en línea (sin cuadro azul, más sobrio)
    resumen_text = (
        "<b>Resumen—</b> Este informe presenta la evaluación experimental de una estructura de datos aumentada diseñada para "
        "almacenar y consultar informes de retroalimentación automática de presentaciones orales del sistema RAP (Ochoa et al., 2018). "
        "Frente a esquemas tradicionales basados en barridos secuenciales <i>O(N)</i>, se implementó una arquitectura desacoplada en "
        "dos etapas: (i) índices secundarios en memoria mediante cuatro árboles AVL aumentados con invariantes <i>(C, S, SS)</i> "
        "que resuelven consultas estadísticas por intervalo con costo <i>O(log D<sub>m</sub>)</i> en el peor caso, y (ii) almacenamiento primario "
        "persistente en un motor LSM-Tree (LevelDB 1.23) con Bloom Filter nativo y una implementación personalizada de Ribbon integrada mediante "
        "la interfaz extensible <i>FilterPolicy</i>. Las pruebas sobre 1,000, 10,000 y 50,000 reportes demuestran factores de aceleración de hasta "
        "<b>9,300x</b> en agregaciones de rango y reducciones de latencia de hasta el 18.2% en lecturas puntuales según el estado de la caché, "
        "analizando de forma crítica las fortalezas asintóticas, el efecto de la discretización de claves y los compromisos de concurrencia y memoria."
    )
    story.append(Paragraph(resumen_text, abstract_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#E2E8F0"), spaceBefore=0, spaceAfter=5))

    # =========================================================================
    # SECCIÓN 1: INTRODUCCIÓN Y CONTEXTO OPERATIVO
    # =========================================================================
    story.append(Paragraph("1. Introducción y Contexto Operativo de RAP", h1_style))
    story.append(Paragraph(
        "El sistema RAP (<i>Automatic Presentation Feedback</i>, Ochoa et al., 2018) provee retroalimentación sobre habilidades de "
        "exposición oral mediante sensores multimodales de bajo costo. Cada presentación genera un informe que resume métricas cuantitativas "
        "de contacto visual, volumen y postura. En su concepción original, RAP almacena reportes como archivos independientes o registros "
        "relacionales sin indexación secundaria multidimensional. Al acumular miles de presentaciones a lo largo de diversos periodos "
        "académicos, responder consultas agregadas de cohorte o clasificaciones mediante barridos lineales (<b>Fuerza Bruta</b>) impone una "
        "complejidad <i>O(N)</i> que compromete la respuesta en tiempo real.", body_style
    ))

    # =========================================================================
    # SECCIÓN 2: MODELO FORMAL Y ARQUITECTURA PROPUESTA
    # =========================================================================
    story.append(Paragraph("2. Modelo de Informes y Arquitectura Algorítmica", h1_style))
    story.append(Paragraph(
        "Cada informe se modela formalmente como <i>r<sub>i</sub> = (id<sub>i</sub>, u<sub>i</sub>, t<sub>i</sub>, M<sub>i</sub>, D<sub>i</sub>)</i>, "
        "donde <i>id<sub>i</sub></i> es el identificador único, <i>u<sub>i</sub></i> el expositor, <i>t<sub>i</sub></i> la marca de tiempo, "
        "<i>D<sub>i</sub></i> el payload JSON (~1 KB con desglose multimodal detallado) y <i>M<sub>i</sub> = (g, z, v, p)</i> reúne cuatro "
        "métricas continuas dentro de los dominios definidos para la evaluación: puntaje global <i>g ∈ [1.0, 5.0]</i> y componentes normalizados "
        "de contacto visual <i>z ∈ [0.0, 1.0]</i>, volumen <i>v ∈ [0.0, 1.0]</i> y postura <i>p ∈ [0.0, 1.0]</i>, acordes a las escalas observadas "
        "en la literatura de RAP. Se implementó una <b>arquitectura desacoplada en dos fases</b>:", body_style
    ))
    story.append(Paragraph(
        "• <b>Fase 1 (Índices Secundarios Aumentados en RAM):</b> Cuatro árboles AVL independientes (<i>I<sub>g</sub>, I<sub>z</sub>, I<sub>v</sub>, I<sub>p</sub></i>). "
        "Cada nodo almacena la clave métrica <i>k<sub>x</sub></i>, una lista de identificadores <i>L<sub>x</sub></i> y campos aumentados de subárbol: "
        "cardinalidad <i>C(x) = C(x<sub>L</sub>) + |L<sub>x</sub>| + C(x<sub>R</sub>)</i>, suma <i>S(x) = S(x<sub>L</sub>) + k<sub>x</sub>|L<sub>x</sub>| + S(x<sub>R</sub>)</i> "
        "y suma de cuadrados <i>SS(x) = SS(x<sub>L</sub>) + k<sub>x</sub><sup>2</sup>|L<sub>x</sub>| + SS(x<sub>R</sub>)</i>, actualizados en <i>O(1)</i> "
        "durante inserciones y rotaciones. Mediante la función de prefijo <code>AgregadoLE(t)</code>, las estadísticas de cualquier intervalo <i>[a, b]</i> "
        "se calculan como <i>A<sub>[a,b]</sub> = A<sub>≤b</sub> - A<sub>&lt;a</sub></i> con costo <b><i>O(log D<sub>m</sub>)</i></b> en el peor caso, "
        "independiente del número de elementos contenidos en el rango.<br/>"
        "• <b>Fase 2 (Almacenamiento Persistente en LSM-Tree):</b> Los payloads <i>D<sub>i</sub></i> residen en LevelDB 1.23. Tras resolver "
        "los predicados en RAM y determinar el conjunto de identificadores <i>R<sub>Q</sub></i> mediante intersección ordenada por cardinalidad creciente, "
        "se implementó <code>MultiGet(R<sub>Q</sub>)</code> a nivel de la aplicación como una operación por lotes sobre llamadas individuales <code>Get()</code> "
        "de LevelDB, asistidas por filtros probabilísticos (Bloom nativo y Ribbon personalizado mediante <i>FilterPolicy</i>).", body_style
    ))

    # =========================================================================
    # SECCIÓN 3: METODOLOGÍA EXPERIMENTAL
    # =========================================================================
    story.append(Paragraph("3. Metodología Experimental y Validación de Correctitud", h1_style))
    story.append(Paragraph(
        "Los experimentos se ejecutaron sobre Linux 6.8 (Intel Core i5-12600KF, 32 GB RAM, NVMe) evaluando tres escalas: "
        "<b><i>N = 1,000</i></b>, <b><i>N = 10,000</i></b> y <b><i>N = 50,000</i></b> informes sintéticos generados dentro de los dominios definidos "
        "(semilla fija <code>seed=42</code>). Las mediciones corresponden a microbenchmarks con datos calientes en caché L1/L2 ejecutados 50 veces "
        "consecutivas para promediar latencias; en este régimen sub-microsegundo los tiempos reportados reflejan el orden de magnitud (decenas de "
        "nanosegundos) sujeto al overhead de medición del temporizador, predicción de saltos y optimizaciones del compilador.<br/>"
        "<b>Validación de Correctitud:</b> Mediante pruebas unitarias automáticas (<code>test_correctness.cpp</code>) se verificó que el balance "
        "<i>|h<sub>L</sub> - h<sub>R</sub>| ≤ 1</i> se preserva rigurosamente (altura máxima <i>h = 11</i> con 401 claves discretas), y que la media, "
        "varianza y desviación estándar coinciden con la implementación de Fuerza Bruta dentro de una tolerancia numérica de <i>10<sup>-6</sup></i>.", body_style
    ))

    # =========================================================================
    # SECCIÓN 4: RESULTADOS EXPERIMENTALES (TABLAS SOBRIAS)
    # =========================================================================
    story.append(Paragraph("4. Resultados Experimentales Consolidados", h1_style))
    story.append(Paragraph(
        "A continuación se sintetizan las métricas de rendimiento obtenidas en las tres escalas evaluadas.", body_style
    ))

    # Estilos de tablas sobrias (Gris Grafito / Slate profesional)
    c_hdr = colors.HexColor("#2D3748")      # Gris grafito oscuro
    c_border = colors.HexColor("#CBD5E0")   # Borde gris sutil
    c_zebra = colors.HexColor("#F8F9FA")    # Fondo alterno muy tenue

    # Tabla 1: Ingesta
    story.append(Paragraph("Tabla 1: Tiempo de Ingesta e Indexación en Memoria", h2_style))
    raw_tbl1 = [
        [Paragraph("Escala N", tbl_hdr_style), Paragraph("Ingesta Fuerza Bruta (std::vector)", tbl_hdr_style), Paragraph("Ingesta + 4 AVL Aumentados", tbl_hdr_style), Paragraph("Latencia por Informe", tbl_hdr_style)],
        [Paragraph("N = 1,000", tbl_cell_style), Paragraph("0.354 ms", tbl_cell_style), Paragraph("0.282 ms", tbl_cell_bold), Paragraph("0.282 µs / informe", tbl_cell_style)],
        [Paragraph("N = 10,000", tbl_cell_style), Paragraph("3.277 ms", tbl_cell_style), Paragraph("2.590 ms", tbl_cell_bold), Paragraph("0.259 µs / informe", tbl_cell_style)],
        [Paragraph("N = 50,000", tbl_cell_style), Paragraph("15.585 ms", tbl_cell_style), Paragraph("11.351 ms", tbl_cell_bold), Paragraph("0.227 µs / informe", tbl_cell_style)],
    ]
    t1 = Table(raw_tbl1, colWidths=[1.2*inch, 2.3*inch, 2.3*inch, 1.6*inch])
    t1.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_hdr),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_zebra]),
        ('ALIGN', (1,1), (-1,-1), 'CENTER'),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
    ]))
    story.append(t1)
    story.append(Paragraph(
        "<i>Nota metodológica sobre Tabla 1:</i> La ingesta en std::vector realiza la copia profunda del objeto <code>RAPReport</code> completo "
        "(incluyendo el payload JSON de ~1 KB y reasignaciones dinámicas de memoria para cada informe). En contraste, la arquitectura propuesta "
        "desacopla el payload hacia LevelDB y únicamente indexa en memoria las claves numéricas y punteros/IDs ligeros en los cuatro AVL "
        "(con <i>D<sub>m</sub> ≤ 401</i> claves discretas, el número de nodos es acotado y no se clonan los payloads), explicando la menor "
        "latencia de indexación en RAM frente a la clonación en vector.",
        ParagraphStyle('TblNote', parent=styles['Normal'], fontName='Helvetica-Oblique', fontSize=6.8, leading=8.5, textColor=colors.HexColor("#4A5568"), spaceAfter=4)
    ))
    story.append(Spacer(1, 2))

    # Tabla 2: Consultas Estadísticas
    story.append(Paragraph("Tabla 2: Consultas Estadísticas de Rango (Algoritmo 4: AgregadoLE)", h2_style))
    raw_tbl2 = [
        [Paragraph("Escala N", tbl_hdr_style), Paragraph("Intervalo Evaluado", tbl_hdr_style), Paragraph("k Items", tbl_hdr_style), Paragraph("AVL Aumentado O(log D)", tbl_hdr_style), Paragraph("Fuerza Bruta O(N)", tbl_hdr_style), Paragraph("Factor Speedup", tbl_hdr_style)],
        [Paragraph("N = 1,000", tbl_cell_style), Paragraph("Puntaje Global [3.50, 3.80]", tbl_cell_style), Paragraph("358", tbl_cell_style), Paragraph("0.0253 µs (25 ns)", tbl_cell_bold), Paragraph("3.55 µs", tbl_cell_style), Paragraph("140.3x", tbl_cell_bold)],
        [Paragraph("N = 10,000", tbl_cell_style), Paragraph("Puntaje Global [3.50, 3.80]", tbl_cell_style), Paragraph("3,570", tbl_cell_style), Paragraph("0.0299 µs (30 ns)", tbl_cell_bold), Paragraph("39.84 µs", tbl_cell_style), Paragraph("1,331.7x", tbl_cell_bold)],
        [Paragraph("N = 50,000", tbl_cell_style), Paragraph("Puntaje Global [3.50, 3.80]", tbl_cell_style), Paragraph("17,896", tbl_cell_style), Paragraph("0.0273 µs (27 ns)", tbl_cell_bold), Paragraph("253.54 µs", tbl_cell_style), Paragraph("9,300.9x", tbl_cell_bold)],
        [Paragraph("N = 50,000", tbl_cell_style), Paragraph("Mirada Audiencia [0.60, 0.85]", tbl_cell_style), Paragraph("28,074", tbl_cell_style), Paragraph("0.0391 µs (39 ns)", tbl_cell_bold), Paragraph("220.13 µs", tbl_cell_style), Paragraph("5,629.8x", tbl_cell_bold)],
        [Paragraph("N = 50,000", tbl_cell_style), Paragraph("Volumen de Voz [0.65, 0.90]", tbl_cell_style), Paragraph("31,590", tbl_cell_style), Paragraph("0.0334 µs (33 ns)", tbl_cell_bold), Paragraph("182.15 µs", tbl_cell_style), Paragraph("5,453.6x", tbl_cell_bold)],
    ]
    t2 = Table(raw_tbl2, colWidths=[1.0*inch, 2.1*inch, 0.8*inch, 1.5*inch, 1.0*inch, 1.0*inch])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_hdr),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_zebra]),
        ('ALIGN', (2,1), (-1,-1), 'CENTER'),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
    ]))
    story.append(t2)
    story.append(Spacer(1, 4))

    # Tabla 3: Top-K
    story.append(Paragraph("Tabla 3: Selección Top-k de Expositores (Algoritmo 7: TopK)", h2_style))
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
        ('BACKGROUND', (0,0), (-1,0), c_hdr),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_zebra]),
        ('ALIGN', (2,1), (-1,-1), 'CENTER'),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
    ]))
    story.append(t3)
    story.append(Spacer(1, 4))

    # Tabla 4: MultiGet LevelDB
    story.append(Paragraph("Tabla 4: Materialización en Almacenamiento Persistente (LevelDB 1.23 + Filtros AMQ)", h2_style))
    raw_tbl4 = [
        [Paragraph("Escala N", tbl_hdr_style), Paragraph("Claves RQ", tbl_hdr_style), Paragraph("Sin Filtro (Baseline)", tbl_hdr_style), Paragraph("Bloom Filter (10 bpk)", tbl_hdr_style), Paragraph("Ribbon Filter (10 bpk equiv)", tbl_hdr_style), Paragraph("Ahorro AMQ", tbl_hdr_style)],
        [Paragraph("N = 1,000", tbl_cell_style), Paragraph("215 items", tbl_cell_style), Paragraph("3.298 µs / op", tbl_cell_style), Paragraph("2.712 µs / op", tbl_cell_style), Paragraph("2.698 µs / op", tbl_cell_bold), Paragraph("18.2% ahorro", tbl_cell_bold)],
        [Paragraph("N = 10,000", tbl_cell_style), Paragraph("2,146 items", tbl_cell_style), Paragraph("3.271 µs / op", tbl_cell_style), Paragraph("2.687 µs / op", tbl_cell_style), Paragraph("2.675 µs / op", tbl_cell_bold), Paragraph("18.2% ahorro", tbl_cell_bold)],
        [Paragraph("N = 50,000", tbl_cell_style), Paragraph("10,801 items", tbl_cell_style), Paragraph("2.282 µs / op", tbl_cell_style), Paragraph("2.292 µs / op", tbl_cell_style), Paragraph("2.324 µs / op", tbl_cell_style), Paragraph("Caché caliente", tbl_cell_style)],
        [Paragraph("Misses (1k)", tbl_cell_style), Paragraph("1,000 claves", tbl_cell_style), Paragraph("0.057 µs / op", tbl_cell_style), Paragraph("0.066 µs / op", tbl_cell_style), Paragraph("0.049 µs / op", tbl_cell_bold), Paragraph("Descarte veloz", tbl_cell_style)],
    ]
    t4 = Table(raw_tbl4, colWidths=[1.0*inch, 1.0*inch, 1.4*inch, 1.4*inch, 1.5*inch, 1.1*inch])
    t4.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_hdr),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_zebra]),
        ('ALIGN', (2,1), (-1,-1), 'CENTER'),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
    ]))
    story.append(t4)
    story.append(Spacer(1, 5))

    # =========================================================================
    # SECCIÓN 5: ANÁLISIS CRÍTICO - FORTALEZAS Y DEBILIDADES
    # =========================================================================
    story.append(Paragraph("5. Análisis Crítico: Fortalezas de la Propuesta", h1_style))
    story.append(Paragraph(
        "<b>1. Invarianza Temporal Asintótica:</b> La mayor fortaleza es la estabilidad de <code>AgregadoLE</code> con costo <b><i>O(log D<sub>m</sub>)</i></b> "
        "en el peor caso. Las mediciones de microbenchmark muestran tiempos del orden de ~25 a 30 nanosegundos tanto para <i>N = 1,000</i> como para "
        "<i>N = 50,000</i>, incluso cuando el intervalo engloba más de 17,800 informes. Al eliminar la dependencia de la cantidad de elementos seleccionados (<i>k</i>), "
        "la aceleración sobre el barrido secuencial supera <b>9,300x</b>.<br/>"
        "<b>2. Desacoplamiento y Poda Selectiva de E/S (2,146 / 10,000):</b> En una consulta por notas en <i>[4.00, 4.50]</i> sobre 10,000 reportes, "
        "el índice en RAM determina que solo 2,146 cumplen la condición. El almacenamiento secundario ejecuta <code>MultiGet</code> únicamente sobre ellos, "
        "<b>evitando consultar 7,854 reportes que no pertenecen al resultado</b> sobre el almacenamiento persistente.<br/>"
        "<b>3. Aceleración con Filtros AMQ Modernos (Ribbon vs. Bloom):</b> En las escalas de 1,000 y 10,000 reportes se observó una reducción aproximada "
        "del <b>18.2%</b> frente al baseline sin filtro; con 50,000 reportes y caché caliente la ventaja desapareció (~2.3 µs/op), evidenciando que el beneficio "
        "de los filtros depende del patrón de acceso y del estado de la caché del SO. La implementación personalizada de <b>Ribbon Filter</b> mediante "
        "la interfaz extensible <i>FilterPolicy</i> de LevelDB igualó la velocidad de Bloom (2.675 µs vs 2.687 µs) con un 30% menos sobrecosto de bits teórico.<br/>"
        "<b>4. Poda Temprana en Consultas Compuestas:</b> Ordenar los predicados por cardinalidad creciente minimiza el tamaño de los conjuntos intermedios "
        "desde el primer paso, permitiendo abortar la evaluación inmediatamente si la intersección se vacía.", body_style
    ))

    story.append(Paragraph("6. Análisis Crítico: Debilidades y Desafíos Arquitectónicos", h1_style))
    story.append(Paragraph(
        "A pesar de sus ventajas algorítmicas, se identificaron cuatro limitaciones operativas fundamentales:<br/>"
        "<b>1. Concurrencia y Replicación de Índices en Memoria:</b><br/>"
        "Aunque la complejidad individual de las consultas permanece baja, múltiples consultas e inserciones concurrentes en un servidor "
        "requieren políticas de sincronización sobre los árboles AVL (cerrojos de lectura/escritura), lo que induce contención bajo alta concurrencia. "
        "En una arquitectura distribuida, además, cada réplica debe mantener una versión consistente de los índices secundarios en RAM, "
        "por lo que la escalabilidad horizontal introduce costos significativos de coordinación y replicación.<br/>"
        "<b>2. Sobrecarga de Memoria Principal (RAM):</b><br/>"
        "Mantener cuatro índices residentes en memoria implica almacenar <i>O(M · N)</i> referencias y punteros de nodos. Para cientos de miles de informes, "
        "la huella en RAM puede limitar entornos con recursos acotados, requiriendo esquemas de paginación o particionamiento.<br/>"
        "<b>3. Costo de Rebalanceo en Ingesta Continua:</b><br/>"
        "Cada informe nuevo exige actualizar los cuatro AVL. Las rotaciones y el recálculo ascendente de <i>(C, S, SS)</i> (~0.25 µs/informe) imponen "
        "un límite superior a la tasa de ingesta en comparación con motores LSM <i>append-only</i> puros.<br/>"
        "<b>4. Influencia de la Discretización de Claves:</b><br/>"
        "El excelente comportamiento temporal observado no depende únicamente del balance AVL, sino también de la baja cardinalidad del dominio "
        "discretizado (con redondeo a 2 decimales, <i>D<sub>m</sub> ≤ 401</i> claves distintas, <i>h ≤ 11</i>, agrupando múltiples reportes en las listas "
        "<i>L<sub>x</sub></i> de cada nodo). Si se utilizara punto flotante de 64 bits sin discretizar, <i>D<sub>m</sub> ≈ N</i>, aumentando la altura "
        "del árbol, la cantidad de nodos independientes y la fragmentación en el heap.", body_style
    ))

    # =========================================================================
    # SECCIÓN 7: COMPARATIVA CON ESQUEMA BASE SIN ÍNDICES SECUNDARIOS
    # =========================================================================
    story.append(PageBreak())
    story.append(Paragraph("7. Comparación con un Esquema Base sin Indexación Secundaria", h1_style))
    story.append(Paragraph(
        "El siguiente cuadro contrasta las características operativas de un esquema base sin indexación secundaria (almacenamiento plano y barrido lineal) "
        "frente a la arquitectura propuesta con índices aumentados y almacenamiento LSM:", body_style
    ))

    raw_tbl5 = [
        [Paragraph("Dimensión de Análisis", tbl_hdr_style), Paragraph("Esquema Base sin Índices Secundarios", tbl_hdr_style), Paragraph("Propuesta con Estructura Aumentada + LSM", tbl_hdr_style)],
        [
            Paragraph("<b>Almacenamiento</b>", tbl_cell_bold),
            Paragraph("Pasivo: Informes almacenados en archivos planos o tablas relacionales sin índices secundarios multidimensionales.", tbl_cell_style),
            Paragraph("Desacoplado y Activo: Índices secundarios en RAM sincronizados con LevelDB LSM persistente.", tbl_cell_style)
        ],
        [
            Paragraph("<b>Estadísticas de Cohorte</b>", tbl_cell_bold),
            Paragraph("Fuerza Bruta <i>O(N)</i>: Escanea toda la colección para calcular media y varianza.", tbl_cell_style),
            Paragraph("Aumentación <i>O(log D<sub>m</sub>)</i>: Cálculo en decenas de nanosegundos mediante resta de prefijos sin recorrer datos.", tbl_cell_style)
        ],
        [
            Paragraph("<b>Selección Top-K</b>", tbl_cell_bold),
            Paragraph("Fuerza Bruta con min-heap <i>O(N log k)</i>: Costoso al acumular grandes volúmenes <i>N</i>.", tbl_cell_style),
            Paragraph("Poda en AVL <i>O(log D<sub>m</sub> + k)</i>: 0.13 µs en microbenchmark (440x más rápido que Fuerza Bruta para k=10).", tbl_cell_style)
        ],
        [
            Paragraph("<b>Consultas Multi-Criterio</b>", tbl_cell_bold),
            Paragraph("Barrido secuencial multi-filtro con degradación lineal proporcional a <i>N</i>.", tbl_cell_style),
            Paragraph("Intersección por cardinalidad creciente con salida temprana.", tbl_cell_style)
        ],
        [
            Paragraph("<b>Escalabilidad</b>", tbl_cell_bold),
            Paragraph("Acotado a procesamiento en lotes pequeños por aula académica.", tbl_cell_style),
            Paragraph("Escala de Campus: Diseñado para analítica en tiempo real sobre decenas de miles de reportes.", tbl_cell_style)
        ],
        [
            Paragraph("<b>Eficiencia de E/S</b>", tbl_cell_bold),
            Paragraph("Sin filtros probabilísticos: lecturas innecesarias para descartar reportes no coincidentes.", tbl_cell_style),
            Paragraph("Filtros Ribbon y Bloom en LevelDB: hasta 18% menos latencia en hits y descarte casi instantáneo en misses.", tbl_cell_style)
        ]
    ]
    t5 = Table(raw_tbl5, colWidths=[1.5*inch, 2.9*inch, 3.0*inch])
    t5.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_hdr),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_zebra]),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
    ]))
    story.append(t5)
    story.append(Spacer(1, 5))

    # =========================================================================
    # SECCIÓN 8: CONCLUSIONES Y REFERENCIAS
    # =========================================================================
    story.append(Paragraph("8. Conclusiones", h1_style))
    story.append(Paragraph(
        "<b>1. Validación Empírica:</b> Las mediciones de microbenchmark muestran tiempos del orden de decenas de nanosegundos consistentes "
        "con las cotas <i>O(log D<sub>m</sub>)</i> deducidas formalmente: la aumentación transforma cálculos agregados en operaciones de costo "
        "logarítmico en el peor caso (aceleración de hasta <b>9,300x</b> frente al barrido lineal).<br/>"
        "<b>2. Viabilidad Analítica:</b> Los resultados indican que la arquitectura propuesta es adecuada como base para consultas analíticas "
        "interactivas sobre colecciones de decenas de miles de reportes, aunque su comportamiento bajo concurrencia pesada y despliegues "
        "distribuidos requiere evaluación adicional.<br/>"
        "<b>3. Balance Arquitectónico:</b> El beneficio de la aceleración analítica debe sopesarse con el consumo de memoria RAM para los índices "
        "residentes, la sincronización requerida en entornos multi-hilo y la sensibilidad a la discretización de las métricas numéricas.", body_style
    ))

    story.append(Paragraph("Referencias Bibliográficas", h2_style))
    story.append(Paragraph(
        "<font size=6.8 color='#4A5568'>"
        "[1] X. Ochoa et al., “The RAP system: Automatic feedback of oral presentation skills using multimodal analysis and low-cost sensors,” in <i>Proc. LAK ’18</i>. ACM, 2018.<br/>"
        "[2] T. H. Cormen, C. E. Leiserson, R. L. Rivest, and C. Stein, <i>Introduction to Algorithms</i>, 4th ed. MIT Press, 2022.<br/>"
        "[3] G. M. Adelson-Velsky and E. M. Landis, “An algorithm for the organization of information,” <i>Soviet Math. Doklady</i>, 1962.<br/>"
        "[4] P. C. Dillinger and S. Walzer, “Ribbon filter: Practically smaller than bloom and xor,” <i>CoRR</i>, vol. abs/2103.02515, 2021.<br/>"
        "[5] P. E. O’Neil, E. Cheng, D. Gawlick, and E. J. O’Neil, “The log-structured merge-tree (LSM-tree),” <i>Acta Informatica</i>, 1996."
        "</font>", body_style
    ))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[✓] PDF generado exitosamente en: {output_path}")

def main():
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    output_pdf = os.path.join(root_dir, "Informe_Evaluacion_Algoritmos_RAP.pdf")

    if len(sys.argv) > 1:
        output_pdf = sys.argv[1]

    build_pdf(output_pdf)

if __name__ == "__main__":
    main()
