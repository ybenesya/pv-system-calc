import requests
import json
from datetime import timedelta


def get_json_temp_between_dates(start_date,end_date,station_name,station_dict):
    """
    This function create variable containing json file with all the temperature data from Meteorological Station,
    at a specific date range
    :param start_date: first day to pull information from the meteorological Station, in format 'yyyy/mm/dd'
    :param end_date: last day to pull information from the meteorological Station, in format 'yyyy/mm/dd'
    :param station_name: The station from which we pull information from
    :param station_dict: dict containing all stations information
    :return: variable containing the json file
    """
    if station_name == "BET DAGAN RAD":
        station_name = "BET DAGAN"
    station_id = station_dict[station_name][1]
    temp_id = station_dict[station_name][3]

    url = "https://api.ims.gov.il/v1/envista/stations/"+station_id+"/data/"+temp_id+"?from="+start_date+"&to="+end_date
    headers = {
        'Authorization': 'ApiToken f058958a-d8bd-47cc-95d7-7ecf98610e47'
    }
    try:
        response = requests.request("GET", url, headers=headers)
        data = json.loads(response.text.encode('utf8'))
        return data
    except:
        return None


def get_json_temp(start_date,end_date,station_name,station_dict):
    """
    This function read the temp data from meteorological station, and send this data to create a dict containing all the data
    :param start_date: start day of the days range , type: datetime
    :param end_date: end day of the days range , type: datetime
    :param station_name: the name of the closest meteorological station
    :param station_dict: dict containing all stations information
    :return: variable containing station temp data
    """
    #e_date = end_date + timedelta(days=1)
    end_date_str = str(end_date).split(" ")[0].replace('-', '/')
    start_date_str = str(start_date).split(" ")[0].replace('-', '/')
    temp_json_data =get_json_temp_between_dates(start_date_str,end_date_str,station_name,station_dict)
    if temp_json_data is None:
        return -2
    return temp_json_data


def get_temp_cell(ambient_temp_dict , gt_dict,conversion_efficiency, temp_c_noct, duration_time,start_day):
    """
    This function calculate the temperature of the cell.
    The equation is from : https://www.homerenergy.com/products/pro/docs/latest/how_homer_calculates_the_pv_cell_temperature.html
    :param ambient_temp_dict: dict contain the ambient temp value, from the meteorological station.
    :param gt_dict: dict contain the irradiance incident on the PV array
    :param conversion_efficiency: The pannel efficiency
    :param temp_c_noct: the nominal operating cell temperature
    :param duration_time: number of days to calc on
    :param start_day: the first day to start the calculation
    :return: dict containing the pv cell temp
    """
    pv_temp_dict ={}
    for i in range(duration_time):
        date_key = start_day + timedelta(days=i)
        date_key = str(date_key).split(" ")[0].replace('-', '/')
        pv_temp_dict[date_key] = []

    for d in ambient_temp_dict:
        for j in range(len(ambient_temp_dict[d])):
            val = ambient_temp_dict[d][j] + gt_dict[d][j]*((temp_c_noct-20)/800)*(1-(conversion_efficiency/0.81))
            pv_temp_dict[d].append(val)

    return pv_temp_dict