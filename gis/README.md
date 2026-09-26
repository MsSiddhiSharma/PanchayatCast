# Geospatial Information Systems (GIS) Guide — PanchayatCast (SIH26074)

## 1. Overview

The `gis/` subsystem manages spatial vectors, raster digital elevation models, land use classifications, and raster-to-polygon zonal extraction routines.

---

## 2. Directory Hierarchy

```text
gis/
├── README.md                      # GIS processing guide and standards (this file)
├── boundaries/                    # Raw administrative boundary vector packages
├── panchayats/                    # Gram Panchayat boundary polygons (GeoJSON / SHP)
├── blocks/                        # Block boundary polygons
├── districts/                     # District boundary polygons
├── raster/                        # DEM GeoTIFFs, slope rasters, LULC rasters
└── processed/                     # Merged spatial feature tables with zonal statistics
```

---

## 3. Geospatial Processing Standards

### 3.1 Coordinate Reference Systems (CRS)
- **Storage & Vector Interoperability:** `EPSG:4326` (WGS 84 geographic coordinates in decimal degrees).
- **Zonal Geometry & Distance Computations:** Reprojected locally to appropriate UTM Zone (e.g., `EPSG:32643` for Western India) or `EPSG:3857` (Web Mercator for frontend map rendering).
- **Raster Projection:** Ensure DEM and LULC rasters match vector CRS before rasterization or zonal aggregation.

### 3.2 Raster-to-Polygon Zonal Aggregations
For every Gram Panchayat polygon, static physiographic indicators are extracted from high-resolution rasters:
1. **Elevation ($\text{SRTM 30m}$):** Mean, standard deviation (surface roughness), minimum, maximum elevation.
2. **Topographic Gradient:** Slope gradient (degrees) and solar exposure Aspect ($\sin(\theta)$, $\cos(\theta)$).
3. **Land Cover Fractions ($\text{Bhuvan LULC}$):** % Cropland, % Forest Canopy, % Surface Water Bodies, % Built-Up.

---

## 4. Preservation of Stable Panchayat Identifiers

> [!IMPORTANT]
> **Panchayat ID Invariance Rule:**
> Every Panchayat boundary feature must be keyed using its official **Local Government Directory (LGD) Gram Panchayat Code** (or official Census 2011 Village/Panchayat Code).
> 
> Under no circumstance may arbitrary auto-incremented array indices (e.g. `0, 1, 2...`) be used as identifiers. LGD codes remain immutable across all relational database tables, ML feature matrices, and frontend API responses.

---

## 5. Spatial Formats Supported
- **Vector:** GeoJSON (RFC 7946), ESRI Shapefile (`.shp`), Geopackage (`.gpkg`).
- **Raster:** Cloud-Optimized GeoTIFF (`.tif`), NetCDF4 (`.nc`), GRIB2 (`.grib2`).
