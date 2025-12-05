import requests
import json
from urllib.parse import quote

API_BASE_URL = "https://api-product-parts.prontomowers.app"

def consume_where_used(sku: str, brand_name: str):
    """
    Consume la API de where-used para obtener información de dónde se usa un SKU específico.
    
    Args:
        sku (str): SKU del producto
        brand_name (str): Nombre de la marca
        
    Returns:
        Dict: Respuesta de la API o error
    """
    url = f"{API_BASE_URL}/api/product/v0/where-used"
    
    # Parámetros de la consulta
    params = {
        "sku": sku,
        "brand_name": brand_name
    }
    
    print(f"🔹 Calling API at URL: {url}")
    print(f"🔹 Parameters: SKU={sku}, Brand={brand_name}")

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        result = response.json()
        
        return result

    except requests.exceptions.RequestException as e:
        return {"error": str(e)}
    except json.JSONDecodeError as e:
        return {"error": f"Invalid JSON response: {str(e)}"}

if __name__ == "__main__":
    # Ejemplo de uso
    test_sku = "C534000270"
    test_brand = "Echo / Shindaiwa"
    
    result = consume_where_used(test_sku, test_brand)
    print(result)