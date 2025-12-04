"""
Script simple para comparar productos que cumplen vs no cumplen el filtro
========================================================================

Filtro: availability = 'available' o 'preorder' AND price > 0
"""

import sys
from pathlib import Path

# Agregar el directorio raíz del proyecto al Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from db.get_all_products import get_available_products_count
from db.get_data_base import get_database

def compare_filtered_vs_total(store_id: int):
    """
    Compara productos que cumplen el filtro vs total de productos
    """
    try:
        # Obtener total de productos de la tienda (sin filtros)
        db = get_database()
        collection = db["Products"]
        total_products = collection.count_documents({"STOREID": store_id})
        
        # Obtener productos que SÍ cumplen el filtro usando tu función
        products_que_cumplen = get_available_products_count(store_id)
        
        # Calcular los que NO cumplen
        products_que_no_cumplen = total_products - products_que_cumplen
        
        # Mostrar resultados
        print(f"TIENDA ID: {store_id}")
        print("=" * 50)
        print(f"Total productos en la tienda: {total_products}")
        print(f"Productos que SÍ cumplen filtro: {products_que_cumplen}")
        print(f"Productos que NO cumplen filtro: {products_que_no_cumplen}")
        
        if total_products > 0:
            porcentaje_cumplen = (products_que_cumplen / total_products) * 100
            porcentaje_no_cumplen = (products_que_no_cumplen / total_products) * 100
            print(f"% que cumplen: {porcentaje_cumplen:.1f}%")
            print(f"% que NO cumplen: {porcentaje_no_cumplen:.1f}%")
        
        print("\nFiltro aplicado:")
        print("- AVAILABILITY = 'available' o 'preorder'")
        print("- PRICE > 0")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    STORE_ID = 5 # Cambiar por tu store_id real
    compare_filtered_vs_total(STORE_ID)