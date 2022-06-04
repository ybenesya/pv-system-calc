import math
import Irad

#comments : all the math function use radiance


def find_azimuth_angle(azimuth_choice):
    """
    This function return the angle of the azimuth in degrees due to the user choice
    :param azimuth_choice:
    :return: azimuth angle in degrees
    """
    if azimuth_choice == "North":
        return 0
    if azimuth_choice == "South":
        return 180
    if azimuth_choice == "West":
        return 270
    if azimuth_choice == "East":
        return 90
    if azimuth_choice == "North west":
        return 315
    if azimuth_choice == "North east":
        return 45
    if azimuth_choice == "South west":
        return 225
    if azimuth_choice == "South east":
        return 135


def get_declination_angle(day):
    """
    This function calculate the declination angle
    the equation is according: https://www.pveducation.org/pvcdrom/properties-of-sunlight/declination-angle
    :param day: the number of day in the year
    :return: the declination angle in radiance
    """
    angle = (360/365)*(day+10)
    delta = -23.45*math.cos(math.radians(angle))
    return delta


def get_sunrise_angle_hourly(lat, delta):
    """
    This function calculate the sunrise angle
    the equation is according: https://www.homerenergy.com/products/pro/docs/latest/how_homer_calculates_clearness_index.html
    :param lat: latitude of the location
    :param delta: declination angle
    :return: the sunrise angle
    """
    tan_pi = math.tan(math.radians(lat))
    tan_delta = math.tan(math.radians(delta))
    w_s = math.acos(-tan_pi*tan_delta)
    return w_s


def get_opt_tilt(location,irrad_dict ,start_date , duration_time):
    """
    This function calculate the optimal tilt for placing the PV array on the roof.
    The calculation is done iteratively while searching for the highest irradiation incident on the PV array
    :param location: loaction of the roof, type: Location
    :param irrad_dict: dict containing the global irradiance from meteorological station
    :param start_date: the date we start the calculation
    :param duration_time: number of days for the calculation
    :return: the optimal tilt
    """
    ho_dict ={}
    kt_dict ={}
    min_tilt = -15 + location.latitude
    tilt_lst = []
    sum_gt_max = 0
    opt_tilt = -1
    kt_dict,ho_dict = Irad.get_kt_ho_dict(irrad_dict,start_date, duration_time, location.latitude)
    for i in range(31):
         tilt_lst.append(min_tilt+i)
    for tilt in tilt_lst:
        sum_gt = 0
        gt_dict = Irad.calc_radiation_incident(kt_dict, irrad_dict,start_date,duration_time, tilt, location.latitude)
        for d in gt_dict:
            sum_gt = sum(gt_dict[d]) + sum_gt
        if sum_gt_max < sum_gt:
            sum_gt_max = sum_gt
            opt_tilt = tilt
    return opt_tilt


