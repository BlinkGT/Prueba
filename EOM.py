import streamlit as st
import math
import base64
import json
import hashlib
from datetime import datetime

# --- Constantes ---
GRAVEDAD = 9.8
TOLERANCIA = 0.05 # Tolerancia de +/- 0.05 para las respuestas

# --- Funciones Auxiliares ---

def redondear_a_2_decimales(numero):
    """
    Redondea un número a 2 decimales y lo formatea como un float con dos decimales.
    Si es None, inf, o nan, devuelve None.
    """
    if numero is None or math.isinf(numero) or math.isnan(numero):
        return None
    return float(f"{numero:.2f}")

def calcular_respuestas(clave):
    """Calcula las respuestas correctas para cada pregunta basándose en la clave."""
    respuestas = {}
    
    if not isinstance(clave, (int, float)) or clave <= 0:
        for i in range(1, 11):
            respuestas[f'pregunta{i}'] = None
        return respuestas

    # Pregunta 1: t=sqrt("clave"/4.9)
    respuestas['pregunta1'] = redondear_a_2_decimales(math.sqrt(clave / (GRAVEDAD / 2)))

    # Pregunta 2: v=sqrt(2*9.8*"clave")
    respuestas['pregunta2'] = redondear_a_2_decimales(math.sqrt(2 * GRAVEDAD * clave))

    # Pregunta 3: t="clave"/9.8
    respuestas['pregunta3'] = redondear_a_2_decimales(clave / GRAVEDAD)

    # Pregunta 4: t=2*"clave"/9.8
    respuestas['pregunta4'] = redondear_a_2_decimales(2 * clave / GRAVEDAD)
    
    # Pregunta 5: La respuesta es el mismo valor de "clave"
    respuestas['pregunta5'] = redondear_a_2_decimales(float(clave))

    # Pregunta 6: v= sqrt("clave"^2 + 2*9.8*100)
    altura_p6 = 100.0
    respuestas['pregunta6'] = redondear_a_2_decimales(math.sqrt(clave**2 + 2 * GRAVEDAD * altura_p6))

    # Pregunta 7: t=[sqrt("clave"^2 + 2*9.8*100)-"clave"]/9.8
    velocidad_final_p7_calc = math.sqrt(clave**2 + 2 * GRAVEDAD * altura_p6)
    respuestas['pregunta7'] = redondear_a_2_decimales((velocidad_final_p7_calc - clave) / GRAVEDAD)

    # Pregunta 8: h=1/2*9.8*"clave"^2
    respuestas['pregunta8'] = redondear_a_2_decimales(0.5 * GRAVEDAD * clave**2)

    # Pregunta 9: t=sqrt("clave"/9.8)
    respuestas['pregunta9'] = redondear_a_2_decimales(math.sqrt(clave / GRAVEDAD))

    # Pregunta 10: t=sqrt("clave"/4.9) - sqrt("clave"/9.8)
    t_total_p10 = math.sqrt(clave / (GRAVEDAD / 2))
    t_primera_mitad_p10 = math.sqrt(clave / GRAVEDAD)
    respuestas['pregunta10'] = redondear_a_2_decimales(t_total_p10 - t_primera_mitad_p10)

    return respuestas

def codificar_calificacion(datos_calificacion):
    json_data = json.dumps(datos_calificacion)
    encoded_data = base64.b64encode(json_data.encode('utf-8')).decode('utf-8')
    return encoded_data

# --- Lógica de la Aplicación Streamlit ---

st.title("Programa de Examen de Física")

# Inicialización de session_state (es crucial para mantener el estado entre interacciones)
if 'nombre_alumno' not in st.session_state:
    st.session_state.nombre_alumno = ""
if 'clave_alumno' not in st.session_state:
    st.session_state.clave_alumno = None
if 'preguntas_list' not in st.session_state:
    st.session_state.preguntas_list = []
if 'respuestas_estudiante_guardadas' not in st.session_state:
    st.session_state.respuestas_estudiante_guardadas = []
