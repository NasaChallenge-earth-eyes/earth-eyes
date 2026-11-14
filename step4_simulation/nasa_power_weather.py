import datetime as dt
import requests
import math
import os
import json

_PCSE_IMPORT_ERROR = None
try:
    from pcse.base.weather import WeatherDataProvider
    from pcse.base import WeatherDataContainer
    from pcse.util import reference_ET
    from pcse.exceptions import PCSEError
except Exception as exc:
    WeatherDataProvider = object
    WeatherDataContainer = None
    reference_ET = None
    PCSEError = Exception
    _PCSE_IMPORT_ERROR = exc
else:
    _PCSE_IMPORT_ERROR = None

class NASAPowerWeatherDataProvider(WeatherDataProvider):
    """
    Weather data provider that fetches daily agroclimatological variables
    directly from NASA POWER API (NASA Langley Research Center).
    Supports offline caching for stability during hackathon demonstrations.
    """
    
    def __init__(self, latitude: float, longitude: float, start_date: dt.date, end_date: dt.date):
        super().__init__()
        self.latitude = latitude
        self.longitude = longitude
        self.angstA = 0.25
        self.angstB = 0.50

        if WeatherDataContainer is None or reference_ET is None:
            raise RuntimeError(f"PCSE n'est pas disponible : {_PCSE_IMPORT_ERROR}")

        self._fetch_nasa_power_data(start_date, end_date)
        
    def _fetch_nasa_power_data(self, start_date: dt.date, end_date: dt.date):
        cache_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "nasa_weather_cache.json")
        cache_key = f"{round(self.latitude, 3)},{round(self.longitude, 3)},{start_date.isoformat()},{end_date.isoformat()}"
        
        cache = {}
        if os.path.exists(cache_file):
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    cache = json.load(f)
            except Exception:
                pass
                
        if cache_key in cache:
            data = cache[cache_key]
        else:
            url = "https://power.larc.nasa.gov/api/temporal/daily/point"
            params = {
                "parameters": "T2M,T2M_MAX,T2M_MIN,PRECTOTCORR,ALLSKY_SFC_SW_DWN,RH2M,WS2M",
                "community": "AG",
                "longitude": round(self.longitude, 4),
                "latitude": round(self.latitude, 4),
                "start": start_date.strftime("%Y%m%d"),
                "end": end_date.strftime("%Y%m%d"),
                "format": "JSON"
            }
            
            try:
                r = requests.get(url, params=params, timeout=12)
                r.raise_for_status()
                data = r.json()
            except Exception as ex:
                raise PCSEError(f"Failed to fetch data from NASA POWER API: {ex}")
            
            try:
                cache[cache_key] = data
                with open(cache_file, "w", encoding="utf-8") as f:
                    json.dump(cache, f, indent=2)
            except Exception:
                pass
        
        header = data.get("geometry", {}).get("coordinates", [self.longitude, self.latitude, 500.0])
        self.elevation = header[2] if len(header) > 2 else 500.0
        
        param_data = data.get("properties", {}).get("parameter", {})
        tmax_dict = param_data.get("T2M_MAX", {})
        tmin_dict = param_data.get("T2M_MIN", {})
        tmean_dict = param_data.get("T2M", {})
        precip_dict = param_data.get("PRECTOTCORR", {})
        rad_dict = param_data.get("ALLSKY_SFC_SW_DWN", {})
        rh_dict = param_data.get("RH2M", {})
        wind_dict = param_data.get("WS2M", {})
        
        dates_sorted = sorted(tmax_dict.keys())
        for d_str in dates_sorted:
            try:
                day = dt.datetime.strptime(d_str, "%Y%m%d").date()
            except ValueError:
                continue
                
            tmax = tmax_dict.get(d_str)
            tmin = tmin_dict.get(d_str)
            tmean = tmean_dict.get(d_str)
            precip = precip_dict.get(d_str, 0.0)
            rad_mj = rad_dict.get(d_str, 15.0)
            rh = rh_dict.get(d_str, 50.0)
            wind_2m = wind_dict.get(d_str, 2.0)
            
            # Handle NASA POWER missing values (coded as -999.0)
            if any(val is None or val == -999.0 for val in [tmax, tmin, tmean, rad_mj]):
                continue
            if precip is None or precip == -999.0:
                precip = 0.0
            if wind_2m is None or wind_2m == -999.0:
                wind_2m = 2.0
            if rh is None or rh == -999.0:
                rh = 50.0
                
            # Vapor pressure from relative humidity and mean temperature
            # Saturation vapor pressure (Tetens formula in hPa)
            es = 6.112 * math.exp((17.67 * tmean) / (tmean + 243.5))
            vap = es * (rh / 100.0)
            
            # Global Radiation in J/m2/day
            irrad = rad_mj * 1e6
            
            # Rain in cm/day (PCSE standard unit)
            rain = precip / 10.0
            
            try:
                E0, ES0, ET0 = reference_ET(
                    day, self.latitude, self.elevation, tmin, tmax, irrad,
                    vap, wind_2m, self.angstA, self.angstB, self.ETmodel
                )
            except Exception:
                E0, ES0, ET0 = 0.2, 0.2, 0.2
            
            wdc = WeatherDataContainer(
                LAT=self.latitude,
                LON=self.longitude,
                ELEV=self.elevation,
                DAY=day,
                TMAX=tmax,
                TMIN=tmin,
                TEMP=tmean,
                RAIN=rain,
                WIND=wind_2m,
                VAP=vap,
                IRRAD=irrad,
                E0=E0/10.0,
                ES0=ES0/10.0,
                ET0=ET0/10.0
            )
            self._store_WeatherDataContainer(wdc, day)
