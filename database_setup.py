import sqlite3

def initialize_database():
    # 1. Establish connection to the SQLite database file
    # If the file does not exist, SQLite will automatically create it.
    conn = sqlite3.connect('tecmilenio_maps.db')
    cursor = conn.cursor()

    # 2. Data Definition Language (DDL): Creating the Tables
    cursor.executescript('''
        CREATE TABLE IF NOT EXISTS Student (
            student_id TEXT PRIMARY KEY,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            oet_score INTEGER,
            specialization_track TEXT
        );

        CREATE TABLE IF NOT EXISTS EnglishPlacementRules (
            course_level TEXT PRIMARY KEY,
            min_score INTEGER NOT NULL,
            max_score INTEGER NOT NULL
        );

        CREATE TABLE IF NOT EXISTS CourseCatalog (
            course_id TEXT PRIMARY KEY,
            course_name TEXT NOT NULL,
            course_type TEXT NOT NULL,
            specialization_track TEXT,
            theoretical_semester INTEGER,
            theoretical_block INTEGER
        );

        CREATE TABLE IF NOT EXISTS AcademicRecord (
            record_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            course_id TEXT NOT NULL,
            status TEXT NOT NULL,
            term_taken TEXT,
            FOREIGN KEY (student_id) REFERENCES Student(student_id),
            FOREIGN KEY (course_id) REFERENCES CourseCatalog(course_id)
        );
    ''')

    # 3. Data Manipulation Language (DML): Populating English Placement Rules
    english_rules = [
        ('INGLES I', 0, 20),
        ('INGLES II', 21, 50),
        ('INGLES III', 51, 80),
        ('INGLES IV', 81, 110),
        ('INGLES V', 111, 140),
        ('INGLES AVANZADO I', 141, 170),
        ('INGLES AVANZADO II', 141, 170), 
        ('INGLES AVANZADO III', 171, 200)
    ]
    cursor.executemany('''
        INSERT OR IGNORE INTO EnglishPlacementRules (course_level, min_score, max_score)
        VALUES (?, ?, ?)
    ''', english_rules)

    # 4. Data Manipulation Language (DML): Populating the Mechatronics Core Curriculum
    # Format: (course_id, course_name, course_type, specialization_track, semester, block)
    core_courses = [
        # Semester 1
        ('MEC101', 'Ciencias de la Ingeneria', 'Core', None, 1, 1),
        ('MEC102', 'Dibujo Computarizado', 'Core', None, 1, 1),
        ('MEC103', 'Fundamentos de Programacion', 'Core', None, 1, 2),
        # Semester 2
        ('MEC201', 'Procesos de Manufactura', 'Core', None, 2, 1),
        ('MEC202', 'Probabilidad y estadistica para ciencia de datos', 'Core', None, 2, 1),
        ('MEC203', 'Administracion de operaciones', 'Core', None, 2, 2),
        # Semester 3
        ('MEC301', 'Mecanica de Materiales', 'Core', None, 3, 1),
        ('MEC302', 'Circuitos Electricos y Electronicos', 'Core', None, 3, 1),
        ('MEC303', 'Matematicas Avanzadas', 'Core', None, 3, 2),
        # Semester 4
        ('MEC401', 'Ingenieria de Control', 'Core', None, 4, 1),
        ('MEC402', 'Diseño Mecatronico', 'Core', None, 4, 1),
        ('MEC403', 'Automatizacion Industrial', 'Core', None, 4, 2),
        # Semester 5
        ('MEC501', 'Control Digital', 'Core', None, 5, 1),
        ('MEC502', 'Diseño de Redes Industriales', 'Core', None, 5, 1),
        ('MEC503', 'Robotica Industrial', 'Core', None, 5, 2),
        # Semester 8
        ('MEC801', 'Estancia Empresarial', 'Practicum', None, 8, 1)
    ]
    cursor.executemany('''
        INSERT OR IGNORE INTO CourseCatalog (course_id, course_name, course_type, specialization_track, theoretical_semester, theoretical_block)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', core_courses)

    # 5. Data Manipulation Language (DML): Populating Optativas
    optativas = [
        # Mecatrónica Avanzada
        ('OPT_MA1', 'Fundamentos de planificación y diseño', 'Optativa', 'Mecatrónica Avanzada', 6, 1),
        ('OPT_MA2', 'Implementación y optimización en manufactura', 'Optativa', 'Mecatrónica Avanzada', 6, 2),
        # Automatización Industrial
        ('OPT_AI1', 'Programación de PLC', 'Optativa', 'Automatización Industrial', 6, 1),
        ('OPT_AI2', 'Simulación de procesos y gemelos digitales', 'Optativa', 'Automatización Industrial', 6, 2)
        # Note: Additional optativas follow the same structural matrix and can be appended here.
    ]
    cursor.executemany('''
        INSERT OR IGNORE INTO CourseCatalog (course_id, course_name, course_type, specialization_track, theoretical_semester, theoretical_block)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', optativas)

# Insert Test Student
    cursor.execute('''
        INSERT OR IGNORE INTO Student (student_id, first_name, last_name, oet_score, specialization_track)
        VALUES ('2670193', 'Roberto', 'Corral Franco', 150, 'Mecatrónica Avanzada')
    ''')

    # 6. Commit transactions and terminate connection
    conn.commit()
    conn.close()
    print("Database architecture successfully compiled and populated.")

if __name__ == '__main__':
    initialize_database()

