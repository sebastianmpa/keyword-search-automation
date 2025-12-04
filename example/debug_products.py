"""
Script simple para ver productos filtrados - Versión Debug
==========================================================
"""

import sys
from pathlib import Path

# Agregar el directorio raíz del proyecto al Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

def test_connection():
    """Test básico de conexión a la base de datos"""
    try:
        from db.get_data_base import get_database
        db = get_database()
        
        # Test de conexión
        collections = db.list_collection_names()
        print(f"✅ Conexión exitosa. Colecciones disponibles: {collections}")
        
        # Verificar colección Products
        if "Products" in collections:
            products_collection = db["Products"]
            total_docs = products_collection.count_documents({})
            print(f"📦 Total documentos en Products: {total_docs}")
            
            # Mostrar una muestra
            sample = products_collection.find_one({})
            if sample:
                print(f"📋 Campos disponibles: {list(sample.keys())}")
                print(f"🏪 Store ID de muestra: {sample.get('STOREID', 'N/A')}")
                print(f"🏷️  Availability de muestra: {sample.get('AVAILABILITY', 'N/A')}")
                print(f"💰 Price de muestra: {sample.get('PRICE', 'N/A')}")
            else:
                print("❌ No hay documentos en la colección Products")
        else:
            print("❌ Colección 'Products' no encontrada")
            
        return True
    except Exception as e:
        print(f"❌ Error de conexión: {str(e)}")
        return False

def show_sample_products(store_id: int, limit: int = 10):
    """Muestra una muestra de productos que cumplen los filtros"""
    try:
        from db.get_all_products import get_available_products_batch
        
        print(f"\n🔍 BUSCANDO PRODUCTOS EN TIENDA {store_id}")
        print("Filtros: availability in ['available', 'preorder'] AND price > 0")
        print("-" * 60)
        
        count = 0
        for product in get_available_products_batch(store_id, batch_size=50):
            count += 1
            
            print(f"\n{count}. PRODUCTO ENCONTRADO:")
            print(f"   ID: {product.get('ID', 'N/A')}")
            print(f"   Nombre: {product.get('PRODUCTNAME', 'N/A')[:50]}...")
            print(f"   SKU: {product.get('SKU', 'N/A')}")
            print(f"   Precio: ${product.get('PRICE', 0)}")
            print(f"   Disponibilidad: {product.get('AVAILABILITY', 'N/A')}")
            print(f"   Marca: {product.get('BRAND', 'N/A')}")
            
            if count >= limit:
                print(f"\n⚠️  Mostrando solo {limit} productos. Hay más disponibles...")
                break
                
        if count == 0:
            print("❌ No se encontraron productos que cumplan los filtros")
            print(f"   Verifica que el STORE_ID {store_id} sea correcto")
        else:
            print(f"\n✅ Se encontraron productos que cumplen los filtros")
            
    except Exception as e:
        print(f"❌ Error al buscar productos: {str(e)}")

if __name__ == "__main__":
    print("🧪 SCRIPT DE DEBUG - PRODUCTOS FILTRADOS")
    print("=" * 50)
    
    # Test de conexión primero
    if test_connection():
        # Si la conexión es exitosa, buscar productos
        STORE_ID = 1  # ⚠️ CAMBIAR POR TU STORE_ID REAL
        show_sample_products(STORE_ID, limit=5)
    else:
        print("\n❌ No se pudo conectar a la base de datos")
        print("Verifica:")
        print("1. Variables de entorno en .env")
        print("2. Conexión a MongoDB")
        print("3. Permisos de acceso a la base de datos")