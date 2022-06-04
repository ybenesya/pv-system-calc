from datetime import timedelta


class PanelData:
    """
     class PanelData represent a specific type of pv cell.
    """
    def __init__(self,brand,model, pmax_stc,pmax_noct, temp_noct,alpha_p,efficiency,panel_length, panel_width):
        """
        :param brand: company name
        :param model: model name of the PV
        :param pmax_stc: the cell's Pmax under STC from cell's datasheet, as int
        :param pmax_noct: max power at nominal operation cell temp
        :param temp_noct: nominal operating cell temperature, in Celsius, as int, from cell's datasheet
        :param alpha_p: temp coefficients of pmax
        :param efficiency: the cell's temperature coefficient in %/celsius_degree, from cell's datasheet, as int
        :param panel_length:  panel length (north to south part) in m from datasheet, as int
        :param panel_width: panel width (east to west part) in m from datasheet, as int
        """
        self.brand = brand
        self.model = model
        self.pmax_stc = pmax_stc
        self.pmax_noct = pmax_noct
        self.temp_noct = temp_noct
        self.alpha_p = alpha_p
        self.efficiency = efficiency
        self.panel_lenght = panel_length
        self.panel_width = panel_width

    def __repr__(self):
        print_value = "Pannel info:"
        print_value += "Brand: " + self.brand +"\n"
        print_value += "Model: " + self.model + "\n"
        print_value += "Peak Power STC: "+str(self.pmax_stc)+" [W]\n"
        print_value += "Peak Power NOCT: " + str(self.pmax_noct) + " [W]\n"
        print_value += "NOCT: " + str(self.temp_noct) + " [\u00B0C]\n"
        print_value +="Temprature coefficient of power:"+ str(self.alpha_p) + "[%/\u00B0C]\n"
        print_value += "Efficiency: " + str(self.efficiency) + " [%]\n"
        print_value +="Panel size: "+ str(self.panel_lenght)+"[m] ,"+str(self.panel_width) +"[m]\n"
        return print_value


def get_panels_data():
    """
     This function read csv file contains all the panels information and return list of panels (type: PanelData)
    :return: list of panels (type: PanelData)
    """
    is_first_line = True
    panels =[]
    with open('cells_info.csv', 'r') as file:
        lines = file.readlines()
        for line in lines:
            if is_first_line:
                is_first_line = False
                continue
            new_line = line.strip()
            split_line = new_line.split(",")
            panel = PanelData(split_line[0], split_line[1], int(split_line[2]), float(split_line[3]), int(split_line[4]),
                              (float(split_line[5]) / 100),(float(split_line[6]) / 100),(float(split_line[7]) / 1000)
                               ,(float(split_line[8]) / 1000))
            panels.append(panel)
    return panels


def calc_pv_power_dict(gt_dict, alpha_p, temp_dict, temp_noct, efficiency,duration_time,start_day):
    """
    This function calculate the power for m ^2 of the PV array of every 10 minutes
    :param gt_dict: incident irradiance on the PV array
    :param alpha_p: temp coefficients of pmax
    :param temp_dict: dict contains ambient temp from meteorological service
    :param temp_noct:  the nominal operating cell temperature of a panel
    :param efficiency: the cell's temperature coefficient in %/celsius_degree, from cell's datasheet, as int
    :param duration_time: number of days
    :param start_day: start day of the days range, type: datetime
    :return:power_dict
    calculate according : https://www.homerenergy.com/products/pro/docs/latest/how_homer_calculates_the_pv_array_power_output.html
    """
    power_dict = {}
    for i in range(duration_time):
        date_key = start_day + timedelta(days=i)
        date_key = str(date_key).split(" ")[0].replace('-', '/')
        power_dict[date_key] = []

    for d in gt_dict:
        for j in range(len(gt_dict[d])):
            val = efficiency * gt_dict[d][j] * (1 + alpha_p * (temp_dict[d][j] - temp_noct))
            power_dict[d].append(val)
    return power_dict


def calc_power_for_pv_array(power_array,num_cells,panel):
    """
    This function calculate the power for all the pannels for graphs
    :param power_array: array contains power information for each day for m^2
    :param num_cells: number of cells on the roof
    :param panel:contain information about the chosen panel, type: Panel
    :return: power_pv_array in KW
    """
    power_pv_array = []
    for item in power_array:
        power_pv_array.append(item*num_cells*panel.panel_lenght*panel.panel_width/1000)
    return power_pv_array


def calc_total_power_pv_array(pv_power_array,num_cells,panel):
    """
    This function calculates the total power of pv array
    :param pv_power_array: array contains power information for each day for m^2
    :param num_cells: number of cells on the roof
    :param panel: contain information about the chosen panel, type: Panel
    :return: total power of pv array
    """
    total_power = sum(pv_power_array) * num_cells * panel.panel_lenght * panel.panel_width
    return total_power
