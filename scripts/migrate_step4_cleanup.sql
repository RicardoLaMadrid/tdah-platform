-- ============================================================
-- PASO 4: Eliminar tablas y rol padre — SOLO después de
--         verificar que verify_migration.py reporta 0 huérfanos
-- ============================================================

-- 1. Eliminar usuarios con role='parent' (si quedaron huérfanos)
DELETE FROM users WHERE role = 'parent';

-- 2. Eliminar tablas obsoletas
DROP TABLE IF EXISTS parent_student;
DROP TABLE IF EXISTS parents;

-- 3. Quitar 'parent' del ENUM de users.role
--    IMPORTANTE: esto falla si todavía existen filas con role='parent'.
--    El DELETE del paso 1 garantiza que no quedan.
ALTER TABLE users
  MODIFY COLUMN role ENUM('admin','teacher','student') NOT NULL DEFAULT 'student';

-- 4. Verificar resultado final
SELECT role, COUNT(*) AS total FROM users GROUP BY role;
DESCRIBE users;
