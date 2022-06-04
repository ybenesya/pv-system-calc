import math
import plotly.graph_objects as go

#Fixed variables for converting coordinates
distance_in_degree_lat = 364000*0.3048
distance_in_degree_long = 288200 * 0.3048
distance_addition_lat = 1/distance_in_degree_lat
distance_addition_long = 1/distance_in_degree_long


class Bbox():
    """
    Class Bbox for roof and cells that contain the coordinates of the roof/cell and id
    """
    def __init__(self, cell_id, coor1, coor2, coor3, coor4):
        self.id = cell_id
        self.coor1 = coor1
        self.coor2 = coor2
        self.coor3 = coor3
        self.coor4 = coor4

    def southest_points(self):
        """
        This function calculate the two southernmost coordinates from the coordinate list
        :return: the index of the two southernmost coordinates of the coordinate list
        """
        lats = [self.coor1[0],self.coor2[0], self.coor3[0], self.coor4[0]]
        min_index = lats.index(min(lats))
        min2_index = lats.index(min(lats))
        return min_index,min2_index

    def find_coor_direction(self):
        """
        The function organize the coordinates list according to: [n,s,e,w]
        :return: return the organize list
        """
        lats = [self.coor1[0], self.coor2[0], self.coor3[0], self.coor4[0]]
        longs = [self.coor1[1],self.coor2[1], self.coor3[1], self.coor4[1]]
        south_index = lats.index(min(lats))
        north_index = lats.index(max(lats))
        west_index = longs.index(min(longs))
        east_index = longs.index(max(longs))
        index_direction = [north_index,south_index,east_index,west_index]
        return index_direction


def calc_distance_between_to_coordinates(coor1,coor2):
    """
    This function calculate the distance between the 2 coordinates in meters
    :param coor1: [lat,long]
    :param coor2: [lat,long]
    :return: the distance between the 2 coordinates in meters
    """
    radius_earth = 6371*1000
    dlat = to_rad(coor2[0]-coor1[0])
    dlong = to_rad(coor2[1] - coor1[1])
    lat1 = to_rad(coor1[0])
    lat2 = to_rad(coor2[0])
    a = math.pow(math.sin(dlat/2),2) + math.pow(math.sin(dlong/2),2)*math.cos(lat1)*math.cos(lat2)
    c = 2*math.atan2(math.sqrt(a),math.sqrt(1-a))
    d = radius_earth*c
    return d


def to_rad(x):
    """
    This function convert angle from degree to radiance
    :param x: angle in degree
    :return: angle in radiance
    """
    return x*math.pi /180


def get_numbers_of_cell_for_tilt_roof(l,w, length , width, buff= 0.1 ):
    """
    This function calculate the number of cell that fit in the length of the roof and the number
    of the cell that fit in the width of the roof
    :param l: length of the PV cell
    :param w: the width of the PV cell
    :param length: length of the roof
    :param width: the width of the roof
    :param buff: buffer from roof edges
    :return: the number of cell that fit in the length of the roof and the number of the cell that
    fit in the width of thr roof
    """
    num_len = (length-2*buff)/l
    num_width = (width - 2 * buff) / w
    return math.floor(num_len), math.floor(num_width)


def create_bbox_for_roof(azimuth, length,width,location):
    """
    This function create bounding box for the roof
    :param azimuth: the azimuth angle of the roof in radiance
    :param length: the length of the roof
    :param width: the width of the roof
    :param location: the location of the roof in format of Location
    :return: bounding box for the roof
    """
    if azimuth == math.pi or azimuth== 0 or azimuth == math.pi/2 or azimuth == 3*math.pi/2:
        azimuth = azimuth + math.radians(0.005)
    lat_addition1 = (math.cos(azimuth) * length)/distance_in_degree_lat
    long_addition1 = (math.sin(azimuth) * length)/distance_in_degree_long
    if azimuth > math.pi/2:
        lat_addition2 = (math.cos(math.pi*2-(-azimuth + math.pi/2)) * width)/distance_in_degree_lat
        long_addition2 = (math.sin(math.pi*2-(-azimuth + math.pi/2)) * width)/distance_in_degree_long
    else:
        lat_addition2 = (math.cos(azimuth-math.pi/2) * width) / distance_in_degree_lat
        long_addition2 = (math.sin(azimuth-math.pi/2) * width) / distance_in_degree_long
    point1 = [location.latitude, location.longitude]
    point2 = [location.latitude + lat_addition1, location.longitude + long_addition1]
    point3 = [location.latitude + lat_addition2, location.longitude + long_addition2]
    point4 = [location.latitude + lat_addition1 + lat_addition2, location.longitude + long_addition1 + long_addition2]
    bb_box = Bbox(0, point1,point2,point3,point4)
    return bb_box


