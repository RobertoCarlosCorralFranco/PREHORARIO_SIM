# Sistema de Gestión de Trayectoria Académica - Tecmilenio MAPS

## Resumen Ejecutivo
Este proyecto constituye una solución computacional basada en restricciones (Constraint-Based Scheduling) diseñada para automatizar y optimizar la proyección de la carga académica de los estudiantes de ingeniería bajo el modelo educativo MAPS de la Universidad Tecmilenio. El sistema reemplaza los procesos heurísticos manuales con un motor matemático determinístico que calcula prehorarios y recalcula rutas críticas ante desviaciones académicas (reprobación o límites de inasistencia).

## Arquitectura del Sistema
La aplicación opera bajo una arquitectura modular de tres capas:
* **Capa de Datos:** Implementada mediante SQLite, albergando el catálogo maestro de materias, reglas de seriación por paridad y las rutas de especialización técnica (ej. Mecatrónica Avanzada, Inteligencia Artificial).
* **Capa Lógica (Motor de Proyección):** Un algoritmo secuencial que evalúa ocho líneas de ensamble independientes (rieles por semestre, bloque y slot). "La programación basada en restricciones permite aislar el impacto de una falla académica, empujando exclusivamente la materia afectada hacia su siguiente iteración matemática válida (par o impar) sin corromper la totalidad de la matriz de graduación" (Pinedo, 2016, p. 112).
* **Capa de Presentación:** Interfaz desarrollada en Streamlit que proporciona módulos separados para evaluación actual, proyección optimista (Prehorario), proyección condicional (Horario) y un panel administrativo para métricas de eficiencia de grupos.

## Requisitos del Entorno
Para ejecutar este sistema en un entorno local, se requiere Python 3.9 o superior y las dependencias listadas en el manifiesto del repositorio.

1. Clonar el repositorio.
2. Instalar dependencias: `pip install -r requirements.txt`
3. Ejecutar la aplicación: `streamlit run app.py`

## Funcionalidades Operativas
* **Simulador de Rutas de Enfoque:** Permite la modificación dinámica del plan de estudios basado en 7 especialidades de ingeniería.
* **Recálculo Dinámico:** Reasigna materias reprobadas respetando restricciones de oferta par/impar y pospone algorítmicamente la Estancia Empresarial al nodo final del programa.
* **Exportación y Comunicación:** Generación automatizada de reportes en formato PDF y simulación de protocolos de envío mediante cliente SMTP institucional (formato al0+matrícula).
* **Inteligencia Administrativa:** Dashboard para mentores operativos que calcula la eficiencia presencial de los grupos (capacidad máxima de 25, límite de apertura de 8) y la viabilidad de transferencia a modalidad online.

## Referencias
* Pinedo, M. L. (2016). *Scheduling: Theory, Algorithms, and Systems* (5th ed.). Springer. https://doi.org/10.1007/978-3-319-26580-3