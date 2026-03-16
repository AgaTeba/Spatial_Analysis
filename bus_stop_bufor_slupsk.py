import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib_scalebar.scalebar import ScaleBar
from matplotlib.patches import Patch
from matplotlib.lines import Line2D

# ==========================================
# KONFIGURACJA I ŚCIEŻKI
# ==========================================

FILE_BOUNDARIES = "granice_slupsk.geojson"
FILE_STOPS = "bus_stop_slupsk.geojson"
FILE_ROADS = "drogi_slupsk.geojson"
FILE_BUILDINGS = "budynki_slupsk.geojson"

CRS_CODE = 2180             # Układ współrzędnych (PUWG 1992)
BUFFER_METERS = 500         # Promień bufora w metrach
OUTPUT_FILE = "slupsk_bus_reach.png"

AUTHOR = "Agnieszka Trzciałkowska"
YEAR = 2026
DATA_SOURCE = "źródło danych: OpenStreetMap"
PROJECT_TITLE = "Analiza dostępności komunikacji zbiorowej w Słupsku\n– czy 500 metrów wystarczy?"

# ==========================================
# WCZYTYWANIE I PRZETWARZANIE
# ==========================================

# Wczytywanie
granice = gpd.read_file(FILE_BOUNDARIES).to_crs(epsg=CRS_CODE)
przystanki = gpd.read_file(FILE_STOPS).to_crs(epsg=CRS_CODE)
drogi = gpd.read_file(FILE_ROADS).to_crs(epsg=CRS_CODE)
budynki = gpd.read_file(FILE_BUILDINGS).to_crs(epsg=CRS_CODE)

# Przycinanie
przystanki = gpd.clip(przystanki, granice)
drogi = gpd.clip(drogi, granice)
budynki = gpd.clip(budynki, granice)

# Obliczenia (Logika)
strefy = przystanki.buffer(BUFFER_METERS)
strefa_zbiorcza = strefy.geometry.union_all()
granica_miasta = granice.geometry.union_all()
strefa_dostepnosci_only_slupsk = strefa_zbiorcza.intersection(granica_miasta)

pow_miasta = granica_miasta.area
pow_dostepna = strefa_dostepnosci_only_slupsk.area
procent_dostepnosci = (pow_dostepna / pow_miasta) * 100

budynki_w_zasiegu = budynki[budynki.geometry.intersects(strefa_zbiorcza)]
procent_budynkow = (len(budynki_w_zasiegu) / len(budynki)) * 100

# ==========================================
# WIZUALIZACJA
# ==========================================
fig, ax = plt.subplots(figsize=(12, 10))

drogi.plot(ax=ax, color='grey', linewidth=0.5, zorder=1)
budynki.plot(ax=ax, color='red', linewidth=0, zorder=2)
strefy.plot(ax=ax, color='blue', alpha=0.07, zorder=3)
granice.plot(ax=ax, color='none', edgecolor='black', linewidth=1, zorder=4)
przystanki.plot(ax=ax, color='black', markersize=5, zorder=5)

ax.axis('off') # Usunięcie ramki z cyframi, aby mapa była czysta

# Dodanie podziałki liniowej
# Ponieważ używamy układu EPSG:2180, jednostką jest metr (dx=1)

scalebar = ScaleBar(
    dx=1,
    units="m",
    location="lower right",
    color="black",           # Kolor kreski
    box_color="white",       # Kolor tła
    box_alpha=0.5,           # Lekka przezroczystość tła
    font_properties={"size": 12}, # Czcionka
    sep=5,                   # Odstęp między kreską a liczbą
    pad=0.5                  # Marginesy wewnątrz ramki
)
ax.add_artist(scalebar)

# Dodanie wyników obliczeń  na mapie:
ax.text(
    -0.02, 0.08,
    f"Dostępność komunikacji zbiorowej w całkowitej powierzchni miasta: {procent_dostepnosci:.1f}%",
    transform=ax.transAxes,
    fontsize=10,
    bbox=dict(facecolor='white', alpha=0.1)
)

ax.text(
    -0.02, 0.03,
    f"Procent budynków w zasięgu 500m: {procent_budynkow:.1f}%",
    transform=ax.transAxes,
    fontsize=10,
    bbox=dict(facecolor='white', alpha=0.1)
)

# Legenda
legend_elements = [
    Line2D([0], [0], marker='o', color='none', markerfacecolor='blue',
           markeredgecolor='none', markersize=26, alpha=0.07,
           linestyle='none', label='Zasięg 500 m od przystanku'),
    Patch(facecolor='red', edgecolor='none', label='Budynki'),
    Line2D([0], [0], color='grey', lw=0.8, label='Drogi'),
    Line2D([0], [0], marker='o', color='black', markersize=3, linestyle='', label='Przystanki'),
]
legenda = ax.legend(
    handles=legend_elements,
    loc='upper left',              # Punkt zakotwiczenia legendy
    bbox_to_anchor=(0.83, 0.98),      # (1.02, 1) przesuwa ją na zewnątrz w prawo
    borderaxespad=0,               # Brak dodatkowego marginesu od osi
    borderpad=1.0,           # Zwiększa margines wewnątrz całej ramki legendy
    labelspacing=1.5,        # Zwiększa odstępy między wierszami
    fontsize=10
)

# Zmiana ramki legendy
legenda.get_frame().set_linewidth(0.25)  # Grubość linii ramki
legenda.get_frame().set_edgecolor('gray') # Kolor ramki

# Źródło i autor
ax.text(
     -0.02, -0.03,
    f"Opracowanie: {AUTHOR}, {YEAR}, {DATA_SOURCE}",
     transform=ax.transAxes,
     fontsize=9
)

# Tytuł projektu
ax.set_title(
    f"{PROJECT_TITLE}",
     fontsize=15
)

# Zapis
plt.savefig(OUTPUT_FILE, dpi=300, bbox_inches='tight')
plt.show()