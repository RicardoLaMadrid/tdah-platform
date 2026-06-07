-- Migración: eliminar rol 'parent' del ENUM de la columna users.role
-- Ejecutar en phpMyAdmin DESPUÉS de verificar que no hay usuarios con role='parent':
--   SELECT COUNT(*) FROM users WHERE role = 'parent';  -- debe devolver 0
--
-- IMPORTANTE: aplicar en mantenimiento (sin usuarios conectados)

ALTER TABLE users
  MODIFY COLUMN role ENUM('admin', 'teacher', 'student') NOT NULL;
