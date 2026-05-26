import sqlite3
import pandas as pd
import os

def initialize_database():
    print("Iniciando la construcción de la Base de Datos MAPS con correcciones...")
    
    # 1. Borramos la base de datos vieja
    if os.path.exists('tecmilenio_maps.db'):
        os.remove('tecmilenio_maps.db')

    conn = sqlite3.connect('tecmilenio_maps.db')
    cursor = conn.cursor()

    # 2. Creamos las Tablas Relacionales
    cursor.executescript('''
        CREATE TABLE Student (
            student_id TEXT PRIMARY KEY,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            oet_score INTEGER,
            major TEXT,
            specialization_track TEXT
        );

        CREATE TABLE CourseCatalog (
            catalog_id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id TEXT NOT NULL,
            course_name TEXT NOT NULL,
            course_type TEXT NOT NULL,
            major TEXT NOT NULL,
            specialization_track TEXT,
            theoretical_semester INTEGER,
            theoretical_block INTEGER,
            theoretical_order INTEGER, 
            credits INTEGER DEFAULT 8
        );

        CREATE TABLE AcademicRecord (
            record_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            course_id TEXT NOT NULL,
            status TEXT NOT NULL,
            term_taken TEXT,
            FOREIGN KEY (student_id) REFERENCES Student(student_id)
        );
    ''')

    # 3. Leemos tu NUEVO archivo de Excel
    try:
        # Aquí cambiamos el nombre para que apunte a tu archivo corregido
        df = pd.read_csv('Base de Datos de Carreras MAPS.csv', encoding='utf-8')
        df.columns = df.columns.str.strip()

        if 'Ruta de Enfoque' in df.columns:
            df['Ruta de Enfoque'] = df['Ruta de Enfoque'].fillna('Tronco Común')
            df['Ruta de Enfoque'] = df['Ruta de Enfoque'].replace('0', 'Tronco Común')
            # El str.strip() borra automáticamente los espacios extra que se nos hayan ido al teclear
            df['Ruta de Enfoque'] = df['Ruta de Enfoque'].astype(str).str.strip()
        
        records = []
        for index, row in df.iterrows():
            ruta = row['Ruta de Enfoque']
            if ruta == 'Tronco Común':
                ruta = None 
            
            codigo = str(row['Código']).strip()
            orden = int(row['Orden'])
            course_id = f"{codigo}_{orden}_{index}"

            cat = str(row['Categoría']).strip() if pd.notna(row['Categoría']) else "Sin Categoría"
            
            # str.strip() también arreglará si tecleamos espacios al final del nombre de la materia
            mat = str(row['Materia']).strip() if pd.notna(row['Materia']) else "Materia X"

            records.append((
                course_id,
                mat,
                cat,
                str(row['Carrera']).strip(),
                ruta,
                int(row['Semestre']),
                int(row['Bloque']),
                orden, 
                8 
            ))
            
        cursor.executemany('''
            INSERT INTO CourseCatalog 
            (course_id, course_name, course_type, major, specialization_track, theoretical_semester, theoretical_block, theoretical_order, credits)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', records)
        
        print(f"¡Éxito! Se cargaron todas las materias corregidas a la base de datos.")
        
    except Exception as e:
        print(f"Error al leer tu nuevo archivo CSV: {e}")

    # 4. Insertamos a los estudiantes
    cursor.executemany('''
        INSERT INTO Student (student_id, first_name, last_name, oet_score, major, specialization_track)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', [
        ('2670193', 'Roberto', 'Corral Franco', 150, 'Licenciatura en Ingeniería en Mecatrónica', 'Mecatrónica Avanzada'),
        ('2670194', 'Ana', 'Gómez', 120, 'Licenciatura en Mercadotecnia', 'Estrategia Publicitaria')
    ])

    conn.commit()
    conn.close()
    print("Base de Datos Creada Correctamente con la nueva información.")

if __name__ == '__main__':
    initialize_database()