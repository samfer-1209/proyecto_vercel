# 🚀 Configurar PostgreSQL en Vercel - GUÍA RÁPIDA

## ✅ Tu Información Extraída

```
DB_HOST: ep-spring-cherry-atjoh3xp.c-9.us-east-1.aws.neon.tech
DB_PORT: 5432
DB_NAME: neondb
DB_USER: neondb_owner
DB_PASSWORD: npg_Pr3xVq5QfXcC
DATABASE_URL: postgresql://neondb_owner:npg_Pr3xVq5QfXcC@ep-spring-cherry-atjoh3xp.c-9.us-east-1.aws.neon.tech/neondb?sslmode=require
```

---

## 📋 CONFIGURAR EN VERCEL (2 MINUTOS)

### **Paso 1: Ir a Vercel Dashboard**
1. Abre: https://vercel.com/dashboard
2. Selecciona tu proyecto: `proyecto-vercel-iota`

### **Paso 2: Environment Variables**
1. Ve a **Settings** → **Environment Variables**
2. Añade estas variables (copia y pega exactamente):

#### Variable 1:
```
Name: DATABASE_URL
Value: postgresql://neondb_owner:npg_Pr3xVq5QfXcC@ep-spring-cherry-atjoh3xp.c-9.us-east-1.aws.neon.tech/neondb?sslmode=require
```
Haz clic en **Add**

#### Variable 2:
```
Name: DB_HOST
Value: ep-spring-cherry-atjoh3xp.c-9.us-east-1.aws.neon.tech
```
Haz clic en **Add**

#### Variable 3:
```
Name: DB_PORT
Value: 5432
```
Haz clic en **Add**

#### Variable 4:
```
Name: DB_NAME
Value: neondb
```
Haz clic en **Add**

#### Variable 5:
```
Name: DB_USER
Value: neondb_owner
```
Haz clic en **Add**

#### Variable 6:
```
Name: DB_PASSWORD
Value: npg_Pr3xVq5QfXcC
```
Haz clic en **Add**

#### Variable 7 (si no la tienes):
```
Name: DJANGO_DEBUG
Value: False
```
Haz clic en **Add**

#### Variable 8 (si no la tienes):
```
Name: DJANGO_SECRET_KEY
Value: [tu-clave-secreta-aqui]
```

---

## 🚀 PASO 3: Desplegar

Ya los cambios están en GitHub (push anterior), así que:

1. Ve a: https://vercel.com/dashboard
2. Tu proyecto debería estar desplegándose automáticamente
3. Espera a que termine (aparecerá ✅)

O manualmente:
```bash
vercel --prod
```

---

## 🔄 PASO 4: Ejecutar Migraciones

Una vez desplegado, ejecuta:

```bash
cd /home/samuel/Documentos/trabajo_luna
python run_migrations.py
```

O si quieres verlo en tiempo real:
```bash
vercel logs
```

---

## ✅ VERIFICACIÓN FINAL

Después de 2-3 minutos, abre tu aplicación:

```
https://proyecto-vercel-iota.vercel.app/login/
```

**Debería funcionar sin error de "unable to open database file"** ✓

---

## 🧪 Testear la Conexión (Opcional)

Para verificar que la conexión a PostgreSQL funciona localmente:

```bash
python manage.py shell
```

```python
from django.db import connection
cursor = connection.cursor()
cursor.execute("SELECT 1")
print("✓ Conexión a PostgreSQL exitosa")
```

---

## 📊 Estado de Despliegue

- ✅ Code pushed a GitHub
- ✅ PostgreSQL configurado en Neon
- ⏳ Variables de entorno en Vercel (TÚ LAS AÑADES AHORA)
- ⏳ Despliegue en Vercel (automático)
- ⏳ Migraciones (ejecutar `python run_migrations.py`)

---

## 🆘 Si Algo Falla

1. **Error de conexión a Neon:**
   - Verifica que `DATABASE_URL` está copiado correctamente (sin espacios)

2. **Migraciones fallan:**
   ```bash
   python manage.py migrate --verbosity=3
   ```
   Para ver el error exacto

3. **Variable no reconocida:**
   - Espera 1-2 minutos después de guardar en Vercel
   - Vercel necesita tiempo para propagar cambios

---

**¿Ya añadiste las variables en Vercel?** Dime cuando hayas completado y te ayudaré con las migraciones.
