"""
consultas.py
Pantalla de consultas médicas (CRUD completo con ORM).
Cada consulta pertenece a un paciente, que se elige de una lista desplegable.
"""
from PySide6.QtCore import QDate
from PySide6.QtWidgets import QLineEdit, QComboBox, QDateEdit, QTextEdit
import repositorio
from validaciones import validar_consulta
from hilos.trabajador import ejecutar_en_hilo
from paginas.base_crud import PaginaCrud


class PaginaConsultas(PaginaCrud):
    TITULO = "Consultas médicas"
    SUBTITULO = "Registre el motivo, síntomas, diagnóstico y tratamiento de cada consulta."
    # Columna 1 (id del paciente) se oculta: solo sirve para cargar el formulario
    COLUMNAS = ["ID", "ID PACIENTE", "PACIENTE", "FECHA", "MOTIVO", "SÍNTOMAS",
                "DIAGNÓSTICO", "TRATAMIENTO", "OBSERVACIONES"]
    COLUMNAS_OCULTAS = [1]
    PLACEHOLDER = "Buscar por paciente, cédula, motivo o diagnóstico..."
    NOMBRE_EXPORTAR = "consultas"
    NOMBRE_ELEMENTO = "consulta"

    def construir_formulario(self, form):
        """Campos del formulario de consultas."""
        self.combo_paciente = QComboBox()

        self.fecha = QDateEdit()
        self.fecha.setCalendarPopup(True)
        self.fecha.setDisplayFormat("dd/MM/yyyy")
        self.fecha.setMaximumDate(QDate.currentDate())
        self.fecha.setDate(QDate.currentDate())

        self.motivo = QLineEdit()
        self.sintomas = QTextEdit()
        self.diagnostico = QTextEdit()
        self.tratamiento = QTextEdit()
        self.observaciones = QTextEdit()
        for campo in (self.sintomas, self.diagnostico, self.tratamiento, self.observaciones):
            campo.setFixedHeight(50)

        form.addRow("Paciente:", self.combo_paciente)
        form.addRow("Fecha:", self.fecha)
        form.addRow("Motivo:", self.motivo)
        form.addRow("Síntomas:", self.sintomas)
        form.addRow("Diagnóstico:", self.diagnostico)
        form.addRow("Tratamiento:", self.tratamiento)
        form.addRow("Observaciones:", self.observaciones)

    # ----- Lista de pacientes (se carga en un hilo) -----
    def cargar_combos(self):
        ejecutar_en_hilo(repositorio.pacientes_combo, al_terminar=self._llenar_combo)

    def _llenar_combo(self, pacientes):
        """Llena la lista desplegable conservando la selección actual."""
        actual = self.combo_paciente.currentData()
        self.combo_paciente.blockSignals(True)
        self.combo_paciente.clear()
        self.combo_paciente.addItem("Seleccione un paciente...", None)
        for id_paciente, texto in pacientes:
            self.combo_paciente.addItem(texto, id_paciente)
        indice = self.combo_paciente.findData(actual)
        self.combo_paciente.setCurrentIndex(indice if indice >= 0 else 0)
        self.combo_paciente.blockSignals(False)

    def leer_formulario(self):
        return {
            "id_paciente": self.combo_paciente.currentData(),
            "fecha": self.fecha.date().toPython(),
            "motivo": self.motivo.text().strip(),
            "sintomas": self.sintomas.toPlainText().strip(),
            "diagnostico": self.diagnostico.toPlainText().strip(),
            "tratamiento": self.tratamiento.toPlainText().strip(),
            "observaciones": self.observaciones.toPlainText().strip(),
        }

    def poner_formulario(self, fila):
        (_id, id_paciente, _nombre, fecha, motivo, sintomas, diagnostico,
         tratamiento, observaciones) = fila
        self.combo_paciente.setCurrentIndex(max(0, self.combo_paciente.findData(id_paciente)))
        if fecha:
            self.fecha.setDate(QDate(fecha.year, fecha.month, fecha.day))
        self.motivo.setText(motivo or "")
        self.sintomas.setPlainText(sintomas or "")
        self.diagnostico.setPlainText(diagnostico or "")
        self.tratamiento.setPlainText(tratamiento or "")
        self.observaciones.setPlainText(observaciones or "")

    def limpiar_formulario(self):
        self.combo_paciente.setCurrentIndex(0)
        self.fecha.setDate(QDate.currentDate())
        self.motivo.clear()
        for campo in (self.sintomas, self.diagnostico, self.tratamiento, self.observaciones):
            campo.clear()

    def fila_a_textos(self, fila):
        t = super().fila_a_textos(fila)
        if fila[3]:
            t[3] = fila[3].strftime("%d/%m/%Y")
        return t

    # ----- Conexión con validaciones y repositorio (ORM) -----
    def validar(self, datos):
        return validar_consulta(datos)

    def fn_listar(self, filtro):
        return repositorio.listar_consultas(filtro)

    def fn_crear(self, datos):
        return repositorio.crear_consulta(datos)

    def fn_actualizar(self, id_registro, datos):
        return repositorio.actualizar_consulta(id_registro, datos)

    def fn_eliminar(self, id_registro):
        return repositorio.eliminar_consulta(id_registro)
