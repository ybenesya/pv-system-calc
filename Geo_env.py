from pvlib.location import Location
import json
import googlemaps
from urllib.request import urlopen
from timezonefinder import TimezoneFinder


def get_location_info(address, address_type):
    """
    This function create Location struct from the address/coordinate that the user puts using google maps API.
    if the user puts address the function will find the coordinate, if the user puts coordinates the function will find the address
    :param address: (city+ street + home number OR coordinates) as string according of the user input
    :param address_type: 0 if we get address, 1 if coordinates as a string
    :return: location: class Location with fields latitude, longitude, timezone, altitude (default = 0), location name
    if address can't be found return None
    """
    api_key = ""
    try:
        if address_type ==1:
            lat = float(address.split(",")[0])
            long = float(address.split(",")[1])
            url = "https://maps.googleapis.com/maps/api/geocode/json?key="
            url += api_key+"&latlng=%s,%s&sensor=false" % (lat, long)
            v = urlopen(url).read()
            j = json.loads(v)
            components = j['results'][0]['address_components']
            timezone = TimezoneFinder().timezone_at(lng=long, lat=lat)
            home_number=" "
            street= " "
            for i in components:
                if i['types'][0] == 'street_number':
                    home_number = i['long_name']
                if i['types'][0] == 'route':
                    street = i['long_name']
                if i['types'][0] == 'locality':
                    city = i['long_name']
                if i['types'][0] == 'country':
                    country = i['long_name']
            if street == " " or home_number == " ":
                location_name =  str(city) + ", " + str(country)
            else:
                location_name = str(street) + " " + str(home_number) + ", " + str(city)+ ", " + str(country)
        else:
            map_client = googlemaps.Client(api_key)
            response = map_client.geocode(address)
            if response == []:
                return None
            lat = response[0]['geometry']['location']['lat']
            long = response[0]['geometry']['location']['lng']
            location_name = address
            timezone = TimezoneFinder().timezone_at(lng=long, lat=lat)
        location = Location(lat, long, timezone, 0, location_name)
    except:
        return None
    return location



