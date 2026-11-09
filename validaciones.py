"""
validaciones.py
Reglas de validación de los formularios. Son funciones puras (no usan la
interfaz ni la base de datos), por eso se pueden probar de forma automática.

Cada función recibe un diccionario con los datos del formulario y devuelve una
LISTA de mensajes de error. Si la lista está vacía, los datos son válidos.
"""
import re
from datetime import date

# Cédula nicaragüense: 001-230926-0001A (3 dígitos, 6 dígitos, 4 dígitos y letra)
RE_CEDULA = re.compile(r"^\d{3}-\d{6}-\d{4}[A-Za-z]$")
RE_CORREO = re.compile(r"^[\w.+-]+@[\w-]+(\.[\w-]+)+$")
RE_TELEFONO = re.compile(r"^\d{4}-?\d{4}$")
RE_NOMBRE = re.compile(r"^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ' ]+$")

TIPOS_SANGRE = ("A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-")


def validar_paciente(d, hoy=None):
    """Valida los datos de un paciente. Devuelve la lista de errores."""
    hoy = hoy or date.today()
    errores = []

    cedula = (d.get("cedula") or "").strip()
    if not cedula:
        errores.append("La cédula es obligatoria.")
    elif not RE_CEDULA.match(cedula):
        errores.append("La cédula debe tener el formato 001-230926-0001A.")

    for campo, etiqueta in (("nombre", "El nombre"), ("apellido", "El apellido")):
        valor = (d.get(campo) or "").strip()
        if not valor:
            errores.append(f"{etiqueta} es obligatorio.")
        elif not RE_NOMBRE.match(valor):
            errores.append(f"{etiqueta} solo puede contener letras.")

    fecha = d.get("fecha_nacimiento")
    if not isinstance(fecha, date):
        errores.append("La fecha de nacimiento es obligatoria.")
    elif fecha > hoy:
        errores.append("La fecha de nacimiento no puede ser futura.")
    elif (hoy.year - fecha.year) > 120:
        errores.append("La fecha de nacimiento no es realista (más de 120 años).")

    if d.get("sexo") not in ("M", "F"):
        errores.append("Seleccione el sexo del paciente.")

    telefono = (d.get("telefono") or "").strip()
    if telefono and not RE_TELEFONO.match(telefono):
        errores.append("El teléfono debe tener 8 dígitos (ejemplo: 8888-8888).")

    correo = (d.get("correo") or "").strip()
    if correo and not RE_CORREO.match(correo):
        errores.append("El correo electrónico no es válido.")

    sangre = (d.get("tipo_sangre") or "").strip()
    if sangre and sangre not in TIPOS_SANGRE:
        errores.append("El tipo de sangre no es válido.")

    return errores


def validar_consulta(d, hoy=None):
    """Valida los datos de una consulta médica."""
    hoy = hoy or date.today()
    errores = []

    if not d.get("id_paciente"):
        errores.append("Seleccione el paciente de la consulta.")

    fecha = d.get("fecha")
    if not isinstance(fecha, date):
        errores.append("La fecha de la consulta es obligatoria.")
    elif fecha > hoy:
        errores.append("La fecha de la consulta no puede ser futura.")

    for campo, etiqueta in (
        ("motivo", "El motivo"), ("sintomas", "Los síntomas"),
        ("diagnostico", "El diagnóstico"), ("tratamiento", "El tratamiento"),
    ):
        if not (d.get(campo) or "").strip():
            errores.append(f"{etiqueta} es obligatorio.")

    return errores


def validar_tratamiento(d):
    """Valida los datos de un tratamiento."""
    errores = []

    if not d.get("id_paciente"):
        errores.append("Seleccione el paciente del tratamiento.")

    for campo, mensaje in (
        ("medicamento", "El medicamento es obligatorio."),
        ("dosis", "La dosis es obligatoria."),
        ("frecuencia", "La frecuencia es obligatoria."),
        ("duracion", "La duración es obligatoria."),
    ):
        if not (d.get(campo) or "").strip():
            errores.append(mensaje)

    return errores
