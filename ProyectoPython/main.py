import tkinter as tk
from tkinter import ttk, messagebox
import serial
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import csv
from datetime import datetime
import numpy as np

# Intenta conectar con el arduino
try:
    arduino = serial.Serial('COM5', 9600, timeout=0.1)
except:
    arduino = None

# valor de x visibles en la gráfica
muestras = 50
datos_plot0 = np.zeros(muestras)
datos_plot1 = np.zeros(muestras)
grabando = False
archivo_csv = None
escritor_csv = None


def update():
    global datos_plot0, datos_plot1, grabando
    if arduino and arduino.in_waiting > 0:
        try:
            sum = 0
            for i in range(20):
                linea = arduino.readline().decode("utf-8").strip().split(",")
                analog0 = float(linea[0])
                sum += analog0

            sum /= 20

            if sum:
                print(f"{sum}")
                lbl_digitos0.config(text=f'{sum:.2f}')

                datos_plot0 = np.roll(datos_plot0, -1)
                datos_plot0[-1] = sum
                linea0_plot.set_ydata(datos_plot0)

                canvas.draw()

                if grabando:
                    ahora = datetime.now().strftime('%H:%M:%S.%f')[:-3]
                    escritor_csv.writerow([ahora, sum])
        except:
            pass

    ventana.after(30, update)  # Re-ejecutar en 30ms


def start():
    global grabando, archivo_csv, escritor_csv
    if not grabando:
        try:
            nombre_archivo = f"log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            archivo_csv = open(nombre_archivo, "w", newline='')
            escritor_csv = csv.writer(archivo_csv)

            escritor_csv.writerow(["Fecha y Hora", "ADC0", "ADC1"])

            grabando = True
            btn_start.config(state="disabled")
            btn_stop.config(state="normal")
            lbl_status.config(text=f"Grabando en: {nombre_archivo}",
                              foreground="red")
        except Exception as e:
            messagebox.showerror("Error", "No se pudo crear el " +
                                 f"archivo: {e}")


def stop():
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
linea0_plot, = ax.plot(datos_plot0, color='blue', lw=2, label="ADC")

ax.set_ylim(430, 460)
ax.set_title("Señal de ADC")
ax.legend()
canvas = FigureCanvasTkAgg(fig, master=frm_izq)
canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

frm_der = ttk.Frame(ventana, padding=20, relief="sunken")
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