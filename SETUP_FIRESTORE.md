# Configuración de Cloud Firestore API

## Problema

Si ves el error:
```
PermissionDenied: 403 Cloud Firestore API has not been used in project <PROJECT_ID> before or it is disabled.
```

Significa que la API de Cloud Firestore no está habilitada en tu proyecto de Google Cloud.

## Solución

### Opción 1: Habilitar desde Firebase Console (Recomendado)

1. Abre [Firebase Console](https://console.firebase.google.com/).
2. Selecciona tu proyecto: `proyecto-luna-5e33d`.
3. En el menú izquierdo, ve a **Build** → **Firestore Database**.
4. Si ves un botón **Create database**, haz clic.
5. Selecciona:
   - **Start in production mode** (o testing si es desarrollo local)
   - **Location**: Elige una región cercana (ej. `us-central1`)
6. Haz clic en **Create** y espera a que se inicialice.

### Opción 2: Habilitar desde Google Cloud Console

1. Abre [Google Cloud Console](https://console.cloud.google.com/).
2. En el menú superior, selecciona el proyecto `proyecto-luna-5e33d`.
3. Ve a **APIs & Services** → **Library**.
4. Busca `"Cloud Firestore API"`.
5. Haz clic en el resultado y luego en **ENABLE**.
6. Espera a que se active (puede tardar unos segundos a minutos).

### Opción 3: Desde el link del error

El error incluye un link directo. Simplemente haz clic en:
```
https://console.developers.google.com/apis/api/firestore.googleapis.com/overview?project=proyecto-luna-5e33d
```

Y haz clic en **ENABLE**.

## Después de habilitar

1. Espera **1-2 minutos** para que la activación se propague.
2. Recarga la aplicación Django (`http://127.0.0.1:8000/`).
3. Intenta registrarte de nuevo.

## Verificar que Firestore funciona

Una vez habilitado:

```bash
python manage.py shell
```

En el intérprete Python:

```python
from taskhub.firebase import get_collection
usuarios = get_collection("usuarios")
print(list(usuarios.stream()))  # Debería devolver una lista (vacía si no hay usuarios)
```

Si no hay excepción, Firestore está funcionando correctamente.

## Seguridad en producción

En producción, establece reglas de seguridad apropiadas en Firestore:

1. En Firebase Console → **Firestore Database** → **Rules** → **Edit rules**
2. Usa reglas como:

```firestore
rules_version = '3';
service cloud.firestore {
  match /databases/{database}/documents {
    match /usuarios/{userId} {
      allow read: if request.auth.uid == userId;
      allow write: if request.auth.uid == userId;
    }
    match /proyectos/{document=**} {
      allow read: if request.auth != null;
      allow write: if request.auth.uid == resource.data.propietario_id;
    }
  }
}
```

## Troubleshooting

- **"API no se habilita"**: Espera unos minutos y recarga la página.
- **Persiste el error tras habilitar**: Asegúrate de tener permisos de administrador en el proyecto GCP.
- **Error en el deploy en Vercel**: Configura las variables de entorno correctamente (especialmente `FIREBASE_PROJECT_ID` y `FIREBASE_SERVICE_ACCOUNT_JSON`).

## Referencias

- [Cloud Firestore Documentación](https://firebase.google.com/docs/firestore)
- [Enabling APIs in Google Cloud](https://cloud.google.com/docs/apis/getting-started#enabling_apis)
