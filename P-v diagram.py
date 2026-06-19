import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

from pathlib import Path


# ================= INSTELLINGEN =================

PLOT_TITLE = (
    "Elektrisch en mechanisch vermogen t.o.v. vaarsnelheid "
    "- Amstel 15-06-2026 ster 8:1 (Incapa)"
)

CSV_BESTANDEN = {
    "Master": "1_Master_08_05.csv",
    "VESC": "7_VESC_20_02.csv",
    "Loadcell": "5_LoadCell_21_03.csv",
}


# ================= VELDEN =================
# Veldnummers beginnen bij 1.

VELD_TIJD = 2

# Master
VELD_SNELHEID = 11

# VESC
VELD_INGANGSSTROOM = 11
VELD_SPANNING = 14

# Loadcell
VELD_LOADCELL_ADC = 6


# ================= LOADCELLKALIBRATIE =================

RICHTINGSCOEFFICIENT = -2E-06 #-2.471E-05
STARTWAARDE = -4.457 #-5.583

LOADCELL_OMKEREN = True

# ================= TIJDSYNCHRONISATIE =================

TIJD_TOLERANTIE = 0.25


# ================= FILTERS =================

TIJD_MIN = None
TIJD_MAX = None

SNELHEID_MIN = 0
SNELHEID_MAX = 15

Y_AS_MIN = 0
Y_AS_MAX = None


# ================= TRENDLIJN =================

ELEKTRISCHE_TRENDLIJN = True

# 2 = tweedegraads
# 3 = derdegraads
TREND_GRAAD = 3


# ================= WEERGAVE MEETPUNTEN =================
# Jitter verandert alleen de horizontale weergave.
# De echte snelheid en alle berekeningen blijven ongewijzigd.

X_JITTER = 0.10

MARKER_GROOTTE = 8
MARKER_ALPHA = 0.35

# Met een vaste seed ziet de willekeurige spreiding
# er bij iedere uitvoering hetzelfde uit.
JITTER_SEED = 42


# ================= CSV INLEZEN =================

def lees_csv(bestandsnaam, naam):
    bestand = Path(bestandsnaam)

    if not bestand.exists():
        print(
            f"WAARSCHUWING: {naam}-bestand niet gevonden: "
            f"{bestandsnaam}"
        )
        return None

    try:
        df = pd.read_csv(
            bestand,
            header=None,
            sep=",",
            comment="#",
            engine="python"
        )

        print(
            f"{naam}: {df.shape[0]} regels en "
            f"{df.shape[1]} kolommen ingelezen"
        )

        return df

    except Exception as fout:
        print(
            f"WAARSCHUWING: {naam} kon niet worden ingelezen: "
            f"{fout}"
        )
        return None


master_df = lees_csv(
    CSV_BESTANDEN["Master"],
    "Master"
)

vesc_df = lees_csv(
    CSV_BESTANDEN["VESC"],
    "VESC"
)

loadcell_df = lees_csv(
    CSV_BESTANDEN["Loadcell"],
    "Loadcell"
)


# ================= KOLOMINDEXEN =================

ix_tijd = VELD_TIJD - 1
ix_snelheid = VELD_SNELHEID - 1

ix_ingangsstroom = VELD_INGANGSSTROOM - 1
ix_spanning = VELD_SPANNING - 1

ix_loadcell_adc = VELD_LOADCELL_ADC - 1


# ================= GEGEVENS SELECTEREN =================

master = None
vesc = None
loadcell = None


# ---------- Master ----------

if master_df is not None:

    benodigde_index = max(
        ix_tijd,
        ix_snelheid
    )

    if benodigde_index < master_df.shape[1]:

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

        master = (
            master
            .dropna(subset=["tijd", "snelheid_kmh"])
            .sort_values("tijd")
            .drop_duplicates(subset="tijd")
        )

    else:
        print(
            "WAARSCHUWING: benodigde Master-velden ontbreken"
        )


# ---------- VESC ----------

if vesc_df is not None:

    benodigde_index = max(
        ix_tijd,
        ix_ingangsstroom,
        ix_spanning
    )

    if benodigde_index < vesc_df.shape[1]:

        vesc = pd.DataFrame({
            "tijd": pd.to_numeric(
                vesc_df.iloc[:, ix_tijd],
                errors="coerce"
            ),
            "ingangsstroom_A": pd.to_numeric(
                vesc_df.iloc[:, ix_ingangsstroom],
                errors="coerce"
            ),
            "spanning_V": pd.to_numeric(
                vesc_df.iloc[:, ix_spanning],
                errors="coerce"
            ),
        })

        vesc = (
            vesc
            .dropna(subset=["tijd"])
            .sort_values("tijd")
            .drop_duplicates(subset="tijd")
        )

    else:
        print(
            "WAARSCHUWING: benodigde VESC-velden ontbreken"
        )


# ---------- Loadcell ----------

