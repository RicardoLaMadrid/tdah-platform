-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 13-05-2026 a las 21:48:00
-- Versión del servidor: 10.4.32-MariaDB
-- Versión de PHP: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `tdah_platform`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `activities`
--

CREATE TABLE `activities` (
  `id` int(11) NOT NULL,
  `student_id` int(11) NOT NULL,
  `teacher_id` int(11) NOT NULL,
  `title` varchar(200) NOT NULL,
  `description` text DEFAULT NULL,
  `ar_content` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`ar_content`)),
  `difficulty_level` int(11) DEFAULT NULL,
  `activity_type` varchar(50) DEFAULT NULL COMMENT 'vision, audio, stroop, gonogo, ar_caza, ar_secuencia, ar_respiracion',
  `instructions` text DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `created_by` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `activities`
--

INSERT INTO `activities` (`id`, `student_id`, `teacher_id`, `title`, `description`, `ar_content`, `difficulty_level`, `activity_type`, `instructions`, `created_at`, `created_by`) VALUES
(1, 1, 2, 'Encuentra las Diferencias AR', 'Juego de atención visual con realidad aumentada', '{\"enabled\": true, \"type\": \"markerless\"}', 2, 'atencion', '1. Escanea el entorno\n2. Toca los objetos\n3. Encuentra diferencias', '2025-12-05 21:25:33', NULL),
(2, 2, 3, 'Secuencia de Colores', 'Memoriza y repite secuencias', '{\"enabled\": false}', 1, 'memoria', '1. Observa\n2. Memoriza\n3. Repite', '2025-12-05 21:25:33', NULL);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `ar_activity_data`
--

