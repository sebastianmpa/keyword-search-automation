"""
Script para probar la consulta de tiendas desde MySQL
====================================================
"""

import sys
from pathlib import Path

# Agregar el directorio raíz del proyecto al Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from db.get_stores import get_stores, get_store_by_id, print_stores

def test_stores_connection():
    """
    Prueba la conexión y consulta de tiendas
    """
    print("🧪 PROBANDO CONEXIÓN A MYSQL Y CONSULTA DE TIENDAS")
    print("=" * 60)
    
    try:
        # Test 1: Obtener todas las tiendas
        print("\n1️⃣ Obteniendo todas las tiendas...")
        print_stores()
        
        # Test 2: Obtener lista programática
        print("\n2️⃣ Obteniendo lista de tiendas programáticamente...")
        stores = get_stores()
        print(f"Resultado: {len(stores)} tiendas obtenidas")
        
        if stores:
            print("Primeras 3 tiendas:")
            for i, store in enumerate(stores[:3]):
                print(f"  {i+1}. ID: {store['id']} - {store['description']}")
        
        # Test 3: Buscar tienda específica
        if stores:
            test_id = stores[0]['id']  # Usar el ID de la primera tienda
            print(f"\n3️⃣ Buscando tienda específica con ID {test_id}...")
            specific_store = get_store_by_id(test_id)
            if specific_store:
                print(f"Encontrada: {specific_store['description']}")
            else:
                print("No encontrada")
        
        print("\n✅ TODAS LAS PRUEBAS COMPLETADAS")
        
    except Exception as e:
        print(f"❌ Error durante las pruebas: {str(e)}")
        print("\nVerifica:")
        print("1. Variables de entorno MySQL en .env")
        print("2. Conexión a la base de datos MySQL")
        print("3. Que la tabla prontoweb.stores exista")

if __name__ == "__main__":
    test_stores_connection()