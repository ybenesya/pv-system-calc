import math
import csv
import requests
import json

def create_station_dict_from_csv():
    """
    This function create a dict of all the station of meteorological service that measured irradiance.
    In the grad_working_stations.csv there is a list of all the station and relevant data about every station
    :return: station_dict that contains relevant information about the station (like: station_name ect)
    """
    station_dict = {}
    flag= True
    with open('grad_working_stations.csv') as file:
        lines= file.readlines()
        for line in lines:
            if flag:
                flag = False
                continue
            lat = float(line.split(']')[1].split(',')[1])
            long = float(line.split(']')[1].split(',')[2])
            station_id = line.split(']')[1].split(',')[3]
            station_name = line.split(']')[1].split(',')[4][:-1]
            grad_channel = line.split(']')[0].split('[')[0].split(',')[1]
            td_channel = line.split(']')[0].split('[')[0].split(',')[0]
            station_dict[station_name] = [[lat, long], station_id , grad_channel, td_channel]
    return station_dict


def get_closest_grad_station(station_dict, coordinates):
    """
    This function return the closest meteorological service station to the location that the user puts
    :param station_dict: dict with all the information about station of meteorological service
    :param coordinates: the coordinates of the loctaion that the user inters
    :return: the name of the closest meteorological service to user location
    """
    lat_address = coordinates[0]
    long_address = coordinates[1]
    distance = 1000000
    station_name_closest = ""
    for station_name in station_dict:
        lat_station = station_dict[station_name][0][0]
        long_station = station_dict[station_name][0][1]
        distance_from_station = math.sqrt(((lat_station-lat_address)**2) +((long_station-long_address)**2))
        if distance_from_station<distance:
            distance = distance_from_station
            station_name_closest = station_name
    return station_name_closest

def get_all_stations_info_in_json_file():
    """
    This function create variable containing json file with all the station names of Meteorological Station.
    :return: data that contains all the information from Meteorological Station
    """
    url = "https://api.ims.gov.il/v1/envista/stations"

    headers = {
        'Authorization': 'ApiToken f058958a-d8bd-47cc-95d7-7ecf98610e47'
    }
    try:
        response = requests.request("GET", url, headers=headers)
        data = json.loads(response.text.encode('utf8'))
        return data
    except:
        return None


def update_grad_csv_file(station_dict):
    """
    This function gets all the station info from Meteorological Station and update the dict according to this info.
    :param station_dict: station_dict that contains relevant information about the station
    :return: station dict that update for relevant stations
    """
    json_data = get_all_stations_info_in_json_file()
    if json_data is None:
        return station_dict
    for i in range(len(json_data)):
        grad_channel_id = 0
        TD_channel_id = -1
        measurements = []
        station_name = json_data[i]['name']
        station_id = json_data[i]['stationId']
        lat = json_data[i]['location']['latitude']
        long = json_data[i]['location']['longitude']
        station_status = json_data[i]['active'] #if this is False the station is not working
        monitors_array = json_data[i]['monitors']
        for j in range(len(monitors_array)):
            measurements.append(monitors_array[j]['name'])
            if monitors_array[j]['name'] == 'Grad':
                grad_channel_id = monitors_array[j]['channelId']
                grad_status = monitors_array[j]['active']
            if monitors_array[j]['name'] == 'TD':
                TD_channel_id = monitors_array[j]['channelId']
                TD_status = monitors_array[j]['active']
                if TD_status == 'False':
                    TD_channel_id = -1
        if grad_channel_id == 0:
            continue
        elif station_status == 'True' and grad_status == 'True':
                if station_name not in station_dict:
                    station_dict[station_name] = [[lat, long], station_id , grad_channel_id, TD_channel_id]
                    fields = [station_name,station_id, lat, long,measurements, grad_channel_id, TD_channel_id]
                    with open(r'grad_working_stations.csv', 'a') as f:
                        writer = csv.writer(f)
                        writer.writerow(fields)
    return station_dict



