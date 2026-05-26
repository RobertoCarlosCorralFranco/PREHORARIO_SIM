# Sistema de Gestión de Trayectoria Académica - Tecmilenio MAPS

## Resumen Ejecutivo
Este proyecto consiste en una solución tecnológica e inteligente diseñada para optimizar y automatizar la operación de los mentores académicos en la Universidad Tecmilenio bajo el modelo modular MAPS. El sistema reemplaza las proyecciones manuales y heurísticas por un motor algorítmico determinístico capaz de generar prehorarios óptimos y recalcular horarios oficiales ante desviaciones (reprobaciones o estatus de Sin Derecho). 

Esta aplicación nace como una expansión tecnológica y de automatización del proyecto de optimización operativa bajo la metodología **Lean Six Sigma Black Belt** liderado por la **Mtra. Erika Muñoz**, traduciendo las reglas de negocio institucionales en restricciones lógicas de software para reducir drásticamente los tiempos de ciclo y eliminar errores humanos mediante un Poka-Yoke estructural.

## Arquitectura del Sistema
El software está desarrollado bajo una arquitectura modular de tres capas acopladas de manera limpia:
1. **Capa de Datos (Cerebro Relacional):** Implementada en SQLite (`tecmilenio_maps.db`), la cual aloja de forma plana la matriz de tronco común de todas las carreras, las reglas de paridad, los talleres institucionales (SEDI), y las rutas de especialización técnica.
2. **Capa Lógica (Motor de Proyección LSS):** Un algoritmo basado en restricciones (*Constraint-Based Scheduling*) que evalúa las líneas de carga académica divididas por semestres (pares/nones), bloques bimestrales y asientos de materia específicos (Slots). Aísla el impacto de una falla académica empujando la materia de forma exclusiva en su riel de paridad correspondiente.
3. **Capa de Presentación (UI Dinámica):** Interfaz web interactiva construida en Streamlit que despliega de forma clara cuatro módulos operativos: Evaluación actual, Prehorario ideal, Horario ajustado y el Dashboard de eficiencia de grupos para la toma de decisiones.

## Estructura del Repositorio
El proyecto mantiene una estructura limpia de archivos planos (*Flat Architecture*):

* `app_v3.py`: El punto de entrada de la aplicación web de Streamlit, encargado del procesamiento lógico de los horarios y el despliegue de la interfaz de usuario.
* `crear_bd.py`: Script de automatización encargado de limpiar el CSV maestro, estructurar las tablas SQL relacionales e inyectar el catálogo completo de materias y alumnos de prueba.
* `Base de Datos de Carreras MAPS.csv`: El archivo de datos de origen corregido que alimenta el sistema con el tronco común, SEDIs y las rutas de enfoque de las carreras vigentes en el campus.
* `requirements.txt`: Manifiesto que lista las librerías necesarias y dependencias del entorno de Python.
* `.gitignore`: Archivo de configuración que restringe la subida de entornos virtuales (`venv/`), archivos compilados del sistema y la base de datos local (`*.db`) para mantener el repositorio limpio.
* `LICENSE`: Licencia de código abierto (MIT License).

## Requisitos e Instalación

Para desplegar y ejecutar este sistema de manera local en cualquier sistema operativo (Windows/macOS/Linux), sigue estos pasos desde tu terminal o consola en tu entorno de desarrollo (como Visual Studio Code):

1. **Clonar el repositorio:**
   ```bash
   git clone [https://github.com/RobertoCarlosCorralFranco/PREEARIO_SIM.git](https://github.com/RobertoCarlosCorralFranco/PREEARIO_SIM.git)
   cd PREHORARIO_SIM
