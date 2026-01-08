import pandas as pd
import matplotlib.pyplot as plt

# ================= INSTELLINGEN =================

Plot_title = "Alles in een" # Titel van de plot

CSV_BESTANDEN = {
    "Master": "1_Master_08_05.csv",
    "VESC":   "7_VESC_20_02.csv",
    "MPPT1":  "2_MPPT_0_05_07.csv",
    "MPPT2":  "A_MPPT_1_05_07.csv",
    "MPPT3":  "B_MPPT_2_05_07.csv",
    "MPPT4":  "8_MPPT_3_05_07.csv",
    "MPPT5":  "9_MPPT_4_05_07.csv",
}

veld_x = 2   # dataloggertijd

# ================= Ranges =================
x_min = 2000
x_max = 3000

y_left_min  = 0
y_left_max  = None

y_right_min = 0
y_right_max = None
# ================= LIJNEN voorbeelden typen =================

# Standaard formaat, gebruik deze als template: (zonder #) 

#    {
#        "csv": "Master",       (welke csv uit CSV_BESTANDEN)
#        "veld": 10,            (welk veld uit de csv)
#        "as": "links",         (linker of rechter y-as)
#        "smooth": False,       (Wel of geen smoothing)
#        "window": 15,          (Smooth factor, hoger hoe meer)
#        "linestyle": "solid",  (lijnstijl: solid, dashed, dashdot, dotted)
#        "linewidth": 2,        (lijn dikte)
#        "marker": None,        (marker type: ., o, v, ^,)
#        "markersize": 3,       (marker grootte)
#        "alpha": 1.0,          (doorzichtigheid 0-1)
#    },

# Copy paste deze onder lijnen, gebruik of linestyle of marker op "None" zetten om ze uit te zetten.

# Toevoegen iqr= (onder "alpha":1.0,)
#   "filter": "iqr", #iqr, rolling_z, None
#   "k": 1.5

# Toevoegen rolling_z=
#   "filter": "rolling_z", 
#   "z_window": 50,
#   "z": 3.0


# ================= LIJNEN =================
LIJNEN = [
 
    {
        "csv": "Master",
        "veld": 18,
        "as": "links",
        "smooth": False,
        "window": 15,
        "linestyle": "None",
        "marker": ".",
        "markersize": 3,
        "alpha": 0.8,
    },
    
]

