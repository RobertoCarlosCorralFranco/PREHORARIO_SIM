import streamlit as st
import sqlite3
import pandas as pd
from fpdf import FPDF
from datetime import datetime
import time

# --- Capa de Acceso a Datos ---
def get_db_connection():
    conn = sqlite3.connect('tecmilenio_maps.db')
    conn.row_factory = sqlite3.Row 
    return conn

def fetch_student_data(student_id):
    conn = get_db_connection()
    student = conn.execute("SELECT * FROM Student WHERE student_id = ?", (student_id,)).fetchone()
    conn.close()
    return student

def fetch_full_curriculum(specialization, oet_score=None):
    conn = get_db_connection()
    query = """
        SELECT course_id, course_name, theoretical_semester, theoretical_block, course_type, credits
        FROM CourseCatalog
        WHERE course_type IN ('Core', 'Practicum') 
           OR (course_type = 'Optativa' AND specialization_track = ?)
    """
    df = pd.read_sql_query(query, conn, params=(specialization,))
    
    df = df.sort_values(by=['theoretical_semester', 'theoretical_block', 'course_id'])
    df['theoretical_slot'] = df.groupby(['theoretical_semester', 'theoretical_block']).cumcount() + 1
    
    if oet_score is not None:
        language_courses = []
        starting_level = 1 
        if oet_score > 80: starting_level = 4
        
        for sem in range(1, 8):
            language_courses.append({
                'course_id': f'ENG{sem}00',
                'course_name': f'Lengua Extranjera Nivel {starting_level + sem - 1}',
                'theoretical_semester': sem,
                'theoretical_block': 2,
                'course_type': 'Language',
                'credits': 8,
                'theoretical_slot': 2 
            })
        df = pd.concat([df, pd.DataFrame(language_courses)], ignore_index=True)

    conn.close()
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
        
    practicum_df = pending_df[pending_df['course_type'] == 'Practicum']
    academic_df = pending_df[pending_df['course_type'] != 'Practicum'].copy()
        
    schedule = []
    
    for parity in [0, 1]: 
        for block in [1, 2]:
            for slot in [1, 2]:
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
    """Calcula la eficiencia de grupos presenciales y la transferencia a online."""
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
    pdf.cell(200, 6, txt=f"Correo Institucional: {generate_institutional_email(student_data['student_id'])}", ln=True)
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
        schedule_df = schedule_df.sort_values(by=['projected_semester', 'projected_block'])
        for index, row in schedule_df.iterrows():
            course_name = str(row['course_name']).encode('latin-1', 'replace').decode('latin-1')
            
            pdf.cell(20, 8, str(row['projected_semester']), 1)
            pdf.cell(15, 8, str(row['projected_block']), 1)
            pdf.cell(30, 8, str(row['course_id']), 1)
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
    display_cols = ['course_id', 'course_name', 'credits', 'course_type']
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
    
    track_options = [
        "Mecatrónica Avanzada", "Automatización Industrial", "Semiconductores y Micro Manufactura",
        "Sistemas de control", "Vehículos autónomos", "Inteligencia Artificial", "Diseño de procesos sostenibles de manufactura"
    ]

    st.sidebar.header("Parámetros del Estudiante")
    target_student_id = st.sidebar.text_input("Ingrese la Matrícula:", value="2670193")
    student_record = fetch_student_data(target_student_id)
    
    current_track = student_record['specialization_track'] if student_record else track_options[0]
    selected_track = st.sidebar.selectbox("Ruta de Enfoque (Simulador):", track_options, index=track_options.index(current_track) if current_track in track_options else 0)

    tab_calif, tab_pre, tab_hor, tab_mentor = st.tabs([
        "1. Calificaciones Actuales", "2. Prehorario (Optimista)", "3. Horario Oficial (Recálculo LSS)", "4. Dashboard del Mentor"
    ])

    if student_record:
        full_curriculum_df = fetch_full_curriculum(selected_track, student_record['oet_score'])
        
        current_classes = full_curriculum_df[
            (full_curriculum_df['theoretical_semester'] == 4) & 
            (full_curriculum_df['theoretical_block'] == 1)
        ]
        
        future_classes_base = full_curriculum_df[
            (full_curriculum_df['theoretical_semester'] >= 4)
        ].copy()
        future_classes_base = future_classes_base.drop(current_classes.index)

        with tab_calif:
            st.subheader(f"Evaluación Actual | Ruta Activa: {selected_track}")
            st.write("Semestre 4, Bloque 1")
            
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
                st.download_button(
                    label="📥 Imprimir PDF (Prehorario)", 
                    data=pdf_bytes_pre, 
                    file_name=f"Prehorario_{target_student_id}.pdf", 
                    mime="application/pdf",
                    use_container_width=True
                )
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
                st.download_button(
                    label="📥 Imprimir PDF (Horario)", 
                    data=pdf_bytes_hor, 
                    file_name=f"Horario_{target_student_id}.pdf", 
                    mime="application/pdf",
                    use_container_width=True
                )
            with col4:
                if st.button("📧 Enviar Horario al Estudiante", use_container_width=True, key="btn_env_hor"):
                    simulate_email_send(target_student_id, "Horario Oficial")
                    
            st.divider()
            display_segmented_schedule(horario_df, "Horario Oficial")
            
        with tab_mentor:
            st.subheader("Dashboard Operativo del Mentor: Monitoreo y Eficiencia")
            st.write("Análisis consolidado de la cohorte actual (Simulación Semestre 4, Bloque 1).")
            
            # Generación de datos simulados para la cohorte
            cohort_data = pd.DataFrame({
                "Clave": ["MEC401", "MEC402", "MEC201", "MEC302"],
                "Materia": ["Ingeniería de Control", "Diseño Mecatrónico", "Procesos de Manufactura", "Circuitos Eléctricos"],
                "Alumnos Reprobados": [32, 14, 5, 29]
            }).sort_values(by="Alumnos Reprobados", ascending=False)
            
            st.markdown("### 1. Priorización de Riesgo Académico (Oferta de Clases)")
            st.write("Identificación de materias con mayor índice de reprobación para planificar recursamientos prioritarios.")
            st.dataframe(cohort_data, hide_index=True, use_container_width=True)
            
            st.markdown("### 2. Sábana de Seguimiento Granular (Estudiantes)")
            student_failures = pd.DataFrame({
                "Matrícula": ["2670100", "2670101", "2670102", "2670103"],
                "Estudiante": ["David Alfonso Muela Olivas", "Brayan Fernando Hernández Luna", "Sofía López", "Leo Martínez"],
                "Bloque de Falla": [1, 1, 2, 1],
                "Total Reprobadas": [2, 1, 1, 2],
                "Materias Específicas": ["Ingeniería de Control, Diseño Mecatrónico", "Ingeniería de Control", "Procesos de Manufactura", "Ingeniería de Control, Circuitos Eléctricos"]
            })
            st.dataframe(student_failures, hide_index=True, use_container_width=True)
            
            st.markdown("### 3. Análisis de Eficiencia de Grupos (Optimización de Recursos)")
            st.write("Cálculo matemático de viabilidad de grupos presenciales (Capacidad: 25) y transferencia a modalidad Online (Mínimo requerido: 8).")
            
            eficiencia_df = cohort_data.copy()
            eficiencia_df[["Grupos Presenciales Requeridos", "Alumnos Transferidos a Online"]] = eficiencia_df["Alumnos Reprobados"].apply(calculate_group_efficiency)
            st.dataframe(eficiencia_df, hide_index=True, use_container_width=True)

if __name__ == "__main__":
    main()