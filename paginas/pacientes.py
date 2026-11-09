"""
pacientes.py
Pantalla de gestión de pacientes (CRUD completo con ORM).
Hereda de PaginaCrud: solo define los campos, las validaciones y qué funciones
del repositorio se usan.
"""
from PySide6.QtCore import QDate
from PySide6.QtWidgets import QLineEdit, QComboBox, QDateEdit, QTextEdit
import repositorio
from validaciones import validar_paciente, TIPOS_SANGRE
from paginas.base_crud import PaginaCrud


class PaginaPacientes(PaginaCrud):
    TITULO = "Gestión de pacientes"
    SUBTITULO = "Registre, consulte, actualice y elimine los datos de los pacientes."
    COLUMNAS = ["ID", "CÉDULA", "NOMBRE", "APELLIDO", "NACIMIENTO", "SEXO",
                "TELÉFONO", "DIRECCIÓN", "CORREO", "SANGRE", "ALERGIAS"]
    PLACEHOLDER = "Buscar por cédula, nombre o apellido..."
    NOMBRE_EXPORTAR = "pacientes"
    NOMBRE_ELEMENTO = "paciente"

    def construir_formulario(self, form):
        """Campos del formulario de pacientes."""
        self.cedula = QLineEdit()
        self.cedula.setPlaceholderText("Ejemplo: 001-230926-0001A")
        self.nombre = QLineEdit()
        self.apellido = QLineEdit()

        self.fecha = QDateEdit()
        self.fecha.setCalendarPopup(True)
        self.fecha.setDisplayFormat("dd/MM/yyyy")
        self.fecha.setMaximumDate(QDate.currentDate())   # no permite fechas futuras
        self.fecha.setDate(QDate(2000, 1, 1))

        self.sexo = QComboBox()
        self.sexo.addItem("Seleccione...", "")
        self.sexo.addItem("Masculino", "M")
        self.sexo.addItem("Femenino", "F")

        self.telefono = QLineEdit()
        self.telefono.setPlaceholderText("Ejemplo: 8888-8888")
        self.direccion = QLineEdit()
        self.correo = QLineEdit()
        self.correo.setPlaceholderText("ejemplo@correo.com")

        self.sangre = QComboBox()
        self.sangre.addItem("Seleccione...", "")
        for tipo in TIPOS_SANGRE:
            self.sangre.addItem(tipo, tipo)

        self.alergias = QTextEdit()
        self.alergias.setFixedHeight(55)

        form.addRow("Cédula:", self.cedula)
        form.addRow("Nombre:", self.nombre)
        form.addRow("Apellido:", self.apellido)
        form.addRow("Fecha de nacimiento:", self.fecha)
        form.addRow("Sexo:", self.sexo)
        form.addRow("Teléfono:", self.telefono)
        form.addRow("Dirección:", self.direccion)
        form.addRow("Correo:", self.correo)
        form.addRow("Tipo de sangre:", self.sangre)
        form.addRow("Alergias:", self.alergias)

    def leer_formulario(self):
        """Lee los campos y los convierte a los tipos que espera el ORM."""
        return {
            "cedula": self.cedula.text().strip(),
            "nombre": self.nombre.text().strip(),
            "apellido": self.apellido.text().strip(),
            "fecha_nacimiento": self.fecha.date().toPython(),   # QDate -> date
            "sexo": self.sexo.currentData() or "",
            "telefono": self.telefono.text().strip(),
            "direccion": self.direccion.text().strip(),
            "correo": self.correo.text().strip(),
            "tipo_sangre": self.sangre.currentData() or "",
            "alergias": self.alergias.toPlainText().strip(),
        }

    def poner_formulario(self, fila):
        """Llena el formulario con la fila seleccionada de la tabla."""
        (_id, cedula, nombre, apellido, nacimiento, sexo, telefono,
         direccion, correo, sangre, alergias) = fila
        self.cedula.setText(cedula or "")
        self.nombre.setText(nombre or "")
        self.apellido.setText(apellido or "")
        if nacimiento:
            self.fecha.setDate(QDate(nacimiento.year, nacimiento.month, nacimiento.day))
        self.sexo.setCurrentIndex(max(0, self.sexo.findData(sexo or "")))
        self.telefono.setText(telefono or "")
        self.direccion.setText(direccion or "")
        self.correo.setText(correo or "")
        self.sangre.setCurrentIndex(max(0, self.sangre.findData(sangre or "")))
        self.alergias.setPlainText(alergias or "")

    def limpiar_formulario(self):
        for campo in (self.cedula, self.nombre, self.apellido, self.telefono,
                      self.direccion, self.correo):
            campo.clear()
        self.fecha.setDate(QDate(2000, 1, 1))
        self.sexo.setCurrentIndex(0)
        self.sangre.setCurrentIndex(0)
        self.alergias.clear()

    def fila_a_textos(self, fila):
        """Muestra la fecha como dd/mm/aaaa y el sexo con su nombre completo."""
        t = super().fila_a_textos(fila)
        if fila[4]:
            t[4] = fila[4].strftime("%d/%m/%Y")
        t[5] = {"M": "Masculino", "F": "Femenino"}.get(fila[5], t[5])
        return t

    # ----- Conexión con validaciones y repositorio (ORM) -----
    def validar(self, datos):
        return validar_paciente(datos)

    def fn_listar(self, filtro):
        return repositorio.listar_pacientes(filtro)

    def fn_crear(self, datos):
        return repositorio.crear_paciente(datos)

    def fn_actualizar(self, id_registro, datos):
        return repositorio.actualizar_paciente(id_registro, datos)

    def fn_eliminar(self, id_registro):
        return repositorio.eliminar_paciente(id_registro)