if loadcell_df is not None:

    benodigde_index = max(
        ix_tijd,
        ix_loadcell_adc
    )

    if benodigde_index < loadcell_df.shape[1]:

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

        loadcell = (
            loadcell
            .dropna(subset=["tijd"])
            .sort_values("tijd")
            .drop_duplicates(subset="tijd")
        )

    else:
        print(
            "WAARSCHUWING: benodigde loadcellvelden ontbreken"
        )


# ================= MASTER CONTROLEREN =================

if master is None or master.empty:
    raise FileNotFoundError(
        "De Master-CSV is nodig omdat deze de vaarsnelheid bevat."
    )


# ================= TIJDREEKSEN KOPPELEN =================

data = master.copy()


if vesc is not None and not vesc.empty:

    data = pd.merge_asof(
        data.sort_values("tijd"),
        vesc.sort_values("tijd"),
        on="tijd",
        direction="nearest",
        tolerance=TIJD_TOLERANTIE
    )

    print("VESC-data gekoppeld")

else:
    print("VESC-data niet beschikbaar")


if loadcell is not None and not loadcell.empty:

    data = pd.merge_asof(
        data.sort_values("tijd"),
        loadcell.sort_values("tijd"),
        on="tijd",
        direction="nearest",
        tolerance=TIJD_TOLERANTIE
    )

    print("Loadcelldata gekoppeld")

else:
    print("Loadcelldata niet beschikbaar")


# ================= ALGEMENE BEREKENINGEN =================

data["snelheid_ms"] = (
    data["snelheid_kmh"] / 3.6
)


# ================= ELEKTRISCH VERMOGEN =================

benodigde_elektrische_kolommen = {
    "spanning_V",
    "ingangsstroom_A"
}

if benodigde_elektrische_kolommen.issubset(data.columns):

    data["vermogen_elektrisch_W"] = (
        data["spanning_V"]
        * data["ingangsstroom_A"]
    )

    print("Elektrisch vermogen berekend")

else:
    print(
        "Elektrisch vermogen overgeslagen: "
        "VESC-data ontbreekt"
    )


# ================= MECHANISCH VERMOGEN =================
# De kalibratieformule geeft direct de kracht bij de schroef.
# Er wordt daarom geen hefboomverhouding meer toegepast.

if "loadcell_adc" in data.columns:

    data["kracht_schroef_N"] = (
        RICHTINGSCOEFFICIENT
        * data["loadcell_adc"]
        + STARTWAARDE
    )

    if LOADCELL_OMKEREN:
        data["kracht_schroef_N"] *= -1

    data["vermogen_mechanisch_W"] = (
        data["kracht_schroef_N"]
        * data["snelheid_ms"]
    )

    print("Mechanisch vermogen berekend")

else:
    print(
        "Mechanisch vermogen overgeslagen: "
        "loadcelldata ontbreekt"
    )

# ================= REFERENTIE UIT SLEEPTEST =================

data["kracht_sleeptest_N"] = (
    0.6908 * data["snelheid_kmh"] ** 2
    + 1.4184 * data["snelheid_kmh"]
)

data["vermogen_sleeptest_W"] = (
    data["kracht_sleeptest_N"]
    * data["snelheid_ms"]
)


# ================= ALGEMENE FILTERS =================

mask = data["snelheid_kmh"].notna()


if TIJD_MIN is not None:
    mask &= data["tijd"] >= TIJD_MIN

if TIJD_MAX is not None:
    mask &= data["tijd"] <= TIJD_MAX

if SNELHEID_MIN is not None:
    mask &= data["snelheid_kmh"] >= SNELHEID_MIN

if SNELHEID_MAX is not None:
    mask &= data["snelheid_kmh"] <= SNELHEID_MAX


data = data.loc[mask].copy()

data = data.replace(
    [np.inf, -np.inf],
    np.nan
)

data = data.sort_values("snelheid_kmh")

print(
    f"{len(data)} meetpunten na tijd- en snelheidsfilter"
)


# ================= JITTER VOOR DE WEERGAVE =================
# Deze kolom wordt alleen voor de scatterpunten gebruikt.

rng = np.random.default_rng(
    JITTER_SEED
)

data["snelheid_plot_kmh"] = (
    data["snelheid_kmh"]
    + rng.normal(
        loc=0,
        scale=X_JITTER,
        size=len(data)
    )
)


# ================= ELEKTRISCHE TRENDLIJN =================
# De trendlijn gebruikt snelheid_kmh, dus niet snelheid_plot_kmh.

trend_data = None

