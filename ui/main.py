import sys
import os
import pandas as pd
from datetime import datetime
import time
import openpyxl
# Agregar el directorio raíz al sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from scripts_automation.google_adds import keyword_planner_automation, login_automation, cerrar_navegador
from scripts_automation.merge_csv import merge_csv_files
from rest_consumer.keyword_planner import consume_generate_keywords,  consume_generate_complementary_keywords
# Definir la ruta fija para guardar los archivos

def cargar_keywords():
    file_path = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx")])
    if file_path:
        try:
            df = pd.read_excel(file_path)
            # Convertir filas a formato de keyword con variantes separadas por coma
            keywords = df.apply(lambda row: ", ".join(row.dropna().astype(str)), axis=1).tolist()

            # Insertar los datos en el campo de texto
            entry_keywords.delete("1.0", tk.END)
            entry_keywords.insert("1.0", "\n".join(keywords))

            messagebox.showinfo("Carga exitosa", "Keywords cargadas correctamente desde el archivo.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el archivo: {e}")

def iniciar_automatizacion():
    keywords = entry_keywords.get("1.0", tk.END).strip().split("\n")
    url = entry_url.get().strip()
    num_files = len(keywords)

    if not keywords or keywords == ['']:
        messagebox.showwarning("Campos incompletos", "Debe ingresar al menos una palabra clave.")
        return

    destination_folder = entry_carpeta_destino.get().strip()
    if not destination_folder:
        messagebox.showwarning("Error", "Debe seleccionar una carpeta para guardar los archivos.")
        return

    messagebox.showinfo("Automatización iniciada", "El proceso ha comenzado. Revisa la terminal para detalles.")

    # Capturar el tiempo de inicio
    start_time = time.time()

    # 🔹 Iniciar sesión y abrir el Keyword Planner solo una vez
    driver, wait = login_automation()  # Guardamos el driver y wait para reusarlos

    processed_keywords = 0

    for keyword_row in keywords:
        if ',' not in keyword_row:
            response = consume_generate_complementary_keywords(keyword_row.strip())
            if "error" in response:
                print(f"⚠️ Error al generar variantes con IA para '{keyword_row}': {response['error']}")
                continue
            keyword_row = f"{response['Keyword']}, {', '.join(response['Variations'])}"

        # 🔹 Llamamos correctamente `keyword_planner_automation` pasando driver y wait
        keyword_planner_automation(driver, wait, [keyword_row], url if url else None)

        # 🔹 Generar el JSON en memoria y pasarlo directamente a la API sin guardarlo
        time.sleep(5)  # Esperar a que se complete la descarga
        json_data = merge_csv_files(1, destination_folder, "Keyword_Volumen", return_json=True)
        
        if ai_suggestion_var.get() and json_data:
            print(f"🔹 AI keyword suggestion enabled for '{keyword_row}' - Calling API...")
            result = consume_generate_keywords(json_data, destination_folder)
            print("🔹 AI Response:", result)

        processed_keywords += 1

    if consolidated_var.get():
        merge_csv_files(num_files, destination_folder, "consolidated_keywords")

    # 🔹 Cerrar el navegador solo al final del proceso
    cerrar_navegador(driver)
    print("🚪 Navegador cerrado después de completar todas las iteraciones.")

    # Capturar el tiempo de fin
    end_time = time.time()
    elapsed_time = end_time - start_time

    # Convertir el tiempo transcurrido a horas, minutos y segundos
    hours, rem = divmod(elapsed_time, 3600)
    minutes, seconds = divmod(rem, 60)

    # Mostrar alerta con el tiempo transcurrido y la cantidad de keywords procesadas
    messagebox.showinfo("Automatización completada", f"Se procesaron {processed_keywords} keywords en {int(hours)} horas, {int(minutes)} minutos y {int(seconds)} segundos.")




def descargar_template():
    """Permite al usuario descargar el archivo de ejemplo Keywords.xlsx"""
    # Se obtiene el directorio padre (donde se encuentra 'example')
    directorio_padre = os.path.dirname(os.path.dirname(__file__))
    ruta_origen = os.path.join(directorio_padre, "example", "Keywords.xlsx")

    if not os.path.exists(ruta_origen):
        messagebox.showerror("Error", "No se encontró el archivo de plantilla.")
        return

    ruta_destino = filedialog.asksaveasfilename(
        defaultextension=".xlsx",
        filetypes=[("Excel Files", "*.xlsx")],
        title="Guardar plantilla como"
    )

    if ruta_destino:
        try:
            import shutil
            shutil.copy(ruta_origen, ruta_destino)
            messagebox.showinfo("Descarga exitosa", f"Plantilla guardada en: {ruta_destino}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el archivo: {e}")

