# 📚 INSTRUCCIONES — Plataforma TDAH

Plataforma web educativa para la detección y seguimiento de TDAH en estudiantes,
desarrollada con Flask + MySQL + OpenCV + OpenAI.

---

## 🛠️ Requisitos del sistema

- Python 3.10 o superior
- MySQL / MariaDB 10.4+
- pip (gestor de paquetes Python)
- Navegador moderno con acceso a cámara (Chrome recomendado)

---

## ⚙️ Instalación

### 1. Clonar / abrir el proyecto

```bash
cd C:\Users\Dogui\Documents\proyecto\tdah-platform
```

### 2. Crear y activar entorno virtual

```bash
python -m venv venv

# Windows:
venv\Scripts\activate

# Linux/Mac:
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

---

## 🔧 Configuración

### 4. Crear archivo `.env` en la raíz del proyecto

```env
# Base de datos (sin contraseña)
DATABASE_URL=mysql+pymysql://root@localhost/tdah_platform

# Clave secreta Flask (cambia esto en producción)
SECRET_KEY=tdah-platform-secret-key-2025

# OpenAI (opcional, para generación de actividades con IA)
OPENAI_API_KEY=sk-tu-clave-aqui
AI_MODEL=gpt-4o-mini
AI_MAX_TOKENS=2000
AI_TEMPERATURE=0.7
```

> **Nota:** Si tu MySQL tiene contraseña, usa:
> `DATABASE_URL=mysql+pymysql://root:tucontraseña@localhost/tdah_platform`

### 5. Verificar conexión a MySQL

```bash
python probar_conexion.py
```

---

## 🗄️ Inicializar base de datos

### 6. Importar la base de datos existente

Abre phpMyAdmin → Importar → selecciona `tdah_platform.sql`

**O** crea la base vacía y déjala que Flask la llene:

```sql
CREATE DATABASE tdah_platform CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

---

## 🚀 Ejecutar el proyecto

```bash
python run.py
```

Abre en el navegador: **http://localhost:5000**

---

## 👤 Credenciales de acceso

| Rol | Usuario | Contraseña |
|-----|---------|------------|
| Administrador | `admin` | `admin123` |
| Profesor | `teacher1` | `teacher123` |
| Estudiante | `carlos` | `student123` |
| Padre/Madre | `maria_madre` | `password123` |

---

## 🏗️ Estructura del proyecto

```
tdah-platform/
│
├── app/
│   ├── __init__.py          # Factory de la app Flask
│   ├── models/              # Modelos SQLAlchemy
│   │   ├── user.py          # Usuario (admin/teacher/student/parent)
│   │   ├── student.py       # Perfil del estudiante + algoritmo TDAH
│   │   ├── activity.py      # Actividades y sesiones
│   │   ├── report.py        # Reportes de tests
│   │   └── parent.py        # Padres y notificaciones
│   │
│   ├── routes/              # Blueprints/Controladores
│   │   ├── auth.py          # Login, logout, perfil
│   │   ├── admin.py         # Gestión de usuarios y asignaciones
│   │   ├── teacher.py       # Dashboard profesor, actividades, reportes
│   │   ├── student.py       # Dashboard estudiante, progreso
│   │   ├── parent.py        # Dashboard padre, notificaciones
│   │   └── ar.py            # Actividades de Realidad Aumentada
│   │
│   ├── services/            # Lógica de negocio
│   │   ├── vision.py        # OpenCV: seguimiento ocular + heatmaps
│   │   ├── audio_api.py     # Whisper: transcripción de lectura
│   │   ├── stroop.py        # Test de Stroop (control inhibitorio)
│   │   ├── gonogo.py        # Test Go/No-Go (impulsividad)
│   │   ├── ai_service.py    # Servicio OpenAI GPT
│   │   ├── ai_generator.py  # Generador de actividades con IA
│   │   └── ar_integration.py# Configuración de experiencias AR
│   │
│   ├── templates/           # Plantillas Jinja2
│   │   ├── base.html        # Base con navbar
│   │   ├── auth/            # Login, perfil
│   │   ├── admin/           # Panel administrador
│   │   ├── teacher/         # Panel profesor
│   │   ├── student/         # Panel estudiante + tests
│   │   ├── parent/          # Panel padre
│   │   ├── ar/              # Actividades AR
│   │   └── errors/          # Páginas 404, 500
│   │
│   └── static/
│       ├── css/style.css    # Estilos principales
│       ├── js/main.js       # JavaScript utilitario
│       └── ar/viewer.html   # Visor AR con A-Frame
│
├── config.py                # Configuraciones por entorno
├── run.py                   # Punto de entrada
├── requirements.txt         # Dependencias Python
├── tdah_platform.sql        # Dump de la base de datos
└── .env                     # Variables de entorno (NO subir a Git)
```

---

## 🧠 Funcionalidades principales

### Tests cognitivos (estudiante)
| Test | Mide | Tecnología |
|------|------|-----------|
| Visión | Seguimiento ocular, atención visual | OpenCV + Haar Cascades |
| Audio | Lectura en voz alta, fluidez | SpeechRecognition + pydub |
| Stroop | Control inhibitorio | JavaScript puro |
| Go/No-Go | Impulsividad, tiempo reacción | JavaScript puro |

### Algoritmo de clasificación TDAH
- Combina resultados de los 4 tests usando **consenso ponderado**
- Tipos: `typical`, `inatento`, `hiperactivo`, `combinado`
- Requiere mínimo 2 tests con confianza ≥40%
- Se actualiza automáticamente tras cada test

### Actividades AR
- **Caza de Objetos**: Atención selectiva con objetos en cámara
- **Secuencia de Luces**: Memoria de trabajo (Simon dice)
- **Respiración Guiada**: Autorregulación emocional (técnica 4-4-4)

---

## 🔄 Comandos útiles

```bash
# Ver rutas disponibles
python verificar_rutas.py

