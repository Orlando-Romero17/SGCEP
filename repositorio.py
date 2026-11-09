"""
repositorio.py
Todas las operaciones de base de datos del sistema, escritas con el ORM.
La interfaz NO escribe SQL: llama a estas funciones.

  C (Create) -> crear_*        R (Read)   -> listar_* / obtener_*
  U (Update) -> actualizar_*   D (Delete) -> eliminar_*

Cada función abre su propia sesión (with SessionLocal() as s), así es segura
para usarse desde hilos. Las funciones devuelven tuplas o diccionarios simples
(no objetos del ORM) para evitar problemas al usarlos fuera de la sesión.
Las reglas de negocio se lanzan como ValueError con un mensaje claro.
"""
from datetime import date, timedelta
from sqlalchemy import or_, func
from modelos import SessionLocal, Paciente, Consulta, Tratamiento

CAMPOS_PACIENTE = [
    "cedula", "nombre", "apellido", "fecha_nacimiento", "sexo",
    "telefono", "direccion", "correo", "tipo_sangre", "alergias",
]


def _t(valor):
    """Convierte None en cadena vacía y todo lo demás en texto."""
    return "" if valor is None else str(valor)


def _nombre_sexo(sexo):
    return {"M": "Masculino", "F": "Femenino"}.get(sexo, _t(sexo))


# =====================================================================
# PACIENTES
# =====================================================================
def listar_pacientes(filtro=""):
    """READ: lista pacientes; si hay texto, busca por cédula, nombre o apellido."""
    with SessionLocal() as s:
        q = s.query(Paciente)
        if filtro:
            patron = f"%{filtro}%"
            q = q.filter(or_(Paciente.cedula.like(patron),
                             Paciente.nombre.like(patron),
                             Paciente.apellido.like(patron)))
        q = q.order_by(Paciente.id_paciente)
        return [(p.id_paciente, p.cedula, p.nombre, p.apellido,
                 p.fecha_nacimiento, p.sexo, p.telefono, p.direccion,
                 p.correo, p.tipo_sangre, p.alergias) for p in q.all()]


def obtener_paciente(id_paciente):
    """READ: devuelve un paciente como diccionario (o None si no existe)."""
    with SessionLocal() as s:
        p = s.get(Paciente, id_paciente)
        if p is None:
            return None
        datos = {campo: getattr(p, campo) for campo in CAMPOS_PACIENTE}
        datos["id_paciente"] = p.id_paciente
        return datos


def _cedula_repetida(s, cedula, excluir_id=None):
    q = s.query(func.count(Paciente.id_paciente)).filter(Paciente.cedula == cedula)
    if excluir_id is not None:
        q = q.filter(Paciente.id_paciente != excluir_id)
    return q.scalar() > 0


def crear_paciente(datos):
    """CREATE: inserta un paciente y devuelve su id. No permite cédulas repetidas."""
    with SessionLocal() as s:
        if _cedula_repetida(s, datos["cedula"]):
            raise ValueError("Ya existe un paciente registrado con esa cédula.")
        paciente = Paciente(**datos)
        s.add(paciente)
        s.commit()
        return paciente.id_paciente


def actualizar_paciente(id_paciente, datos):
    """UPDATE: modifica los datos de un paciente existente."""
    with SessionLocal() as s:
        paciente = s.get(Paciente, id_paciente)
        if paciente is None:
            raise ValueError("El paciente ya no existe.")
        if _cedula_repetida(s, datos["cedula"], excluir_id=id_paciente):
            raise ValueError("Ya existe otro paciente con esa cédula.")
        for campo, valor in datos.items():
            setattr(paciente, campo, valor)
        s.commit()


def eliminar_paciente(id_paciente):
    """DELETE: elimina un paciente. Regla de negocio: si tiene consultas o
    tratamientos registrados NO se elimina, para no perder su historial."""
    with SessionLocal() as s:
        paciente = s.get(Paciente, id_paciente)
        if paciente is None:
            raise ValueError("El paciente ya no existe.")
        n_consultas = s.query(func.count(Consulta.id_consulta)).filter(
            Consulta.id_paciente == id_paciente).scalar()
        n_trat = s.query(func.count(Tratamiento.id_tratamiento)).filter(
            Tratamiento.id_paciente == id_paciente).scalar()
        if n_consultas or n_trat:
            raise ValueError(
                "No se puede eliminar el paciente porque tiene "
                f"{n_consultas} consulta(s) y {n_trat} tratamiento(s) registrados. "
                "Elimine primero ese historial."
            )
        s.delete(paciente)
        s.commit()