def create_first_cell_location(roof_box, azimuth, buff):
    """
    This function calculate the first coordinate of the first PV cell to place on the roof
    :param roof_box: bounding box for the roof
    :param azimuth: the azimuth angle of the roof in radiance
    :param buff: buffer from roof edges
    :return: the first coordinate of the PV cell to place on the roof
    """
    if azimuth > math.pi/2:
        addition1_long = (buff*math.sin(math.pi*2-(-azimuth + math.pi/2)))/distance_in_degree_long
        addition1_lat = (buff * math.cos(math.pi*2-(-azimuth + math.pi/2)))/distance_in_degree_lat
    else:
        addition1_long = (buff * math.sin(azimuth-math.pi/2)) / distance_in_degree_long
        addition1_lat = (buff * math.cos(azimuth-math.pi/2)) / distance_in_degree_lat
    addition2_long = (buff * math.sin(azimuth))/distance_in_degree_long
    addition2_lat = (buff * math.cos(azimuth))/distance_in_degree_lat
    point1=[roof_box.coor1[0]+addition1_lat+addition2_lat,roof_box.coor1[1]+addition1_long+addition2_long]
    return point1


def create_bbox_of_cell_location(first_location, azimuth,l,w,counter):
    """
    This function find for each cell 3 more coordinates of the cell and create bbox for the cell
    :param first_location: the first coordinate of the PV cell
    :param azimuth: the azimuth angle of the roof in radiance
    :param l: length of the PV cell
    :param w: the width of the PV cell
    :param counter: id (number) of the cell
    :return: bbox of one cell
    """
    lat_adition1 = (math.cos(azimuth) * l) / distance_in_degree_lat
    long_adition1 = (math.sin(azimuth) * l) / distance_in_degree_long
    if azimuth > math.pi/2:
        lat_adition2 = (math.cos(math.pi*2 - (-azimuth + math.pi/2)) * w) / distance_in_degree_lat
        long_adition2 = (math.sin(math.pi*2 - (-azimuth + math.pi/2)) * w) / distance_in_degree_long
    else:
        lat_adition2 = (math.cos(azimuth-math.pi/2) * w) / distance_in_degree_lat
        long_adition2 = (math.sin(azimuth-math.pi/2) * w) / distance_in_degree_long
    point1 = first_location
    point2 = [first_location[0] + lat_adition1, first_location[1] + long_adition1]
    point3 = [first_location[0] + lat_adition2, first_location[1] + long_adition2]
    point4 = [first_location[0] + lat_adition1 + lat_adition2, first_location[1] + long_adition1 + long_adition2]
    bb_box = Bbox(counter, point1, point2, point3, point4)
    return bb_box


def get_cells_bbox_tilt(location ,l,w, length , width , azimuth, buff= 0.1):
    """
    This function calculate the number of cell that fit on tilt roof and create array of bbox cells
    :param location: the location of the roof in format of Location
    :param l: length of the PV cell
    :param w: the width of the PV cell
    :param length: the length of the roof
    :param width: the width of the roof
    :param azimuth: the azimuth angle of the roof in radiance
    :param buff: buffer from roof edges
    :return: the number of cell that fit on tilt roof and create array of bbox cells
    """
    roof_bbox = create_bbox_for_roof(azimuth,length,width,location)
    first_point = create_first_cell_location(roof_bbox,azimuth,buff)
    num_cells_len, num_cells_width = get_numbers_of_cell_for_tilt_roof(l, w, length, width, buff)
    num_cells_len = int(num_cells_len)
    num_cells_width = int(num_cells_width)
    cells = []
    counter = 0
    for i in range(num_cells_width):
        if i != 0:
            first_point = cells[num_cells_len*(i-1)].coor3
        for j in range(num_cells_len):
            counter +=1
            bbox_cell= create_bbox_of_cell_location(first_point,azimuth,l,w,counter)
            first_point = bbox_cell.coor2
            cells.append(bbox_cell)
    num_cells = counter
    return num_cells,cells


