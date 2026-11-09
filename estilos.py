"""
estilos.py
Hoja de estilos (CSS de Qt) única de todo el sistema. Se aplica una sola vez
con app.setStyleSheet(GENERAL) y llega a todas las ventanas.

Los widgets se estilizan de dos formas:
  - Por clase:   QLineEdit { ... }            (todos los campos de texto)
  - Por nombre:  QPushButton#peligro { ... }  (solo el botón con setObjectName("peligro"))
"""

GENERAL = """
/* ============ BASE ============ */
QWidget {
    background-color: #EEF7F2;
    color: #26332D;
    font-family: Arial;
    font-size: 13px;
}
QLabel, QCheckBox {
    background-color: transparent;
}
QDialog, QMessageBox {
    background-color: #EEF7F2;
}

/* ============ BARRA LATERAL ============ */
QFrame#sidebar {
    background-color: #176B4D;
}
QFrame#sidebar QLabel {
    background-color: transparent;
}
QLabel#marca {
    color: white;
    font-size: 21px;
    font-weight: bold;
    padding: 10px;
}
QPushButton#menu {
    text-align: left;
    background-color: transparent;
    color: white;
    border: none;
    border-radius: 7px;
    padding: 14px;
    font-size: 15px;
}
QPushButton#menu:hover {
    background-color: #218C65;
}
QPushButton#activo {
    text-align: left;
    background-color: #0F5139;
    color: white;
    border: none;
    border-radius: 7px;
    padding: 14px;
    font-size: 15px;
    font-weight: bold;
}

/* ============ TEXTOS ============ */
QLabel#titulo {
    color: #176B4D;
    font-size: 26px;
    font-weight: bold;
}
QLabel#subtitulo {
    color: #5A6B63;
    font-size: 14px;
}
QLabel#estado {
    color: #5A6B63;
    font-size: 12px;
}
QLabel#cifra {
    color: #176B4D;
    font-size: 38px;
    font-weight: bold;
}
QLabel#etiqueta_tarjeta {
    color: #606060;
    font-size: 13px;
}

/* ============ TARJETAS Y CAJAS ============ */
QFrame#tarjeta {
    background-color: white;
    border: 1px solid #C9E1D5;
    border-radius: 12px;
}
QFrame#tarjeta QLabel {
    background-color: transparent;
    border: none;
}
QGroupBox {
    background-color: white;
    border: 1px solid #C9E1D5;
    border-radius: 8px;
    margin-top: 12px;
    padding: 14px;
    font-weight: bold;
    color: #176B4D;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
    background-color: #EEF7F2;
}
QGroupBox QLabel {
    background-color: transparent;
    color: #26332D;
    font-weight: normal;
}

/* ============ CAMPOS DE ENTRADA ============ */
QLineEdit, QTextEdit, QComboBox, QDateEdit {
    background-color: #FFFFFF;
    border: 1px solid #BFD8CB;
    border-radius: 6px;
    padding: 7px;
    min-height: 20px;
}
QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QDateEdit:focus {
    border: 2px solid #176B4D;
    background-color: #F7FFFB;
}
QComboBox QAbstractItemView {
    background-color: white;
    selection-background-color: #176B4D;
    selection-color: white;
}

/* ============ BOTONES ============ */
QPushButton {
    background-color: #E1EEE7;
    color: #26332D;
    border: none;
    border-radius: 6px;
    padding: 9px 16px;
}
QPushButton:hover {
    background-color: #CFE5DA;
}
QPushButton:disabled {
    background-color: #E7ECE9;
    color: #9AA8A0;
}
QPushButton#principal {
    background-color: #176B4D;
    color: white;
}
QPushButton#principal:hover {
    background-color: #218C65;
}
QPushButton#principal:pressed {
    background-color: #0F5139;
}
QPushButton#principal:disabled {
    background-color: #9CC2B1;
    color: white;
}
QPushButton#secundario {
    background-color: #E1EEE7;
    color: #26332D;
}
QPushButton#peligro {
    background-color: #C0392B;
    color: white;
}
QPushButton#peligro:hover {
    background-color: #A5301F;
}
QPushButton#peligro:disabled {
    background-color: #E2B4AE;
    color: white;
}

/* ============ TABLAS ============ */
QTableWidget {
    background-color: white;
    alternate-background-color: #F0F8F4;
    gridline-color: #C9DDD3;
    border: 1px solid #BFD8CB;
    border-radius: 6px;
    font-size: 13px;
}
QTableWidget::item:selected {
    background-color: #BDE2D0;
    color: #123D2C;
}
QHeaderView::section {
    background-color: #176B4D;
    color: white;
    padding: 8px;
    border: 1px solid #0F5139;
    font-weight: bold;
}

/* ============ BARRAS DE DESPLAZAMIENTO ============ */
QScrollBar:vertical {
    background-color: #DCEDE5;
    width: 12px;
    margin: 2px;
}
QScrollBar::handle:vertical {
    background-color: #176B4D;
    min-height: 30px;
    border-radius: 5px;
}
QScrollBar:horizontal {
    background-color: #DCEDE5;
    height: 12px;
    margin: 2px;
}
QScrollBar::handle:horizontal {
    background-color: #176B4D;
    min-width: 30px;
    border-radius: 5px;
}
"""
