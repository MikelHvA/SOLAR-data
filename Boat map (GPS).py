import pandas as pd
import numpy as np
import plotly.graph_objects as go

from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

# ================= GEOLOCATIE =================

geolocator = Nominatim(user_agent="boat_gps_analysis")
reverse = RateLimiter(geolocator.reverse, min_delay_seconds=1)

def latlon_to_place(lat, lon):
    try:
        location = reverse((lat, lon), zoom=12, language="nl")
        if not location:
            return "Onbekende locatie"

        addr = location.raw.get("address", {})
        return (
            addr.get("city")
            or addr.get("town")
            or addr.get("village")
            or addr.get("municipality")
            or addr.get("hamlet")
            or "Onbekende locatie"
        )
    except Exception:
        return "Onbekende locatie"

# ================= INSTELLINGEN =================

CSV_GPS    = "7_SDR_xx_02.csv"
CSV_MASTER = "9_Master_08_05.csv"

kolom_tijd     = 2
kolom_lat      = 24
kolom_lat_ns   = 25
kolom_lon      = 26
kolom_lon_ew   = 27
kolom_snelheid = 18   # uit master

# Filters
tijd_min = None
tijd_max = None

snelheid_min = 1    # km/h
snelheid_max = None

# Detectie
STOP_SNELHEID_MAX = 1.0
STOP_DUUR_MIN = 60           # seconden
ANKER_MAX_AFSTAND_M = 15     # meter

MAX_AFSTAND_M = 50            # lijn breken

# ================= HULPFUNCTIES =================

def dm_to_dd(dm):
    deg = np.floor(dm / 100)
    minutes = dm - deg * 100
    return deg + minutes / 60

def apply_hemisphere(value, hemi):
    return -value if hemi in ["S", "W"] else value

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1 = np.radians(lat1)
    phi2 = np.radians(lat2)
    dphi = np.radians(lat2 - lat1)
    dlambda = np.radians(lon2 - lon1)

    a = (
        np.sin(dphi / 2)**2
        + np.cos(phi1) * np.cos(phi2) * np.sin(dlambda / 2)**2
    )
    return 2 * R * np.arcsin(np.sqrt(a))

# ================= GPS CSV =================

df_gps = pd.read_csv(CSV_GPS, header=None, sep=",", comment="#")

gps = pd.DataFrame({
    "tijd":     pd.to_numeric(df_gps.iloc[:, kolom_tijd - 1], errors="coerce"),
    "lat_raw":  pd.to_numeric(df_gps.iloc[:, kolom_lat - 1], errors="coerce"),
    "lat_ns":   df_gps.iloc[:, kolom_lat_ns - 1],
    "lon_raw":  pd.to_numeric(df_gps.iloc[:, kolom_lon - 1], errors="coerce"),
    "lon_ew":   df_gps.iloc[:, kolom_lon_ew - 1],
}).dropna()

# ================= MASTER CSV =================

df_master = pd.read_csv(CSV_MASTER, header=None, sep=",", comment="#")

master = pd.DataFrame({
    "tijd": pd.to_numeric(df_master.iloc[:, kolom_tijd - 1], errors="coerce"),
    "snelheid": pd.to_numeric(
        df_master.iloc[:, kolom_snelheid - 1], errors="coerce"
    ),
}).dropna()

# ================= COORDINATEN =================

gps["lat"] = dm_to_dd(gps["lat_raw"])
gps["lon"] = dm_to_dd(gps["lon_raw"])

gps["lat"] = gps.apply(lambda r: apply_hemisphere(r["lat"], r["lat_ns"]), axis=1)
gps["lon"] = gps.apply(lambda r: apply_hemisphere(r["lon"], r["lon_ew"]), axis=1)

# ================= TIJD KOPPELEN =================

gps = gps.sort_values("tijd")
master = master.sort_values("tijd")

gps = pd.merge_asof(
    gps,
    master,
    on="tijd",
    direction="nearest",
    tolerance=1.0
).dropna(subset=["snelheid"])

# ================= FILTERS =================

if tijd_min is not None:
    gps = gps[gps["tijd"] >= tijd_min]

if tijd_max is not None:
    gps = gps[gps["tijd"] <= tijd_max]

if snelheid_min is not None:
    gps = gps[gps["snelheid"] >= snelheid_min]

