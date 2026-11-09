"""
base_crud.py
Clase base para las pantallas con CRUD (pacientes, consultas, tratamientos).
Aquí está TODO lo que se repite en las tres pantallas:
  - formulario + botones Agregar / Actualizar / Eliminar / Limpiar / Exportar
  - cuadro de búsqueda que filtra mientras se escribe
  - tabla de resultados (se carga en un hilo para no congelar la ventana)
  - validaciones con QMessageBox y confirmación antes de eliminar

Cada pantalla hija solo define sus campos y las funciones del repositorio.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QGroupBox, QFormLayout, QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView, QMessageBox
)
from hilos.trabajador import ejecutar_en_hilo
from utilidades import exportar_tabla


class PaginaCrud(QWidget):
    # ----- Lo que cada pantalla hija debe definir -----
    TITULO = ""
    SUBTITULO = ""
    COLUMNAS = []            # encabezados de la tabla
    COLUMNAS_OCULTAS = []    # índices de columnas que no se muestran (ej. ids)
    PLACEHOLDER = "Buscar..."
    NOMBRE_EXPORTAR = "datos"
    NOMBRE_ELEMENTO = "registro"

    def __init__(self):
        super().__init__()
        self._peticion = 0       # contador para descartar respuestas viejas
        self._filas = []         # filas (tuplas) que muestra la tabla
        self._id_actual = None   # id del registro seleccionado

        raiz = QVBoxLayout(self)
        raiz.setContentsMargins(30, 25, 30, 25)
        raiz.setSpacing(10)

        titulo = QLabel(self.TITULO)
        titulo.setObjectName("titulo")
        raiz.addWidget(titulo)
        subtitulo = QLabel(self.SUBTITULO)
        subtitulo.setObjectName("subtitulo")
        raiz.addWidget(subtitulo)

        # ----- Formulario (lo construye la pantalla hija) -----
        grupo = QGroupBox("Datos")
        self.form = QFormLayout(grupo)
        self.construir_formulario(self.form)
        raiz.addWidget(grupo)

        # ----- Botones de acción del CRUD -----
        botones = QHBoxLayout()
        self.btn_agregar = QPushButton("Agregar")
        self.btn_agregar.setObjectName("principal")
        self.btn_agregar.clicked.connect(self.agregar)
        self.btn_actualizar = QPushButton("Actualizar")
        self.btn_actualizar.setObjectName("principal")
        self.btn_actualizar.clicked.connect(self.actualizar)
        self.btn_eliminar = QPushButton("Eliminar")
        self.btn_eliminar.setObjectName("peligro")
        self.btn_eliminar.clicked.connect(self.eliminar)
        self.btn_limpiar = QPushButton("Limpiar")
        self.btn_limpiar.setObjectName("secundario")
        self.btn_limpiar.clicked.connect(self.limpiar)
        self.btn_exportar = QPushButton("Exportar")
        self.btn_exportar.setObjectName("secundario")
        self.btn_exportar.clicked.connect(
            lambda: exportar_tabla(self, self.tabla, self.NOMBRE_EXPORTAR))
        for b in (self.btn_agregar, self.btn_actualizar, self.btn_eliminar,
                  self.btn_limpiar):
            botones.addWidget(b)
        botones.addStretch()
        botones.addWidget(self.btn_exportar)
        raiz.addLayout(botones)

        # Actualizar y Eliminar solo se habilitan al seleccionar una fila
        self.btn_actualizar.setEnabled(False)
        self.btn_eliminar.setEnabled(False)

        # ----- Búsqueda -----
        self.buscar = QLineEdit()
        self.buscar.setPlaceholderText(self.PLACEHOLDER)
        self.buscar.textChanged.connect(self.recargar)   # filtra mientras se escribe
        raiz.addWidget(self.buscar)

        # ----- Tabla -----
        self.tabla = QTableWidget(0, len(self.COLUMNAS))
        self.tabla.setHorizontalHeaderLabels(self.COLUMNAS)
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabla.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tabla.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabla.setAlternatingRowColors(True)
        for c in self.COLUMNAS_OCULTAS:
            self.tabla.setColumnHidden(c, True)
        self.tabla.itemSelectionChanged.connect(self._seleccionar)
        raiz.addWidget(self.tabla, 1)

        # Mensaje de estado ("Cargando...", "12 registro(s)", errores)
        self.estado = QLabel("")
        self.estado.setObjectName("estado")
        raiz.addWidget(self.estado)

        self.al_mostrar()

    # =================================================================
    # Métodos que la pantalla hija debe implementar
    # =================================================================
    def construir_formulario(self, form):
        raise NotImplementedError

    def leer_formulario(self):
        """Devuelve un diccionario con los datos del formulario."""
        raise NotImplementedError

    def poner_formulario(self, fila):
        """Coloca en el formulario los datos de la fila seleccionada."""
        raise NotImplementedError

    def limpiar_formulario(self):
        raise NotImplementedError

    def validar(self, datos):
        """Devuelve la lista de errores de validación (vacía si todo está bien)."""
        raise NotImplementedError

    def fn_listar(self, filtro):
        raise NotImplementedError

    def fn_crear(self, datos):
        raise NotImplementedError

    def fn_actualizar(self, id_registro, datos):
        raise NotImplementedError

    def fn_eliminar(self, id_registro):
        raise NotImplementedError

    def fila_a_textos(self, fila):
        """Convierte una fila en los textos que se muestran en la tabla."""
        return ["" if v is None else str(v) for v in fila]

    def cargar_combos(self):
        """Las pantallas con listas de pacientes la sobrescriben."""
        pass

    # =================================================================
    # Carga de datos en segundo plano
    # =================================================================
    def al_mostrar(self):
        """Se llama al crear la pantalla y cada vez que se vuelve a ella."""
        self.cargar_combos()
        self.recargar()

    def recargar(self):
        """Lanza la consulta (ORM) en un hilo para no congelar la ventana."""
        self._peticion += 1
        numero = self._peticion
        self.estado.setText("Cargando...")
        ejecutar_en_hilo(
            self.fn_listar, self.buscar.text().strip(),
            al_terminar=lambda filas, n=numero: self._mostrar(filas, n),
            al_error=self._mostrar_error,
        )

    def _mostrar(self, filas, numero):
        """Pinta los resultados (si no llegó una respuesta más nueva)."""
        if numero != self._peticion:
            return
        self._filas = filas
        self.tabla.blockSignals(True)
        self.tabla.setRowCount(len(filas))
        for i, fila in enumerate(filas):
            for j, texto in enumerate(self.fila_a_textos(fila)):
                self.tabla.setItem(i, j, QTableWidgetItem(texto))
        self.tabla.blockSignals(False)
        self.estado.setText(f"{len(filas)} registro(s)")

    def _mostrar_error(self, mensaje):
        self.estado.setText(f"Error: {mensaje}")

    # =================================================================
    # Selección de una fila
    # =================================================================
    def _seleccionar(self):
        fila = self.tabla.currentRow()
        if fila < 0 or fila >= len(self._filas):
            return
        registro = self._filas[fila]
        self._id_actual = registro[0]
        self.poner_formulario(registro)
        self.btn_actualizar.setEnabled(True)
        self.btn_eliminar.setEnabled(True)
        self.btn_agregar.setEnabled(False)   # evita duplicar un registro existente

    # =================================================================
    # Acciones del CRUD
    # =================================================================
    def agregar(self):
        """CREATE: valida, guarda y refresca la tabla."""
        datos = self.leer_formulario()
        errores = self.validar(datos)
        if errores:
            QMessageBox.warning(self, "Validación", "\n".join(errores))
            return
        try:
            self.fn_crear(datos)
        except ValueError as e:        # regla de negocio (ej. cédula repetida)
            QMessageBox.warning(self, "No se pudo guardar", str(e))
        except Exception as e:         # error inesperado (ej. base de datos caída)
            QMessageBox.critical(self, "Error", f"Error al guardar:\n{e}")
        else:
            QMessageBox.information(
                self, "Guardado", f"El {self.NOMBRE_ELEMENTO} se guardó correctamente.")
            self.limpiar()
            self.recargar()

    def actualizar(self):
        """UPDATE: valida y modifica el registro seleccionado."""
        if self._id_actual is None:
            QMessageBox.information(
                self, "Actualizar", f"Seleccione un {self.NOMBRE_ELEMENTO} de la tabla.")
            return
        datos = self.leer_formulario()
        errores = self.validar(datos)
        if errores:
            QMessageBox.warning(self, "Validación", "\n".join(errores))
            return
        try:
            self.fn_actualizar(self._id_actual, datos)
        except ValueError as e:
            QMessageBox.warning(self, "No se pudo actualizar", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al actualizar:\n{e}")
        else:
            QMessageBox.information(
                self, "Actualizado", f"El {self.NOMBRE_ELEMENTO} se actualizó correctamente.")
            self.limpiar()
            self.recargar()

    def eliminar(self):
        """DELETE: pide confirmación y elimina el registro seleccionado."""
        if self._id_actual is None:
            QMessageBox.information(
                self, "Eliminar", f"Seleccione un {self.NOMBRE_ELEMENTO} de la tabla.")
            return
        respuesta = QMessageBox.question(
            self, "Eliminar",
            f"¿Está seguro de que desea eliminar este {self.NOMBRE_ELEMENTO}?\n"
            "Esta acción no se puede deshacer.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if respuesta != QMessageBox.Yes:
            return
        try:
            self.fn_eliminar(self._id_actual)
        except ValueError as e:        # ej. paciente con historial
            QMessageBox.warning(self, "No se pudo eliminar", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al eliminar:\n{e}")
        else:
            QMessageBox.information(
                self, "Eliminado", f"El {self.NOMBRE_ELEMENTO} se eliminó correctamente.")
            self.limpiar()
            self.recargar()

    def limpiar(self):
        """Vacía el formulario y vuelve al modo 'agregar'."""
        self._id_actual = None
        self.limpiar_formulario()
        self.tabla.clearSelection()
        self.btn_actualizar.setEnabled(False)
        self.btn_eliminar.setEnabled(False)
        self.btn_agregar.setEnabled(True)
