import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

from pathlib import Path


# ================= INSTELLINGEN =================

PLOT_TITLE = "Dual-Prop Frankrijk  - vermogen t.o.v. vaarsnelheid ALU + PPS Driehoek 5:1"


# ================= TESTVAARTEN =================
# Zet hier alle testvaarten die je in één grafiek wilt tonen.
#
# map:
#   "." betekent: dezelfde map als waar je script draait.
#   Voor andere mappen gebruik je bijvoorbeeld:
#   r"C:\Users\mikel\OneDrive - HvA\Plotten\Testvaart_1"
#
# veld_snelheid:
#   18 = snelheid t.o.v. water
#   11 = snelheid t.o.v. grond

TESTVAARTEN = [
    {
        "naam": "Frankrijk Driehoek 5:1 16-05-2026 Incapblad Dag 3",
        "map": r"C:\Users\mikel\OneDrive - HvA\CleanMobility - SOLAR 25-26\2e jrs\Data\Vaartochten gebruikt voor data analyse\Frankrijk 2026\20260705_frankrijk_dag3\0089 - 20260705T064702 14h8m58s 113.622km Trevoux - Chalon-sur-Saone",

        "csv_master": "1_Master_08_05.csv",
        "csv_vesc": "5_VESC_20_02.csv",
        "csv_loadcell": "4_LoadCell_21_03.csv",

        "veld_snelheid": 18,
        "veld_loadcell_adc": 6,

        "tijd_min": 6935,
        "tijd_max": 48497,

        "snelheid_min": 0,
        "snelheid_max": 13,

        "richtingscoefficient": -2E-06,
        "startwaarde": -4.457,
        "loadcell_omkeren": True,
    },
    {
        "naam": "Frankrijk Driehoek 5:1 16-05-2026 Incapblad Dag 4",
        "map": r"C:\Users\mikel\OneDrive - HvA\CleanMobility - SOLAR 25-26\2e jrs\Data\Vaartochten gebruikt voor data analyse\Frankrijk 2026\20260707_frankrijk_dag4\0093 - 20260707T070216 13h58m27s 104.189km Durnal - Flemalle-Haute",

        "csv_master": "1_Master_08_05.csv",
        "csv_vesc": "5_VESC_20_02.csv",
        "csv_loadcell": "4_LoadCell_21_03.csv",

        "veld_snelheid": 18,
        "veld_loadcell_adc": 6,

        "tijd_min": 5633,
        "tijd_max": 48793,

        "snelheid_min": 0,
        "snelheid_max": 20,

        "richtingscoefficient": -2E-06,
        "startwaarde": -4.457,
        "loadcell_omkeren": True,
    },
    {
        "naam": "Frankrijk Driehoek 5:1 16-05-2026 Incapblad Dag 5",
        "map": r"C:\Users\mikel\OneDrive - HvA\CleanMobility - SOLAR 25-26\2e jrs\Data\Vaartochten gebruikt voor data analyse\Frankrijk 2026\20260708_frankrijk_dag5\0130 - 20260708T065114 14h57m20s 163.363km Durnal - Heel",

        "csv_master": "1_Master_08_05.csv",
        "csv_vesc": "5_VESC_20_02.csv",
        "csv_loadcell": "4_LoadCell_21_03.csv",

        "veld_snelheid": 18,
        "veld_loadcell_adc": 6,

        "tijd_min": 15673,
        "tijd_max": 52598,

        "snelheid_min": 0,
        "snelheid_max": 20,

        "richtingscoefficient": -2E-06,
        "startwaarde": -4.457,
        "loadcell_omkeren": True,
    },

    # Kopieer dit blok voor een tweede testvaart:
    #
    # {
    #     "naam": "Amstel 15-06-2026 ster 8:1 Incapa",
    #     "map": r"C:\Users\mikel\OneDrive - HvA\Plotten\Testvaart_15_06_2026",
    #
    #     "csv_master": "1_Master_08_05.csv",
    #     "csv_vesc": "7_VESC_20_02.csv",
    #     "csv_loadcell": "5_LoadCell_21_03.csv",
    #
    #     "veld_snelheid": 11,
    #     "veld_loadcell_adc": 5,
    #
    #     "tijd_min": 9240,
    #     "tijd_max": 13600,
    #
    #     "snelheid_min": 0,
    #     "snelheid_max": 20,
    #
    #     "richtingscoefficient": -2.471E-05,
    #     "startwaarde": -5.583,
    #     "loadcell_omkeren": True,
    # },
]


