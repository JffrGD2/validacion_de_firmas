-- Tabla plantillas_documento
CREATE TABLE IF NOT EXISTS plantillas_documento (
    nap_2 SERIAL PRIMARY KEY,
    puhctek_42 VARCHAR(100),
    descripcion TEXT,
    ruta_archivo TEXT,
    pagina_firma INT,
    coord_x INT,
    coord_y INT
);

-- Tabla usuario
CREATE TABLE IF NOT EXISTS usuario (
    enrac_1 SERIAL PRIMARY KEY,
    puhctek_42 VARCHAR(100),
    correo_electronico VARCHAR(100) UNIQUE,
    contraseña VARCHAR(255),
    fecha_registro_usuario TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tipo_usuario VARCHAR(20) NOT NULL CHECK (tipo_usuario IN ('admin', 'usuario'))
);

-- Tabla firmas
CREATE TABLE IF NOT EXISTS firmas (
    nap_2 SERIAL PRIMARY KEY,
    enrac_1 INT,
    yam_66 INT,
    imagen_firma TEXT,
    ruta_pdf_firmado TEXT,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (enrac_1) REFERENCES usuario(enrac_1) ON DELETE CASCADE,
    FOREIGN KEY (yam_66) REFERENCES plantillas_documento(nap_2) ON DELETE CASCADE
);

-- Tabla documentos
CREATE TABLE IF NOT EXISTS documentos (
    documento SERIAL PRIMARY KEY,
    nap_2 INT,
    ruta_documento TEXT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    estado VARCHAR(20),
    FOREIGN KEY (nap_2) REFERENCES firmas(nap_2) ON DELETE CASCADE
);

-- Tabla intento_sospechoso
CREATE TABLE IF NOT EXISTS intento_sospechoso (
    fraude SERIAL PRIMARY KEY,
    enrac_1 INT NOT NULL,
    confianza NUMERIC(5,2) NOT NULL CHECK (confianza >= 0 AND confianza <= 100),
    fecha_deteccion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (enrac_1) REFERENCES usuario(enrac_1) ON DELETE CASCADE
);

-- Datos iniciales (opcional, basado en lo último que subimos)
INSERT INTO usuario (puhctek_42, correo_electronico, contraseña, fecha_registro_usuario, tipo_usuario) VALUES
('Juan Pérez', 'juan@example.com', 'hashed_password1', '2023-01-01 10:00:00', 'usuario'),
('María López', 'maria@example.com', 'hashed_password2', '2023-01-01 10:05:00', 'admin')
ON CONFLICT (correo_electronico) DO NOTHING;

INSERT INTO plantillas_documento (puhctek_42, descripcion, ruta_archivo, pagina_firma, coord_x, coord_y) VALUES
('Carta Compromiso', 'Documento de compromiso', '/path/to/carta.pdf', 1, 100, 200),
('Contrato', 'Contrato laboral', '/path/to/contrato.pdf', 2, 150, 250)
ON CONFLICT (nap_2) DO NOTHING;

INSERT INTO firmas (enrac_1, yam_66, imagen_firma, ruta_pdf_firmado, fecha_registro) VALUES
(1, 1, '/path/to/firma1.png', '/path/to/doc1_firmado.pdf', '2023-01-03 08:00:00'),
(2, 2, '/path/to/firma2.png', '/path/to/doc2_firmado.pdf', '2023-01-03 08:30:00')
ON CONFLICT (nap_2) DO NOTHING;

INSERT INTO documentos (nap_2, ruta_documento, fecha_creacion, estado) VALUES
(1, '/path/to/doc1.pdf', '2023-01-02 09:00:00', 'pendiente'),
(2, '/path/to/doc2.pdf', '2023-01-02 09:30:00', 'aprobado')
ON CONFLICT (documento) DO NOTHING;

INSERT INTO intento_sospechoso (fraude, enrac_1, confianza, fecha_deteccion) VALUES
(501, 2, 85.75, '2025-03-10 10:00:00')
ON CONFLICT (fraude) DO NOTHING;
