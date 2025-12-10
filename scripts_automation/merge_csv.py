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
        print(f"🔍 [DEBUG] Leyendo archivo: {file_path}")
        df = pd.read_csv(file_path, skiprows=2, encoding="utf-16", delimiter="\t")
        print(f"🔍 [DEBUG] Filas leídas inicialmente: {len(df)}")
        print(f"🔍 [DEBUG] Columnas encontradas: {df.columns.tolist()}")
        
        df.columns = df.columns.str.strip()
        required_columns = ['Keyword', 'Avg. monthly searches', 'Competition', 'Competition (indexed value)']
        if not set(required_columns).issubset(df.columns):
            print(f"⚠ Columnas faltantes en {file_path}")
            print(f"🔍 [DEBUG] Se esperaban: {required_columns}")
            return None
        
        print(f"🔍 [DEBUG] Primeras 3 filas antes de procesar:")
        print(df[required_columns].head(3))
        
        df = df[required_columns].rename(columns={'Competition (indexed value)': 'Competition_index'})
        
        # Limpiar comas de los números antes de convertir
        print(f"🔍 [DEBUG] Valores originales de 'Avg. monthly searches' (primeros 5): {df['Avg. monthly searches'].head().tolist()}")
        df['Avg_monthly_searches'] = df['Avg. monthly searches'].astype(str).str.replace(',', '').str.strip()
        print(f"🔍 [DEBUG] Después de limpiar comas: {df['Avg_monthly_searches'].head().tolist()}")
        
        df['Avg_monthly_searches'] = pd.to_numeric(df['Avg_monthly_searches'], errors='coerce')
        print(f"🔍 [DEBUG] Después de to_numeric: {df['Avg_monthly_searches'].head().tolist()}")
        print(f"🔍 [DEBUG] Valores NaN encontrados: {df['Avg_monthly_searches'].isna().sum()}")
        
        df['Competition_index'] = pd.to_numeric(df['Competition_index'], errors='coerce').fillna(0.0)
        
        print(f"🔍 [DEBUG] Filas antes de dropna: {len(df)}")
        # Reemplazar NaN con 0 en lugar de eliminar las filas
        df['Avg_monthly_searches'] = df['Avg_monthly_searches'].fillna(0)
        print(f"🔍 [DEBUG] Filas después de fillna(0): {len(df)}")
        
        # Mostrar estadísticas de volumen
        print(f"🔍 [DEBUG] Valores de Avg_monthly_searches:")
        print(f"         Min: {df['Avg_monthly_searches'].min()}")
        print(f"         Max: {df['Avg_monthly_searches'].max()}")
        print(f"         Valores únicos: {df['Avg_monthly_searches'].unique()[:10]}")
        print(f"         Keywords con volumen 0: {(df['Avg_monthly_searches'] == 0).sum()}")
        print(f"         Keywords con volumen > 0: {(df['Avg_monthly_searches'] > 0).sum()}")
        
        if len(df) == 0:
            print(f"⚠️ [WARNING] No hay datos en el CSV.")
            return None
        
        df = df[['Keyword', 'Competition', 'Avg_monthly_searches', 'Competition_index']]
        df = df.sort_values(by='Avg_monthly_searches', ascending=False)
        print(f"✅ [DEBUG] Filas finales a retornar: {len(df)}")
        return df[['Keyword', 'Competition', 'Avg_monthly_searches', 'Competition_index']]
    except Exception as e:
        print(f"❌ Error al procesar {file_path}: {e}")
        import traceback
        traceback.print_exc()
        return None

def merge_csv_files(num_files, destination_folder, file_prefix, return_json=False):
    if not destination_folder:
        print("⚠ No se ha especificado una carpeta de destino.")
        return None

    print(f"🔍 [DEBUG] Buscando {num_files} archivo(s) CSV en: {SOURCE_FOLDER}")
    
    # 🔹 Obtener todos los archivos CSV recientes
    latest_files = get_latest_csv_files(SOURCE_FOLDER, num_files)
    print(f"🔍 [DEBUG] Archivos CSV encontrados: {len(latest_files)}")
    for i, f in enumerate(latest_files):
        print(f"         Archivo {i+1}: {f}")

    if len(latest_files) < num_files:
        print(f"⚠ No hay suficientes archivos CSV para fusionar. Se esperaban {num_files}, pero se encontraron {len(latest_files)}")
        return None

    # 🔹 Procesar cada archivo y limpiarlo
    cleaned_dfs = []
    for file in latest_files:
        cleaned_data = clean_csv(file)
        if cleaned_data is not None:
            print(f"✅ [DEBUG] Archivo procesado exitosamente: {len(cleaned_data)} filas")
            cleaned_dfs.append(cleaned_data)
        else:
            print(f"❌ [DEBUG] Archivo no se pudo procesar o está vacío")

    if not cleaned_dfs:
        print("❌ Error: No se pudieron procesar archivos correctamente.")
        return None

    print(f"🔍 [DEBUG] Total de DataFrames a fusionar: {len(cleaned_dfs)}")
    
    # 🔹 Fusionar todos los archivos obtenidos en un solo DataFrame
    merged_df = pd.concat(cleaned_dfs, ignore_index=True).drop_duplicates()
    print(f"🔍 [DEBUG] Filas después de concat y drop_duplicates: {len(merged_df)}")
    
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
    print(f"🔍 [DEBUG] JSON generado con {len(json.loads(merged_json))} registros")

    if return_json:
        result = json.loads(merged_json)
        print(f"🔍 [DEBUG] Retornando JSON con {len(result)} elementos")
        if len(result) > 0:
            print(f"🔍 [DEBUG] Primer elemento del JSON: {result[0]}")
        return result  # Devuelve JSON como dict
    else:
        save_json_path = os.path.join(destination_folder, f'{file_prefix}_{timestamp}.json')
        with open(save_json_path, 'w', encoding='utf-8') as f:
            f.write(merged_json)

        print(f"✅ Archivo JSON guardado en: {save_json_path}")

if __name__ == "__main__":
    # Ejemplo de uso
    destination = os.path.join(os.path.expanduser("~"), "Downloads", "Keyword_Results")
    merge_csv_files(num_files=1, destination_folder=destination, file_prefix="Merged_Keywords")