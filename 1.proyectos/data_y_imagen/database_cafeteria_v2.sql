-- =====================================================
-- BASE DE DATOS CAFETERIA - POSTGRESQL
-- Versión 2 - Modificaciones:
--   * cliente simplificado (solo campos necesarios)
--   * ENUM metodo_pago en nota_venta
--   * ENUM estado_pedido en pedido
-- =====================================================

-- =====================================================
-- ENUMS
-- =====================================================

CREATE TYPE metodo_pago_enum AS ENUM ('efectivo', 'qr', 'tarjeta');

CREATE TYPE estado_pedido_enum AS ENUM ('pendiente', 'en_preparacion', 'listo', 'entregado', 'cancelado');

-- =====================================================
-- CATÁLOGOS
-- =====================================================

CREATE TABLE turno (
    id_turno     SERIAL,
    descripcion  VARCHAR(100) NOT NULL,

    CONSTRAINT pk_turno PRIMARY KEY (id_turno)
);

CREATE TABLE estado_civil (
    id_estado_civil SERIAL,
    descripcion     VARCHAR(100) NOT NULL,

    CONSTRAINT pk_estado_civil PRIMARY KEY (id_estado_civil)
);

CREATE TABLE nacionalidad (
    id_nacionalidad SERIAL,
    descripcion     VARCHAR(100) NOT NULL,

    CONSTRAINT pk_nacionalidad PRIMARY KEY (id_nacionalidad)
);

CREATE TABLE estado (
    id_estado    SERIAL,
    descripcion  VARCHAR(100) NOT NULL,

    CONSTRAINT pk_estado PRIMARY KEY (id_estado)
);

CREATE TABLE tipo_contacto (
    id_tipo_contacto SERIAL,
    descripcion      VARCHAR(100) NOT NULL,

    CONSTRAINT pk_tipo_contacto PRIMARY KEY (id_tipo_contacto)
);

CREATE TABLE salario (
    id_salario   SERIAL,
    descripcion  VARCHAR(150) NOT NULL,
    monto        DECIMAL(12,2) NOT NULL CHECK (monto >= 0),

    CONSTRAINT pk_salario PRIMARY KEY (id_salario)
);

-- =====================================================
-- MENÚ
-- =====================================================

CREATE TABLE categoria_producto (
    id_categoria  SERIAL,
    nombre        VARCHAR(100) NOT NULL,
    descripcion   TEXT,

    CONSTRAINT pk_categoria_producto PRIMARY KEY (id_categoria)
);

CREATE TABLE producto (
    id_producto   SERIAL,
    id_categoria  INT NOT NULL,
    nombre        VARCHAR(200) NOT NULL,
    descripcion   TEXT,
    precio        DECIMAL(12,2) NOT NULL CHECK (precio >= 0),
    disponible    BOOLEAN NOT NULL DEFAULT TRUE,

    CONSTRAINT pk_producto PRIMARY KEY (id_producto),

    CONSTRAINT fk_pro_categoria FOREIGN KEY (id_categoria)
        REFERENCES categoria_producto (id_categoria)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);

-- =====================================================
-- PERSONAS
-- =====================================================

CREATE TABLE empleado (
    id_empleado        SERIAL,
    nombre_empleado    VARCHAR(200) NOT NULL,
    ci                 VARCHAR(20) UNIQUE,
    tel_fijo           VARCHAR(20),
    cel                VARCHAR(20),
    tel_contacto       VARCHAR(20),
    nombre_contacto    VARCHAR(200),
    email              VARCHAR(200),
    direccion          TEXT,
    fecha_ingreso      DATE NOT NULL,

    id_turno           INT NOT NULL,
    id_estado_civil    INT NOT NULL,
    id_nacionalidad    INT NOT NULL,
    id_estado          INT NOT NULL,
    id_tipo_contacto   INT NOT NULL,
    id_salario         INT NOT NULL,

    CONSTRAINT pk_empleado PRIMARY KEY (id_empleado),

    CONSTRAINT fk_emp_turno FOREIGN KEY (id_turno)
        REFERENCES turno (id_turno)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    CONSTRAINT fk_emp_estado_civil FOREIGN KEY (id_estado_civil)
        REFERENCES estado_civil (id_estado_civil)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    CONSTRAINT fk_emp_nacionalidad FOREIGN KEY (id_nacionalidad)
        REFERENCES nacionalidad (id_nacionalidad)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    CONSTRAINT fk_emp_estado FOREIGN KEY (id_estado)
        REFERENCES estado (id_estado)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    CONSTRAINT fk_emp_tipo_contacto FOREIGN KEY (id_tipo_contacto)
        REFERENCES tipo_contacto (id_tipo_contacto)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    CONSTRAINT fk_emp_salario FOREIGN KEY (id_salario)
        REFERENCES salario (id_salario)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);

