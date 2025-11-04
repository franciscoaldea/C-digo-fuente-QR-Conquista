DROP DATABASE IF EXISTS QRConquista;
CREATE DATABASE IF NOT EXISTS QRConquista;
USE QRConquista;


CREATE TABLE IF NOT EXISTS tipos_de_usuario (
    tipo_usuario VARCHAR(20) NOT NULL PRIMARY KEY
) ENGINE=INNODB;

INSERT INTO tipos_de_usuario (tipo_usuario)
VALUES ("admin"), ("docente"), ("alumno");


CREATE TABLE IF NOT EXISTS Usuario (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    nombre_usuario VARCHAR(20) NOT NULL,
    gmail VARCHAR(50),
    contraseña VARCHAR(255) NOT NULL,
    tipo_usuario VARCHAR(20),
    FOREIGN KEY (tipo_usuario) REFERENCES tipos_de_usuario (tipo_usuario)
) ENGINE=INNODB;

-- Usuario de prueba (fran / 123)
INSERT INTO Usuario (nombre_usuario, gmail, contraseña, tipo_usuario)
VALUES ("fran", "fran@gmail.com", "123", "admin");



CREATE TABLE IF NOT EXISTS Cursos (
    id_curso INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    Turno VARCHAR(20) NOT NULL,
    especialidad VARCHAR(25),
    año INT NOT NULL,
    division INT NOT NULL,
    horarios VARCHAR(50)
) ENGINE=INNODB;

-- Curso de prueba (id_curso = 1)
INSERT INTO Cursos (Turno, especialidad, año, division, horarios)
VALUES ("Mañana", "Computación", 5, 7, "8:00 - 12:00");


CREATE TABLE IF NOT EXISTS Aulas (
    id_aula INT PRIMARY KEY,
    ubicacion VARCHAR(70) NOT NULL

) ENGINE=INNODB;

-- DATOS AÑADIDOS: Aulas generales con ubicación (lo que se mostrará en el listado)
INSERT INTO Aulas (id_aula, ubicacion)
VALUES
(101, 'Aula 1'), -- Referenciado por Aulas_Computacion
(102, 'Aula 2'),
(103, 'Aula 3');


CREATE TABLE IF NOT EXISTS Aulas_Computacion (
    id_aula_comp INT AUTO_INCREMENT PRIMARY KEY,
    nombre_aula VARCHAR(20) NOT NULL,
    estado ENUM("ocupado", "desocupado", "cerrada") DEFAULT "desocupado",
    id_aula INT,
    id_curso INT,
    FOREIGN KEY (id_aula) REFERENCES Aulas (id_aula),
    FOREIGN KEY (id_curso) REFERENCES Cursos (id_curso)
) ENGINE=INNODB;

-- Datos de Aulas de Computación
INSERT INTO Aulas_Computacion (nombre_aula, estado, id_aula, id_curso)
VALUES
("PC 1 - Lab", "desocupado", 101, 1),
("PC 2 - Lab", "desocupado", 101, 1),
("PC 3 - Lab", "desocupado", 101, 1),
("PC 4 - Lab", "desocupado", 101, 1);


ALTER TABLE aulas CHANGE ubicacion nombre VARCHAR(255);
select * from aulas;
ALTER TABLE aulas ADD COLUMN estado VARCHAR(50) DEFAULT 'Libre';
