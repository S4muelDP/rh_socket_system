-- Crear la base de datos
CREATE DATABASE IF NOT EXISTS rh_socket_system;
USE rh_socket_system;

-- Tabla de Departamentos
CREATE TABLE departamentos (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(100) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    jefe_id INT
);

-- Tabla de Cargos
CREATE TABLE cargo (
    id INT PRIMARY KEY AUTO_INCREMENT,
    titulo VARCHAR(100) NOT NULL,
    descripcion VARCHAR(255),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    departamento_id INT,
    FOREIGN KEY (departamento_id) REFERENCES departamentos(id)
);

-- Tabla de Empleados
CREATE TABLE empleados (
    id INT PRIMARY KEY AUTO_INCREMENT,
    primer_nombre VARCHAR(50) NOT NULL,
    segundo_nombre VARCHAR(50),
    primer_apellido VARCHAR(50) NOT NULL,
    segundo_apellido VARCHAR(50),
    email VARCHAR(100) UNIQUE NOT NULL,
    celular VARCHAR(20) UNIQUE NOT NULL,
    fecha_contratacion DATE NOT NULL,
    estado BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    departamento_id INT,
    cargo_id INT,
    FOREIGN KEY (departamento_id) REFERENCES departamentos(id),
    FOREIGN KEY (cargo_id) REFERENCES cargo(id)
);

-- Actualizar la referencia del jefe en departamentos
ALTER TABLE departamentos
ADD FOREIGN KEY (jefe_id) REFERENCES empleados(id);

-- Tabla de Asistencias
CREATE TABLE asistencias (
    id INT PRIMARY KEY AUTO_INCREMENT,
    fecha DATE NOT NULL,
    hora_entrada TIME NOT NULL,
    hora_salida TIME,
    estado ENUM('presente', 'ausente', 'permiso') NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    empleado_id INT,
    FOREIGN KEY (empleado_id) REFERENCES empleados(id)
);

-- Tabla de Tipos de Permisos
CREATE TABLE tipos_permisos (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(100) NOT NULL,
    descripcion VARCHAR(255),
    estado BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Tabla de Permisos
CREATE TABLE permisos (
    id INT PRIMARY KEY AUTO_INCREMENT,
    fecha_inicio DATETIME NOT NULL,
    fecha_fin DATETIME NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    tipo_permiso_id INT,
    empleado_id INT,
    FOREIGN KEY (tipo_permiso_id) REFERENCES tipos_permisos(id),
    FOREIGN KEY (empleado_id) REFERENCES empleados(id)
);

-- Tabla de Salarios
CREATE TABLE salarios (
    id INT PRIMARY KEY AUTO_INCREMENT,
    salario_base INT NOT NULL,
    bonificaciones INT DEFAULT 0,
    deducciones INT DEFAULT 0,
    salario_total INT NOT NULL,
    estado BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    empleado_id INT,
    FOREIGN KEY (empleado_id) REFERENCES empleados(id)
);

-- Tabla de Históricos
CREATE TABLE historicos (
    id INT PRIMARY KEY AUTO_INCREMENT,
    empleado_id INT,
    fecha_retiro DATE NOT NULL,
    motivo VARCHAR(255),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (empleado_id) REFERENCES empleados(id)
);