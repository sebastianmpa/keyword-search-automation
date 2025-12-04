from mysql_connection import get_mysql_connection
from mysql.connector import Error
import logging
from typing import List, Dict, Optional

logger = logging.getLogger("stores_db")

def get_stores() -> List[Dict[str, any]]:
    """
    Obtiene todas las tiendas desde MySQL.
    
    Query: SELECT id, DESCRIPTION FROM prontoweb.stores
    
    Returns:
        List[Dict]: Lista de diccionarios con id y descripción de las tiendas
    """
    stores = []
    connection = None
    
    try:
        logger.info("[get_stores] Iniciando consulta de tiendas desde MySQL")
        
        connection = get_mysql_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Query específica solicitada
        query = "SELECT id, DESCRIPTION FROM prontoweb.stores"
        logger.debug(f"[get_stores] Ejecutando query: {query}")
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        # Convertir a formato más limpio
        for row in results:
            store = {
                "id": row["id"],
                "description": row["DESCRIPTION"]
            }
            stores.append(store)
        
        logger.info(f"[get_stores] Se encontraron {len(stores)} tiendas")
        
        return stores
        
    except Error as e:
        logger.error(f"[get_stores] Error en consulta MySQL: {str(e)}")
        raise
        
    finally:
        if connection and connection.is_connected():
            connection.close()
            logger.debug("[get_stores] Conexión MySQL cerrada")

def get_store_by_id(store_id: int) -> Optional[Dict[str, any]]:
    """
    Obtiene una tienda específica por su ID desde MySQL.
    
    Args:
        store_id (int): ID de la tienda a buscar
        
    Returns:
        Optional[Dict]: Diccionario con id y descripción de la tienda o None si no existe
    """
    connection = None
    
    try:
        logger.debug(f"[get_store_by_id] Buscando tienda con ID: {store_id}")
        
        connection = get_mysql_connection()
        cursor = connection.cursor(dictionary=True)
        
        query = "SELECT id, DESCRIPTION FROM prontoweb.stores WHERE id = %s"
        logger.debug(f"[get_store_by_id] Ejecutando query: {query} con parámetro: {store_id}")
        
        cursor.execute(query, (store_id,))
        result = cursor.fetchone()
        
        if result:
            store = {
                "id": result["id"],
                "description": result["DESCRIPTION"]
            }
            logger.debug(f"[get_store_by_id] Tienda encontrada: {store}")
            return store
        else:
            logger.warning(f"[get_store_by_id] No se encontró tienda con ID: {store_id}")
            return None
            
    except Error as e:
        logger.error(f"[get_store_by_id] Error en consulta MySQL: {str(e)}")
        raise
        
    finally:
        if connection and connection.is_connected():
            connection.close()
            logger.debug("[get_store_by_id] Conexión MySQL cerrada")

def print_stores():
    """
    Función auxiliar para mostrar las tiendas en formato legible.
    """
    try:
        stores = get_stores()
        
        print("🏪 TIENDAS DISPONIBLES")
        print("=" * 50)
        
        if not stores:
            print("❌ No se encontraron tiendas")
            return
            
        for store in stores:
            print(f"ID: {store['id']:3d} | {store['description']}")
            
        print(f"\n📊 Total: {len(stores)} tiendas")
        
    except Exception as e:
        print(f"❌ Error al obtener tiendas: {str(e)}")

# Ejemplo de uso
if __name__ == "__main__":
    # Configurar logging
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    try:
        # Mostrar todas las tiendas
        print_stores()
        
        # Ejemplo de búsqueda por ID específico
        store_id = 1  # Cambiar por el ID que quieras buscar
        store = get_store_by_id(store_id)
        if store:
            print(f"\n🔍 Tienda específica (ID {store_id}): {store['description']}")
        
    except Exception as e:
        print(f"Error general: {str(e)}")