def seleccionar_carpeta_destino():
    """ Abre un cuadro de diálogo para que el usuario elija la carpeta donde guardar los archivos fusionados """
    folder_selected = filedialog.askdirectory(title="Selecciona una carpeta para guardar los archivos fusionados")
    if folder_selected:
        entry_carpeta_destino.delete(0, tk.END)
        entry_carpeta_destino.insert(0, folder_selected)

def cerrar_aplicacion():
    root.destroy()

# Configuración de la ventana principal
root = tk.Tk()
root.title("Automatización Google Ads")
root.geometry("950x950")
root.resizable(False, False)
root.configure(bg="#F8F9FA")  # Fondo gris claro

# Estilos
style = ttk.Style()
style.configure("TFrame", background="#F8F9FA")  # Fondo gris claro
style.configure("TLabel", font=("Arial", 12, "bold"), background="#F8F9FA", foreground="#0D47A1")  # Texto azul oscuro
style.configure("Rounded.TButton", font=("Arial", 12, "bold"), background="#1565C0", foreground="white", padding=10, relief="raised", borderwidth=2)
style.map("Rounded.TButton", background=[("active", "#0D47A1")])

# Encabezado
header = ttk.Frame(root, style="TFrame", padding=10)
header.pack(fill="x")

ttk.Label(header, text="🤖 Keyword Planner", font=("Arial", 16, "bold"), style="TLabel").pack(side="left")
ttk.Label(header, text=datetime.now().strftime('%B %d, %Y %I:%M %p'), font=("Arial", 12), background="#F8F9FA").pack(side="right")

# Contenedor principal
main_frame = ttk.Frame(root, padding=20, style="TFrame")
main_frame.pack(fill="both", expand=True)

# Sección de Automatización de Google Ads
google_ads_frame = ttk.LabelFrame(main_frame, text="Automation Google Ads", padding=20)
google_ads_frame.pack(fill="both", expand=True, padx=10, pady=10)

ttk.Label(google_ads_frame, text="Keywords (One line each group):", style="TLabel").pack(anchor="w", pady=5)
entry_keywords = tk.Text(google_ads_frame, height=5, width=50, font=("Arial", 12), relief="solid", borderwidth=2, bg="#ffffff", fg="#333333")
entry_keywords.pack(fill="x", pady=5)

# Crear un frame para los botones
button_frame = ttk.Frame(google_ads_frame, style="TFrame")
button_frame.pack(pady=5)

btn_cargar = tk.Button(button_frame, text="💾 Upload", command=cargar_keywords, font=("Arial", 12, "bold"),
                       bg="#1565C0", fg="white", activebackground="#0D47A1", activeforeground="white",
                       relief="raised", padx=10, pady=5, borderwidth=2)
btn_cargar.pack(side="left", padx=5)




btn_descargar = tk.Button(google_ads_frame, text="⬇ Download Template", command=descargar_template,
                          font=("Arial", 12, "bold"), bg="white", fg="#1565C0", activebackground="#E3F2FD",
                          activeforeground="#1565C0", relief="flat", padx=10, pady=5, borderwidth=0)
btn_descargar.pack(pady=5)




ttk.Label(google_ads_frame, text="🌍 URL (Optional):", style="TLabel").pack(anchor="w", pady=5)
entry_url = ttk.Entry(google_ads_frame, width=50, font=("Arial", 12))
entry_url.pack(fill="x", pady=5)

# Checkboxes
checkbox_frame = ttk.Frame(google_ads_frame, style="TFrame")
checkbox_frame.pack(fill="x", pady=10)

ai_suggestion_var = tk.BooleanVar()
consolidated_var = tk.BooleanVar()

ttk.Label(google_ads_frame, text="📁 Destination folder:", style="TLabel").pack(anchor="w", pady=5)
entry_carpeta_destino = ttk.Entry(google_ads_frame, width=50, font=("Arial", 12))
entry_carpeta_destino.pack(fill="x", pady=5)

btn_seleccionar_carpeta = tk.Button(google_ads_frame, text="🗂 Select folder",
                                    command=seleccionar_carpeta_destino, font=("Arial", 12, "bold"),
                                    bg="white", fg="#1565C0", activebackground="#E3F2FD",
                                    activeforeground="#1565C0", relief="flat", padx=10, pady=5, borderwidth=0)
btn_seleccionar_carpeta.pack(pady=5)


ai_suggestion_check = ttk.Checkbutton(checkbox_frame, text="AI keyword suggestion:", variable=ai_suggestion_var)
ai_suggestion_check.pack(side="left", padx=10)

consolidated_check = ttk.Checkbutton(checkbox_frame, text="Consolidated:", variable=consolidated_var)
consolidated_check.pack(side="left", padx=10)

btn_iniciar = tk.Button(google_ads_frame, text="✅ Process", command=iniciar_automatizacion, font=("Arial", 12, "bold"), bg="#1565C0", fg="white", activebackground="#0D47A1", activeforeground="white", relief="raised", padx=10, pady=5, borderwidth=2)
btn_iniciar.pack(pady=10)

root.mainloop()