if 'pregunta_actual_idx' not in st.session_state:
    st.session_state.pregunta_actual_idx = 0
if 'examen_iniciado' not in st.session_state:
    st.session_state.examen_iniciado = False
if 'examen_finalizado' not in st.session_state:
    st.session_state.examen_finalizado = False
if 'respuestas_correctas_calc' not in st.session_state: # Para almacenar las respuestas calculadas
    st.session_state.respuestas_correctas_calc = {}
if 'final_dat_content' not in st.session_state: # Para almacenar el contenido del .dat para descarga
    st.session_state.final_dat_content = None
if 'final_filename' not in st.session_state:
    st.session_state.final_filename = None


# --- Pantalla de Inicio ---
if not st.session_state.examen_iniciado:
    st.write("¡Bienvenido al examen de física!")
    nombre_input = st.text_input("Por favor, ingresa tu nombre completo:", key="nombre_entrada")
    clave_input = st.text_input("Ingresa tu número de clave (un entero POSITIVO):", type="password", key="clave_entrada")

    if st.button("Iniciar Examen"):
        if not nombre_input:
            st.error("Por favor, ingresa tu nombre.")
        else:
            try:
                clave = int(clave_input)
                if clave <= 0:
                    st.error("La clave debe ser un número entero POSITIVO.")
                else:
                    st.session_state.nombre_alumno = nombre_input
                    st.session_state.clave_alumno = clave
                    st.session_state.examen_iniciado = True
                    st.session_state.respuestas_correctas_calc = calcular_respuestas(clave)
                    st.session_state.preguntas_list = [
                        f"Se deja caer un objeto desde {clave} m. Encuentre su tiempo de caída en s. (2 decimales)",
                        f"Se deja caer un objeto desde {clave} m. Encuentre su velocidad final en m/s. (2 decimales)",
                        f"Se lanza un objeto hacia arriba con velocidad de {clave} m/s. Encuentre su tiempo de subida en s. (2 decimales)",
                        f"Se lanza un objeto hacia arriba con velocidad de {clave} m/s. Encuentre su tiempo de vuelo total en s. (2 decimales)",
                        f"Se lanza un objeto hacia arriba con velocidad de {clave} m/s. Encuentre la magnitud de su velocidad cuando regresa al punto de lanzamiento. (2 decimales)",
                        f"Se lanza un objeto hacia abajo con rapidez de {clave} m/s desde 100 m de altura. Encuentre su rapidez final en m/s. (2 decimales)",
                        f"Se lanza un objeto hacia abajo con rapidez de {clave} m/s desde 100 m de altura. Encuentre su tiempo de caída en s. (2 decimales)",
                        f"Si un objeto se deja caer y cae en {clave} s, encuentre la altura en m desde la que cayó. (2 decimales)",
                        f"Si un objeto cae desde {clave} m de altura, encuentre el tiempo en s en que cae la primera mitad de su recorrido. (2 decimales)",
                        f"Si un objeto cae desde {clave} m de altura, encuentre el tiempo en s en que cae la segunda mitad de su recorrido."
                    ]
                    st.rerun() # CAMBIO: de experimental_rerun() a rerun()
            except ValueError:
                st.error("Número de clave inválido. Ingresa un número entero.")