CREATE TABLE `ar_activity_data` (
  `id` int(11) NOT NULL,
  `report_id` int(11) NOT NULL,
  `activity_type` varchar(50) NOT NULL COMMENT 'ar_caza, ar_secuencia, ar_respiracion',
  `score` float DEFAULT 0,
  `errors` int(11) DEFAULT 0,
  `time_taken` int(11) DEFAULT 0 COMMENT 'Tiempo en segundos',
  `attempts` int(11) DEFAULT 1,
  `objects_found` int(11) DEFAULT 0 COMMENT 'Para caza de objetos',
  `sequence_length` int(11) DEFAULT 0 COMMENT 'Para secuencia',
  `breathing_consistency` float DEFAULT NULL COMMENT 'Para respiraci├│n',
  `detailed_data` text DEFAULT NULL COMMENT 'JSON con datos adicionales',
  `created_at` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `audio_test_data`
--

CREATE TABLE `audio_test_data` (
  `id` int(11) NOT NULL,
  `report_id` int(11) NOT NULL,
  `reaction_times` text DEFAULT NULL COMMENT 'JSON con tiempos de reacci├│n',
  `correct_responses` int(11) DEFAULT 0,
  `false_positives` int(11) DEFAULT 0,
  `missed_responses` int(11) DEFAULT 0,
  `avg_reaction_time` float DEFAULT NULL,
  `audio_file_path` varchar(255) DEFAULT NULL,
  `created_at` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `gonogo_test_data`
--

CREATE TABLE `gonogo_test_data` (
  `id` int(11) NOT NULL,
  `report_id` int(11) NOT NULL,
  `go_trials` int(11) DEFAULT 0,
  `nogo_trials` int(11) DEFAULT 0,
  `go_correct` int(11) DEFAULT 0,
  `nogo_correct` int(11) DEFAULT 0,
  `go_accuracy` float DEFAULT NULL,
  `nogo_accuracy` float DEFAULT NULL,
  `false_alarms` int(11) DEFAULT 0,
  `avg_reaction_time` float DEFAULT NULL,
  `created_at` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `notifications`
--

CREATE TABLE `notifications` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `title` varchar(200) DEFAULT NULL,
  `message` text DEFAULT NULL,
  `type` varchar(50) DEFAULT NULL,
  `is_read` tinyint(1) DEFAULT 0,
  `related_student_id` int(11) DEFAULT NULL,
  `created_at` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `notifications`
--

INSERT INTO `notifications` (`id`, `user_id`, `title`, `message`, `type`, `is_read`, `related_student_id`, `created_at`) VALUES
(1, 16, '¡Bienvenido/a al Sistema!', 'Tu cuenta ha sido vinculada con el estudiante juan_estudiante. Ahora puedes hacer seguimiento de su progreso.', 'info', 0, 8, '2025-12-09 19:16:55'),
(2, 16, 'Test de Visión Completado', 'juan_estudiante ha completado un test de visión. Puedes revisar los resultados en su perfil.', 'test_completed', 0, 8, '2025-12-09 19:16:55'),
(3, 15, 'Cuenta vinculada', 'Tu cuenta ha sido vinculada con el estudiante lucia', 'info', 0, 2, '2025-12-10 06:15:01');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `parents`
--

CREATE TABLE `parents` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `created_at` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `parents`
--

INSERT INTO `parents` (`id`, `user_id`, `phone`, `created_at`) VALUES
(1, 15, '71766383', '2025-12-09 19:14:55'),
(2, 16, '+591 70123456', '2025-12-09 19:16:55');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `parent_student`
--

CREATE TABLE `parent_student` (
  `id` int(11) NOT NULL,
  `parent_id` int(11) NOT NULL,
  `student_id` int(11) NOT NULL,
  `relationship` varchar(50) DEFAULT 'padre/madre',
  `created_at` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `parent_student`
--

INSERT INTO `parent_student` (`id`, `parent_id`, `student_id`, `relationship`, `created_at`) VALUES
(1, 2, 8, 'madre', '2025-12-09 19:16:55'),
(2, 1, 2, 'padre', '2025-12-10 06:15:01');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `reports`
--

CREATE TABLE `reports` (
  `id` int(11) NOT NULL,
  `student_id` int(11) NOT NULL,
  `teacher_id` int(11) DEFAULT NULL,
  `session_id` int(11) DEFAULT NULL,
  `report_type` varchar(50) DEFAULT NULL,
  `content` text DEFAULT NULL,
  `recommendations` text DEFAULT NULL,
  `sent_to_parents` tinyint(1) DEFAULT NULL,
  `parent_email` varchar(100) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `test_type` varchar(50) DEFAULT 'vision',
  `tipo_tdah` varchar(50) DEFAULT 'sin_determinar',
  `confianza` float DEFAULT 0,
  `result_data` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `reports`
--

INSERT INTO `reports` (`id`, `student_id`, `teacher_id`, `session_id`, `report_type`, `content`, `recommendations`, `sent_to_parents`, `parent_email`, `created_at`, `test_type`, `tipo_tdah`, `confianza`, `result_data`) VALUES
(1, 1, NULL, NULL, NULL, '{\"tipo_tdah\": \"inatento\", \"confianza\": 0, \"metricas\": {\"frames_procesados\": 297, \"dispersion_promedio\": 35.17, \"atencion_central\": 100.0, \"atencion_periferica\": 0.0, \"atencion_dispersa\": 0.0}, \"duracion\": 30}', 'Tipo detectado: inatento con 0% de confianza', 0, NULL, '2025-12-08 05:10:00', 'vision', 'sin_determinar', 0, '{\"tipo_tdah\": \"inatento\", \"confianza\": 0, \"metricas\": {\"frames_procesados\": 297, \"dispersion_promedio\": 35.17, \"atencion_central\": 100.0, \"atencion_periferica\": 0.0, \"atencion_dispersa\": 0.0}, \"duracion\": 30}'),
(2, 1, NULL, NULL, NULL, '{\"tipo_tdah\": \"inatento\", \"confianza\": 0, \"metricas\": {\"frames_procesados\": 297, \"dispersion_promedio\": 31.15, \"atencion_central\": 98.56, \"atencion_periferica\": 1.44, \"atencion_dispersa\": 0.0}, \"duracion\": 30}', 'Tipo detectado: inatento con 0% de confianza', 0, NULL, '2025-12-08 05:10:39', 'vision', 'sin_determinar', 0, '{\"tipo_tdah\": \"inatento\", \"confianza\": 0, \"metricas\": {\"frames_procesados\": 297, \"dispersion_promedio\": 31.15, \"atencion_central\": 98.56, \"atencion_periferica\": 1.44, \"atencion_dispersa\": 0.0}, \"duracion\": 30}'),
(3, 1, NULL, NULL, 'vision_test', '{\"tipo_tdah\": \"inatento\", \"confianza\": 0, \"metricas\": {\"frames_procesados\": 261, \"dispersion_promedio\": 35.42, \"atencion_central\": 85.97, \"atencion_periferica\": 14.03, \"atencion_dispersa\": 0.0}, \"duracion\": 30}', 'Tipo detectado: inatento con 0% de confianza', 0, NULL, '2025-12-08 05:46:19', 'vision', 'sin_determinar', 0, '{\"tipo_tdah\": \"inatento\", \"confianza\": 0, \"metricas\": {\"frames_procesados\": 261, \"dispersion_promedio\": 35.42, \"atencion_central\": 85.97, \"atencion_periferica\": 14.03, \"atencion_dispersa\": 0.0}, \"duracion\": 30}'),
(4, 7, NULL, NULL, 'vision_test', '{\"tipo_tdah\": \"inatento\", \"confianza\": 0, \"metricas\": {\"frames_procesados\": 300, \"dispersion_promedio\": 35.37, \"atencion_central\": 99.65, \"atencion_periferica\": 0.35, \"atencion_dispersa\": 0.0}, \"duracion\": 30}', 'Tipo detectado: inatento con 0% de confianza', 0, NULL, '2025-12-08 05:50:01', 'vision', 'sin_determinar', 0, '{\"tipo_tdah\": \"inatento\", \"confianza\": 0, \"metricas\": {\"frames_procesados\": 300, \"dispersion_promedio\": 35.37, \"atencion_central\": 99.65, \"atencion_periferica\": 0.35, \"atencion_dispersa\": 0.0}, \"duracion\": 30}'),
(5, 7, NULL, NULL, 'vision_test', '{\"tipo_tdah\": \"inatento\", \"confianza\": 0, \"metricas\": {\"frames_procesados\": 294, \"dispersion_promedio\": 37.1, \"atencion_central\": 84.52, \"atencion_periferica\": 15.48, \"atencion_dispersa\": 0.0}, \"duracion\": 30}', 'Tipo detectado: inatento con 0% de confianza', 0, NULL, '2025-12-08 05:58:21', 'vision', 'sin_determinar', 0, '{\"tipo_tdah\": \"inatento\", \"confianza\": 0, \"metricas\": {\"frames_procesados\": 294, \"dispersion_promedio\": 37.1, \"atencion_central\": 84.52, \"atencion_periferica\": 15.48, \"atencion_dispersa\": 0.0}, \"duracion\": 30}'),
(6, 1, NULL, NULL, 'vision_test', '{\"tipo_tdah\": \"inatento\", \"confianza\": 48, \"metricas\": {\"frames_procesados\": 296, \"dispersion_promedio\": 35.49, \"atencion_central\": 48.91, \"atencion_periferica\": 51.09, \"atencion_dispersa\": 0.0}, \"duracion\": 30}', 'Tipo detectado: inatento con 48% de confianza', 0, NULL, '2025-12-08 06:04:26', 'vision', 'sin_determinar', 48, '{\"tipo_tdah\": \"inatento\", \"confianza\": 48, \"metricas\": {\"frames_procesados\": 296, \"dispersion_promedio\": 35.49, \"atencion_central\": 48.91, \"atencion_periferica\": 51.09, \"atencion_dispersa\": 0.0}, \"duracion\": 30}'),
(7, 1, NULL, NULL, 'vision_test', '{\"tipo_tdah\": \"typical\", \"confianza\": 52, \"scores_detallados\": {\"typical\": {\"probabilidad\": 52.3, \"detalles\": {\"atencion_central\": {\"valor\": 99.32, \"rango_esperado\": [75, 95], \"match\": 95.5}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [10, 25], \"match\": 0}, \"atencion_periferica\": {\"valor\": 0.68, \"rango_esperado\": [5, 20], \"match\": 13.6}, \"atencion_dispersa\": {\"valor\": 0.0, \"rango_esperado\": [0, 10], \"match\": 100}}, \"severidad\": \"Moderada\"}, \"inatento\": {\"probabilidad\": 15.4, \"detalles\": {\"atencion_central\": {\"valor\": 99.32, \"rango_esperado\": [40, 70], \"match\": 58.1}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [15, 35], \"match\": 0}, \"atencion_periferica\": {\"valor\": 0.68, \"rango_esperado\": [20, 40], \"match\": 3.4}, \"atencion_dispersa\": {\"valor\": 0.0, \"rango_esperado\": [5, 20], \"match\": 0}}, \"severidad\": \"Mínima\"}, \"hiperactivo\": {\"probabilidad\": 18.0, \"detalles\": {\"atencion_central\": {\"valor\": 99.32, \"rango_esperado\": [50, 75], \"match\": 67.6}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [35, 70], \"match\": 0}, \"atencion_periferica\": {\"valor\": 0.68, \"rango_esperado\": [15, 35], \"match\": 4.5}, \"atencion_dispersa\": {\"valor\": 0.0, \"rango_esperado\": [10, 25], \"match\": 0}}, \"severidad\": \"Mínima\"}, \"combinado\": {\"probabilidad\": 9.3, \"detalles\": {\"atencion_central\": {\"valor\": 99.32, \"rango_esperado\": [30, 60], \"match\": 34.5}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [30, 60], \"match\": 0}, \"atencion_periferica\": {\"valor\": 0.68, \"rango_esperado\": [25, 45], \"match\": 2.7}, \"atencion_dispersa\": {\"valor\": 0.0, \"rango_esperado\": [15, 35], \"match\": 0}}, \"severidad\": \"Mínima\"}}, \"metricas\": {\"frames_procesados\": 299, \"dispersion_promedio\": 39.91, \"atencion_central\": 99.32, \"atencion_periferica\": 0.68, \"atencion_dispersa\": 0.0}, \"duracion\": 30, \"interpretacion\": \"Los patrones observados están dentro del rango típico. La atención y el control de la mirada son adecuados para la edad.\"}', 'Tipo principal: typical (52%). Los patrones observados están dentro del rango típico. La atención y el control de la mirada son adecuados para la edad.', 0, NULL, '2025-12-08 06:15:19', 'vision', 'sin_determinar', 52, '{\"tipo_tdah\": \"typical\", \"confianza\": 52, \"scores_detallados\": {\"typical\": {\"probabilidad\": 52.3, \"detalles\": {\"atencion_central\": {\"valor\": 99.32, \"rango_esperado\": [75, 95], \"match\": 95.5}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [10, 25], \"match\": 0}, \"atencion_periferica\": {\"valor\": 0.68, \"rango_esperado\": [5, 20], \"match\": 13.6}, \"atencion_dispersa\": {\"valor\": 0.0, \"rango_esperado\": [0, 10], \"match\": 100}}, \"severidad\": \"Moderada\"}, \"inatento\": {\"probabilidad\": 15.4, \"detalles\": {\"atencion_central\": {\"valor\": 99.32, \"rango_esperado\": [40, 70], \"match\": 58.1}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [15, 35], \"match\": 0}, \"atencion_periferica\": {\"valor\": 0.68, \"rango_esperado\": [20, 40], \"match\": 3.4}, \"atencion_dispersa\": {\"valor\": 0.0, \"rango_esperado\": [5, 20], \"match\": 0}}, \"severidad\": \"Mínima\"}, \"hiperactivo\": {\"probabilidad\": 18.0, \"detalles\": {\"atencion_central\": {\"valor\": 99.32, \"rango_esperado\": [50, 75], \"match\": 67.6}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [35, 70], \"match\": 0}, \"atencion_periferica\": {\"valor\": 0.68, \"rango_esperado\": [15, 35], \"match\": 4.5}, \"atencion_dispersa\": {\"valor\": 0.0, \"rango_esperado\": [10, 25], \"match\": 0}}, \"severidad\": \"Mínima\"}, \"combinado\": {\"probabilidad\": 9.3, \"detalles\": {\"atencion_central\": {\"valor\": 99.32, \"rango_esperado\": [30, 60], \"match\": 34.5}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [30, 60], \"match\": 0}, \"atencion_periferica\": {\"valor\": 0.68, \"rango_esperado\": [25, 45], \"match\": 2.7}, \"atencion_dispersa\": {\"valor\": 0.0, \"rango_esperado\": [15, 35], \"match\": 0}}, \"severidad\": \"Mínima\"}}, \"metricas\": {\"frames_procesados\": 299, \"dispersion_promedio\": 39.91, \"atencion_central\": 99.32, \"atencion_periferica\": 0.68, \"atencion_dispersa\": 0.0}, \"duracion\": 30, \"interpretacion\": \"Los patrones observados están dentro del rango típico. La atención y el control de la mirada son adecuados para la edad.\"}'),
(8, 1, NULL, NULL, 'vision_test', '{\"tipo_tdah\": \"typical\", \"confianza\": 48, \"scores_detallados\": {\"typical\": {\"probabilidad\": 48.7, \"detalles\": {\"atencion_central\": {\"valor\": 100.0, \"rango_esperado\": [75, 95], \"match\": 94.7}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [10, 25], \"match\": 0}, \"atencion_periferica\": {\"valor\": 0.0, \"rango_esperado\": [5, 20], \"match\": 0}, \"atencion_dispersa\": {\"valor\": 0.0, \"rango_esperado\": [0, 10], \"match\": 100}}, \"severidad\": \"Moderada\"}, \"inatento\": {\"probabilidad\": 14.3, \"detalles\": {\"atencion_central\": {\"valor\": 100.0, \"rango_esperado\": [40, 70], \"match\": 57.1}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [15, 35], \"match\": 0}, \"atencion_periferica\": {\"valor\": 0.0, \"rango_esperado\": [20, 40], \"match\": 0}, \"atencion_dispersa\": {\"valor\": 0.0, \"rango_esperado\": [5, 20], \"match\": 0}}, \"severidad\": \"Mínima\"}, \"hiperactivo\": {\"probabilidad\": 16.7, \"detalles\": {\"atencion_central\": {\"valor\": 100.0, \"rango_esperado\": [50, 75], \"match\": 66.7}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [35, 70], \"match\": 0}, \"atencion_periferica\": {\"valor\": 0.0, \"rango_esperado\": [15, 35], \"match\": 0}, \"atencion_dispersa\": {\"valor\": 0.0, \"rango_esperado\": [10, 25], \"match\": 0}}, \"severidad\": \"Mínima\"}, \"combinado\": {\"probabilidad\": 8.3, \"detalles\": {\"atencion_central\": {\"valor\": 100.0, \"rango_esperado\": [30, 60], \"match\": 33.3}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [30, 60], \"match\": 0}, \"atencion_periferica\": {\"valor\": 0.0, \"rango_esperado\": [25, 45], \"match\": 0}, \"atencion_dispersa\": {\"valor\": 0.0, \"rango_esperado\": [15, 35], \"match\": 0}}, \"severidad\": \"Mínima\"}}, \"metricas\": {\"frames_procesados\": 298, \"dispersion_promedio\": 36.98, \"atencion_central\": 100.0, \"atencion_periferica\": 0.0, \"atencion_dispersa\": 0.0}, \"duracion\": 30, \"interpretacion\": \"Los patrones observados están dentro del rango típico. La atención y el control de la mirada son adecuados para la edad.\"}', 'Tipo principal: typical (48%). Los patrones observados están dentro del rango típico. La atención y el control de la mirada son adecuados para la edad.', 0, NULL, '2025-12-08 06:16:22', 'vision', 'sin_determinar', 48, '{\"tipo_tdah\": \"typical\", \"confianza\": 48, \"scores_detallados\": {\"typical\": {\"probabilidad\": 48.7, \"detalles\": {\"atencion_central\": {\"valor\": 100.0, \"rango_esperado\": [75, 95], \"match\": 94.7}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [10, 25], \"match\": 0}, \"atencion_periferica\": {\"valor\": 0.0, \"rango_esperado\": [5, 20], \"match\": 0}, \"atencion_dispersa\": {\"valor\": 0.0, \"rango_esperado\": [0, 10], \"match\": 100}}, \"severidad\": \"Moderada\"}, \"inatento\": {\"probabilidad\": 14.3, \"detalles\": {\"atencion_central\": {\"valor\": 100.0, \"rango_esperado\": [40, 70], \"match\": 57.1}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [15, 35], \"match\": 0}, \"atencion_periferica\": {\"valor\": 0.0, \"rango_esperado\": [20, 40], \"match\": 0}, \"atencion_dispersa\": {\"valor\": 0.0, \"rango_esperado\": [5, 20], \"match\": 0}}, \"severidad\": \"Mínima\"}, \"hiperactivo\": {\"probabilidad\": 16.7, \"detalles\": {\"atencion_central\": {\"valor\": 100.0, \"rango_esperado\": [50, 75], \"match\": 66.7}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [35, 70], \"match\": 0}, \"atencion_periferica\": {\"valor\": 0.0, \"rango_esperado\": [15, 35], \"match\": 0}, \"atencion_dispersa\": {\"valor\": 0.0, \"rango_esperado\": [10, 25], \"match\": 0}}, \"severidad\": \"Mínima\"}, \"combinado\": {\"probabilidad\": 8.3, \"detalles\": {\"atencion_central\": {\"valor\": 100.0, \"rango_esperado\": [30, 60], \"match\": 33.3}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [30, 60], \"match\": 0}, \"atencion_periferica\": {\"valor\": 0.0, \"rango_esperado\": [25, 45], \"match\": 0}, \"atencion_dispersa\": {\"valor\": 0.0, \"rango_esperado\": [15, 35], \"match\": 0}}, \"severidad\": \"Mínima\"}}, \"metricas\": {\"frames_procesados\": 298, \"dispersion_promedio\": 36.98, \"atencion_central\": 100.0, \"atencion_periferica\": 0.0, \"atencion_dispersa\": 0.0}, \"duracion\": 30, \"interpretacion\": \"Los patrones observados están dentro del rango típico. La atención y el control de la mirada son adecuados para la edad.\"}'),
(9, 1, NULL, NULL, 'vision_test', '{\"tipo_tdah\": \"inatento\", \"confianza\": 50, \"scores_detallados\": {\"typical\": {\"probabilidad\": 49.5, \"detalles\": {\"atencion_central\": {\"valor\": 62.82, \"rango_esperado\": [75, 95], \"match\": 83.8}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [10, 25], \"match\": 0}, \"atencion_periferica\": {\"valor\": 37.18, \"rango_esperado\": [5, 20], \"match\": 14.1}, \"atencion_dispersa\": {\"valor\": 0.0, \"rango_esperado\": [0, 10], \"match\": 100}}, \"severidad\": \"Moderada\"}, \"inatento\": {\"probabilidad\": 50.0, \"detalles\": {\"atencion_central\": {\"valor\": 62.82, \"rango_esperado\": [40, 70], \"match\": 100}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [15, 35], \"match\": 0}, \"atencion_periferica\": {\"valor\": 37.18, \"rango_esperado\": [20, 40], \"match\": 100}, \"atencion_dispersa\": {\"valor\": 0.0, \"rango_esperado\": [5, 20], \"match\": 0}}, \"severidad\": \"Moderada\"}, \"hiperactivo\": {\"probabilidad\": 48.4, \"detalles\": {\"atencion_central\": {\"valor\": 62.82, \"rango_esperado\": [50, 75], \"match\": 100}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [35, 70], \"match\": 0}, \"atencion_periferica\": {\"valor\": 37.18, \"rango_esperado\": [15, 35], \"match\": 93.8}, \"atencion_dispersa\": {\"valor\": 0.0, \"rango_esperado\": [10, 25], \"match\": 0}}, \"severidad\": \"Moderada\"}, \"combinado\": {\"probabilidad\": 48.8, \"detalles\": {\"atencion_central\": {\"valor\": 62.82, \"rango_esperado\": [30, 60], \"match\": 95.3}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [30, 60], \"match\": 0}, \"atencion_periferica\": {\"valor\": 37.18, \"rango_esperado\": [25, 45], \"match\": 100}, \"atencion_dispersa\": {\"valor\": 0.0, \"rango_esperado\": [15, 35], \"match\": 0}}, \"severidad\": \"Moderada\"}}, \"metricas\": {\"frames_procesados\": 189, \"dispersion_promedio\": 57.45, \"atencion_central\": 62.82, \"atencion_periferica\": 37.18, \"atencion_dispersa\": 0.0}, \"duracion\": 30, \"interpretacion\": \"Se observan patrones consistentes con dificultades de atención. La mirada tiende a dispersarse y hay dificultad para mantener el foco central.\\n\\nTambién se observan características de: typical (49.5%), combinado (48.8%), hiperactivo (48.4%)\"}', 'Tipo principal: inatento (50%). Se observan patrones consistentes con dificultades de atención. La mirada tiende a dispersarse y hay dificultad para mantener el foco central.\n\nTambién se observan características de: typical (49.5%),', 0, NULL, '2025-12-08 06:17:12', 'vision', 'sin_determinar', 50, '{\"tipo_tdah\": \"inatento\", \"confianza\": 50, \"scores_detallados\": {\"typical\": {\"probabilidad\": 49.5, \"detalles\": {\"atencion_central\": {\"valor\": 62.82, \"rango_esperado\": [75, 95], \"match\": 83.8}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [10, 25], \"match\": 0}, \"atencion_periferica\": {\"valor\": 37.18, \"rango_esperado\": [5, 20], \"match\": 14.1}, \"atencion_dispersa\": {\"valor\": 0.0, \"rango_esperado\": [0, 10], \"match\": 100}}, \"severidad\": \"Moderada\"}, \"inatento\": {\"probabilidad\": 50.0, \"detalles\": {\"atencion_central\": {\"valor\": 62.82, \"rango_esperado\": [40, 70], \"match\": 100}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [15, 35], \"match\": 0}, \"atencion_periferica\": {\"valor\": 37.18, \"rango_esperado\": [20, 40], \"match\": 100}, \"atencion_dispersa\": {\"valor\": 0.0, \"rango_esperado\": [5, 20], \"match\": 0}}, \"severidad\": \"Moderada\"}, \"hiperactivo\": {\"probabilidad\": 48.4, \"detalles\": {\"atencion_central\": {\"valor\": 62.82, \"rango_esperado\": [50, 75], \"match\": 100}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [35, 70], \"match\": 0}, \"atencion_periferica\": {\"valor\": 37.18, \"rango_esperado\": [15, 35], \"match\": 93.8}, \"atencion_dispersa\": {\"valor\": 0.0, \"rango_esperado\": [10, 25], \"match\": 0}}, \"severidad\": \"Moderada\"}, \"combinado\": {\"probabilidad\": 48.8, \"detalles\": {\"atencion_central\": {\"valor\": 62.82, \"rango_esperado\": [30, 60], \"match\": 95.3}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [30, 60], \"match\": 0}, \"atencion_periferica\": {\"valor\": 37.18, \"rango_esperado\": [25, 45], \"match\": 100}, \"atencion_dispersa\": {\"valor\": 0.0, \"rango_esperado\": [15, 35], \"match\": 0}}, \"severidad\": \"Moderada\"}}, \"metricas\": {\"frames_procesados\": 189, \"dispersion_promedio\": 57.45, \"atencion_central\": 62.82, \"atencion_periferica\": 37.18, \"atencion_dispersa\": 0.0}, \"duracion\": 30, \"interpretacion\": \"Se observan patrones consistentes con dificultades de atención. La mirada tiende a dispersarse y hay dificultad para mantener el foco central.\\n\\nTambién se observan características de: typical (49.5%), combinado (48.8%), hiperactivo (48.4%)\"}'),
(10, 7, NULL, NULL, 'audio_test', '{\"transcripcion\": \"el viaje hacia el autoconocimiento es fundamental para comprender nuestras fortalezas y debilidades muchas personas se encuentran difícil mantener la concentración en teorías prolongadas Especialmente cuando hay múltiples estímulos en el ambiente la capacidad de regular la tensión es una habilidad que puede desarrollarse con práctica constante y estrategias adecuadas\", \"metricas\": {\"duracion_grabacion\": 28.672, \"palabras_correctas\": 48, \"palabras_totales\": 49, \"precision\": 97.95918367346938, \"pausas_detectadas\": 0, \"repeticiones\": 7, \"fluidez\": 68.33090379008748, \"velocidad_lectura\": 104.63169642857143}, \"tipo_tdah\": \"hiperactivo\", \"confianza\": 20}', 'Tipo detectado: hiperactivo con 20% de confianza', 0, NULL, '2025-12-08 06:37:41', 'vision', 'sin_determinar', 20, '{\"transcripcion\": \"el viaje hacia el autoconocimiento es fundamental para comprender nuestras fortalezas y debilidades muchas personas se encuentran difícil mantener la concentración en teorías prolongadas Especialmente cuando hay múltiples estímulos en el ambiente la capacidad de regular la tensión es una habilidad que puede desarrollarse con práctica constante y estrategias adecuadas\", \"metricas\": {\"duracion_grabacion\": 28.672, \"palabras_correctas\": 48, \"palabras_totales\": 49, \"precision\": 97.95918367346938, \"pausas_detectadas\": 0, \"repeticiones\": 7, \"fluidez\": 68.33090379008748, \"velocidad_lectura\": 104.63169642857143}, \"tipo_tdah\": \"hiperactivo\", \"confianza\": 20}'),
(11, 1, NULL, NULL, 'audio_test', '{\"transcripcion\": \"el viaje es el autoconocimiento es fundamental para comprender nuestras fortalezas y debilidades muchas personas se encuentran difícil mantener la constitución en tareas prolongadas Especialmente cuando hay múltiples estímulos en ambiente la capacidad de regular la tensión es una habilidad que puede desarrollarse con práctica constante y estrategias adecuadas\", \"metricas\": {\"duracion_grabacion\": 26.795, \"palabras_correctas\": 46, \"palabras_totales\": 49, \"precision\": 93.87755102040816, \"pausas_detectadas\": 0, \"repeticiones\": 7, \"fluidez\": 68.6695278969957, \"velocidad_lectura\": 109.72196305280835}, \"tipo_tdah\": \"hiperactivo\", \"confianza\": 20}', 'Tipo detectado: hiperactivo con 20% de confianza', 0, NULL, '2025-12-08 17:06:36', 'vision', 'sin_determinar', 20, '{\"transcripcion\": \"el viaje es el autoconocimiento es fundamental para comprender nuestras fortalezas y debilidades muchas personas se encuentran difícil mantener la constitución en tareas prolongadas Especialmente cuando hay múltiples estímulos en ambiente la capacidad de regular la tensión es una habilidad que puede desarrollarse con práctica constante y estrategias adecuadas\", \"metricas\": {\"duracion_grabacion\": 26.795, \"palabras_correctas\": 46, \"palabras_totales\": 49, \"precision\": 93.87755102040816, \"pausas_detectadas\": 0, \"repeticiones\": 7, \"fluidez\": 68.6695278969957, \"velocidad_lectura\": 109.72196305280835}, \"tipo_tdah\": \"hiperactivo\", \"confianza\": 20}'),
(12, 1, NULL, NULL, 'audio_test', '{\"transcripcion\": \"el viaje hacia el autoconocimiento es fundamental para comprender nuestras fortalezas y debilidades muchas personas se encuentran difícil mantener la concentración en tareas prolongadas Especialmente cuando hay múltiples estímulos en el ambiente la capacidad de regular la atención es una habilidad que puede desarrollarse con práctica constante y estrategias adecuadas\", \"metricas\": {\"duracion_grabacion\": 22.101, \"palabras_correctas\": 49, \"palabras_totales\": 49, \"precision\": 100.0, \"pausas_detectadas\": 0, \"repeticiones\": 7, \"fluidez\": 90.49364282159178, \"velocidad_lectura\": 135.74046423238767}, \"tipo_tdah\": \"hiperactivo\", \"confianza\": 20}', 'Tipo detectado: hiperactivo con 20% de confianza', 0, NULL, '2025-12-08 17:07:45', 'vision', 'sin_determinar', 20, '{\"transcripcion\": \"el viaje hacia el autoconocimiento es fundamental para comprender nuestras fortalezas y debilidades muchas personas se encuentran difícil mantener la concentración en tareas prolongadas Especialmente cuando hay múltiples estímulos en el ambiente la capacidad de regular la atención es una habilidad que puede desarrollarse con práctica constante y estrategias adecuadas\", \"metricas\": {\"duracion_grabacion\": 22.101, \"palabras_correctas\": 49, \"palabras_totales\": 49, \"precision\": 100.0, \"pausas_detectadas\": 0, \"repeticiones\": 7, \"fluidez\": 90.49364282159178, \"velocidad_lectura\": 135.74046423238767}, \"tipo_tdah\": \"hiperactivo\", \"confianza\": 20}'),
(13, 1, NULL, NULL, 'vision_test', '{\"tipo_tdah\": \"typical\", \"confianza\": 25, \"scores_detallados\": {\"typical\": {\"probabilidad\": 25.0, \"detalles\": {\"atencion_central\": {\"valor\": 0, \"rango_esperado\": [75, 95], \"match\": 0}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [10, 25], \"match\": 0}, \"atencion_periferica\": {\"valor\": 0, \"rango_esperado\": [5, 20], \"match\": 0}, \"atencion_dispersa\": {\"valor\": 0, \"rango_esperado\": [0, 10], \"match\": 100}}, \"severidad\": \"Leve\"}, \"inatento\": {\"probabilidad\": 0.0, \"detalles\": {\"atencion_central\": {\"valor\": 0, \"rango_esperado\": [40, 70], \"match\": 0}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [15, 35], \"match\": 0}, \"atencion_periferica\": {\"valor\": 0, \"rango_esperado\": [20, 40], \"match\": 0}, \"atencion_dispersa\": {\"valor\": 0, \"rango_esperado\": [5, 20], \"match\": 0}}, \"severidad\": \"Mínima\"}, \"hiperactivo\": {\"probabilidad\": 0.0, \"detalles\": {\"atencion_central\": {\"valor\": 0, \"rango_esperado\": [50, 75], \"match\": 0}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [35, 70], \"match\": 0}, \"atencion_periferica\": {\"valor\": 0, \"rango_esperado\": [15, 35], \"match\": 0}, \"atencion_dispersa\": {\"valor\": 0, \"rango_esperado\": [10, 25], \"match\": 0}}, \"severidad\": \"Mínima\"}, \"combinado\": {\"probabilidad\": 0.0, \"detalles\": {\"atencion_central\": {\"valor\": 0, \"rango_esperado\": [30, 60], \"match\": 0}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [30, 60], \"match\": 0}, \"atencion_periferica\": {\"valor\": 0, \"rango_esperado\": [25, 45], \"match\": 0}, \"atencion_dispersa\": {\"valor\": 0, \"rango_esperado\": [15, 35], \"match\": 0}}, \"severidad\": \"Mínima\"}}, \"metricas\": {\"frames_procesados\": 299, \"dispersion_promedio\": 0, \"atencion_central\": 0, \"atencion_periferica\": 0, \"atencion_dispersa\": 0}, \"duracion\": 30, \"interpretacion\": \"Los patrones observados están dentro del rango típico. La atención y el control de la mirada son adecuados para la edad.\"}', 'Tipo principal: typical (25%). Los patrones observados están dentro del rango típico. La atención y el control de la mirada son adecuados para la edad.', 0, NULL, '2025-12-08 17:49:30', 'vision', 'sin_determinar', 25, '{\"tipo_tdah\": \"typical\", \"confianza\": 25, \"scores_detallados\": {\"typical\": {\"probabilidad\": 25.0, \"detalles\": {\"atencion_central\": {\"valor\": 0, \"rango_esperado\": [75, 95], \"match\": 0}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [10, 25], \"match\": 0}, \"atencion_periferica\": {\"valor\": 0, \"rango_esperado\": [5, 20], \"match\": 0}, \"atencion_dispersa\": {\"valor\": 0, \"rango_esperado\": [0, 10], \"match\": 100}}, \"severidad\": \"Leve\"}, \"inatento\": {\"probabilidad\": 0.0, \"detalles\": {\"atencion_central\": {\"valor\": 0, \"rango_esperado\": [40, 70], \"match\": 0}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [15, 35], \"match\": 0}, \"atencion_periferica\": {\"valor\": 0, \"rango_esperado\": [20, 40], \"match\": 0}, \"atencion_dispersa\": {\"valor\": 0, \"rango_esperado\": [5, 20], \"match\": 0}}, \"severidad\": \"Mínima\"}, \"hiperactivo\": {\"probabilidad\": 0.0, \"detalles\": {\"atencion_central\": {\"valor\": 0, \"rango_esperado\": [50, 75], \"match\": 0}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [35, 70], \"match\": 0}, \"atencion_periferica\": {\"valor\": 0, \"rango_esperado\": [15, 35], \"match\": 0}, \"atencion_dispersa\": {\"valor\": 0, \"rango_esperado\": [10, 25], \"match\": 0}}, \"severidad\": \"Mínima\"}, \"combinado\": {\"probabilidad\": 0.0, \"detalles\": {\"atencion_central\": {\"valor\": 0, \"rango_esperado\": [30, 60], \"match\": 0}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [30, 60], \"match\": 0}, \"atencion_periferica\": {\"valor\": 0, \"rango_esperado\": [25, 45], \"match\": 0}, \"atencion_dispersa\": {\"valor\": 0, \"rango_esperado\": [15, 35], \"match\": 0}}, \"severidad\": \"Mínima\"}}, \"metricas\": {\"frames_procesados\": 299, \"dispersion_promedio\": 0, \"atencion_central\": 0, \"atencion_periferica\": 0, \"atencion_dispersa\": 0}, \"duracion\": 30, \"interpretacion\": \"Los patrones observados están dentro del rango típico. La atención y el control de la mirada son adecuados para la edad.\"}'),
(14, 1, NULL, NULL, 'audio_test', '{\"transcripcion\": \"el viaje hacia el autoconocimiento es fundamental para comprender nuestras fortalezas y debilidades muchas personas se encuentran difícil mantener la concentración en tareas prolongadas Especialmente cuando hay múltiples estímulos en el ambiente la capacidad de regular la atención es una habilidad que puede desarrollarse con práctica constante y estrategias adecuadas\", \"metricas\": {\"duracion_grabacion\": 29.44, \"palabras_correctas\": 49, \"palabras_totales\": 49, \"precision\": 100.0, \"pausas_detectadas\": 0, \"repeticiones\": 7, \"fluidez\": 67.93478260869564, \"velocidad_lectura\": 101.90217391304347}, \"tipo_tdah\": \"hiperactivo\", \"confianza\": 20}', 'Tipo detectado: hiperactivo con 20% de confianza', 0, NULL, '2025-12-08 17:50:45', 'vision', 'sin_determinar', 20, '{\"transcripcion\": \"el viaje hacia el autoconocimiento es fundamental para comprender nuestras fortalezas y debilidades muchas personas se encuentran difícil mantener la concentración en tareas prolongadas Especialmente cuando hay múltiples estímulos en el ambiente la capacidad de regular la atención es una habilidad que puede desarrollarse con práctica constante y estrategias adecuadas\", \"metricas\": {\"duracion_grabacion\": 29.44, \"palabras_correctas\": 49, \"palabras_totales\": 49, \"precision\": 100.0, \"pausas_detectadas\": 0, \"repeticiones\": 7, \"fluidez\": 67.93478260869564, \"velocidad_lectura\": 101.90217391304347}, \"tipo_tdah\": \"hiperactivo\", \"confianza\": 20}'),
(15, 7, NULL, NULL, 'vision_test', '{\"tipo_tdah\": \"typical\", \"confianza\": 48, \"scores_detallados\": {\"typical\": {\"probabilidad\": 48.7, \"detalles\": {\"atencion_central\": {\"valor\": 100.0, \"rango_esperado\": [75, 95], \"match\": 94.7}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [10, 25], \"match\": 0}, \"atencion_periferica\": {\"valor\": 0.0, \"rango_esperado\": [5, 20], \"match\": 0}, \"atencion_dispersa\": {\"valor\": 0.0, \"rango_esperado\": [0, 10], \"match\": 100}}, \"severidad\": \"Moderada\"}, \"inatento\": {\"probabilidad\": 14.3, \"detalles\": {\"atencion_central\": {\"valor\": 100.0, \"rango_esperado\": [40, 70], \"match\": 57.1}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [15, 35], \"match\": 0}, \"atencion_periferica\": {\"valor\": 0.0, \"rango_esperado\": [20, 40], \"match\": 0}, \"atencion_dispersa\": {\"valor\": 0.0, \"rango_esperado\": [5, 20], \"match\": 0}}, \"severidad\": \"Mínima\"}, \"hiperactivo\": {\"probabilidad\": 16.7, \"detalles\": {\"atencion_central\": {\"valor\": 100.0, \"rango_esperado\": [50, 75], \"match\": 66.7}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [35, 70], \"match\": 0}, \"atencion_periferica\": {\"valor\": 0.0, \"rango_esperado\": [15, 35], \"match\": 0}, \"atencion_dispersa\": {\"valor\": 0.0, \"rango_esperado\": [10, 25], \"match\": 0}}, \"severidad\": \"Mínima\"}, \"combinado\": {\"probabilidad\": 8.3, \"detalles\": {\"atencion_central\": {\"valor\": 100.0, \"rango_esperado\": [30, 60], \"match\": 33.3}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [30, 60], \"match\": 0}, \"atencion_periferica\": {\"valor\": 0.0, \"rango_esperado\": [25, 45], \"match\": 0}, \"atencion_dispersa\": {\"valor\": 0.0, \"rango_esperado\": [15, 35], \"match\": 0}}, \"severidad\": \"Mínima\"}}, \"metricas\": {\"frames_procesados\": 300, \"dispersion_promedio\": 47.36, \"atencion_central\": 100.0, \"atencion_periferica\": 0.0, \"atencion_dispersa\": 0.0}, \"duracion\": 30, \"interpretacion\": \"Los patrones observados están dentro del rango típico. La atención y el control de la mirada son adecuados para la edad.\"}', 'Tipo principal: typical (48%). Los patrones observados están dentro del rango típico. La atención y el control de la mirada son adecuados para la edad.', 0, NULL, '2025-12-08 19:59:58', 'vision', 'sin_determinar', 48, '{\"tipo_tdah\": \"typical\", \"confianza\": 48, \"scores_detallados\": {\"typical\": {\"probabilidad\": 48.7, \"detalles\": {\"atencion_central\": {\"valor\": 100.0, \"rango_esperado\": [75, 95], \"match\": 94.7}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [10, 25], \"match\": 0}, \"atencion_periferica\": {\"valor\": 0.0, \"rango_esperado\": [5, 20], \"match\": 0}, \"atencion_dispersa\": {\"valor\": 0.0, \"rango_esperado\": [0, 10], \"match\": 100}}, \"severidad\": \"Moderada\"}, \"inatento\": {\"probabilidad\": 14.3, \"detalles\": {\"atencion_central\": {\"valor\": 100.0, \"rango_esperado\": [40, 70], \"match\": 57.1}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [15, 35], \"match\": 0}, \"atencion_periferica\": {\"valor\": 0.0, \"rango_esperado\": [20, 40], \"match\": 0}, \"atencion_dispersa\": {\"valor\": 0.0, \"rango_esperado\": [5, 20], \"match\": 0}}, \"severidad\": \"Mínima\"}, \"hiperactivo\": {\"probabilidad\": 16.7, \"detalles\": {\"atencion_central\": {\"valor\": 100.0, \"rango_esperado\": [50, 75], \"match\": 66.7}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [35, 70], \"match\": 0}, \"atencion_periferica\": {\"valor\": 0.0, \"rango_esperado\": [15, 35], \"match\": 0}, \"atencion_dispersa\": {\"valor\": 0.0, \"rango_esperado\": [10, 25], \"match\": 0}}, \"severidad\": \"Mínima\"}, \"combinado\": {\"probabilidad\": 8.3, \"detalles\": {\"atencion_central\": {\"valor\": 100.0, \"rango_esperado\": [30, 60], \"match\": 33.3}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [30, 60], \"match\": 0}, \"atencion_periferica\": {\"valor\": 0.0, \"rango_esperado\": [25, 45], \"match\": 0}, \"atencion_dispersa\": {\"valor\": 0.0, \"rango_esperado\": [15, 35], \"match\": 0}}, \"severidad\": \"Mínima\"}}, \"metricas\": {\"frames_procesados\": 300, \"dispersion_promedio\": 47.36, \"atencion_central\": 100.0, \"atencion_periferica\": 0.0, \"atencion_dispersa\": 0.0}, \"duracion\": 30, \"interpretacion\": \"Los patrones observados están dentro del rango típico. La atención y el control de la mirada son adecuados para la edad.\"}'),
(16, 7, NULL, NULL, 'vision_test', '{\"tipo_tdah\": \"typical\", \"confianza\": 72, \"scores_detallados\": {\"typical\": {\"probabilidad\": 72.4, \"detalles\": {\"atencion_central\": {\"valor\": 100.0, \"rango_esperado\": [75, 95], \"match\": 94.7}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [10, 25], \"match\": 0}, \"precision_seguimiento\": {\"valor\": 100.0, \"rango_esperado\": [70, 95], \"match\": 94.7}, \"reaccion_promedio\": {\"valor\": 0.5, \"rango_esperado\": [0.3, 0.8], \"match\": 100}}, \"severidad\": \"Moderada-Alta\"}, \"inatento\": {\"probabilidad\": 41.4, \"detalles\": {\"atencion_central\": {\"valor\": 100.0, \"rango_esperado\": [40, 70], \"match\": 57.1}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [15, 35], \"match\": 0}, \"precision_seguimiento\": {\"valor\": 100.0, \"rango_esperado\": [40, 65], \"match\": 46.2}, \"reaccion_promedio\": {\"valor\": 0.5, \"rango_esperado\": [0.8, 1.5], \"match\": 62.5}}, \"severidad\": \"Moderada\"}, \"hiperactivo\": {\"probabilidad\": 56.0, \"detalles\": {\"atencion_central\": {\"valor\": 100.0, \"rango_esperado\": [50, 75], \"match\": 66.7}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [35, 70], \"match\": 0}, \"precision_seguimiento\": {\"valor\": 100.0, \"rango_esperado\": [50, 70], \"match\": 57.1}, \"reaccion_promedio\": {\"valor\": 0.5, \"rango_esperado\": [0.2, 0.5], \"match\": 100}}, \"severidad\": \"Moderada\"}, \"combinado\": {\"probabilidad\": 41.7, \"detalles\": {\"atencion_central\": {\"valor\": 100.0, \"rango_esperado\": [30, 60], \"match\": 33.3}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [30, 60], \"match\": 0}, \"precision_seguimiento\": {\"valor\": 100.0, \"rango_esperado\": [35, 60], \"match\": 33.3}, \"reaccion_promedio\": {\"valor\": 0.5, \"rango_esperado\": [0.5, 1.2], \"match\": 100}}, \"severidad\": \"Moderada\"}}, \"metricas\": {\"frames_procesados\": 296, \"dispersion_promedio\": 1.52, \"atencion_central\": 100.0, \"precision_seguimiento\": 100.0, \"reaccion_promedio\": 0.5, \"puntos_completados\": 1, \"aciertos_totales\": 287, \"observaciones_totales\": 287}, \"duracion\": 30, \"interpretacion\": \"Los patrones observados están dentro del rango típico. Precisión de seguimiento: 100.0%.\"}', 'Tipo: typical (72%). Los patrones observados están dentro del rango típico. Precisión de seguimiento: 100.0%.', 0, NULL, '2025-12-08 20:07:56', 'vision', 'sin_determinar', 72, '{\"tipo_tdah\": \"typical\", \"confianza\": 72, \"scores_detallados\": {\"typical\": {\"probabilidad\": 72.4, \"detalles\": {\"atencion_central\": {\"valor\": 100.0, \"rango_esperado\": [75, 95], \"match\": 94.7}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [10, 25], \"match\": 0}, \"precision_seguimiento\": {\"valor\": 100.0, \"rango_esperado\": [70, 95], \"match\": 94.7}, \"reaccion_promedio\": {\"valor\": 0.5, \"rango_esperado\": [0.3, 0.8], \"match\": 100}}, \"severidad\": \"Moderada-Alta\"}, \"inatento\": {\"probabilidad\": 41.4, \"detalles\": {\"atencion_central\": {\"valor\": 100.0, \"rango_esperado\": [40, 70], \"match\": 57.1}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [15, 35], \"match\": 0}, \"precision_seguimiento\": {\"valor\": 100.0, \"rango_esperado\": [40, 65], \"match\": 46.2}, \"reaccion_promedio\": {\"valor\": 0.5, \"rango_esperado\": [0.8, 1.5], \"match\": 62.5}}, \"severidad\": \"Moderada\"}, \"hiperactivo\": {\"probabilidad\": 56.0, \"detalles\": {\"atencion_central\": {\"valor\": 100.0, \"rango_esperado\": [50, 75], \"match\": 66.7}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [35, 70], \"match\": 0}, \"precision_seguimiento\": {\"valor\": 100.0, \"rango_esperado\": [50, 70], \"match\": 57.1}, \"reaccion_promedio\": {\"valor\": 0.5, \"rango_esperado\": [0.2, 0.5], \"match\": 100}}, \"severidad\": \"Moderada\"}, \"combinado\": {\"probabilidad\": 41.7, \"detalles\": {\"atencion_central\": {\"valor\": 100.0, \"rango_esperado\": [30, 60], \"match\": 33.3}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [30, 60], \"match\": 0}, \"precision_seguimiento\": {\"valor\": 100.0, \"rango_esperado\": [35, 60], \"match\": 33.3}, \"reaccion_promedio\": {\"valor\": 0.5, \"rango_esperado\": [0.5, 1.2], \"match\": 100}}, \"severidad\": \"Moderada\"}}, \"metricas\": {\"frames_procesados\": 296, \"dispersion_promedio\": 1.52, \"atencion_central\": 100.0, \"precision_seguimiento\": 100.0, \"reaccion_promedio\": 0.5, \"puntos_completados\": 1, \"aciertos_totales\": 287, \"observaciones_totales\": 287}, \"duracion\": 30, \"interpretacion\": \"Los patrones observados están dentro del rango típico. Precisión de seguimiento: 100.0%.\"}'),
(17, 7, NULL, NULL, 'vision_test', '{\"tipo_tdah\": \"typical\", \"confianza\": 72, \"scores_detallados\": {\"typical\": {\"probabilidad\": 72.4, \"detalles\": {\"atencion_central\": {\"valor\": 100.0, \"rango_esperado\": [75, 95], \"match\": 94.7}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [10, 25], \"match\": 0}, \"precision_seguimiento\": {\"valor\": 100.0, \"rango_esperado\": [70, 95], \"match\": 94.7}, \"reaccion_promedio\": {\"valor\": 0.5, \"rango_esperado\": [0.3, 0.8], \"match\": 100}}, \"severidad\": \"Moderada-Alta\"}, \"inatento\": {\"probabilidad\": 41.4, \"detalles\": {\"atencion_central\": {\"valor\": 100.0, \"rango_esperado\": [40, 70], \"match\": 57.1}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [15, 35], \"match\": 0}, \"precision_seguimiento\": {\"valor\": 100.0, \"rango_esperado\": [40, 65], \"match\": 46.2}, \"reaccion_promedio\": {\"valor\": 0.5, \"rango_esperado\": [0.8, 1.5], \"match\": 62.5}}, \"severidad\": \"Moderada\"}, \"hiperactivo\": {\"probabilidad\": 56.0, \"detalles\": {\"atencion_central\": {\"valor\": 100.0, \"rango_esperado\": [50, 75], \"match\": 66.7}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [35, 70], \"match\": 0}, \"precision_seguimiento\": {\"valor\": 100.0, \"rango_esperado\": [50, 70], \"match\": 57.1}, \"reaccion_promedio\": {\"valor\": 0.5, \"rango_esperado\": [0.2, 0.5], \"match\": 100}}, \"severidad\": \"Moderada\"}, \"combinado\": {\"probabilidad\": 41.7, \"detalles\": {\"atencion_central\": {\"valor\": 100.0, \"rango_esperado\": [30, 60], \"match\": 33.3}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [30, 60], \"match\": 0}, \"precision_seguimiento\": {\"valor\": 100.0, \"rango_esperado\": [35, 60], \"match\": 33.3}, \"reaccion_promedio\": {\"valor\": 0.5, \"rango_esperado\": [0.5, 1.2], \"match\": 100}}, \"severidad\": \"Moderada\"}}, \"metricas\": {\"frames_procesados\": 297, \"dispersion_promedio\": 1.53, \"atencion_central\": 100.0, \"precision_seguimiento\": 100.0, \"reaccion_promedio\": 0.5, \"puntos_completados\": 1, \"aciertos_totales\": 288, \"observaciones_totales\": 288}, \"duracion\": 30, \"interpretacion\": \"Los patrones observados están dentro del rango típico. Precisión de seguimiento: 100.0%.\"}', 'Tipo: typical (72%). Los patrones observados están dentro del rango típico. Precisión de seguimiento: 100.0%.', 0, NULL, '2025-12-08 20:07:56', 'vision', 'sin_determinar', 72, '{\"tipo_tdah\": \"typical\", \"confianza\": 72, \"scores_detallados\": {\"typical\": {\"probabilidad\": 72.4, \"detalles\": {\"atencion_central\": {\"valor\": 100.0, \"rango_esperado\": [75, 95], \"match\": 94.7}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [10, 25], \"match\": 0}, \"precision_seguimiento\": {\"valor\": 100.0, \"rango_esperado\": [70, 95], \"match\": 94.7}, \"reaccion_promedio\": {\"valor\": 0.5, \"rango_esperado\": [0.3, 0.8], \"match\": 100}}, \"severidad\": \"Moderada-Alta\"}, \"inatento\": {\"probabilidad\": 41.4, \"detalles\": {\"atencion_central\": {\"valor\": 100.0, \"rango_esperado\": [40, 70], \"match\": 57.1}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [15, 35], \"match\": 0}, \"precision_seguimiento\": {\"valor\": 100.0, \"rango_esperado\": [40, 65], \"match\": 46.2}, \"reaccion_promedio\": {\"valor\": 0.5, \"rango_esperado\": [0.8, 1.5], \"match\": 62.5}}, \"severidad\": \"Moderada\"}, \"hiperactivo\": {\"probabilidad\": 56.0, \"detalles\": {\"atencion_central\": {\"valor\": 100.0, \"rango_esperado\": [50, 75], \"match\": 66.7}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [35, 70], \"match\": 0}, \"precision_seguimiento\": {\"valor\": 100.0, \"rango_esperado\": [50, 70], \"match\": 57.1}, \"reaccion_promedio\": {\"valor\": 0.5, \"rango_esperado\": [0.2, 0.5], \"match\": 100}}, \"severidad\": \"Moderada\"}, \"combinado\": {\"probabilidad\": 41.7, \"detalles\": {\"atencion_central\": {\"valor\": 100.0, \"rango_esperado\": [30, 60], \"match\": 33.3}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [30, 60], \"match\": 0}, \"precision_seguimiento\": {\"valor\": 100.0, \"rango_esperado\": [35, 60], \"match\": 33.3}, \"reaccion_promedio\": {\"valor\": 0.5, \"rango_esperado\": [0.5, 1.2], \"match\": 100}}, \"severidad\": \"Moderada\"}}, \"metricas\": {\"frames_procesados\": 297, \"dispersion_promedio\": 1.53, \"atencion_central\": 100.0, \"precision_seguimiento\": 100.0, \"reaccion_promedio\": 0.5, \"puntos_completados\": 1, \"aciertos_totales\": 288, \"observaciones_totales\": 288}, \"duracion\": 30, \"interpretacion\": \"Los patrones observados están dentro del rango típico. Precisión de seguimiento: 100.0%.\"}'),
(18, 7, NULL, NULL, 'vision_test', '{\"tipo_tdah\": \"typical\", \"confianza\": 72, \"scores_detallados\": {\"typical\": {\"probabilidad\": 72.5, \"detalles\": {\"atencion_central\": {\"valor\": 99.66, \"rango_esperado\": [75, 95], \"match\": 95.1}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [10, 25], \"match\": 0}, \"precision_seguimiento\": {\"valor\": 99.66, \"rango_esperado\": [70, 95], \"match\": 95.1}, \"reaccion_promedio\": {\"valor\": 0.5, \"rango_esperado\": [0.3, 0.8], \"match\": 100}}, \"severidad\": \"Moderada-Alta\"}, \"inatento\": {\"probabilidad\": 41.7, \"detalles\": {\"atencion_central\": {\"valor\": 99.66, \"rango_esperado\": [40, 70], \"match\": 57.6}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [15, 35], \"match\": 0}, \"precision_seguimiento\": {\"valor\": 99.66, \"rango_esperado\": [40, 65], \"match\": 46.7}, \"reaccion_promedio\": {\"valor\": 0.5, \"rango_esperado\": [0.8, 1.5], \"match\": 62.5}}, \"severidad\": \"Moderada\"}, \"hiperactivo\": {\"probabilidad\": 56.2, \"detalles\": {\"atencion_central\": {\"valor\": 99.66, \"rango_esperado\": [50, 75], \"match\": 67.1}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [35, 70], \"match\": 0}, \"precision_seguimiento\": {\"valor\": 99.66, \"rango_esperado\": [50, 70], \"match\": 57.6}, \"reaccion_promedio\": {\"valor\": 0.5, \"rango_esperado\": [0.2, 0.5], \"match\": 100}}, \"severidad\": \"Moderada\"}, \"combinado\": {\"probabilidad\": 42.0, \"detalles\": {\"atencion_central\": {\"valor\": 99.66, \"rango_esperado\": [30, 60], \"match\": 33.9}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [30, 60], \"match\": 0}, \"precision_seguimiento\": {\"valor\": 99.66, \"rango_esperado\": [35, 60], \"match\": 33.9}, \"reaccion_promedio\": {\"valor\": 0.5, \"rango_esperado\": [0.5, 1.2], \"match\": 100}}, \"severidad\": \"Moderada\"}}, \"metricas\": {\"frames_procesados\": 300, \"dispersion_promedio\": 1.5, \"atencion_central\": 99.66, \"precision_seguimiento\": 99.66, \"reaccion_promedio\": 0.5, \"puntos_completados\": 1, \"aciertos_totales\": 295, \"observaciones_totales\": 296}, \"duracion\": 30, \"interpretacion\": \"Los patrones observados están dentro del rango típico. Precisión de seguimiento: 99.7%.\"}', 'Tipo: typical (72%). Los patrones observados están dentro del rango típico. Precisión de seguimiento: 99.7%.', 0, NULL, '2025-12-08 20:08:47', 'vision', 'sin_determinar', 72, '{\"tipo_tdah\": \"typical\", \"confianza\": 72, \"scores_detallados\": {\"typical\": {\"probabilidad\": 72.5, \"detalles\": {\"atencion_central\": {\"valor\": 99.66, \"rango_esperado\": [75, 95], \"match\": 95.1}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [10, 25], \"match\": 0}, \"precision_seguimiento\": {\"valor\": 99.66, \"rango_esperado\": [70, 95], \"match\": 95.1}, \"reaccion_promedio\": {\"valor\": 0.5, \"rango_esperado\": [0.3, 0.8], \"match\": 100}}, \"severidad\": \"Moderada-Alta\"}, \"inatento\": {\"probabilidad\": 41.7, \"detalles\": {\"atencion_central\": {\"valor\": 99.66, \"rango_esperado\": [40, 70], \"match\": 57.6}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [15, 35], \"match\": 0}, \"precision_seguimiento\": {\"valor\": 99.66, \"rango_esperado\": [40, 65], \"match\": 46.7}, \"reaccion_promedio\": {\"valor\": 0.5, \"rango_esperado\": [0.8, 1.5], \"match\": 62.5}}, \"severidad\": \"Moderada\"}, \"hiperactivo\": {\"probabilidad\": 56.2, \"detalles\": {\"atencion_central\": {\"valor\": 99.66, \"rango_esperado\": [50, 75], \"match\": 67.1}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [35, 70], \"match\": 0}, \"precision_seguimiento\": {\"valor\": 99.66, \"rango_esperado\": [50, 70], \"match\": 57.6}, \"reaccion_promedio\": {\"valor\": 0.5, \"rango_esperado\": [0.2, 0.5], \"match\": 100}}, \"severidad\": \"Moderada\"}, \"combinado\": {\"probabilidad\": 42.0, \"detalles\": {\"atencion_central\": {\"valor\": 99.66, \"rango_esperado\": [30, 60], \"match\": 33.9}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [30, 60], \"match\": 0}, \"precision_seguimiento\": {\"valor\": 99.66, \"rango_esperado\": [35, 60], \"match\": 33.9}, \"reaccion_promedio\": {\"valor\": 0.5, \"rango_esperado\": [0.5, 1.2], \"match\": 100}}, \"severidad\": \"Moderada\"}}, \"metricas\": {\"frames_procesados\": 300, \"dispersion_promedio\": 1.5, \"atencion_central\": 99.66, \"precision_seguimiento\": 99.66, \"reaccion_promedio\": 0.5, \"puntos_completados\": 1, \"aciertos_totales\": 295, \"observaciones_totales\": 296}, \"duracion\": 30, \"interpretacion\": \"Los patrones observados están dentro del rango típico. Precisión de seguimiento: 99.7%.\"}');
INSERT INTO `reports` (`id`, `student_id`, `teacher_id`, `session_id`, `report_type`, `content`, `recommendations`, `sent_to_parents`, `parent_email`, `created_at`, `test_type`, `tipo_tdah`, `confianza`, `result_data`) VALUES
(19, 7, NULL, NULL, 'vision_test', '{\"tipo_tdah\": \"typical\", \"confianza\": 72, \"scores_detallados\": {\"typical\": {\"probabilidad\": 72.5, \"detalles\": {\"atencion_central\": {\"valor\": 99.66, \"rango_esperado\": [75, 95], \"match\": 95.1}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [10, 25], \"match\": 0}, \"precision_seguimiento\": {\"valor\": 99.66, \"rango_esperado\": [70, 95], \"match\": 95.1}, \"reaccion_promedio\": {\"valor\": 0.5, \"rango_esperado\": [0.3, 0.8], \"match\": 100}}, \"severidad\": \"Moderada-Alta\"}, \"inatento\": {\"probabilidad\": 41.7, \"detalles\": {\"atencion_central\": {\"valor\": 99.66, \"rango_esperado\": [40, 70], \"match\": 57.6}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [15, 35], \"match\": 0}, \"precision_seguimiento\": {\"valor\": 99.66, \"rango_esperado\": [40, 65], \"match\": 46.7}, \"reaccion_promedio\": {\"valor\": 0.5, \"rango_esperado\": [0.8, 1.5], \"match\": 62.5}}, \"severidad\": \"Moderada\"}, \"hiperactivo\": {\"probabilidad\": 56.2, \"detalles\": {\"atencion_central\": {\"valor\": 99.66, \"rango_esperado\": [50, 75], \"match\": 67.1}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [35, 70], \"match\": 0}, \"precision_seguimiento\": {\"valor\": 99.66, \"rango_esperado\": [50, 70], \"match\": 57.6}, \"reaccion_promedio\": {\"valor\": 0.5, \"rango_esperado\": [0.2, 0.5], \"match\": 100}}, \"severidad\": \"Moderada\"}, \"combinado\": {\"probabilidad\": 42.0, \"detalles\": {\"atencion_central\": {\"valor\": 99.66, \"rango_esperado\": [30, 60], \"match\": 33.9}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [30, 60], \"match\": 0}, \"precision_seguimiento\": {\"valor\": 99.66, \"rango_esperado\": [35, 60], \"match\": 33.9}, \"reaccion_promedio\": {\"valor\": 0.5, \"rango_esperado\": [0.5, 1.2], \"match\": 100}}, \"severidad\": \"Moderada\"}}, \"metricas\": {\"frames_procesados\": 301, \"dispersion_promedio\": 1.5, \"atencion_central\": 99.66, \"precision_seguimiento\": 99.66, \"reaccion_promedio\": 0.5, \"puntos_completados\": 1, \"aciertos_totales\": 296, \"observaciones_totales\": 297}, \"duracion\": 30, \"interpretacion\": \"Los patrones observados están dentro del rango típico. Precisión de seguimiento: 99.7%.\"}', 'Tipo: typical (72%). Los patrones observados están dentro del rango típico. Precisión de seguimiento: 99.7%.', 0, NULL, '2025-12-08 20:08:47', 'vision', 'sin_determinar', 72, '{\"tipo_tdah\": \"typical\", \"confianza\": 72, \"scores_detallados\": {\"typical\": {\"probabilidad\": 72.5, \"detalles\": {\"atencion_central\": {\"valor\": 99.66, \"rango_esperado\": [75, 95], \"match\": 95.1}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [10, 25], \"match\": 0}, \"precision_seguimiento\": {\"valor\": 99.66, \"rango_esperado\": [70, 95], \"match\": 95.1}, \"reaccion_promedio\": {\"valor\": 0.5, \"rango_esperado\": [0.3, 0.8], \"match\": 100}}, \"severidad\": \"Moderada-Alta\"}, \"inatento\": {\"probabilidad\": 41.7, \"detalles\": {\"atencion_central\": {\"valor\": 99.66, \"rango_esperado\": [40, 70], \"match\": 57.6}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [15, 35], \"match\": 0}, \"precision_seguimiento\": {\"valor\": 99.66, \"rango_esperado\": [40, 65], \"match\": 46.7}, \"reaccion_promedio\": {\"valor\": 0.5, \"rango_esperado\": [0.8, 1.5], \"match\": 62.5}}, \"severidad\": \"Moderada\"}, \"hiperactivo\": {\"probabilidad\": 56.2, \"detalles\": {\"atencion_central\": {\"valor\": 99.66, \"rango_esperado\": [50, 75], \"match\": 67.1}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [35, 70], \"match\": 0}, \"precision_seguimiento\": {\"valor\": 99.66, \"rango_esperado\": [50, 70], \"match\": 57.6}, \"reaccion_promedio\": {\"valor\": 0.5, \"rango_esperado\": [0.2, 0.5], \"match\": 100}}, \"severidad\": \"Moderada\"}, \"combinado\": {\"probabilidad\": 42.0, \"detalles\": {\"atencion_central\": {\"valor\": 99.66, \"rango_esperado\": [30, 60], \"match\": 33.9}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [30, 60], \"match\": 0}, \"precision_seguimiento\": {\"valor\": 99.66, \"rango_esperado\": [35, 60], \"match\": 33.9}, \"reaccion_promedio\": {\"valor\": 0.5, \"rango_esperado\": [0.5, 1.2], \"match\": 100}}, \"severidad\": \"Moderada\"}}, \"metricas\": {\"frames_procesados\": 301, \"dispersion_promedio\": 1.5, \"atencion_central\": 99.66, \"precision_seguimiento\": 99.66, \"reaccion_promedio\": 0.5, \"puntos_completados\": 1, \"aciertos_totales\": 296, \"observaciones_totales\": 297}, \"duracion\": 30, \"interpretacion\": \"Los patrones observados están dentro del rango típico. Precisión de seguimiento: 99.7%.\"}'),
(20, 7, NULL, NULL, 'vision_test', '{\"tipo_tdah\": \"typical\", \"confianza\": 73, \"scores_detallados\": {\"typical\": {\"probabilidad\": 73.4, \"detalles\": {\"atencion_central\": {\"valor\": 98.11, \"rango_esperado\": [75, 95], \"match\": 96.7}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [10, 25], \"match\": 0}, \"precision_seguimiento\": {\"valor\": 98.11, \"rango_esperado\": [70, 95], \"match\": 96.7}, \"reaccion_promedio\": {\"valor\": 0.5, \"rango_esperado\": [0.3, 0.8], \"match\": 100}}, \"severidad\": \"Moderada-Alta\"}, \"inatento\": {\"probabilidad\": 42.9, \"detalles\": {\"atencion_central\": {\"valor\": 98.11, \"rango_esperado\": [40, 70], \"match\": 59.8}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [15, 35], \"match\": 0}, \"precision_seguimiento\": {\"valor\": 98.11, \"rango_esperado\": [40, 65], \"match\": 49.1}, \"reaccion_promedio\": {\"valor\": 0.5, \"rango_esperado\": [0.8, 1.5], \"match\": 62.5}}, \"severidad\": \"Moderada\"}, \"hiperactivo\": {\"probabilidad\": 57.3, \"detalles\": {\"atencion_central\": {\"valor\": 98.11, \"rango_esperado\": [50, 75], \"match\": 69.2}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [35, 70], \"match\": 0}, \"precision_seguimiento\": {\"valor\": 98.11, \"rango_esperado\": [50, 70], \"match\": 59.8}, \"reaccion_promedio\": {\"valor\": 0.5, \"rango_esperado\": [0.2, 0.5], \"match\": 100}}, \"severidad\": \"Moderada\"}, \"combinado\": {\"probabilidad\": 43.2, \"detalles\": {\"atencion_central\": {\"valor\": 98.11, \"rango_esperado\": [30, 60], \"match\": 36.5}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [30, 60], \"match\": 0}, \"precision_seguimiento\": {\"valor\": 98.11, \"rango_esperado\": [35, 60], \"match\": 36.5}, \"reaccion_promedio\": {\"valor\": 0.5, \"rango_esperado\": [0.5, 1.2], \"match\": 100}}, \"severidad\": \"Moderada\"}}, \"metricas\": {\"frames_procesados\": 269, \"dispersion_promedio\": 7.79, \"atencion_central\": 98.11, \"precision_seguimiento\": 98.11, \"reaccion_promedio\": 0.5, \"puntos_completados\": 1, \"aciertos_totales\": 208, \"observaciones_totales\": 212}, \"duracion\": 30, \"interpretacion\": \"Los patrones observados están dentro del rango típico. Precisión de seguimiento: 98.1%.\"}', 'Tipo: typical (73%). Los patrones observados están dentro del rango típico. Precisión de seguimiento: 98.1%.', 0, NULL, '2025-12-08 20:09:29', 'vision', 'sin_determinar', 73, '{\"tipo_tdah\": \"typical\", \"confianza\": 73, \"scores_detallados\": {\"typical\": {\"probabilidad\": 73.4, \"detalles\": {\"atencion_central\": {\"valor\": 98.11, \"rango_esperado\": [75, 95], \"match\": 96.7}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [10, 25], \"match\": 0}, \"precision_seguimiento\": {\"valor\": 98.11, \"rango_esperado\": [70, 95], \"match\": 96.7}, \"reaccion_promedio\": {\"valor\": 0.5, \"rango_esperado\": [0.3, 0.8], \"match\": 100}}, \"severidad\": \"Moderada-Alta\"}, \"inatento\": {\"probabilidad\": 42.9, \"detalles\": {\"atencion_central\": {\"valor\": 98.11, \"rango_esperado\": [40, 70], \"match\": 59.8}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [15, 35], \"match\": 0}, \"precision_seguimiento\": {\"valor\": 98.11, \"rango_esperado\": [40, 65], \"match\": 49.1}, \"reaccion_promedio\": {\"valor\": 0.5, \"rango_esperado\": [0.8, 1.5], \"match\": 62.5}}, \"severidad\": \"Moderada\"}, \"hiperactivo\": {\"probabilidad\": 57.3, \"detalles\": {\"atencion_central\": {\"valor\": 98.11, \"rango_esperado\": [50, 75], \"match\": 69.2}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [35, 70], \"match\": 0}, \"precision_seguimiento\": {\"valor\": 98.11, \"rango_esperado\": [50, 70], \"match\": 59.8}, \"reaccion_promedio\": {\"valor\": 0.5, \"rango_esperado\": [0.2, 0.5], \"match\": 100}}, \"severidad\": \"Moderada\"}, \"combinado\": {\"probabilidad\": 43.2, \"detalles\": {\"atencion_central\": {\"valor\": 98.11, \"rango_esperado\": [30, 60], \"match\": 36.5}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [30, 60], \"match\": 0}, \"precision_seguimiento\": {\"valor\": 98.11, \"rango_esperado\": [35, 60], \"match\": 36.5}, \"reaccion_promedio\": {\"valor\": 0.5, \"rango_esperado\": [0.5, 1.2], \"match\": 100}}, \"severidad\": \"Moderada\"}}, \"metricas\": {\"frames_procesados\": 269, \"dispersion_promedio\": 7.79, \"atencion_central\": 98.11, \"precision_seguimiento\": 98.11, \"reaccion_promedio\": 0.5, \"puntos_completados\": 1, \"aciertos_totales\": 208, \"observaciones_totales\": 212}, \"duracion\": 30, \"interpretacion\": \"Los patrones observados están dentro del rango típico. Precisión de seguimiento: 98.1%.\"}'),
(21, 7, NULL, NULL, 'vision_test', '{\"tipo_tdah\": \"typical\", \"confianza\": 72, \"scores_detallados\": {\"typical\": {\"probabilidad\": 72.4, \"detalles\": {\"atencion_central\": {\"valor\": 100.0, \"rango_esperado\": [75, 95], \"match\": 94.7}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [10, 25], \"match\": 0}, \"precision_seguimiento\": {\"valor\": 100.0, \"rango_esperado\": [70, 95], \"match\": 94.7}, \"reaccion_promedio\": {\"valor\": 0.5, \"rango_esperado\": [0.3, 0.8], \"match\": 100}}, \"severidad\": \"Moderada-Alta\"}, \"inatento\": {\"probabilidad\": 41.4, \"detalles\": {\"atencion_central\": {\"valor\": 100.0, \"rango_esperado\": [40, 70], \"match\": 57.1}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [15, 35], \"match\": 0}, \"precision_seguimiento\": {\"valor\": 100.0, \"rango_esperado\": [40, 65], \"match\": 46.2}, \"reaccion_promedio\": {\"valor\": 0.5, \"rango_esperado\": [0.8, 1.5], \"match\": 62.5}}, \"severidad\": \"Moderada\"}, \"hiperactivo\": {\"probabilidad\": 56.0, \"detalles\": {\"atencion_central\": {\"valor\": 100.0, \"rango_esperado\": [50, 75], \"match\": 66.7}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [35, 70], \"match\": 0}, \"precision_seguimiento\": {\"valor\": 100.0, \"rango_esperado\": [50, 70], \"match\": 57.1}, \"reaccion_promedio\": {\"valor\": 0.5, \"rango_esperado\": [0.2, 0.5], \"match\": 100}}, \"severidad\": \"Moderada\"}, \"combinado\": {\"probabilidad\": 41.7, \"detalles\": {\"atencion_central\": {\"valor\": 100.0, \"rango_esperado\": [30, 60], \"match\": 33.3}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [30, 60], \"match\": 0}, \"precision_seguimiento\": {\"valor\": 100.0, \"rango_esperado\": [35, 60], \"match\": 33.3}, \"reaccion_promedio\": {\"valor\": 0.5, \"rango_esperado\": [0.5, 1.2], \"match\": 100}}, \"severidad\": \"Moderada\"}}, \"metricas\": {\"frames_procesados\": 300, \"dispersion_promedio\": 1.14, \"atencion_central\": 100.0, \"precision_seguimiento\": 100.0, \"reaccion_promedio\": 0.5, \"puntos_completados\": 1, \"aciertos_totales\": 297, \"observaciones_totales\": 297}, \"duracion\": 30, \"interpretacion\": \"Los patrones observados están dentro del rango típico. Precisión de seguimiento: 100.0%.\"}', 'Tipo: typical (72%). Los patrones observados están dentro del rango típico. Precisión de seguimiento: 100.0%.', 0, NULL, '2025-12-08 20:11:32', 'vision', 'sin_determinar', 72, '{\"tipo_tdah\": \"typical\", \"confianza\": 72, \"scores_detallados\": {\"typical\": {\"probabilidad\": 72.4, \"detalles\": {\"atencion_central\": {\"valor\": 100.0, \"rango_esperado\": [75, 95], \"match\": 94.7}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [10, 25], \"match\": 0}, \"precision_seguimiento\": {\"valor\": 100.0, \"rango_esperado\": [70, 95], \"match\": 94.7}, \"reaccion_promedio\": {\"valor\": 0.5, \"rango_esperado\": [0.3, 0.8], \"match\": 100}}, \"severidad\": \"Moderada-Alta\"}, \"inatento\": {\"probabilidad\": 41.4, \"detalles\": {\"atencion_central\": {\"valor\": 100.0, \"rango_esperado\": [40, 70], \"match\": 57.1}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [15, 35], \"match\": 0}, \"precision_seguimiento\": {\"valor\": 100.0, \"rango_esperado\": [40, 65], \"match\": 46.2}, \"reaccion_promedio\": {\"valor\": 0.5, \"rango_esperado\": [0.8, 1.5], \"match\": 62.5}}, \"severidad\": \"Moderada\"}, \"hiperactivo\": {\"probabilidad\": 56.0, \"detalles\": {\"atencion_central\": {\"valor\": 100.0, \"rango_esperado\": [50, 75], \"match\": 66.7}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [35, 70], \"match\": 0}, \"precision_seguimiento\": {\"valor\": 100.0, \"rango_esperado\": [50, 70], \"match\": 57.1}, \"reaccion_promedio\": {\"valor\": 0.5, \"rango_esperado\": [0.2, 0.5], \"match\": 100}}, \"severidad\": \"Moderada\"}, \"combinado\": {\"probabilidad\": 41.7, \"detalles\": {\"atencion_central\": {\"valor\": 100.0, \"rango_esperado\": [30, 60], \"match\": 33.3}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [30, 60], \"match\": 0}, \"precision_seguimiento\": {\"valor\": 100.0, \"rango_esperado\": [35, 60], \"match\": 33.3}, \"reaccion_promedio\": {\"valor\": 0.5, \"rango_esperado\": [0.5, 1.2], \"match\": 100}}, \"severidad\": \"Moderada\"}}, \"metricas\": {\"frames_procesados\": 300, \"dispersion_promedio\": 1.14, \"atencion_central\": 100.0, \"precision_seguimiento\": 100.0, \"reaccion_promedio\": 0.5, \"puntos_completados\": 1, \"aciertos_totales\": 297, \"observaciones_totales\": 297}, \"duracion\": 30, \"interpretacion\": \"Los patrones observados están dentro del rango típico. Precisión de seguimiento: 100.0%.\"}'),
(22, 7, NULL, NULL, 'vision_test', '{\"tipo_tdah\": \"typical\", \"confianza\": 72, \"scores_detallados\": {\"typical\": {\"probabilidad\": 72.4, \"detalles\": {\"atencion_central\": {\"valor\": 100.0, \"rango_esperado\": [75, 95], \"match\": 94.7}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [10, 25], \"match\": 0}, \"precision_seguimiento\": {\"valor\": 100.0, \"rango_esperado\": [70, 95], \"match\": 94.7}, \"reaccion_promedio\": {\"valor\": 0.5, \"rango_esperado\": [0.3, 0.8], \"match\": 100}}, \"severidad\": \"Moderada-Alta\"}, \"inatento\": {\"probabilidad\": 41.4, \"detalles\": {\"atencion_central\": {\"valor\": 100.0, \"rango_esperado\": [40, 70], \"match\": 57.1}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [15, 35], \"match\": 0}, \"precision_seguimiento\": {\"valor\": 100.0, \"rango_esperado\": [40, 65], \"match\": 46.2}, \"reaccion_promedio\": {\"valor\": 0.5, \"rango_esperado\": [0.8, 1.5], \"match\": 62.5}}, \"severidad\": \"Moderada\"}, \"hiperactivo\": {\"probabilidad\": 56.0, \"detalles\": {\"atencion_central\": {\"valor\": 100.0, \"rango_esperado\": [50, 75], \"match\": 66.7}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [35, 70], \"match\": 0}, \"precision_seguimiento\": {\"valor\": 100.0, \"rango_esperado\": [50, 70], \"match\": 57.1}, \"reaccion_promedio\": {\"valor\": 0.5, \"rango_esperado\": [0.2, 0.5], \"match\": 100}}, \"severidad\": \"Moderada\"}, \"combinado\": {\"probabilidad\": 41.7, \"detalles\": {\"atencion_central\": {\"valor\": 100.0, \"rango_esperado\": [30, 60], \"match\": 33.3}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [30, 60], \"match\": 0}, \"precision_seguimiento\": {\"valor\": 100.0, \"rango_esperado\": [35, 60], \"match\": 33.3}, \"reaccion_promedio\": {\"valor\": 0.5, \"rango_esperado\": [0.5, 1.2], \"match\": 100}}, \"severidad\": \"Moderada\"}}, \"metricas\": {\"frames_procesados\": 301, \"dispersion_promedio\": 1.13, \"atencion_central\": 100.0, \"precision_seguimiento\": 100.0, \"reaccion_promedio\": 0.5, \"puntos_completados\": 1, \"aciertos_totales\": 298, \"observaciones_totales\": 298}, \"duracion\": 30, \"interpretacion\": \"Los patrones observados están dentro del rango típico. Precisión de seguimiento: 100.0%.\"}', 'Tipo: typical (72%). Los patrones observados están dentro del rango típico. Precisión de seguimiento: 100.0%.', 0, NULL, '2025-12-08 20:11:32', 'vision', 'sin_determinar', 72, '{\"tipo_tdah\": \"typical\", \"confianza\": 72, \"scores_detallados\": {\"typical\": {\"probabilidad\": 72.4, \"detalles\": {\"atencion_central\": {\"valor\": 100.0, \"rango_esperado\": [75, 95], \"match\": 94.7}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [10, 25], \"match\": 0}, \"precision_seguimiento\": {\"valor\": 100.0, \"rango_esperado\": [70, 95], \"match\": 94.7}, \"reaccion_promedio\": {\"valor\": 0.5, \"rango_esperado\": [0.3, 0.8], \"match\": 100}}, \"severidad\": \"Moderada-Alta\"}, \"inatento\": {\"probabilidad\": 41.4, \"detalles\": {\"atencion_central\": {\"valor\": 100.0, \"rango_esperado\": [40, 70], \"match\": 57.1}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [15, 35], \"match\": 0}, \"precision_seguimiento\": {\"valor\": 100.0, \"rango_esperado\": [40, 65], \"match\": 46.2}, \"reaccion_promedio\": {\"valor\": 0.5, \"rango_esperado\": [0.8, 1.5], \"match\": 62.5}}, \"severidad\": \"Moderada\"}, \"hiperactivo\": {\"probabilidad\": 56.0, \"detalles\": {\"atencion_central\": {\"valor\": 100.0, \"rango_esperado\": [50, 75], \"match\": 66.7}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [35, 70], \"match\": 0}, \"precision_seguimiento\": {\"valor\": 100.0, \"rango_esperado\": [50, 70], \"match\": 57.1}, \"reaccion_promedio\": {\"valor\": 0.5, \"rango_esperado\": [0.2, 0.5], \"match\": 100}}, \"severidad\": \"Moderada\"}, \"combinado\": {\"probabilidad\": 41.7, \"detalles\": {\"atencion_central\": {\"valor\": 100.0, \"rango_esperado\": [30, 60], \"match\": 33.3}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [30, 60], \"match\": 0}, \"precision_seguimiento\": {\"valor\": 100.0, \"rango_esperado\": [35, 60], \"match\": 33.3}, \"reaccion_promedio\": {\"valor\": 0.5, \"rango_esperado\": [0.5, 1.2], \"match\": 100}}, \"severidad\": \"Moderada\"}}, \"metricas\": {\"frames_procesados\": 301, \"dispersion_promedio\": 1.13, \"atencion_central\": 100.0, \"precision_seguimiento\": 100.0, \"reaccion_promedio\": 0.5, \"puntos_completados\": 1, \"aciertos_totales\": 298, \"observaciones_totales\": 298}, \"duracion\": 30, \"interpretacion\": \"Los patrones observados están dentro del rango típico. Precisión de seguimiento: 100.0%.\"}'),
(23, 7, NULL, NULL, 'vision_test', '{\"tipo_tdah\": \"combinado\", \"confianza\": 65, \"scores_detallados\": {\"typical\": {\"probabilidad\": 43.1, \"detalles\": {\"atencion_central\": {\"valor\": 26.28, \"rango_esperado\": [75, 95], \"match\": 35.0}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [10, 25], \"match\": 0}, \"precision_seguimiento\": {\"valor\": 26.28, \"rango_esperado\": [70, 95], \"match\": 37.5}, \"reaccion_promedio\": {\"valor\": 0.5, \"rango_esperado\": [0.3, 0.8], \"match\": 100}}, \"severidad\": \"Moderada\"}, \"inatento\": {\"probabilidad\": 48.5, \"detalles\": {\"atencion_central\": {\"valor\": 26.28, \"rango_esperado\": [40, 70], \"match\": 65.7}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [15, 35], \"match\": 0}, \"precision_seguimiento\": {\"valor\": 26.28, \"rango_esperado\": [40, 65], \"match\": 65.7}, \"reaccion_promedio\": {\"valor\": 0.5, \"rango_esperado\": [0.8, 1.5], \"match\": 62.5}}, \"severidad\": \"Moderada\"}, \"hiperactivo\": {\"probabilidad\": 51.3, \"detalles\": {\"atencion_central\": {\"valor\": 26.28, \"rango_esperado\": [50, 75], \"match\": 52.6}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [35, 70], \"match\": 0}, \"precision_seguimiento\": {\"valor\": 26.28, \"rango_esperado\": [50, 70], \"match\": 52.6}, \"reaccion_promedio\": {\"valor\": 0.5, \"rango_esperado\": [0.2, 0.5], \"match\": 100}}, \"severidad\": \"Moderada\"}, \"combinado\": {\"probabilidad\": 65.7, \"detalles\": {\"atencion_central\": {\"valor\": 26.28, \"rango_esperado\": [30, 60], \"match\": 87.6}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [30, 60], \"match\": 0}, \"precision_seguimiento\": {\"valor\": 26.28, \"rango_esperado\": [35, 60], \"match\": 75.1}, \"reaccion_promedio\": {\"valor\": 0.5, \"rango_esperado\": [0.5, 1.2], \"match\": 100}}, \"severidad\": \"Moderada-Alta\"}}, \"metricas\": {\"frames_procesados\": 300, \"dispersion_promedio\": 4.08, \"atencion_central\": 26.28, \"precision_seguimiento\": 26.28, \"reaccion_promedio\": 0.5, \"puntos_completados\": 1, \"aciertos_totales\": 77, \"observaciones_totales\": 293}, \"duracion\": 30, \"interpretacion\": \"Características mixtas. Precisión: 26.3%, Dispersión: 4.08.\"}', 'Tipo: combinado (65%). Características mixtas. Precisión: 26.3%, Dispersión: 4.08.', 0, NULL, '2025-12-08 20:12:36', 'vision', 'sin_determinar', 65, '{\"tipo_tdah\": \"combinado\", \"confianza\": 65, \"scores_detallados\": {\"typical\": {\"probabilidad\": 43.1, \"detalles\": {\"atencion_central\": {\"valor\": 26.28, \"rango_esperado\": [75, 95], \"match\": 35.0}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [10, 25], \"match\": 0}, \"precision_seguimiento\": {\"valor\": 26.28, \"rango_esperado\": [70, 95], \"match\": 37.5}, \"reaccion_promedio\": {\"valor\": 0.5, \"rango_esperado\": [0.3, 0.8], \"match\": 100}}, \"severidad\": \"Moderada\"}, \"inatento\": {\"probabilidad\": 48.5, \"detalles\": {\"atencion_central\": {\"valor\": 26.28, \"rango_esperado\": [40, 70], \"match\": 65.7}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [15, 35], \"match\": 0}, \"precision_seguimiento\": {\"valor\": 26.28, \"rango_esperado\": [40, 65], \"match\": 65.7}, \"reaccion_promedio\": {\"valor\": 0.5, \"rango_esperado\": [0.8, 1.5], \"match\": 62.5}}, \"severidad\": \"Moderada\"}, \"hiperactivo\": {\"probabilidad\": 51.3, \"detalles\": {\"atencion_central\": {\"valor\": 26.28, \"rango_esperado\": [50, 75], \"match\": 52.6}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [35, 70], \"match\": 0}, \"precision_seguimiento\": {\"valor\": 26.28, \"rango_esperado\": [50, 70], \"match\": 52.6}, \"reaccion_promedio\": {\"valor\": 0.5, \"rango_esperado\": [0.2, 0.5], \"match\": 100}}, \"severidad\": \"Moderada\"}, \"combinado\": {\"probabilidad\": 65.7, \"detalles\": {\"atencion_central\": {\"valor\": 26.28, \"rango_esperado\": [30, 60], \"match\": 87.6}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [30, 60], \"match\": 0}, \"precision_seguimiento\": {\"valor\": 26.28, \"rango_esperado\": [35, 60], \"match\": 75.1}, \"reaccion_promedio\": {\"valor\": 0.5, \"rango_esperado\": [0.5, 1.2], \"match\": 100}}, \"severidad\": \"Moderada-Alta\"}}, \"metricas\": {\"frames_procesados\": 300, \"dispersion_promedio\": 4.08, \"atencion_central\": 26.28, \"precision_seguimiento\": 26.28, \"reaccion_promedio\": 0.5, \"puntos_completados\": 1, \"aciertos_totales\": 77, \"observaciones_totales\": 293}, \"duracion\": 30, \"interpretacion\": \"Características mixtas. Precisión: 26.3%, Dispersión: 4.08.\"}'),
(24, 7, NULL, NULL, 'vision_test', '{\"tipo_tdah\": \"combinado\", \"confianza\": 66, \"scores_detallados\": {\"typical\": {\"probabilidad\": 43.3, \"detalles\": {\"atencion_central\": {\"valor\": 26.53, \"rango_esperado\": [75, 95], \"match\": 35.4}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [10, 25], \"match\": 0}, \"precision_seguimiento\": {\"valor\": 26.53, \"rango_esperado\": [70, 95], \"match\": 37.9}, \"reaccion_promedio\": {\"valor\": 0.5, \"rango_esperado\": [0.3, 0.8], \"match\": 100}}, \"severidad\": \"Moderada\"}, \"inatento\": {\"probabilidad\": 48.8, \"detalles\": {\"atencion_central\": {\"valor\": 26.53, \"rango_esperado\": [40, 70], \"match\": 66.3}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [15, 35], \"match\": 0}, \"precision_seguimiento\": {\"valor\": 26.53, \"rango_esperado\": [40, 65], \"match\": 66.3}, \"reaccion_promedio\": {\"valor\": 0.5, \"rango_esperado\": [0.8, 1.5], \"match\": 62.5}}, \"severidad\": \"Moderada\"}, \"hiperactivo\": {\"probabilidad\": 51.5, \"detalles\": {\"atencion_central\": {\"valor\": 26.53, \"rango_esperado\": [50, 75], \"match\": 53.1}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [35, 70], \"match\": 0}, \"precision_seguimiento\": {\"valor\": 26.53, \"rango_esperado\": [50, 70], \"match\": 53.1}, \"reaccion_promedio\": {\"valor\": 0.5, \"rango_esperado\": [0.2, 0.5], \"match\": 100}}, \"severidad\": \"Moderada\"}, \"combinado\": {\"probabilidad\": 66.1, \"detalles\": {\"atencion_central\": {\"valor\": 26.53, \"rango_esperado\": [30, 60], \"match\": 88.4}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [30, 60], \"match\": 0}, \"precision_seguimiento\": {\"valor\": 26.53, \"rango_esperado\": [35, 60], \"match\": 75.8}, \"reaccion_promedio\": {\"valor\": 0.5, \"rango_esperado\": [0.5, 1.2], \"match\": 100}}, \"severidad\": \"Moderada-Alta\"}}, \"metricas\": {\"frames_procesados\": 301, \"dispersion_promedio\": 4.06, \"atencion_central\": 26.53, \"precision_seguimiento\": 26.53, \"reaccion_promedio\": 0.5, \"puntos_completados\": 1, \"aciertos_totales\": 78, \"observaciones_totales\": 294}, \"duracion\": 30, \"interpretacion\": \"Características mixtas. Precisión: 26.5%, Dispersión: 4.06.\"}', 'Tipo: combinado (66%). Características mixtas. Precisión: 26.5%, Dispersión: 4.06.', 0, NULL, '2025-12-08 20:12:36', 'vision', 'sin_determinar', 66, '{\"tipo_tdah\": \"combinado\", \"confianza\": 66, \"scores_detallados\": {\"typical\": {\"probabilidad\": 43.3, \"detalles\": {\"atencion_central\": {\"valor\": 26.53, \"rango_esperado\": [75, 95], \"match\": 35.4}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [10, 25], \"match\": 0}, \"precision_seguimiento\": {\"valor\": 26.53, \"rango_esperado\": [70, 95], \"match\": 37.9}, \"reaccion_promedio\": {\"valor\": 0.5, \"rango_esperado\": [0.3, 0.8], \"match\": 100}}, \"severidad\": \"Moderada\"}, \"inatento\": {\"probabilidad\": 48.8, \"detalles\": {\"atencion_central\": {\"valor\": 26.53, \"rango_esperado\": [40, 70], \"match\": 66.3}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [15, 35], \"match\": 0}, \"precision_seguimiento\": {\"valor\": 26.53, \"rango_esperado\": [40, 65], \"match\": 66.3}, \"reaccion_promedio\": {\"valor\": 0.5, \"rango_esperado\": [0.8, 1.5], \"match\": 62.5}}, \"severidad\": \"Moderada\"}, \"hiperactivo\": {\"probabilidad\": 51.5, \"detalles\": {\"atencion_central\": {\"valor\": 26.53, \"rango_esperado\": [50, 75], \"match\": 53.1}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [35, 70], \"match\": 0}, \"precision_seguimiento\": {\"valor\": 26.53, \"rango_esperado\": [50, 70], \"match\": 53.1}, \"reaccion_promedio\": {\"valor\": 0.5, \"rango_esperado\": [0.2, 0.5], \"match\": 100}}, \"severidad\": \"Moderada\"}, \"combinado\": {\"probabilidad\": 66.1, \"detalles\": {\"atencion_central\": {\"valor\": 26.53, \"rango_esperado\": [30, 60], \"match\": 88.4}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [30, 60], \"match\": 0}, \"precision_seguimiento\": {\"valor\": 26.53, \"rango_esperado\": [35, 60], \"match\": 75.8}, \"reaccion_promedio\": {\"valor\": 0.5, \"rango_esperado\": [0.5, 1.2], \"match\": 100}}, \"severidad\": \"Moderada-Alta\"}}, \"metricas\": {\"frames_procesados\": 301, \"dispersion_promedio\": 4.06, \"atencion_central\": 26.53, \"precision_seguimiento\": 26.53, \"reaccion_promedio\": 0.5, \"puntos_completados\": 1, \"aciertos_totales\": 78, \"observaciones_totales\": 294}, \"duracion\": 30, \"interpretacion\": \"Características mixtas. Precisión: 26.5%, Dispersión: 4.06.\"}'),
(25, 1, NULL, NULL, 'stroop_test', '{\"tipo_tdah\": \"combinado\", \"confianza\": 92, \"metricas\": {\"total_intentos\": 30, \"correctos\": 16, \"incorrectos\": 14, \"precision\": 53.333333333333336, \"tiempo_promedio\": 1319.875, \"errores_congruentes\": 1, \"errores_incongruentes\": 13, \"tiempo_congruente\": 1205.9285714285713, \"tiempo_incongruente\": 2117.5, \"efecto_stroop\": 911.5714285714287}, \"scores_detallados\": {\"typical\": {\"probabilidad\": 41.7, \"detalles\": {\"precision\": {\"valor\": 53.333333333333336, \"rango_esperado\": [80, 100], \"match\": 66.7}, \"tiempo_promedio\": {\"valor\": 1319.875, \"rango_esperado\": [800, 1500], \"match\": 100}, \"errores_incongruentes\": {\"valor\": 13, \"rango_esperado\": [0, 3], \"match\": 0}, \"efecto_stroop\": {\"valor\": 911.5714285714287, \"rango_esperado\": [100, 300], \"match\": 0}}, \"severidad\": \"Moderada\"}, \"inatento\": {\"probabilidad\": 76.5, \"detalles\": {\"precision\": {\"valor\": 53.333333333333336, \"rango_esperado\": [50, 75], \"match\": 100}, \"tiempo_promedio\": {\"valor\": 1319.875, \"rango_esperado\": [1500, 2500], \"match\": 88.0}, \"errores_incongruentes\": {\"valor\": 13, \"rango_esperado\": [4, 10], \"match\": 70.0}, \"efecto_stroop\": {\"valor\": 911.5714285714287, \"rango_esperado\": [300, 600], \"match\": 48.1}}, \"severidad\": \"Moderada-Alta\"}, \"hiperactivo\": {\"probabilidad\": 72.1, \"detalles\": {\"precision\": {\"valor\": 53.333333333333336, \"rango_esperado\": [60, 85], \"match\": 88.9}, \"tiempo_promedio\": {\"valor\": 1319.875, \"rango_esperado\": [600, 1200], \"match\": 90.0}, \"errores_incongruentes\": {\"valor\": 13, \"rango_esperado\": [5, 12], \"match\": 91.7}, \"efecto_stroop\": {\"valor\": 911.5714285714287, \"rango_esperado\": [200, 500], \"match\": 17.7}}, \"severidad\": \"Moderada-Alta\"}, \"combinado\": {\"probabilidad\": 92.4, \"detalles\": {\"precision\": {\"valor\": 53.333333333333336, \"rango_esperado\": [45, 70], \"match\": 100}, \"tiempo_promedio\": {\"valor\": 1319.875, \"rango_esperado\": [1200, 2200], \"match\": 100}, \"errores_incongruentes\": {\"valor\": 13, \"rango_esperado\": [6, 15], \"match\": 100}, \"efecto_stroop\": {\"valor\": 911.5714285714287, \"rango_esperado\": [350, 700], \"match\": 69.8}}, \"severidad\": \"Alta\"}}, \"duracion\": 58}', 'Tipo: combinado (92%)', 0, NULL, '2025-12-09 05:58:54', 'vision', 'sin_determinar', 92, '{\"tipo_tdah\": \"combinado\", \"confianza\": 92, \"metricas\": {\"total_intentos\": 30, \"correctos\": 16, \"incorrectos\": 14, \"precision\": 53.333333333333336, \"tiempo_promedio\": 1319.875, \"errores_congruentes\": 1, \"errores_incongruentes\": 13, \"tiempo_congruente\": 1205.9285714285713, \"tiempo_incongruente\": 2117.5, \"efecto_stroop\": 911.5714285714287}, \"scores_detallados\": {\"typical\": {\"probabilidad\": 41.7, \"detalles\": {\"precision\": {\"valor\": 53.333333333333336, \"rango_esperado\": [80, 100], \"match\": 66.7}, \"tiempo_promedio\": {\"valor\": 1319.875, \"rango_esperado\": [800, 1500], \"match\": 100}, \"errores_incongruentes\": {\"valor\": 13, \"rango_esperado\": [0, 3], \"match\": 0}, \"efecto_stroop\": {\"valor\": 911.5714285714287, \"rango_esperado\": [100, 300], \"match\": 0}}, \"severidad\": \"Moderada\"}, \"inatento\": {\"probabilidad\": 76.5, \"detalles\": {\"precision\": {\"valor\": 53.333333333333336, \"rango_esperado\": [50, 75], \"match\": 100}, \"tiempo_promedio\": {\"valor\": 1319.875, \"rango_esperado\": [1500, 2500], \"match\": 88.0}, \"errores_incongruentes\": {\"valor\": 13, \"rango_esperado\": [4, 10], \"match\": 70.0}, \"efecto_stroop\": {\"valor\": 911.5714285714287, \"rango_esperado\": [300, 600], \"match\": 48.1}}, \"severidad\": \"Moderada-Alta\"}, \"hiperactivo\": {\"probabilidad\": 72.1, \"detalles\": {\"precision\": {\"valor\": 53.333333333333336, \"rango_esperado\": [60, 85], \"match\": 88.9}, \"tiempo_promedio\": {\"valor\": 1319.875, \"rango_esperado\": [600, 1200], \"match\": 90.0}, \"errores_incongruentes\": {\"valor\": 13, \"rango_esperado\": [5, 12], \"match\": 91.7}, \"efecto_stroop\": {\"valor\": 911.5714285714287, \"rango_esperado\": [200, 500], \"match\": 17.7}}, \"severidad\": \"Moderada-Alta\"}, \"combinado\": {\"probabilidad\": 92.4, \"detalles\": {\"precision\": {\"valor\": 53.333333333333336, \"rango_esperado\": [45, 70], \"match\": 100}, \"tiempo_promedio\": {\"valor\": 1319.875, \"rango_esperado\": [1200, 2200], \"match\": 100}, \"errores_incongruentes\": {\"valor\": 13, \"rango_esperado\": [6, 15], \"match\": 100}, \"efecto_stroop\": {\"valor\": 911.5714285714287, \"rango_esperado\": [350, 700], \"match\": 69.8}}, \"severidad\": \"Alta\"}}, \"duracion\": 58}'),
(26, 1, NULL, NULL, 'gonogo_test', '{\"tipo_tdah\": \"inatento\", \"confianza\": 85, \"metricas\": {\"total_go\": 28, \"total_nogo\": 12, \"aciertos_go\": 7, \"aciertos_nogo\": 10, \"errores_omision\": 21, \"falsos_positivos\": 2, \"precision_go\": 25.0, \"precision_nogo\": 83.33333333333334, \"tiempo_reaccion_promedio\": 613.1428571428571, \"anticipaciones\": 0}, \"scores_detallados\": {\"typical\": {\"probabilidad\": 81.3, \"detalles\": {\"precision_go\": {\"valor\": 25.0, \"rango_esperado\": [85, 100], \"match\": 29.4}, \"precision_nogo\": {\"valor\": 83.33333333333334, \"rango_esperado\": [85, 100], \"match\": 98.0}, \"falsos_positivos\": {\"valor\": 2, \"rango_esperado\": [0, 3], \"match\": 100}, \"tiempo_reaccion_promedio\": {\"valor\": 613.1428571428571, \"rango_esperado\": [300, 600], \"match\": 97.8}}, \"severidad\": \"Alta\"}, \"inatento\": {\"probabilidad\": 85.4, \"detalles\": {\"precision_go\": {\"valor\": 25.0, \"rango_esperado\": [60, 80], \"match\": 41.7}, \"precision_nogo\": {\"valor\": 83.33333333333334, \"rango_esperado\": [70, 90], \"match\": 100}, \"falsos_positivos\": {\"valor\": 2, \"rango_esperado\": [2, 6], \"match\": 100}, \"tiempo_reaccion_promedio\": {\"valor\": 613.1428571428571, \"rango_esperado\": [500, 900], \"match\": 100}}, \"severidad\": \"Alta\"}, \"hiperactivo\": {\"probabilidad\": 46.5, \"detalles\": {\"precision_go\": {\"valor\": 25.0, \"rango_esperado\": [75, 95], \"match\": 33.3}, \"precision_nogo\": {\"valor\": 83.33333333333334, \"rango_esperado\": [40, 70], \"match\": 81.0}, \"falsos_positivos\": {\"valor\": 2, \"rango_esperado\": [8, 20], \"match\": 25.0}, \"tiempo_reaccion_promedio\": {\"valor\": 613.1428571428571, \"rango_esperado\": [200, 400], \"match\": 46.7}}, \"severidad\": \"Moderada\"}, \"combinado\": {\"probabilidad\": 68.6, \"detalles\": {\"precision_go\": {\"valor\": 25.0, \"rango_esperado\": [55, 75], \"match\": 45.5}, \"precision_nogo\": {\"valor\": 83.33333333333334, \"rango_esperado\": [50, 75], \"match\": 88.9}, \"falsos_positivos\": {\"valor\": 2, \"rango_esperado\": [5, 12], \"match\": 40.0}, \"tiempo_reaccion_promedio\": {\"valor\": 613.1428571428571, \"rango_esperado\": [400, 700], \"match\": 100}}, \"severidad\": \"Moderada-Alta\"}}, \"duracion\": 62}', 'Tipo: inatento (85%)', 0, NULL, '2025-12-09 06:00:16', 'vision', 'sin_determinar', 85, '{\"tipo_tdah\": \"inatento\", \"confianza\": 85, \"metricas\": {\"total_go\": 28, \"total_nogo\": 12, \"aciertos_go\": 7, \"aciertos_nogo\": 10, \"errores_omision\": 21, \"falsos_positivos\": 2, \"precision_go\": 25.0, \"precision_nogo\": 83.33333333333334, \"tiempo_reaccion_promedio\": 613.1428571428571, \"anticipaciones\": 0}, \"scores_detallados\": {\"typical\": {\"probabilidad\": 81.3, \"detalles\": {\"precision_go\": {\"valor\": 25.0, \"rango_esperado\": [85, 100], \"match\": 29.4}, \"precision_nogo\": {\"valor\": 83.33333333333334, \"rango_esperado\": [85, 100], \"match\": 98.0}, \"falsos_positivos\": {\"valor\": 2, \"rango_esperado\": [0, 3], \"match\": 100}, \"tiempo_reaccion_promedio\": {\"valor\": 613.1428571428571, \"rango_esperado\": [300, 600], \"match\": 97.8}}, \"severidad\": \"Alta\"}, \"inatento\": {\"probabilidad\": 85.4, \"detalles\": {\"precision_go\": {\"valor\": 25.0, \"rango_esperado\": [60, 80], \"match\": 41.7}, \"precision_nogo\": {\"valor\": 83.33333333333334, \"rango_esperado\": [70, 90], \"match\": 100}, \"falsos_positivos\": {\"valor\": 2, \"rango_esperado\": [2, 6], \"match\": 100}, \"tiempo_reaccion_promedio\": {\"valor\": 613.1428571428571, \"rango_esperado\": [500, 900], \"match\": 100}}, \"severidad\": \"Alta\"}, \"hiperactivo\": {\"probabilidad\": 46.5, \"detalles\": {\"precision_go\": {\"valor\": 25.0, \"rango_esperado\": [75, 95], \"match\": 33.3}, \"precision_nogo\": {\"valor\": 83.33333333333334, \"rango_esperado\": [40, 70], \"match\": 81.0}, \"falsos_positivos\": {\"valor\": 2, \"rango_esperado\": [8, 20], \"match\": 25.0}, \"tiempo_reaccion_promedio\": {\"valor\": 613.1428571428571, \"rango_esperado\": [200, 400], \"match\": 46.7}}, \"severidad\": \"Moderada\"}, \"combinado\": {\"probabilidad\": 68.6, \"detalles\": {\"precision_go\": {\"valor\": 25.0, \"rango_esperado\": [55, 75], \"match\": 45.5}, \"precision_nogo\": {\"valor\": 83.33333333333334, \"rango_esperado\": [50, 75], \"match\": 88.9}, \"falsos_positivos\": {\"valor\": 2, \"rango_esperado\": [5, 12], \"match\": 40.0}, \"tiempo_reaccion_promedio\": {\"valor\": 613.1428571428571, \"rango_esperado\": [400, 700], \"match\": 100}}, \"severidad\": \"Moderada-Alta\"}}, \"duracion\": 62}'),
(27, 1, NULL, NULL, 'vision_test', '{\"tipo_tdah\": \"typical\", \"confianza\": 72, \"scores_detallados\": {\"typical\": {\"probabilidad\": 72.4, \"detalles\": {\"atencion_central\": {\"valor\": 100.0, \"rango_esperado\": [75, 95], \"match\": 94.7}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [10, 25], \"match\": 0}, \"precision_seguimiento\": {\"valor\": 100.0, \"rango_esperado\": [70, 95], \"match\": 94.7}, \"reaccion_promedio\": {\"valor\": 0.5, \"rango_esperado\": [0.3, 0.8], \"match\": 100}}, \"severidad\": \"Moderada-Alta\"}, \"inatento\": {\"probabilidad\": 41.4, \"detalles\": {\"atencion_central\": {\"valor\": 100.0, \"rango_esperado\": [40, 70], \"match\": 57.1}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [15, 35], \"match\": 0}, \"precision_seguimiento\": {\"valor\": 100.0, \"rango_esperado\": [40, 65], \"match\": 46.2}, \"reaccion_promedio\": {\"valor\": 0.5, \"rango_esperado\": [0.8, 1.5], \"match\": 62.5}}, \"severidad\": \"Moderada\"}, \"hiperactivo\": {\"probabilidad\": 56.0, \"detalles\": {\"atencion_central\": {\"valor\": 100.0, \"rango_esperado\": [50, 75], \"match\": 66.7}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [35, 70], \"match\": 0}, \"precision_seguimiento\": {\"valor\": 100.0, \"rango_esperado\": [50, 70], \"match\": 57.1}, \"reaccion_promedio\": {\"valor\": 0.5, \"rango_esperado\": [0.2, 0.5], \"match\": 100}}, \"severidad\": \"Moderada\"}, \"combinado\": {\"probabilidad\": 41.7, \"detalles\": {\"atencion_central\": {\"valor\": 100.0, \"rango_esperado\": [30, 60], \"match\": 33.3}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [30, 60], \"match\": 0}, \"precision_seguimiento\": {\"valor\": 100.0, \"rango_esperado\": [35, 60], \"match\": 33.3}, \"reaccion_promedio\": {\"valor\": 0.5, \"rango_esperado\": [0.5, 1.2], \"match\": 100}}, \"severidad\": \"Moderada\"}}, \"metricas\": {\"frames_procesados\": 198, \"dispersion_promedio\": 5.42, \"atencion_central\": 100.0, \"precision_seguimiento\": 100.0, \"reaccion_promedio\": 0.5, \"puntos_completados\": 1, \"aciertos_totales\": 172, \"observaciones_totales\": 172}, \"duracion\": 30, \"interpretacion\": \"Los patrones observados están dentro del rango típico. Precisión de seguimiento: 100.0%.\"}', 'Tipo: typical (72%). Los patrones observados están dentro del rango típico. Precisión de seguimiento: 100.0%.', 0, NULL, '2025-12-10 16:57:05', 'vision', 'sin_determinar', 72, '{\"tipo_tdah\": \"typical\", \"confianza\": 72, \"scores_detallados\": {\"typical\": {\"probabilidad\": 72.4, \"detalles\": {\"atencion_central\": {\"valor\": 100.0, \"rango_esperado\": [75, 95], \"match\": 94.7}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [10, 25], \"match\": 0}, \"precision_seguimiento\": {\"valor\": 100.0, \"rango_esperado\": [70, 95], \"match\": 94.7}, \"reaccion_promedio\": {\"valor\": 0.5, \"rango_esperado\": [0.3, 0.8], \"match\": 100}}, \"severidad\": \"Moderada-Alta\"}, \"inatento\": {\"probabilidad\": 41.4, \"detalles\": {\"atencion_central\": {\"valor\": 100.0, \"rango_esperado\": [40, 70], \"match\": 57.1}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [15, 35], \"match\": 0}, \"precision_seguimiento\": {\"valor\": 100.0, \"rango_esperado\": [40, 65], \"match\": 46.2}, \"reaccion_promedio\": {\"valor\": 0.5, \"rango_esperado\": [0.8, 1.5], \"match\": 62.5}}, \"severidad\": \"Moderada\"}, \"hiperactivo\": {\"probabilidad\": 56.0, \"detalles\": {\"atencion_central\": {\"valor\": 100.0, \"rango_esperado\": [50, 75], \"match\": 66.7}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [35, 70], \"match\": 0}, \"precision_seguimiento\": {\"valor\": 100.0, \"rango_esperado\": [50, 70], \"match\": 57.1}, \"reaccion_promedio\": {\"valor\": 0.5, \"rango_esperado\": [0.2, 0.5], \"match\": 100}}, \"severidad\": \"Moderada\"}, \"combinado\": {\"probabilidad\": 41.7, \"detalles\": {\"atencion_central\": {\"valor\": 100.0, \"rango_esperado\": [30, 60], \"match\": 33.3}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [30, 60], \"match\": 0}, \"precision_seguimiento\": {\"valor\": 100.0, \"rango_esperado\": [35, 60], \"match\": 33.3}, \"reaccion_promedio\": {\"valor\": 0.5, \"rango_esperado\": [0.5, 1.2], \"match\": 100}}, \"severidad\": \"Moderada\"}}, \"metricas\": {\"frames_procesados\": 198, \"dispersion_promedio\": 5.42, \"atencion_central\": 100.0, \"precision_seguimiento\": 100.0, \"reaccion_promedio\": 0.5, \"puntos_completados\": 1, \"aciertos_totales\": 172, \"observaciones_totales\": 172}, \"duracion\": 30, \"interpretacion\": \"Los patrones observados están dentro del rango típico. Precisión de seguimiento: 100.0%.\"}'),
(28, 1, NULL, NULL, 'audio_test', '{\"transcripcion\": \"Había una vez un niño llamado Lucas Lucas siempre tenía muchas ideas y le encantaba soñar despierto en la escuela su maestro le decía que prestara más atención Pero a veces su mente se iba a lugares mágicos un día Lucas decidió explorar un bosque cercano mientras caminaba vio una ardilla corre rápido de un árbol a otro Lucas intentó seguirla pero se distrajo con una mariposa colorida\", \"metricas\": {\"duracion_grabacion\": 36.096, \"palabras_correctas\": 67, \"palabras_totales\": 69, \"precision\": 97.10144927536231, \"pausas_detectadas\": 0, \"repeticiones\": 14, \"fluidez\": 73.17041833693084, \"velocidad_lectura\": 113.03191489361703}, \"tipo_tdah\": \"hiperactivo\", \"confianza\": 74, \"scores_detallados\": {\"typical\": {\"probabilidad\": 73.0, \"detalles\": {\"precision\": {\"valor\": 97.10144927536231, \"rango_esperado\": [75, 95], \"match\": 97.8}, \"velocidad_lectura\": {\"valor\": 113.03191489361703, \"rango_esperado\": [120, 180], \"match\": 94.2}, \"repeticiones\": {\"valor\": 14, \"rango_esperado\": [0, 3], \"match\": 0}, \"fluidez\": {\"valor\": 73.17041833693084, \"rango_esperado\": [70, 95], \"match\": 100}}, \"severidad\": \"Moderada-Alta\"}, \"inatento\": {\"probabilidad\": 61.5, \"detalles\": {\"precision\": {\"valor\": 97.10144927536231, \"rango_esperado\": [40, 70], \"match\": 61.3}, \"velocidad_lectura\": {\"valor\": 113.03191489361703, \"rango_esperado\": [60, 110], \"match\": 97.2}, \"repeticiones\": {\"valor\": 14, \"rango_esperado\": [2, 6], \"match\": 0}, \"fluidez\": {\"valor\": 73.17041833693084, \"rango_esperado\": [40, 65], \"match\": 87.4}}, \"severidad\": \"Moderada-Alta\"}, \"hiperactivo\": {\"probabilidad\": 74.2, \"detalles\": {\"precision\": {\"valor\": 97.10144927536231, \"rango_esperado\": [60, 80], \"match\": 78.6}, \"velocidad_lectura\": {\"valor\": 113.03191489361703, \"rango_esperado\": [180, 250], \"match\": 62.8}, \"repeticiones\": {\"valor\": 14, \"rango_esperado\": [4, 10], \"match\": 60.0}, \"fluidez\": {\"valor\": 73.17041833693084, \"rango_esperado\": [50, 70], \"match\": 95.5}}, \"severidad\": \"Moderada-Alta\"}, \"combinado\": {\"probabilidad\": 63.4, \"detalles\": {\"precision\": {\"valor\": 97.10144927536231, \"rango_esperado\": [35, 65], \"match\": 50.6}, \"velocidad_lectura\": {\"valor\": 113.03191489361703, \"rango_esperado\": [70, 190], \"match\": 100}, \"repeticiones\": {\"valor\": 14, \"rango_esperado\": [3, 8], \"match\": 25.0}, \"fluidez\": {\"valor\": 73.17041833693084, \"rango_esperado\": [35, 60], \"match\": 78.0}}, \"severidad\": \"Moderada-Alta\"}}}', 'Tipo detectado: hiperactivo con 74% de confianza', 0, NULL, '2025-12-10 16:58:15', 'vision', 'sin_determinar', 74, '{\"transcripcion\": \"Había una vez un niño llamado Lucas Lucas siempre tenía muchas ideas y le encantaba soñar despierto en la escuela su maestro le decía que prestara más atención Pero a veces su mente se iba a lugares mágicos un día Lucas decidió explorar un bosque cercano mientras caminaba vio una ardilla corre rápido de un árbol a otro Lucas intentó seguirla pero se distrajo con una mariposa colorida\", \"metricas\": {\"duracion_grabacion\": 36.096, \"palabras_correctas\": 67, \"palabras_totales\": 69, \"precision\": 97.10144927536231, \"pausas_detectadas\": 0, \"repeticiones\": 14, \"fluidez\": 73.17041833693084, \"velocidad_lectura\": 113.03191489361703}, \"tipo_tdah\": \"hiperactivo\", \"confianza\": 74, \"scores_detallados\": {\"typical\": {\"probabilidad\": 73.0, \"detalles\": {\"precision\": {\"valor\": 97.10144927536231, \"rango_esperado\": [75, 95], \"match\": 97.8}, \"velocidad_lectura\": {\"valor\": 113.03191489361703, \"rango_esperado\": [120, 180], \"match\": 94.2}, \"repeticiones\": {\"valor\": 14, \"rango_esperado\": [0, 3], \"match\": 0}, \"fluidez\": {\"valor\": 73.17041833693084, \"rango_esperado\": [70, 95], \"match\": 100}}, \"severidad\": \"Moderada-Alta\"}, \"inatento\": {\"probabilidad\": 61.5, \"detalles\": {\"precision\": {\"valor\": 97.10144927536231, \"rango_esperado\": [40, 70], \"match\": 61.3}, \"velocidad_lectura\": {\"valor\": 113.03191489361703, \"rango_esperado\": [60, 110], \"match\": 97.2}, \"repeticiones\": {\"valor\": 14, \"rango_esperado\": [2, 6], \"match\": 0}, \"fluidez\": {\"valor\": 73.17041833693084, \"rango_esperado\": [40, 65], \"match\": 87.4}}, \"severidad\": \"Moderada-Alta\"}, \"hiperactivo\": {\"probabilidad\": 74.2, \"detalles\": {\"precision\": {\"valor\": 97.10144927536231, \"rango_esperado\": [60, 80], \"match\": 78.6}, \"velocidad_lectura\": {\"valor\": 113.03191489361703, \"rango_esperado\": [180, 250], \"match\": 62.8}, \"repeticiones\": {\"valor\": 14, \"rango_esperado\": [4, 10], \"match\": 60.0}, \"fluidez\": {\"valor\": 73.17041833693084, \"rango_esperado\": [50, 70], \"match\": 95.5}}, \"severidad\": \"Moderada-Alta\"}, \"combinado\": {\"probabilidad\": 63.4, \"detalles\": {\"precision\": {\"valor\": 97.10144927536231, \"rango_esperado\": [35, 65], \"match\": 50.6}, \"velocidad_lectura\": {\"valor\": 113.03191489361703, \"rango_esperado\": [70, 190], \"match\": 100}, \"repeticiones\": {\"valor\": 14, \"rango_esperado\": [3, 8], \"match\": 25.0}, \"fluidez\": {\"valor\": 73.17041833693084, \"rango_esperado\": [35, 60], \"match\": 78.0}}, \"severidad\": \"Moderada-Alta\"}}}');
INSERT INTO `reports` (`id`, `student_id`, `teacher_id`, `session_id`, `report_type`, `content`, `recommendations`, `sent_to_parents`, `parent_email`, `created_at`, `test_type`, `tipo_tdah`, `confianza`, `result_data`) VALUES
(29, 1, NULL, NULL, 'stroop_test', '{\"tipo_tdah\": \"combinado\", \"confianza\": 66, \"metricas\": {\"total_intentos\": 30, \"correctos\": 11, \"incorrectos\": 19, \"precision\": 36.666666666666664, \"tiempo_promedio\": 2538.818181818182, \"errores_congruentes\": 6, \"errores_incongruentes\": 13, \"tiempo_congruente\": 2539.1111111111113, \"tiempo_incongruente\": 2537.5, \"efecto_stroop\": -1.6111111111113132}, \"scores_detallados\": {\"typical\": {\"probabilidad\": 19.1, \"detalles\": {\"precision\": {\"valor\": 36.666666666666664, \"rango_esperado\": [80, 100], \"match\": 45.8}, \"tiempo_promedio\": {\"valor\": 2538.818181818182, \"rango_esperado\": [800, 1500], \"match\": 30.7}, \"errores_incongruentes\": {\"valor\": 13, \"rango_esperado\": [0, 3], \"match\": 0}, \"efecto_stroop\": {\"valor\": -1.6111111111113132, \"rango_esperado\": [100, 300], \"match\": 0}}, \"severidad\": \"Mínima\"}, \"inatento\": {\"probabilidad\": 60.4, \"detalles\": {\"precision\": {\"valor\": 36.666666666666664, \"rango_esperado\": [50, 75], \"match\": 73.3}, \"tiempo_promedio\": {\"valor\": 2538.818181818182, \"rango_esperado\": [1500, 2500], \"match\": 98.4}, \"errores_incongruentes\": {\"valor\": 13, \"rango_esperado\": [4, 10], \"match\": 70.0}, \"efecto_stroop\": {\"valor\": -1.6111111111113132, \"rango_esperado\": [300, 600], \"match\": 0}}, \"severidad\": \"Moderada-Alta\"}, \"hiperactivo\": {\"probabilidad\": 38.2, \"detalles\": {\"precision\": {\"valor\": 36.666666666666664, \"rango_esperado\": [60, 85], \"match\": 61.1}, \"tiempo_promedio\": {\"valor\": 2538.818181818182, \"rango_esperado\": [600, 1200], \"match\": 0}, \"errores_incongruentes\": {\"valor\": 13, \"rango_esperado\": [5, 12], \"match\": 91.7}, \"efecto_stroop\": {\"valor\": -1.6111111111113132, \"rango_esperado\": [200, 500], \"match\": 0}}, \"severidad\": \"Leve\"}, \"combinado\": {\"probabilidad\": 66.5, \"detalles\": {\"precision\": {\"valor\": 36.666666666666664, \"rango_esperado\": [45, 70], \"match\": 81.5}, \"tiempo_promedio\": {\"valor\": 2538.818181818182, \"rango_esperado\": [1200, 2200], \"match\": 84.6}, \"errores_incongruentes\": {\"valor\": 13, \"rango_esperado\": [6, 15], \"match\": 100}, \"efecto_stroop\": {\"valor\": -1.6111111111113132, \"rango_esperado\": [350, 700], \"match\": 0}}, \"severidad\": \"Moderada-Alta\"}}, \"duracion\": 79}', 'Tipo: combinado (66%)', 0, NULL, '2025-12-10 17:00:07', 'vision', 'sin_determinar', 66, '{\"tipo_tdah\": \"combinado\", \"confianza\": 66, \"metricas\": {\"total_intentos\": 30, \"correctos\": 11, \"incorrectos\": 19, \"precision\": 36.666666666666664, \"tiempo_promedio\": 2538.818181818182, \"errores_congruentes\": 6, \"errores_incongruentes\": 13, \"tiempo_congruente\": 2539.1111111111113, \"tiempo_incongruente\": 2537.5, \"efecto_stroop\": -1.6111111111113132}, \"scores_detallados\": {\"typical\": {\"probabilidad\": 19.1, \"detalles\": {\"precision\": {\"valor\": 36.666666666666664, \"rango_esperado\": [80, 100], \"match\": 45.8}, \"tiempo_promedio\": {\"valor\": 2538.818181818182, \"rango_esperado\": [800, 1500], \"match\": 30.7}, \"errores_incongruentes\": {\"valor\": 13, \"rango_esperado\": [0, 3], \"match\": 0}, \"efecto_stroop\": {\"valor\": -1.6111111111113132, \"rango_esperado\": [100, 300], \"match\": 0}}, \"severidad\": \"Mínima\"}, \"inatento\": {\"probabilidad\": 60.4, \"detalles\": {\"precision\": {\"valor\": 36.666666666666664, \"rango_esperado\": [50, 75], \"match\": 73.3}, \"tiempo_promedio\": {\"valor\": 2538.818181818182, \"rango_esperado\": [1500, 2500], \"match\": 98.4}, \"errores_incongruentes\": {\"valor\": 13, \"rango_esperado\": [4, 10], \"match\": 70.0}, \"efecto_stroop\": {\"valor\": -1.6111111111113132, \"rango_esperado\": [300, 600], \"match\": 0}}, \"severidad\": \"Moderada-Alta\"}, \"hiperactivo\": {\"probabilidad\": 38.2, \"detalles\": {\"precision\": {\"valor\": 36.666666666666664, \"rango_esperado\": [60, 85], \"match\": 61.1}, \"tiempo_promedio\": {\"valor\": 2538.818181818182, \"rango_esperado\": [600, 1200], \"match\": 0}, \"errores_incongruentes\": {\"valor\": 13, \"rango_esperado\": [5, 12], \"match\": 91.7}, \"efecto_stroop\": {\"valor\": -1.6111111111113132, \"rango_esperado\": [200, 500], \"match\": 0}}, \"severidad\": \"Leve\"}, \"combinado\": {\"probabilidad\": 66.5, \"detalles\": {\"precision\": {\"valor\": 36.666666666666664, \"rango_esperado\": [45, 70], \"match\": 81.5}, \"tiempo_promedio\": {\"valor\": 2538.818181818182, \"rango_esperado\": [1200, 2200], \"match\": 84.6}, \"errores_incongruentes\": {\"valor\": 13, \"rango_esperado\": [6, 15], \"match\": 100}, \"efecto_stroop\": {\"valor\": -1.6111111111113132, \"rango_esperado\": [350, 700], \"match\": 0}}, \"severidad\": \"Moderada-Alta\"}}, \"duracion\": 79}'),
(30, 1, NULL, NULL, 'gonogo_test', '{\"tipo_tdah\": \"typical\", \"confianza\": 100, \"metricas\": {\"total_go\": 28, \"total_nogo\": 12, \"aciertos_go\": 28, \"aciertos_nogo\": 12, \"errores_omision\": 0, \"falsos_positivos\": 0, \"precision_go\": 100.0, \"precision_nogo\": 100.0, \"tiempo_reaccion_promedio\": 530.6071428571429, \"anticipaciones\": 0}, \"scores_detallados\": {\"typical\": {\"probabilidad\": 100.0, \"detalles\": {\"precision_go\": {\"valor\": 100.0, \"rango_esperado\": [85, 100], \"match\": 100}, \"precision_nogo\": {\"valor\": 100.0, \"rango_esperado\": [85, 100], \"match\": 100}, \"falsos_positivos\": {\"valor\": 0, \"rango_esperado\": [0, 3], \"match\": 100}, \"tiempo_reaccion_promedio\": {\"valor\": 530.6071428571429, \"rango_esperado\": [300, 600], \"match\": 100}}, \"severidad\": \"Alta\"}, \"inatento\": {\"probabilidad\": 66.0, \"detalles\": {\"precision_go\": {\"valor\": 100.0, \"rango_esperado\": [60, 80], \"match\": 75.0}, \"precision_nogo\": {\"valor\": 100.0, \"rango_esperado\": [70, 90], \"match\": 88.9}, \"falsos_positivos\": {\"valor\": 0, \"rango_esperado\": [2, 6], \"match\": 0}, \"tiempo_reaccion_promedio\": {\"valor\": 530.6071428571429, \"rango_esperado\": [500, 900], \"match\": 100}}, \"severidad\": \"Moderada-Alta\"}, \"hiperactivo\": {\"probabilidad\": 54.8, \"detalles\": {\"precision_go\": {\"valor\": 100.0, \"rango_esperado\": [75, 95], \"match\": 94.7}, \"precision_nogo\": {\"valor\": 100.0, \"rango_esperado\": [40, 70], \"match\": 57.1}, \"falsos_positivos\": {\"valor\": 0, \"rango_esperado\": [8, 20], \"match\": 0}, \"tiempo_reaccion_promedio\": {\"valor\": 530.6071428571429, \"rango_esperado\": [200, 400], \"match\": 67.3}}, \"severidad\": \"Moderada\"}, \"combinado\": {\"probabilidad\": 58.3, \"detalles\": {\"precision_go\": {\"valor\": 100.0, \"rango_esperado\": [55, 75], \"match\": 66.7}, \"precision_nogo\": {\"valor\": 100.0, \"rango_esperado\": [50, 75], \"match\": 66.7}, \"falsos_positivos\": {\"valor\": 0, \"rango_esperado\": [5, 12], \"match\": 0}, \"tiempo_reaccion_promedio\": {\"valor\": 530.6071428571429, \"rango_esperado\": [400, 700], \"match\": 100}}, \"severidad\": \"Moderada\"}}, \"duracion\": 62}', 'Tipo: typical (100%)', 0, NULL, '2025-12-10 17:01:44', 'vision', 'sin_determinar', 100, '{\"tipo_tdah\": \"typical\", \"confianza\": 100, \"metricas\": {\"total_go\": 28, \"total_nogo\": 12, \"aciertos_go\": 28, \"aciertos_nogo\": 12, \"errores_omision\": 0, \"falsos_positivos\": 0, \"precision_go\": 100.0, \"precision_nogo\": 100.0, \"tiempo_reaccion_promedio\": 530.6071428571429, \"anticipaciones\": 0}, \"scores_detallados\": {\"typical\": {\"probabilidad\": 100.0, \"detalles\": {\"precision_go\": {\"valor\": 100.0, \"rango_esperado\": [85, 100], \"match\": 100}, \"precision_nogo\": {\"valor\": 100.0, \"rango_esperado\": [85, 100], \"match\": 100}, \"falsos_positivos\": {\"valor\": 0, \"rango_esperado\": [0, 3], \"match\": 100}, \"tiempo_reaccion_promedio\": {\"valor\": 530.6071428571429, \"rango_esperado\": [300, 600], \"match\": 100}}, \"severidad\": \"Alta\"}, \"inatento\": {\"probabilidad\": 66.0, \"detalles\": {\"precision_go\": {\"valor\": 100.0, \"rango_esperado\": [60, 80], \"match\": 75.0}, \"precision_nogo\": {\"valor\": 100.0, \"rango_esperado\": [70, 90], \"match\": 88.9}, \"falsos_positivos\": {\"valor\": 0, \"rango_esperado\": [2, 6], \"match\": 0}, \"tiempo_reaccion_promedio\": {\"valor\": 530.6071428571429, \"rango_esperado\": [500, 900], \"match\": 100}}, \"severidad\": \"Moderada-Alta\"}, \"hiperactivo\": {\"probabilidad\": 54.8, \"detalles\": {\"precision_go\": {\"valor\": 100.0, \"rango_esperado\": [75, 95], \"match\": 94.7}, \"precision_nogo\": {\"valor\": 100.0, \"rango_esperado\": [40, 70], \"match\": 57.1}, \"falsos_positivos\": {\"valor\": 0, \"rango_esperado\": [8, 20], \"match\": 0}, \"tiempo_reaccion_promedio\": {\"valor\": 530.6071428571429, \"rango_esperado\": [200, 400], \"match\": 67.3}}, \"severidad\": \"Moderada\"}, \"combinado\": {\"probabilidad\": 58.3, \"detalles\": {\"precision_go\": {\"valor\": 100.0, \"rango_esperado\": [55, 75], \"match\": 66.7}, \"precision_nogo\": {\"valor\": 100.0, \"rango_esperado\": [50, 75], \"match\": 66.7}, \"falsos_positivos\": {\"valor\": 0, \"rango_esperado\": [5, 12], \"match\": 0}, \"tiempo_reaccion_promedio\": {\"valor\": 530.6071428571429, \"rango_esperado\": [400, 700], \"match\": 100}}, \"severidad\": \"Moderada\"}}, \"duracion\": 62}'),
(31, 1, NULL, NULL, 'stroop_test', '{\"tipo_tdah\": \"typical\", \"confianza\": 80, \"metricas\": {\"total_intentos\": 30, \"correctos\": 29, \"incorrectos\": 1, \"precision\": 96.66666666666667, \"tiempo_promedio\": 1762.5862068965516, \"errores_congruentes\": 0, \"errores_incongruentes\": 1, \"tiempo_congruente\": 1529.8666666666666, \"tiempo_incongruente\": 2011.9285714285713, \"efecto_stroop\": 482.06190476190477}, \"scores_detallados\": {\"typical\": {\"probabilidad\": 80.5, \"detalles\": {\"precision\": {\"valor\": 96.66666666666667, \"rango_esperado\": [80, 100], \"match\": 100}, \"tiempo_promedio\": {\"valor\": 1762.5862068965516, \"rango_esperado\": [800, 1500], \"match\": 82.5}, \"errores_incongruentes\": {\"valor\": 1, \"rango_esperado\": [0, 3], \"match\": 100}, \"efecto_stroop\": {\"valor\": 482.06190476190477, \"rango_esperado\": [100, 300], \"match\": 39.3}}, \"severidad\": \"Alta\"}, \"inatento\": {\"probabilidad\": 74.0, \"detalles\": {\"precision\": {\"valor\": 96.66666666666667, \"rango_esperado\": [50, 75], \"match\": 71.1}, \"tiempo_promedio\": {\"valor\": 1762.5862068965516, \"rango_esperado\": [1500, 2500], \"match\": 100}, \"errores_incongruentes\": {\"valor\": 1, \"rango_esperado\": [4, 10], \"match\": 25.0}, \"efecto_stroop\": {\"valor\": 482.06190476190477, \"rango_esperado\": [300, 600], \"match\": 100}}, \"severidad\": \"Moderada-Alta\"}, \"hiperactivo\": {\"probabilidad\": 64.8, \"detalles\": {\"precision\": {\"valor\": 96.66666666666667, \"rango_esperado\": [60, 85], \"match\": 86.3}, \"tiempo_promedio\": {\"valor\": 1762.5862068965516, \"rango_esperado\": [600, 1200], \"match\": 53.1}, \"errores_incongruentes\": {\"valor\": 1, \"rango_esperado\": [5, 12], \"match\": 20.0}, \"efecto_stroop\": {\"valor\": 482.06190476190477, \"rango_esperado\": [200, 500], \"match\": 100}}, \"severidad\": \"Moderada-Alta\"}, \"combinado\": {\"probabilidad\": 69.6, \"detalles\": {\"precision\": {\"valor\": 96.66666666666667, \"rango_esperado\": [45, 70], \"match\": 61.9}, \"tiempo_promedio\": {\"valor\": 1762.5862068965516, \"rango_esperado\": [1200, 2200], \"match\": 100}, \"errores_incongruentes\": {\"valor\": 1, \"rango_esperado\": [6, 15], \"match\": 16.7}, \"efecto_stroop\": {\"valor\": 482.06190476190477, \"rango_esperado\": [350, 700], \"match\": 100}}, \"severidad\": \"Moderada-Alta\"}}, \"duracion\": 66}', 'Tipo: typical (80%)', 0, NULL, '2025-12-11 21:04:36', 'vision', 'sin_determinar', 0, NULL),
(32, 1, NULL, NULL, 'vision_test', '{\"tipo_tdah\": \"typical\", \"confianza\": 75, \"scores_detallados\": {\"typical\": {\"probabilidad\": 75.0, \"detalles\": {\"atencion_central\": {\"valor\": 86.78, \"rango_esperado\": [75, 95], \"match\": 100}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [10, 25], \"match\": 0}, \"precision_seguimiento\": {\"valor\": 86.78, \"rango_esperado\": [70, 95], \"match\": 100}, \"reaccion_promedio\": {\"valor\": 0.5, \"rango_esperado\": [0.3, 0.8], \"match\": 100}}, \"severidad\": \"Moderada-Alta\"}, \"inatento\": {\"probabilidad\": 51.3, \"detalles\": {\"atencion_central\": {\"valor\": 86.78, \"rango_esperado\": [40, 70], \"match\": 76.0}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [15, 35], \"match\": 0}, \"precision_seguimiento\": {\"valor\": 86.78, \"rango_esperado\": [40, 65], \"match\": 66.5}, \"reaccion_promedio\": {\"valor\": 0.5, \"rango_esperado\": [0.8, 1.5], \"match\": 62.5}}, \"severidad\": \"Moderada\"}, \"hiperactivo\": {\"probabilidad\": 65.1, \"detalles\": {\"atencion_central\": {\"valor\": 86.78, \"rango_esperado\": [50, 75], \"match\": 84.3}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [35, 70], \"match\": 0}, \"precision_seguimiento\": {\"valor\": 86.78, \"rango_esperado\": [50, 70], \"match\": 76.0}, \"reaccion_promedio\": {\"valor\": 0.5, \"rango_esperado\": [0.2, 0.5], \"match\": 100}}, \"severidad\": \"Moderada-Alta\"}, \"combinado\": {\"probabilidad\": 52.7, \"detalles\": {\"atencion_central\": {\"valor\": 86.78, \"rango_esperado\": [30, 60], \"match\": 55.4}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [30, 60], \"match\": 0}, \"precision_seguimiento\": {\"valor\": 86.78, \"rango_esperado\": [35, 60], \"match\": 55.4}, \"reaccion_promedio\": {\"valor\": 0.5, \"rango_esperado\": [0.5, 1.2], \"match\": 100}}, \"severidad\": \"Moderada\"}}, \"metricas\": {\"frames_procesados\": 295, \"dispersion_promedio\": 3.71, \"atencion_central\": 86.78, \"precision_seguimiento\": 86.78, \"reaccion_promedio\": 0.5, \"puntos_completados\": 1, \"aciertos_totales\": 256, \"observaciones_totales\": 295}, \"duracion\": 30, \"interpretacion\": \"Los patrones observados están dentro del rango típico. Precisión de seguimiento: 86.8%.\"}', 'Tipo: typical (75%). Los patrones observados están dentro del rango típico. Precisión de seguimiento: 86.8%.', 0, NULL, '2025-12-11 21:27:14', 'vision', 'sin_determinar', 0, NULL),
(33, 1, NULL, NULL, 'vision_test', '{\"tipo_tdah\": \"typical\", \"confianza\": 75, \"scores_detallados\": {\"typical\": {\"probabilidad\": 75.0, \"detalles\": {\"atencion_central\": {\"valor\": 86.82, \"rango_esperado\": [75, 95], \"match\": 100}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [10, 25], \"match\": 0}, \"precision_seguimiento\": {\"valor\": 86.82, \"rango_esperado\": [70, 95], \"match\": 100}, \"reaccion_promedio\": {\"valor\": 0.5, \"rango_esperado\": [0.3, 0.8], \"match\": 100}}, \"severidad\": \"Moderada-Alta\"}, \"inatento\": {\"probabilidad\": 51.2, \"detalles\": {\"atencion_central\": {\"valor\": 86.82, \"rango_esperado\": [40, 70], \"match\": 76.0}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [15, 35], \"match\": 0}, \"precision_seguimiento\": {\"valor\": 86.82, \"rango_esperado\": [40, 65], \"match\": 66.4}, \"reaccion_promedio\": {\"valor\": 0.5, \"rango_esperado\": [0.8, 1.5], \"match\": 62.5}}, \"severidad\": \"Moderada\"}, \"hiperactivo\": {\"probabilidad\": 65.1, \"detalles\": {\"atencion_central\": {\"valor\": 86.82, \"rango_esperado\": [50, 75], \"match\": 84.2}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [35, 70], \"match\": 0}, \"precision_seguimiento\": {\"valor\": 86.82, \"rango_esperado\": [50, 70], \"match\": 76.0}, \"reaccion_promedio\": {\"valor\": 0.5, \"rango_esperado\": [0.2, 0.5], \"match\": 100}}, \"severidad\": \"Moderada-Alta\"}, \"combinado\": {\"probabilidad\": 52.7, \"detalles\": {\"atencion_central\": {\"valor\": 86.82, \"rango_esperado\": [30, 60], \"match\": 55.3}, \"dispersion\": {\"valor\": 0, \"rango_esperado\": [30, 60], \"match\": 0}, \"precision_seguimiento\": {\"valor\": 86.82, \"rango_esperado\": [35, 60], \"match\": 55.3}, \"reaccion_promedio\": {\"valor\": 0.5, \"rango_esperado\": [0.5, 1.2], \"match\": 100}}, \"severidad\": \"Moderada\"}}, \"metricas\": {\"frames_procesados\": 296, \"dispersion_promedio\": 3.71, \"atencion_central\": 86.82, \"precision_seguimiento\": 86.82, \"reaccion_promedio\": 0.5, \"puntos_completados\": 1, \"aciertos_totales\": 257, \"observaciones_totales\": 296}, \"duracion\": 30, \"interpretacion\": \"Los patrones observados están dentro del rango típico. Precisión de seguimiento: 86.8%.\"}', 'Tipo: typical (75%). Los patrones observados están dentro del rango típico. Precisión de seguimiento: 86.8%.', 0, NULL, '2025-12-11 21:27:14', 'vision', 'sin_determinar', 0, NULL),
(34, 1, NULL, NULL, 'audio_test', '{\"transcripcion\": \"Había una vez un niño llamado Lucas Lucas siempre tenía muchas ideas y le encantaba soñar despierto en la escuela su maestro le decía que prestara más atención Pero a veces su mente se iba a lugares mágicos un día Lucas decidió explorar un bosque cercano mientras caminaba vio una ardilla correr rápido de un árbol a otro Lucas intentó seguirla pero se distrajo con una mariposa colorida\", \"metricas\": {\"duracion_grabacion\": 24.576, \"palabras_correctas\": 67, \"palabras_totales\": 69, \"precision\": 97.10144927536231, \"pausas_detectadas\": 0, \"repeticiones\": 14, \"fluidez\": 107.46905193236714, \"velocidad_lectura\": 166.015625}, \"tipo_tdah\": \"typical\", \"confianza\": 71, \"scores_detallados\": {\"typical\": {\"probabilidad\": 71.2, \"detalles\": {\"precision\": {\"valor\": 97.10144927536231, \"rango_esperado\": [75, 95], \"match\": 97.8}, \"velocidad_lectura\": {\"valor\": 166.015625, \"rango_esperado\": [120, 180], \"match\": 100}, \"repeticiones\": {\"valor\": 14, \"rango_esperado\": [0, 3], \"match\": 0}, \"fluidez\": {\"valor\": 107.46905193236714, \"rango_esperado\": [70, 95], \"match\": 86.9}}, \"severidad\": \"Moderada-Alta\"}, \"inatento\": {\"probabilidad\": 36.3, \"detalles\": {\"precision\": {\"valor\": 97.10144927536231, \"rango_esperado\": [40, 70], \"match\": 61.3}, \"velocidad_lectura\": {\"valor\": 166.015625, \"rango_esperado\": [60, 110], \"match\": 49.1}, \"repeticiones\": {\"valor\": 14, \"rango_esperado\": [2, 6], \"match\": 0}, \"fluidez\": {\"valor\": 107.46905193236714, \"rango_esperado\": [40, 65], \"match\": 34.7}}, \"severidad\": \"Leve\"}, \"hiperactivo\": {\"probabilidad\": 69.3, \"detalles\": {\"precision\": {\"valor\": 97.10144927536231, \"rango_esperado\": [60, 80], \"match\": 78.6}, \"velocidad_lectura\": {\"valor\": 166.015625, \"rango_esperado\": [180, 250], \"match\": 92.2}, \"repeticiones\": {\"valor\": 14, \"rango_esperado\": [4, 10], \"match\": 60.0}, \"fluidez\": {\"valor\": 107.46905193236714, \"rango_esperado\": [50, 70], \"match\": 46.5}}, \"severidad\": \"Moderada-Alta\"}, \"combinado\": {\"probabilidad\": 49.1, \"detalles\": {\"precision\": {\"valor\": 97.10144927536231, \"rango_esperado\": [35, 65], \"match\": 50.6}, \"velocidad_lectura\": {\"valor\": 166.015625, \"rango_esperado\": [70, 190], \"match\": 100}, \"repeticiones\": {\"valor\": 14, \"rango_esperado\": [3, 8], \"match\": 25.0}, \"fluidez\": {\"valor\": 107.46905193236714, \"rango_esperado\": [35, 60], \"match\": 20.9}}, \"severidad\": \"Moderada\"}}}', 'Tipo detectado: typical con 71% de confianza', 0, NULL, '2025-12-11 21:39:10', 'vision', 'sin_determinar', 0, NULL),
(35, 1, NULL, NULL, 'stroop_test', '{\"tipo_tdah\": \"inatento\", \"confianza\": 94, \"metricas\": {\"total_intentos\": 30, \"correctos\": 22, \"incorrectos\": 8, \"precision\": 73.33333333333333, \"tiempo_promedio\": 1584.6818181818182, \"errores_congruentes\": 1, \"errores_incongruentes\": 7, \"tiempo_congruente\": 1498.0, \"tiempo_incongruente\": 1736.375, \"efecto_stroop\": 238.375}, \"scores_detallados\": {\"typical\": {\"probabilidad\": 71.5, \"detalles\": {\"precision\": {\"valor\": 73.33333333333333, \"rango_esperado\": [80, 100], \"match\": 91.7}, \"tiempo_promedio\": {\"valor\": 1584.6818181818182, \"rango_esperado\": [800, 1500], \"match\": 94.4}, \"errores_incongruentes\": {\"valor\": 7, \"rango_esperado\": [0, 3], \"match\": 0}, \"efecto_stroop\": {\"valor\": 238.375, \"rango_esperado\": [100, 300], \"match\": 100}}, \"severidad\": \"Moderada-Alta\"}, \"inatento\": {\"probabilidad\": 94.9, \"detalles\": {\"precision\": {\"valor\": 73.33333333333333, \"rango_esperado\": [50, 75], \"match\": 100}, \"tiempo_promedio\": {\"valor\": 1584.6818181818182, \"rango_esperado\": [1500, 2500], \"match\": 100}, \"errores_incongruentes\": {\"valor\": 7, \"rango_esperado\": [4, 10], \"match\": 100}, \"efecto_stroop\": {\"valor\": 238.375, \"rango_esperado\": [300, 600], \"match\": 79.5}}, \"severidad\": \"Alta\"}, \"hiperactivo\": {\"probabilidad\": 92.0, \"detalles\": {\"precision\": {\"valor\": 73.33333333333333, \"rango_esperado\": [60, 85], \"match\": 100}, \"tiempo_promedio\": {\"valor\": 1584.6818181818182, \"rango_esperado\": [600, 1200], \"match\": 67.9}, \"errores_incongruentes\": {\"valor\": 7, \"rango_esperado\": [5, 12], \"match\": 100}, \"efecto_stroop\": {\"valor\": 238.375, \"rango_esperado\": [200, 500], \"match\": 100}}, \"severidad\": \"Alta\"}, \"combinado\": {\"probabilidad\": 90.8, \"detalles\": {\"precision\": {\"valor\": 73.33333333333333, \"rango_esperado\": [45, 70], \"match\": 95.2}, \"tiempo_promedio\": {\"valor\": 1584.6818181818182, \"rango_esperado\": [1200, 2200], \"match\": 100}, \"errores_incongruentes\": {\"valor\": 7, \"rango_esperado\": [6, 15], \"match\": 100}, \"efecto_stroop\": {\"valor\": 238.375, \"rango_esperado\": [350, 700], \"match\": 68.1}}, \"severidad\": \"Alta\"}}, \"duracion\": 62}', 'Tipo: inatento (94%)', 0, NULL, '2025-12-11 21:42:09', 'vision', 'sin_determinar', 0, NULL),
(36, 1, NULL, NULL, 'gonogo_test', '{\"tipo_tdah\": \"typical\", \"confianza\": 97, \"metricas\": {\"total_go\": 28, \"total_nogo\": 12, \"aciertos_go\": 28, \"aciertos_nogo\": 9, \"errores_omision\": 0, \"falsos_positivos\": 3, \"precision_go\": 100.0, \"precision_nogo\": 75.0, \"tiempo_reaccion_promedio\": 457.5357142857143, \"anticipaciones\": 0}, \"scores_detallados\": {\"typical\": {\"probabilidad\": 97.1, \"detalles\": {\"precision_go\": {\"valor\": 100.0, \"rango_esperado\": [85, 100], \"match\": 100}, \"precision_nogo\": {\"valor\": 75.0, \"rango_esperado\": [85, 100], \"match\": 88.2}, \"falsos_positivos\": {\"valor\": 3, \"rango_esperado\": [0, 3], \"match\": 100}, \"tiempo_reaccion_promedio\": {\"valor\": 457.5357142857143, \"rango_esperado\": [300, 600], \"match\": 100}}, \"severidad\": \"Alta\"}, \"inatento\": {\"probabilidad\": 91.6, \"detalles\": {\"precision_go\": {\"valor\": 100.0, \"rango_esperado\": [60, 80], \"match\": 75.0}, \"precision_nogo\": {\"valor\": 75.0, \"rango_esperado\": [70, 90], \"match\": 100}, \"falsos_positivos\": {\"valor\": 3, \"rango_esperado\": [2, 6], \"match\": 100}, \"tiempo_reaccion_promedio\": {\"valor\": 457.5357142857143, \"rango_esperado\": [500, 900], \"match\": 91.5}}, \"severidad\": \"Alta\"}, \"hiperactivo\": {\"probabilidad\": 77.7, \"detalles\": {\"precision_go\": {\"valor\": 100.0, \"rango_esperado\": [75, 95], \"match\": 94.7}, \"precision_nogo\": {\"valor\": 75.0, \"rango_esperado\": [40, 70], \"match\": 92.9}, \"falsos_positivos\": {\"valor\": 3, \"rango_esperado\": [8, 20], \"match\": 37.5}, \"tiempo_reaccion_promedio\": {\"valor\": 457.5357142857143, \"rango_esperado\": [200, 400], \"match\": 85.6}}, \"severidad\": \"Moderada-Alta\"}, \"combinado\": {\"probabilidad\": 81.7, \"detalles\": {\"precision_go\": {\"valor\": 100.0, \"rango_esperado\": [55, 75], \"match\": 66.7}, \"precision_nogo\": {\"valor\": 75.0, \"rango_esperado\": [50, 75], \"match\": 100}, \"falsos_positivos\": {\"valor\": 3, \"rango_esperado\": [5, 12], \"match\": 60.0}, \"tiempo_reaccion_promedio\": {\"valor\": 457.5357142857143, \"rango_esperado\": [400, 700], \"match\": 100}}, \"severidad\": \"Alta\"}}, \"duracion\": 62}', 'Tipo: typical (97%)', 0, NULL, '2025-12-11 21:44:36', 'vision', 'sin_determinar', 0, NULL);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `sessions`
--

CREATE TABLE `sessions` (
  `id` int(11) NOT NULL,
  `student_id` int(11) NOT NULL,
  `activity_id` int(11) DEFAULT NULL,
  `video_path` varchar(255) DEFAULT NULL,
  `audio_path` varchar(255) DEFAULT NULL,
  `heatmap_path` varchar(255) DEFAULT NULL,
  `transcription` text DEFAULT NULL,
  `analysis_result` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`analysis_result`)),
  `attention_score` float DEFAULT NULL,
  `completion_time` int(11) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `stroop_test_data`
--

CREATE TABLE `stroop_test_data` (
  `id` int(11) NOT NULL,
  `report_id` int(11) NOT NULL,
  `congruent_time` float DEFAULT NULL COMMENT 'Tiempo promedio congruente',
  `incongruent_time` float DEFAULT NULL COMMENT 'Tiempo promedio incongruente',
  `interference_effect` float DEFAULT NULL COMMENT 'Efecto de interferencia',
  `total_trials` int(11) DEFAULT 0,
  `correct_trials` int(11) DEFAULT 0,
  `errors` int(11) DEFAULT 0,
  `created_at` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `students`
--

CREATE TABLE `students` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `teacher_id` int(11) DEFAULT NULL,
  `tdah_type` varchar(50) DEFAULT NULL,
  `age` int(11) DEFAULT NULL,
  `notes` text DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `grade` varchar(50) DEFAULT NULL,
  `section` varchar(50) DEFAULT NULL,
  `tdah_confidence` float DEFAULT 0,
  `last_evaluation_date` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `students`
--

INSERT INTO `students` (`id`, `user_id`, `teacher_id`, `tdah_type`, `age`, `notes`, `created_at`, `grade`, `section`, `tdah_confidence`, `last_evaluation_date`) VALUES
(1, 5, 2, 'inatento', 8, NULL, '2025-12-05 21:25:32', NULL, NULL, 72.5, '2025-12-11 21:44:36'),
(2, 6, 3, 'hiperactivo', 9, NULL, '2025-12-05 21:25:32', NULL, NULL, 0, NULL),
(3, 7, 4, 'combinado', 10, NULL, '2025-12-05 21:25:32', NULL, NULL, 0, NULL),
(4, 8, 2, 'inatento', 11, NULL, '2025-12-05 21:25:32', NULL, NULL, 0, NULL),
(5, 9, 3, 'hiperactivo', 8, NULL, '2025-12-05 21:25:33', NULL, NULL, 0, NULL),
(6, 10, 4, 'combinado', 9, NULL, '2025-12-05 21:25:33', NULL, NULL, 0, NULL),
(7, 12, 3, 'hiperactivo', 10, NULL, '2025-12-08 03:55:02', NULL, NULL, 0, NULL),
(8, 13, NULL, NULL, NULL, NULL, '2025-12-09 19:10:51', '5to Primaria', 'A', 0, NULL);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `teachers`
--

CREATE TABLE `teachers` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `specialty` varchar(100) DEFAULT NULL,
  `created_at` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `teacher_student`
--

CREATE TABLE `teacher_student` (
  `id` int(11) NOT NULL,
  `teacher_id` int(11) NOT NULL,
  `student_id` int(11) NOT NULL,
  `created_at` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `username` varchar(50) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `role` enum('admin','teacher','student','parent') NOT NULL,
  `created_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `users`
--

INSERT INTO `users` (`id`, `username`, `email`, `password_hash`, `role`, `created_at`) VALUES
(1, 'admin', 'admin@tdahplatform.com', 'scrypt:32768:8:1$WUhZm3Jr8MDS76Ta$2b53273ffdf0991c3b1f5fbf8533d811807159b8d5a38dcb3013f1b0a25fc564c55950d18ae724e3c668755a3d174e086b50ddbe526bb2fcc9f21c734a824a02', 'admin', '2025-12-05 21:25:32'),
(2, 'teacher1', 'teacher1@demo.com', 'scrypt:32768:8:1$ewkNh0KSfXS0Qu06$e6ec2226e74a23584629d8d04b76c0d1051036ef98e181e4cd63b35e556fc7fa9bdcbb2dd6d5eaac945a08b00aae16c3687a1b2bc6b32a2c021bd8e26fb8b937', 'teacher', '2025-12-05 21:25:32'),
(3, 'teacher2', 'teacher2@demo.com', 'scrypt:32768:8:1$GFUP4W4QYa9QNMnL$780c3d0a14ca351c0cef9093765726744c5af39fe0935b23b2f33899d996d725ddf995a8bc505894f88257a4112ee99ad20aaba26d6a82b4a6927197324b95cc', 'teacher', '2025-12-05 21:25:32'),
(4, 'teacher3', 'teacher3@demo.com', 'scrypt:32768:8:1$QoJr2pIbSm6QT3ws$9b166b10f1f518582ad4944537e82a0bfe7d06e7ab7204b75a6a753cdc474a150ceff5de48f44d6710d15ef54ed8106be1702db5818af7f7f5a248a308d4bcc9', 'teacher', '2025-12-05 21:25:32'),
(5, 'carlos', 'carlos@estudiante.com', 'scrypt:32768:8:1$nRrgvVBQjpic7eD4$9a5c4b73d81aae544b8b7979cacc0af192e4a4136dc628614e48f7f01049a5f4db96aa8c91903944d925a4eea0a08424e4de1aa089086a2591e8d58d09bc0cee', 'student', '2025-12-05 21:25:32'),
(6, 'lucia', 'lucia@estudiante.com', 'scrypt:32768:8:1$HbWr06rNn3EakSjY$09cfbc42324560e525113b93327b1e92008b83ae2b25174833c7142d29d4902dec6f81e557216a2925a79c28862dc62ad5f3dfe6961510b1263294273aea1fdd', 'student', '2025-12-05 21:25:32'),
(7, 'miguel', 'miguel@estudiante.com', 'scrypt:32768:8:1$rWJzHcpIuoIsl3aM$ebf38c892131704cd86e231a89333d97def75a466cfd0cba62f70405886d2d6d198d74ba84c55e30bbe939a4e27d5967c4b6e58bf981500e45bebc54f19f7bcd', 'student', '2025-12-05 21:25:32'),
(8, 'sofia', 'sofia@estudiante.com', 'scrypt:32768:8:1$z1OLGzd98bTx3onF$2b910dca7f5632420536770f19389b99d5105ef9540b3b3f2eef1bd1af14486ef0c1fba38a5e05d80d61c611e6e0969ae8ea7abf0ba18f51230c28e455b0ac13', 'student', '2025-12-05 21:25:32'),
(9, 'diego', 'diego@estudiante.com', 'scrypt:32768:8:1$OYzLp6E8NzMWtI26$ff1698d4ff8b35a41df7907b53d9a5642b2a55596c0a75454d0f13f20fe5730b623c4d736cf807b665f45290eec58f1f9177dae7d2e2ca515e225ca7eb5bb6f9', 'student', '2025-12-05 21:25:32'),
(10, 'emma', 'emma@estudiante.com', 'scrypt:32768:8:1$bEPECIonRBJRgJHj$c3a246fef8ec579df686689fd028a4ffa476594754f752692c8ba3bff7601c700cc942aa71e7d025672b3a3e4aa0a988a05216465f0904c5da5533b6eb8b5416', 'student', '2025-12-05 21:25:33'),
(11, 'Ricardo', 'ricardolm160@gmail.com', 'scrypt:32768:8:1$0MQU8GhwEkL9bNKl$43f4acb15a505e4f057e92837323def20afcaa446e13bcdd3edf52e932d020c3e36a9356bbf3afbe94c91ca85b8ea3d37ce08fa73118f9fc3f12ce78c6e61c69', 'admin', '2025-12-05 21:28:12'),
(12, 'David', 'david@gmai.com', 'scrypt:32768:8:1$Tu7Wx7lRhScx6U3z$4c31580bbbc6f6a019189a4618ed6600e8c159653cee77e22af6c6ef82a2e07faceeb785b260b6a0cdc5ec94f31b9507d11f554b2f3f31e8b248cec501ac79ae', 'student', '2025-12-08 03:55:02'),
(13, 'juan_estudiante', 'estudiante@test.com', 'scrypt:32768:8:1$Ku7ho6XR14ikWScd$426bfae499ae90fa9646ae8e66c9694a21abfeb6a91be28eb3ddf56bc912ff937c18fbf44eb02ebe02ba636d591b843a21542daa85354d46163dd59231d614dd', 'student', '2025-12-09 19:10:51'),
(15, 'Rick', 'ricardolm180@gmail.com', 'scrypt:32768:8:1$dsF3P8jgWUpI50sr$2fa2bf74dc817869a027e7e0a0fedb774ccac2f1ba2b2fd8ec73f7cd7bab31e080773886d54ac838ce7116c42a6036d9143c67377ee2ecd03ad8592a83cb2ef8', 'student', '2025-12-09 19:14:55'),
(16, 'maria_madre', 'padre@test.com', 'scrypt:32768:8:1$kwFbn43we4lCZKON$6cee8af75ea23705aacdc4d1172977452289169b6d2282038975159e5a8b89871af47bf65fd1fd2fee40793e1ed828a374dfa380d3b4762a39c374713d4024b1', 'parent', '2025-12-09 19:16:55');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `vision_test_data`
--

CREATE TABLE `vision_test_data` (
  `id` int(11) NOT NULL,
  `report_id` int(11) NOT NULL,
  `gaze_points` text DEFAULT NULL COMMENT 'JSON con puntos de mirada',
  `fixation_duration` float DEFAULT NULL,
  `saccade_count` int(11) DEFAULT NULL,
  `heatmap_data` text DEFAULT NULL COMMENT 'JSON con mapa de calor',
  `frames_procesados` int(11) DEFAULT NULL,
  `dispersion_promedio` float DEFAULT NULL,
  `atencion_central` float DEFAULT NULL,
  `atencion_periferica` float DEFAULT NULL,
  `atencion_dispersa` float DEFAULT NULL,
  `created_at` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura Stand-in para la vista `v_parent_children`
-- (Véase abajo para la vista actual)
--
CREATE TABLE `v_parent_children` (
`parent_id` int(11)
,`parent_name` varchar(50)
,`parent_email` varchar(100)
,`relationship` varchar(50)
,`student_id` int(11)
,`student_name` varchar(50)
,`grade` varchar(50)
,`section` varchar(50)
,`tdah_type` varchar(50)
,`tdah_confidence` float
);

-- --------------------------------------------------------

--
-- Estructura Stand-in para la vista `v_reports_detallados`
-- (Véase abajo para la vista actual)
--
CREATE TABLE `v_reports_detallados` (
`report_id` int(11)
,`test_type` varchar(50)
,`tipo_tdah` varchar(50)
,`confianza` float
,`created_at` datetime
,`student_id` int(11)
,`student_name` varchar(50)
,`student_tdah_type` varchar(50)
,`student_confidence` float
);

-- --------------------------------------------------------

--
-- Estructura Stand-in para la vista `v_students_tdah`
-- (Véase abajo para la vista actual)
--
CREATE TABLE `v_students_tdah` (
`id` int(11)
,`username` varchar(50)
,`email` varchar(100)
,`grade` varchar(50)
,`section` varchar(50)
,`tdah_type` varchar(50)
,`tdah_confidence` float
,`last_evaluation_date` datetime
,`total_reports` bigint(21)
,`promedio_confianza` double
);

-- --------------------------------------------------------

--
-- Estructura para la vista `v_parent_children`
--
DROP TABLE IF EXISTS `v_parent_children`;

CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `v_parent_children`  AS SELECT `p`.`id` AS `parent_id`, `pu`.`username` AS `parent_name`, `pu`.`email` AS `parent_email`, `ps`.`relationship` AS `relationship`, `s`.`id` AS `student_id`, `su`.`username` AS `student_name`, `s`.`grade` AS `grade`, `s`.`section` AS `section`, `s`.`tdah_type` AS `tdah_type`, `s`.`tdah_confidence` AS `tdah_confidence` FROM ((((`parents` `p` join `users` `pu` on(`p`.`user_id` = `pu`.`id`)) join `parent_student` `ps` on(`p`.`id` = `ps`.`parent_id`)) join `students` `s` on(`ps`.`student_id` = `s`.`id`)) join `users` `su` on(`s`.`user_id` = `su`.`id`)) ;

-- --------------------------------------------------------

--
-- Estructura para la vista `v_reports_detallados`
--
DROP TABLE IF EXISTS `v_reports_detallados`;

CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `v_reports_detallados`  AS SELECT `r`.`id` AS `report_id`, `r`.`test_type` AS `test_type`, `r`.`tipo_tdah` AS `tipo_tdah`, `r`.`confianza` AS `confianza`, `r`.`created_at` AS `created_at`, `s`.`id` AS `student_id`, `u`.`username` AS `student_name`, `s`.`tdah_type` AS `student_tdah_type`, `s`.`tdah_confidence` AS `student_confidence` FROM ((`reports` `r` join `students` `s` on(`r`.`student_id` = `s`.`id`)) join `users` `u` on(`s`.`user_id` = `u`.`id`)) ;

-- --------------------------------------------------------

--
-- Estructura para la vista `v_students_tdah`
--
DROP TABLE IF EXISTS `v_students_tdah`;

CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `v_students_tdah`  AS SELECT `s`.`id` AS `id`, `u`.`username` AS `username`, `u`.`email` AS `email`, `s`.`grade` AS `grade`, `s`.`section` AS `section`, `s`.`tdah_type` AS `tdah_type`, `s`.`tdah_confidence` AS `tdah_confidence`, `s`.`last_evaluation_date` AS `last_evaluation_date`, count(distinct `r`.`id`) AS `total_reports`, avg(`r`.`confianza`) AS `promedio_confianza` FROM ((`students` `s` join `users` `u` on(`s`.`user_id` = `u`.`id`)) left join `reports` `r` on(`s`.`id` = `r`.`student_id`)) GROUP BY `s`.`id` ;

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `activities`
--
ALTER TABLE `activities`
  ADD PRIMARY KEY (`id`),
  ADD KEY `student_id` (`student_id`),
  ADD KEY `teacher_id` (`teacher_id`),
  ADD KEY `created_by` (`created_by`);

--
-- Indices de la tabla `ar_activity_data`
--
ALTER TABLE `ar_activity_data`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `report_id` (`report_id`),
  ADD KEY `idx_activity_type` (`activity_type`);

--
-- Indices de la tabla `audio_test_data`
--
ALTER TABLE `audio_test_data`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `report_id` (`report_id`);

--
-- Indices de la tabla `gonogo_test_data`
--
ALTER TABLE `gonogo_test_data`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `report_id` (`report_id`);

--
-- Indices de la tabla `notifications`
--
ALTER TABLE `notifications`
  ADD PRIMARY KEY (`id`),
  ADD KEY `related_student_id` (`related_student_id`),
  ADD KEY `idx_user_read` (`user_id`,`is_read`),
  ADD KEY `idx_created_at` (`created_at`);

--
-- Indices de la tabla `parents`
--
ALTER TABLE `parents`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `unique_user` (`user_id`);

--
-- Indices de la tabla `parent_student`
--
ALTER TABLE `parent_student`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `unique_parent_student` (`parent_id`,`student_id`),
  ADD KEY `student_id` (`student_id`);

--
-- Indices de la tabla `reports`
--
ALTER TABLE `reports`
  ADD PRIMARY KEY (`id`),
  ADD KEY `teacher_id` (`teacher_id`),
  ADD KEY `session_id` (`session_id`),
  ADD KEY `idx_student_test` (`student_id`,`test_type`),
  ADD KEY `idx_created_at` (`created_at`);

--
-- Indices de la tabla `sessions`
--
ALTER TABLE `sessions`
  ADD PRIMARY KEY (`id`),
  ADD KEY `activity_id` (`activity_id`),
  ADD KEY `idx_student_session` (`student_id`,`created_at`);

--
-- Indices de la tabla `stroop_test_data`
--
ALTER TABLE `stroop_test_data`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `report_id` (`report_id`);

--
-- Indices de la tabla `students`
--
ALTER TABLE `students`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `teacher_id` (`teacher_id`),
  ADD KEY `idx_tdah_type` (`tdah_type`);

--
-- Indices de la tabla `teachers`
--
ALTER TABLE `teachers`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `user_id` (`user_id`);

--
-- Indices de la tabla `teacher_student`
--
ALTER TABLE `teacher_student`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `unique_assignment` (`teacher_id`,`student_id`),
  ADD KEY `student_id` (`student_id`);

--
-- Indices de la tabla `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`),
  ADD UNIQUE KEY `email` (`email`),
  ADD KEY `idx_role` (`role`),
  ADD KEY `idx_email` (`email`);

--
-- Indices de la tabla `vision_test_data`
--
ALTER TABLE `vision_test_data`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `report_id` (`report_id`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `activities`
--
ALTER TABLE `activities`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT de la tabla `ar_activity_data`
--
ALTER TABLE `ar_activity_data`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `audio_test_data`
--
ALTER TABLE `audio_test_data`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `gonogo_test_data`
--
ALTER TABLE `gonogo_test_data`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `notifications`
--
ALTER TABLE `notifications`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT de la tabla `parents`
--
ALTER TABLE `parents`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT de la tabla `parent_student`
--
ALTER TABLE `parent_student`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT de la tabla `reports`
--
ALTER TABLE `reports`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=37;

--
-- AUTO_INCREMENT de la tabla `sessions`
--
ALTER TABLE `sessions`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `stroop_test_data`
--
ALTER TABLE `stroop_test_data`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `students`
--
ALTER TABLE `students`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- AUTO_INCREMENT de la tabla `teachers`
--
ALTER TABLE `teachers`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `teacher_student`
--
ALTER TABLE `teacher_student`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=17;

--
-- AUTO_INCREMENT de la tabla `vision_test_data`
--
ALTER TABLE `vision_test_data`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `activities`
--
ALTER TABLE `activities`
  ADD CONSTRAINT `activities_ibfk_1` FOREIGN KEY (`student_id`) REFERENCES `students` (`id`),
  ADD CONSTRAINT `activities_ibfk_2` FOREIGN KEY (`teacher_id`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `activities_ibfk_3` FOREIGN KEY (`created_by`) REFERENCES `teachers` (`id`) ON DELETE SET NULL;

--
-- Filtros para la tabla `ar_activity_data`
--
ALTER TABLE `ar_activity_data`
  ADD CONSTRAINT `ar_activity_data_ibfk_1` FOREIGN KEY (`report_id`) REFERENCES `reports` (`id`) ON DELETE CASCADE;

--
-- Filtros para la tabla `audio_test_data`
--
ALTER TABLE `audio_test_data`
  ADD CONSTRAINT `audio_test_data_ibfk_1` FOREIGN KEY (`report_id`) REFERENCES `reports` (`id`) ON DELETE CASCADE;

--
-- Filtros para la tabla `gonogo_test_data`
--
ALTER TABLE `gonogo_test_data`
  ADD CONSTRAINT `gonogo_test_data_ibfk_1` FOREIGN KEY (`report_id`) REFERENCES `reports` (`id`) ON DELETE CASCADE;

--
-- Filtros para la tabla `notifications`
--
ALTER TABLE `notifications`
  ADD CONSTRAINT `notifications_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `notifications_ibfk_2` FOREIGN KEY (`related_student_id`) REFERENCES `students` (`id`) ON DELETE SET NULL;

--
-- Filtros para la tabla `parents`
--
ALTER TABLE `parents`
  ADD CONSTRAINT `parents_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Filtros para la tabla `parent_student`
--
ALTER TABLE `parent_student`
  ADD CONSTRAINT `parent_student_ibfk_1` FOREIGN KEY (`parent_id`) REFERENCES `parents` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `parent_student_ibfk_2` FOREIGN KEY (`student_id`) REFERENCES `students` (`id`) ON DELETE CASCADE;

--
-- Filtros para la tabla `reports`
--
ALTER TABLE `reports`
  ADD CONSTRAINT `reports_ibfk_1` FOREIGN KEY (`student_id`) REFERENCES `students` (`id`),
  ADD CONSTRAINT `reports_ibfk_2` FOREIGN KEY (`teacher_id`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `reports_ibfk_3` FOREIGN KEY (`session_id`) REFERENCES `sessions` (`id`);

--
-- Filtros para la tabla `sessions`
--
ALTER TABLE `sessions`
  ADD CONSTRAINT `sessions_ibfk_1` FOREIGN KEY (`student_id`) REFERENCES `students` (`id`),
  ADD CONSTRAINT `sessions_ibfk_2` FOREIGN KEY (`activity_id`) REFERENCES `activities` (`id`);

--
-- Filtros para la tabla `stroop_test_data`
--
ALTER TABLE `stroop_test_data`
  ADD CONSTRAINT `stroop_test_data_ibfk_1` FOREIGN KEY (`report_id`) REFERENCES `reports` (`id`) ON DELETE CASCADE;

--
-- Filtros para la tabla `students`
--
ALTER TABLE `students`
  ADD CONSTRAINT `students_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `students_ibfk_2` FOREIGN KEY (`teacher_id`) REFERENCES `users` (`id`);

--
-- Filtros para la tabla `teachers`
--
ALTER TABLE `teachers`
  ADD CONSTRAINT `teachers_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Filtros para la tabla `teacher_student`
--
ALTER TABLE `teacher_student`
  ADD CONSTRAINT `teacher_student_ibfk_1` FOREIGN KEY (`teacher_id`) REFERENCES `teachers` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `teacher_student_ibfk_2` FOREIGN KEY (`student_id`) REFERENCES `students` (`id`) ON DELETE CASCADE;

--
-- Filtros para la tabla `vision_test_data`
--
ALTER TABLE `vision_test_data`
  ADD CONSTRAINT `vision_test_data_ibfk_1` FOREIGN KEY (`report_id`) REFERENCES `reports` (`id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
