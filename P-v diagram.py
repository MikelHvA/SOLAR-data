import pandas as pd
import matplotlib.pyplot as plt

# ================= INSTELLINGEN =================

PLOT_TITLE = "Elektrisch en mechanisch vermogen t.o.v. vaarsnelheid - Rondje + Sprint Akkrum 2026 ster 5:1 "

CSV_BESTANDEN = {
    "Master": "1_Master_08_05.csv",
    "VESC": "7_VESC_20_02.csv",
    "Loadcell": "5_LoadCell_21_03.csv",
}

# ================= VELDEN =================
# De veldnummers beginnen bij 1, net zoals in je eerdere script.

VELD_TIJD = 2

VELD_SNELHEID = 18       # Master: snelheid t.o.v. water in km/h

VELD_MOTORSTROOM = 11    # VESC: motorstroom VESC in A
VELD_DUTY_CYCLE = 12     # VESC: duty-cycle tussen 0 en 1
VELD_SPANNING = 14       # VESC: ingangsspanning in V

VELD_LOADCELL_ADC = 5    # Loadcell: ADC-waarde

# ================= LOADCELLKALIBRATIE =================

RICHTINGSCOEFFICIENT = -2.471E-05
STARTWAARDE = -5.583

# De gemeten loadcellkracht wordt omgekeerd met * -1
LOADCELL_OMKEREN = True

# ================= HEFBOOMAFSTANDEN =================

L1 = 0.20   # afstand draaipunt tot loadcell in meter
L2 = 0.71   # afstand draaipunt tot schroef in meter

# ================= TIJDSYNCHRONISATIE =================

# Maximale afstand tussen twee gekoppelde tijdstippen.
# Pas dit aan wanneer de logfrequenties ver uit elkaar liggen.
TIJD_TOLERANTIE = 0.25


# ================= FILTERS =================

SNELHEID_MIN = 0
SNELHEID_MAX = 20

# Punten met negatieve of extreem hoge duty-cycle verwijderen
DUTY_MIN = 0
DUTY_MAX = 1

Y_AS_MIN = 0
Y_AS_MAX = None

# ================= CSV INLEZEN =================


def lees_csv(bestandsnaam):
    df = pd.read_csv(
        bestandsnaam,
        header=None,
        sep=",",
        comment="#",
        engine="python"
    )

    print(f"{bestandsnaam}: {df.shape[1]} kolommen ingelezen")
    return df


master_df = lees_csv(CSV_BESTANDEN["Master"])
vesc_df = lees_csv(CSV_BESTANDEN["VESC"])
loadcell_df = lees_csv(CSV_BESTANDEN["Loadcell"])

# ================= GEGEVENS SELECTEREN =================

# -1 omdat pandas vanaf kolom 0 telt
ix_tijd = VELD_TIJD - 1
ix_snelheid = VELD_SNELHEID - 1

ix_motorstroom = VELD_MOTORSTROOM - 1
ix_duty = VELD_DUTY_CYCLE - 1
ix_spanning = VELD_SPANNING - 1

ix_loadcell_adc = VELD_LOADCELL_ADC - 1

master = pd.DataFrame({
    "tijd": pd.to_numeric(
        master_df.iloc[:, ix_tijd],
        errors="coerce"
    ),
    "snelheid_kmh": pd.to_numeric(
        master_df.iloc[:, ix_snelheid],
        errors="coerce"
    ),
})

vesc = pd.DataFrame({
    "tijd": pd.to_numeric(
        vesc_df.iloc[:, ix_tijd],
        errors="coerce"
    ),
    "motorstroom_A": pd.to_numeric(
        vesc_df.iloc[:, ix_motorstroom],
        errors="coerce"
    ),
    "duty_cycle": pd.to_numeric(
        vesc_df.iloc[:, ix_duty],
        errors="coerce"
    ),
    "spanning_V": pd.to_numeric(
        vesc_df.iloc[:, ix_spanning],
        errors="coerce"
    ),
})

loadcell = pd.DataFrame({
    "tijd": pd.to_numeric(
        loadcell_df.iloc[:, ix_tijd],
        errors="coerce"
    ),
    "loadcell_adc": pd.to_numeric(
        loadcell_df.iloc[:, ix_loadcell_adc],
        errors="coerce"
    ),
})

# Ongeldige regels verwijderen
master = master.dropna().sort_values("tijd")
vesc = vesc.dropna().sort_values("tijd")
loadcell = loadcell.dropna().sort_values("tijd")

# Dubbele tijdstippen verwijderen
master = master.drop_duplicates(subset="tijd")
vesc = vesc.drop_duplicates(subset="tijd")
loadcell = loadcell.drop_duplicates(subset="tijd")

# ================= TIJDREEKSEN KOPPELEN =================
# Master wordt als basis gebruikt.
# De dichtstbijzijnde VESC- en loadcellmeting wordt gekoppeld.

data = pd.merge_asof(
    master,
    vesc,
    on="tijd",
    direction="nearest",
    tolerance=TIJD_TOLERANTIE
)

data = pd.merge_asof(
    data,
    loadcell,
    on="tijd",
    direction="nearest",
    tolerance=TIJD_TOLERANTIE
)