# ================= STANDAARD VELDEN =================
# Veldnummers beginnen bij 1.

VELD_TIJD = 2

VELD_INGANGSSTROOM = 11
VELD_SPANNING = 14


# ================= TIJDSYNCHRONISATIE =================

TIJD_TOLERANTIE = 0.25


# ================= PLOT FILTERS =================

Y_AS_MIN = 0
Y_AS_MAX = None


# ================= TRENDLIJN =================

ELEKTRISCHE_TRENDLIJN = True

# 2 = tweedegraads
# 3 = derdegraads
TREND_GRAAD = 3


# ================= WEERGAVE MEETPUNTEN =================

X_JITTER = 0.10

MARKER_GROOTTE = 8
MARKER_ALPHA = 0.55

# Alle scatterpunten krijgen kleur op basis van voortgang in de testvaart.
# 0% = begin van die testvaart, 100% = einde van die testvaart.
TIJD_KLEURENKAART = "viridis"

JITTER_SEED = 42


# ================= HULPFUNCTIES =================

def lees_csv(map_pad, bestandsnaam, naam):
    bestand = Path(map_pad) / bestandsnaam

    if not bestand.exists():
        print(
            f"WAARSCHUWING: {naam}-bestand niet gevonden: "
            f"{bestand}"
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


def maak_dataframe_master(df, veld_snelheid):
    ix_tijd = VELD_TIJD - 1
    ix_snelheid = veld_snelheid - 1

    if max(ix_tijd, ix_snelheid) >= df.shape[1]:
        raise ValueError(
            "Benodigde Master-velden ontbreken"
        )

    master = pd.DataFrame({
        "tijd": pd.to_numeric(
            df.iloc[:, ix_tijd],
            errors="coerce"
        ),
        "snelheid_kmh": pd.to_numeric(
            df.iloc[:, ix_snelheid],
            errors="coerce"
        ),
    })

    master = (
        master
        .dropna(subset=["tijd", "snelheid_kmh"])
        .sort_values("tijd")
        .drop_duplicates(subset="tijd")
    )

    return master


def maak_dataframe_vesc(df):
    ix_tijd = VELD_TIJD - 1
    ix_ingangsstroom = VELD_INGANGSSTROOM - 1
    ix_spanning = VELD_SPANNING - 1

    if max(ix_tijd, ix_ingangsstroom, ix_spanning) >= df.shape[1]:
        raise ValueError(
            "Benodigde VESC-velden ontbreken"
        )

    vesc = pd.DataFrame({
        "tijd": pd.to_numeric(
            df.iloc[:, ix_tijd],
            errors="coerce"
        ),
        "ingangsstroom_A": pd.to_numeric(
            df.iloc[:, ix_ingangsstroom],
            errors="coerce"
        ),
        "spanning_V": pd.to_numeric(
            df.iloc[:, ix_spanning],
            errors="coerce"
        ),
    })

    vesc = (
        vesc
        .dropna(subset=["tijd"])
        .sort_values("tijd")
        .drop_duplicates(subset="tijd")
    )

    return vesc


def maak_dataframe_loadcell(df, veld_loadcell_adc):
    ix_tijd = VELD_TIJD - 1
    ix_loadcell_adc = veld_loadcell_adc - 1

    if max(ix_tijd, ix_loadcell_adc) >= df.shape[1]:
        raise ValueError(
            "Benodigde loadcellvelden ontbreken"
        )

    loadcell = pd.DataFrame({
        "tijd": pd.to_numeric(
            df.iloc[:, ix_tijd],
            errors="coerce"
        ),
        "loadcell_adc": pd.to_numeric(
            df.iloc[:, ix_loadcell_adc],
            errors="coerce"
        ),
    })

    loadcell = (
        loadcell
        .dropna(subset=["tijd"])
        .sort_values("tijd")
        .drop_duplicates(subset="tijd")
    )

    return loadcell


def bereken_trendlijn(data, x_kolom, y_kolom, graad):
    trend_data = data[
        [x_kolom, y_kolom]
    ].replace(
        [np.inf, -np.inf],
        np.nan
    ).dropna().copy()

    if trend_data.empty:
        return None, None, None

    # Punten met exact dezelfde snelheid middelen.
    # Dit maakt polyfit stabieler bij verticale meetstroken.
    trend_data = (
        trend_data
        .groupby(x_kolom, as_index=False)[y_kolom]
        .mean()
        .sort_values(x_kolom)
    )

    aantal_unieke_snelheden = trend_data[x_kolom].nunique()
    gebruikte_graad = min(
        graad,
        aantal_unieke_snelheden - 1
    )

    if gebruikte_graad < 1:
        return None, None, None

    try:
        coefficienten = np.polyfit(
            trend_data[x_kolom].to_numpy(dtype=float),
            trend_data[y_kolom].to_numpy(dtype=float),
            gebruikte_graad
        )

        trend_functie = np.poly1d(
            coefficienten
        )

        trend_x = np.linspace(
            trend_data[x_kolom].min(),
            trend_data[x_kolom].max(),
            300
        )

        trend_y = trend_functie(
            trend_x
        )

        return trend_x, trend_y, trend_functie

    except (
        np.linalg.LinAlgError,
        ValueError,
        TypeError
    ) as fout:
        print(
            f"WAARSCHUWING: trendlijn kon niet worden berekend: {fout}"
        )
        return None, None, None


def verwerk_testvaart(testvaart, test_index):
    naam = testvaart["naam"]
    map_pad = testvaart.get("map", ".")

    print()
    print("=" * 70)
    print(f"Testvaart: {naam}")
    print("=" * 70)

    df_master = lees_csv(
        map_pad,
        testvaart.get("csv_master", "1_Master_08_05.csv"),
        f"{naam} - Master"
    )

    df_vesc = lees_csv(
        map_pad,
        testvaart.get("csv_vesc", "7_VESC_20_02.csv"),
        f"{naam} - VESC"
    )

    df_loadcell = lees_csv(
        map_pad,
        testvaart.get("csv_loadcell", "5_LoadCell_21_03.csv"),
        f"{naam} - Loadcell"
    )

    if df_master is None:
        print(
            f"{naam}: overgeslagen, want Master ontbreekt"
        )
        return None

    try:
        master = maak_dataframe_master(
            df_master,
            testvaart.get("veld_snelheid", 18)
        )
    except Exception as fout:
        print(
            f"{naam}: Master-data niet bruikbaar: {fout}"
        )
        return None

    if master.empty:
        print(
            f"{naam}: overgeslagen, geen geldige Master-data"
        )
        return None

    data = master.copy()

    # ---------- VESC koppelen ----------
    if df_vesc is not None:
        try:
            vesc = maak_dataframe_vesc(
                df_vesc
            )

            if not vesc.empty:
                data = pd.merge_asof(
                    data.sort_values("tijd"),
                    vesc.sort_values("tijd"),
                    on="tijd",
                    direction="nearest",
                    tolerance=TIJD_TOLERANTIE
                )

                print("VESC-data gekoppeld")

        except Exception as fout:
            print(
                f"WAARSCHUWING: VESC-data overgeslagen: {fout}"
            )
    else:
        print("VESC-data niet beschikbaar")

    # ---------- Loadcell koppelen ----------
    if df_loadcell is not None:
        try:
            loadcell = maak_dataframe_loadcell(
                df_loadcell,
                testvaart.get("veld_loadcell_adc", 5)
            )

            if not loadcell.empty:
                data = pd.merge_asof(
                    data.sort_values("tijd"),
                    loadcell.sort_values("tijd"),
                    on="tijd",
                    direction="nearest",
                    tolerance=TIJD_TOLERANTIE
                )

                print("Loadcelldata gekoppeld")

        except Exception as fout:
            print(
                f"WAARSCHUWING: loadcelldata overgeslagen: {fout}"
            )
    else:
        print("Loadcelldata niet beschikbaar")

    # ================= BEREKENINGEN =================

    data["snelheid_ms"] = (
        data["snelheid_kmh"] / 3.6
    )

    # ---------- Elektrisch vermogen ----------
    if {
        "spanning_V",
        "ingangsstroom_A"
    }.issubset(data.columns):

        data["vermogen_elektrisch_W"] = (
            data["spanning_V"]
            * data["ingangsstroom_A"]
        )

        print("Elektrisch vermogen berekend")

    else:
        print(
            "Elektrisch vermogen overgeslagen"
        )

    # ---------- Mechanisch vermogen ----------
    if "loadcell_adc" in data.columns:

        richtingscoefficient = testvaart.get(
            "richtingscoefficient",
            -2.471E-05
        )

        startwaarde = testvaart.get(
            "startwaarde",
            -5.583
        )

        loadcell_omkeren = testvaart.get(
            "loadcell_omkeren",
            True
        )

        data["kracht_schroef_N"] = (
            richtingscoefficient
            * data["loadcell_adc"]
            + startwaarde
        )

        if loadcell_omkeren:
            data["kracht_schroef_N"] *= -1

        data["vermogen_mechanisch_W"] = (
            data["kracht_schroef_N"]
            * data["snelheid_ms"]
        )

        print("Mechanisch vermogen berekend")

    else:
        print(
            "Mechanisch vermogen overgeslagen"
        )

    # ---------- Sleeptest ----------
    data["kracht_sleeptest_N"] = (
        0.6908 * data["snelheid_kmh"] ** 2
        + 1.4184 * data["snelheid_kmh"]
    )

    data["vermogen_sleeptest_W"] = (
        data["kracht_sleeptest_N"]
        * data["snelheid_ms"]
    )

    # ================= FILTERS =================

    mask = data["snelheid_kmh"].notna()

    tijd_min = testvaart.get("tijd_min", None)
    tijd_max = testvaart.get("tijd_max", None)

    snelheid_min = testvaart.get("snelheid_min", None)
    snelheid_max = testvaart.get("snelheid_max", None)

    if tijd_min is not None:
        mask &= data["tijd"] >= tijd_min

    if tijd_max is not None:
        mask &= data["tijd"] <= tijd_max

    if snelheid_min is not None:
        mask &= data["snelheid_kmh"] >= snelheid_min

    if snelheid_max is not None:
        mask &= data["snelheid_kmh"] <= snelheid_max

    data = data.loc[mask].copy()

    data = data.replace(
        [np.inf, -np.inf],
        np.nan
    )

    if data.empty:
        print(
            f"{naam}: geen meetpunten over na filters"
        )
        return None

    # ================= TIJD ALS KLEUR =================
    # Relatief per testvaart: 0% = begin, 100% = einde.

    tijd_min_data = data["tijd"].min()
    tijd_max_data = data["tijd"].max()

    if tijd_min_data == tijd_max_data:
        data["tijd_progressie_pct"] = 0
    else:
        data["tijd_progressie_pct"] = (
            (data["tijd"] - tijd_min_data)
            / (tijd_max_data - tijd_min_data)
            * 100
        )

    # ================= JITTER =================

    rng = np.random.default_rng(
        JITTER_SEED + test_index
    )

    data["snelheid_plot_kmh"] = (
        data["snelheid_kmh"]
        + rng.normal(
            loc=0,
            scale=X_JITTER,
            size=len(data)
        )
    )

    data = data.sort_values(
        "snelheid_kmh"
    )

    # ================= TRENDLIJN =================

    trend_x = None
    trend_y = None
    trend_functie = None

    if (
        ELEKTRISCHE_TRENDLIJN
        and "vermogen_elektrisch_W" in data.columns
    ):
        trend_x, trend_y, trend_functie = bereken_trendlijn(
            data,
            "snelheid_kmh",
            "vermogen_elektrisch_W",
            TREND_GRAAD
        )

        if trend_functie is not None:
            print("Elektrische trendlijn:")
            print(trend_functie)

    print(
        f"{naam}: {len(data)} meetpunten na filters"
    )

    return {
        "naam": naam,
        "data": data,
        "trend_x": trend_x,
        "trend_y": trend_y,
    }


# ================= TESTVAARTEN VERWERKEN =================

resultaten = []

for i, testvaart in enumerate(TESTVAARTEN):
    resultaat = verwerk_testvaart(
        testvaart,
        i
    )

    if resultaat is not None:
        resultaten.append(
            resultaat
        )

if not resultaten:
    raise RuntimeError(
        "Geen enkele testvaart kon worden verwerkt."
    )


# ================= PLOT =================

fig, ax = plt.subplots(
    figsize=(13, 7)
)

grafiek_objecten = []
tijdgekleurde_scatter_aanwezig = False

tijd_norm = plt.Normalize(
    vmin=0,
    vmax=100
)


# ================= TESTVAARTEN PLOTTEN =================

for resultaat in resultaten:
    naam = resultaat["naam"]
    data = resultaat["data"]

    # ---------- Elektrisch vermogen ----------
    if "vermogen_elektrisch_W" in data.columns:

        elektrisch_data = data.dropna(
            subset=[
                "snelheid_plot_kmh",
                "vermogen_elektrisch_W",
                "tijd_progressie_pct"
            ]
        )

        if not elektrisch_data.empty:

            scatter_elektrisch = ax.scatter(
                elektrisch_data["snelheid_plot_kmh"],
                elektrisch_data["vermogen_elektrisch_W"],
                c=elektrisch_data["tijd_progressie_pct"],
                cmap=TIJD_KLEURENKAART,
                norm=tijd_norm,
                marker="o",
                s=MARKER_GROOTTE,
                alpha=MARKER_ALPHA,
                label=f"{naam} - elektrisch"
            )

            grafiek_objecten.append(
                scatter_elektrisch
            )

            tijdgekleurde_scatter_aanwezig = True

    # ---------- Elektrische trendlijn ----------
    if (
        resultaat["trend_x"] is not None
        and resultaat["trend_y"] is not None
    ):
        lijn_elektrisch_trend, = ax.plot(
            resultaat["trend_x"],
            resultaat["trend_y"],
            linewidth=2,
            label=f"{naam} - trendlijn elektrisch"
        )

        grafiek_objecten.append(
            lijn_elektrisch_trend
        )

    # ---------- Mechanisch vermogen ----------
    if "vermogen_mechanisch_W" in data.columns:

        mechanisch_data = data.dropna(
            subset=[
                "snelheid_plot_kmh",
                "vermogen_mechanisch_W",
                "tijd_progressie_pct"
            ]
        )

        if not mechanisch_data.empty:

            scatter_mechanisch = ax.scatter(
                mechanisch_data["snelheid_plot_kmh"],
                mechanisch_data["vermogen_mechanisch_W"],
                c=mechanisch_data["tijd_progressie_pct"],
                cmap=TIJD_KLEURENKAART,
                norm=tijd_norm,
                marker="^",
                s=MARKER_GROOTTE,
                alpha=MARKER_ALPHA,
                label=f"{naam} - mechanisch"
            )

            grafiek_objecten.append(
                scatter_mechanisch
            )

            tijdgekleurde_scatter_aanwezig = True


# ================= SLEEPTEST REFERENTIE =================
# Eén algemene sleeptestlijn over het totale snelheidsbereik.

alle_snelheden = pd.concat(
    [
        resultaat["data"]["snelheid_kmh"]
        for resultaat in resultaten
    ],
    ignore_index=True
).dropna()

if not alle_snelheden.empty:

    snelheid_sleeptest = np.linspace(
        alle_snelheden.min(),
        alle_snelheden.max(),
        300
    )

    kracht_sleeptest_N = (
        0.6908 * snelheid_sleeptest ** 2
        + 1.4184 * snelheid_sleeptest
    )

    vermogen_sleeptest_W = (
        kracht_sleeptest_N
        * (snelheid_sleeptest / 3.6)
    )

    lijn_sleeptest, = ax.plot(
        snelheid_sleeptest,
        vermogen_sleeptest_W,
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


# ================= KLEURBALK VOOR TIJD =================

if tijdgekleurde_scatter_aanwezig:

    tijd_kleurmapper = plt.cm.ScalarMappable(
        norm=tijd_norm,
        cmap=TIJD_KLEURENKAART
    )

    tijd_kleurmapper.set_array([])

    kleurbar = fig.colorbar(
        tijd_kleurmapper,
        ax=ax,
        pad=0.02
    )

    kleurbar.set_label(
        "Voortgang binnen testvaart (%)"
    )


# ================= KLIKBARE LEGENDA =================

legenda = ax.legend(
    loc="best"
)

koppeling = {}

if hasattr(legenda, "legend_handles"):
    legenda_items = legenda.legend_handles
else:
    legenda_items = legenda.legendHandles

for legenda_item, grafiek_item in zip(
    legenda_items,
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