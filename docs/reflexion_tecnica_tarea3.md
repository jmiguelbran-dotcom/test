DOCUMENTO DE REFLEXIÓN TÉCNICA

Actividad: IA como Herramienta, no como Autor: Desarrollo Guiado y Validado de un Script en Python


Módulo / Enfoque: Semana 3 – IA-first mindset (Supervisión Humana y Validación)

Estudiante: JUAN BRAN

Comentarios adicionales: Quiero ser sincero y me cuesta mucho lo de GITHUB. HE tratado de hacer lo mejor posible, pero si algo no funciona, favor decirmelo.

Script asociado: log_analyzer.py

1. Desglose del Desarrollo: Asistencia de IA vs. Criterio Humano

En el desarrollo de este analizador de registros de eventos (logs), la Inteligencia Artificial generativa fue empleada como un asistente de aceleración técnica y consulta sintáctica, manteniendo el control de la lógica de negocio y las decisiones arquitectónicas bajo estricta supervisión humana.

1.1. Partes del código sugeridas o apoyadas por IA

Construcción preliminar de Expresiones Regulares (regex): Se consultó a la IA para obtener patrones que identificaran etiquetas en corchetes ([INFO|WARNING|ERROR]) y secuencias numéricas de fechas ISO (\d{4}-\d{2}-\d{2}).

Estructura base de funciones (Boilerplate): La IA generó la plantilla de cabecera de las funciones, los bloques try/except estándar y la estructura del diccionario acumulador de métricas.

Formato visual de salida en consola: Apoyo en el diseño estético de la función mostrar_resumen(), empleando separadores de caracteres para mejorar la legibilidad de las métricas.

1.2. Partes que correspondieron a decisiones exclusivas del estudiante (Criterio Humano)

Definición de las reglas de clasificación: Determinar que un registro como [WARNING] Invalid password attempt no debía descartarse ni categorizarse como error total, sino contabilizarse dentro de los WARNING, sumando simultáneamente un aviso al contador de registros sin fecha o incompletos.

Tratamiento de casos borde (Edge Cases):

Decidir deliberadamente que las líneas vacías o compuestas exclusivamente por espacios en blanco no deben inflar el total de eventos leídos, sino contabilizarse en una categoría separada de auditoría (lineas_blancas).

Diseñar la captura interactiva vía input() con sanitización de comillas accidentales y rutas con espacios.

Control de errores de E/S (I/O): Implementar el manejo diferenciado de excepciones con mensajes contextualizados para FileNotFoundError, PermissionError y UnicodeDecodeError, evitando que el script falle abruptamente ante fallos del sistema de archivos.

2. Ejemplo Concreto: Detección y Corrección de Sugerencias de la IA

2.1. Propuesta inicial errónea/incompleta de la IA

Durante la primera iteración, la IA sugirió una única expresión regular monolítica para procesar la línea completa de un solo paso:

# Sugerencia inicial generada por la IA:
PATRON_LOG_IA = re.compile(r"^\[(?P<nivel>INFO|WARNING|ERROR)\]\s+(?P<fecha>\d{4}-\d{2}-\d{2})\s+(?P<mensaje>.*)$")


Problemas detectados por el estudiante:

Fragilidad ante líneas sin fecha: La expresión regular exigía obligatoriamente la fecha después del nivel de severidad. Cuando se le pasaba el ejemplo de la guía [WARNING] Invalid password attempt, el patrón fallaba por completo, provocando que la línea se catalogara falsamente como "línea corrupta", perdiendo el conteo del WARNING.

Falsa validación de calendarios: La expresión regular aceptaba fechas sintácticamente numéricas pero humanamente imposibles (por ejemplo, 2025-02-31 o mes 2025-99-99), validándolas como correctas.

Rigidez ante caracteres previos: Si la línea contenía un carácter de viñeta inicial (como · [INFO]...), la regex fallaba por culpa del delimitador de inicio de línea ^.

2.2. Corrección implementada por el estudiante

Se descartó la regex única y se rediseñó el pipeline de análisis en fases independientes:

Desacoplamiento de severidad y fecha: Se crearon dos expresiones regulares independientes (REGEX_SEVERIDAD y REGEX_FECHA). Esto permite extraer el nivel de severidad aunque la fecha no esté presente.

Validación real con el módulo datetime: En lugar de confiar ciegamente en una regex para la fecha, se introdujo la función validar_fecha() utilizando datetime.strptime(fecha_str, "%Y-%m-%d"), garantizando que fechas como el 31 de febrero o meses inexistentes sean capturadas como inconsistencias cronológicas:

