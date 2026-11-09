"""
Pruebas del CRUD con el ORM sobre una base SQLite temporal (no toca MySQL).
Ejecutar desde la carpeta del proyecto:  python -m unittest discover -s pruebas -v
Requiere: pip install SQLAlchemy python-dotenv
"""
import os
import sys
import tempfile
import unittest
from datetime import date

# La base de pruebas se define ANTES de importar los modelos
_ARCHIVO = os.path.join(tempfile.mkdtemp(), "prueba.db")
os.environ["DB_TIPO"] = "sqlite"
os.environ["DB_ARCHIVO"] = _ARCHIVO
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import modelos
import repositorio


def datos_paciente(cedula="001-150295-0001A"):
    return dict(cedula=cedula, nombre="María", apellido="López",
                fecha_nacimiento=date(1995, 2, 15), sexo="F", telefono="8888-1111",
                direccion="Managua", correo="m@x.com", tipo_sangre="O+", alergias="")


class PruebasCrud(unittest.TestCase):
    def setUp(self):
        modelos.Base.metadata.drop_all(modelos.engine)
        modelos.crear_tablas()

    def test_crear_y_leer_paciente(self):
        id_p = repositorio.crear_paciente(datos_paciente())
        self.assertEqual(repositorio.obtener_paciente(id_p)["nombre"], "María")
        self.assertEqual(len(repositorio.listar_pacientes()), 1)

    def test_cedula_duplicada(self):
        repositorio.crear_paciente(datos_paciente())
        with self.assertRaises(ValueError):
            repositorio.crear_paciente(datos_paciente())

    def test_actualizar_paciente(self):
        id_p = repositorio.crear_paciente(datos_paciente())
        d = datos_paciente(); d["nombre"] = "Marta"
        repositorio.actualizar_paciente(id_p, d)
        self.assertEqual(repositorio.obtener_paciente(id_p)["nombre"], "Marta")

    def test_buscar_paciente(self):
        repositorio.crear_paciente(datos_paciente())
        self.assertEqual(len(repositorio.listar_pacientes("lópez")), 1)
        self.assertEqual(len(repositorio.listar_pacientes("zzz")), 0)

    def test_eliminar_paciente(self):
        id_p = repositorio.crear_paciente(datos_paciente())
        repositorio.eliminar_paciente(id_p)
        self.assertEqual(repositorio.listar_pacientes(), [])

    def test_no_elimina_paciente_con_consultas(self):
        id_p = repositorio.crear_paciente(datos_paciente())
        repositorio.crear_consulta(dict(id_paciente=id_p, fecha=date(2026, 9, 1),
            motivo="Dolor", sintomas="Fiebre", diagnostico="Gripe",
            tratamiento="Reposo", observaciones=""))
        with self.assertRaises(ValueError):
            repositorio.eliminar_paciente(id_p)

    def test_crud_consulta(self):
        id_p = repositorio.crear_paciente(datos_paciente())
        id_c = repositorio.crear_consulta(dict(id_paciente=id_p, fecha=date(2026, 9, 1),
            motivo="Dolor", sintomas="Fiebre", diagnostico="Gripe",
            tratamiento="Reposo", observaciones=""))
        self.assertEqual(len(repositorio.listar_consultas()), 1)
        repositorio.eliminar_consulta(id_c)
        self.assertEqual(repositorio.listar_consultas(), [])

    def test_consulta_con_paciente_inexistente(self):
        with self.assertRaises(ValueError):
            repositorio.crear_consulta(dict(id_paciente=999, fecha=date(2026, 9, 1),
                motivo="x", sintomas="x", diagnostico="x", tratamiento="x", observaciones=""))

    def test_crud_tratamiento_y_expediente(self):
        id_p = repositorio.crear_paciente(datos_paciente())
        repositorio.crear_tratamiento(dict(id_paciente=id_p, medicamento="Paracetamol",
            dosis="500 mg", frecuencia="Cada 8 horas", duracion="5 días", indicaciones=""))
        exp = repositorio.expediente(id_p)
        self.assertEqual(len(exp["tratamientos"]), 1)
        self.assertEqual(exp["consultas"], [])

    def test_reportes(self):
        repositorio.crear_paciente(datos_paciente())
        for tipo in repositorio.TIPOS_REPORTE:
            encabezados, filas = repositorio.datos_reporte(tipo)
            self.assertTrue(len(encabezados) > 0)
        # Con un paciente y sin consultas, estos dos reportes tienen 1 fila
        self.assertEqual(len(repositorio.datos_reporte("Listado de pacientes")[1]), 1)
        self.assertEqual(len(repositorio.datos_reporte("Consultas por paciente")[1]), 1)
        # y estos dos no tienen filas
        self.assertEqual(repositorio.datos_reporte("Consultas médicas")[1], [])
        self.assertEqual(repositorio.datos_reporte("Tratamientos")[1], [])

    def test_estadisticas(self):
        repositorio.crear_paciente(datos_paciente())
        self.assertEqual(repositorio.estadisticas()["pacientes"], 1)


if __name__ == "__main__":
    unittest.main()
