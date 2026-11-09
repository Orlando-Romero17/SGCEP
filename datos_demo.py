"""
datos_demo.py
Carga datos de prueba (ficticios) en la base de datos usando el ORM.
Útil para la demostración y las capturas del informe.

Ejecutar con:  python datos_demo.py
Es seguro ejecutarlo varias veces: no repite pacientes que ya existen.
"""
from datetime import date
from modelos import crear_tablas
import repositorio

PACIENTES = [
    dict(cedula="001-150295-0001A", nombre="María", apellido="López",
         fecha_nacimiento=date(1995, 2, 15), sexo="F", telefono="8888-1111",
         direccion="Managua, Villa Fontana", correo="maria.lopez@correo.com",
         tipo_sangre="O+", alergias="Penicilina"),
    dict(cedula="001-030388-0002B", nombre="Carlos", apellido="Gómez",
         fecha_nacimiento=date(1988, 3, 3), sexo="M", telefono="8888-2222",
         direccion="León, Barrio Subtiava", correo="carlos.gomez@correo.com",
         tipo_sangre="A+", alergias="Ninguna"),
    dict(cedula="281-101200-0003C", nombre="Ana", apellido="Martínez",
         fecha_nacimiento=date(2000, 12, 10), sexo="F", telefono="8888-3333",
         direccion="Chinandega, Centro", correo="ana.martinez@correo.com",
         tipo_sangre="B+", alergias="Polvo"),
    dict(cedula="401-220575-0004D", nombre="José", apellido="Pérez",
         fecha_nacimiento=date(1975, 5, 22), sexo="M", telefono="8888-4444",
         direccion="Masaya, Barrio Monimbó", correo="", tipo_sangre="AB-",
         alergias="Ninguna"),
]

CONSULTAS = [  # (cédula del paciente, datos de la consulta)
    ("001-150295-0001A", dict(fecha=date(2026, 9, 23), motivo="Dolor de cabeza",
        sintomas="Dolor de cabeza y fiebre", diagnostico="Infección viral",
        tratamiento="Reposo e hidratación", observaciones="Control en 3 días")),
    ("001-150295-0001A", dict(fecha=date(2026, 10, 15), motivo="Control",
        sintomas="Ninguno", diagnostico="Paciente recuperada",
        tratamiento="Ninguno", observaciones="Alta médica")),
    ("001-030388-0002B", dict(fecha=date(2026, 10, 2), motivo="Dolor de espalda",
        sintomas="Dolor lumbar al caminar", diagnostico="Contractura muscular",
        tratamiento="Analgésico y reposo", observaciones="")),
    ("281-101200-0003C", dict(fecha=date(2026, 11, 2), motivo="Alergia",
        sintomas="Estornudos y picazón", diagnostico="Rinitis alérgica",
        tratamiento="Antihistamínico", observaciones="Evitar el polvo")),
]

TRATAMIENTOS = [  # (cédula del paciente, datos del tratamiento)
    ("001-150295-0001A", dict(medicamento="Paracetamol", dosis="500 mg",
        frecuencia="Cada 8 horas", duracion="5 días", indicaciones="Tomar con alimentos")),
    ("001-030388-0002B", dict(medicamento="Ibuprofeno", dosis="400 mg",
        frecuencia="Cada 12 horas", duracion="7 días", indicaciones="No tomar en ayunas")),
    ("281-101200-0003C", dict(medicamento="Loratadina", dosis="10 mg",
        frecuencia="Una vez al día", duracion="10 días", indicaciones="")),
]


def cargar():
    crear_tablas()
    # Se obtienen los pacientes existentes para no repetirlos
    existentes = {fila[1]: fila[0] for fila in repositorio.listar_pacientes()}
    for datos in PACIENTES:
        if datos["cedula"] not in existentes:
            existentes[datos["cedula"]] = repositorio.crear_paciente(datos)
            print("Paciente creado:", datos["nombre"], datos["apellido"])

    if not repositorio.listar_consultas():
        for cedula, datos in CONSULTAS:
            repositorio.crear_consulta({"id_paciente": existentes[cedula], **datos})
        print(f"{len(CONSULTAS)} consultas creadas.")

    if not repositorio.listar_tratamientos():
        for cedula, datos in TRATAMIENTOS:
            repositorio.crear_tratamiento({"id_paciente": existentes[cedula], **datos})
        print(f"{len(TRATAMIENTOS)} tratamientos creados.")
    print("Datos de demostración listos.")


if __name__ == "__main__":
    cargar()
