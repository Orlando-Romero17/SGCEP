"""
expedientes.py
Pantalla de expedientes clínicos e historial médico.
Al elegir un paciente se muestran sus datos, su historial de consultas y sus
tratamientos. Permite generar el expediente en PDF (ReportLab) y exportar el
historial a Excel/CSV.
"""
from datetime import date
from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton,
    QGroupBox, QFormLayout, QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView, QFileDialog, QMessageBox
)
import repositorio
from hilos.trabajador import ejecutar_en_hilo
from reporte_pdf import generar_pdf_expediente
from utilidades import calcular_edad, exportar_tabla


def _tabla(columnas):
    """Crea una tabla de solo lectura con los encabezados indicados."""
    tabla = QTableWidget(0, len(columnas))
    tabla.setHorizontalHeaderLabels(columnas)
    tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    tabla.setSelectionBehavior(QAbstractItemView.SelectRows)
    tabla.setEditTriggers(QAbstractItemView.NoEditTriggers)
    tabla.setAlternatingRowColors(True)
    return tabla


class PaginaExpedientes(QWidget):
    def __init__(self):
        super().__init__()
        self._expediente = None   # datos del expediente mostrado (para el PDF)

        raiz = QVBoxLayout(self)
        raiz.setContentsMargins(30, 25, 30, 25)
        raiz.setSpacing(10)

        titulo = QLabel("Expedientes clínicos")
        titulo.setObjectName("titulo")
        raiz.addWidget(titulo)
        sub = QLabel("Consulte el expediente completo y el historial médico de un paciente.")
        sub.setObjectName("subtitulo")
        raiz.addWidget(sub)

        # ----- Selector de paciente y botones -----
        fila = QHBoxLayout()
        fila.addWidget(QLabel("Paciente:"))
        self.combo = QComboBox()
        self.combo.setMinimumWidth(350)
        self.combo.currentIndexChanged.connect(self.cargar_expediente)
        fila.addWidget(self.combo, 1)
        self.btn_pdf = QPushButton("Generar PDF del expediente")
        self.btn_pdf.setObjectName("principal")
        self.btn_pdf.clicked.connect(self.generar_pdf)
        self.btn_exportar = QPushButton("Exportar historial")
        self.btn_exportar.setObjectName("secundario")
        self.btn_exportar.clicked.connect(
            lambda: exportar_tabla(self, self.tabla_consultas, "historial_paciente"))
        fila.addWidget(self.btn_pdf)
        fila.addWidget(self.btn_exportar)
        raiz.addLayout(fila)

        # ----- Datos del paciente -----
        grupo = QGroupBox("Datos del paciente")
        form = QFormLayout(grupo)
        self.lbl_cedula = QLabel("-")
        self.lbl_nombre = QLabel("-")
        self.lbl_nacimiento = QLabel("-")
        self.lbl_sexo = QLabel("-")
        self.lbl_telefono = QLabel("-")
        self.lbl_correo = QLabel("-")
        self.lbl_sangre = QLabel("-")
        self.lbl_alergias = QLabel("-")
        self.lbl_alergias.setWordWrap(True)
        form.addRow("Cédula:", self.lbl_cedula)
        form.addRow("Nombre completo:", self.lbl_nombre)
        form.addRow("Fecha de nacimiento:", self.lbl_nacimiento)
        form.addRow("Sexo:", self.lbl_sexo)
        form.addRow("Teléfono:", self.lbl_telefono)
        form.addRow("Correo:", self.lbl_correo)
        form.addRow("Tipo de sangre:", self.lbl_sangre)
        form.addRow("Alergias:", self.lbl_alergias)
        raiz.addWidget(grupo)

        # ----- Historial de consultas y tratamientos -----
        g1 = QGroupBox("Historial de consultas")
        l1 = QVBoxLayout(g1)
        self.tabla_consultas = _tabla(
            ["ID", "FECHA", "MOTIVO", "SÍNTOMAS", "DIAGNÓSTICO", "TRATAMIENTO", "OBSERVACIONES"])
        l1.addWidget(self.tabla_consultas)
        raiz.addWidget(g1, 1)

        g2 = QGroupBox("Tratamientos")
        l2 = QVBoxLayout(g2)
        self.tabla_trat = _tabla(
            ["ID", "MEDICAMENTO", "DOSIS", "FRECUENCIA", "DURACIÓN", "INDICACIONES"])
        l2.addWidget(self.tabla_trat)
        raiz.addWidget(g2, 1)

        self.estado = QLabel("")
        self.estado.setObjectName("estado")
        raiz.addWidget(self.estado)

        self.al_mostrar()

    # ----- Carga de datos (en hilos) -----
    def al_mostrar(self):
        """Recarga la lista de pacientes cada vez que se abre la pantalla."""
        ejecutar_en_hilo(repositorio.pacientes_combo, al_terminar=self._llenar_combo)

    def _llenar_combo(self, pacientes):
        actual = self.combo.currentData()
        self.combo.blockSignals(True)
        self.combo.clear()
        self.combo.addItem("Seleccione un paciente...", None)
        for id_paciente, texto in pacientes:
            self.combo.addItem(texto, id_paciente)
        indice = self.combo.findData(actual)
        self.combo.setCurrentIndex(indice if indice >= 0 else 0)
        self.combo.blockSignals(False)
        self.cargar_expediente()

    def cargar_expediente(self):
        """Pide el expediente del paciente elegido (ORM) en segundo plano."""
        id_paciente = self.combo.currentData()
        if id_paciente is None:
            self._limpiar()
            return
        self.estado.setText("Cargando expediente...")
        ejecutar_en_hilo(
            repositorio.expediente, id_paciente,
            al_terminar=self._mostrar_expediente,
            al_error=lambda m: self.estado.setText(f"Error: {m}"),
        )

    def _limpiar(self):
        self._expediente = None
        for lbl in (self.lbl_cedula, self.lbl_nombre, self.lbl_nacimiento, self.lbl_sexo,
                    self.lbl_telefono, self.lbl_correo, self.lbl_sangre, self.lbl_alergias):
            lbl.setText("-")
        self.tabla_consultas.setRowCount(0)
        self.tabla_trat.setRowCount(0)
        self.estado.setText("")

    def _mostrar_expediente(self, exp):
        if exp is None:
            self._limpiar()
            return
        self._expediente = exp
        p = exp["paciente"]
        nac = p["fecha_nacimiento"]
        self.lbl_cedula.setText(p["cedula"] or "-")
        self.lbl_nombre.setText(f"{p['nombre']} {p['apellido']}")
        if isinstance(nac, date):
            self.lbl_nacimiento.setText(f"{nac:%d/%m/%Y} ({calcular_edad(nac)} años)")
        self.lbl_sexo.setText({"M": "Masculino", "F": "Femenino"}.get(p["sexo"], "-"))
        self.lbl_telefono.setText(p["telefono"] or "-")
        self.lbl_correo.setText(p["correo"] or "-")
        self.lbl_sangre.setText(p["tipo_sangre"] or "-")
        self.lbl_alergias.setText(p["alergias"] or "Ninguna registrada")
        self._llenar(self.tabla_consultas, exp["consultas"])
        self._llenar(self.tabla_trat, exp["tratamientos"])
        self.estado.setText(
            f"{len(exp['consultas'])} consulta(s) y {len(exp['tratamientos'])} tratamiento(s).")

    @staticmethod
    def _llenar(tabla, filas):
        tabla.setRowCount(len(filas))
        for i, fila in enumerate(filas):
            for j, valor in enumerate(fila):
                if isinstance(valor, date):
                    valor = valor.strftime("%d/%m/%Y")
                tabla.setItem(i, j, QTableWidgetItem("" if valor is None else str(valor)))

    # ----- PDF del expediente (en un hilo) -----
    def generar_pdf(self):
        if self._expediente is None:
            QMessageBox.information(self, "PDF", "Seleccione primero un paciente.")
            return
        p = self._expediente["paciente"]
        sugerido = f"expediente_{p['apellido']}_{p['nombre']}.pdf".replace(" ", "_")
        ruta, _ = QFileDialog.getSaveFileName(
            self, "Guardar expediente en PDF", sugerido, "PDF (*.pdf)")
        if not ruta:
            return
        if not ruta.lower().endswith(".pdf"):
            ruta += ".pdf"
        self.estado.setText("Generando PDF...")
        ejecutar_en_hilo(
            generar_pdf_expediente, ruta, self._expediente,
            al_terminar=self._pdf_listo,
            al_error=lambda m: self.estado.setText(f"Error al generar el PDF: {m}"),
        )

    def _pdf_listo(self, ruta):
        self.estado.setText(f"PDF generado: {ruta}")
        QMessageBox.information(self, "PDF", f"El expediente se generó en:\n{ruta}")
        QDesktopServices.openUrl(QUrl.fromLocalFile(ruta))   # lo abre automáticamente
