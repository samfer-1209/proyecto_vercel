# 🔧 Solución: Cambiar a PostgreSQL en Vercel

## 🚨 Problema Identificado
- SQLite no funciona en Vercel (entorno serverless sin persistencia)
- Error: `unable to open database file`
- Cada solicitud HTTP es una instancia nueva sin acceso a archivos

## ✅ Solución: PostgreSQL en la Nube

Usaremos **Neon** (PostgreSQL gratuito y confiable):

---

## 📋 PASOS PARA CONFIGURAR

### **PASO 1: Crear BD en Neon (5 minutos)**

1. Ve a: https://console.neon.tech/
2. Regístrate/inicia sesión con GitHub
3. Crea un nuevo proyecto
4. Verás la **connection string**, cópiala:
   ```
   postgresql://user:password@host.neon.tech/database?sslmode=require
   ```

### **PASO 2: Configurar Variables en Vercel**

1. Ve a: https://vercel.com/dashboard → Tu Proyecto
2. **Settings** → **Environment Variables**
3. Añade estas variables (basadas en la connection string de Neon):

```
DATABASE_URL=postgresql://user:password@host.neon.tech/database?sslmode=require
DB_HOST=host.neon.tech
DB_PORT=5432
DB_NAME=database
DB_USER=user
DB_PASSWORD=password
DJANGO_DEBUG=False
DJANGO_SECRET_KEY=tu-clave-secreta-larga-aqui
DJANGO_ALLOWED_HOSTS=tu-dominio.vercel.app
FIREBASE_PROJECT_ID=proyecto-luna-5e33d
FIREBASE_SERVICE_ACCOUNT_JSON={"type":"service_account",...}
```

**IMPORTANTE:** Reemplaza `user`, `password`, `host`, `database` con los valores de Neon.

### **PASO 3: Actualizar requirements.txt (YA HECHO)**

✅ Incluye `psycopg2-binary` para PostgreSQL

### **PASO 4: Desplegar en Vercel**

```bash
# Commit de cambios
git add taskhub/settings.py requirements.txt run_migrations.py
git commit -m "feat: usar PostgreSQL en producción (Vercel)"
git push origin main
```

Vercel se desplegará automáticamente. **Espera a que termine** (~2-3 minutos).

### **PASO 5: Ejecutar Migraciones**

Una vez desplegado, ejecuta las migraciones en Vercel:

**Opción A: Manual (más rápido ahora)**
```bash
vercel env pull  # Descarga variables de Vercel
python run_migrations.py
```

**Opción B: Automático (próximas veces)**
Modifica `api/index.py` para ejecutar migraciones al iniciar:

```python
# Al inicio de api/index.py, ANTES de importar Django views
import os
import sys

# Ejecutar migraciones al iniciar (solo en producción)
if os.environ.get("DJANGO_DEBUG") == "False" and os.environ.get("MIGRATIONS_RAN") != "true":
    os.environ["MIGRATIONS_RAN"] = "true"
    try:
        from django.core.management import call_command
        call_command("migrate", "--noinput")
        print("✓ Migraciones ejecutadas")
    except Exception as e:
        print(f"⚠️  Error en migraciones: {e}")

# ... resto del archivo
```

---

## ✅ Checklist Final

- [ ] Neon PostgreSQL creado y connection string copiada
- [ ] Variables de entorno configuradas en Vercel
- [ ] `psycopg2-binary` en requirements.txt
- [ ] Cambios en `settings.py` para PostgreSQL
- [ ] Nuevo despliegue en Vercel completado
- [ ] Migraciones ejecutadas (sin errores)
- [ ] Puedes iniciar sesión sin error de BD

---

## 🧪 Verificar que Funciona

Después de desplegar:

1. **Abre la aplicación en Vercel:**
   ```
   https://tu-dominio.vercel.app/login/
   ```

2. **Intenta iniciar sesión** con un usuario existente:
   - Usuario: `samuel_11`
   - (Primero necesitarás obtener la contraseña o crear un nuevo usuario)

3. **Verifica los logs de Vercel:**
   ```bash
   vercel logs
   ```
   Debería decir: `✓ Migraciones ejecutadas` sin errores

4. **Verifica que Firestore funciona:**
   - Firebase Console → Firestore Database
   - Deberías ver la colección `usuarios`

---

## 🆘 Troubleshooting

### ❌ **Error: "password authentication failed"**
- Verifica que `DB_PASSWORD` es correcto en Vercel
- Neon credentials pueden cambiar, obtén la connection string de nuevo

### ❌ **Error: "connection refused" en Neon**
- Asegúrate que el proyecto de Neon está activo
- Verifica que la connection string tiene `sslmode=require`

### ❌ **Las migraciones fallan**
```bash
# Ejecuta localmente para ver el error exacto:
python manage.py migrate
```

### ❌ **La aplicación aún dice "unable to open database file"**
- Limpia el cache de Vercel: `vercel --prod --no-cache`
- Verifica que `DJANGO_DEBUG=False` en Vercel

---

## 📊 Comparativa: SQLite vs PostgreSQL

| Aspecto | SQLite | PostgreSQL (Neon) |
|--------|--------|---|
| **Persistencia en Vercel** | ❌ No | ✅ Sí |
| **Costo** | Gratis (no funciona) | Gratis con límites generosos |
| **Escalabilidad** | Muy limitada | Excelente |
| **Configuración** | Sencilla | Media |
| **Para producción** | ❌ No recomendado | ✅ Recomendado |

---

## 🎯 Siguiente: Desplegar

**Ya está todo configurado. Solo necesitas:**

1. Asegurar que las variables de entorno en Vercel sean correctas
2. Hacer `git push`
3. Esperar a que Vercel despliegue
4. Ejecutar: `python run_migrations.py`
5. ¡Listo!

**¿Problemas?** Comparte el error exacto que ves. 🚀
