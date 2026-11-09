"""
Pruebas automáticas de las validaciones (no necesitan base de datos ni interfaz).
Ejecutar desde la carpeta del proyecto:  python -m unittest discover -s pruebas -v
"""
import os
import sys
import unittest
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from validaciones import validar_paciente, validar_consulta, validar_tratamiento

HOY = date(2026, 11, 9)


def paciente_valido():
    return dict(cedula="001-150295-0001A", nombre="María", apellido="López",
                fecha_nacimiento=date(1995, 2, 15), sexo="F", telefono="8888-1111",
                correo="maria@correo.com", tipo_sangre="O+")


class PruebasPaciente(unittest.TestCase):
    def test_paciente_valido(self):
        self.assertEqual(validar_paciente(paciente_valido(), HOY), [])

    def test_cedula_vacia(self):
        d = paciente_valido(); d["cedula"] = ""
        self.assertIn("La cédula es obligatoria.", validar_paciente(d, HOY))

    def test_cedula_formato_incorrecto(self):
        d = paciente_valido(); d["cedula"] = "12345"
        self.assertTrue(any("formato" in e for e in validar_paciente(d, HOY)))

    def test_nombre_con_numeros(self):
        d = paciente_valido(); d["nombre"] = "Mar1a"
        self.assertTrue(any("solo puede contener letras" in e for e in validar_paciente(d, HOY)))

    def test_fecha_futura(self):
        d = paciente_valido(); d["fecha_nacimiento"] = date(2027, 1, 1)
        self.assertTrue(any("futura" in e for e in validar_paciente(d, HOY)))

    def test_sexo_obligatorio(self):
        d = paciente_valido(); d["sexo"] = ""
        self.assertTrue(any("sexo" in e for e in validar_paciente(d, HOY)))

    def test_correo_invalido(self):
        d = paciente_valido(); d["correo"] = "maria@"
        self.assertTrue(any("correo" in e for e in validar_paciente(d, HOY)))

    def test_correo_vacio_es_valido(self):
        d = paciente_valido(); d["correo"] = ""
        self.assertEqual(validar_paciente(d, HOY), [])

    def test_telefono_invalido(self):
        d = paciente_valido(); d["telefono"] = "123"
        self.assertTrue(any("teléfono" in e for e in validar_paciente(d, HOY)))

    def test_telefono_sin_guion(self):
        d = paciente_valido(); d["telefono"] = "88881111"
        self.assertEqual(validar_paciente(d, HOY), [])


class PruebasConsulta(unittest.TestCase):
    def datos(self):
        return dict(id_paciente=1, fecha=date(2026, 11, 1), motivo="Dolor",
                    sintomas="Fiebre", diagnostico="Gripe", tratamiento="Reposo")

    def test_consulta_valida(self):
        self.assertEqual(validar_consulta(self.datos(), HOY), [])

    def test_sin_paciente(self):
        d = self.datos(); d["id_paciente"] = None
        self.assertTrue(any("paciente" in e for e in validar_consulta(d, HOY)))

    def test_fecha_futura(self):
        d = self.datos(); d["fecha"] = date(2027, 1, 1)
        self.assertTrue(any("futura" in e for e in validar_consulta(d, HOY)))

    def test_campos_obligatorios(self):
        d = self.datos(); d["motivo"] = " "; d["diagnostico"] = ""
        self.assertEqual(len(validar_consulta(d, HOY)), 2)


class PruebasTratamiento(unittest.TestCase):
    def test_tratamiento_valido(self):
        d = dict(id_paciente=1, medicamento="Paracetamol", dosis="500 mg",
                 frecuencia="Cada 8 horas", duracion="5 días")
        self.assertEqual(validar_tratamiento(d), [])

    def test_tratamiento_incompleto(self):
        d = dict(id_paciente=None, medicamento="", dosis="", frecuencia="", duracion="")
        self.assertEqual(len(validar_tratamiento(d)), 5)


if __name__ == "__main__":
    unittest.main()