def pacientes_combo():
    """Lista (id, texto) para llenar las listas desplegables de pacientes."""
    with SessionLocal() as s:
        filas = (s.query(Paciente.id_paciente, Paciente.nombre,
                         Paciente.apellido, Paciente.cedula)
                 .order_by(Paciente.apellido, Paciente.nombre).all())
        return [(i, f"{n} {a} ({c})") for i, n, a, c in filas]


# =====================================================================
# CONSULTAS MÉDICAS
# =====================================================================
def listar_consultas(filtro=""):
    """READ: consultas con el nombre del paciente (JOIN con pacientes)."""
    with SessionLocal() as s:
        q = s.query(Consulta, Paciente).join(
            Paciente, Consulta.id_paciente == Paciente.id_paciente)
        if filtro:
            patron = f"%{filtro}%"
            q = q.filter(or_(Paciente.cedula.like(patron),
                             Paciente.nombre.like(patron),
                             Paciente.apellido.like(patron),
                             Consulta.motivo.like(patron),
                             Consulta.diagnostico.like(patron)))
        q = q.order_by(Consulta.fecha.desc(), Consulta.id_consulta.desc())
        return [(c.id_consulta, c.id_paciente, f"{p.nombre} {p.apellido}",
                 c.fecha, c.motivo, c.sintomas, c.diagnostico,
                 c.tratamiento, c.observaciones) for c, p in q.all()]


def crear_consulta(datos):
    """CREATE: registra una consulta. El paciente debe existir."""
    with SessionLocal() as s:
        if s.get(Paciente, datos["id_paciente"]) is None:
            raise ValueError("El paciente seleccionado no existe.")
        consulta = Consulta(**datos)
        s.add(consulta)
        s.commit()
        return consulta.id_consulta


def actualizar_consulta(id_consulta, datos):
    """UPDATE: modifica una consulta existente."""
    with SessionLocal() as s:
        consulta = s.get(Consulta, id_consulta)
        if consulta is None:
            raise ValueError("La consulta ya no existe.")
        if s.get(Paciente, datos["id_paciente"]) is None:
            raise ValueError("El paciente seleccionado no existe.")
        for campo, valor in datos.items():
            setattr(consulta, campo, valor)
        s.commit()


def eliminar_consulta(id_consulta):
    """DELETE: elimina una consulta."""
    with SessionLocal() as s:
        consulta = s.get(Consulta, id_consulta)
        if consulta is None:
            raise ValueError("La consulta ya no existe.")
        s.delete(consulta)
        s.commit()


# =====================================================================
# TRATAMIENTOS
# =====================================================================
def listar_tratamientos(filtro=""):
    """READ: tratamientos con el nombre del paciente (JOIN con pacientes)."""
    with SessionLocal() as s:
        q = s.query(Tratamiento, Paciente).join(
            Paciente, Tratamiento.id_paciente == Paciente.id_paciente)
        if filtro:
            patron = f"%{filtro}%"
            q = q.filter(or_(Paciente.cedula.like(patron),
                             Paciente.nombre.like(patron),
                             Paciente.apellido.like(patron),
                             Tratamiento.medicamento.like(patron)))
        q = q.order_by(Tratamiento.id_tratamiento.desc())
        return [(t.id_tratamiento, t.id_paciente, f"{p.nombre} {p.apellido}",
                 t.medicamento, t.dosis, t.frecuencia, t.duracion,
                 t.indicaciones) for t, p in q.all()]


def crear_tratamiento(datos):
    """CREATE: registra un tratamiento. El paciente debe existir."""
    with SessionLocal() as s:
        if s.get(Paciente, datos["id_paciente"]) is None:
            raise ValueError("El paciente seleccionado no existe.")
        tratamiento = Tratamiento(**datos)
        s.add(tratamiento)
        s.commit()
        return tratamiento.id_tratamiento


def actualizar_tratamiento(id_tratamiento, datos):
    """UPDATE: modifica un tratamiento existente."""
    with SessionLocal() as s:
        tratamiento = s.get(Tratamiento, id_tratamiento)
        if tratamiento is None:
            raise ValueError("El tratamiento ya no existe.")
        if s.get(Paciente, datos["id_paciente"]) is None:
            raise ValueError("El paciente seleccionado no existe.")
        for campo, valor in datos.items():
            setattr(tratamiento, campo, valor)
        s.commit()


def eliminar_tratamiento(id_tratamiento):
    """DELETE: elimina un tratamiento."""
    with SessionLocal() as s:
        tratamiento = s.get(Tratamiento, id_tratamiento)
        if tratamiento is None:
            raise ValueError("El tratamiento ya no existe.")
        s.delete(tratamiento)
        s.commit()