# ================= VELDNAMEN =================
VELDNAAM = {
    "Master": {
        2: "Tijd (s)",
        4: "Cycle count (-)",
        5: "Tijd (s)",
        7: "Latitude (°)", 
        9: "Longitude (°)",
        11: "Snelheid over de grond (km/h)",
        12: "Richting van de snelheid (°)",
        18: "Snelheid t.o.v. water (km/h)",
        19: "Board Temperatuur (°C)",
    },
    "VESC": {
        2: "Tijd (s)",
        4: "Tijd sinds boot (s)",
        10: "Motorstroom (A)",
        14: "Ingangsspanning VESC (V)",
    },
    "MPPT1": {
        2: "Tijd (s)",
        5: "Paneel 1 ingangsspanning (V)",
        6: "Paneel 1 ingangsstroom (A)",
        7: "Paneel 1 instantaan ingangsvermogen (W)",
        8: "Paneel 1 totale ingangsenergie (J)",
        9: "Paneel 2 ingangsspanning (V)",
        10: "Paneel 2 ingangsstroom (A)",
        11: "Paneel 2 instantaan ingangsvermogen (W)",
        12: "Paneel 2 totale ingangsenergie (J)",
        13: "Uitgangsspanning (V)",
        14: "Kanaal 1 uitgangsstroom (A)",
        15: "Kanaal 2 uitgangsstroom (A)",
        16: "Kanaal 1 instantaan uitgangsvermogen (W)",
        17: "Kanaal 2 instantaan uitgangsvermogen (W)",
        18: "Kanaal 1 totale energie (J)",
        19: "Kanaal 2 totale energie (J)",
        20: "Paneel 1 temperatuur (°C)",
        21: "Paneel 2 temperatuur (°C)",
        22: "Kanaal 1 temperatuur (fets) (°C)",
        23: "Kanaal 2 temperatuur (fets) (°C)",
        25: "Kanaal 1 DAC waarde, in 12 bits ",
        26: "Kanaal 2 DAC waarde, in 12 bits ",
        34: "Berekende zoninval pyranometer, in W/m2 (ongekalibreerd)",
        35: "Ruwe meetwaarde pyranometer",
    },
    "MPPT2": {
        2: "Tijd (s)",
        5: "Paneel 1 ingangsspanning (V)",
        6: "Paneel 1 ingangsstroom (A)",
        7: "Paneel 1 instantaan ingangsvermogen (W)",
        8: "Paneel 1 totale ingangsenergie (J)",
        9: "Paneel 2 ingangsspanning (V)",
        10: "Paneel 2 ingangsstroom (A)",
        11: "Paneel 2 instantaan ingangsvermogen (W)",
        12: "Paneel 2 totale ingangsenergie (J)",
        13: "Uitgangsspanning (V)",
        14: "Kanaal 1 uitgangsstroom (A)",
        15: "Kanaal 2 uitgangsstroom (A)",
        16: "Kanaal 1 instantaan uitgangsvermogen (W)",
        17: "Kanaal 2 instantaan uitgangsvermogen (W)",
        18: "Kanaal 1 totale energie (J)",
        19: "Kanaal 2 totale energie (J)",
        20: "Paneel 1 temperatuur (°C)",
        21: "Paneel 2 temperatuur (°C)",
        22: "Kanaal 1 temperatuur (fets) (°C)",
        23: "Kanaal 2 temperatuur (fets) (°C)",
        25: "Kanaal 1 DAC waarde, in 12 bits ",
        26: "Kanaal 2 DAC waarde, in 12 bits ",
        34: "Berekende zoninval pyranometer, in W/m2 (ongekalibreerd)",
        35: "Ruwe meetwaarde pyranometer",
    },
    "MPPT3": {
        2: "Tijd (s)",
        5: "Paneel 1 ingangsspanning (V)",
        6: "Paneel 1 ingangsstroom (A)",
        7: "Paneel 1 instantaan ingangsvermogen (W)",
        8: "Paneel 1 totale ingangsenergie (J)",
        9: "Paneel 2 ingangsspanning (V)",
        10: "Paneel 2 ingangsstroom (A)",
        11: "Paneel 2 instantaan ingangsvermogen (W)",
        12: "Paneel 2 totale ingangsenergie (J)",
        13: "Uitgangsspanning (V)",
        14: "Kanaal 1 uitgangsstroom (A)",
        15: "Kanaal 2 uitgangsstroom (A)",
        16: "Kanaal 1 instantaan uitgangsvermogen (W)",
        17: "Kanaal 2 instantaan uitgangsvermogen (W)",
        18: "Kanaal 1 totale energie (J)",
        19: "Kanaal 2 totale energie (J)",
        20: "Paneel 1 temperatuur (°C)",
        21: "Paneel 2 temperatuur (°C)",
        22: "Kanaal 1 temperatuur (fets) (°C)",
        23: "Kanaal 2 temperatuur (fets) (°C)",
        25: "Kanaal 1 DAC waarde, in 12 bits ",
        26: "Kanaal 2 DAC waarde, in 12 bits ",
        34: "Berekende zoninval pyranometer, in W/m2 (ongekalibreerd)",
        35: "Ruwe meetwaarde pyranometer",
    },
    "MPPT4": {
        2: "Tijd (s)",
        5: "Paneel 1 ingangsspanning (V)",
        6: "Paneel 1 ingangsstroom (A)",
        7: "Paneel 1 instantaan ingangsvermogen (W)",
        8: "Paneel 1 totale ingangsenergie (J)",
        9: "Paneel 2 ingangsspanning (V)",
        10: "Paneel 2 ingangsstroom (A)",
        11: "Paneel 2 instantaan ingangsvermogen (W)",
        12: "Paneel 2 totale ingangsenergie (J)",
        13: "Uitgangsspanning (V)",
        14: "Kanaal 1 uitgangsstroom (A)",
        15: "Kanaal 2 uitgangsstroom (A)",
        16: "Kanaal 1 instantaan uitgangsvermogen (W)",
        17: "Kanaal 2 instantaan uitgangsvermogen (W)",
        18: "Kanaal 1 totale energie (J)",
        19: "Kanaal 2 totale energie (J)",
        20: "Paneel 1 temperatuur (°C)",
        21: "Paneel 2 temperatuur (°C)",
        22: "Kanaal 1 temperatuur (fets) (°C)",
        23: "Kanaal 2 temperatuur (fets) (°C)",
        25: "Kanaal 1 DAC waarde, in 12 bits ",
        26: "Kanaal 2 DAC waarde, in 12 bits ",
        34: "Berekende zoninval pyranometer, in W/m2 (ongekalibreerd)",
        35: "Ruwe meetwaarde pyranometer",
    },
    "MPPT5": {
        2: "Tijd (s)",
        5: "Paneel 1 ingangsspanning (V)",
        6: "Paneel 1 ingangsstroom (A)",
        7: "Paneel 1 instantaan ingangsvermogen (W)",
        8: "Paneel 1 totale ingangsenergie (J)",
        9: "Paneel 2 ingangsspanning (V)",
        10: "Paneel 2 ingangsstroom (A)",
        11: "Paneel 2 instantaan ingangsvermogen (W)",
        12: "Paneel 2 totale ingangsenergie (J)",
        13: "Uitgangsspanning (V)",
        14: "Kanaal 1 uitgangsstroom (A)",
        15: "Kanaal 2 uitgangsstroom (A)",
        16: "Kanaal 1 instantaan uitgangsvermogen (W)",
        17: "Kanaal 2 instantaan uitgangsvermogen (W)",
        18: "Kanaal 1 totale energie (J)",
        19: "Kanaal 2 totale energie (J)",
        20: "Paneel 1 temperatuur (°C)",
        21: "Paneel 2 temperatuur (°C)",
        22: "Kanaal 1 temperatuur (fets) (°C)",
        23: "Kanaal 2 temperatuur (fets) (°C)",
        25: "Kanaal 1 DAC waarde, in 12 bits ",
        26: "Kanaal 2 DAC waarde, in 12 bits ",
        34: "Berekende zoninval pyranometer, in W/m2 (ongekalibreerd)",
        35: "Ruwe meetwaarde pyranometer",
    }
}
# ===============================================


