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

CSV_GPS    = "7_SDR_xx_02.csv"      # Voor 2025--> geldt CSV_GPS = "1_master_08_05.csv", voor 2024 en ouder geldt CSV_GPS = "7_SDR_xx_02.csv"
CSV_MASTER = "1_Master_08_05.csv" 
CSV_VESC   = "7_VESC_20_02.csv"     # Voor 2025--> geldt CSV_VESC = "7_VESC_20_02csv", voor 2024 en ouder geldt CSV_VESC = "B_VESC_20_02.csv"
kolom_tijd     = 2
kolom_lat      = 7                        # 24 voor oude format, alleen van toepassing voor 2024 of ouder (SDR) ander 7
kolom_lat_ns   = 8                         # 25 voor oude format (SDR) anders 8
kolom_lon      = 9                         # 26 voor oude format (SDR) anders 9
kolom_lon_ew   = 10                        # 27 voor oude format (SDR) anders 10
kolom_snelheid = 18      # uit master
kolom_rpm      = 13      # uit VESC

# Filters
tijd_min = None
tijd_max = None

snelheid_min = None
snelheid_max = 18

RPM_min = None
RPM_max = None

Reductiekast_verhouding = 7 # Overbrenging van motor naar schroefas

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

df_gps = pd.read_csv(CSV_GPS, header=None, sep=",", comment="#", engine="python", on_bad_lines="skip")

gps = pd.DataFrame({
    "tijd":     pd.to_numeric(df_gps.iloc[:, kolom_tijd - 1], errors="coerce"),
    "lat_raw":  pd.to_numeric(df_gps.iloc[:, kolom_lat - 1], errors="coerce"),
    "lat_ns":   df_gps.iloc[:, kolom_lat_ns - 1],
    "lon_raw":  pd.to_numeric(df_gps.iloc[:, kolom_lon - 1], errors="coerce"),
    "lon_ew":   df_gps.iloc[:, kolom_lon_ew - 1],
}).dropna()

# ================= MASTER CSV =================

df_master = pd.read_csv(CSV_MASTER, header=None, sep=",", comment="#", engine="python", on_bad_lines="skip")

master = pd.DataFrame({
    "tijd": pd.to_numeric(df_master.iloc[:, kolom_tijd - 1], errors="coerce"),
    "snelheid": pd.to_numeric(df_master.iloc[:, kolom_snelheid - 1], errors="coerce"),
}).dropna()

# ================= VESC CSV =================

df_vesc = pd.read_csv(CSV_VESC, header=None, sep=",", comment="#", engine="python", on_bad_lines="skip")

vesc = pd.DataFrame({
    "tijd": pd.to_numeric(df_vesc.iloc[:, kolom_tijd - 1], errors="coerce"),
    "rpm": pd.to_numeric(df_vesc.iloc[:, kolom_rpm - 1], errors="coerce"),
}).dropna()

# ================= COORDINATEN =================

gps["lat"] = dm_to_dd(gps["lat_raw"])
gps["lon"] = dm_to_dd(gps["lon_raw"])

gps["lat"] = gps.apply(lambda r: apply_hemisphere(r["lat"], r["lat_ns"]), axis=1)
gps["lon"] = gps.apply(lambda r: apply_hemisphere(r["lon"], r["lon_ew"]), axis=1)

# ================= TIJD KOPPELEN =================

gps = gps.sort_values("tijd")
master = master.sort_values("tijd")
vesc = vesc.sort_values("tijd")

gps = pd.merge_asof(
    gps,
    master,
    on="tijd",
    direction="nearest",
    tolerance=1.0
).dropna(subset=["snelheid"])

gps = pd.merge_asof(
    gps,    
    vesc,
    on="tijd",
    direction="nearest",
    tolerance=1.0
)

gps["rpm_schroef"] = gps["rpm"] / Reductiekast_verhouding


# ================= FILTERS =================

if tijd_min is not None:
    gps = gps[gps["tijd"] >= tijd_min]

if tijd_max is not None:
    gps = gps[gps["tijd"] <= tijd_max]

if snelheid_min is not None:
    gps = gps[gps["snelheid"] >= snelheid_min]

if snelheid_max is not None:
    gps = gps[gps["snelheid"] <= snelheid_max]

if RPM_min is not None:
    gps = gps[gps["rpm"] >= RPM_min]

if RPM_max is not None:
    gps = gps[gps["rpm"] <= RPM_max]

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
    (
        f"Tijd: {t:.1f}s"
        f"<br>Snelheid: {v:.2f} km/h"
        f"<br>RPM motor: {r:.0f} ({rs:.0f})"
    )
    if pd.notna(r) else
    (
        f"Tijd: {t:.1f}s"
        f"<br>Snelheid: {v:.2f} km/h"
        f"<br>RPM motor: n.v.t."
    )
    for t, v, r, rs in zip(
        gps["tijd"],
        gps["snelheid"],
        gps["rpm"],
        gps["rpm_schroef"],
    )
],
name = "SOLAR"   
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
    legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
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
print(f"GPS regels: {len(df_gps)}")
print(f"MASTER regels: {len(df_master)}")
print(f"VESC regels: {len(df_vesc)}")


