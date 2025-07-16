#!/usr/bin/env python3
"""
Script para inicializar la base de datos en producción
"""

from app import app, db, Usuario
import os

def init_database():
    """Inicializa la base de datos y crea el usuario admin por defecto"""
    with app.app_context():
        # Crear todas las tablas
        db.create_all()
        
        # Crear usuario admin por defecto si no existe
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

if __name__ == '__main__':
    init_database()