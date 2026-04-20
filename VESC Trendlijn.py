# Js berekenen testvaart.pyplot

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

K = 0.335  # Diametercoëfficiënt voor Js berekening  
W = 6   # Gearbox ratio

S = 0 #start tijd 
E = 6000 # eind tijd
T= '09 02-04-2026 water tenopzicht van de ondergrond'

df1_raw = pd.read_csv('/Users/mariekekok/Documents/plotten/09020426/1_Master_08_05.csv',  sep=',', header=None, comment='#')
df2_raw = pd.read_csv('/Users/mariekekok/Documents/plotten/09020426/7_VESC_20_02.csv', sep=',', header=None, comment='#')

df1 = pd.DataFrame({
    'Time': df1_raw[1],       # kolom 2 = tijd
    'Snelheid': df1_raw[10]   # kolom 10 = snelheid
})

df2 = pd.DataFrame({
    'Time': df2_raw[1],       # kolom 1 = tijd
    'A': df2_raw[10],        # kolom 10 = Ampere
    'V': df2_raw[13]        # kolom 13 = Voltage
})

df2['Vermogen'] = df2['A'] * df2['V']
# Zorg dat kolommen float zijn (zorgen dat er mee gerekend kan worden zonder fouten)
df1['Time'] = df1['Time'].astype(float)
df1['Snelheid'] = df1['Snelheid'].astype(float)
df2['Time'] = df2['Time'].astype(float)
df2['A'] = df2['A'].astype(float)
df2['V'] = df2['V'].astype(float)         

# Sorteren (vereist voor interpolatie / merge)
df1 = df1.sort_values("Time").reset_index(drop=True)
df2 = df2.sort_values("Time").reset_index(drop=True)

# Interpoleer RPM naar de tijdstippen van Snelheid
rpm_interpolated = np.interp(df1['Time'], df2['Time'], df2['A'] * df2['V'])  # Vermogen interpoleren in plaats van RPM

# Voeg geïnterpoleerde RPM toe aan df1
df1['RPM'] = rpm_interpolated

df2.plot(x='Time', y='Vermogen', kind='line')

# 4. Voeg wat styling toe
plt.title('Verkoopoverzicht')
plt.xlabel('time')
plt.ylabel('vermogen')
plt.grid(True)

# 5. Toon de plot
plt.show()

#plot Vermogen vs Snelheid
plt.figure()
ax = df1.plot(x='Snelheid', y='RPM', kind='scatter', label='Data punten', color='blue')


# Voeg trendlijn 2 toe
x_trend = np.sort(np.array(df1['Snelheid'].dropna()))
y_trend = 0.1664 * x_trend**3 + 1.1467 * x_trend**2 - 4.3168 * x_trend
ax.plot(x_trend, y_trend, color='pink', label='Trendlijn 2 sleeptest', linewidth=2)

# De X-as laten lopen van 0 tot 17
ax.set_xlim(0, 17)

# De Y-as laten lopen van 0 tot 1500
ax.set_ylim(0, 1500)

# 4. Voeg wat styling toe
plt.title('Vermogen vs Snelheid')
plt.xlabel('Snelheid')
plt.ylabel('Vermogen')
plt.legend()
plt.grid(True)

# 5. Toon de plot
plt.show() 

