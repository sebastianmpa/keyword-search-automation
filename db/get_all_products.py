from db.get_data_base import get_database
import logging
from typing import Generator, Optional, Dict, Any
from pymongo.cursor import Cursor

logger = logging.getLogger("products_db")

def get_product_by_id(store_id: int, product_id: int) -> Optional[dict]:
    """
    Obtiene un producto específico por su ID y store_id
    """
    db = get_database()
    collection = db["Products"]
    query = {"ID": product_id, "STOREID": store_id}
    logger.debug(f"[get_product_by_id] Executing query: {query}")
    data = collection.find_one(query)
    if data:
        logger.debug(f"[get_product_by_id] 1 record(s) found: {data}")
    else:
        logger.debug("[get_product_by_id] No records found")
    return data


def get_available_products_batch(
    store_id: int, 
    batch_size: int = 1000,
    projection: Optional[Dict[str, int]] = None
) -> Generator[Dict[str, Any], None, None]:
    """
    Obtiene productos disponibles de una tienda específica en lotes optimizados.
    
    Filtros aplicados:
    - STOREID = store_id
    - AVAILABILITY in ['available', 'preorder'] 
    - PRICE > 0
    
    Args:
        store_id (int): ID de la tienda
        batch_size (int): Tamaño del lote para optimizar memoria (default: 1000)
        projection (dict, optional): Campos específicos a retornar (None = todos los campos)
    
    Yields:
        dict: Producto que cumple con los criterios
    """
    db = get_database()
    collection = db["Products"]
    
    # Query optimizada con índices compuestos
    query = {
        "STOREID": store_id,
        "AVAILABILITY": {"$in": ["available", "preorder"]},
        "PRICE": {"$gt": 0}
    }
    
    # Proyección por defecto si no se especifica
    if projection is None:
        projection = {
            "_id": 1,
            "ID": 1,
            "STOREID": 1,
            "SKU": 1,
            "MPN": 1,
            "PRODUCTNAME": 1,
            "PRICE": 1,
            "SALE_PRICE": 1,
            "RETAIL_PRICE": 1,
            "COST_PRICE": 1,
            "INVENTORY_LEVEL": 1,
            "AVAILABILITY": 1,
            "BRAND": 1,
            "BRAND_ID": 1,
            "CATEGORIES": 1,
            "UPC": 1,
            "CUSTOM_URL": 1,
            "PAGE_TITLE": 1,
            "MARKETPLACE_PRICE": 1,
            "MARKETPLACE_MARGIN": 1,
            "MARKETPLACE": 1,
            "createdAt": 1,
            "updatedAt": 1
        }
    
    logger.info(f"[get_available_products_batch] Starting batch processing for store_id: {store_id}")
    logger.debug(f"[get_available_products_batch] Query: {query}")
    logger.debug(f"[get_available_products_batch] Batch size: {batch_size}")
    
    try:
        # Cursor optimizado con batch_size
        cursor: Cursor = collection.find(
            query, 
            projection
        ).batch_size(batch_size)
        
        # Agregar hint para usar índices si están disponibles
        # cursor = cursor.hint([("STOREID", 1), ("AVAILABILITY", 1), ("PRICE", 1)])
        
        total_processed = 0
        batch_count = 0
        
        for document in cursor:
            total_processed += 1
            
            # Log cada 1000 documentos procesados
            if total_processed % 1000 == 0:
                logger.info(f"[get_available_products_batch] Processed {total_processed} products")
            
            yield document
            
        logger.info(f"[get_available_products_batch] Completed. Total products processed: {total_processed}")
        
    except Exception as e:
        logger.error(f"[get_available_products_batch] Error processing batch for store_id {store_id}: {str(e)}")
        raise


def get_available_products_count(store_id: int) -> int:
    """
    Obtiene el conteo total de productos disponibles para una tienda específica.
    Útil para estimar el progreso del procesamiento.
    
    Args:
        store_id (int): ID de la tienda
        
    Returns:
        int: Número total de productos que cumplen los criterios
    """
    db = get_database()
    collection = db["Products"]
    
    query = {
        "STOREID": store_id,
        "AVAILABILITY": {"$in": ["available", "preorder"]},
        "PRICE": {"$gt": 0}
    }
    
    logger.debug(f"[get_available_products_count] Counting query: {query}")
    
    try:
        count = collection.count_documents(query)
        logger.info(f"[get_available_products_count] Found {count} available products for store_id: {store_id}")
        return count
    except Exception as e:
        logger.error(f"[get_available_products_count] Error counting products for store_id {store_id}: {str(e)}")
        raise


def get_available_products_list(
    store_id: int, 
    limit: Optional[int] = None,
    projection: Optional[Dict[str, int]] = None
) -> list:
    """
    Obtiene una lista completa de productos disponibles (usar con precaución en grandes datasets).
    Para datasets grandes, preferir get_available_products_batch().
    
    Args:
        store_id (int): ID de la tienda
        limit (int, optional): Límite máximo de productos a retornar
        projection (dict, optional): Campos específicos a retornar
        
    Returns:
        list: Lista de productos que cumplen los criterios
    """
    products = []
    
    logger.warning(f"[get_available_products_list] Loading all products into memory for store_id: {store_id}")
    
    try:
        for product in get_available_products_batch(store_id, projection=projection):
            products.append(product)
            
            if limit and len(products) >= limit:
                logger.info(f"[get_available_products_list] Reached limit of {limit} products")
                break
                
        logger.info(f"[get_available_products_list] Loaded {len(products)} products into memory")
        return products
        
    except Exception as e:
        logger.error(f"[get_available_products_list] Error loading products for store_id {store_id}: {str(e)}")
        raise


# Ejemplo de uso optimizado:
"""
# Para procesar en lotes (recomendado para grandes datasets):
for product in get_available_products_batch(store_id=123):
    # Procesar cada producto individualmente
    process_product(product)

# Para obtener conteo total:
total_products = get_available_products_count(store_id=123)
print(f"Total productos disponibles: {total_products}")

# Para cargar todo en memoria (solo datasets pequeños):
all_products = get_available_products_list(store_id=123, limit=5000)
"""