def create_new_roof_without_buffers(bbox_roof ,azimuth, buff=0.1):
    """
    This function creating the new roof bbox after decrease the roof size by buff from the edges
    :param bbox_roof: the bbox of the roof
    :param azimuth: the azimuth angle of the roof in radiance
    :param buff: buffer from roof edges
    :return: new roof bbox
    """
    coor1_new = [bbox_roof.coor1[0]+(buff*math.sin(azimuth)+buff*math.cos(azimuth))/distance_in_degree_lat,bbox_roof.coor1[1]+(-buff*math.cos(azimuth)+buff*math.sin(azimuth))/distance_in_degree_long]
    coor2_new = [bbox_roof.coor2[0]+(buff*math.sin(azimuth)-buff*math.cos(azimuth))/distance_in_degree_lat,bbox_roof.coor2[1]+(-buff*math.cos(azimuth)-buff*math.sin(azimuth))/distance_in_degree_long]
    coor3_new = [bbox_roof.coor3[0] + (-buff * math.sin(azimuth) + buff * math.cos(azimuth)) / distance_in_degree_lat,
                 bbox_roof.coor3[1] + (buff * math.cos(azimuth) + buff * math.sin(azimuth)) / distance_in_degree_long]
    coor4_new = [bbox_roof.coor4[0] + (-buff * math.cos(azimuth) - buff * math.sin(azimuth)) / distance_in_degree_lat,
                 bbox_roof.coor4[1] + (-buff * math.sin(azimuth) + buff * math.cos(azimuth)) / distance_in_degree_long]
    return Bbox(1,coor1_new,coor2_new,coor3_new,coor4_new)


def create_equation_a_b_array (bbox_roof_new):
    """
    This function creating the new roof bbox equation a b array [[a_n_e,b_n_e],[a_n_w,b_n_w],[a_s_e,b_s_e],[a_s_w,b_s_w]]
    This function module the roof coordinates to equations like: y=ax+b
    :param bbox_roof_new:  bbox of the roof after reduction of the buffer
    :return:values of a,b of the roof
    """
    coor_array = [bbox_roof_new.coor1, bbox_roof_new.coor2, bbox_roof_new.coor3, bbox_roof_new.coor4]
    index_direction = bbox_roof_new.find_coor_direction()
    north_coor = coor_array[index_direction[0]]
    south_coor = coor_array[index_direction[1]]
    west_coor = coor_array[index_direction[3]]
    east_coor = coor_array[index_direction[2]]
    # north -> west
    a_n_w = (west_coor[1]-north_coor[1])/(west_coor[0]-north_coor[0])
    b_n_w = west_coor[1] - a_n_w*west_coor[0]
    # north -> east
    a_n_e = (east_coor[1] - north_coor[1]) / (east_coor[0] - north_coor[0])
    b_n_e = east_coor[1] - a_n_e * east_coor[0]
    # south -> east
    a_s_e = (east_coor[1] - south_coor[1]) / (east_coor[0] - south_coor[0])
    b_s_e = east_coor[1] - a_s_e * east_coor[0]
    # south -> west
    a_s_w = (west_coor[1] - south_coor[1]) / (west_coor[0] - south_coor[0])
    b_s_w = west_coor[1] - a_s_w * west_coor[0]
    equation_a_b_array = [[a_n_e,b_n_e],[a_n_w,b_n_w],[a_s_e,b_s_e],[a_s_w,b_s_w]]
    return equation_a_b_array