def validar_fecha(fecha_str: str) -> bool:
    try:
        datetime.strptime(fecha_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False


3. Evidencia de Pruebas y Resultados Obtenidos

Para certificar el correcto funcionamiento del script y el cumplimiento de las decisiones de negocio, se diseñaron y ejecutaron dos archivos de prueba representativos:

3.1. Prueba 1: Archivo bien formado (logs_validos.log)

Contenido: 10 eventos estructurados con severidades (INFO, WARNING, ERROR), marcas temporales válidas en formato YYYY-MM-DD y mensajes claros.

Resultados esperados:

Total eventos: 10

INFO: 6 | WARNING: 2 | ERROR: 2

Sin fecha/incompletas: 0

Mal formateadas: 0

Líneas en blanco: 0

Resultados obtenidos (Salida real de consola):

============================================================
 RESUMEN DE AUDITORÍA DE LOGS: logs_validos.log
============================================================
 Total de eventos leídos (no vacíos) : 10
------------------------------------------------------------
 Distribución por Nivel de Severidad:
   • [INFO]    : 6
   • [WARNING] : 2
   • [ERROR]   : 2
------------------------------------------------------------
 Calidad y Consistencia de los Registros:
   • Registros sin fecha válida/incompletos : 0
   • Líneas mal formateadas (sin severidad) : 0
   • Líneas en blanco (sin datos)          : 0
============================================================


Conclusión: El script reconoció la totalidad de los datos estructurados sin falsos positivos.

3.2. Prueba 2: Archivo con inconsistencias y casos borde (logs_con_errores.log)

Contenido analizado:

Líneas con fecha válida y formato correcto (2 eventos).

Líneas con severidad pero sin fecha (2 eventos: [WARNING] y [WARNING] Session timeout...).

Líneas con fechas imposibles (2025-02-31 y 2025-99-99).

Líneas vacías y con espacios en blanco (3 líneas).

Línea con viñeta inicial pero severidad y fecha válidas (· [INFO] 2025-01-15...).

Líneas corruptas sin ningún formato identificable (2 eventos de basura textual).

Resultados esperados:

Total de eventos (no vacíos): 9

INFO: 3 | WARNING: 2 | ERROR: 2

Registros sin fecha o con fecha inválida: 4

Líneas mal formateadas: 2

Líneas en blanco ignoradas: 3

Resultados obtenidos (Salida real de consola):

============================================================
 RESUMEN DE AUDITORÍA DE LOGS: logs_con_errores.log
============================================================
 Total de eventos leídos (no vacíos) : 9
------------------------------------------------------------
 Distribución por Nivel de Severidad:
   • [INFO]    : 3
   • [WARNING] : 2
   • [ERROR]   : 2
------------------------------------------------------------
 Calidad y Consistencia de los Registros:
   • Registros sin fecha válida/incompletos : 4
   • Líneas mal formateadas (sin severidad) : 2
   • Líneas en blanco (sin datos)          : 3
============================================================


Conclusión: Las reglas de negocio se aplicaron con exactitud. Las fechas imposibles y las líneas sin marca temporal se reflejaron en la métrica de inconsistencias sin perder el conteo de severidad del evento.

4. Aprendizajes: La IA como Herramienta y no como Reemplazo

El desarrollo de esta actividad permitió constatar que la Inteligencia Artificial actúa eficazmente como un acelerador de código inicial, pero es incapaz de sustituir el razonamiento crítico del desarrollador:

La IA desconoce la intención de negocio sin directivas humanas: Un modelo de lenguaje sugiere soluciones sintácticamente elegantes basadas en el promedio de su entrenamiento (como una regex rígida), pero no comprende las consecuencias de descartar un registro de advertencia (WARNING) que carece de fecha en un entorno real de auditoría.

El peligro de la complacencia técnica: Si el estudiante copia y pega las soluciones de la IA sin verificarlas contra casos de prueba exhaustivos, introduce bugs sutiles (como aceptar el 31 de febrero como fecha válida) que solo se hacen visibles en producción.

El rol del desarrollador como auditor: El valor fundamental del desarrollador moderno no reside en memorizar la sintaxis de expresiones regulares o librerías estándar, sino en diseñar las pruebas, establecer los criterios de tolerancia a fallos y validar que el software se comporte de acuerdo con las especificaciones éticas y técnicas esperadas.