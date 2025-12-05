def generate_combinations(part_type: str, brand: str, model: str, sku: str) -> list:
    """
    Genera combinaciones de part_type, brand, model y sku en diferentes órdenes.
    Ejemplo:
        - "spark plug SRM-225"
        - "spark plug ECHO SRM-225"
        - "Echo SRM-225 spark plug"
        - "SRM-225 spark plug Echo"
        - "SRM-225 Echo spark plug"
        - "Echo C534000270"
        - "C534000270 Echo"
    
    Args:
        part_type (str): Tipo de parte
        brand (str): Marca
        model (str): Modelo
        sku (str): SKU
    
    Returns:
        list: Lista de combinaciones posibles
    """
    combinations = [
        f"{part_type} {model}",
        f"{part_type} {brand} {model}",
        f"{brand} {model} {part_type}",
        f"{model} {part_type} {brand}",
        f"{model} {brand} {part_type}",
        f"{brand} {sku}",
        f"{sku} {brand}",
    ]
    return combinations

# Ejemplo de uso
if __name__ == "__main__":
    combos = generate_combinations("spark plug", "Echo", "SRM-225", "C534000270")
    for c in combos:
        print(c)