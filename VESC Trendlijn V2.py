# Js berekenen testvaart.pyplot

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

K = 0.335  
W = 6  

S = 0 
E = 6000
T= '09 02-04-2026 water tenopzicht van de ondergrond'
Title= "Trendlijnen vaartocht Franeker - Leeuwaarden 2025"

df1_raw = pd.read_csv('C:/Users/mikel/OneDrive - HvA/CleanMobility - Vaartochten gebruikt voor data analyse/0079 - Franeker - Leeuwaarden/1_Master_08_05.csv',  sep=',', header=None, comment='#')
df2_raw = pd.read_csv('C:/Users/mikel/OneDrive - HvA/CleanMobility - Vaartochten gebruikt voor data analyse/0079 - Franeker - Leeuwaarden/7_VESC_20_02.csv', sep=',', header=None, comment='#')

df1 = pd.DataFrame({
    'Time': df1_raw[1],
    'Snelheid': df1_raw[10]
})

df2 = pd.DataFrame({
    'Time': df2_raw[1],
    'A': df2_raw[10],
    'V': df2_raw[13]
})

# Vermogen berekenen
df2['Vermogen'] = df2['A'] * df2['V']

# Float maken
df1['Time'] = df1['Time'].astype(float)
df1['Snelheid'] = df1['Snelheid'].astype(float)
df2['Time'] = df2['Time'].astype(float)
df2['A'] = df2['A'].astype(float)
df2['V'] = df2['V'].astype(float)

# Sorteren
df1 = df1.sort_values("Time").reset_index(drop=True)
df2 = df2.sort_values("Time").reset_index(drop=True)

# Interpolatie
vermogen_interpolated = np.interp(df1['Time'], df2['Time'], df2['Vermogen'])
df1['Vermogen'] = vermogen_interpolated

# -----------------------------
# PLOT 1
# -----------------------------
df2.plot(x='Time', y='Vermogen')
plt.title('Vermogen over tijd')
plt.xlabel('time')
plt.ylabel('vermogen')
plt.grid(True)
plt.show()

# -----------------------------
# LOKALE FILTER (verbeterd)
# -----------------------------
df_clean = df1[['Snelheid', 'Vermogen']].dropna().copy()

# Verwijder echt onzin (nulband)
df_clean = df_clean[
    (df_clean['Snelheid'] > 1.0) &
    (df_clean['Vermogen'] > 10)
]

# Ruwe fit (globaal)
coeffs_rough = np.polyfit(df_clean['Snelheid'], df_clean['Vermogen'], 2)
poly_rough = np.poly1d(coeffs_rough)

# Verwachte waarde
df_clean['y_expected'] = poly_rough(df_clean['Snelheid'])

# Relatieve afwijking
df_clean['rel_error'] = abs(df_clean['Vermogen'] - df_clean['y_expected']) / df_clean['y_expected']

# Bins maken
df_clean['bin'] = pd.cut(df_clean['Snelheid'], bins=25)

filtered_list = []

for _, group in df_clean.groupby('bin'):
    if len(group) < 5:
        continue

    # Stap 1: filter op model (belangrijkste stap)
    group = group[group['rel_error'] < 0.5]

    if len(group) < 5:
        continue

    # Stap 2: extra IQR cleanup (fijnslijpen)
    Q1 = group['Vermogen'].quantile(0.03)
    Q3 = group['Vermogen'].quantile(0.97)
    IQR = Q3 - Q1

    group_filtered = group[
        (group['Vermogen'] >= Q1 - 1.0 * IQR) &
        (group['Vermogen'] <= Q3 + 1.0 * IQR)
    ]

    filtered_list.append(group_filtered)

df_filtered = pd.concat(filtered_list)
# -----------------------------
# NIEUWE TRENDSLIJN (FYSISCH)
# -----------------------------
x = df_filtered['Snelheid'].values
y = df_filtered['Vermogen'].values

# Fit: alleen v^3 term (door oorsprong, geen rare kromming)
coeffs = np.polyfit(x, y, 3)
poly_new = np.poly1d(coeffs)

x_new = np.linspace(x.min(), x.max(), 200)
y_new = poly_new(x_new)

# Sleeptest
y_sleeptest = 0.1664 * x_new**3 + 1.1467 * x_new**2 - 4.3168 * x_new

print("Trendlijn vermogen:")
print(poly_new)
# -----------------------------
# RENDEMENT
# -----------------------------
mask = x_new > 3  # lage snelheden eruit

x_eff = x_new[mask]
y_eff = y_new[mask]
y_sleep_eff = y_sleeptest[mask]

rendement = (y_sleep_eff / y_eff) * 100

print("Coefficient fit:", coeffs)
print("Gemiddeld rendement:", np.mean(rendement))

# -----------------------------
# PLOT MET 2 Y-ASSEN
# -----------------------------
fig, ax1 = plt.subplots()

# Data
ax1.scatter(df1['Snelheid'], df1['Vermogen'], color='lightgray', label='Ruwe data')
ax1.scatter(df_filtered['Snelheid'], df_filtered['Vermogen'], color='blue', label='Gefilterde data')

# Sleeptest
x_trend = np.sort(np.array(df1['Snelheid'].dropna()))
y_trend = 0.1664 * x_trend**3 + 1.1467 * x_trend**2 - 4.3168 * x_trend
ax1.plot(x_trend, y_trend, color='pink', label='Trendlijn sleeptest', linewidth=2)

# Nieuwe fit
ax1.plot(x_new, y_new, color='red', label='Trendlijn vermogen', linewidth=2)

ax1.set_xlim(0, 17)
ax1.set_ylim(0, 1500)
ax1.set_xlabel('Snelheid')
ax1.set_ylabel('Vermogen')

# Rechter as
ax2 = ax1.twinx()
ax2.plot(x_eff, rendement, color='green', label='Rendement (%)')
ax2.set_ylim(0, 100)
ax2.set_ylabel('Rendement (%)')

# Legend combineren
lines_1, labels_1 = ax1.get_legend_handles_labels()
lines_2, labels_2 = ax2.get_legend_handles_labels()
ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper left')

def onclick(event):
    if event.xdata is None:
        return
    
    v = event.xdata

    vermogen = poly_new(v)
    vermogen_sleeptest = 0.1664 * v**3 + 1.1467 * v**2 - 4.3168 * v
    rendement = (vermogen_sleeptest / vermogen) * 100

    print(f"Snelheid: {v:.2f}")
    print(f"Vermogen: {vermogen:.2f}")
    print(f"Rendement: {rendement:.2f}%\n")

fig.canvas.mpl_connect('button_press_event', onclick)

plt.title(Title)
plt.grid(True)
plt.show()