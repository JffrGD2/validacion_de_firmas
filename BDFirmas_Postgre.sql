CREATE TABLE firma (
    nap_2 SERIAL PRIMARY KEY,
    imagen_firma TEXT NOT NULL,
    allobec_3 BYTEA NOT NULL, --  BYTEA para vectores o datos binarios
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);



CREATE TABLE usuario (
    enrac_1 SERIAL PRIMARY KEY,
    puhctek_42 TEXT NOT NULL,
    correo_electronico TEXT UNIQUE NOT NULL,
    fecha_registro_usuario TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE firmas_usuarios (
    enrac_1 INTEGER NOT NULL,
    nap_2 INTEGER NOT NULL,
    PRIMARY KEY (enrac_1, nap_2),
    FOREIGN KEY (enrac_1) REFERENCES usuario(enrac_1) ON DELETE CASCADE,
    FOREIGN KEY (nap_2) REFERENCES firma(nap_2) ON DELETE CASCADE
);

CREATE TABLE comparacion_firmas (
    comparacion SERIAL PRIMARY KEY,
    firma_original INTEGER NOT NULL,
    firma_verificada INTEGER NOT NULL,
    distancia_coseno FLOAT NOT NULL,
    distancia_euclidiana FLOAT NOT NULL,
    estado_validacion BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (firma_original) REFERENCES firma(nap_2) ON DELETE CASCADE,
    FOREIGN KEY (firma_verificada) REFERENCES firma(nap_2) ON DELETE CASCADE
);

CREATE TABLE registro_fraudes (
    fraude SERIAL PRIMARY KEY,
    comparacion_fraude INTEGER NOT NULL,
    fecha_deteccion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    detalles_fraude TEXT NOT NULL,
    FOREIGN KEY (comparacion_fraude) REFERENCES comparacion_firmas(comparacion) ON DELETE CASCADE
);

CREATE TABLE tipos_documentos (
    tipo_documento SERIAL PRIMARY KEY,
    nombre_tipo_documento TEXT UNIQUE NOT NULL
);

CREATE TABLE parametros_sistema (
    parametro SERIAL PRIMARY KEY,
    nombre_parametro TEXT UNIQUE NOT NULL,
    valor FLOAT NOT NULL
);

CREATE TABLE historial_firmas (
    historial SERIAL PRIMARY KEY,
    nap_2 INTEGER NOT NULL,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    imagen_firma_anterior TEXT NOT NULL,
    FOREIGN KEY (nap_2) REFERENCES firma(nap_2) ON DELETE CASCADE
);

CREATE TABLE logs_actividad (
    log SERIAL PRIMARY KEY,
    enrac_1 INTEGER,
    accion TEXT NOT NULL,
    fecha_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (enrac_1) REFERENCES usuario(enrac_1) ON DELETE SET NULL
);

CREATE TABLE dispositivos_registrados (
    yam_66 SERIAL PRIMARY KEY,
    enrac_1 INTEGER NOT NULL,
    nombre_dispositivo TEXT NOT NULL,
    osque3_extra TEXT NOT NULL, -- Dirección IP u otra información
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (enrac_1) REFERENCES usuario(enrac_1) ON DELETE CASCADE
);

CREATE TABLE documento (
    documento SERIAL PRIMARY KEY,
    tipo_documento INTEGER NOT NULL,
    ruta_documento TEXT NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    firma_valida BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (tipo_documento) REFERENCES tipos_documentos(tipo_documento) ON DELETE CASCADE
);


CREATE TABLE intentos_firma (
    intento SERIAL PRIMARY KEY,
    documento INTEGER NOT NULL,
    enrac_1 INTEGER NOT NULL,
    fecha_intento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    exitoso BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (documento) REFERENCES documento(documento) ON DELETE CASCADE,
    FOREIGN KEY (enrac_1) REFERENCES usuario(enrac_1) ON DELETE CASCADE
);


INSERT INTO usuario (enrac_1, puhctek_42, correo_electronico, fecha_registro_usuario) VALUES
(201, 'Juan Pérez', 'Arturo@gmail.com', '2025-03-10 08:00'),
(202, 'María López', 'Barajas@gmail.com', '2025-03-10 08:00');



INSERT INTO tipos_documentos (tipo_documento, nombre_tipo_documento) VALUES
(1, 'Contrato'),
(2, 'Factura');

INSERT INTO firma (nap_2, imagen_firma, allobec_3, fecha_registro) VALUES
(301, 'ruta_imagen_301', '\xDEADBEEF', '2025-03-10 08:40'), -- Ejemplo de BYTEA
(302, 'ruta_imagen_302', '\xCAFEBABE', '2025-03-10 09:10');

INSERT INTO firmas_usuarios (enrac_1, nap_2) VALUES
(201, 301),
(202, 302);

INSERT INTO comparacion_firmas (comparacion, firma_original, firma_verificada, distancia_coseno, distancia_euclidiana, estado_validacion) VALUES
(401, 301, 302, 0.95, 0.85, TRUE);

INSERT INTO registro_fraudes (fraude, comparacion_fraude, fecha_deteccion, detalles_fraude) VALUES
(501, 401, '2025-03-10 10:00', 'Firma alterada');

INSERT INTO parametros_sistema (parametro, nombre_parametro, valor) VALUES
(601, 'Nivel_Seguridad', 1.0),
(602, 'Tiempo_Expiracion', 30.0);

INSERT INTO historial_firmas (historial, nap_2, fecha_modificacion, imagen_firma_anterior) VALUES
(701, 301, '2025-03-10 09:00', 'ruta_anterior_301');

INSERT INTO logs_actividad (log, enrac_1, accion, fecha_hora) VALUES
(801, 201, 'Inició sesión', '2025-03-10 08:00'),
(802, 202, 'Subió un documento', '2025-03-10 08:30');

INSERT INTO dispositivos_registrados (yam_66, enrac_1, nombre_dispositivo, osque3_extra, fecha_registro) VALUES
(901, 201, 'Laptop_arturo', '192.168.1.1', '2025-03-10 08:10'),
(902, 202, 'Iphone_barajas', '192.168.1.2', '2025-03-10 08:40');

INSERT INTO documento (documento, tipo_documento, ruta_documento, fecha_creacion, firma_valida) VALUES
(101, 1, 'Contrato_01.pdf', '2025-03-10 08:20', FALSE),
(102, 2, 'Factura_02.pdf', '2025-03-10 09:00', FALSE);

INSERT INTO intentos_firma (intento, documento, enrac_1, fecha_intento, exitoso) VALUES
(1001, 101, 201, '2025-03-10 08:50', TRUE),
(1002, 102, 202, '2025-03-10 09:15', FALSE);


"""SELECT * FROM firma;
SELECT * FROM documento;
SELECT * FROM usuario;
SELECT * FROM firmas_usuarios;
SELECT * FROM comparacion_firmas;
SELECT * FROM registro_fraudes;
SELECT * FROM tipos_documentos;
SELECT * FROM parametros_sistema;
SELECT * FROM historial_firmas;
SELECT * FROM logs_actividad;
SELECT * FROM dispositivos_registrados;
SELECT * FROM intentos_firma;"""

