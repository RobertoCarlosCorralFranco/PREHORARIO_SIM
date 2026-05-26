import streamlit as st
import sqlite3
import pandas as pd
from fpdf import FPDF
from datetime import datetime
import time
import os  # <-- Asegúrate de agregar esta librería

# --- MAGIA PARA LA NUBE: Si la BD no existe, la crea automáticamente ---
if not os.path.exists('tecmilenio_maps.db'):
    import crear_bd
    crear_bd.initialize_database()

# --- Capa de Acceso a Datos ---
def get_db_connection():
    conn = sqlite3.connect('tecmilenio_maps.db')
    conn.row_factory = sqlite3.Row 
    return conn

# ... (El resto de tu código se queda exactamente igual)

def fetch_student_data(student_id):
    conn = get_db_connection()
    student = conn.execute("SELECT * FROM Student WHERE student_id = ?", (student_id,)).fetchone()
    conn.close()
    return student

# Esta función lee las carreras dinámicamente desde la BD
def get_available_majors_and_tracks():
    conn = get_db_connection()
    majors_df = pd.read_sql_query("SELECT DISTINCT major FROM CourseCatalog", conn)
    tracks_df = pd.read_sql_query("SELECT DISTINCT major, specialization_track FROM CourseCatalog WHERE specialization_track IS NOT NULL", conn)
    conn.close()
    
    majors = majors_df['major'].tolist()
    tracks_by_major = {}
    for major in majors:
        tracks = tracks_df[tracks_df['major'] == major]['specialization_track'].tolist()
        tracks_by_major[major] = tracks if tracks else ["Sin Rutas"]
        
    return majors, tracks_by_major

def fetch_full_curriculum(specialization, major):
    conn = get_db_connection()
    
    query = """
        SELECT course_id, course_name, theoretical_semester, theoretical_block, theoretical_order, course_type, credits
        FROM CourseCatalog
        WHERE major = ? AND (specialization_track IS NULL OR specialization_track = ?)
    """
    df = pd.read_sql_query(query, conn, params=(major, specialization))
    conn.close()
    
    # 1. Ordenamos tal cual estaba en el Orden original del CSV
    df = df.sort_values(by=['theoretical_semester', 'theoretical_block', 'theoretical_order'])
    
    # 2. LA MAGIA RESTAURADA: Regeneramos el Slot dinámico (1, 2, 3...) por cada bloque
    # Esto asegura que el algoritmo siempre tenga un riel de 1 a 4 para acomodar Materias y SEDIs
    df['theoretical_slot'] = df.groupby(['theoretical_semester', 'theoretical_block']).cumcount() + 1
    
    return df

# --- Lógica Algorítmica y Utilidades ---
def evaluate_grade(score, is_sd):
    if is_sd: return 'SD'
    elif score >= 70: return 'Aprobado'
    else: return 'Reprobado'

def generate_institutional_email(student_id):
    return f"al0{student_id}@tecmilenio.mx"

def simulate_email_send(student_id, report_type):
    email = generate_institutional_email(student_id)
    with st.spinner(f"Conectando con el servidor de correo para enviar a {email}..."):
        time.sleep(1.5)
    st.success(f"📧 ¡Éxito! El documento de {report_type} ha sido enviado a la bandeja de: **{email}**")

def calculate_dynamic_projection(pending_df, current_sem, current_block):
    if pending_df.empty:
        return pd.DataFrame()
        
    # Extraemos la Estancia Empresarial para anclarla al final del mapa
    practicum_df = pending_df[pending_df['course_type'] == 'Estancia Empresarial']
    academic_df = pending_df[pending_df['course_type'] != 'Estancia Empresarial'].copy()
        
    schedule = []
    
    # Motor Constraint-Based
    for parity in [0, 1]: 
        for block in [1, 2]:
            # Buscamos en los slots del 1 al 8 (Suficientes para Materia 1, Materia 2, SEDI, Lenguaje, etc.)
            for slot in range(1, 9): 
                queue_df = academic_df[
                    (academic_df['theoretical_semester'] % 2 == parity) & 
                    (academic_df['theoretical_block'] == block) &
                    (academic_df['theoretical_slot'] == slot)
                ].sort_values('theoretical_semester') 
                
                v_sems = []
                for sem in range(1, 30):
                    if sem % 2 == parity:
                        if sem < current_sem: continue
                        if sem == current_sem and block < current_block: continue
                        v_sems.append(sem)
                        
                for i, row in enumerate(queue_df.to_dict('records')):
                    row['projected_semester'] = v_sems[i]
                    row['projected_block'] = block
                    schedule.append(row)
        
    # Anclaje de la Estancia Empresarial
    if not practicum_df.empty:
        max_academic_sem = max([c['projected_semester'] for c in schedule]) if schedule else current_sem
        final_practicum_sem = max(8, max_academic_sem + 1)
        
        for _, course in practicum_df.iterrows():
            course_copy = course.to_dict()
            course_copy['projected_semester'] = final_practicum_sem
            course_copy['projected_block'] = 1
            schedule.append(course_copy)
        
    return pd.DataFrame(schedule)

