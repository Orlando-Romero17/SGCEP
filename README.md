# SGCEP – Sistema Gestor de Consultas y Expedientes de Pacientes

Aplicación de escritorio para registrar pacientes, consultas médicas y tratamientos,
y consultar el expediente clínico de cada paciente. Proyecto Integrador II – UNAN-León,
Ingeniería en Sistemas de Información.

## Tecnologías
Python 3 · PySide6 (interfaz) · SQLAlchemy (ORM) · MySQL · ReportLab (PDF) · openpyxl (Excel) · hilos con QThreadPool

## Funciones
- **CRUD completo con ORM** de pacientes, consultas y tratamientos.
- **Expediente clínico** por paciente (datos + historial + tratamientos) y su **PDF en vivo**.
- **Reportes** (4 tipos) con vista previa, **PDF** (ReportLab) y exportación a **Excel/CSV**.
- **Validaciones** con `QMessageBox` (cédula, correo, teléfono, fechas, duplicados, campos obligatorios).
- **Hilos**: las consultas y la creación de PDF corren en segundo plano, la ventana no se congela.
- **Integridad referencial**: no se elimina un paciente que tenga consultas o tratamientos.

## Instalación

1. Instale las librerías (se recomienda un entorno virtual):
   ```bash
   pip install -r requirements.txt
   ```
2. Configure la conexión: copie `.env.example` como `.env` y escriba sus datos.
   - Con **MySQL** (recomendado): `DB_TIPO=mysql` y su usuario/contraseña.
     Cree antes la base: ejecute `base_datos/clinica_db.sql` en MySQL Workbench
     (o solo `CREATE DATABASE clinica_db;`). Las tablas las crea la aplicación sola.
   - Para una prueba rápida **sin MySQL**: `DB_TIPO=sqlite` (usa un archivo local `clinica.db`).
3. (Opcional) Cargue datos de demostración:
   ```bash
   python datos_demo.py
   ```
4. Ejecute el sistema:
   ```bash
   python main.py
   ```

## Pruebas
```bash
python -m unittest discover -s pruebas -v
```
`test_validaciones.py` no necesita nada más. `test_repositorio.py` prueba el CRUD con el ORM
sobre una base SQLite temporal (no toca MySQL).

## Estructura
```
main.py                  Ventana principal (menú lateral + pantallas)
modelos.py               ORM: engine, sesiones y clases Paciente, Consulta, Tratamiento
repositorio.py           CRUD y consultas con el ORM (la interfaz no escribe SQL)
validaciones.py          Reglas de validación de los formularios
reporte_pdf.py           PDF con ReportLab (reportes y expediente)
utilidades.py            Exportar a Excel/CSV y cálculo de edad
estilos.py               Hoja de estilos única de toda la interfaz
datos_demo.py            Datos de prueba
hilos/trabajador.py      Ejecución de tareas en segundo plano
paginas/                 base_crud.py, pacientes.py, consultas.py,
                         tratamientos.py, expedientes.py, reportes.py
base_datos/clinica_db.sql  Script de la base de datos MySQL
pruebas/                 Pruebas automáticas
```

## Arquitectura
`Interfaz (paginas/)  →  Hilos  →  repositorio.py  →  modelos.py (ORM)  →  MySQL`

## Seguridad
- Las credenciales están en `.env`, que **no se sube** a GitHub (`.gitignore`).
- Los valores se envían a la base como parámetros (el ORM evita la inyección SQL).