if (
    ELEKTRISCHE_TRENDLIJN
    and "vermogen_elektrisch_W" in data.columns
):

    trend_data = data.dropna(
        subset=[
            "snelheid_kmh",
            "vermogen_elektrisch_W"
        ]
    ).copy()

    minimaal_aantal_punten = TREND_GRAAD + 1

    if len(trend_data) >= minimaal_aantal_punten:

        try:
            coefficienten = np.polyfit(
                trend_data["snelheid_kmh"],
                trend_data["vermogen_elektrisch_W"],
                TREND_GRAAD
            )

            trend_functie = np.poly1d(
                coefficienten
            )

            # Een vloeiende x-reeks voor een nette trendlijn
            trend_x = np.linspace(
                trend_data["snelheid_kmh"].min(),
                trend_data["snelheid_kmh"].max(),
                300
            )

            trend_y = trend_functie(
                trend_x
            )

            print("Elektrische trendlijn:")
            print(trend_functie)

        except (
            np.linalg.LinAlgError,
            ValueError,
            TypeError
        ) as fout:

            print(
                "Elektrische trendlijn kon niet worden berekend: "
                f"{fout}"
            )

            trend_data = None

    else:
        print(
            "Elektrische trendlijn overgeslagen: "
            "te weinig geldige meetpunten"
        )

        trend_data = None


# ================= PLOT =================

fig, ax = plt.subplots(
    figsize=(11, 6)
)

grafiek_objecten = []


# ---------- Elektrisch vermogen ----------

if "vermogen_elektrisch_W" in data.columns:

    elektrisch_data = data.dropna(
        subset=[
            "snelheid_plot_kmh",
            "vermogen_elektrisch_W"
        ]
    )

    if not elektrisch_data.empty:

        scatter_elektrisch = ax.scatter(
            elektrisch_data["snelheid_plot_kmh"],
            elektrisch_data["vermogen_elektrisch_W"],
            s=MARKER_GROOTTE,
            alpha=MARKER_ALPHA,
            label="Elektrisch vermogen"
        )

        grafiek_objecten.append(
            scatter_elektrisch
        )


# ---------- Elektrische trendlijn ----------

if trend_data is not None:

    lijn_elektrisch_trend, = ax.plot(
        trend_x,
        trend_y,
        linewidth=2,
        label="Trendlijn elektrisch vermogen",
        color="pink"
    )

    grafiek_objecten.append(
        lijn_elektrisch_trend
    )


# ---------- Mechanisch vermogen ----------

if "vermogen_mechanisch_W" in data.columns:

    mechanisch_data = data.dropna(
        subset=[
            "snelheid_plot_kmh",
            "vermogen_mechanisch_W"
        ]
    )

    if not mechanisch_data.empty:

        scatter_mechanisch = ax.scatter(
            mechanisch_data["snelheid_plot_kmh"],
            mechanisch_data["vermogen_mechanisch_W"],
            s=MARKER_GROOTTE,
            alpha=MARKER_ALPHA,
            label="Mechanisch vermogen loadcell"
        )

        grafiek_objecten.append(
            scatter_mechanisch
        )


# ---------- Sleeptest ----------

sleeptest_data = data.dropna(
    subset=[
        "snelheid_kmh",
        "vermogen_sleeptest_W"
    ]
).sort_values(
    "snelheid_kmh"
)

if not sleeptest_data.empty:

    lijn_sleeptest, = ax.plot(
        sleeptest_data["snelheid_kmh"],
        sleeptest_data["vermogen_sleeptest_W"],
        linewidth=2,
        label="Referentievermogen sleeptest",
        color="green"
    )

    grafiek_objecten.append(
        lijn_sleeptest
    )


# ================= PLOT CONTROLEREN =================

if not grafiek_objecten:
    raise RuntimeError(
        "Er zijn geen beschikbare gegevens om te plotten."
    )


# ================= PLOTOPMAAK =================

ax.set_xlabel(
    "Vaarsnelheid (km/h)"
)

ax.set_ylabel(
    "Vermogen (W)"
)

ax.set_title(
    PLOT_TITLE
)

if (
    Y_AS_MIN is not None
    or Y_AS_MAX is not None
):
    ax.set_ylim(
        Y_AS_MIN,
        Y_AS_MAX
    )

ax.grid(True)


# ================= KLIKBARE LEGENDA =================

legenda = ax.legend(
    loc="best"
)

koppeling = {}

for legenda_item, grafiek_item in zip(
    legenda.legend_handles,
    grafiek_objecten
):
    legenda_item.set_picker(True)

    if hasattr(
        legenda_item,
        "set_pickradius"
    ):
        legenda_item.set_pickradius(5)

    koppeling[legenda_item] = grafiek_item


def bij_klik(event):
    legenda_item = event.artist

    grafiek_item = koppeling.get(
        legenda_item
    )

    if grafiek_item is None:
        return

    zichtbaar = not grafiek_item.get_visible()

    grafiek_item.set_visible(
        zichtbaar
    )

    legenda_item.set_alpha(
        1.0 if zichtbaar else 0.2
    )

    fig.canvas.draw_idle()


fig.canvas.mpl_connect(
    "pick_event",
    bij_klik
)


plt.tight_layout()
plt.show()