# =====================================================================
# EXPEDIENTE CLÍNICO (vista consolidada de un paciente)
# =====================================================================
def expediente(id_paciente):
    """Reúne el paciente, su historial de consultas y sus tratamientos.
    El expediente se genera automáticamente: todo paciente tiene el suyo."""
    with SessionLocal() as s:
        paciente = s.get(Paciente, id_paciente)
        if paciente is None:
            return None
        datos = {campo: getattr(paciente, campo) for campo in CAMPOS_PACIENTE}
        datos["id_paciente"] = paciente.id_paciente

        consultas = [
            (c.id_consulta, c.fecha, c.motivo, c.sintomas, c.diagnostico,
             c.tratamiento, c.observaciones)
            for c in s.query(Consulta)
            .filter(Consulta.id_paciente == id_paciente)
            .order_by(Consulta.fecha.desc(), Consulta.id_consulta.desc()).all()
        ]
        tratamientos = [
            (t.id_tratamiento, t.medicamento, t.dosis, t.frecuencia,
             t.duracion, t.indicaciones)
            for t in s.query(Tratamiento)
            .filter(Tratamiento.id_paciente == id_paciente)
            .order_by(Tratamiento.id_tratamiento.desc()).all()
        ]
        return {"paciente": datos, "consultas": consultas, "tratamientos": tratamientos}


# =====================================================================
# ESTADÍSTICAS Y REPORTES
# =====================================================================
def estadisticas():
    """Totales para las tarjetas de la pantalla de inicio."""
    with SessionLocal() as s:
        hace_30 = date.today() - timedelta(days=30)
        return {
            "pacientes": s.query(func.count(Paciente.id_paciente)).scalar(),
            "consultas": s.query(func.count(Consulta.id_consulta)).scalar(),
            "tratamientos": s.query(func.count(Tratamiento.id_tratamiento)).scalar(),
            "consultas_mes": s.query(func.count(Consulta.id_consulta))
                              .filter(Consulta.fecha >= hace_30).scalar(),
        }


TIPOS_REPORTE = [
    "Listado de pacientes",
    "Consultas médicas",
    "Tratamientos",
    "Consultas por paciente",
]


def datos_reporte(tipo):
    """Datos de un reporte: devuelve (encabezados, filas) con todo en texto."""
    with SessionLocal() as s:
        if tipo == "Listado de pacientes":
            encabezados = ["CÉDULA", "PACIENTE", "NACIMIENTO", "SEXO",
                           "TELÉFONO", "SANGRE", "ALERGIAS"]
            filas = [
                (p.cedula, f"{p.nombre} {p.apellido}", _t(p.fecha_nacimiento),
                 _nombre_sexo(p.sexo), _t(p.telefono), _t(p.tipo_sangre),
                 _t(p.alergias))
                for p in s.query(Paciente).order_by(Paciente.apellido).all()
            ]
        elif tipo == "Consultas médicas":
            encabezados = ["FECHA", "PACIENTE", "MOTIVO", "DIAGNÓSTICO", "TRATAMIENTO"]
            q = (s.query(Consulta, Paciente)
                 .join(Paciente, Consulta.id_paciente == Paciente.id_paciente)
                 .order_by(Consulta.fecha.desc(), Consulta.id_consulta.desc()))
            filas = [(_t(c.fecha), f"{p.nombre} {p.apellido}", c.motivo,
                      c.diagnostico, c.tratamiento) for c, p in q.all()]
        elif tipo == "Tratamientos":
            encabezados = ["PACIENTE", "MEDICAMENTO", "DOSIS", "FRECUENCIA", "DURACIÓN"]
            q = (s.query(Tratamiento, Paciente)
                 .join(Paciente, Tratamiento.id_paciente == Paciente.id_paciente)
                 .order_by(Paciente.apellido, Tratamiento.id_tratamiento))
            filas = [(f"{p.nombre} {p.apellido}", t.medicamento, t.dosis,
                      t.frecuencia, t.duracion) for t, p in q.all()]
        elif tipo == "Consultas por paciente":
            # Consulta con agrupación: cuenta las consultas de cada paciente
            encabezados = ["PACIENTE", "CÉDULA", "TOTAL DE CONSULTAS", "ÚLTIMA CONSULTA"]
            q = (s.query(Paciente.nombre, Paciente.apellido, Paciente.cedula,
                         func.count(Consulta.id_consulta), func.max(Consulta.fecha))
                 .outerjoin(Consulta, Consulta.id_paciente == Paciente.id_paciente)
                 .group_by(Paciente.id_paciente, Paciente.nombre,
                           Paciente.apellido, Paciente.cedula)
                 .order_by(Paciente.apellido))
            filas = [(f"{n} {a}", c, _t(total), _t(ultima) or "Sin consultas")
                     for n, a, c, total, ultima in q.all()]
        else:
            raise ValueError("Tipo de reporte no válido.")
        return encabezados, filas