# Probar conexión MySQL
python probar_conexion.py

# Probar servicio de IA
python test_ia.py

# Diagnóstico de usuarios
python diagnostico_usuarios.py
```

---

## 🚨 Solución de problemas comunes

### Error: "No se detectó rostro" en test de visión
- Asegúrate de tener buena iluminación
- Usa Chrome (mejor soporte WebRTC)
- Permite el acceso a la cámara cuando el navegador lo solicite

### Error de conexión a MySQL
```
OperationalError: Can't connect to MySQL server
```
- Verifica que MySQL esté corriendo
- Comprueba usuario/contraseña en `.env`
- Ejecuta `python probar_conexion.py`

### Tipo TDAH no se asigna
- El estudiante necesita completar al menos 2 tests
- La confianza mínima es 40%
- Verifica en admin → usuarios → estudiante

### Error con OpenAI
- Verifica que `OPENAI_API_KEY` esté en `.env`
- Las actividades con IA funcionan en modo "fallback" sin API key

---

## 📦 Dependencias principales

```
Flask==3.0.0
Flask-SQLAlchemy==3.1.1
Flask-Login==0.6.3
PyMySQL==1.1.0
opencv-python==4.10.0.84
openai-whisper
openai
SpeechRecognition
pydub
PyJWT==2.8.0
python-dotenv==1.0.0
```

---

## 🎓 Contexto académico

Este proyecto es la tesis de titulación de **Ricardo**, desarrollado como plataforma
educativa para apoyo a estudiantes con TDAH, integrando:
- Visión por computadora para análisis de atención
- Inteligencia Artificial para personalización de actividades  
- Realidad Aumentada para actividades interactivas
- Sistema de seguimiento para profesores y padres

---

*Desarrollado con Flask + SQLAlchemy + OpenCV + OpenAI + Bootstrap 5*
