import sys
import os
import json
import pandas as pd
from datetime import datetime
import time
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from db.get_stores import get_stores
from db.get_all_products import get_available_products_batch
from rest_consumer.where_used_api import consume_where_used
from scripts_automation.generate_convinations import generate_combinations
from db.insert_model_keyword import insert_model_keyword
from scripts_automation.google_adds import keyword_planner_automation, login_automation, cerrar_navegador
from scripts_automation.merge_csv import merge_csv_files

# Cargar brands mapping
with open(os.path.join(os.path.dirname(__file__), "..", "example", "brands_mapping.json"), "r", encoding="utf-8") as f:
    brands_mapping = json.load(f)["brands_mapping"]

def get_brand_api(store_id):
    for b in brands_mapping:
        if b.get("store_id") == store_id:
            return b.get("brand_api", "")
    return ""

def get_brand_db(store_id):
    for b in brands_mapping:
        if b.get("store_id") == store_id:
            return b.get("brand_db", "")
    return ""

def iniciar_automatizacion():
    selected_desc = combo_store.get()
    if not selected_desc or selected_desc not in store_id_map:
        messagebox.showwarning("Error", "Debe seleccionar una tienda válida.")
        return
    store_id = int(store_id_map[selected_desc])
    destination_folder = entry_carpeta_destino.get().strip()
    if not destination_folder:
        messagebox.showwarning("Error", "Debe seleccionar una carpeta para guardar los archivos.")
        return

    messagebox.showinfo("Automatización iniciada", "El proceso ha comenzado. Revisa la terminal para detalles.")
    start_time = time.time()
    processed_keywords = 0

    # Iniciar sesión en Google Ads Keyword Planner
    print("🔹 Iniciando sesión en Google Ads Keyword Planner...")
    driver, wait = login_automation()
    print("✅ Sesión iniciada correctamente")

    # Traer productos filtrados y realizar keyword research
    print(f"🔹 Consultando productos para store_id: {store_id}")
    product_count = 0
    for product in get_available_products_batch(store_id):
        product_count += 1
        print(f"\n📦 Producto #{product_count}")
        
        sku = product.get("SKU")
        store_id_prod = product.get("STOREID")
        
        print(f"   SKU: {sku}, Store ID: {store_id_prod}")
        
        if not sku:
            print(f"   ⚠️ Producto omitido - falta SKU")
            continue

        brand_api = get_brand_api(store_id_prod)
        brand_db = get_brand_db(store_id_prod)
        print(f"   Brand API: {brand_api}, Brand DB: {brand_db}")
        
        if not brand_api or not brand_db:
            print(f"   ⚠️ Producto omitido - no se encontró brand mapping")
            continue

        # Consultar API externa
        print(f"   🌐 Consultando API where_used para SKU: {sku}, Brand: {brand_api}")
        api_response = consume_where_used(sku, brand_api)
        print(f"   📡 Respuesta API: {type(api_response)}")
        
        if not isinstance(api_response, list) or not api_response or not isinstance(api_response[0], list):
            print(f"   ⚠️ Respuesta API inválida o vacía")
            continue

        print(f"   ✅ API response válida, procesando {len(api_response[0])} items")
        for idx, item in enumerate(api_response[0]):
            print(f"\n   🔹 Item #{idx + 1}: SKU={item.get('sku')}, Model={item.get('model')}, Part Type={item.get('part_type')}")
            
            # Generar combinaciones usando brand_db
            keywords = generate_combinations(
                item.get("part_type", ""),
                brand_db,
                item.get("model", ""),
                item.get("sku", "")
            )
            print(f"   🔑 Keywords generadas: {keywords}")
            
            # Realizar keyword research en Google Ads y obtener resultado en memoria
            print(f"   🚀 Ejecutando keyword research para {len(keywords)} keywords...")
            result_json = keyword_planner_automation(driver, wait, keywords)
            print(f"   📊 Resultado keyword research: {type(result_json)}")
            
            # Insertar en BD inmediatamente con los datos del keyword research
            if isinstance(result_json, list):
                print(f"   💾 Insertando {len(result_json)} keywords en BD...")
                for kw_data in result_json:
                    doc = {
                        "brand": brand_db,
                        "sku": item.get("sku", ""),
                        "model": item.get("model", ""),
                        "part_type": item.get("part_type", ""),
                        "keyword": kw_data.get("Keyword", ""),
                        "volume": kw_data.get("Avg_monthly_searches", 0)
                    }
                    insert_model_keyword(doc)
                    processed_keywords += 1
                print(f"   ✅ Keywords insertadas. Total procesadas: {processed_keywords}")
            else:
                print(f"   ⚠️ result_json no es una lista, se omite inserción")
    
    print(f"\n🏁 Loop de productos completado. Total productos procesados: {product_count}")
    cerrar_navegador(driver)

    end_time = time.time()
    elapsed_time = end_time - start_time
    hours, rem = divmod(elapsed_time, 3600)
    minutes, seconds = divmod(rem, 60)
    messagebox.showinfo("Automatización completada", f"Se procesaron {processed_keywords} keywords en {int(hours)} horas, {int(minutes)} minutos y {int(seconds)} segundos.")

def seleccionar_carpeta_destino():
    folder_selected = filedialog.askdirectory(title="Selecciona una carpeta para guardar los archivos fusionados")
    if folder_selected:
        entry_carpeta_destino.delete(0, tk.END)
        entry_carpeta_destino.insert(0, folder_selected)

# Configuración de la ventana principal
root = tk.Tk()
root.title("Automatización Model Keywords")
root.geometry("700x400")
root.resizable(False, False)
root.configure(bg="#F8F9FA")

main_frame = ttk.Frame(root, padding=20)
main_frame.pack(fill="both", expand=True)

# Selector de tienda
ttk.Label(main_frame, text="Selecciona la tienda:", font=("Arial", 12, "bold")).pack(anchor="w", pady=5)
stores = get_stores()
store_options = [s["description"] for s in stores if "description" in s and "id" in s]
store_id_map = {s["description"]: s["id"] for s in stores if "description" in s and "id" in s}
combo_store = ttk.Combobox(main_frame, values=store_options, state="readonly", width=30)
combo_store.pack(pady=5)
if store_options:
    combo_store.set(store_options[0])

ttk.Label(main_frame, text="📁 Destination folder:", font=("Arial", 12, "bold")).pack(anchor="w", pady=5)
entry_carpeta_destino = ttk.Entry(main_frame, width=50, font=("Arial", 12))
entry_carpeta_destino.pack(fill="x", pady=5)

btn_seleccionar_carpeta = tk.Button(main_frame, text="🗂 Select folder",
                                    command=seleccionar_carpeta_destino, font=("Arial", 12, "bold"),
                                    bg="white", fg="#1565C0", activebackground="#E3F2FD",
                                    activeforeground="#1565C0", relief="flat", padx=10, pady=5, borderwidth=0)
btn_seleccionar_carpeta.pack(pady=5)

btn_iniciar = tk.Button(main_frame, text="✅ Process", command=iniciar_automatizacion, font=("Arial", 12, "bold"),
                        bg="#1565C0", fg="white", activebackground="#0D47A1", activeforeground="white",
                        relief="raised", padx=10, pady=5, borderwidth=2)
btn_iniciar.pack(pady=10)

root.mainloop()