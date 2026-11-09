"""
modelos.py
Capa ORM del sistema con SQLAlchemy (mapeo objeto-relacional).

Contiene:
  - La conexion (engine) a MySQL o SQLite, segun el archivo .env.
  - La fabrica de sesiones (SessionLocal).
  - Las clases Paciente, Consulta y Tratamiento: cada clase representa una
    tabla y cada objeto representa una fila.

Relaciones:
  Paciente 1 --- N Consulta
  Paciente 1 --- N Tratamiento
"""
import os
from dotenv import load_dotenv
from sqlalchemy import (
    create_engine, event, Column, Integer, String, Date, Text, ForeignKey
)
from sqlalchemy.engine import URL
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

# Lee las credenciales desde el archivo .env (no quedan escritas en el codigo)
load_dotenv()

RAIZ = os.path.dirname(os.path.abspath(__file__))


def _crear_engine():
    """Crea el engine segun DB_TIPO: 'mysql' (por defecto en .env) o 'sqlite'."""
    tipo = os.getenv("DB_TIPO", "sqlite").lower()

    if tipo == "mysql":
        # URL.create maneja bien contrasenas con caracteres especiales
        url = URL.create(
            "mysql+mysqlconnector",
            username=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "3306")),
            database=os.getenv("DB_NAME", "clinica_db"),
        )
        # pool_pre_ping verifica que la conexion siga viva antes de usarla
        return create_engine(url, pool_pre_ping=True, pool_recycle=1800)

    # SQLite: un archivo local, util para pruebas sin instalar MySQL
    archivo = os.getenv("DB_ARCHIVO", os.path.join(RAIZ, "clinica.db"))
    engine = create_engine(
        f"sqlite:///{archivo}", connect_args={"check_same_thread": False}
    )

    @event.listens_for(engine, "connect")
    def _activar_llaves_foraneas(conexion_dbapi, _registro):
        # SQLite no aplica las llaves foraneas si no se activan explicitamente
        conexion_dbapi.execute("PRAGMA foreign_keys=ON")

    return engine


# Engine: administra un pool de conexiones y es seguro entre hilos
engine = _crear_engine()

# Cada operacion abre su propia sesion: with SessionLocal() as s: ...
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

# Clase base de la que heredan todos los modelos
Base = declarative_base()


class Paciente(Base):
    """Tabla pacientes: datos personales y clinicos basicos."""
    __tablename__ = "pacientes"

    id_paciente = Column(Integer, primary_key=True, autoincrement=True)
    cedula = Column(String(20), nullable=False, unique=True)
    nombre = Column(String(60), nullable=False)
    apellido = Column(String(60), nullable=False)
    fecha_nacimiento = Column(Date, nullable=False)
    sexo = Column(String(1), nullable=False)          # 'M' o 'F'
    telefono = Column(String(15))
    direccion = Column(String(200))
    correo = Column(String(100))
    tipo_sangre = Column(String(5))
    alergias = Column(Text)

    # Un paciente tiene muchas consultas y muchos tratamientos (1 a N)
    consultas = relationship("Consulta", back_populates="paciente")
    tratamientos = relationship("Tratamiento", back_populates="paciente")


class Consulta(Base):
    """Tabla consultas: cada visita medica de un paciente."""
    __tablename__ = "consultas"

    id_consulta = Column(Integer, primary_key=True, autoincrement=True)
    # Llave foranea: toda consulta pertenece a un paciente existente
    id_paciente = Column(
        Integer, ForeignKey("pacientes.id_paciente", ondelete="RESTRICT"),
        nullable=False
    )
    fecha = Column(Date, nullable=False)
    motivo = Column(String(200), nullable=False)
    sintomas = Column(Text, nullable=False)
    diagnostico = Column(Text, nullable=False)
    tratamiento = Column(Text, nullable=False)
    observaciones = Column(Text)

    paciente = relationship("Paciente", back_populates="consultas")


class Tratamiento(Base):
    """Tabla tratamientos: medicamentos e indicaciones de un paciente."""
    __tablename__ = "tratamientos"

    id_tratamiento = Column(Integer, primary_key=True, autoincrement=True)
    id_paciente = Column(
        Integer, ForeignKey("pacientes.id_paciente", ondelete="RESTRICT"),
        nullable=False
    )
    medicamento = Column(String(120), nullable=False)
    dosis = Column(String(60), nullable=False)
    frecuencia = Column(String(60), nullable=False)
    duracion = Column(String(60), nullable=False)
    indicaciones = Column(Text)

    paciente = relationship("Paciente", back_populates="tratamientos")


def crear_tablas():
    """Crea las tablas que no existan (no modifica ni borra las existentes)."""
    Base.metadata.create_all(engine)
