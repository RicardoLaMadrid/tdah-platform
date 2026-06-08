-- ============================================================
-- PASO 1: Agregar columnas tutor_* a la tabla students
-- Ejecutar DESPUÉS de hacer backup de la BD
-- ============================================================

ALTER TABLE students
  ADD COLUMN tutor_full_name      VARCHAR(200) NULL AFTER emergency_contact_phone,
  ADD COLUMN tutor_relationship   VARCHAR(50)  NULL,
  ADD COLUMN tutor_phone          VARCHAR(20)  NULL,
  ADD COLUMN tutor_email          VARCHAR(120) NULL,
  ADD COLUMN tutor_national_id    VARCHAR(50)  NULL,
  ADD COLUMN tutor_whatsapp_enabled TINYINT(1) DEFAULT 1,
  ADD COLUMN tutor_secondary_name  VARCHAR(200) NULL,
  ADD COLUMN tutor_secondary_phone VARCHAR(20)  NULL;

-- Verificar que las columnas se agregaron correctamente:
DESCRIBE students;
