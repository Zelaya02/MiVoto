-- =============================================
-- Mi Voto 2.0 - Base de datos PostgreSQL
-- =============================================

-- Crear base de datos (ejecutar como superusuario si es necesario)
-- CREATE DATABASE mivoto;
-- \c mivoto

-- Extensión para UUID (opcional, por si luego se necesita)
-- CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ====================
-- Tablas principales
-- ====================

CREATE TABLE socios (
    id SERIAL PRIMARY KEY,
    cedula VARCHAR(20) UNIQUE NOT NULL,
    nro_socio VARCHAR(20) UNIQUE NOT NULL,
    nombres VARCHAR(100) NOT NULL,
    apellidos VARCHAR(100) NOT NULL,
    fecha_nacimiento DATE,
    fecha_ingreso DATE,
    sexo VARCHAR(15),
    situacion VARCHAR(50) DEFAULT 'activo',
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE moras (
    id SERIAL PRIMARY KEY,
    socio_id INTEGER NOT NULL REFERENCES socios(id) ON DELETE CASCADE,
    producto VARCHAR(30) NOT NULL,       -- ej: 'CC', 'SOL', 'APE', 'CREDITO', 'CABAL', 'VISA'
    estado VARCHAR(20) NOT NULL,         -- 'al_dia', 'moroso'
    fecha_consulta DATE NOT NULL DEFAULT CURRENT_DATE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_mora_socio_producto_fecha UNIQUE (socio_id, producto, fecha_consulta)
);

CREATE TABLE asambleas (
    id SERIAL PRIMARY KEY,
    tipo VARCHAR(30) NOT NULL,           -- 'ordinaria', 'extraordinaria', 'sectorial'
    fecha DATE NOT NULL,
    hora_inicio TIME,
    lugar VARCHAR(200),
    quorum_minimo INTEGER,
    estado VARCHAR(30) DEFAULT 'programada',  -- 'programada', 'en_curso', 'finalizada', 'cancelada'
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE padron_asamblea (
    id SERIAL PRIMARY KEY,
    socio_id INTEGER NOT NULL REFERENCES socios(id) ON DELETE CASCADE,
    asamblea_id INTEGER NOT NULL REFERENCES asambleas(id) ON DELETE CASCADE,
    situacion VARCHAR(30) NOT NULL DEFAULT 'pendiente',  -- 'habilitado', 'inhabilitado', 'pendiente'
    motivo_inhabilitacion VARCHAR(200),
    fecha_acreditacion TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_padron_socio_asamblea UNIQUE (socio_id, asamblea_id)
);

CREATE TABLE credenciales (
    id SERIAL PRIMARY KEY,
    padron_id INTEGER NOT NULL REFERENCES padron_asamblea(id) ON DELETE CASCADE,
    descripcion VARCHAR(200),
    reimpresion BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE mociones (
    id SERIAL PRIMARY KEY,
    asamblea_id INTEGER NOT NULL REFERENCES asambleas(id) ON DELETE CASCADE,
    titulo VARCHAR(255) NOT NULL,
    tipo_votacion VARCHAR(20) DEFAULT 'si_no',   -- 'si_no', 'multiple'
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE opciones_mocion (
    id SERIAL PRIMARY KEY,
    mocion_id INTEGER NOT NULL REFERENCES mociones(id) ON DELETE CASCADE,
    texto VARCHAR(200) NOT NULL
);

CREATE TABLE votos (
    id SERIAL PRIMARY KEY,
    socio_id INTEGER NOT NULL REFERENCES socios(id) ON DELETE CASCADE,
    mocion_id INTEGER NOT NULL REFERENCES mociones(id) ON DELETE CASCADE,
    opcion_elegida VARCHAR(100),               -- 'si', 'no', 'abstencion', o el texto de la opción
    timestamp_voto TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_voto_socio_mocion UNIQUE (socio_id, mocion_id)
);

-- ====================
-- Usuarios y roles
-- ====================

CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(50) UNIQUE NOT NULL,
    descripcion VARCHAR(200)
);

CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    nombre_completo VARCHAR(150),
    activo BOOLEAN DEFAULT TRUE,
    rol_id INTEGER NOT NULL REFERENCES roles(id),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- ====================
-- Índices adicionales
-- ====================

CREATE INDEX idx_socios_apellidos_nombres ON socios (apellidos, nombres);
CREATE INDEX idx_socios_nro_socio ON socios (nro_socio);
CREATE INDEX idx_moras_socio_id ON moras (socio_id);
CREATE INDEX idx_moras_producto_estado ON moras (producto, estado);
CREATE INDEX idx_padron_asamblea_id ON padron_asamblea (asamblea_id);
CREATE INDEX idx_padron_socio_id ON padron_asamblea (socio_id);
CREATE INDEX idx_padron_situacion ON padron_asamblea (situacion);
CREATE INDEX idx_mociones_asamblea_id ON mociones (asamblea_id);
CREATE INDEX idx_votos_mocion_id ON votos (mocion_id);
CREATE INDEX idx_votos_socio_id ON votos (socio_id);

-- ====================
-- Función para actualizar automáticamente updated_at
-- ====================

CREATE OR REPLACE FUNCTION actualizar_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Aplicar a tablas que tengan updated_at
CREATE TRIGGER trg_socios_updated_at BEFORE UPDATE ON socios
FOR EACH ROW EXECUTE PROCEDURE actualizar_timestamp();

CREATE TRIGGER trg_asambleas_updated_at BEFORE UPDATE ON asambleas
FOR EACH ROW EXECUTE PROCEDURE actualizar_timestamp();

CREATE TRIGGER trg_usuarios_updated_at BEFORE UPDATE ON usuarios
FOR EACH ROW EXECUTE PROCEDURE actualizar_timestamp();

-- ====================
-- Datos semilla (opcional)
-- ====================

-- Roles básicos
INSERT INTO roles (nombre, descripcion) VALUES 
('admin', 'Administrador del sistema'),
('operador', 'Operador de asamblea'),
('consulta', 'Solo lectura');

-- Usuario admin (password: admin123, hash de ejemplo - cambiar en producción)
INSERT INTO usuarios (username, email, password_hash, nombre_completo, activo, rol_id) VALUES
('admin', 'admin@cooperativa.com', 'bcrypt_hash_generado_con_flask', 'Administrador Principal', true, 1);

COMMIT;