def place_cells_bbox_for_level_roof_with_azimuth(first_coor, l, w,num_cells_w, cell_id):
    """
    This function creating new bbox cells array
    :param first_coor: first coordinate of the PV cell
    :param l: length of the PV cell
    :param w: the width of the PV cell
    :param num_cells_w:  the number of cells that fit on the width of the roof
    :param cell_id: the number of cell
    :return: new bbox cells array, last cell id
    """
    cells =[]
    for i in range(num_cells_w):
        cells.append(Bbox(cell_id,[first_coor[0],first_coor[1]],[first_coor[0],first_coor[1]+w/distance_in_degree_long],
                     [first_coor[0]+l/distance_in_degree_lat,first_coor[1]],[first_coor[0]+l/distance_in_degree_lat,first_coor[1]+w/distance_in_degree_long]))
        cell_id += 1
        first_coor =[first_coor[0],first_coor[1]+w/distance_in_degree_long]
    return cell_id,cells


def get_cells_bbox_for_level_roof_with_azimuth(roof_bbox , azimuth, l, w, d_between_cells,buff= 0.1):
    """
    This function finds all cells places on a level roof with azimuth and find the number of cells fit on the roof.
    for level roof with azimuth we place all cell to south
    :param roof_bbox:  bbox of the roof
    :param azimuth: the azimuth angle of the roof in radiance
    :param l: length of the PV cell
    :param w: the width of the PV cell
    :param d_between_cells: distance between the cells rows
    :param buff:buffer from roof edges
    :return: number of cells fit on the roof and cells bbox array
    """
    new_roof_bbox = create_new_roof_without_buffers(roof_bbox,azimuth,buff)
    coors_array = [new_roof_bbox.coor1,new_roof_bbox.coor2,new_roof_bbox.coor3,new_roof_bbox.coor4]
    index_direction= new_roof_bbox.find_coor_direction()
    south_coor = coors_array[index_direction[1]]
    north_coor = coors_array[index_direction[0]]
    east_coor = coors_array[index_direction[2]]
    west_coor = coors_array[index_direction[3]]
    equation_a_b_array = create_equation_a_b_array(new_roof_bbox)
    lat = south_coor[0]
    num_cells = 0
    counter = 2
    cells =[]
    eq1 = equation_a_b_array[2]  #start from south to east
    eq2 = equation_a_b_array[3]   #start from south to west
    while lat < north_coor[0]:
        if lat > east_coor[0]:
            eq1 = equation_a_b_array[0]  #change to east to notrh
        if lat > west_coor[0]:
            eq2 = equation_a_b_array[1]  # change to west to north
        long1 = eq1[0]*lat + eq1[1]  #east
        long2 = eq2[0] * lat + eq2[1]  #west
        distance_long = long1 - long2
        dis_w = w/distance_in_degree_long
        num_cell_w = math.floor(distance_long/dis_w)
        if num_cell_w >= 2: #at least 2 panells in a row
            lat_new = lat + ((d_between_cells+l)/distance_in_degree_lat)
            if (lat + ((d_between_cells+l)/distance_in_degree_lat)) > east_coor[0]:
                long_e_new = long1
                eq1_new = equation_a_b_array[0]
                while long_e_new > long2:
                    lat_e_check = (long_e_new-eq1_new[1])/eq1_new[0]
                    if lat_new > lat_e_check:
                        long_e_new = long_e_new -buff*distance_addition_long
                    else:
                        long1 = long_e_new
                        break
            if lat + ((d_between_cells+l)/distance_in_degree_lat) > west_coor[0]:
                long_w_new = long2
                eq2_new = equation_a_b_array[1]
                while long_w_new < long1:
                    lat_w_check = (long_w_new-eq2_new[1])/eq2_new[0]
                    if lat_new > lat_w_check:
                        long_w_new = long_w_new +buff*distance_addition_long
                    else:
                        long2 = long_w_new
                        break
            if lat + ((d_between_cells + l) / distance_in_degree_lat) > north_coor[0]:
                break
            distance = long1 - long2
            dis_w = w / distance_in_degree_long
            num_cell_w = math.floor(distance / dis_w)
            if num_cell_w < 2:
                break
            counter, cells_bbox = place_cells_bbox_for_level_roof_with_azimuth([lat,long2], l, w, num_cell_w, counter)
            for j in range(len(cells_bbox)):
                cells.append(cells_bbox[j])
            num_cells += num_cell_w
            lat = lat + ((d_between_cells+l)/distance_in_degree_lat)
        else:
            lat = lat + buff*distance_addition_lat
    return num_cells, cells


