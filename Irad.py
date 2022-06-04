import json
import requests
from datetime import timedelta, time, date
import math
import Angle


def get_json_irrdiance_between_dates(start_date,end_date,station_name,station_dict):
    """
    This function create variable containing json file with all the irradiance data from Meteorological Station,
    at a specific date range
    :param start_date: first day to pull information from the meteorological Station, in foramt 'yyyy/mm/dd'
    :param end_date: last day to pull information from the meteorological Station, in foramt 'yyyy/mm/dd'
    :param station_name: The station from which we pull information from
    :param station_dict: dict containing all stations information
    :return: variable containing the json file
    """
    if station_name == "BET DAGAN":
        station_name = "BET DAGAN RAD"
    station_id = station_dict[station_name][1]
    grad_id = station_dict[station_name][2]

    url = "https://api.ims.gov.il/v1/envista/stations/"+station_id+"/data/"+grad_id+"?from="+start_date+"&to="+end_date
    headers = {
        'Authorization': 'ApiToken '
    }
    try:
        response = requests.request("GET", url, headers=headers)
        data = json.loads(response.text.encode('utf8'))
        #data_formatted_str = json.dumps(response.json(), indent=2)
        return data
    except:
        return None


def find_min_date_type (datetime_temp,datetime_irad,index_irad, index_temp):
    """
    This function check which of the dates of the irrad and the temp values is smaller, and then increases the correct index.
    Due to problems in meteorological stations, sometimes we are missing some data. this function created to synchronize
    between the irrad and temp data.
    :param datetime_temp: the date of the temp value, type: datetime
    :param datetime_irad: the date of the irrad value, type: datetime
    :param index_irad: index of the irrad value in the array
    :param index_temp: index of the temp value in the array
    :return: new irrad and temp values
    """
    temp_array= datetime_temp.split('/')
    date_temp = date(int(temp_array[0]),int(temp_array[1]),int(temp_array[2]))
    irad_array = datetime_irad.split('/')
    date_irad = date(int(irad_array[0]), int(irad_array[1]), int(irad_array[2]))
    if date_irad <date_temp:
        return index_irad+1, index_temp
    return index_irad, index_temp+1


def find_min_time_type (time_temp,time_irrad,index_irad, index_temp):
    """
    This function check which of the times of the irrad and the temp values is smaller, and then increases the correct index.
    Due to problems in meteorological stations, sometimes we are missing some data. this function created to synchronize
    between the irrad and temp data.
    :param time_temp: the time of the temp value, type: datetime
    :param time_irrad: the time of the irrad value, type: datetime
    :param index_irad: index of the irrad value in the array
    :param index_temp: index of the temp value in the array
    :return: new irrad and temp values
    """
    temp_array= time_temp.split('+')[0].split(":")
    date_temp = time(int(temp_array[0]),int(temp_array[1]),int(temp_array[2]))
    irad_array = time_irrad.split('+')[0].split(":")
    date_irad = time(int(irad_array[0]), int(irad_array[1]), int(irad_array[2]))
    if date_irad <date_temp:
        return index_irad+1, index_temp
    return index_irad, index_temp+1


def create_irrad_temp_dict(irradiance_json_data, temp_json_data, s_date, duration_days):
    """
    This function read the json data variable, and create dicts containing irrad data and temp data, and an array
    containing all the irradiance and temperature data including dates and time.
    :param irradiance_json_data: variable containing the irradiance data in json format
    :param temp_json_data: variable containing the temperature data in json format
    :param s_date: start day of duration days , type: datetime
    :param duration_days: number of days.
    :return: irrad_dict, temp_dict, array_all_data
    """
    irrad_dict = {}
    temp_dict = {}
    array_all_data = []
    index_irad = 0
    index_temp = 0
    for i in range(duration_days):
        date_key = s_date + timedelta(days=i)
        date_key = str(date_key).split(" ")[0].replace('-', '/')
        irrad_dict[date_key] = []
        temp_dict[date_key] = []
    while index_irad < (duration_days*24*6) and index_temp <(duration_days*24*6):
        if index_irad >= len(irradiance_json_data['data']):
            break
        datetime_irrad = irradiance_json_data['data'][index_irad]['datetime'].split("T")[0].replace('-', '/')
        datetime_temp = temp_json_data['data'][index_temp]['datetime'].split("T")[0].replace('-', '/')
        datetime_all = temp_json_data['data'][index_temp]['datetime'].replace('T',' ').replace('-', '/')
        if datetime_temp != datetime_irrad:
            index_irad, index_temp = find_min_date_type(datetime_temp, datetime_irrad, index_irad, index_temp)
            continue
        time_irrad = irradiance_json_data['data'][index_irad]['datetime'].split("T")[1]
        time_temp = temp_json_data['data'][index_temp]['datetime'].split("T")[1]
        if time_irrad != time_temp:
            index_irad, index_temp = find_min_time_type(time_temp, time_irrad, index_irad, index_temp)
            continue
        irrad_value = irradiance_json_data['data'][index_irad]['channels'][0]['value']
        valid_irad = irradiance_json_data['data'][index_irad]['channels'][0]['valid']
        temp_value = temp_json_data['data'][index_temp]['channels'][0]['value']
        valid_temp = temp_json_data['data'][index_temp]['channels'][0]['valid']
        if valid_irad and valid_temp:
            array_all_data.append([datetime_all, [irrad_value,temp_value]])
            irrad_dict[datetime_irrad].append(irrad_value)
            temp_dict[datetime_temp].append(temp_value)
        index_irad += 1
        index_temp += 1
    return irrad_dict, temp_dict, array_all_data


