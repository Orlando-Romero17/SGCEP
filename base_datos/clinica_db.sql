-- ============================================================
-- Script de la base de datos del SGCEP (MySQL)
-- Sirve para crear la base manualmente desde MySQL Workbench.
-- Si no lo ejecuta, la aplicación crea las tablas sola al abrir
-- (siempre que la base clinica_db ya exista).
-- ============================================================
CREATE DATABASE IF NOT EXISTS clinica_db
    CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE clinica_db;

CREATE TABLE IF NOT EXISTS pacientes (
    id_paciente      INT AUTO_INCREMENT PRIMARY KEY,
    cedula           VARCHAR(20)  NOT NULL UNIQUE,
    nombre           VARCHAR(60)  NOT NULL,
    apellido         VARCHAR(60)  NOT NULL,
    fecha_nacimiento DATE         NOT NULL,
    sexo             VARCHAR(1)   NOT NULL,
    telefono         VARCHAR(15),
    direccion        VARCHAR(200),
    correo           VARCHAR(100),
    tipo_sangre      VARCHAR(5),
    alergias         TEXT
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS consultas (
    id_consulta   INT AUTO_INCREMENT PRIMARY KEY,
    id_paciente   INT          NOT NULL,
    fecha         DATE         NOT NULL,
    motivo        VARCHAR(200) NOT NULL,
    sintomas      TEXT         NOT NULL,
    diagnostico   TEXT         NOT NULL,
    tratamiento   TEXT         NOT NULL,
    observaciones TEXT,
    CONSTRAINT fk_consulta_paciente FOREIGN KEY (id_paciente)
        REFERENCES pacientes (id_paciente) ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS tratamientos (
    id_tratamiento INT AUTO_INCREMENT PRIMARY KEY,
    id_paciente    INT          NOT NULL,
    medicamento    VARCHAR(120) NOT NULL,
    dosis          VARCHAR(60)  NOT NULL,
    frecuencia     VARCHAR(60)  NOT NULL,
    duracion       VARCHAR(60)  NOT NULL,
    indicaciones   TEXT,
    CONSTRAINT fk_tratamiento_paciente FOREIGN KEY (id_paciente)
        REFERENCES pacientes (id_paciente) ON DELETE RESTRICT
) ENGINE=InnoDB;
