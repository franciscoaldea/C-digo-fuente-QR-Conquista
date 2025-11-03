-- Crear base de datos (si no existe)
CREATE DATABASE IF NOT EXISTS QRConquista;
USE QRConquista;

-- --------------------------------------------------------
-- Estructura de tabla para la tabla `cursos`
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS `cursos` (
  `id_curso` INT(11) NOT NULL AUTO_INCREMENT,
  `Turno` VARCHAR(20) NOT NULL,
  `especialidad` VARCHAR(25) DEFAULT NULL,
  `año` INT(11) NOT NULL,
  `division` INT(11) NOT NULL,
  `horarios` DATE DEFAULT NULL,
  PRIMARY KEY (`id_curso`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------
-- Estructura de tabla para la tabla `aulas`
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS `aulas` (
  `id_aula` INT(11) NOT NULL AUTO_INCREMENT,
  `ubicacion` VARCHAR(20) NOT NULL,
  `id_curso` INT(11) DEFAULT NULL,
  PRIMARY KEY (`id_aula`),
  KEY `id_curso` (`id_curso`),
  CONSTRAINT `aulas_ibfk_1` FOREIGN KEY (`id_curso`) REFERENCES `cursos` (`id_curso`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------
-- Estructura de tabla para la tabla `tipos_de_usuario`
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS `tipos_de_usuario` (
  `tipo_usuario` VARCHAR(20) NOT NULL,
  PRIMARY KEY (`tipo_usuario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------
-- Estructura de tabla para la tabla `usuario`
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS `Usuario` (
  `nombre_usuario` VARCHAR(20) DEFAULT NULL,
  `gmail` VARCHAR(50) DEFAULT NULL,
  `contrasena` VARCHAR(20) DEFAULT NULL,
  `tipo_usuario` VARCHAR(20) DEFAULT NULL,
  KEY `tipo_usuario` (`tipo_usuario`),
  CONSTRAINT `usuario_ibfk_1` FOREIGN KEY (`tipo_usuario`) REFERENCES `tipos_de_usuario` (`tipo_usuario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------
-- Inserciones de ejemplo
-- --------------------------------------------------------
INSERT INTO `cursos` (`Turno`, `especialidad`, `año`, `division`, `horarios`) VALUES
('Mañana', 'Computación', 5, 7, NULL);

INSERT INTO `usuario` (`nombre_usuario`, `gmail`, `contrasena`, `tipo_usuario`) VALUES
('fran', NULL, '123', NULL);

COMMIT;

select * from usuario;
