"""
tratamientos.py
Pantalla de tratamientos (CRUD completo con ORM): medicamento, dosis, frecuencia,
duración e indicaciones de cada paciente.
"""
from PySide6.QtWidgets import QLineEdit, QComboBox, QTextEdit
import repositorio
from validaciones import validar_tratamiento
from hilos.trabajador import ejecutar_en_hilo
from paginas.base_crud import PaginaCrud


class PaginaTratamientos(PaginaCrud):
    TITULO = "Tratamientos"
    SUBTITULO = "Administre los medicamentos e indicaciones asignados a cada paciente."
    COLUMNAS = ["ID", "ID PACIENTE", "PACIENTE", "MEDICAMENTO", "DOSIS",
                "FRECUENCIA", "DURACIÓN", "INDICACIONES"]
    COLUMNAS_OCULTAS = [1]
    PLACEHOLDER = "Buscar por paciente, cédula o medicamento..."
    NOMBRE_EXPORTAR = "tratamientos"
    NOMBRE_ELEMENTO = "tratamiento"

    def construir_formulario(self, form):
        self.combo_paciente = QComboBox()
        self.medicamento = QLineEdit()
        self.dosis = QLineEdit()
        self.dosis.setPlaceholderText("Ejemplo: 500 mg")
        self.frecuencia = QLineEdit()
        self.frecuencia.setPlaceholderText("Ejemplo: Cada 8 horas")
        self.duracion = QLineEdit()
        self.duracion.setPlaceholderText("Ejemplo: 5 días")
        self.indicaciones = QTextEdit()
        self.indicaciones.setFixedHeight(55)

        form.addRow("Paciente:", self.combo_paciente)
        form.addRow("Medicamento:", self.medicamento)
        form.addRow("Dosis:", self.dosis)
        form.addRow("Frecuencia:", self.frecuencia)
        form.addRow("Duración:", self.duracion)
        form.addRow("Indicaciones:", self.indicaciones)

    def cargar_combos(self):
        ejecutar_en_hilo(repositorio.pacientes_combo, al_terminar=self._llenar_combo)

    def _llenar_combo(self, pacientes):
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
            "medicamento": self.medicamento.text().strip(),
            "dosis": self.dosis.text().strip(),
            "frecuencia": self.frecuencia.text().strip(),
            "duracion": self.duracion.text().strip(),
            "indicaciones": self.indicaciones.toPlainText().strip(),
        }

    def poner_formulario(self, fila):
        (_id, id_paciente, _nombre, medicamento, dosis, frecuencia,
         duracion, indicaciones) = fila
        self.combo_paciente.setCurrentIndex(max(0, self.combo_paciente.findData(id_paciente)))
        self.medicamento.setText(medicamento or "")
        self.dosis.setText(dosis or "")
        self.frecuencia.setText(frecuencia or "")
        self.duracion.setText(duracion or "")
        self.indicaciones.setPlainText(indicaciones or "")

    def limpiar_formulario(self):
        self.combo_paciente.setCurrentIndex(0)
        for campo in (self.medicamento, self.dosis, self.frecuencia, self.duracion):
            campo.clear()
        self.indicaciones.clear()

    def validar(self, datos):
        return validar_tratamiento(datos)

    def fn_listar(self, filtro):
        return repositorio.listar_tratamientos(filtro)

    def fn_crear(self, datos):
        return repositorio.crear_tratamiento(datos)

    def fn_actualizar(self, id_registro, datos):
        return repositorio.actualizar_tratamiento(id_registro, datos)

    def fn_eliminar(self, id_registro):
        return repositorio.eliminar_tratamiento(id_registro)
