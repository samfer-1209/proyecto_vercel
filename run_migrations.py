#!/usr/bin/env python
"""
Script para ejecutar migraciones de Django.
Se ejecuta automáticamente en Vercel al desplegar.
"""

import os
import sys
import django
from pathlib import Path

# Configurar Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "taskhub.settings")

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

django.setup()

from django.core.management import call_command
from django.db import connection

def run_migrations():
    """Ejecuta todas las migraciones pendientes."""
    print("\n" + "=" * 60)
    print("🔄 Ejecutando migraciones de Django...")
    print("=" * 60)
    
    try:
        # Verificar conexión a la BD
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        print("✓ Conexión a base de datos establecida")
        
        # Ejecutar migraciones
        call_command("migrate", "--noinput")
        print("✅ Migraciones completadas exitosamente")
        return True
        
    except Exception as e:
        print(f"❌ Error durante migraciones: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_migrations()
    sys.exit(0 if success else 1)