def smooth_series(y, window=15):
    return y.rolling(window=window, center=True).mean()


def filter_outliers_iqr(y, k=1.5):
    q1 = y.quantile(0.25)
    q3 = y.quantile(0.75)
    iqr = q3 - q1
    return y.where((y >= q1 - k * iqr) & (y <= q3 + k * iqr))


def filter_outliers_rolling_z(y, window=50, z=3.0):
    mean = y.rolling(window, center=True).mean()
    std = y.rolling(window, center=True).std()
    z_score = (y - mean) / std
    return y.where(z_score.abs() < z)


# ---------- gebruikte CSV’s ----------
gebruikte_csvs = sorted({cfg["csv"] for cfg in LIJNEN})

data = {}
for naam in gebruikte_csvs:
    df = pd.read_csv(
        CSV_BESTANDEN[naam],
        header=None,
        sep=",",
        comment="#",
        engine="python"
    )
    data[naam] = df
    print(f"{naam}: {df.shape[1]} kolommen ingelezen")


# ================= PLOT =================
kleuren = plt.cm.tab10.colors
fig, ax_left = plt.subplots(figsize=(11, 5))
ax_right = None

lines = []
labels = []

for i, cfg in enumerate(LIJNEN):
    kleur = kleuren[i % len(kleuren)]
    df = data[cfg["csv"]]

    ix_x = veld_x - 1
    ix_y = cfg["veld"] - 1

    if ix_x >= df.shape[1] or ix_y >= df.shape[1]:
        print(f"⚠ {cfg['csv']} veld {cfg['veld']} bestaat niet")
        continue

    x = pd.to_numeric(df.iloc[:, ix_x], errors="coerce")
    x_local = pd.to_numeric(df.iloc[:, ix_x], errors="coerce")
    y = pd.to_numeric(df.iloc[:, ix_y], errors="coerce")
    

    # ---------- uitschieter-filter ----------
    if cfg.get("filter") == "iqr":
        y = filter_outliers_iqr(y, k=cfg.get("k", 1.5))

    elif cfg.get("filter") == "rolling_z":
        y = filter_outliers_rolling_z(
            y,
            window=cfg.get("z_window", 50),
            z=cfg.get("z", 3.0)
        )

    # ---------- smoothing ----------
    if cfg.get("smooth"):
        y = smooth_series(y, cfg.get("window", 15))

    mask = x.notna() & y.notna()

    if x_min is not None:
        mask &= x >= x_min
    if x_max is not None:
        mask &= x <= x_max

    ax = ax_left
    if cfg["as"] == "rechts":
        if ax_right is None:
            ax_right = ax_left.twinx()
        ax = ax_right

    veldnaam = VELDNAAM[cfg["csv"]].get(cfg["veld"], f"Veld {cfg['veld']}")
    label = f"{cfg['csv']} – {veldnaam}"

    line, = ax.plot(
    x_local[mask],
    y[mask],
    linestyle=cfg.get("linestyle", "solid"),
    linewidth=cfg.get("linewidth", 2),
    marker=cfg.get("marker", None),
    markersize=cfg.get("markersize", 4),
    alpha=cfg.get("alpha", 1.0),
    color=kleur,
    label=label
    )

    lines.append(line)
    labels.append(label)


# ---------- labels ----------
ax_left.set_xlabel(VELDNAAM["Master"].get(veld_x, "Tijd"))
ax_left.set_ylabel(" / ".join(
    VELDNAAM[c["csv"]].get(c["veld"], f"Veld {c['veld']}")
    for c in LIJNEN if c["as"] == "links"
))

if ax_right:
    ax_right.set_ylabel(" / ".join(
        VELDNAAM[c["csv"]].get(c["veld"], f"Veld {c['veld']}")
        for c in LIJNEN if c["as"] == "rechts"
    ))

# ---------- ranges ----------
ax_left.set_xlim(x_min, x_max)

if y_left_min is not None or y_left_max is not None:
    ax_left.set_ylim(y_left_min, y_left_max)

if ax_right and (y_right_min is not None or y_right_max is not None):
    ax_right.set_ylim(y_right_min, y_right_max)

ax_left.grid(True)
ax_left.legend(lines, labels, loc="best")

fig.suptitle(Plot_title)
plt.tight_layout()
plt.show()
