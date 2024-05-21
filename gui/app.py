import tkinter as tk
from tkinter import messagebox
from tkcalendar import DateEntry

def realizar_scraping():
    fecha_inicio = fecha_inicio_entry.get()
    fecha_fin = fecha_fin_entry.get()
    messagebox.showinfo("Scraping", f"Iniciando scraping desde {fecha_inicio} hasta {fecha_fin}")
    print(f"Fecha de inicio: {fecha_inicio}")
    print(f"Fecha de fin: {fecha_fin}")

# Crear la ventana principal
root = tk.Tk()
root.title("Scraping de Fechas")

# Etiqueta y entrada para la fecha de inicio
tk.Label(root, text="Fecha de inicio:").grid(row=0, column=0, padx=10, pady=10)
fecha_inicio_entry = DateEntry(root, width=12, background='darkblue',
                            foreground='white', borderwidth=2, year=2024, month=1, day=1)
fecha_inicio_entry.grid(row=0, column=1, padx=10, pady=10)

# Etiqueta y entrada para la fecha de fin
tk.Label(root, text="Fecha de fin:").grid(row=1, column=0, padx=10, pady=10)
fecha_fin_entry = DateEntry(root, width=12, background='darkblue',
                            foreground='white', borderwidth=2, year=2024, month=1, day=1)
fecha_fin_entry.grid(row=1, column=1, padx=10, pady=10)

# Botón para realizar el scraping
scraping_button = tk.Button(root, text="Realizar scraping", command=realizar_scraping)
scraping_button.grid(row=2, column=0, columnspan=2, pady=20)

# Iniciar el loop de la aplicación
root.mainloop()
