from suntime import Sun


def sum_data_per_day_from_dict_to_array(data_dict,name=None):
    """
    This function calculate the sum of the data per day
    :param data_dict: dict contain the relevant data
    :param name: name of the data (relevant only for ho)
    :return: array containing sum per day
    """
    data_array = []
    for d in data_dict:
        sum_data = 0
        if name == "ho":
            data_array.append(data_dict[d])
            continue
        for j in range(len(data_dict[d])):
            sum_data += data_dict[d][j] * (1 / 6)
        data_array.append(sum_data)
    return data_array


def calc_avg_data_per_day(data_dict,name=None, duration_array=None, location=None):
    """
    This function calculate the data array containing avg data per day and then the avg value of all the days
    :param data_dict: dict contain the relevant data
    :param name: name of the data (relevant only for ho, kt,temp)
    :param duration_array: array contains all the dates in the duration days that the user enters
    :param location: the location that the user enters , type:Loctaion
    :return: data array, avg of the data array
    """
    data_array = sum_data_per_day_from_dict_to_array(data_dict,name)
    sum_data = 0
    for i in range(len(data_array)):
        if name == "temp":
            sum_data += data_array[i] / 24
        elif name == "kt":
            sun = Sun(location.latitude, location.longitude)
            sunrise_hour = sun.get_local_sunrise_time(duration_array[i])
            sunset_hour = sun.get_local_sunset_time(duration_array[i])
            number_of_light_hour = str(sunset_hour-sunrise_hour).split(":")[0]
            sum_data+=data_array[i]/int(number_of_light_hour)
        else:
            sum_data += data_array[i]
    data_avg = sum_data/len(data_array)
    return data_array,data_avg


def calc_max_value_per_day_from_dict(data_dict):
    """
    This function find the max value of the day and the dict
    :param data_dict: dict contain the relevant data
    :return: array contaioning max value per day, max value from the dict
    """
    max_values_array=[]
    maximum_value = 0
    for d in data_dict:
        max_value = 0
        for j in range(len(data_dict[d])):
            if data_dict[d][j] > max_value:
                max_value = data_dict[d][j]
        if max_value > maximum_value:
            maximum_value = max_value
        max_values_array.append(max_value)
    return max_values_array, maximum_value