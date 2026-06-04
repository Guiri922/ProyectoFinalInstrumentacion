import serial
import numpy as np
from time import sleep

import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt, find_peaks

def ask_serial(arduino, port, baudrate, number_to_send:int):
    if arduino:
        try:
            arduino.write(str(number_to_send).encode('utf-8'))
            for i in range(20):
                sleep(1)
                print(f"Espera {20-i} segundos...")
            line1 = arduino.readline().decode('utf-8').strip()
            line2 = arduino.readline().decode('utf-8').strip()
            v = np.array([int(x.strip()) for x in line1.split(',')])
            t = np.array([int(x.strip()) for x in line2.split(',')])

            return v, t
        except serial.SerialException as e:
            print(f"Serial communication error: {e}")
            return None, None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None, None
    elif arduino.in_waiting == 0:
        print("Error en tiempo")
    else:
        print("Error en el arduino")
    return None, None

def connect():
    try:
        arduino = serial.Serial("COM5", 9600, timeout=0)
    except:
        arduino = None

    return arduino

def filtrar(tiempos, valores):
    # Frecuencia de muestreo promedio
    fs = 1_000_000.0 / np.mean(np.diff(tiempos))
    nyq = fs / 2.0
    # Filtro Butterworth pasa-bajas de orden 4
    b, a = butter(4, 3 / nyq)
    return filtfilt(b, a, valores)

def detectar_picos(tiempos, valores_filtrados):
    fs = 1_000_000.0 / np.mean(np.diff(tiempos))
    distancia_muestras = int(0.4 * fs)
    indices, props = find_peaks(valores_filtrados,
                                distance=distancia_muestras,
                                prominence=50)
    return indices


def mostrar_resultados(picos_idx, tiempos, valores_filtrados):
    pt = tiempos[picos_idx]/1_000_000
    pv = valores_filtrados[picos_idx]
    print("=" * 55)
    print(f"  Picos detectados : {len(picos_idx)}")
    print(f"  {'#':>3}  {'Tiempo (s)':>12}  {'ADC':>7}  {'Δt':>10}")
    print(f"  {'-'*3}  {'-'*12}  {'-'*7}  {'-'*10}")
    for i in range(len(pt)):
        dt = f"{pt[i] - pt[i-1]:.3f} s" if i > 0 else "—"
        print(f"  {i+1:>3}  {pt[i]:>12.3f}  {pv[i]:>7.0f}  {dt:>10}")
    if len(pt) > 1:
        deltas = np.diff(pt)
        bpm = 60.0 / np.mean(deltas)
        print(f"\n  Δt promedio : {np.mean(deltas):.3f} s")
        print(f"  BPM aprox.  : {bpm:.1f}")
    else:
        bpm = 0
    print("=" * 55)
    return round(bpm)

def capture(arduino):
    print(f"arduino: {arduino}")
    if arduino is not None:
        voltaje,tiempo = ask_serial(arduino, "COM5",9600,400)
        if voltaje is not None and tiempo is not None:
            filtered_voltaje = filtrar(tiempo, voltaje)
            peaks_indx = detectar_picos(tiempo, filtered_voltaje)

            bpm = mostrar_resultados(peaks_indx, tiempo, filtered_voltaje)
            return bpm,tiempo,voltaje,filtered_voltaje,peaks_indx

        print("Hubo un error al capturar los datos")
        print(type(tiempo))
    else:
        voltaje,tiempo = None, None
        print("Hubo un error")

    return 0,[],[],[],[]

if __name__ == "__main__":
    arduino = connect()
    bpm = capture(arduino)