def create_irrad_dict_yearly(irradiance_json_data, s_date, duration_days):
    """
    This function create a dict containing all the irrad data for a year
    :param irradiance_json_data: variable containing the irradiance data in json format
    :param s_date: start day of duration days , type: datetime
    :param duration_days: number of days.
    :return: dict containing all irrad data for a year
    """
    irrad_dict = {}
    for i in range(duration_days):
        date_key = s_date + timedelta(days=i)
        date_key = str(date_key).split(" ")[0].replace('-', '/')
        irrad_dict[date_key] = []
    for item in irradiance_json_data['data']:
        datetime = item['datetime'].split("T")[0].replace('-','/')
        irrad_value = item['channels'][0]['value']
        valid = item['channels'][0]['valid']
        if valid :
            irrad_dict[datetime].append(irrad_value)
    return irrad_dict, {}, []


def get_irradiance(start_date,end_date,station_name,station_dict,temp_json_data,year_flag):
    """
    This function read irrad data from meteorological station, and send the data to create a dicts containing all this data
    :param start_date: start day of the days range , type: datetime
    :param end_date: end day of the days range , type: datetime
    :param station_name: the name of the closest meteorological station
    :param station_dict: dict containing all stations information
    :param temp_json_data: variable containing all temp data from the meteorological Station, in format: json
    :param year_flag: if 1, we want to create a dict for all year, else for a range of dates
    :return: dicts containing irrad and temp data , array containing all the data
    """
    end_date_str = str(end_date).split(" ")[0].replace('-', '/')
    start_date_str = str(start_date).split(" ")[0].replace('-', '/')
    irradiance_json_data =get_json_irrdiance_between_dates(start_date_str,end_date_str,station_name,station_dict)
    if irradiance_json_data is None:
        return -2
    duration_days = (end_date - start_date).days
    if year_flag:
        irrad_dict,temp_dict, array_all_data = create_irrad_dict_yearly(irradiance_json_data, start_date ,duration_days)
    else:
        irrad_dict, temp_dict, array_all_data = create_irrad_temp_dict(irradiance_json_data,temp_json_data, start_date ,duration_days)
    return irrad_dict, temp_dict , array_all_data


def create_irrad_dict_for_year(station_dict, station_name, end_date):
    """
    This function Define days range of a year and send to get irrad values for a year
    :param station_dict: dict containing all stations information
    :param station_name: The station from which we pull information from
    :param end_date: last day to pull information from the meteorological Station, type: datetime
    :return: irrad_dict and start_date for a year
    """
    start_date = end_date - timedelta(days=365)
    year_flag = True
    irrad_dict,temp_dict , array_all_data = get_irradiance(start_date, end_date, station_name, station_dict,None,year_flag)
    return irrad_dict,start_date


def calc_ho(day, lat , delta):
    """
    This function calculate the extraterrestrial global irradiance for a specific day.
    The equation is from : https://www.homerenergy.com/products/pro/docs/latest/how_homer_calculates_clearness_index.html
    :param day: day of the year, type: number
    :param lat: latitude of the roof location
    :param delta: declination angle
    :return: extraterrestrial global irradiance value for a day
    """
    g_sc = 1367  # the solar constant 1.367kW/m^2
    g_on = g_sc*(1+0.033*math.cos((2*math.pi*day)/365))
    w_s = Angle.get_sunrise_angle_hourly(lat, delta)
    phi = math.radians(float(lat))
    cos_phi = math.cos(phi)
    cos_delta = math.cos(math.radians(delta))
    sin_ws = math.sin(w_s)
    x = (math.pi * w_s / 180)
    sin_phi = math.sin(math.radians(lat))
    sin_delta = math.sin(math.radians(delta))
    h_o = (24/math.pi)*g_on*(cos_phi*cos_delta*sin_ws + x*sin_phi*sin_delta)
    return h_o


