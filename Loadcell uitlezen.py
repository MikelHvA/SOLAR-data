import pandas as pd
import matplotlib.pyplot as plt
# ================= INSTELLINGEN =================

CSV_BESTAND = "5_LoadCell_21_03.csv"

veld_tijd = 2       # Tijdveld in de CSV
veld_adc = 5        # ADC-waarde van de loadcell

UITVOER_BESTAND = "loadcell_kracht_N.csv"

Plot_title = "Loadcell kracht"

# ================= RANGES =================

x_min = None
x_max = None

y_min = None
y_max = None

# ================= KALIBRATIE =================

RICHTINGSCOEFFICIENT = -2.471E-05
STARTWAARDE = -5.583


def adc_naar_newton(adc):
    """
    Zet de ADC-waarde om naar kracht in newton.

    Formule:
        y = -2,471E-05 * x - 5,583
    """
    return RICHTINGSCOEFFICIENT * adc + STARTWAARDE


# ================= CSV INLEZEN =================

df = pd.read_csv(
    CSV_BESTAND,
    header=None,
    sep=",",
    comment="#",
    engine="python"
)

print(f"{CSV_BESTAND}: {df.shape[1]} kolommen ingelezen")

ix_tijd = veld_tijd - 1
ix_adc = veld_adc - 1

if ix_tijd >= df.shape[1]:
    raise ValueError(
        f"Tijdveld {veld_tijd} bestaat niet. "
        f"Het CSV-bestand heeft {df.shape[1]} kolommen."
    )

if ix_adc >= df.shape[1]:
    raise ValueError(
        f"ADC-veld {veld_adc} bestaat niet. "
        f"Het CSV-bestand heeft {df.shape[1]} kolommen."
    )

tijd = pd.to_numeric(df.iloc[:, ix_tijd], errors="coerce")
adc = pd.to_numeric(df.iloc[:, ix_adc], errors="coerce")

# ADC omrekenen naar kracht in N (inclusief hefboom staartstuk)
kracht_N = (0.2 * (adc_naar_newton(adc) * -1)) / 0.71

# Alleen regels gebruiken waarin tijd, ADC en kracht geldig zijn
mask = tijd.notna() & adc.notna() & kracht_N.notna()

if x_min is not None:
    mask &= tijd >= x_min

if x_max is not None:
    mask &= tijd <= x_max

resultaat = pd.DataFrame({
    "Tijd (s)": tijd[mask],
    "Loadcell ADC": adc[mask],
    "Kracht (N)": kracht_N[mask],
})

# ================= RESULTATEN OPSLAAN =================

resultaat.to_csv(UITVOER_BESTAND, index=False)

print(f"{len(resultaat)} geldige meetregels verwerkt")
print(f"Resultaten opgeslagen als: {UITVOER_BESTAND}")

# ================= PLOT =================

fig, ax = plt.subplots(figsize=(11, 5))

ax.plot(
    resultaat["Tijd (s)"],
    resultaat["Kracht (N)"],
    linestyle="solid",
    linewidth=2,
    marker=None,
    alpha=1.0,
    label="Loadcell – Kracht (N)"
)

ax.set_xlabel("Tijd (s)")
ax.set_ylabel("Kracht (N)")
ax.set_xlim(x_min, x_max)

if y_min is not None or y_max is not None:
    ax.set_ylim(y_min, y_max)

ax.grid(True)
ax.legend(loc="best")

fig.suptitle(Plot_title)
plt.tight_layout()
plt.show()