# Regels zonder gekoppelde meting verwijderen
data = data.dropna()

# ================= LOADCELL NAAR KRACHT =================

data["kracht_loadcell_N"] = (
    RICHTINGSCOEFFICIENT * data["loadcell_adc"]
    + STARTWAARDE
)

if LOADCELL_OMKEREN:
    data["kracht_loadcell_N"] *= -1

# Hefboomwerking:
# L1 * F_loadcell = L2 * F_schroef

data["kracht_schroef_N"] = (
    data["kracht_loadcell_N"] * L1 / L2
)

# ================= VERMOGENS BEREKENEN =================

# Vaarsnelheid omrekenen van km/h naar m/s
data["snelheid_ms"] = data["snelheid_kmh"] / 3.6

# Benadering elektrisch vermogen:
# spanning × motorstroom × duty-cycle
data["vermogen_elektrisch_W"] = (
    data["spanning_V"]
    * data["motorstroom_A"]
)

# Mechanisch/propulsief vermogen:
# schroefkracht × vaarsnelheid
data["vermogen_mechanisch_W"] = (
    data["kracht_schroef_N"]
    * data["snelheid_ms"]
)

# ================= REFERENTIE UIT SLEEPTEST =================

# Trendlijn uit de sleeptest:
# F = 0.6908 * v^2 + 1.4184 * v
# v in km/h, F in N

data["kracht_sleeptest_N"] = (
    0.6908 * data["snelheid_kmh"] ** 2
    + 1.4184 * data["snelheid_kmh"]
)

# Referentievermogen uit sleeptest
data["vermogen_sleeptest_W"] = (
    data["kracht_sleeptest_N"]
    * data["snelheid_ms"]
)

# ================= FILTERS =================

mask = (
    data["snelheid_kmh"].notna()
    & data["vermogen_elektrisch_W"].notna()
    & data["vermogen_mechanisch_W"].notna()
    & data["duty_cycle"].between(DUTY_MIN, DUTY_MAX)
)

if SNELHEID_MIN is not None:
    mask &= data["snelheid_kmh"] >= SNELHEID_MIN

if SNELHEID_MAX is not None:
    mask &= data["snelheid_kmh"] <= SNELHEID_MAX

if Y_AS_MIN is not None:
    mask &= data["vermogen_elektrisch_W"] >= Y_AS_MIN
    mask &= data["vermogen_mechanisch_W"] >= Y_AS_MIN

if Y_AS_MAX is not None:
    mask &= data["vermogen_elektrisch_W"] <= Y_AS_MAX
    mask &= data["vermogen_mechanisch_W"] <= Y_AS_MAX

data = data.loc[mask].copy()

# Sorteren op snelheid, zodat de lijnen niet heen en weer springen
data = data.sort_values("snelheid_kmh")

print(f"{len(data)} gekoppelde en geldige meetpunten")

# ================= RESULTATEN OPSLAAN =================

uitvoer = data[[
    "tijd",
    "snelheid_kmh",
    "snelheid_ms",
    "spanning_V",
    "motorstroom_A",
    "duty_cycle",
    "loadcell_adc",
    "kracht_loadcell_N",
    "kracht_schroef_N",
    "vermogen_elektrisch_W",
    "vermogen_mechanisch_W",
]]

uitvoer.to_csv(
    "vermogen_tov_vaarsnelheid.csv",
    index=False
)

print("Resultaten opgeslagen als vermogen_tov_vaarsnelheid.csv")

# ================= PLOT =================

fig, ax = plt.subplots(figsize=(11, 6))

scatter_elektrisch = ax.scatter(
    data["snelheid_kmh"],
    data["vermogen_elektrisch_W"],
    s=12,
    alpha=0.6,
    label="Elektrisch vermogen"
)

scatter_mechanisch = ax.scatter(
    data["snelheid_kmh"],
    data["vermogen_mechanisch_W"],
    s=12,
    alpha=0.6,
    label="Mechanisch vermogen loadcell"
)

lijn_sleeptest, = ax.plot(
    data["snelheid_kmh"],
    data["vermogen_sleeptest_W"],
    linewidth=2,
    label="Referentievermogen sleeptest",
    color ="green",
)

ax.set_xlabel("Vaarsnelheid (km/h)")
ax.set_ylabel("Vermogen (W)")
ax.grid(True)

legenda = ax.legend(loc="best")

grafiek_objecten = [
    scatter_elektrisch,
    scatter_mechanisch,
    lijn_sleeptest
]

koppeling = {}

for legenda_item, grafiek_item in zip(
    legenda.legend_handles,
    grafiek_objecten
):
    legenda_item.set_picker(True)
    koppeling[legenda_item] = grafiek_item


def bij_klik(event):
    legenda_item = event.artist
    grafiek_item = koppeling.get(legenda_item)

    if grafiek_item is None:
        return

    zichtbaar = not grafiek_item.get_visible()
    grafiek_item.set_visible(zichtbaar)

    legenda_item.set_alpha(
        1.0 if zichtbaar else 0.2
    )

    fig.canvas.draw_idle()


fig.canvas.mpl_connect("pick_event", bij_klik)
plt.title(PLOT_TITLE)
plt.tight_layout()
plt.show()