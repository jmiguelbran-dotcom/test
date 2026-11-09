#!/usr/bin/env python3
"""
Módulo: log_analyzer.py
Actividad: IA como Herramienta, no como Autor: Desarrollo Guiado y Validado de un Script en Python
Bootcamp: AI for Devs Jr. - KODIGO

Descripción:
Script modular que procesa y audita archivos de logs de aplicaciones.
Extrae niveles de severidad (INFO, WARNING, ERROR), valida marcas de tiempo
y contabiliza inconsistencias o líneas vacías aplicando criterio de negocio humano.
"""

import os
import re
from datetime import datetime

# ==============================================================================
# DECISIÓN DEL DESARROLLADOR: Constantes y Expresiones Regulares
# ==============================================================================
# Nota técnica: La IA inicialmente propuso una única expresión regular monolítica y estricta
# que exigía la fecha en formato YYYY-MM-DD. Como decisión de diseño humano, se separó la
# extracción de severidad de la extracción de fecha para no descartar eventos válidos
# que carecieran de marca temporal.

NIVELES_PERMITIDOS = {"INFO", "WARNING", "ERROR"}

# Patrón flexible para capturar el nivel de severidad al inicio o rodeado por corchetes
REGEX_SEVERIDAD = re.compile(r"\[(INFO|WARNING|ERROR)\]", re.IGNORECASE)

# Patrón para identificar marcas de tiempo estándar ISO (YYYY-MM-DD)
REGEX_FECHA = re.compile(r"\b(\d{4}-\d{2}-\d{2})\b")


def validar_fecha(fecha_str: str) -> bool:
    """
    Valida si una cadena de texto corresponde a una fecha del calendario real.
    
    Decisión humana: La regex solo valida el formato numérico (\d{4}-\d{2}-\d{2}),
    pero no la validez cronológica (ej. 2025-02-31 o mes 13). Se utiliza datetime.strptime
    para garantizar integridad del dato real.
    """
    try:
        datetime.strptime(fecha_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def analizar_linea(linea: str, metricas: dict) -> None:
    """
    Analiza una sola línea de log y actualiza el diccionario acumulador de métricas.
    
    Reglas de negocio aplicadas:
    1. Líneas en blanco: Se ignoran operativamente, pero se contabilizan como línea vacía.
    2. Severidad: Si existe [INFO], [WARNING] o [ERROR], se clasifica en su categoría.
    3. Validación de fecha: Si tiene fecha válida, continúa. Si no tiene fecha o está
       mal construida, se computa en 'incompletas_sin_fecha' sin perder el conteo de severidad.
    4. Formato corrupto: Si ni siquiera cuenta con un nivel de severidad reconocido,
       se marca como 'lineas_mal_formateadas'.
    """
    # Caso borde: Líneas vacías o solo con espacios en blanco
    if not linea.strip():
        metricas["lineas_blancas"] += 1
        return

    # Toda línea no vacía se registra como intento de evento procesado
    metricas["total_eventos"] += 1

    # 1. Detección de Severidad
    match_severidad = REGEX_SEVERIDAD.search(linea)
    if not match_severidad:
        # La línea tiene texto pero carece del formato mínimo identificable [SEVERIDAD]
        metricas["lineas_mal_formateadas"] += 1
        return

    nivel = match_severidad.group(1).upper()
    metricas["conteo_severidad"][nivel] += 1

    # 2. Detección y Validación de Marca Temporal (Fecha)
    match_fecha = REGEX_FECHA.search(linea)
    if match_fecha:
        fecha_candidata = match_fecha.group(1)
        if not validar_fecha(fecha_candidata):
            # La regex detectó números con forma de fecha pero calendario inválido
            metricas["incompletas_sin_fecha"] += 1
    else:
        # La línea tiene severidad reconocida pero carece por completo de fecha válida
        metricas["incompletas_sin_fecha"] += 1


def procesar_archivo(ruta_archivo: str) -> dict:
    """
    Lee un archivo línea por línea de manera eficiente y retorna el resumen computado.
    Gestiona excepciones del sistema operativo (archivo no encontrado o sin permisos).
    """
    metricas = {
        "total_eventos": 0,
        "conteo_severidad": {"INFO": 0, "WARNING": 0, "ERROR": 0},
        "incompletas_sin_fecha": 0,
        "lineas_mal_formateadas": 0,
        "lineas_blancas": 0,
    }

    # Control estricto de excepciones de I/O
    try:
        with open(ruta_archivo, mode="r", encoding="utf-8") as archivo:
            for linea in archivo:
                # Se eliminan los saltos de línea finales conservando el cuerpo del registro
                analizar_linea(linea.rstrip("\r\n"), metricas)
    except FileNotFoundError:
        print(f"\n[ERROR CRÍTICO] El archivo '{ruta_archivo}' no existe o la ruta es incorrecta.")
        return None
    except PermissionError:
        print(f"\n[ERROR CRÍTICO] Permiso denegado para leer el archivo '{ruta_archivo}'.")
        return None
    except UnicodeDecodeError:
        print(f"\n[ERROR CRÍTICO] El archivo '{ruta_archivo}' no tiene codificación UTF-8 válida.")
        return None
    except Exception as error_inesperado:
        print(f"\n[ERROR CRÍTICO] Ocurrió un error inesperado al leer el archivo: {error_inesperado}")
        return None

    return metricas


def mostrar_resumen(ruta_archivo: str, metricas: dict) -> None:
    """
    Imprime en consola un informe visual formateado y legible con los resultados del análisis.
    """
    nombre_archivo = os.path.basename(ruta_archivo)
    print("\n" + "=" * 60)
    print(f" RESUMEN DE AUDITORÍA DE LOGS: {nombre_archivo}")
    print("=" * 60)
    print(f" Total de eventos leídos (no vacíos) : {metricas['total_eventos']}")
    print("-" * 60)
    print(" Distribución por Nivel de Severidad:")
    print(f"   • [INFO]    : {metricas['conteo_severidad']['INFO']}")
    print(f"   • [WARNING] : {metricas['conteo_severidad']['WARNING']}")
    print(f"   • [ERROR]   : {metricas['conteo_severidad']['ERROR']}")
    print("-" * 60)
    print(" Calidad y Consistencia de los Registros:")
    print(f"   • Registros sin fecha válida/incompletos : {metricas['incompletas_sin_fecha']}")
    print(f"   • Líneas mal formateadas (sin severidad) : {metricas['lineas_mal_formateadas']}")
    print(f"   • Líneas en blanco (sin datos)          : {metricas['lineas_blancas']}")
    print("=" * 60 + "\n")


def main() -> None:
    """
    Punto de entrada interactivo para el usuario mediante consola/terminal.
    """
    print("\n--- ANALIZADOR DE ARCHIVOS DE LOGS (KODIGO - AI FOR DEVS) ---")
    ruta = input("Ingrese la ruta del archivo de logs que desea analizar: ").strip()

    if not ruta:
        print("[AVISO] No se proporcionó ninguna ruta de archivo. Finalizando ejecución.")
        return

    # Si el usuario introdujo la ruta entre comillas accidentales, las limpiamos
    ruta_limpia = ruta.strip("\"'")

    resultados = procesar_archivo(ruta_limpia)
    if resultados is not None:
        mostrar_resumen(ruta_limpia, resultados)


if __name__ == "__main__":
    main()