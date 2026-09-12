#!/usr/bin/env python3
"""
Generador de Reportes Sintéticos para el Sistema RAP (ESPOL)
Basado en: Ochoa et al., 2018 - The RAP System: Automatic feedback of oral presentation skills.
Genera reportes ri = (id_i, u_i, t_i, M_i, D_i) con M_i = (g, z, v, p) y payload D_i en JSON.
"""

import argparse
import datetime
import json
import os
import random

def clamp(val, low, high):
    return max(low, min(high, val))

def generate_report(i, num_students=1000):
    report_id = f"RAP-2024-{i+1:06d}"
    student_id = f"EST-{random.randint(1, num_students):05d}"
    
    # Simulación de fechas a lo largo de un semestre académico
    base_date = datetime.datetime(2024, 5, 2, 8, 0, 0)
    time_offset = datetime.timedelta(
        days=random.randint(0, 110),
        hours=random.randint(0, 10),
        minutes=random.randint(0, 59),
        seconds=random.randint(0, 59)
    )
    timestamp = (base_date + time_offset).isoformat()
    
    # 1. Mirada hacia la audiencia (z): Gaze ratio [0.0, 1.0]
    z = clamp(random.gauss(0.65, 0.15), 0.10, 0.98)
    
    # 2. Volumen de voz (v): Audio clarity / Volume level [0.0, 1.0]
    v = clamp(random.gauss(0.70, 0.12), 0.15, 0.99)
    
    # 3. Postura corporal (p): Posture stability [0.0, 1.0]
    p = clamp(random.gauss(0.72, 0.14), 0.10, 0.99)
    
    # 4. Puntaje Global (g): Combinación ponderada + factor de desempeño general [1.0, 5.0]
    # RAP pondera las modalidades y genera una nota de 1.0 a 5.0
    combined_score = 0.35 * z + 0.35 * v + 0.30 * p
    noise = random.gauss(0, 0.05)
    g = clamp(1.0 + 4.0 * combined_score + noise, 1.0, 5.0)
    
    # Redondeo para reflejar la resolución del sensor/evaluación RAP
    # Genera grupos de reportes con el mismo puntaje exacto (lista Lx en el AVL)
    g = round(g, 2)
    z = round(z, 2)
    v = round(v, 2)
    p = round(p, 2)
    
    # 5. Payload detallado D_i (simula el reporte completo de RAP para almacenamiento en KV)
    num_slides = random.randint(6, 25)
    filler_pauses = random.randint(2, 28)
    speech_rate_wpm = round(random.gauss(130, 20), 1)
    
    detailed_payload = {
        "report_id": report_id,
        "presenter": student_id,
        "session_date": timestamp,
        "metrics_summary": {
            "global_score": g,
            "gaze_score": z,
            "volume_score": v,
            "posture_score": p
        },
        "multimodal_analysis": {
            "slides_analysis": {
                "total_slides": num_slides,
                "avg_seconds_per_slide": round(random.uniform(25.0, 75.0), 2),
                "text_density_warning": random.random() < 0.25
            },
            "audio_analysis": {
                "words_per_minute": speech_rate_wpm,
                "filler_words_count": filler_pauses,
                "detected_filler_tokens": random.sample(["eh", "este", "o sea", "bueno", "em"], k=min(3, filler_pauses)),
                "silence_ratio": round(random.uniform(0.05, 0.22), 3),
                "avg_pitch_hz": round(random.gauss(175, 30), 1)
            },
            "video_analysis": {
                "eye_contact_percentage": round(z * 100, 1),
                "excessive_movement_flags": random.randint(0, 5),
                "arms_crossed_duration_sec": round(random.uniform(0.0, 45.0), 1),
                "hand_gestures_activity_level": random.choice(["Bajo", "Moderado", "Adecuado", "Excesivo"])
            }
        },
        "feedback_recommendations": [
            "Mantener mayor contacto visual con los laterales del auditorio." if z < 0.60 else "Buen contacto visual sostenido.",
            "Modular el volumen de voz en momentos de énfasis temático." if v < 0.65 else "Nivel de volumen y proyección adecuados.",
            "Reducir el uso de muletillas de relleno ('este', 'eh')." if filler_pauses > 12 else "Ritmo y fluidez verbal controlados."
        ]
    }
    
    payload_str = json.dumps(detailed_payload)
    
    return {
        "id": report_id,
        "user_id": student_id,
        "timestamp": timestamp,
        "g": g,
        "z": z,
        "v": v,
        "p": p,
        "payload": payload_str
    }

def main():
    parser = argparse.ArgumentParser(description="Generador de reportes sintéticos RAP ESPOL")
    parser.add_argument("--n", type=int, default=10000, help="Cantidad de informes a generar (default: 10000)")
    parser.add_argument("--output", type=str, default="Evaluacion_AA_Pruebas/data/rap_reports_10k.jsonl", help="Ruta del archivo de salida")
    parser.add_argument("--seed", type=int, default=42, help="Semilla para reproducibilidad experimental")
    args = parser.parse_args()
    
    random.seed(args.seed)
    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    
    print(f"[*] Generando {args.n} reportes sintéticos RAP ESPOL...")
    total_bytes = 0
    with open(args.output, "w", encoding="utf-8") as f:
        for i in range(args.n):
            rep = generate_report(i)
            line = json.dumps(rep)
            f.write(line + "\n")
            total_bytes += len(line.encode("utf-8"))
            if (i + 1) % 2500 == 0 or (i + 1) == args.n:
                print(f"    - {i + 1}/{args.n} reportes generados...")
                
    mb = total_bytes / (1024 * 1024)
    print(f"[✓] Dataset generado exitosamente en: {args.output}")
    print(f"[✓] Total reportes: {args.n} | Tamaño aproximado: {mb:.2f} MB (~{total_bytes // args.n} bytes/informe)")

if __name__ == "__main__":
    main()