if snelheid_max is not None:
    gps = gps[gps["snelheid"] <= snelheid_max]

# ================= STOP / ANKER =================

gps["snelheid_smooth"] = (
    gps["snelheid"]
    .rolling(window=5, center=True, min_periods=1)
    .mean()
)

gps["is_stop"] = gps["snelheid_smooth"] <= STOP_SNELHEID_MAX
gps["stop_group"] = (gps["is_stop"] != gps["is_stop"].shift()).cumsum()

stops = []

for _, grp in gps[gps["is_stop"]].groupby("stop_group"):
    if len(grp) < 2:
        continue

    duur = grp["tijd"].iloc[-1] - grp["tijd"].iloc[0]
    if duur < STOP_DUUR_MIN:
        continue

    max_afstand = haversine(
        grp["lat"].iloc[0], grp["lon"].iloc[0],
        grp["lat"], grp["lon"]
    ).max()

    stops.append({
        "lat": grp["lat"].mean(),
        "lon": grp["lon"].mean(),
        "duur_s": duur,
        "max_afstand_m": max_afstand,
        "type": "Anker" if max_afstand <= ANKER_MAX_AFSTAND_M else "Stop",
        "tijd_start": grp["tijd"].iloc[0],
        "tijd_einde": grp["tijd"].iloc[-1],
    })

stops_df = pd.DataFrame(stops)

# ================= TITEL OP BASIS VAN GPS =================

plot_title = "Vaarroute"

if len(gps) >= 2:
    start_row = gps.iloc[0]
    end_row   = gps.iloc[-1]

    start_plek = latlon_to_place(start_row["lat"], start_row["lon"])
    eind_plek  = latlon_to_place(end_row["lat"], end_row["lon"])

    plot_title = (
        f"Vaarroute: {start_plek} → {eind_plek}"
        f"<br><sup>"
        f"Snelheidsfilter: {snelheid_min}–{snelheid_max} km/h"
        f"</sup>"
    )
else:
    plot_title = "Vaarroute (onvoldoende data na filter)"


# ================= AFSTAND FILTER =================

gps["afstand_m"] = haversine(
    gps["lat"].shift(),
    gps["lon"].shift(),
    gps["lat"],
    gps["lon"]
)

gps.loc[gps["afstand_m"] > MAX_AFSTAND_M, ["lat", "lon"]] = None

# ================= PLOT =================

fig = go.Figure()

fig.add_trace(go.Scattermapbox(
    lat=gps["lat"],
    lon=gps["lon"],
    mode="lines",
    connectgaps=False,
    line=dict(width=3, color="rgba(60,60,60,0.6)"),
    hoverinfo="skip",
    name="Vaarroute"
))

fig.add_trace(go.Scattermapbox(
    lat=gps["lat"],
    lon=gps["lon"],
    mode="markers",
    marker=dict(
        size=6,
        color=gps["snelheid"],
        colorscale="Turbo",
        colorbar=dict(title="Snelheid (km/h)")
    ),
    text=[
        f"Tijd: {t:.1f}s<br>Snelheid: {v:.2f} km/h"
        for t, v in zip(gps["tijd"], gps["snelheid"])
    ],
    name="Snelheid"
))

if not stops_df.empty:
    fig.add_trace(go.Scattermapbox(
        lat=stops_df["lat"],
        lon=stops_df["lon"],
        mode="markers",
        marker=dict(
            size=14,
            color=stops_df["type"].map({
                "Anker": "green",
                "Stop": "orange"
            })
        ),
        text=[
            f"{t}<br>Duur: {d:.0f}s<br>Drift: {m:.1f} m"
            for t, d, m in zip(
                stops_df["type"],
                stops_df["duur_s"],
                stops_df["max_afstand_m"]
            )
        ],
        name="Stops / Anker"
    ))

fig.update_layout(
    mapbox_style="open-street-map",
    mapbox_center=dict(
        lat=gps["lat"].mean(),
        lon=gps["lon"].mean()
    ),
    mapbox_zoom=8,
    title=plot_title,
    margin=dict(l=0, r=0, t=50, b=0)
)

fig.show()
filename = f"vaarroute_{start_plek}_naar_{eind_plek}.png".replace(" ", "_")
fig.write_image(filename, width=1600, height=900, scale=2)