def calc_clearness(irrad, ho):
    """
    This function calculate the clearness index.
    The equation is from : https://www.homerenergy.com/products/pro/docs/latest/how_homer_calculates_clearness_index.html
    :param irrad: global irradiance value
    :param ho: extraterrestrial global irradiance value
    :return: clearness index value per 10 minutes
    """
    return irrad/(ho*math.pi/24)


def get_kt_ho_dict(irrad_dict,start_date, duration_time, lat):
    """
    This function calculate the dicts for clearness index and extraterrestrial global irradiance
    :param irrad_dict: dict containing the global irradiance from meteorological station
    :param start_date: start day of the days range , type: datetime
    :param duration_time: number of days.
    :param lat: latitude of the roof location
    :return: clearness index dict and extraterrestrial global irradiance dict
    """
    ho_dict = {}
    kt_dict = {}
    for i in range(duration_time):
        date_key = start_date + timedelta(days=i)
        date_key = str(date_key).split(" ")[0].replace('-', '/')
        ho_dict[date_key] = ""
        kt_dict[date_key] = []
    i = 0
    for d in irrad_dict:
        day = start_date.timetuple().tm_yday + i
        delta = Angle.get_declination_angle(day)
        ho_dict[d] = calc_ho(day, lat, delta)
        for value in irrad_dict[d]:
            kt_dict[d].append(calc_clearness(value,ho_dict[d]))
        i += 1
    return kt_dict, ho_dict


def calc_gd_gb(kt_dict,irrad_dict,duration_time , start_date):
    """
    This function calculate the direct and diffuse irradiance.
    The equation is from: https://www.homerenergy.com/products/pro/docs/latest/how_homer_calculates_the_radiation_incident_on_the_pv_array.html
    :param kt_dict: dict containing clearness index values
    :param irrad_dict: dict containing global irradiance values
    :param duration_time: number of days
    :param start_date: start day of the days range , type: datetime
    :return: dicts containing direct and diffuse irradiance values for 10 minutes.
    """
    gd_dict = {}
    gb_dict = {}
    for i in range(duration_time):
        date_key = start_date + timedelta(days=i)
        date_key = str(date_key).split(" ")[0].replace('-', '/')
        gd_dict[date_key] = []
        gb_dict[date_key] = []
    for d in kt_dict:
        for j in range(len(kt_dict[d])):
            if kt_dict[d][j] <= 0.22:
                gd_dict[d].append(irrad_dict[d][j] * (1 - 0.09 * kt_dict[d][j]))
            elif kt_dict[d][j] <= 0.8:
                gd_dict[d].append(irrad_dict[d][j] * (
                            0.9511 - 0.1604 * kt_dict[d][j] + 4.388 * math.pow(kt_dict[d][j], 2) - 16.638 * math.pow(
                        kt_dict[d][j], 3) + 12.336 * math.pow(kt_dict[d][j], 4)))
            else:
                gd_dict[d].append(irrad_dict[d][j] * 0.165)
            gb_dict[d].append(irrad_dict[d][j] - gd_dict[d][j])
    return gd_dict,gb_dict


def calc_radiation_incident(kt_dict, irrad_dict,start_day,duration_time, opt_tilt, lat):
    """
    This function calculate the irradiance incident on the PV cell
    The equation is from : https://www.pveducation.org/pvcdrom/properties-of-sunlight/solar-radiation-on-a-tilted-surface
    :param kt_dict: dict containing clearness index values per 10 minutes
    :param irrad_dict: dict containing global irradiance values
    :param start_day: start day of the days range , type: datetime
    :param duration_time: number of days
    :param opt_tilt: the optimal tilt to place the pv cell
    :param lat: latitude of the roof location
    :return: dict containing irradiance incident on the PV cell
    """
    gt_dict = {}
    for i in range(duration_time):
        date_key = start_day + timedelta(days=i)
        date_key = str(date_key).split(" ")[0].replace('-', '/')
        gt_dict[date_key] = []
    i = 0
    for d in irrad_dict:
        day = start_day.timetuple().tm_yday + i
        i += 1
        for j in range(len(irrad_dict[d])):
            delta = Angle.get_declination_angle(day)
            alpha = 90 - lat + delta
            val = irrad_dict[d][j] * math.sin(math.radians(alpha + opt_tilt))/math.sin(math.radians(alpha))
            gt_dict[d].append(val)
    return gt_dict