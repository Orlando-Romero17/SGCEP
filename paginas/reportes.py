"""
reportes.py
Pantalla de reportes: elige un tipo, muestra una vista previa en tabla y permite
generar el PDF (ReportLab) o exportar a Excel/CSV. Los datos se obtienen con el
ORM en un hilo; el PDF también se crea en un hilo.
"""
from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton,
    QGroupBox, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
    QFileDialog, QMessageBox
)
import repositorio
from hilos.trabajador import ejecutar_en_hilo
from reporte_pdf import generar_pdf
from utilidades import exportar_tabla


class PaginaReportes(QWidget):
    def __init__(self):
        super().__init__()
        self._tipo_actual = None   # tipo del último reporte generado

        raiz = QVBoxLayout(self)
        raiz.setContentsMargins(30, 25, 30, 25)
        raiz.setSpacing(10)

        titulo = QLabel("Reportes")
        titulo.setObjectName("titulo")
        raiz.addWidget(titulo)
        sub = QLabel("Genere reportes de la información registrada y expórtelos a PDF o Excel.")
        sub.setObjectName("subtitulo")
        raiz.addWidget(sub)

        # ----- Selección del reporte y botones -----
        grupo = QGroupBox("Generar reporte")
        fila = QHBoxLayout(grupo)
        fila.addWidget(QLabel("Tipo de reporte:"))
        self.tipo = QComboBox()
        self.tipo.addItem("Seleccione...")
        self.tipo.addItems(repositorio.TIPOS_REPORTE)
        fila.addWidget(self.tipo, 1)
        self.btn_generar = QPushButton("Generar reporte")
        self.btn_generar.setObjectName("principal")
        self.btn_generar.clicked.connect(self.generar_reporte)
        self.btn_pdf = QPushButton("Generar PDF")
        self.btn_pdf.setObjectName("principal")
        self.btn_pdf.clicked.connect(self.generar_pdf_reporte)
        self.btn_exportar = QPushButton("Exportar")
        self.btn_exportar.setObjectName("secundario")
        self.btn_exportar.clicked.connect(self.exportar)
        fila.addWidget(self.btn_generar)
        fila.addWidget(self.btn_pdf)
        fila.addWidget(self.btn_exportar)
        raiz.addWidget(grupo)

        self.mensaje = QLabel("")
        self.mensaje.setObjectName("estado")
        raiz.addWidget(self.mensaje)

        # ----- Vista previa -----
        vista = QGroupBox("Vista previa del reporte")
        vl = QVBoxLayout(vista)
        self.tabla = QTableWidget(0, 0)
        self.tabla.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        vl.addWidget(self.tabla)
        raiz.addWidget(vista, 1)

    def al_mostrar(self):
        """No hay datos que recargar: el reporte se genera al pulsar el botón."""
        pass

    def generar_reporte(self):
        """Valida la selección y consulta los datos (ORM) en segundo plano."""
        if self.tipo.currentIndex() == 0:
            QMessageBox.warning(self, "Validación", "Seleccione un tipo de reporte.")
            return
        tipo = self.tipo.currentText()
        self.mensaje.setText("Generando reporte...")
        ejecutar_en_hilo(
            repositorio.datos_reporte, tipo,
            al_terminar=lambda r, t=tipo: self._mostrar_reporte(r, t),
            al_error=lambda m: self.mensaje.setText(f"Error al generar el reporte: {m}"),
        )

    def _mostrar_reporte(self, resultado, tipo):
        """Llena la vista previa con los encabezados y filas recibidos."""
        encabezados, filas = resultado
        self._tipo_actual = tipo
        self.tabla.setColumnCount(len(encabezados))
        self.tabla.setHorizontalHeaderLabels(encabezados)
        self.tabla.setRowCount(len(filas))
        for i, fila in enumerate(filas):
            for j, valor in enumerate(fila):
                self.tabla.setItem(i, j, QTableWidgetItem("" if valor is None else str(valor)))
        self.mensaje.setText(f"Reporte generado correctamente ({len(filas)} registros).")

    def generar_pdf_reporte(self):
        """Crea el PDF del reporte que se ve en la tabla y lo abre al terminar."""
        if self.tabla.rowCount() == 0 or self._tipo_actual is None:
            QMessageBox.information(self, "PDF", "Primero genere un reporte para crear el PDF.")
            return
        sugerido = f"reporte_{self._tipo_actual.replace(' ', '_').lower()}.pdf"
        ruta, _ = QFileDialog.getSaveFileName(self, "Guardar reporte en PDF", sugerido, "PDF (*.pdf)")
        if not ruta:
            return
        if not ruta.lower().endswith(".pdf"):
            ruta += ".pdf"

        # Se leen los datos de la tabla en el hilo principal (donde vive la interfaz)
        encabezados = [self.tabla.horizontalHeaderItem(c).text()
                       for c in range(self.tabla.columnCount())]
        filas = [[self.tabla.item(f, c).text() if self.tabla.item(f, c) else ""
                  for c in range(self.tabla.columnCount())]
                 for f in range(self.tabla.rowCount())]

        self.mensaje.setText("Generando PDF...")
        ejecutar_en_hilo(
            generar_pdf, ruta, f"Reporte: {self._tipo_actual}",
            "Sistema Gestor de Consultas y Expedientes de Pacientes", encabezados, filas,
            al_terminar=self._pdf_listo,
            al_error=lambda m: self.mensaje.setText(f"Error al generar el PDF: {m}"),
        )

    def _pdf_listo(self, ruta):
        self.mensaje.setText(f"PDF generado: {ruta}")
        QMessageBox.information(self, "PDF", f"El PDF se generó correctamente en:\n{ruta}")
        QDesktopServices.openUrl(QUrl.fromLocalFile(ruta))

    def exportar(self):
        """Exporta la vista previa a Excel o CSV."""
        if self.tabla.rowCount() == 0:
            QMessageBox.information(self, "Exportar", "Primero genere un reporte para exportarlo.")
            return
        exportar_tabla(self, self.tabla, (self._tipo_actual or "reporte").replace(" ", "_").lower())