# --- Pantalla del Examen ---
elif st.session_state.examen_iniciado and not st.session_state.examen_finalizado:
    st.header(f"¡Hola, {st.session_state.nombre_alumno}!")
    st.subheader(f"Clave de examen: {st.session_state.clave_alumno}")

    if st.session_state.pregunta_actual_idx < len(st.session_state.preguntas_list):
        pregunta_actual_text = st.session_state.preguntas_list[st.session_state.pregunta_actual_idx]
        st.markdown(f"**Pregunta {st.session_state.pregunta_actual_idx + 1} de {len(st.session_state.preguntas_list)}:**")
        st.write(pregunta_actual_text)

        respuesta_input = st.text_input("Tu respuesta (ej. 1.00):", key=f"respuesta_{st.session_state.pregunta_actual_idx}")

        if st.button("Siguiente Pregunta"):
            st.session_state.respuestas_estudiante_guardadas.append({
                "pregunta_idx": st.session_state.pregunta_actual_idx,
                "respuesta_ingresada": respuesta_input
            })
            st.session_state.pregunta_actual_idx += 1
            st.rerun() # CAMBIO: de experimental_rerun() a rerun()
    else:
        # --- Finalizar Examen ---
        calificacion = 0
        detalles_respuestas = []
        total_preguntas_validas_para_calificar = 0

        for i, respuesta_guardada in enumerate(st.session_state.respuestas_estudiante_guardadas):
            pregunta_idx = respuesta_guardada['pregunta_idx']
            respuesta_usuario_str = respuesta_guardada['respuesta_ingresada']

            respuesta_correcta_actual = st.session_state.respuestas_correctas_calc.get(f'pregunta{pregunta_idx + 1}')

            es_correcta = False
            
            if respuesta_correcta_actual is not None and not math.isinf(respuesta_correcta_actual) and not math.isnan(respuesta_correcta_actual):
                total_preguntas_validas_para_calificar += 1 
                try:
                    respuesta_usuario_num = float(respuesta_usuario_str)
                    respuesta_usuario_redondeada = round(respuesta_usuario_num, 2)
                    
                    if abs(respuesta_usuario_redondeada - respuesta_correcta_actual) <= TOLERANCIA:
                        es_correcta = True
                    
                except ValueError:
                    es_correcta = False
            else:
                es_correcta = False

            if es_correcta:
                calificacion += 1

            detalles_respuestas.append({
                "pregunta": st.session_state.preguntas_list[pregunta_idx],
                "respuesta_ingresada": respuesta_usuario_str,
                "respuesta_correcta_esperada": respuesta_correcta_actual,
                "es_correcta": es_correcta
            })

        # Preparar datos para el HASH
        datos_para_hash = {
            "nombre_estudiante": st.session_state.nombre_alumno,
            "clave_ingresada": st.session_state.clave_alumno,
            "calificacion_obtenida": calificacion,
            "total_preguntas_examinadas": len(st.session_state.preguntas_list),
            "total_preguntas_validas_para_calificar": total_preguntas_validas_para_calificar,
            "fecha_hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "respuestas_detalles": detalles_respuestas
        }

        datos_json_str = json.dumps(datos_para_hash, sort_keys=True)
        hash_sha256 = hashlib.sha256(datos_json_str.encode('utf-8')).hexdigest()

        datos_finales_para_guardar = datos_para_hash.copy()
        datos_finales_para_guardar["hash_sha256_integridad"] = hash_sha256

        # Generar el archivo .dat codificado y guardarlo en session_state para descarga persistente
        st.session_state.final_dat_content = codificar_calificacion(datos_finales_para_guardar)
        st.session_state.final_filename = f"calificacion_{st.session_state.nombre_alumno.replace(' ', '_')}_{st.session_state.clave_alumno}.dat"

        # Mostrar mensaje de finalización
        st.session_state.examen_finalizado = True
        st.rerun() # CAMBIO: de experimental_rerun() a rerun()

# --- Pantalla de Examen Finalizado ---
elif st.session_state.examen_finalizado:
    st.success(f"¡Gracias por completar el examen, {st.session_state.nombre_alumno}!")
    st.write("Tu examen ha terminado. Por favor, descarga tu archivo de calificación y envíaselo a tu profesor.")
    
    if st.session_state.final_dat_content and st.session_state.final_filename:
        st.download_button(
            label="Descargar Archivo de Calificación (.dat)",
            data=st.session_state.final_dat_content.encode('utf-8'),
            file_name=st.session_state.final_filename,
            mime="application/octet-stream"
        )
    else:
        st.warning("No se pudo generar el archivo de descarga. Por favor, contacta a tu profesor.")
    
    st.write("Puedes cerrar esta pestaña del navegador.")
    st.info("Para realizar el examen de nuevo, cierra y vuelve a abrir esta pestaña.")