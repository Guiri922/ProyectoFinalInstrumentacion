# Imports para interfaz gráfica
import tkinter as tk
from tkinter import ttk, messagebox

# Import para leer arduino
import serial

# Import para graficar
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Import para guardar datos
import csv
from datetime import datetime

# Import para agregar tiempo para inicializar arduino
from time import sleep

# Intenta conectar con el arduino
try:
    arduino = serial.Serial('COM5', 9600, timeout=0)
except:
    arduino = None

sleep(1.5)

# valor de x visibles en la gráfica
muestras = 50
datos_plot = np.zeros(muestras)
grabando = False

archivo_csv = None
escritor_csv = None

def update():
    """
    Actualiza la ventana en Tkinter
    """
    global datos_plot, grabando
    if arduino and arduino.in_waiting > 0:
        try:
            linea = arduino.readline().decode("utf-8").strip().split(",")
            analog = int(linea[0])

            if analog:
                print(analog)
                lbl_digitos0.config(text=f'{analog}')

                datos_plot = np.roll(datos_plot, -1)
                datos_plot[-1] = analog
                linea_plot.set_ydata(datos_plot)

                canvas.draw()

                if grabando:
                    ahora = datetime.now().strftime('%H:%M:%S.%f')[:-3]
                    escritor_csv.writerow([ahora, analog])
        except:
            pass

    ventana.after(1, update)  # Re-ejecutar en 10ms


def start():
    """
    Inicia a grabar los datos para el csv.
    """
    global grabando, archivo_csv, escritor_csv
    if not grabando:
        try:
            nombre_archivo = f"log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            archivo_csv = open(nombre_archivo, "w", newline='')
            escritor_csv = csv.writer(archivo_csv)

            escritor_csv.writerow(["Hora", "ADC"])

            grabando = True
            btn_start.config(state="disabled")
            btn_stop.config(state="normal")
            lbl_status.config(text=f"Grabando en: {nombre_archivo}",
                              foreground="red")
        except Exception as e:
            messagebox.showerror("Error", "No se pudo crear el " +
                                 f"archivo: {e}")


def stop():
    """
    Detiene la grabación del archivo csv.
    """
    global grabando, archivo_csv
    if grabando:
        grabando = False
        archivo_csv.close()
        btn_start.config(state="normal")
        btn_stop.config(state="disabled")
        lbl_status.config(text="Grabación finalizada y guardada",
                          foreground="black")


ventana = tk.Tk()
ventana.title("Dashboard - Gráfica y Guardado de datos")
ventana.geometry("1000x500")

frm_izq = ttk.Frame(ventana, padding=9)
frm_izq.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

fig, ax = plt.subplots(figsize=(4, 3), dpi=100)
linea_plot, = ax.plot(datos_plot, color='blue', lw=2, label="ADC")

ax.set_ylim(-10, 12000)
ax.set_title("Señal de ADC")
ax.legend()
canvas = FigureCanvasTkAgg(fig, master=frm_izq)
canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

frm_der = ttk.Frame(ventana, padding=30, relief="sunken")
frm_der.pack(side=tk.LEFT, fill=tk.Y)

ttk.Label(frm_der, text="Valor ADC", font=("Arial", 10, "bold")).pack()
lbl_digitos0 = ttk.Label(frm_der, text="0", font=("Arial", 30))
lbl_digitos0.pack(pady=10)

ttk.Separator(frm_der, orient=tk.HORIZONTAL).pack(fill="x", pady=20)

btn_start = ttk.Button(frm_der, text="Iniciar grabación", command=start)
btn_start.pack(fill="x", pady=5)

btn_stop = ttk.Button(frm_der, text="Detener grabación", command=stop,
                      state="disabled")
btn_stop.pack(fill="x", pady=5)

lbl_status = ttk.Label(frm_der, text="Estado: En espera", font=("Arial", 9,
                                                                "italic"))
lbl_status.pack(pady=20)
if not arduino:
    messagebox.showerror("Error", "Arduino no encontrado")

update()
ventana.mainloop()

if arduino:
    arduino.close()