def calculate_group_efficiency(demand):
    presencial_groups = demand // 25
    remainder = demand % 25
    online_students = 0
    if remainder >= 8:
        presencial_groups += 1
    elif remainder > 0:
        online_students = remainder
    return pd.Series([presencial_groups, online_students])

# --- Capa de Exportación (PDF) ---
def generate_pdf_report(student_data, schedule_df, report_type):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    current_date = datetime.now().strftime("%m/%d/%Y")
    
    pdf.cell(200, 10, txt=f"Universidad Tecmilenio - {report_type}", ln=True, align='C')
    pdf.set_font("Arial", size=10)
    pdf.cell(200, 10, txt=f"Fecha de Emision: {current_date}", ln=True, align='R')
    pdf.cell(200, 6, txt=f"Estudiante: {student_data['first_name']} {student_data['last_name']}", ln=True)
    pdf.cell(200, 6, txt=f"Matricula: {student_data['student_id']}", ln=True)
    pdf.cell(200, 6, txt=f"Carrera: {student_data['major']}", ln=True)
    pdf.cell(200, 6, txt=f"Ruta de Enfoque: {student_data['specialization_track']}", ln=True)
    
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 9)
    pdf.cell(20, 10, "Semestre", 1)
    pdf.cell(15, 10, "Bloque", 1)
    pdf.cell(30, 10, "Clave", 1)
    pdf.cell(100, 10, "Materia", 1)
    pdf.cell(20, 10, "Tipo", 1)
    pdf.ln()
    
    pdf.set_font("Arial", '', 8)
    if not schedule_df.empty:
        schedule_df = schedule_df.sort_values(by=['projected_semester', 'projected_block', 'theoretical_slot'])
        for index, row in schedule_df.iterrows():
            course_name = str(row['course_name']).encode('latin-1', 'replace').decode('latin-1')
            pdf.cell(20, 8, str(row['projected_semester']), 1)
            pdf.cell(15, 8, str(row['projected_block']), 1)
            pdf.cell(30, 8, str(row['course_id']).split('_')[0], 1)
            pdf.cell(100, 8, course_name, 1)
            pdf.cell(20, 8, str(row['course_type']), 1)
            pdf.ln()
    
    return pdf.output(dest="S").encode("latin-1")

# --- Capa de Presentación (UI y Segmentación) ---
def display_segmented_schedule(df_schedule, title_prefix=""):
    if df_schedule.empty:
        st.info("No hay materias programadas.")
        return

    df_schedule = pd.DataFrame(df_schedule).sort_values(by=['projected_semester', 'projected_block', 'theoretical_slot'])
    
    first_sem = df_schedule['projected_semester'].min()
    first_block = df_schedule[df_schedule['projected_semester'] == first_sem]['projected_block'].min()
    
    df_next_block = df_schedule[(df_schedule['projected_semester'] == first_sem) & (df_schedule['projected_block'] == first_block)]
    df_future = df_schedule.drop(df_next_block.index)

    st.markdown(f"#### {title_prefix}: Bloque Inmediato Proyectado (Semestre {first_sem}, Bloque {first_block})")
    display_cols = ['course_name', 'credits', 'course_type']
    st.dataframe(df_next_block[display_cols], use_container_width=True, hide_index=True)

    if not df_future.empty:
        st.markdown(f"#### {title_prefix}: Despliegue de Semestres Posteriores")
        future_semesters = sorted(df_future['projected_semester'].unique())
        
        for sem in future_semesters:
            sem_data = df_future[df_future['projected_semester'] == sem]
            with st.expander(f"Semestre Proyectado {sem}", expanded=True):
                st.dataframe(sem_data[['projected_block'] + display_cols], use_container_width=True, hide_index=True)

