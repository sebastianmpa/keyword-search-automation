import requests
import os
import json
import pandas as pd
from datetime import datetime

API_BASE_URL = "http://127.0.0.1:8001"

SYSTEM_CONTEXT = "Act like a Senior SEO Analyst for a retailer company who sells replacement parts for Briggs & Stratton Angines. We also sell the engines themselves. We select the keywords based on Monthly search volume, Business goals and user intent."
BUSINESS_GOAL = "Sell replacement parts for Briggs & Stratton small engines"
USER_INTENT = "Buy a replacement part for his Briggs & Stratton engine"

def consume_generate_keywords(keyword_volume, destination_folder):
    url = f"{API_BASE_URL}/generate-keywords"
    print(f"🔹 Calling API at URL: {url}")

    try:
        if isinstance(keyword_volume, str):
            keyword_volume = json.loads(keyword_volume)

        payload = {
            "system_context": SYSTEM_CONTEXT,
            "business_goal": BUSINESS_GOAL,
            "user_intent": USER_INTENT,
            "keyword_volume": keyword_volume
        }
        print(payload)
        
        response = requests.post(url, json=payload)
        response.raise_for_status()
        result = response.json()

        # Crear DataFrame con los nuevos datos
        new_data = pd.DataFrame({
            'Main_keyword': [result['Main_keyword']],
            'SecKw_1': [result['SecKw_1']],
            'SecKw_2': [result['SecKw_2']],
            'SecKw_3': [result['SecKw_3']],
            'Other_keywords': [', '.join(result['Other_keywords'])]
        })

        # Ruta del archivo de salida (siempre el mismo)
        output_path = os.path.join(destination_folder, "keywords.xlsx")

        # 🔹 Verificar si el archivo ya existe
        if os.path.exists(output_path):
            existing_data = pd.read_excel(output_path)  # Leer el archivo existente
            combined_data = pd.concat([existing_data, new_data], ignore_index=True)  # Combinar datos
        else:
            combined_data = new_data  # Si no existe, solo usar los nuevos datos

        # Guardar el archivo actualizado
        combined_data.to_excel(output_path, index=False)

        print(f"✅ Datos agregados a: {output_path}")
        return result

    except json.JSONDecodeError:
        return {"error": "Invalid JSON format in keyword_volume."}
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


    except json.JSONDecodeError:
        return {"error": "Invalid JSON format in keyword_volume."}
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

def consume_generate_complementary_keywords(main_keyword):
    url = f"{API_BASE_URL}/generate-complementary-keywords"
    payload = {
        "system_context": SYSTEM_CONTEXT,
        "business_goal": BUSINESS_GOAL,
        "user_intent": USER_INTENT,
        "main_keyword": main_keyword
    }
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}
