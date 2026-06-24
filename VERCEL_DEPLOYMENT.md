# 🚀 Despliegue en Vercel - Guía Completa

## ⚠️ Problema Resuelto

**Antes:** SQLite en Vercel → **datos se pierden** en cada despliegue ❌  
**Ahora:** Firestore + BD en memoria en producción → **datos persistentes** ✅

---

## 📋 Cambios Realizados

### 1. **settings.py - Configuración Condicional**
```python
if DEBUG:
    # Desarrollo: SQLite local (con persistencia)
    DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "db.sqlite3"}}
else:
    # Producción (Vercel): BD en memoria (Firestore maneja datos)
    DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}
```

---

## 🔧 Pasos para Desplegar Nuevamente

### **Paso 1: Verificar Variables de Entorno en Vercel**

1. Ve a: https://vercel.com/dashboard
2. Selecciona tu proyecto
3. **Settings** → **Environment Variables**
4. Verifica que estas variables estén presentes:

```
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=tu-dominio.vercel.app
FIREBASE_PROJECT_ID=proyecto-luna-5e33d
FIREBASE_SERVICE_ACCOUNT_JSON={"type":"service_account",...}
```

⚠️ **IMPORTANTE:** `FIREBASE_SERVICE_ACCOUNT_JSON` debe ser el JSON completo del archivo de credenciales.

Para obtener el JSON:
```bash
# En tu máquina local:
cat firebase_service_account.json
```

Copia todo el contenido y pégalo en Vercel como una variable de entorno.

---

### **Paso 2: Hacer un Nuevo Despliegue**

**Opción A: Desde GitHub (Recomendado)**
```bash
# En tu máquina, haz commit de los cambios
git add taskhub/settings.py
git commit -m "fix: usar Firestore en producción"
git push origin main
```
Vercel se desplegará automáticamente.

**Opción B: Desde la CLI de Vercel**
```bash
# Instalar Vercel CLI (si no está instalado)
npm i -g vercel

# Desplegar
vercel --prod
```

---

### **Paso 3: Ejecutar Migraciones en Vercel (si es necesario)**

Si recibiste errores de BD en el despliegue, ejecuta:

```bash
# Conectarse a Vercel
vercel ssh

# Dentro del shell de Vercel:
python manage.py migrate
python manage.py createsuperuser  # Si necesitas un usuario admin nuevo
```

O mejor, añade un script de post-despliegue en `api/index.py`:

```python
# Al inicio del archivo
import os
if os.environ.get("RUNNING_MIGRATIONS") != "true":
    os.environ["RUNNING_MIGRATIONS"] = "true"
    from django.core.management import call_command
    try:
        call_command("migrate", "--noinput")
    except Exception as e:
        print(f"Migration error: {e}")
```

---

### **Paso 4: Verificar que Firestore Funciona**

1. Abre tu aplicación en Vercel: `https://tu-dominio.vercel.app`
2. Intenta registrarte con un nuevo usuario
3. Ve a **Firebase Console** → **Firestore Database** → Colección `usuarios`
4. Deberías ver el nuevo usuario creado en Firestore ✓

---

## 🔍 Troubleshooting

### ❌ **Error: "Cloud Firestore API has not been used"**
**Solución:** 
- Habilita la API en Google Cloud Console
- Ve a: https://console.cloud.google.com/apis/api/firestore.googleapis.com
- Haz clic en **ENABLE**

### ❌ **Error: "Permission denied" al escribir en Firestore**
**Solución:**
- Verifica las reglas de seguridad en Firestore
- Firestore Database → **Rules** → **Edit Rules**
- Usa estas reglas básicas:
```firestore
rules_version = '3';
service cloud.firestore {
  match /databases/{database}/documents {
    match /{document=**} {
      allow read, write: if request.auth != null;
    }
  }
}
```

### ❌ **Los datos no persisten después de desplegar**
**Verificar:**
1. ¿Las variables de entorno están configuradas en Vercel?
2. ¿Firestore está habilitado en Google Cloud?
3. ¿El archivo `firebase_service_account.json` tiene permisos correctos?

---

## 📊 Verificación Final

Después de desplegar, ejecuta estos comandos locales para verificar:

```bash
# Conectar a Firestore y ver usuarios
python manage.py shell
```

```python
from taskhub.firebase import get_collection
usuarios = list(get_collection("usuarios").stream())
print(f"Usuarios en Firestore: {len(usuarios)}")
for doc in usuarios:
    print(f"  - {doc.to_dict()['email']}")
```

---

## 📝 Checklist de Despliegue

- [ ] Variables de entorno configuradas en Vercel
- [ ] `FIREBASE_SERVICE_ACCOUNT_JSON` contiene el JSON completo
- [ ] Cambios en `settings.py` han sido pusheados
- [ ] API de Firestore habilitada en Google Cloud
- [ ] Reglas de seguridad de Firestore configuradas
- [ ] Nuevo despliegue en Vercel completado
- [ ] Usuario de prueba creado exitosamente
- [ ] Datos visibles en Firestore Console

---

## 🎯 Resultado Esperado

✅ **Usuarios se registran** → Se guardan en Firestore  
✅ **Datos persisten** entre despliegues  
✅ **Sin errores de BD** en los logs  
✅ **Aplicación funciona al 100%**

---

**¿Problemas?** Comparte el error exacto que ves en los logs de Vercel.