def reverse_bbox_coordinate(roof_bbox):
    """
    This function change between coor latitude and longitude for showing on a map function
    :param roof_bbox: the roof bbox
    :return: 4 coordinates of the roof in a specific order
    """
    point1 = [roof_bbox.coor1[1], roof_bbox.coor1[0]]
    point2 = [roof_bbox.coor2[1], roof_bbox.coor2[0]]
    point3 = [roof_bbox.coor3[1], roof_bbox.coor3[0]]
    point4 =  [roof_bbox.coor4[1], roof_bbox.coor4[0]]
    return point4,point3,point1,point2


def create_lon_lat_cells_array_for_print(cells):
    """
    This function create arrays for the cells latitude and longitude coordinates for showing on a map
    :param cells: the array of cells bbox
    :return: arrays for the cells latitude and longitude coordinates
    """
    lon = []
    lat = []
    for i in range(len(cells)):
        p1, p2, p3, p4 = reverse_bbox_coordinate(cells[i])
        lon.extend([p1[0], p2[0], p3[0], p4[0]])
        lat.extend([p1[1], p2[1], p3[1], p4[1]])
        if i != (len(cells) - 1):
            lon.append(None)
            lat.append(None)
    return lon,lat


def placing_on_roof(location,azimuth, length,width,l_cell, w_cell, distance_between_cells, is_tilt,opt_tilt, buff):
    """
    This function find the number of cells fits on wanted roof and generate all the cells coordinate on the roof
    :param location: the location of the roof in format of Location
    :param azimuth: the azimuth angle of the roof in radiance
    :param length: the length of the roof
    :param width: the width of the roof
    :param l_cell: length of the cell
    :param w_cell: width of the cell
    :param distance_between_cells: distance between the cells rows
    :param is_tilt: 1- if the roof is tilt 0- else
    :param opt_tilt: optimal tilt angle of the PV cells on the roof
    :param buff:buffer from the edge of the roof
    :return:the number of cells fits on wanted roof and generate all the cells coordinate on the roof and roof coordinate for showing on a map
    """
    azimuth = math.radians(azimuth)
    roof_bbox = create_bbox_for_roof(azimuth, length,width, location)
    point1, point2, point3, point4 = reverse_bbox_coordinate(roof_bbox)
    if buff >=1:
        new_buff = math.sqrt(buff)
    else:
        new_buff = buff*buff
    if is_tilt:
        num_cells , cells = get_cells_bbox_tilt(location, l_cell, w_cell, length, width, azimuth,new_buff)
    else:
        l_tilt_cell = l_cell*math.cos(math.radians(opt_tilt))
        num_cells , cells = get_cells_bbox_for_level_roof_with_azimuth(roof_bbox, azimuth,l_tilt_cell, w_cell, distance_between_cells,new_buff)
    point_array = [point1,point2,point3,point4]
    return num_cells, cells,point_array


def placing_on_map (roof_coors,lon_array,lat_array):
    """
    This function gets the coordinate of the roof, and arrays contains all the cell latitude and longitude.
    Creates a map interface with a drawing of the roof and the cells located on it.
    :param roof_coors: array contains coordinates of the roof
    :param lon: array contains cells latitude
    :param lat: array contains cells longitude
    """
    fig = go.Figure(go.Scattermapbox(
        mode = "lines", fill = "toself",
        lon = lon_array,
        lat = lat_array,
        marker={'size':10,'color':"steelblue"}))

    fig.update_layout(
        mapbox = {'layers':[{'source': {
                    'type': "FeatureCollection",
                    'features': [{
                        'type': "Feature",
                        'geometry': {
                            'type': "MultiPolygon",
                            'coordinates':[[roof_coors]] } }]},
            'type': "fill",'below':"traces",'color': "silver"}]})

    fig.update_layout(
        mapbox = {'style': "stamen-terrain", 'center': {'lon': roof_coors[0][0], 'lat': roof_coors[0][1]}, 'zoom': 18},
        showlegend = False,
        margin = {'l':0, 'r':0, 'b':0, 't':0})
    fig.show()







