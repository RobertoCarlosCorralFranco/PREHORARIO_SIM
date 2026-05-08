import sqlite3

def inject_full_specializations():
    conn = sqlite3.connect('tecmilenio_maps.db')
    cursor = conn.cursor()

    # 1. Limpiar optativas previas para evitar duplicados o errores
    cursor.execute("DELETE FROM CourseCatalog WHERE course_type = 'Optativa'")

    # 2. Diccionario Maestro de Rutas
    optativas_data = {
        "Mecatrónica Avanzada": ["Fundamentos de planificación y diseño", "Implementación y optimización en manufactura", "Sistemas hidráulicos y neumáticos", "Integración de sistemas mecatrónicos", "Fundamentos de gestión de proyectos", "Diseño de celdas de manufactura"],
        "Automatización Industrial": ["Programación de PLC", "Simulación de procesos y gemelos digitales", "Robótica avanzada", "Robótica móvil", "Internet Industrial de las Cosas y sistemas embebidos", "Sistemas de visión y procesamiento de imágenes"],
        "Semiconductores y Micro Manufactura": ["Fundamentos de ciencia e ingeniería de los materiales", "Teoría de dispositivos semiconductores", "Introducción al empaquetado de semiconductores", "Manufactura de empaquetado de semiconductores", "Análisis de elemento finíto", "Empaquetado de semiconductores avanzado"],
        "Sistemas de control": ["Sistemas de control embebido", "Control avanzado", "Automatización y control de procesos de fabricación", "Control de redes y comunicación Máquina a Máquina", "Sistemas de control no lineales", "Simulación y diseño de sistemas de control"],
        "Vehículos autónomos": ["Actuadores y sistemas de dirección", "Sistemas de control y navegación", "Integración de tecnologías de vehículos conectados", "Sistemas de seguridad activa y pasiva", "Potencia automotriz", "Diseño de sistemas de seguridad de vehículos autónomos"],
        "Inteligencia Artificial": ["Ciencia de datos", "Inteligencia artificial", "Optimización de trayectorias de robots", "Sistemas de visión artificial", "Algoritmos de aprendizaje automático", "Predicción de fallas para mantenimiento"],
        "Diseño de procesos sostenibles de manufactura": ["Materiales sostenibles", "Procesos de manufactura y gestión de residuos", "Tecnologías de baterías y almacenamiento", "Automatización verde en la manufactura", "Diseño de productos eco innovadores", "Análisis y evaluación de ciclo de vida y ecoeficiencia"]
    }

    # 3. Mapeo estructural de Rieles (2 por bloque)
    # Las primeras 3 son del Semestre 6, las últimas 3 del Semestre 7
    # Nota: El Bloque 2 solo recibe 1 optativa porque el slot restante lo ocupa Lengua Extranjera
    slots_mapping = [
        (6, 1), # Optativa 1
        (6, 1), # Optativa 2
        (6, 2), # Optativa 3
        (7, 1), # Optativa 4
        (7, 1), # Optativa 5
        (7, 2)  # Optativa 6
    ]

    records_to_insert = []
    
    for track_name, courses in optativas_data.items():
        # Generar un prefijo único para la llave primaria (ej. MA para Mecatrónica Avanzada)
        prefix = ''.join([word[0] for word in track_name.split() if word.lower() != 'de' and word.lower() != 'y'])
        
        for idx, course_name in enumerate(courses):
            sem, blk = slots_mapping[idx]
            course_id = f"OPT_{prefix}_{idx+1}"
            records_to_insert.append((course_id, course_name, 'Optativa', track_name, sem, blk, 8))

    # 4. Inserción Masiva
    cursor.executemany('''
        INSERT INTO CourseCatalog (course_id, course_name, course_type, specialization_track, theoretical_semester, theoretical_block, credits)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', records_to_insert)

    conn.commit()
    conn.close()
    print("Base de datos actualizada: Catálogo maestro de Optativas inyectado correctamente.")

if __name__ == '__main__':
    inject_full_specializations()