def main():
    st.set_page_config(page_title="Sistema de Proyección MAPS", layout="wide")
    st.title("Ingeniería de Trayectoria Académica - Tecmilenio MAPS")

    major_options, tracks_by_major = get_available_majors_and_tracks()

    st.sidebar.header("Parámetros del Estudiante")
    target_student_id = st.sidebar.text_input("Ingrese la Matrícula:", value="2670193")
    student_record = fetch_student_data(target_student_id)
    
    current_major = student_record['major'] if student_record else major_options[0]
    selected_major = st.sidebar.selectbox("Carrera (Simulador):", major_options, index=major_options.index(current_major) if current_major in major_options else 0)

    available_tracks = tracks_by_major.get(selected_major, ["Sin Rutas"])
    current_track = student_record['specialization_track'] if student_record else available_tracks[0]
    selected_track = st.sidebar.selectbox("Ruta de Enfoque (Simulador):", available_tracks, index=available_tracks.index(current_track) if current_track in available_tracks else 0)

    tab_calif, tab_pre, tab_hor, tab_mentor = st.tabs([
        "1. Calificaciones Actuales", "2. Prehorario (Optimista)", "3. Horario Oficial (Recálculo LSS)", "4. Dashboard del Mentor"
    ])

    if student_record:
        full_curriculum_df = fetch_full_curriculum(selected_track, selected_major)
        
        current_classes = full_curriculum_df[
            (full_curriculum_df['theoretical_semester'] == 4) & 
            (full_curriculum_df['theoretical_block'] == 1)
        ]
        
        future_classes_base = full_curriculum_df[
            (full_curriculum_df['theoretical_semester'] >= 4)
        ].copy()
        future_classes_base = future_classes_base.drop(current_classes.index)

        with tab_calif:
            st.subheader(f"Evaluación Actual | {selected_major}")
            st.write(f"Ruta Activa: {selected_track}")
            st.write("Semestre 4, Bloque 1")
            
            if current_classes.empty:
                st.info("No se encontraron clases para el Semestre 4, Bloque 1 en la Base de Datos para esta carrera.")
            
            grading_results = {}
            for index, row in current_classes.iterrows():
                c1, c2, c3, c4 = st.columns(4)
                c1.write(f"**{row['course_name']}**")
                score = c2.number_input(f"Nota", min_value=0, max_value=100, value=85, key=f"score_{row['course_id']}")
                is_sd = c3.checkbox(f"SD (Límite Faltas)", key=f"sd_{row['course_id']}")
                
                status = evaluate_grade(score, is_sd)
                if status == 'Aprobado': c4.success(status)
                else: c4.error(status)
                
                grading_results[row['course_id']] = {'course_name': row['course_name'], 'status': status, 'row_data': row}

        with tab_pre:
            st.subheader("Prehorario: Proyección Asumiendo Cero Retrasos")
            prehorario_df = calculate_dynamic_projection(future_classes_base, current_sem=4, current_block=2)
            
            col1, col2 = st.columns(2)
            with col1:
                pdf_bytes_pre = generate_pdf_report(student_record, prehorario_df, "Prehorario Académico")
                st.download_button(label="📥 Imprimir PDF (Prehorario)", data=pdf_bytes_pre, file_name=f"Prehorario_{target_student_id}.pdf", mime="application/pdf", use_container_width=True)
            with col2:
                if st.button("📧 Enviar Prehorario al Estudiante", use_container_width=True, key="btn_env_pre"):
                    simulate_email_send(target_student_id, "Prehorario")
            
            st.divider()
            display_segmented_schedule(prehorario_df, "Prehorario")

        with tab_hor:
            st.subheader("Horario: Recalculado con Restricciones Estructurales")
            
            failed_courses = []
            for cid, data in grading_results.items():
                if data['status'] in ['Reprobado', 'SD']:
                    failed_row = data['row_data'].copy()
                    failed_row['course_name'] = failed_row['course_name'] + " (RECURSE)"
                    failed_row['course_type'] = 'Retake'
                    failed_courses.append(failed_row)
            
            if failed_courses:
                st.warning("Desviación detectada. Recalculando matriz de materias empujando el riel correspondiente.")
                failed_df = pd.DataFrame(failed_courses)
                pending_df_horario = pd.concat([failed_df, future_classes_base], ignore_index=True)
            else:
                st.success("Trayectoria óptima. Algoritmo refleja la ruta ideal.")
                pending_df_horario = future_classes_base.copy()
            
            horario_df = calculate_dynamic_projection(pending_df_horario, current_sem=4, current_block=2)
            
            col3, col4 = st.columns(2)
            with col3:
                pdf_bytes_hor = generate_pdf_report(student_record, horario_df, "Horario Oficial (Ajustado)")
                st.download_button(label="📥 Imprimir PDF (Horario)", data=pdf_bytes_hor, file_name=f"Horario_{target_student_id}.pdf", mime="application/pdf", use_container_width=True)
            with col4:
                if st.button("📧 Enviar Horario al Estudiante", use_container_width=True, key="btn_env_hor"):
                    simulate_email_send(target_student_id, "Horario Oficial")
                    
            st.divider()
            display_segmented_schedule(horario_df, "Horario Oficial")
            
        with tab_mentor:
            st.subheader("Dashboard Operativo del Mentor")
            st.write("Análisis consolidado de la cohorte actual (Simulación).")
            
            cohort_data = pd.DataFrame({
                "Materia": ["Materia X", "Materia Y", "SEDI", "Lenguaje"],
                "Alumnos Reprobados": [32, 14, 5, 29]
            }).sort_values(by="Alumnos Reprobados", ascending=False)
            
            st.dataframe(cohort_data, hide_index=True, use_container_width=True)
            
            eficiencia_df = cohort_data.copy()
            eficiencia_df[["Grupos Presenciales Requeridos", "Alumnos Transferidos a Online"]] = eficiencia_df["Alumnos Reprobados"].apply(calculate_group_efficiency)
            st.dataframe(eficiencia_df, hide_index=True, use_container_width=True)

if __name__ == "__main__":
    main()