CREATE TABLE login (
    id_login         SERIAL,
    id_empleado      INT NOT NULL UNIQUE,
    nombre           VARCHAR(100) NOT NULL,
    email            VARCHAR(200) NOT NULL,
    password_hash    VARCHAR(255) NOT NULL,
    estado           VARCHAR(20) NOT NULL,
    fecha_creacion   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_login      TIMESTAMP,

    CONSTRAINT pk_login PRIMARY KEY (id_login),

    CONSTRAINT fk_log_empleado FOREIGN KEY (id_empleado)
        REFERENCES empleado (id_empleado)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- Cliente simplificado para sistema presencial
-- Solo datos necesarios para facturación
CREATE TABLE cliente (
    id_cliente      SERIAL,
    ci_o_nit        VARCHAR(20),
    nombre          VARCHAR(200) NOT NULL,
    fecha_registro  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_cliente PRIMARY KEY (id_cliente)
);

-- =====================================================
-- OPERACIONES
-- =====================================================

CREATE TABLE pedido (
    id_pedido     SERIAL,
    id_cliente    INT NOT NULL,
    id_empleado   INT NOT NULL,
    fecha         TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    estado        estado_pedido_enum NOT NULL DEFAULT 'pendiente',
    total         DECIMAL(12,2) NOT NULL CHECK (total >= 0),

    CONSTRAINT pk_pedido PRIMARY KEY (id_pedido),

    CONSTRAINT fk_ped_cliente FOREIGN KEY (id_cliente)
        REFERENCES cliente (id_cliente)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT fk_ped_empleado FOREIGN KEY (id_empleado)
        REFERENCES empleado (id_empleado)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);

CREATE TABLE pedido_detalle (
    id_detalle       SERIAL,
    id_pedido        INT NOT NULL,
    id_producto      INT NOT NULL,
    cantidad         INT NOT NULL CHECK (cantidad > 0),
    precio_unitario  DECIMAL(12,2) NOT NULL CHECK (precio_unitario >= 0),
    subtotal         DECIMAL(12,2) NOT NULL CHECK (subtotal >= 0),

    CONSTRAINT pk_pedido_detalle PRIMARY KEY (id_detalle),

    CONSTRAINT fk_det_pedido FOREIGN KEY (id_pedido)
        REFERENCES pedido (id_pedido)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT fk_det_producto FOREIGN KEY (id_producto)
        REFERENCES producto (id_producto)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);

CREATE TABLE nota_venta (
    id_nota        SERIAL,
    id_pedido      INT NOT NULL UNIQUE,
    id_cliente     INT NOT NULL,
    id_empleado    INT NOT NULL,
    fecha          DATE NOT NULL DEFAULT CURRENT_DATE,
    nit            VARCHAR(20),
    razon_social   VARCHAR(300),
    total          DECIMAL(12,2) NOT NULL CHECK (total >= 0),
    metodo_pago    metodo_pago_enum NOT NULL,

    CONSTRAINT pk_nota_venta PRIMARY KEY (id_nota),

    CONSTRAINT fk_not_pedido FOREIGN KEY (id_pedido)
        REFERENCES pedido (id_pedido)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT fk_not_cliente FOREIGN KEY (id_cliente)
        REFERENCES cliente (id_cliente)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    CONSTRAINT fk_not_empleado FOREIGN KEY (id_empleado)
        REFERENCES empleado (id_empleado)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);

-- =====================================================
-- AUDITORÍA
-- =====================================================

CREATE TABLE bitacora (
    id_bitacora    SERIAL,
    id_login       INT NOT NULL,
    id_empleado    INT NOT NULL,
    fecha          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    accion         TEXT NOT NULL,
    detalle        TEXT,

    CONSTRAINT pk_bitacora PRIMARY KEY (id_bitacora),

    CONSTRAINT fk_bit_login FOREIGN KEY (id_login)
        REFERENCES login (id_login)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT fk_bit_empleado FOREIGN KEY (id_empleado)
        REFERENCES empleado (id_empleado)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);
