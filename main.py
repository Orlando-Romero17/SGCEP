"""
main.py
Punto de entrada del sistema. Crea la ventana principal con un menú lateral y un
QStackedWidget que muestra una pantalla a la vez:
  Inicio, Pacientes, Consultas, Tratamientos, Expedientes y Reportes.

Ejecutar con:  python main.py
"""
import sys
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QFrame, QHBoxLayout, QVBoxLayout,
    QLabel, QPushButton, QStackedWidget, QMessageBox
)
from estilos import GENERAL
from modelos import crear_tablas
from hilos.trabajador import ejecutar_en_hilo
import repositorio
from paginas.pacientes import PaginaPacientes
from paginas.consultas import PaginaConsultas
from paginas.tratamientos import PaginaTratamientos
from paginas.expedientes import PaginaExpedientes
from paginas.reportes import PaginaReportes


class PaginaInicio(QWidget):
    """Pantalla de bienvenida con las estadísticas del sistema."""

    def __init__(self):
        super().__init__()
        raiz = QVBoxLayout(self)
        raiz.setContentsMargins(45, 40, 45, 40)
        raiz.setSpacing(14)

        titulo = QLabel("Sistema Gestor de Consultas y Expedientes")
        titulo.setObjectName("titulo")
        raiz.addWidget(titulo)
        sub = QLabel("Administración de pacientes, consultas y expedientes médicos")
        sub.setObjectName("subtitulo")
        raiz.addWidget(sub)

        # ----- Tarjetas con los totales (se llenan desde la base de datos) -----
        tarjetas = QHBoxLayout()
        tarjetas.setSpacing(18)
        self.cifras = {}
        for clave, etiqueta in (("pacientes", "Pacientes registrados"),
                                ("consultas", "Consultas registradas"),
                                ("tratamientos", "Tratamientos registrados"),
                                ("consultas_mes", "Consultas (últimos 30 días)")):
            tarjeta = QFrame()
            tarjeta.setObjectName("tarjeta")
            lay = QVBoxLayout(tarjeta)
            lay.setContentsMargins(22, 22, 22, 22)
            cifra = QLabel("0")
            cifra.setObjectName("cifra")
            cifra.setAlignment(Qt.AlignCenter)
            texto = QLabel(etiqueta)
            texto.setObjectName("etiqueta_tarjeta")
            texto.setAlignment(Qt.AlignCenter)
            lay.addWidget(cifra)
            lay.addWidget(texto)
            tarjetas.addWidget(tarjeta)
            self.cifras[clave] = cifra
        raiz.addLayout(tarjetas)

        bienvenida = QFrame()
        bienvenida.setObjectName("tarjeta")
        bl = QVBoxLayout(bienvenida)
        bl.setContentsMargins(30, 30, 30, 30)
        t = QLabel("Bienvenido al sistema")
        t.setObjectName("titulo")
        t.setAlignment(Qt.AlignCenter)
        d = QLabel("Use el menú lateral para registrar pacientes, anotar consultas, "
                   "asignar tratamientos y consultar los expedientes médicos.")
        d.setWordWrap(True)
        d.setAlignment(Qt.AlignCenter)
        bl.addWidget(t)
        bl.addWidget(d)
        raiz.addWidget(bienvenida)
        raiz.addStretch()

        self.al_mostrar()

    def al_mostrar(self):
        """Pide las estadísticas (ORM) en segundo plano."""
        ejecutar_en_hilo(
            repositorio.estadisticas,
            al_terminar=self._mostrar,
            al_error=lambda m: print("Error:", m),
        )

    def _mostrar(self, datos):
        for clave, cifra in self.cifras.items():
            cifra.setText(str(datos.get(clave, 0)))


class MenuPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SGCEP - Sistema Gestor de Consultas y Expedientes de Pacientes")
        self.setMinimumSize(1000, 650)
        self.resize(1250, 780)

        # Páginas del sistema (el orden coincide con los botones del menú)
        self.stack = QStackedWidget()
        self.stack.addWidget(PaginaInicio())          # 0
        self.stack.addWidget(PaginaPacientes())       # 1
        self.stack.addWidget(PaginaConsultas())       # 2
        self.stack.addWidget(PaginaTratamientos())    # 3
        self.stack.addWidget(PaginaExpedientes())     # 4
        self.stack.addWidget(PaginaReportes())        # 5
        # Al cambiar de página se recargan sus datos
        self.stack.currentChanged.connect(self._refrescar)

        central = QWidget()
        self.setCentralWidget(central)
        principal = QHBoxLayout(central)
        principal.setContentsMargins(0, 0, 0, 0)
        principal.setSpacing(0)
        principal.addWidget(self._crear_menu())
        principal.addWidget(self.stack, 1)

    def _crear_menu(self):
        """Barra lateral: un botón por pantalla y el botón Salir."""
        menu = QFrame()
        menu.setObjectName("sidebar")
        menu.setFixedWidth(250)
        lay = QVBoxLayout(menu)
        lay.setContentsMargins(15, 25, 15, 25)
        lay.setSpacing(8)

        marca = QLabel("SISTEMA\nGESTOR DE\nPACIENTES")
        marca.setObjectName("marca")
        marca.setAlignment(Qt.AlignCenter)
        lay.addWidget(marca)
        lay.addSpacing(25)

        self.botones = []
        for i, texto in enumerate(["Inicio", "Pacientes", "Consultas",
                                   "Tratamientos", "Expedientes", "Reportes"]):
            b = QPushButton(texto)
            b.clicked.connect(lambda _=False, idx=i: self.stack.setCurrentIndex(idx))
            lay.addWidget(b)
            self.botones.append(b)
        self._marcar_activo(0)

        lay.addStretch()
        salir = QPushButton("Salir")
        salir.setObjectName("menu")
        salir.clicked.connect(self.salir)
        lay.addWidget(salir)
        return menu

    def _marcar_activo(self, indice):
        """Resalta el botón de la página visible."""
        for i, b in enumerate(self.botones):
            b.setObjectName("activo" if i == indice else "menu")
            b.style().unpolish(b)
            b.style().polish(b)

    def _refrescar(self, indice):
        self._marcar_activo(indice)
        pagina = self.stack.widget(indice)
        if hasattr(pagina, "al_mostrar"):
            pagina.al_mostrar()

    def salir(self):
        r = QMessageBox.question(
            self, "Salir", "¿Está seguro de que desea salir del sistema?",
            QMessageBox.Yes | QMessageBox.No)
        if r == QMessageBox.Yes:
            self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(GENERAL)

    # Crea las tablas si no existen; si la base de datos no responde, avisa y sale
    try:
        crear_tablas()
    except Exception as e:
        QMessageBox.critical(
            None, "Error de base de datos",
            "No se pudo conectar con la base de datos.\n\n"
            "Revise que MySQL esté encendido y que el archivo .env tenga los "
            f"datos correctos.\n\nDetalle: {e}")
        sys.exit(1)

    ventana = MenuPrincipal()
    ventana.show()
    sys.exit(app.exec())
