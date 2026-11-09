"""
utilidades.py
Funciones compartidas por varias páginas:
  - calcular_edad: edad en años a partir de la fecha de nacimiento.
  - exportar_tabla: guarda lo que muestra una tabla en Excel o CSV.
"""
import csv
from datetime import date
from PySide6.QtWidgets import QFileDialog, QMessageBox


def calcular_edad(fecha_nacimiento, hoy=None):
    """Devuelve la edad en años cumplidos."""
    hoy = hoy or date.today()
    edad = hoy.year - fecha_nacimiento.year
    if (hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day):
        edad -= 1
    return edad


def exportar_tabla(parent, tabla, nombre_base="exportacion"):
    """Exporta el contenido de un QTableWidget a un archivo Excel (.xlsx) o CSV."""
    if tabla.rowCount() == 0:
        QMessageBox.information(parent, "Exportar", "No hay datos para exportar.")
        return False

    # Ventana para elegir dónde guardar y en qué formato
    ruta, filtro = QFileDialog.getSaveFileName(
        parent, "Exportar", f"{nombre_base}.xlsx", "Excel (*.xlsx);;CSV (*.csv)"
    )
    if not ruta:
        return False

    # Si no se escribió extensión, se agrega según el filtro elegido
    baja = ruta.lower()
    if not (baja.endswith(".xlsx") or baja.endswith(".csv")):
        ruta += ".csv" if "CSV" in filtro else ".xlsx"

    # Se leen encabezados y filas desde la tabla (omitiendo columnas ocultas)
    columnas = [c for c in range(tabla.columnCount()) if not tabla.isColumnHidden(c)]
    encabezados = []
    for c in columnas:
        h = tabla.horizontalHeaderItem(c)
        encabezados.append(h.text() if h else "")
    filas = [
        [tabla.item(f, c).text() if tabla.item(f, c) else "" for c in columnas]
        for f in range(tabla.rowCount())
    ]

    try:
        if ruta.lower().endswith(".csv"):
            # utf-8-sig para que Excel muestre bien las tildes
            with open(ruta, "w", newline="", encoding="utf-8-sig") as archivo:
                escritor = csv.writer(archivo)
                escritor.writerow(encabezados)
                escritor.writerows(filas)
        else:
            from openpyxl import Workbook
            libro = Workbook()
            hoja = libro.active
            hoja.append(encabezados)
            for fila in filas:
                hoja.append(fila)
            libro.save(ruta)
        QMessageBox.information(parent, "Exportar", f"Archivo guardado en:\n{ruta}")
        return True
    except ImportError:
        QMessageBox.warning(
            parent, "Exportar",
            "Falta la librería openpyxl para Excel.\n"
            "Instálela con: pip install openpyxl\no exporte en formato CSV."
        )
    except Exception as e:
        QMessageBox.warning(parent, "Exportar", f"No se pudo guardar el archivo:\n{e}")
    return False
