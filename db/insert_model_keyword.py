from db.get_data_base import get_database
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("products_db")

def insert_model_keyword(data: Dict[str, Any]) -> Optional[str]:
    """
    Inserta un documento en la colección 'model_keywords'.
    
    Args:
        data (dict): Diccionario con los datos a insertar.
        
    Returns:
        str: El ID del documento insertado, o None si falla.
    """
    db = get_database()
    collection = db["model_keywords"]
    try:
        result = collection.insert_one(data)
        logger.debug(f"[insert_model_keyword] Inserted document with _id: {result.inserted_id}")
        return str(result.inserted_id)
    except Exception as e:
        logger.error(f"[insert_model_keyword] Error inserting document: {str(e)}")
        return None