# Deploy a Railway — Instrucciones paso a paso

## Pre-requisitos (5 min)

1. Crear cuenta en https://railway.app (Sign in with GitHub)
2. Asegurarte de que el proyecto está en GitHub:
   ```
   git remote -v   # verificar que ya tiene remote
   git push origin master
   ```

---

## Paso 1: Crear proyecto en Railway

1. En **railway.app** → clic en **"New Project"**
2. Elegir **"Deploy from GitHub repo"**
3. Seleccionar el repo `tdah-platform`
4. Branch: **`master`**
5. Railway detecta Python automáticamente y empieza el build
6. Mientras tanto, configurar la base de datos (Paso 2)

---

## Paso 2: Agregar MySQL

1. En tu proyecto Railway → clic en **"+ New"**
2. Elegir **"Database"** → **"Add MySQL"**
3. Railway crea la base de datos y genera `DATABASE_URL` automáticamente
4. Esa variable queda disponible para tu app web sin configuración extra

---

## Paso 3: Variables de entorno

En tu servicio web → tab **"Variables"** → agregar:

### Obligatorias

| Variable | Valor |
|----------|-------|
| `SECRET_KEY` | Generar una clave aleatoria de 50+ caracteres |
| `ANTHROPIC_API_KEY` | Tu API key de Anthropic (console.anthropic.com) |

### Opcionales de IA (estos son los defaults — solo agregalas si querés cambiar el valor)

| Variable | Default | Descripción |
|----------|---------|-------------|
| `AI_MODEL` | `claude-haiku-4-5` | Modelo de Claude a usar |
| `AI_MAX_TOKENS` | `1500` | Tokens máximos por respuesta |
| `AI_TEMPERATURE` | `0.3` | Creatividad (0=determinista, 1=creativo) |

Para generar SECRET_KEY, podés usar:
```python
python -c "import secrets; print(secrets.token_hex(32))"
```

### Opcionales (solo si vas a usar esas funciones)

| Variable | Valor |
|----------|-------|
| `GOOGLE_CLIENT_ID` | Client ID de Google Cloud Console |
| `GOOGLE_CLIENT_SECRET` | Client Secret de Google Cloud Console |
| `OAUTH_REDIRECT_URI` | `https://TU-APP.up.railway.app/oauth/google/callback` |
| `TWILIO_ACCOUNT_SID` | SID de tu cuenta Twilio |
| `TWILIO_AUTH_TOKEN` | Auth token de Twilio |
| `TWILIO_WHATSAPP_FROM` | Número Twilio WhatsApp (ej: `whatsapp:+14155238886`) |
| `WHATSAPP_ENABLED` | `True` o `False` |

> **Nota:** `DATABASE_URL` NO la configures manualmente — Railway la inyecta
> automáticamente cuando agregas el plugin de MySQL.

---

## Paso 4: Obtener URL pública

1. Tu servicio web → tab **"Settings"** → sección **"Networking"**
2. Clic en **"Generate Domain"**
3. Railway te asigna una URL: `https://tdah-platform-production.up.railway.app`

Guardá esa URL — la necesitás para configurar OAuth y para compartir en la defensa.

---

## Paso 5: Verificar deploy

1. Abrir la URL en el navegador
2. Debe cargar la pantalla de login
3. Credenciales del seed demo:
   - Admin: `admin` / `admin123`
   - Docente: `prof_maria` / `prof123`
   - Estudiante: `estudiante01` / `est123`
4. Verificar que el dashboard carga correctamente
5. Hacer un test rápido de alguna actividad

---

## Si algo falla

1. En Railway → tab **"Deployments"** → clic en el último deploy → ver **"Build Logs"** y **"Deploy Logs"**

2. Errores comunes:

| Error | Causa | Solución |
|-------|-------|----------|
| `ModuleNotFoundError` | Paquete faltante en requirements.txt | Agregar el paquete y redeploy |
| `OperationalError: Can't connect to MySQL` | DATABASE_URL no configurada o MySQL no agregado | Verificar que el plugin MySQL está conectado al servicio |
| `TemplateNotFound: output.css` | output.css no está en el repo | `git add app/static/css/output.css && git push` |
| Página en blanco | Error de JS | Abrir consola del navegador (F12) |
| `SECRET_KEY` warning en logs | Variable no configurada | Agregar SECRET_KEY en variables de Railway |

---

## Configurar Google OAuth (opcional)

Si querés que funcione el login con Google en la URL de Railway:

1. Ir a [Google Cloud Console](https://console.cloud.google.com) → APIs & Services → Credentials
2. Editar tu OAuth 2.0 Client ID
3. En "Authorized redirect URIs" agregar:
   ```
   https://TU-APP.up.railway.app/oauth/google/callback
   ```
4. Guardar
5. En Railway → Variables → agregar `OAUTH_REDIRECT_URI` con esa URL completa

---

## Actualizar la app después del deploy inicial

Cada `git push origin master` dispara un **re-deploy automático**:
```bash
# Flujo normal de trabajo
git add .
git commit -m "feat: nueva funcionalidad"
git push origin master
# Railway detecta el push y redeploya en ~2 minutos
```

---

## Costos estimados

- Plan gratuito: **$5 USD/mes de crédito**
- App Flask + MySQL con tráfico bajo (defensa, demos): **~$3-4/mes**
- Si supera $5 en un mes, la app se pausa hasta el siguiente mes (los datos no se borran)
- Para la defensa y período de evaluación está dentro del crédito gratuito

---

## Limitaciones conocidas

| Limitación | Descripción | Impacto en defensa |
|------------|-------------|-------------------|
| **Uploads no persistentes** | Archivos subidos (heatmaps, audios) se pierden en cada deploy | Bajo — se regeneran al hacer nuevos tests |
| **WhatsApp** | Requiere cuenta Twilio verificada con número real | No disponible sin configuración |
| **OAuth Google** | Requiere agregar URL de Railway en Google Cloud Console | Solo afecta login con Google, el login normal funciona |
| **Cámara AR** | Requiere HTTPS — Railway provee HTTPS automáticamente | Sin impacto, funciona |
