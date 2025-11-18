
DROP DATABASE IF EXISTS QRConquista;
CREATE DATABASE IF NOT EXISTS QRConquista;
USE QRConquista;

-- TIPOS DE USUARIO
CREATE TABLE IF NOT EXISTS tipos_de_usuario (
    tipo_usuario VARCHAR(20) NOT NULL PRIMARY KEY
) ENGINE=INNODB;

INSERT INTO tipos_de_usuario (tipo_usuario)
VALUES ("admin"), ("docente"), ("alumno");

-- USUARIOS
CREATE TABLE IF NOT EXISTS Usuario (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    nombre_usuario VARCHAR(20) NOT NULL,
    gmail VARCHAR(50),
    contraseña VARCHAR(255) NOT NULL,
    tipo_usuario VARCHAR(20),
    FOREIGN KEY (tipo_usuario) REFERENCES tipos_de_usuario (tipo_usuario)
) ENGINE=INNODB;

-- Usuario de prueba
INSERT INTO Usuario (nombre_usuario, gmail, contraseña, tipo_usuario)
VALUES ("fran", "fran@gmail.com", "123", "admin");

-- AULAS
CREATE TABLE IF NOT EXISTS Aulas (
    id_aula INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    curso VARCHAR(10) DEFAULT '5°7',
    estado VARCHAR(50) DEFAULT 'Libre',
    especialidad VARCHAR(50) DEFAULT 'Computación'
) ENGINE=INNODB;

-- Aulas de ejemplo
INSERT INTO Aulas (nombre, curso, estado, especialidad, id_aula)
VALUES
('Aula 1', "4to1", "Ocupada", "Computación", 101),
('Aula 2', "6to1", "Libre", "Computación", 102),
('Aula 3', "3ro5", "Ocupada", "Computación", 103);

-- CURSOS
CREATE TABLE IF NOT EXISTS Cursos (
    id_curso INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    Turno VARCHAR(20) NOT NULL,
    especialidad VARCHAR(25),
    año INT NOT NULL,
    division INT NOT NULL,
    horarios VARCHAR(50),
    fk_aula INT NOT NULL,
    FOREIGN KEY (fk_aula) REFERENCES Aulas(id_aula)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=INNODB;

INSERT INTO Cursos (Turno, especialidad, año, division, horarios, fk_aula)
VALUES 
('Mañana', 'Computación', 5, 7, '08:00 - 12:00', 104),
('Mañana', 'Computación', 5, 8, '13:00 - 17:00', 105),
('Mañana', 'Mecánica', 5, 1, '18:00 - 22:00', 106);



-- VISTA UNIFICADA PARA LA API
CREATE OR REPLACE VIEW vista_aulas AS
SELECT 
    a.id_aula AS id,
    a.nombre,
    a.curso,
    a.estado,
    a.especialidad,
    COUNT(c.id_curso) AS cantidad_cursos,
    MAX(c.Turno) AS turno
FROM Aulas a
LEFT JOIN Cursos c ON a.id_aula = c.fk_aula
GROUP BY a.id_aula;
ALTER TABLE aulas ADD COLUMN turno VARCHAR(50);

