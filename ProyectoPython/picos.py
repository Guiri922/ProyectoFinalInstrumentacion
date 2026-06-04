"""
Detección de picos en señal ADC (frecuencia cardiaca) con filtrado.
Uso: python detectar_picos.py [archivo.csv] [--umbral N] [--distancia N]
"""

import csv
import sys
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import butter, filtfilt, find_peaks

# ─── Parámetros ajustables ────────────────────────────────────────────────────
ARCHIVO_CSV   = "logs/log_20260526_164038_este_si.csv"
IGNORAR_HASTA = 2.5    # segundos iniciales a ignorar (zona del drop)
IGNORAR_DESDE = 20.0  # segundos a partir de los cuales se ignoran datos
FREC_CORTE    = 3.0    # Hz — corta ruido por encima de esta frecuencia
DISTANCIA_MIN = 0.4    # segundos mínimos entre latidos (~150 bpm máx)
PROMINENCIA   = 50     # cuánto debe sobresalir un pico sobre su entorno
# ─────────────────────────────────────────────────────────────────────────────

def cargar_datos(archivo):
    tiempos, valores = [], []
    ref = None
    with open(archivo, newline="", encoding="utf-8") as f:
        for fila in csv.DictReader(f):
            t = datetime.strptime(fila["Hora"].strip(), "%H:%M:%S.%f")
            if ref is None:
                ref = t
            tiempos.append((t - ref).total_seconds())
            valores.append(int(fila["ADC"].strip()))
    return np.array(tiempos), np.array(valores)


def filtrar(tiempos, valores, frec_corte):
    # Frecuencia de muestreo promedio
    fs = 1.0 / np.mean(np.diff(tiempos))
    nyq = fs / 2.0
    # Filtro Butterworth pasa-bajas de orden 4
    b, a = butter(4, frec_corte / nyq, btype="low")
    return filtfilt(b, a, valores)


def detectar_picos(tiempos, valores_filtrados, distancia_min, prominencia):
    fs = 1.0 / np.mean(np.diff(tiempos))
    distancia_muestras = int(distancia_min * fs)
    indices, props = find_peaks(valores_filtrados,
                                distance=distancia_muestras,
                                prominence=prominencia)
    return indices


def mostrar_resultados(picos_idx, tiempos, valores_filtrados):
    pt = tiempos[picos_idx]
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
    print("=" * 55)


def graficar(tiempos, valores_raw, valores_filtrados, picos_idx, ignorar_hasta):
    mask = tiempos >= ignorar_hasta
    t = tiempos[mask]
    raw = valores_raw[mask]
    filt = valores_filtrados[mask]
    pt = tiempos[picos_idx]
    pv = valores_filtrados[picos_idx]

    fig, axes = plt.subplots(2, 1, figsize=(13, 6), sharex=True)

    # Panel superior: señal cruda
    axes[0].plot(t, raw, color="#888888", linewidth=0.7)
    axes[0].set_ylabel("ADC (cruda)")
    axes[0].set_title("Señal original")
    axes[0].grid(True, alpha=0.3)

    # Panel inferior: señal filtrada + picos
    axes[1].plot(t, filt, color="#4a90d9", linewidth=1.2)
    axes[1].scatter(pt, pv, color="red", zorder=5, s=50)
    axes[1].set_ylabel("ADC (filtrada)")
    axes[1].set_xlabel("Tiempo (s)")
    axes[1].set_title(f"Señal filtrada — {len(picos_idx)} latidos detectados  |  ~{60/np.mean(np.diff(pt)):.1f} BPM")
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig("picos_señal.png", dpi=150)
    # print("  Gráfica guardada: picos_señal.png")
    plt.show()


if __name__ == "__main__":
    archivo = sys.argv[1] if len(sys.argv) > 1 else ARCHIVO_CSV

    tiempos, valores = cargar_datos(archivo)
    print(tiempos)

    # Recortar drop inicial y límite superior
    mask = (tiempos >= IGNORAR_HASTA) & (tiempos <= IGNORAR_DESDE)
    t = tiempos[mask]
    v = valores[mask]

    v_filt = filtrar(t, v, FREC_CORTE)
    picos_idx = detectar_picos(t, v_filt, DISTANCIA_MIN, PROMINENCIA)

    mostrar_resultados(picos_idx, t, v_filt)
    graficar(tiempos, valores, 
             np.concatenate([valores[~mask], v_filt]),  # cruda completa, filtrada post-drop
             picos_idx, IGNORAR_HASTA)
