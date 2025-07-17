import pandas as pd
import psycopg2
from psycopg2.extras import execute_batch
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def safe_float_conversion(value):
    """Convierte un valor a float de manera segura, manejando espacios y valores vacíos"""
    if pd.isna(value):
        return None
    if isinstance(value, str):
        value = value.strip()
        if value == '' or value.isspace():
            return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None

def import_excel_to_postgresql(excel_file_path, batch_size=1000):
    """
    Importa un archivo Excel directamente a PostgreSQL por lotes
    
    Args:
        excel_file_path: Ruta al archivo Excel
        batch_size: Número de registros por lote (default: 1000)
    """
    
    # Configuración de la base de datos
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if not DATABASE_URL:
        print("Error: No se encontró DATABASE_URL en las variables de entorno")
        return False
    
    try:
        # Leer el archivo Excel
        print(f"Leyendo archivo Excel: {excel_file_path}")
        df = pd.read_excel(excel_file_path)
        
        # Verificar columnas requeridas
        columnas_requeridas = ['FECHA', 'PLACA']
        for columna in columnas_requeridas:
            if columna not in df.columns:
                print(f"Error: La columna {columna} no existe en el archivo Excel")
                return False
        
        print(f"Total de registros a importar: {len(df)}")
        
        # Conectar a PostgreSQL
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        # Preparar la consulta SQL
        insert_query = """
        INSERT INTO servicio (
            placa, fecha, cliente, marca, modelo, kilometraje,
            filtro_aceite, precio_filtro_aceite, filtro_aire, precio_filtro_aire,
            filtro_petroleo, precio_filtro_petroleo, aceite_motor, precio_aceite_motor,
            otros_1, precio_otros_1, otros_2, precio_otros_2,
            otros_3, precio_otros_3, otros_4, precio_otros_4,
            total, usuario_id
        ) VALUES (
            %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s,
            %s, %s, %s, %s,
            %s, %s, %s, %s,
            %s, %s, %s, %s,
            %s, %s
        )
        """
        
        # Procesar en lotes
        total_imported = 0
        total_errors = 0
        
        for i in range(0, len(df), batch_size):
            batch_df = df.iloc[i:i+batch_size]
            batch_data = []
            
            print(f"Procesando lote {i//batch_size + 1}: registros {i+1} a {min(i+batch_size, len(df))}")
            
            for _, row in batch_df.iterrows():
                try:
                    # Procesar fecha
                    fecha_raw = row['FECHA']
                    if pd.isna(fecha_raw):
                        print(f"Saltando fila {_+1}: fecha vacía")
                        total_errors += 1
                        continue
                    
                    fecha = pd.to_datetime(fecha_raw).date()
                    
                    # Calcular precios
                    precios = [
                        safe_float_conversion(row.get('PRECIO FILTRO ACEITE')),
                        safe_float_conversion(row.get('PRECIO FILTRO AIRE')),
                        safe_float_conversion(row.get('PRECIO FILTRO PETROLEO')),
                        safe_float_conversion(row.get('PRECIO ACEITE MOTOR')),
                        safe_float_conversion(row.get('PRECIO OTROS 1')),
                        safe_float_conversion(row.get('PRECIO OTROS 2')),
                        safe_float_conversion(row.get('PRECIO OTROS 3')),
                        safe_float_conversion(row.get('PRECIO OTROS 4'))
                    ]
                    
                    total = sum(precio for precio in precios if precio is not None)
                    
                    # Preparar datos para inserción
                    record = (
                        str(row['PLACA']) if pd.notna(row['PLACA']) else None,
                        fecha,
                        str(row['CLIENTE']) if pd.notna(row.get('CLIENTE')) else None,
                        str(row['MARCA']) if pd.notna(row.get('MARCA')) else None,
                        str(row['MODELO']) if pd.notna(row.get('MODELO')) else None,
                        safe_float_conversion(row.get('KM')),
                        str(row['FILTRO DE ACEITE']) if pd.notna(row.get('FILTRO DE ACEITE')) else None,
                        safe_float_conversion(row.get('PRECIO FILTRO ACEITE')),
                        str(row['FILTRO DE AIRE']) if pd.notna(row.get('FILTRO DE AIRE')) else None,
                        safe_float_conversion(row.get('PRECIO FILTRO AIRE')),
                        str(row['FILTRO DE PETROLEO']) if pd.notna(row.get('FILTRO DE PETROLEO')) else None,
                        safe_float_conversion(row.get('PRECIO FILTRO PETROLEO')),
                        str(row['ACEITE DE MOTOR']) if pd.notna(row.get('ACEITE DE MOTOR')) else None,
                        safe_float_conversion(row.get('PRECIO ACEITE MOTOR')),
                        str(row['OTROS 1']) if pd.notna(row.get('OTROS 1')) else None,
                        safe_float_conversion(row.get('PRECIO OTROS 1')),
                        str(row['OTROS 2']) if pd.notna(row.get('OTROS 2')) else None,
                        safe_float_conversion(row.get('PRECIO OTROS 2')),
                        str(row['OTROS 3']) if pd.notna(row.get('OTROS 3')) else None,
                        safe_float_conversion(row.get('PRECIO OTROS 3')),
                        str(row['OTROS 4']) if pd.notna(row.get('OTROS 4')) else None,
                        safe_float_conversion(row.get('PRECIO OTROS 4')),
                        total,
                        1  # usuario_id por defecto
                    )
                    
                    batch_data.append(record)
                    
                except Exception as e:
                    print(f"Error en fila {_+1}: {str(e)}")
                    total_errors += 1
                    continue
            
            # Insertar lote
            if batch_data:
                try:
                    execute_batch(cursor, insert_query, batch_data, page_size=batch_size)
                    conn.commit()
                    total_imported += len(batch_data)
                    print(f"Lote insertado exitosamente: {len(batch_data)} registros")
                except Exception as e:
                    print(f"Error al insertar lote: {str(e)}")
                    conn.rollback()
                    total_errors += len(batch_data)
        
        cursor.close()
        conn.close()
        
        print(f"\nImportación completada:")
        print(f"- Registros importados: {total_imported}")
        print(f"- Errores: {total_errors}")
        print(f"- Total procesados: {total_imported + total_errors}")
        
        return True
        
    except Exception as e:
        print(f"Error general: {str(e)}")
        return False

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        print("Uso: python import_batch.py <ruta_archivo_excel>")
        print("Ejemplo: python import_batch.py datos.xlsx")
        sys.exit(1)
    
    excel_file = sys.argv[1]
    
    if not os.path.exists(excel_file):
        print(f"Error: El archivo {excel_file} no existe")
        sys.exit(1)
    
    print("=== Importación por lotes a PostgreSQL ===")
    print(f"Archivo: {excel_file}")
    print("Iniciando importación...\n")
    
    success = import_excel_to_postgresql(excel_file)
    
    if success:
        print("\n✅ Importación completada exitosamente")
    else:
        print("\n❌ La importación falló")
        sys.exit(1)