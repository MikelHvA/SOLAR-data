import pandas as pd
import plotly.express as px

# ================= INSTELLINGEN =================

CSV_MASTER = "9_Master_08_05.csv"

# Kolomnummers (1-based zoals in je CSV)
kolom_tijd      = 2    # Tijd (s)
kolom_lat       = 7    # Latitude ddmm.mmmm
kolom_lat_dir   = 8    # N / S
kolom_lon       = 9    # Longitude ddmm.mmmm
kolom_lon_dir   = 10   # E / W
kolom_snelheid  = 18   # Snelheid t.o.v. water (km/h)

plot_title = "GPS track boot – kleur = snelheid"

# =============== TIJD / SNELHEID FILTER ====================
# Gebruik None om uit te schakelen

tijd_min = None     # bijv. 2000
tijd_max = None     # bijv. 3800

snelheid_min = None  # bijv. 0.5
snelheid_max = None  # bijv. 15.0
# =================================================


# ---------- HULPFUNCTIES ----------

def ddmm_to_decimal(value):
    """
    Zet GPS-coördinaat in ddmm.mmmm formaat om naar decimale graden
    """
    if pd.isna(value):
        return None

    degrees = int(value // 100)
    minutes = value - degrees * 100
    return degrees + minutes / 60


# ---------- CSV INLEZEN ----------
df = pd.read_csv(
    CSV_MASTER,
    header=None,
    sep=",",
    comment="#",
    engine="python"
)

print(f"Ingelezen: {df.shape[0]} rijen, {df.shape[1]} kolommen")


# ---------- GPS DATAFRAME ----------
gps = pd.DataFrame({
    "tijd (s)": pd.to_numeric(df.iloc[:, kolom_tijd - 1], errors="coerce"),

    "lat_raw": pd.to_numeric(df.iloc[:, kolom_lat - 1], errors="coerce"),
    "lat_dir": df.iloc[:, kolom_lat_dir - 1].astype(str).str.upper(),

    "lon_raw": pd.to_numeric(df.iloc[:, kolom_lon - 1], errors="coerce"),
    "lon_dir": df.iloc[:, kolom_lon_dir - 1].astype(str).str.upper(),

    "snelheid (km/h)": pd.to_numeric(df.iloc[:, kolom_snelheid - 1], errors="coerce"),
})


# ---------- COÖRDINATEN OMREKENEN ----------
gps["lat"] = gps["lat_raw"].apply(ddmm_to_decimal)
gps["lon"] = gps["lon_raw"].apply(ddmm_to_decimal)

# N/S & E/W toepassen
gps.loc[gps["lat_dir"] == "S", "lat"] *= -1
gps.loc[gps["lon_dir"] == "W", "lon"] *= -1


# ---------- OPSCHONEN ----------
gps = gps.dropna(subset=["lat", "lon", "tijd (s)", "snelheid (km/h)"])


# ---------- TIJD FILTER ----------
if tijd_min is not None:
    gps = gps[gps["tijd (s)"] >= tijd_min]

if tijd_max is not None:
    gps = gps[gps["tijd (s)"] <= tijd_max]

print(f"Gebruikte GPS punten: {len(gps)}")

# ---------- SNELHEID FILTER ----------
if snelheid_min is not None:
    gps = gps[gps["snelheid (km/h)"] >= snelheid_min]

if snelheid_max is not None:
    gps = gps[gps["snelheid (km/h)"] <= snelheid_max]


# ---------- SANITY CHECK ----------
print(gps[["lat", "lon"]].head())
print(gps[["lat", "lon"]].describe())


# ---------- PLOT ----------
fig = px.line_mapbox(
    gps,
    lat="lat",
    lon="lon",
    color="snelheid (km/h)",
    hover_data={
        "tijd (s)": True,
        "snelheid (km/h)": ":.2f",
        "lat": False,
        "lon": False,
    },
    zoom=13,
    height=650,
)

fig.update_layout(
    mapbox_style="open-street-map",
    title=dict(
        text=plot_title,
        x=0.5,
        xanchor="center"
    ),
    margin=dict(l=0, r=0, t=50, b=0),
    coloraxis_colorbar=dict(
        title="Snelheid (km/h)"
    )
)

# automatisch centreren
fig.update_layout(
    mapbox_center={
        "lat": gps["lat"].mean(),
        "lon": gps["lon"].mean(),
    }
)

fig.show()


# ---------- OPTIONEEL EXPORT ----------
# fig.write_html("gps_track_snelheid.html")
# fig.write_image("gps_track_snelheid.png")  # kaleido nodig
