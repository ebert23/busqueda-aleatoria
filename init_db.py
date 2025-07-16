#!/usr/bin/env python3
"""
Script para inicializar la base de datos en producción
"""

import os
import sys

def init_database():
    """Inicializa la base de datos y crea el usuario admin por defecto"""
    try:
        from app import app, db, Usuario
        
        print("Iniciando inicialización de base de datos...")
        print(f"DATABASE_URL configurada: {'Sí' if os.getenv('DATABASE_URL') else 'No'}")
        
        with app.app_context():
            # Crear todas las tablas
            print("Creando tablas...")
            db.create_all()
            print("Tablas creadas exitosamente")
            
            # Crear usuario admin por defecto si no existe
            print("Verificando usuario admin...")
            admin = Usuario.query.filter_by(username='admin').first()
            if not admin:
                admin = Usuario(username='admin', nombre='Administrador', es_admin=True)
                admin.set_password('admin123')
                db.session.add(admin)
                db.session.commit()
                print("Usuario admin creado exitosamente")
            else:
                print("Usuario admin ya existe")
            
            print("Base de datos inicializada correctamente")
            return True
            
    except Exception as e:
        print(f"Error al inicializar la base de datos: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = init_database()
    if not success:
        sys.exit(1)