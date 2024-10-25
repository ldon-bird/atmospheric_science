import cdsapi
import datetime
from calendar import monthrange

c = cdsapi.Client()
dataset = "reanalysis-era5-pressure-levels"

request = {
    "product_type": ["reanalysis"],
    "variable": [
        "geopotential",
        "relative_humidity",
        "specific_humidity",
        "temperature",
        "u_component_of_wind",
        "v_component_of_wind"
    ],
    "year": ["2022"],
    "month": ["03"],
    "day": ["13", "14", "15"],
    "time": [
        "00:00", "03:00", "06:00",
        "09:00", "12:00", "15:00",
        "18:00", "21:00"
    ],
    "pressure_level": [
        "1", "2", "3",
        "5", "7", "10",
        "20", "30", "50",
        "70", "100", "125",
        "150", "175", "200",
        "225", "250", "300",
        "350", "400", "450",
        "500", "550", "600",
        "650", "700", "750",
        "775", "800", "825",
        "850", "875", "900",
        "925", "950", "975",
        "1000"
    ],
     "data_format": "grib",
    "download_format": "unarchived",
}

SPIN_UP_TIME = datetime.timedelta(hours=48)
START_TIME = datetime.datetime(2000, 1, 24)
END_TIME = datetime.datetime(2000, 2, 1)
START_TIME -= SPIN_UP_TIME
SCRIPT_NAME = 'typhoon-neville'
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
    target = f"{SCRIPT_NAME}-level-{str(i).zfill(3)}.grib"
    
    c.retrieve(dataset, request, target)
    
