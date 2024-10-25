import cdsapi
import datetime
from calendar import monthrange

c = cdsapi.Client()
dataset = "reanalysis-era5-single-levels"

request = {
    "product_type": ["reanalysis"],
    "variable": [
        "10m_u_component_of_wind",
        "10m_v_component_of_wind",
        "2m_dewpoint_temperature",
        "2m_temperature",
        "mean_sea_level_pressure",
        "sea_surface_temperature",
        "surface_pressure",
        "total_precipitation",
        "skin_temperature",
        "surface_latent_heat_flux",
        "top_net_solar_radiation_clear_sky",
        "snow_depth",
        "soil_temperature_level_1",
        "soil_temperature_level_2",
        "soil_temperature_level_3",
        "soil_temperature_level_4",
        "soil_type",
        "volumetric_soil_water_layer_1",
        "volumetric_soil_water_layer_2",
        "volumetric_soil_water_layer_3",
        "volumetric_soil_water_layer_4",
        "leaf_area_index_high_vegetation",
        "geopotential",
        "land_sea_mask",
        "sea_ice_cover"
    ],
     "data_format": "grib",
    "download_format": "unarchived",
}

SPIN_UP_TIME = datetime.timedelta(hours=48)
START_TIME = datetime.datetime(2000, 1, 24)
START_TIME -= SPIN_UP_TIME
END_TIME = datetime.datetime(2000, 2, 1)
SCRIPT_NAME = 'typhoon-kirrily'
INTERVAL_HOURS = 1
time_request_list = [f'{str(t).zfill(2)}:00' for t in range (0, 24, INTERVAL_HOURS)]

request_arr = [] # year start, year end, month start, month end, day start, day end

def split_month(start, end):
    if end.month - start.month > 1:
        # 3-way split
        start_flag = 0 if start.day == 1 else 1
        end_flag = 0 if end.day == monthrange(end.year, end.month)[1] else 1
        if start_flag == 1:
            request_arr.append([start.year, start.year, start.month, start.month, start.day, 31])
        request_arr.append([start.year, start.year, start.month+start_flag, end.month-end_flag, 1, 31])
        if end_flag == 1:
            request_arr.append([start.year, start.year, end.month, end.month, 1, end.day])
    elif end.month - start.month == 1:
        # 2-way split
        request_arr.append([start.year, start.year, start.month, start.month, start.day, 31])
        request_arr.append([start.year, start.year, end.month, end.month, 1, end.day])
    else:
        request_arr.append([start.year, start.year, start.month, start.month, start.day, end.day])

def split_year(start, end):
    if end.year - start.year > 1:
        split_month(start, datetime.datetime(start.year, 12, 31))
        request_arr.append([start.year + 1, end.year - 1, 1, 12, 1, 31])
        split_month(datetime.datetime(end.year, 1, 1), end)
    elif end.year - start.year == 1:
        split_month(start, datetime.datetime(start.year, 12, 31))
        split_month(datetime.datetime(end.year, 1, 1), end)
    else:
        split_month(start, end)
        

split_year(START_TIME, END_TIME)        


for i, r in enumerate(request_arr):
    request['year'] = [str(x) for x in range(r[0], r[1]+1)]
    request['month'] = [str(x).zfill(2) for x in range(r[2], r[3]+1)]
    request['day'] = [str(x).zfill(2) for x in range(r[4], r[5]+1)]
    request['time'] = time_request_list

    print(request)
    target = f"{SCRIPT_NAME}-single-{str(i).zfill(3)}.grib"
    
    c.retrieve(dataset, request, target)
    
