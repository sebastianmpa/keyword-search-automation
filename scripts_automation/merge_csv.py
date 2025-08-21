import os
import pandas as pd
import re
import json
from datetime import datetime

# Detectar automáticamente la carpeta de Descargas del usuario
SOURCE_FOLDER = os.path.join(os.path.expanduser("~"), "Downloads")


def extract_datetime_from_filename(filename):
    """ Extrae la fecha y hora desde el nombre del archivo """
    match = re.search(r"(\d{4}-\d{2}-\d{2}) at (\d{2}_\d{2}_\d{2})", filename)
    if match:
        date_str, time_str = match.groups()
        time_str = time_str.replace("_", ":")  # Ajustar formato de hora
        return datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
    return None

def get_latest_csv_files(directory, num_files):
    """ Obtiene los `num_files` archivos CSV más recientes en la carpeta especificada """
    
    # Buscar archivos CSV en la carpeta proporcionada
    files = [f for f in os.listdir(directory) if f.startswith("Keyword Stats") and f.endswith(".csv")]
    
    # Si no hay archivos, devolver lista vacía
    if not files:
        print(f"⚠ No se encontraron archivos CSV en la carpeta: {directory}")
        return []

    # Ordenar los archivos por fecha extraída del nombre
    files = sorted(files, key=lambda f: extract_datetime_from_filename(f), reverse=True)
    
    # 🔹 Asegurar que devuelve exactamente `num_files` archivos y no solo el último
    return [os.path.join(directory, f) for f in files[:num_files]]


def clean_csv(file_path):
    try:
        df = pd.read_csv(file_path, skiprows=2, encoding="utf-16", delimiter="\t")
        df.columns = df.columns.str.strip()
        required_columns = ['Keyword', 'Avg. monthly searches', 'Competition', 'Competition (indexed value)']
        if not set(required_columns).issubset(df.columns):
            print(f"⚠ Columnas faltantes en {file_path}")
            return None
        df = df[required_columns].rename(columns={'Competition (indexed value)': 'Competition_index'})
        df['Avg_monthly_searches'] = pd.to_numeric(df['Avg. monthly searches'], errors='coerce')
        df['Competition_index'] = pd.to_numeric(df['Competition_index'], errors='coerce').fillna(0.0)
        df = df.dropna(subset=['Avg_monthly_searches'])
        df = df[df['Avg_monthly_searches'] > 0]
        df = df[['Keyword', 'Competition', 'Avg_monthly_searches', 'Competition_index']]
        df = df.sort_values(by='Avg_monthly_searches', ascending=False)
        return df[['Keyword', 'Competition', 'Avg_monthly_searches', 'Competition_index']]
    except Exception as e:
        print(f"❌ Error al procesar {file_path}: {e}")
        return None

def merge_csv_files(num_files, destination_folder, file_prefix, return_json=False):
    if not destination_folder:
        print("⚠ No se ha especificado una carpeta de destino.")
        return None

    # 🔹 Obtener todos los archivos CSV recientes
    latest_files = get_latest_csv_files(SOURCE_FOLDER, num_files)

    if len(latest_files) < num_files:
        print(f"⚠ No hay suficientes archivos CSV para fusionar. Se esperaban {num_files}, pero se encontraron {len(latest_files)}")
        return None

    # 🔹 Procesar cada archivo y limpiarlo
    cleaned_dfs = []
    for file in latest_files:
        cleaned_data = clean_csv(file)
        if cleaned_data is not None:
            cleaned_dfs.append(cleaned_data)

    if not cleaned_dfs:
        print("❌ Error: No se pudieron procesar archivos correctamente.")
        return None

    # 🔹 Fusionar todos los archivos obtenidos en un solo DataFrame
    merged_df = pd.concat(cleaned_dfs, ignore_index=True).drop_duplicates()
    merged_df = merged_df[['Keyword', 'Avg_monthly_searches', 'Competition', 'Competition_index']]
    merged_df = merged_df.sort_values(by='Avg_monthly_searches', ascending=False).reset_index(drop=True)

    # 🔹 Guardar archivo fusionado con timestamp
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    save_xlsx_path = os.path.join(destination_folder, f'{file_prefix}_{timestamp}.xlsx')
    merged_df.to_excel(save_xlsx_path, index=False)

    merged_json = merged_df.to_json(orient="records", force_ascii=False, indent=4)

    print(f"✅ Archivo XLSX guardado en: {save_xlsx_path}")

    if return_json:
        return json.loads(merged_json)  # Devuelve JSON como dict
    else:
        save_json_path = os.path.join(destination_folder, f'{file_prefix}_{timestamp}.json')
        with open(save_json_path, 'w', encoding='utf-8') as f:
            f.write(merged_json)

        print(f"✅ Archivo JSON guardado en: {save_json_path}")
