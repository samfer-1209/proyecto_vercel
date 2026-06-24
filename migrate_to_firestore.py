#!/usr/bin/env python
"""
Script para migrar datos de SQLite a Firestore.
Uso: python migrate_to_firestore.py
"""

import os
import django
from datetime import datetime, timezone

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "taskhub.settings")
django.setup()

from django.contrib.auth.models import User
from taskhub.firebase import get_collection, db
from google.api_core.exceptions import PermissionDenied, ServiceUnavailable


def migrate_usuarios():
    """Migra usuarios de Django/SQLite a Firestore."""
    print("\n🔄 Migrando USUARIOS...")
    
    if not db:
        print("❌ Firestore no está configurado. Verifica SETUP_FIRESTORE.md")
        return False
    
    usuarios_collection = get_collection("usuarios")
    migrated = 0
    
    try:
        for user in User.objects.all():
            doc_id = str(user.id)
            
            payload = {
                "uid": doc_id,
                "email": user.email,
                "nombre": user.first_name or user.username,
                "apellido": user.last_name or "",
                "rol": "Administrador" if user.is_staff else "Usuario",
                "fecha_creacion": datetime.now(timezone.utc),
                "username": user.username,
                "is_active": user.is_active,
            }
            
            usuarios_collection.document(doc_id).set(payload)
            print(f"  ✓ {user.username} ({user.email})")
            migrated += 1
    
    except (PermissionDenied, ServiceUnavailable) as e:
        print(f"❌ Error de Firestore: {e}")
        print("   Asegúrate de que la API está habilitada en Firebase Console")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False
    
    print(f"\n✅ {migrated} usuario(s) migrado(s) exitosamente")
    return True


def verify_migration():
    """Verifica que los datos se migraron correctamente."""
    print("\n🔍 Verificando migración...")
    
    try:
        usuarios = list(get_collection("usuarios").stream())
        print(f"✓ {len(usuarios)} usuario(s) en Firestore:")
        
        for doc in usuarios:
            data = doc.to_dict()
            print(f"  - {data.get('username')} ({data.get('email')})")
        
        return True
    except Exception as e:
        print(f"❌ Error al verificar: {e}")
        return False


def main():
    print("=" * 50)
    print("MIGRACIÓN DE SQLite A FIRESTORE")
    print("=" * 50)
    
    # Contar datos en SQLite
    user_count = User.objects.count()
    print(f"\n📊 Datos en SQLite:")
    print(f"   - Usuarios: {user_count}")
    
    if user_count == 0:
        print("\n⚠️  No hay datos para migrar en SQLite")
        return
    
    # Confirmar migración
    response = input("\n¿Deseas proceder con la migración? (s/n): ").strip().lower()
    if response != 's':
        print("Migración cancelada.")
        return
    
    # Ejecutar migración
    if migrate_usuarios():
        verify_migration()
        print("\n✨ ¡Migración completada!")
    else:
        print("\n⚠️  La migración falló. Revisa los errores arriba.")


if __name__ == "__main__":
    main()
