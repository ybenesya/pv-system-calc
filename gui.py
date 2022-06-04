import matplotlib.pyplot as plt
from tkinter import messagebox,ttk
from datetime import datetime, timedelta
from tkinter import *
from pandas import DataFrame
import math
import matplotlib.backends.backend_tkagg as tkagg
from tkcalendar import Calendar
from PIL import ImageTk, Image
from tkinter.ttk import Combobox
import Station_Info
from Geo_env import get_location_info
import Irad
import Angle
import Roof_placing
import Power
import Temperature
import Arithmetics


class DataTab:
    """
        create a frame with a scrollbar
    """
    def __init__(self, master):
        """
        :param master: main tab to put the scrollbar
        """
        main_frame = Frame(master)
        main_frame.pack(fill=BOTH, expand=1)
        my_canvas = Canvas(main_frame)
        my_canvas.config(bg='white')
        my_canvas.pack(side=LEFT, fill=BOTH, expand=1)
        self.canvas = my_canvas
        my_scrollbar = ttk.Scrollbar(main_frame, orient=VERTICAL, command=self.canvas.yview)
        my_scrollbar.pack(side=RIGHT, fill=Y)
        self.canvas.configure(yscrollcommand=my_scrollbar.set, height=1000)
        self.canvas.bind('<Configure>',lambda e: my_canvas.configure(scrollregion=self.canvas.bbox("all")))
        sub_frame = Frame(self.canvas, bg='white')
        self.frame = sub_frame
        self.canvas.create_window((300,0), window=self.frame, anchor="nw", width = 3000)


class FrameBuilder:
    """
        create a frame with specific label
    """
    def __init__(self, master, x, y, text, width=1000, height=1000):
        """
        create data frame
        :param master: main tab
        :param x: coor x in main tab to put the frame
        :param y: coor y in main tab to put the frame
        :param text: the text of the label of the frame
        :param width: the width size of the new frame
        :param height: the height size of the new frame
        """
        frame = Frame(master,width=width, height=height, bg="white")
        frame.pack()
        frame.place(anchor='w', relx=x, rely=y)
        label = Label(frame, text=text, font=("Gishal",12,"bold"),bg='white')
        label.pack(anchor = 'w')
        self.frame = frame
        self.label = label


class ToolTip(object):
    """
        function for create the info tips
    """
    def __init__(self, widget):
        self.widget = widget
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0

    def showtip(self, text):
        self.text = text
        if self.tipwindow or not self.text:
            return
        x, y, cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 57
        y = y + cy + self.widget.winfo_rooty() +27
        self.tipwindow = tw = Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry("+%d+%d" % (x, y))
        label = Label(tw, text=self.text, justify=LEFT,background="#ffffe0", relief=SOLID, borderwidth=1,
                      font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()

def reset():
    """
        This functions reset all the open tabs
    :return:
    """

    global frame
    global reset_win
    reset_win = True
    index = 0
    for f in tabs_lst:
        if index == 0:
            index = 1
            continue
        tabs.forget(1)
    tabs.select(0)


def CreateToolTip(widget, text):
    toolTip = ToolTip(widget)
    def enter(event):
        toolTip.showtip(text)
    def leave(event):
        toolTip.hidetip()
    widget.bind('<Enter>', enter)
    widget.bind('<Leave>', leave)


class Info_img:
    """
        place the info picture and add a comment with ToolTip
    """
    def __init__(self, master, x, y, text,info ,width=0.1, height=100):
        info_frame = Frame(master, width=width, height=height)
        info_frame.pack()
        info_frame.place(anchor='center', relx=x, rely=y)
        info_label = Label(info_frame, image=info)
        info_label.pack()
        CreateToolTip(info_label, text=text)
        self.frame = info_frame
        self.label = info_label


def config_loc_txt(clicked_loc_tmp, entry_loc):
    """
    :param clicked_loc_tmp: val = 0 if location is address,  val = 1 if location is coordinate
    :param entry_loc: type Entrey to show default value
    """
    global clicked_loc
    if clicked_loc_tmp == 0:
        loc_examp = "Haim Levanon 19, Tel Aviv"
    else:
        loc_examp = "32.1133, 34.8044"
    entry_loc.delete(0, END)
    entry_loc.insert(0, loc_examp)
    clicked_loc = clicked_loc_tmp


def disable_num_panel_entry(num_choose):
    """
    This function disable entries
    :param num_choose: number of the Radiobutton
    """
    roof_info_entery_array= [coor_of_the_roof_entry, length_roof_entry, width_roof_entry, distance_between_cells_entry,distance_from_roof_edge_entry]
    if num_choose == 1:
        num_panel_entry.config(state = "normal")
        num_panel_entry.update()
    if num_choose ==2:
        for i in range(len(roof_info_entery_array)):
            roof_info_entery_array[i].config(state = "normal")
            roof_info_entery_array[i].update()
            if i == len(roof_info_entery_array) - 1 or i == len(roof_info_entery_array) -2:
                roof_info_entery_array[i].delete(0,END)
                roof_info_entery_array[i].insert(0,"0.5")
    if num_choose == 3:
        roof_tilt_entry.config(state="normal")
        roof_tilt_entry.update()


def update_array_all_data(array_all_data, data_dict):
    """
    This function update data array from the dict, for printing information in tabs 4,5,6
    :param array_all_data:  array contain all data (like gt, gd, ect) every 10 minutes
    :param data_dict: this dict values inserted to array_all_data
    :return: array_all_data
    """
    data_array = []
    for d in data_dict:
        data_array.extend(data_dict[d])
    for i in range(len(data_array)):
        array_all_data[i][1].append(data_array[i])
    return array_all_data


def creating_dicts_data(start_date, end_date, location,station_name,opt_tilt,station_dict,panel):
    """
    This function create all the information dicts and updates all the arrays data
    :param start_date: the start date that the user enter, type: Datatime
    :param end_date: the end date that the user enter ,type: Datatime
    :param location: the location that the user enter, type: Location
    :param station_name: the name of the closest meteorological service station, type: string
    :param opt_tilt: the optimal tilt to placr the pv array of the roof
    :param station_dict: dict with all the meteorological service stations information
    :param panel: the panel that the use chose,type: panel
    :return: all calculated dicts, duration dates array, array containing all the data
    """
    end_date = end_date + timedelta(days=1)
    duration_days = (end_date - start_date).days
    duration_array = []
    array_all_data = []
    for i in range(duration_days):
        duration_array.append(start_date + timedelta(days=1) * i)
    temp_json_data = Temperature.get_json_temp(start_date, end_date, station_name, station_dict)
    irrad_dict, temp_dict, array_all_data = Irad.get_irradiance(start_date, end_date, station_name, station_dict, temp_json_data, False)
    kt_dict, ho_dict = Irad.get_kt_ho_dict(irrad_dict, start_date, duration_days, location.latitude)
    array_all_data = update_array_all_data (array_all_data, kt_dict)
    gd_dict, gb_dict = Irad.calc_gd_gb(kt_dict, irrad_dict, duration_days, start_date)
    array_all_data = update_array_all_data(array_all_data, gd_dict)
    array_all_data = update_array_all_data(array_all_data, gb_dict)
    gt_dict = Irad.calc_radiation_incident(kt_dict, irrad_dict, start_date, duration_days, opt_tilt, location.latitude)
    array_all_data = update_array_all_data(array_all_data, gt_dict)
    pv_temp_dict = Temperature.get_temp_cell(temp_dict, gt_dict, panel.efficiency, panel.temp_noct, duration_days, start_date)
    array_all_data = update_array_all_data(array_all_data, pv_temp_dict)
    pv_power_dict = Power.calc_pv_power_dict(gt_dict, panel.alpha_p, pv_temp_dict, panel.temp_noct,panel.efficiency, duration_days, start_date)
    array_all_data = update_array_all_data(array_all_data, pv_power_dict)
    return irrad_dict, temp_dict,kt_dict, ho_dict, gd_dict, gb_dict, gt_dict,pv_temp_dict,pv_power_dict,duration_array,array_all_data



def placing_on_roof_button(cells, roof_coors):
    """
    This function place the cells on the maps
    :param cells: array contain coordinate for each cell
    :param roof_coors: roof coordinate that the map focus on
    """
    lon_array, lat_array = Roof_placing.create_lon_lat_cells_array_for_print(cells)
    Roof_placing.placing_on_map(roof_coors, lon_array, lat_array)


def fill_result_tab(opt_tilt,num_cells, cells, roof_coors,station_name,location):
    """
    This function prints the result tab
    :param opt_tilt: the optimal tilt angel of the PV cells
    :param num_cells: the number of cells on face on the roof
    :param cells: array of all the coordinates cells
    :param roof_coors: roof coordinate that the map focus on
    :param station_name: the name of the closest meteorological service station, type: string
    :param location: the location that the user enter, type: Location
    """
    global map_btn
    dates_text = str(start_calender.get_date()).replace("-", "/") + " - " + str(
        end_calender.get_date()).replace("-", "/")
    lable_list_info = [["Address: ",0.05,0.16],["Chosen dates: ",0.05,0.19],["Azimuth of the roof: ",0.05,0.22],
                       ["The closest meteorological station : ", 0.05,0.25],["Calculated optimal tilt: ",0.05,0.33],
                       ["Number of PV cells that placed on the roof: ", 0.05,0.36]]
    name_lable_list = []
    global result_list
    index_lists = 0
    result_info =[[location.name,0.12, 0.16],[dates_text,0.15,0.19],[azimuth_cb.get(),0.19,0.22], [station_name,0.29,0.25],
                  [str(format(opt_tilt, ".2f")),0.2,0.33],[str(num_cells),0.335,0.36]]
    result_title = "Calculator Results"
    result_title_frame = FrameBuilder(tab2_results, 0.35, 0.05, result_title)
    result_title_frame.label.config(fg='dark blue', font=("Cooper Black", 30, "bold"))


    if 'reset_win' in globals():
        for r in result_list:
            r.destroy()

    result_list = []
    Inputs_label = Label(tab2_results, text="Inputs: ", font=("Gishal", 12, "underline", "bold"), bg='white')
    Inputs_label.place(anchor='w', relx=0.05, rely=0.13)

    for inf,res in zip(lable_list_info,result_info):
        name_lable_list.append( Label(tab2_results, text=inf[0],font=("Gishal", 12, "bold"),bg='white'))
        name_lable_list[index_lists].place(anchor='w', relx=inf[1], rely=inf[2])
        result_list.append(Label(tab2_results, text=res[0],font=("Gishal", 12),bg='white'))
        result_list[index_lists].place(anchor='w', relx=res[1], rely=res[2])
        index_lists +=1

    summery_outputs_label = Label(tab2_results, text="Summary outputs: ", font=("Gishal", 12, "underline", "bold"), bg='white')
    summery_outputs_label.place(anchor='w', relx=0.05, rely=0.30)

    #Show Pv in web
    if clicked_roof_information.get() == 1:
        map_btn = Button(tab2_results, text="Map", height=1, width=6,font=("Gishal", 10, "bold"), command=lambda:placing_on_roof_button(cells, roof_coors) )
        map_btn.place(anchor='w', relx=0.38, rely=0.36)
    else:
        if 'map_btn' in globals():
            map_btn.destroy()


def fill_result_tab_irad_temp_power(irrad_dict, temp_dict, kt_dict, ho_dict, gt_dict, pv_temp_dict, pv_power_dict, num_cells, panel, duration_array,location):
    """
    This function prints the result tab, and calculte avg and max values
    :param dicts: this function gets relevant dicts
    :param num_cells: the number of cells on face on the roof
    :param panel: contain information about the chosen panel, type: Panel
    :param duration_array:  array contains all the dates in the duration days that the user enters
    :param location: the location that the user enters , type:Loctaion
    :return: max values and pv_power_array
    """
    global result_list2
    temp_array,avg_temp =Arithmetics.calc_avg_data_per_day(temp_dict,"temp")
    max_values_temp_array, maximum_temp = Arithmetics.calc_max_value_per_day_from_dict(temp_dict)
    pv_temp_array,avg_pv_temp = Arithmetics.calc_avg_data_per_day(pv_temp_dict, "temp")
    max_values_pv_temp_array, maximum_pv_temp = Arithmetics.calc_max_value_per_day_from_dict(pv_temp_dict)
    ho_array,avg_ho = Arithmetics.calc_avg_data_per_day(ho_dict,"ho")
    irrad_array,avg_irrad = Arithmetics.calc_avg_data_per_day(irrad_dict)
    max_values_irrad_array, maximum_irrad = Arithmetics.calc_max_value_per_day_from_dict(irrad_dict)
    gt_array,avg_gt = Arithmetics.calc_avg_data_per_day(gt_dict)
    max_values_gt_array, maximum_gt = Arithmetics.calc_max_value_per_day_from_dict(gt_dict)
    kt_array,avg_kt = Arithmetics.calc_avg_data_per_day(kt_dict, "kt", duration_array, location)
    pv_power_array,avg_pv_power = Arithmetics.calc_avg_data_per_day(pv_power_dict)
    max_values_pv_power_array, maximum_pv_power = Arithmetics.calc_max_value_per_day_from_dict(pv_power_dict)
    total_pv_power = Power.calc_total_power_pv_array(pv_power_array,num_cells,panel)

    lable_list_info = [["Hourly average ambient temperature: ", 0.05, 0.41],
                       ["Maximum ambient temperature: ", 0.05, 0.44],
                       ["Hourly average cell temperature: ", 0.05, 0.47], ["Maximum cell temperature: ", 0.05, 0.5],
                       ["Daily average extraterrestrial global irradiance: ", 0.05, 0.55],
                       ["Daily average global irradiance: ", 0.05, 0.58],
                       ["Maximum global irradiance: ", 0.05, 0.61],
                       ["Daily average irradiance incident on PV array: ", 0.05, 0.64],
                       ["Maximun irradiance incident on PV array: ", 0.05, 0.67],
                       ["Daily average clearness index: ", 0.05, 0.72],
                       ["Daily average PV array energy output:  ", 0.05, 0.75],
                       ["Maximum PV array power output:  ", 0.05, 0.78],
                       ["Total PV array energy output:  ", 0.05, 0.81]]
    name_lable_list = []
    index_lists = 0

    result_info = [[str(format(avg_temp, ".2f")) + " [" + celsius + "C]", 0.3, 0.41],
                   [str(format(maximum_temp, ".2f")) + " [" + celsius + "C]", 0.265, 0.44],
                   [str(format(avg_pv_temp, ".2f")) + " [" + celsius + "C]", 0.265, 0.47],
                   [str(format(maximum_pv_temp, ".2f")) + " [" + celsius + "C]", 0.23, 0.5],
                   [str(format(avg_ho, ".2f")) + " [W/m\u00b2]", 0.36, 0.55],
                   [str(format(avg_irrad, ".2f")) + " [W/m\u00b2]", 0.26, 0.58],
                   [str(format(maximum_irrad, ".2f")) + " [W/m\u00b2]", 0.235, 0.61],
                   [str(format(avg_gt, ".2f")) + " [W/m\u00b2]", 0.35, 0.64],
                   [str(format(maximum_gt, ".2f")) + " [W/m\u00b2]", 0.32, 0.67],
                   [str(format(avg_kt, ".2f")), 0.26, 0.72],
                   [str(format(avg_pv_power, ".2f")) + " [J/m\u00b2]", 0.3, 0.75],
                   [str(format(maximum_pv_power, ".2f")) + " [W/m\u00b2]", 0.275, 0.78],
                   [str(format(total_pv_power / 1000, ".2f")) + " [KJ]", 0.25, 0.81]]


    if 'reset_win' in globals():
        for l in result_list2:
            l.destroy()
    result_list2 = []
    for inf,res in zip(lable_list_info,result_info):
        name_lable_list.append( Label(tab2_results, text=inf[0],font=("Gishal", 12, "bold"),bg='white'))
        name_lable_list[index_lists].place(anchor='w', relx=inf[1], rely=inf[2])
        result_list2.append(Label(tab2_results, text=res[0],font=("Gishal", 12),bg='white'))
        result_list2[index_lists].place(anchor='w', relx=res[1], rely=res[2])
        index_lists +=1

    return max_values_irrad_array, max_values_gt_array, max_values_pv_temp_array, pv_power_array


def convert_string_array_to_float(array):
    float_array =[]
    for i in array:
        float_array.append(float(i))
    return float_array


def graph_config(figure,figure1_frame,figure_toolbar_frame):
    """
    This function create a graph from frames
    :param figure: plot of the graph
    :param figure1_frame: frame of the plot
    :param figure_toolbar_frame: frame of the toolbar
    :return: canvas1, toolbar1
    """
    canvas1 = tkagg.FigureCanvasTkAgg(figure, figure1_frame)
    toolbar1 = tkagg.NavigationToolbar2Tk(canvas1, figure_toolbar_frame, pack_toolbar=False)
    toolbar1.update()
    toolbar1.pack(side=TOP)
    canvas1._tkcanvas.pack(side=RIGHT)
    canvas1.draw()
    canvas1.get_tk_widget().pack()
    return canvas1, toolbar1


def create_duration_array_with_none(duration_array):
    """
    This function sparse the duration_array
    :param duration_array: array contains all the dates in the duration days that the user enters
    :return: duration_array_with_none
    """
    duration_array_with_none = []
    x = math.floor(len(duration_array) / 24)
    index = 0
    if x == 0:
        return duration_array
    for d in duration_array:
        if index%(x+1) == 0:
            duration_array_with_none.append(d)
        else:
            duration_array_with_none.append(None)
        index +=1

    return duration_array_with_none


def fill_graphs_tab(irrad_dict, gt_dict,pv_temp_dict,pv_power_dict,duration_array,num_cells, panel, max_values_irrad_array, max_values_gt_array, max_values_pv_temp_array, pv_power_array):
    """
    This function create output graphs for tab 3
    :param dicts: this function gets relevant dicts
    :param duration_array: array contains all the dates in the duration days that the user enters
    :param num_cells: number of cells on the roof
    :param panel: contain information about the chosen panel, type: Panel
    :param max values: max values for the data
    :param pv_power_array: array contains the power values
    """
    global df_irrad
    global canvas_irrad, toolbar_irrad, canvas_gt, toolbar_gt
    global canvas_temp, toolbar_temp
    global canvas_power, toolbar_power
    global canvas_power_pv, toolbar_power_pv, error_label
    duration_array_str = []
    if 'error_label' in globals():
        error_label.destroy()

    for day in duration_array:
        duration_array_str.append(day.strftime("%d/%m/%Y"))

    if len(duration_array) == 1:
        try:
            array_hour = ['00:00', None, None, None, None, None, '01:00', None, None, None, None, None, '02:00',None, None, None, None, None, '03:00',
                          None, None, None, None, None, '04:00', None, None, None, None, None, '05:00',None, None, None, None, None, '06:00', None, None, None, None, None,
                          '07:00',None, None, None, None, None,'08:00',None, None, None, None, None,'09:00',None, None, None, None, None,'10:00',None, None, None, None, None,'11:00',None, None, None, None, None,'12:00',None, None, None, None, None,'13:00',None, None, None, None, None,'14:00',
                          None, None, None, None, None,'15:00',None, None, None, None, None,'16:00',None, None, None, None, None,'17:00',None, None, None, None, None,'18:00',None, None, None, None, None,'19:00',None, None, None, None, None,
                          '20:00',None, None, None, None, None,'21:00',None, None, None, None, None,'22:00',None, None, None, None, None,
                          '23:00',None, None, None, None, None]
            day = str(duration_array[0]).split(" ")[0].replace("-","/")

            data_irrad = {'Hour':array_hour,'Global irridance':convert_string_array_to_float(irrad_dict[day])}
            if 'df_irrad' in globals() :
                canvas_irrad.get_tk_widget().destroy()
                toolbar_irrad.destroy()
                canvas_gt.get_tk_widget().destroy()
                toolbar_gt.destroy()
                canvas_temp.get_tk_widget().destroy()
                toolbar_temp.destroy()
                canvas_power.get_tk_widget().destroy()
                toolbar_power.destroy()
                canvas_power_pv.get_tk_widget().destroy()
                toolbar_power_pv.destroy()
            df_irrad = DataFrame(data_irrad, columns=['Hour', 'Global irridance'])
            figure_irrad = plt.Figure(figsize=(5,5), dpi=75, tight_layout=True)
            ax_irrad = figure_irrad.add_subplot(111)
            df_irrad = df_irrad[['Hour', 'Global irridance']].groupby('Hour').sum()
            df_irrad.plot(kind='line', ax=ax_irrad, legend=False,ylabel = 'Global irradiance [W/m\u00b2]')
            ax_irrad.set_title('Global irradiance Vs. Hour')
            canvas_irrad,toolbar_irrad = graph_config(figure_irrad, figure_tab3_list[0], figure_toolbar_tab3_list[0])

            data_gt = {'Hour': array_hour, 'Incident irradiance on PV array': convert_string_array_to_float(gt_dict[day])}
            df_gt = DataFrame(data_gt, columns=['Hour', 'Incident irradiance on PV array'])
            figure_gt = plt.Figure(figsize=(5, 5), dpi=75,  tight_layout=True)
            ax_gt = figure_gt.add_subplot(111)
            df_gt = df_gt[['Hour', 'Incident irradiance on PV array']].groupby('Hour').sum()
            df_gt.plot(kind='line', ax=ax_gt, legend=False, ylabel='Incident irradiance on PV array [W/m\u00b2]')
            ax_gt.set_title('Incident irradiance on PV array Vs. Hour')
            canvas_gt,toolbar_gt = graph_config(figure_gt, figure_tab3_list[1], figure_toolbar_tab3_list[1])

            data_temp = {'Hour': array_hour, 'Temperature': convert_string_array_to_float(pv_temp_dict[day])}
            df_temp= DataFrame(data_temp, columns=['Hour', 'Temperature'])
            figure_temp = plt.Figure(figsize=(5, 5), dpi=75, tight_layout=True)
            ax_temp = figure_temp.add_subplot(111)
            df_temp = df_temp[['Hour', 'Temperature']].groupby('Hour').sum()
            df_temp.plot(kind='line', ax=ax_temp, legend=False, ylabel='Temperature [C'+celsius+']')
            ax_temp.set_title('Temperature PV cell Vs. Hour')
            canvas_temp,toolbar_temp=graph_config(figure_temp, figure_tab3_list[2], figure_toolbar_tab3_list[2])

            data_power = {'Hour': array_hour, 'Power': convert_string_array_to_float(pv_power_dict[day])}
            df_power = DataFrame(data_power, columns=['Hour', 'Power'])
            figure_power= plt.Figure(figsize=(5, 5), dpi=75, tight_layout=True)
            ax_power = figure_power.add_subplot(111)
            df_power = df_power[['Hour', 'Power']].groupby('Hour').sum()
            df_power.plot(kind='line', ax=ax_power, legend=False, ylabel='Power [W/m\u00b2]')
            ax_power.set_title('Power Vs. Hour for m\u00b2')
            canvas_power,toolbar_power = graph_config(figure_power, figure_tab3_list[3], figure_toolbar_tab3_list[3])

            power_pv_array = Power.calc_power_for_pv_array(convert_string_array_to_float(pv_power_dict[day]), num_cells, panel)
            data_power_array = {'Hour': array_hour, 'Power': power_pv_array}
            df_power_array = DataFrame(data_power_array, columns=['Hour', 'Power'])
            figure_power_array = plt.Figure(figsize=(5, 5), dpi=75, tight_layout=True)
            ax_power_array = figure_power_array.add_subplot(111)
            df_power_array = df_power_array[['Hour', 'Power']].groupby('Hour').sum()
            df_power_array.plot(kind='line', ax=ax_power_array, legend=False, ylabel='Power [KW]')
            ax_power_array.set_title('Power Vs. Hour for PV array')
            canvas_power_pv,toolbar_power_pv = graph_config(figure_power_array, figure_tab3_list[4], figure_toolbar_tab3_list[4])
        except:
            error_title = "Error while creating the graphs\nMissing some data from Israel Meteorological Service.\nPlease try another date"
            error_label = Label(tab3_DataTab.frame, text=error_title, bg='white',font=("Gishal", 20, "bold"))
            error_label.grid(row=1, column=1)
            return

    else:
        duration_array_str_with_none = create_duration_array_with_none(duration_array_str)
        data_irrad = {'Day': duration_array_str_with_none, 'Global irridance': max_values_irrad_array}
        if 'df_irrad' in globals():
            canvas_irrad.get_tk_widget().destroy()
            toolbar_irrad.destroy()
            canvas_irrad.get_tk_widget().destroy()
            toolbar_irrad.destroy()
            canvas_gt.get_tk_widget().destroy()
            toolbar_gt.destroy()
            canvas_temp.get_tk_widget().destroy()
            toolbar_temp.destroy()
            canvas_power.get_tk_widget().destroy()
            toolbar_power.destroy()
            canvas_power_pv.get_tk_widget().destroy()
            toolbar_power_pv.destroy()

        df_irrad = DataFrame(data_irrad, columns=['Day', 'Global irridance'])
        figure_irrad = plt.Figure(figsize=(5, 5), dpi=75, tight_layout=True)
        ax_irrad = figure_irrad.add_subplot(111)
        df_irrad = df_irrad[['Day', 'Global irridance']].groupby('Day',sort=False).sum()
        df_irrad.plot(kind='bar', ax=ax_irrad, legend=False, ylabel='Global irradiance [W/m\u00b2]')
        ax_irrad.set_title('Peak global irradiance for a day')
        canvas_irrad, toolbar_irrad = graph_config(figure_irrad, figure_tab3_list[0], figure_toolbar_tab3_list[0])

        data_gt = {'Day': duration_array_str_with_none, 'Incident irradiance on PV array': max_values_gt_array}
        df_gt = DataFrame(data_gt, columns=['Day', 'Incident irradiance on PV array'])
        figure_gt = plt.Figure(figsize=(5, 5), dpi=75, tight_layout=True)
        ax_gt = figure_gt.add_subplot(111)
        df_gt = df_gt[['Day', 'Incident irradiance on PV array']].groupby('Day',sort=False).sum()
        df_gt.plot(kind='bar', ax=ax_gt, legend=False, ylabel='Incident irradiance on PV array [W/m\u00b2]')
        ax_gt.set_title('Peak incident irradiance on PV array for a Day')
        canvas_gt,toolbar_gt = graph_config(figure_gt, figure_tab3_list[1], figure_toolbar_tab3_list[1])

        data_temp = {'Day': duration_array_str_with_none, 'Temperature':max_values_pv_temp_array}
        df_temp = DataFrame(data_temp, columns=['Day', 'Temperature'])
        figure_temp = plt.Figure(figsize=(5, 5), dpi=75, tight_layout=True)
        ax_temp = figure_temp.add_subplot(111)
        df_temp = df_temp[['Day', 'Temperature']].groupby('Day',sort=False).sum()
        df_temp.plot(kind='bar', ax=ax_temp, legend=False, ylabel='Temperature [C' + celsius + ']')
        ax_temp.set_title('Peak temperature PV cell for a Day')
        canvas_temp,toolbar_temp=graph_config(figure_temp, figure_tab3_list[2], figure_toolbar_tab3_list[2])

        data_power = {'Day': duration_array_str_with_none, 'Energy': pv_power_array}
        df_power = DataFrame(data_power, columns=['Day', 'Energy'])
        figure_power = plt.Figure(figsize=(5, 5), dpi=75, tight_layout=True)
        ax_power = figure_power.add_subplot(111)
        df_power = df_power[['Day', 'Energy']].groupby('Day',sort=False).sum()
        df_power.plot(kind='bar', ax=ax_power, legend=False, ylabel='Energy [J/m\u00b2]')
        ax_power.set_title('Energy Vs. Day for m\u00b2')
        canvas_power,toolbar_power = graph_config(figure_power, figure_tab3_list[3], figure_toolbar_tab3_list[3])

        max_values_pv_power_pv_array=[i*num_cells*panel.panel_width*panel.panel_lenght/1000 for i in pv_power_array]
        data_power_array = {'Day': duration_array_str_with_none, 'Energy': max_values_pv_power_pv_array}
        df_power_array = DataFrame(data_power_array, columns=['Day', 'Energy'])
        figure_power_array = plt.Figure(figsize=(5, 5), dpi=75, tight_layout=True)
        ax_power_array = figure_power_array.add_subplot(111)
        df_power_array = df_power_array[['Day', 'Energy']].groupby('Day',sort=False).sum()
        df_power_array.plot(kind='bar', ax=ax_power_array, legend=False, ylabel='Energy [KJ]')
        ax_power_array.set_title('Energy Vs. Day for PV array')
        canvas_power_pv,toolbar_power_pv =graph_config(figure_power_array, figure_tab3_list[4], figure_toolbar_tab3_list[4])


def fill_irrad_data_tab(array_all_data):
    """
    This function create a table with irradiance data
    :param array_all_data: array that contain all tha data we calculate (like gt)
    """
    irrad_table_frame=Frame(tab4_irrad_table, width=1180, height=750)
    irrad_table_frame.place(anchor='w', relx=0.05, rely=0.51)
    s = ttk.Style()
    s.layout('my.Treeview',[('Treeview.field', {'sticky': 'nswe', 'border': '1', 'children': [('Treeview.padding', {'sticky': 'nswe', 'children': [('Treeview.treearea', {'sticky': 'nswe'})]})]})])
    s.configure('my.Treeview.Heading',font=('Gishal', 10,'bold'))
    my_irrad_table = ttk.Treeview(irrad_table_frame,height=30,selectmode ='browse',style='my.Treeview')
    my_irrad_table['columns'] = ('Dates','Global Irradiance [W\m\u00b2]', 'Diffused Irradiance [W\m\u00b2]','Direct Irradiance [W\m\u00b2]', 'Incident Irradiance [W\m\u00b2]')
    my_irrad_table.column("#0", width=0, stretch=NO)
    my_irrad_table.heading("#0", text="", anchor=CENTER)
    column_heading = ["Dates","Global Irradiance [W\m\u00b2]","Diffused Irradiance [W\m\u00b2]","Direct Irradiance [W\m\u00b2]","Incident Irradiance [W\m\u00b2]"]
    for heading in column_heading:
        my_irrad_table.column(heading, anchor=CENTER, width=175)
        my_irrad_table.heading(heading, text=heading, anchor=CENTER)

    index = 0
    for a in array_all_data:
        my_irrad_table.insert(parent='',index='end',iid=index,text='', values=(a[0],a[1][0],a[1][3],a[1][4],a[1][5]))
        index +=1
    my_irrad_table.grid(row=0, column=0, sticky='nsew')
    scrollbar = ttk.Scrollbar(irrad_table_frame, orient=VERTICAL, command=my_irrad_table.yview)
    my_irrad_table.configure(yscroll=scrollbar.set)
    scrollbar.grid(row=0, column=1, sticky='ns')

    warning_text1 = "Pay attention"
    warning_text1_label = Label(tab4_irrad_table, text=warning_text1, font=("Gishal", 12, 'bold'), bg='white',fg='darkred')
    warning_text1_label.place(anchor='e', relx=0.95, rely=0.3)

    warning_mess_text1 = "Global irradiance is\nmeasured from meteorological\nstaion. Other irradiances\nare calculated using\nan algorithm"
    warning_mess_text1_label = Label(tab4_irrad_table, text=warning_mess_text1, font=("Gishal", 11), bg='white')
    warning_mess_text1_label.place(anchor='e', relx=0.995, rely=0.385)


def fill_temp_data_tab(array_all_data):
    """
    This function create a table with temp data
    :param array_all_data: array that contain all tha data we calculate (like gt)
    """
    temp_table_frame=Frame(tab5_temp_table, width=1180, height=750)
    temp_table_frame.place(anchor='w', relx=0.05, rely=0.51)
    s = ttk.Style()
    s.layout('my.Treeview',[('Treeview.field', {'sticky': 'nswe', 'border': '1', 'children': [('Treeview.padding', {'sticky': 'nswe', 'children': [('Treeview.treearea', {'sticky': 'nswe'})]})]})])
    s.configure('my.Treeview.Heading',font=('Gishal', 10,'bold'))
    my_temp_table = ttk.Treeview(temp_table_frame,height=30,selectmode ='browse',style='my.Treeview')
    my_temp_table['columns'] = ('Dates','Ambient Temperature ['+celsius+'C]', 'PV Cell Temperature ['+celsius+'C]')
    my_temp_table.column("#0", width=0, stretch=NO)
    my_temp_table.heading("#0", text="", anchor=CENTER)
    column_heading = ["Dates",'Ambient Temperature ['+celsius+'C]','PV Cell Temperature ['+celsius+'C]']
    for heading in column_heading:
        my_temp_table.column(heading, anchor=CENTER, width=175)
        my_temp_table.heading(heading, text=heading, anchor=CENTER)
    index = 0
    for a in array_all_data:
       my_temp_table.insert(parent='',index='end',iid=index,text='', values=(a[0],a[1][1],a[1][6]))
       index +=1
    my_temp_table.grid(row=0, column=0, sticky='nsew')
    scrollbar= ttk.Scrollbar(temp_table_frame, orient=VERTICAL, command=my_temp_table.yview)
    my_temp_table.configure(yscroll=scrollbar.set)
    scrollbar.grid(row=0, column=1, sticky='ns')
    warning_text2 = "Pay attention"
    warning_text2_label = Label(tab5_temp_table, text=warning_text2, font=("Gishal", 12, 'bold'), bg='white',
                                fg='darkred')
    warning_text2_label.place(anchor='e', relx=0.774, rely=0.12)
    warning_mess_text2 = "Ambient Tempreture is\nmeasured from meteorological\nstaion. The PV cell\ntempreture is calculate\nusing an algorithm"
    warning_mess_text2_label = Label(tab5_temp_table, text=warning_mess_text2, font=("Gishal", 11), bg='white')
    warning_mess_text2_label.place(anchor='e', relx=0.815, rely=0.205)


def fill_energy_data_tab(array_all_data):
    """
      This function create a table with energy data
      :param array_all_data: array that contain all tha data we calculate (like gt)
      """
    energy_table_frame=Frame(tab6_power_table, width=1180, height=750)
    energy_table_frame.place(anchor='w', relx=0.05, rely=0.51)
    s = ttk.Style()
    s.layout('my.Treeview',[('Treeview.field', {'sticky': 'nswe', 'border': '1', 'children': [('Treeview.padding', {'sticky': 'nswe', 'children': [('Treeview.treearea', {'sticky': 'nswe'})]})]})])
    s.configure('my.Treeview.Heading',font=('Gishal', 10,'bold'))
    my_energy_table = ttk.Treeview(energy_table_frame,height=30,selectmode ='browse',style='my.Treeview')
    my_energy_table['columns'] = ('Dates','Power [W\m\u00b2]', 'Clearness index')
    my_energy_table.column("#0", width=0, stretch=NO)
    my_energy_table.column("Dates", anchor=CENTER, width=150)
    my_energy_table.heading("#0", text="", anchor=CENTER)
    column_heading = ["Dates", "Power [W\m\u00b2]", "Clearness index"]
    for heading in column_heading:
        my_energy_table.column(heading, anchor=CENTER, width=175)
        my_energy_table.heading(heading, text=heading, anchor=CENTER)
    index = 0
    for a in array_all_data:
       my_energy_table.insert(parent='',index='end',iid=index,text='', values=(a[0],a[1][7],a[1][2]))
       index +=1
    my_energy_table.grid(row=0, column=0, sticky='nsew')
    scrollbar= ttk.Scrollbar(energy_table_frame, orient=VERTICAL, command=my_energy_table.yview)
    my_energy_table.configure(yscroll=scrollbar.set)
    scrollbar.grid(row=0, column=1, sticky='ns')


def get_initial_data(location):
    """
    This function get and calculate basic information for running the simulation
    :param location: the location that the user enter, type: Location
    :return: panels_array_info,station_dict, s_date_yearly,station_name, azimuth,start_date, end_date,opt_tilt
    """
    start_date_array = start_calender.get_date().split('-')
    end_date_array = end_calender.get_date().split('-')
    start_date = datetime(int(start_date_array[0]),int(start_date_array[1]),int(start_date_array[2]))
    end_date = datetime(int(end_date_array[0]), int(end_date_array[1]), int(end_date_array[2]))
    last_year = end_date.year - 1
    s_date_yearly = datetime(last_year,1,1)
    station_dict = Station_Info.create_station_dict_from_csv()
    station_dict = Station_Info.update_grad_csv_file(station_dict)

    station_name = Station_Info.get_closest_grad_station(station_dict, [location.latitude, location.longitude])
    panels_array_info = Power.get_panels_data()
    azimuth = Angle.find_azimuth_angle(azimuth_cb.get())
    # for opt tilt
    if clicked_roof_type.get() == 0:
        irad_dict_year, start_date_year = Irad.create_irrad_dict_for_year(station_dict, station_name, s_date_yearly)
        opt_tilt = Angle.get_opt_tilt(location, irad_dict_year, start_date_year, 365)
    else:
        opt_tilt = float(roof_tilt_entry.get())
    return panels_array_info,station_dict, s_date_yearly,station_name, azimuth,start_date, end_date,opt_tilt


def run_simulation(location_right_down_roof,location):
    """
    This function get all the result of the simulation and fill the results tab
    :param location_right_down_roof:
    :param location: the location that the user enter, type: Location
    """
    roof_coors = []
    cells = []
    tabs_list = [[tab2_results,"Results"],[tab3_graphs,"Graphs"],[tab4_irrad_table,"Irradiance Data"],[tab5_temp_table,"Temperature Data"],[tab6_power_table,"Power Data"]]
    panels_array_info, station_dict, s_date_yearly, station_name, azimuth, start_date, end_date,opt_tilt = get_initial_data(location)
    panel = panels_array_info[clicked_pv_cells_type.get()]
    #Roof placing
    if clicked_roof_information.get() == 1:
        if clicked_roof_type.get() == 0:
            is_tilt_roof = False
        else:
            is_tilt_roof = True
        num_cells, cells,roof_coors = Roof_placing.placing_on_roof(location_right_down_roof, azimuth, float(length_roof_entry.get()), float(width_roof_entry.get()), panel.panel_lenght, panel.panel_width,
                                                                    float(distance_between_cells_entry.get()), is_tilt_roof, opt_tilt, float(distance_from_roof_edge_entry.get()))
    else:
        num_cells = int(num_panel_entry.get())

    irrad_dict, temp_dict,kt_dict, ho_dict, gd_dict, gb_dict, gt_dict,pv_temp_dict,pv_power_dict,duration_array,array_all_data = creating_dicts_data(start_date, end_date, location, station_name, opt_tilt, station_dict, panel)
    for t in tabs_list:
        tabs.add(t[0], text=t[1])

    max_values_irrad_array, max_values_gt_array, max_values_pv_temp_array, pv_power_array = fill_result_tab_irad_temp_power(irrad_dict, temp_dict, kt_dict, ho_dict, gt_dict, pv_temp_dict,pv_power_dict,num_cells,panel,duration_array,location)
    fill_result_tab(opt_tilt, num_cells, cells, roof_coors, station_name, location)
    fill_graphs_tab(irrad_dict, gt_dict,pv_temp_dict,pv_power_dict,duration_array,num_cells,panel, max_values_irrad_array, max_values_gt_array, max_values_pv_temp_array, pv_power_array)
    fill_irrad_data_tab(array_all_data)
    fill_temp_data_tab(array_all_data)
    fill_energy_data_tab(array_all_data)


def check_entries():
    """
    This function checking the entries and send to function that run the simulation
    """
    location_left_down_roof = None
    if start_calender.get_date() > end_calender.get_date() or start_calender.get_date() == "" or end_calender.get_date() == "":
        messagebox.showwarning("Warning", "Start date must be before the end date.\nPlease try again.")
        return
    if clicked_location.get() == 100:
        messagebox.showwarning("Warning", "Must choose one the option to location.\nPlease try again.")
        return
    if clicked_roof_information.get() == 100:
        messagebox.showwarning("Warning", "Must choose a way to calculate cells number.\nPlease try again.")
        return
    if clicked_roof_type.get() == 100:
        messagebox.showwarning("Warning", "Must choose roof type.\nPlease try again.")
        return
    if clicked_pv_cells_type.get() == 100:
        messagebox.showwarning("Warning", "Must choose one of the cells.\nPlease try again.")
        return

    location = get_location_info(location_entry.get(), clicked_location.get())
    if location == None:
        messagebox.showwarning("Warning", "Could not find location.\nPlease try again.")
        return

    if clicked_roof_information.get()== 0:
        try:
            if int(num_panel_entry.get()) < 0:
                messagebox.showwarning("Warning", "Number of cells could not be negative.\nPlease try again.")
                return
        except:
            messagebox.showwarning("Warning", "Number of cells is not an integer.\nPlease try again.")
            return
    if clicked_roof_information.get() == 1:
        location_left_down_roof = get_location_info(coor_of_the_roof_entry.get(), 1)
        if location_left_down_roof == None:
            messagebox.showwarning("Warning", "Could not find location for roof.\nPlease try again.")
            return
        try:
            if float(length_roof_entry.get()) < 0 or float(width_roof_entry.get())<0:
                messagebox.showwarning("Warning", "Length or width of the roof could not be negative.\nPlease try again.")
                return
        except:
            messagebox.showwarning("Warning", "Length or width of the roof is not a float.\nPlease try again.")
            return

    if clicked_roof_type.get() == 1:
        try:
            if float(roof_tilt_entry.get()) <0 or float(roof_tilt_entry.get()) >90:
                messagebox.showwarning("Warning", "Tilt angle must be between 0-90"+celsius+".\nPlease try again.")
                return
        except:
            messagebox.showwarning("Warning", "Tilt angle is not a float.\nPlease try again.")
            return
    run_simulation(location_left_down_roof,location)


if __name__ == '__main__':
    res_w = False
    celsius = u"\u00b0"
    window = Tk()
    window.title('PV Calculator')
    window.geometry("1200x780+10+10")
    window.configure(bg='white')
    #Tabs
    tabs = ttk.Notebook(window)
    tabs.pack()
    tab1_main, tab2_results, tab3_graphs,tab4_irrad_table, tab5_temp_table,tab6_power_table = Frame(tabs,width=1180, height=750),Frame(tabs,width=1180, height=750),Frame(tabs,width=1180, height=750),Frame(tabs,width=1180, height=750),Frame(tabs,width=1180, height=750),Frame(tabs,width=1180, height=750)
    tabs_lst = [(tab1_main, "Setup"), (tab2_results, "Results"),(tab3_graphs, "Graphs"),(tab4_irrad_table, "Irradiance Data"),(tab5_temp_table, "Temperature Data"),(tab6_power_table, "Power Data")]
    for tab,title in tabs_lst:
        tab.configure(bg='white')
        tab.pack(fill="both", expand=1)
        tabs.add(tab, text=title)
    for i in range(len(tabs_lst)):
        if i !=0:
            tabs.hide(i)
    # Logo
    logo = ImageTk.PhotoImage(Image.open("logo.png"))
    for j in range(len(tabs_lst)):
        logo_frame = Frame(tabs_lst[j][0], width=600, height=400)
        logo_frame.pack()
        logo_frame.place(anchor='center', relx=0.93, rely=0.085)
        label_logo = Label(logo_frame, image=logo)
        label_logo.pack()

    # roof picture for power
    roof_pic = ImageTk.PhotoImage(Image.open("roof.jpg"))
    roof_pic_frame = Frame(tabs_lst[-1][0], width=100, height=100)
    roof_pic_frame.pack()
    roof_pic_frame.place(anchor='center', relx=0.76, rely=0.52)
    label_roof_pic = Label(roof_pic_frame, image=roof_pic)
    label_roof_pic.pack()

    # roof picture for temp
    pv_pic = ImageTk.PhotoImage(Image.open("pv_pic.jpg"))
    pv_pic_frame = Frame(tabs_lst[4][0], width=100, height=100)
    pv_pic_frame.pack()
    pv_pic_frame.place(anchor='center', relx=0.76, rely=0.52)
    label_pv_pic = Label(pv_pic_frame, image=pv_pic)
    label_pv_pic.pack()

    # tab3
    tab3_DataTab = DataTab(tab3_graphs)
    logo_frame = Frame(tab3_DataTab.canvas, width=5000, height=5000)
    logo_frame.place(anchor='center', relx=0.93, rely=0.085)
    label_logo = Label(logo_frame, image=logo)
    label_logo.pack(anchor='e')
    output_graphs_title = "Output Graphs"
    output_graphs_title = Label(tab3_DataTab.frame, text=output_graphs_title, bg='white', fg='dark blue',font=("Cooper Black", 30, "bold"))
    output_graphs_title.grid(row=1, column=3)

    figure_tab3_list = []
    figure_toolbar_tab3_list = []
    figure_tab3_list_grid=[[2, 2],[2,3],[4,2],[4,3],[4,4]]
    for i in range(5):
        figure_tab3_list.append(Frame(master=tab3_DataTab.frame, width=5000, height=5000))
        figure_tab3_list[i].grid(row = figure_tab3_list_grid[i][0],column = figure_tab3_list_grid[i][1])
        figure_toolbar_tab3_list.append(Frame(master=tab3_DataTab.frame))
        figure_toolbar_tab3_list[i].grid(row=figure_tab3_list_grid[i][0]+1, column=figure_tab3_list_grid[i][1])

    # tab4
    irrad_data_title = "Irradiance Data"
    head_irrad_title_frame = FrameBuilder(tab4_irrad_table, 0.35, 0.05, irrad_data_title)
    head_irrad_title_frame.label.config(fg='dark blue', font=("Cooper Black", 30, "bold"))

    #tab5
    temp_data_title = "Temperature Data"
    head_temp_title_frame = FrameBuilder(tab5_temp_table, 0.35, 0.05, temp_data_title)
    head_temp_title_frame.label.config(fg='dark blue', font=("Cooper Black", 30, "bold"))

    # tab6
    power_data_title = "Power And Clearness Data"
    head_power_title_frame = FrameBuilder(tab6_power_table, 0.35, 0.05, power_data_title)
    head_power_title_frame.label.config(fg='dark blue', font=("Cooper Black", 30, "bold"))

    #Title
    head_title = "PV Calculator"
    head_title_frame = FrameBuilder(tab1_main,0.35,0.05,head_title)
    head_title_frame.label.config(fg='dark blue', font=("Cooper Black", 30,"bold"))
    description = "Welcome to PV Calculator!\n This tool is designed to find you the best PV system for yours roof"
    description_frame = FrameBuilder(tab1_main, 0.225, 0.12, description)
    description_frame.label.config(font=(15))

    #info img
    info_open = Image.open("info.png")
    resized_info = info_open.resize((18, 18), Image.ANTIALIAS)
    info = ImageTk.PhotoImage(resized_info)

    # Location input frame
    location_frame = FrameBuilder(tab1_main, 0.07, 0.235, "Choose location type - Address or Coordinates",700, 500)
    clicked_location = IntVar()
    clicked_location.set(100)
    Radiobutton(location_frame.frame, text="Address", variable=clicked_location, font=("Gishal", 12),value=0,bg="white",
                command=lambda: config_loc_txt(clicked_location.get(), location_entry)).pack(anchor=W)
    Radiobutton(location_frame.frame, text="Coordinates",font=("Gishal", 12), variable=clicked_location, value=1,bg="white",
                command=lambda: config_loc_txt(clicked_location.get(), location_entry)).pack(anchor=W)
    location_entry = Entry(location_frame.frame, width=50,bd=2)
    location_entry.pack(anchor='w')
    azimuth_lable = Label(tab1_main, text="Azimuth: ", font=("Gishal", 12),bg='white')
    azimuth_lable.place(anchor='w', relx=0.07, rely=0.325)
    azimuth_list= StringVar()
    azimuth_list.set("North")
    azimuth_data = ("North", "South", "West", "East", "North west", "North east", "South west","South east")
    azimuth_cb = Combobox(tab1_main, values=azimuth_data)
    azimuth_cb.place(anchor='w', relx=0.14, rely=0.325)
    azimuth_cb.current(0)
    azimuth_info_txt = "Which azimuth the roof is facing"
    info_azimuth_frame = Info_img(tab1_main, 0.28, 0.325, azimuth_info_txt, info,width=0.1, height=100)

    #Roof information
    number_cells_frame = FrameBuilder(tab1_main, 0.07, 0.54, "Choose one of the following ways to calculate cells numbers:",700,250)
    number_cells_frame.frame.pack_propagate(0)
    clicked_roof_information = IntVar()
    clicked_roof_information.set(100)
    Radiobutton(number_cells_frame.frame, text="Number of PV panels",variable=clicked_roof_information, font=("Gishal", 12), value=0,
                bg="white",command = lambda: disable_num_panel_entry(1)).pack(anchor=W)
    num_panel_entry = Entry(number_cells_frame.frame, width=50, bd=2,state = "disabled")
    num_panel_entry.pack(anchor='w')
    num_pv_info_txt = "While choosing this option the application of placing PV panels on the roof will be disable "
    num_pv_info_frame = Info_img(number_cells_frame.frame, 0.28, 0.15, num_pv_info_txt, info, width=0.1, height=100)

    Radiobutton(number_cells_frame.frame, text="Roof information", font=("Gishal", 12), variable=clicked_roof_information, value=1,
                bg="white",command = lambda: disable_num_panel_entry(2)).pack(anchor=W)

    coor_of_the_roof = Label(number_cells_frame.frame, text="Coordinate of the roof: ", font=("Gishal", 12), bg='white')
    coor_of_the_roof.place(anchor='w', relx=0.05, rely=0.46)
    coor_of_the_roof_entry = Entry(number_cells_frame.frame, width=25, bd=2, state="disabled")
    coor_of_the_roof_entry.place(anchor='w', relx=0.37, rely=0.46)
    roof_coor_txt = "Please enter right down most coordinate of the roof"
    roof_coor_frame = Info_img(number_cells_frame.frame, 0.62, 0.46, roof_coor_txt, info, width=0.1, height=100)
    length_roof = Label(number_cells_frame.frame, text="Length of the roof: ", font=("Gishal", 12), bg='white')
    length_roof.place(anchor='w', relx=0.05, rely=0.57)
    length_roof_entry = Entry(number_cells_frame.frame, width=25, bd=2, state="disabled")
    length_roof_entry.place(anchor='w', relx=0.37, rely=0.57)
    length_width_coor_txt = "Please Enter in units of meters"
    length_roof_info_frame = Info_img(number_cells_frame.frame, 0.62, 0.57, length_width_coor_txt, info, width=0.1, height=100)
    width_roof = Label(number_cells_frame.frame, text="Width of the roof: ", font=("Gishal", 12), bg='white')
    width_roof.place(anchor='w', relx=0.05, rely=0.68)
    width_roof_entry = Entry(number_cells_frame.frame, width=25, bd=2, state="disabled")
    width_roof_entry.place(anchor='w', relx=0.37, rely=0.68)
    width_roof_info_frame = Info_img(number_cells_frame.frame, 0.62, 0.68, length_width_coor_txt, info, width=0.1,height=100)
    distance_between_cells = Label(number_cells_frame.frame, text="Distance between PV arrays: ", font=("Gishal", 12), bg='white')
    distance_between_cells.place(anchor='w', relx=0.05, rely=0.79)
    distance_between_cells_entry = Entry(number_cells_frame.frame, width=25, bd=2, state="disabled")
    distance_between_cells_entry.place(anchor='w', relx=0.37, rely=0.79)
    distance_between_cells_info_txt = "This is the distance between two rows of Pv arrays, the default value is 0.5 meter"
    distance_between_cells_info_frame = Info_img(number_cells_frame.frame, 0.62, 0.79, distance_between_cells_info_txt, info, width=0.1,
                                height=100)

    distance_from_roof_edge = Label(number_cells_frame.frame, text="Distance from roof edge: ", font=("Gishal", 12),bg='white')
    distance_from_roof_edge.place(anchor='w', relx=0.05, rely=0.9)
    distance_from_roof_edge_entry = Entry(number_cells_frame.frame, width=25, bd=2, state="disabled")
    distance_from_roof_edge_entry.place(anchor='w', relx=0.37, rely=0.9)
    distance_from_roof_edge_info_txt = "Distance from roof edges to start placing the PV arrays, the default value is 0.5 meter"
    distance_from_roof_edge_info_frame = Info_img(number_cells_frame.frame, 0.62, 0.9, distance_from_roof_edge_info_txt,info, width=0.1,height=100)

    #Roof type and opt tilt
    roof_type_frame = FrameBuilder(tab1_main, 0.07, 0.82,
                                      "Choose your roof type:", 700, 150)
    roof_type_frame.frame.pack_propagate(0)
    clicked_roof_type = IntVar()
    clicked_roof_type.set(100)
    Radiobutton(roof_type_frame.frame, text="Horizontal roof", variable=clicked_roof_type,
                font=("Gishal", 12), value=0,bg="white").pack(anchor=W)
    horizontal_roof_info_txt = "While choosing this option the system will calculate the optimal tilts for placing your PV system"
    horizontal_roof_info_frame = Info_img(roof_type_frame.frame, 0.22, 0.25, horizontal_roof_info_txt,info, width=0.1,height=100)
    Radiobutton(roof_type_frame.frame, text="Tilted roof", variable=clicked_roof_type,
                font=("Gishal", 12), value=1,bg="white",command = lambda: disable_num_panel_entry(3)).pack(anchor=W)
    roof_tilt_label = Label(roof_type_frame.frame, text="Roof angle: ", font=("Gishal", 12), bg='white')
    roof_tilt_label.place(anchor='w', relx=0.05, rely=0.61)
    roof_tilt_entry = Entry(roof_type_frame.frame, width=25, bd=2, state="disabled")
    roof_tilt_entry.place(anchor='w', relx=0.19, rely=0.61)
    roof_tilt_info_txt = "Please enter angle in degree units\nDegree must be between 0-90"+celsius
    roof_tilt_info_frame = Info_img(roof_type_frame.frame, 0.17, 0.45, roof_tilt_info_txt, info,
                                               width=0.1, height=100)

    #PV cells type
    pv_cells_type_frame = FrameBuilder(tab1_main, 0.53, 0.6,"Please choose PV model type:", 700, 200)
    pv_cells_type_frame.frame.pack_propagate(0)
    clicked_pv_cells_type = IntVar()
    clicked_pv_cells_type.set(100)
    Radiobutton(pv_cells_type_frame.frame, text="JKM465M-7RL3-BDVP, jinco", variable=clicked_pv_cells_type,font=("Gishal", 12), value=0, bg="white").pack(anchor=W)
    first_cell_info_txt = "Peak power STC [W]: 465\nPeak power NOCT [W]: 346\nNOCT [" + celsius + "C]: 45\nAlpha p [%]: -0.35\nEfficiency [%]: 20.34\nLength [m]:2.205\nWidth [m]:1.032"
    first_cell_info_frame = Info_img(pv_cells_type_frame.frame, 0.43, 0.19, first_cell_info_txt, info,width=0.1, height=100)
    Radiobutton(pv_cells_type_frame.frame, text="JKM465M-7RL3-V, jinco", variable=clicked_pv_cells_type,font=("Gishal", 12), value=1, bg="white").pack(anchor=W)
    second_cell_info_txt = "Peak power STC [W]: 465\nPeak power NOCT [W]: 346\nNOCT [" + celsius + "C]: 45\nAlpha p [%]: -0.35\nEfficiency [%]: 20.71\nLength [m]:2.182\nWidth [m]:1.029"
    second_cell_info_frame = Info_img(pv_cells_type_frame.frame, 0.43, 0.34, second_cell_info_txt, info, width=0.1,height=100)
    Radiobutton(pv_cells_type_frame.frame, text="JAM72S20-465/MR, Jasolar", variable=clicked_pv_cells_type,font=("Gishal", 12), value=2, bg="white").pack(anchor=W)
    third_cell_info_txt = "Peak power STC [W]: 465\nPeak power NOCT [W]: 352\nNOCT [" + celsius + "C]: 45\nAlpha p [%]: -0.35\nEfficiency [%]: 20.8\nLength [m]:2.120\nWidth [m]:1.052"
    third_cell_info_frame = Info_img(pv_cells_type_frame.frame, 0.43, 0.49, third_cell_info_txt, info, width=0.1,height=100)
    Radiobutton(pv_cells_type_frame.frame, text="TSM-DE17M-460, TALLMAX/Trina", variable=clicked_pv_cells_type,font=("Gishal", 12), value=3, bg="white").pack(anchor=W)
    forth_cell_info_txt = "Peak power STC [W]: 460\nPeak power NOCT [W]: 347\nNOCT [" + celsius + "C]: 43\nAlpha p [%]: -0.34\nEfficiency [%]: 21\nLength [m]:2.102\nWidth [m]:1.020"
    forth_cell_info_frame = Info_img(pv_cells_type_frame.frame, 0.43, 0.64, forth_cell_info_txt, info, width=0.1,height=100)
    Radiobutton(pv_cells_type_frame.frame, text="LR4-72PH-460M, HI-MO/Longi", variable=clicked_pv_cells_type,font=("Gishal", 12), value=4, bg="white").pack(anchor=W)
    fifth_cell_info_txt = "Peak power STC [W]: 460\nPeak power NOCT [W]: 343.5\nNOCT [" + celsius + "C]: 45\nAlpha p [%]: -0.35\nEfficiency [%]: 21.2\nLength [m]:2.094\nWidth [m]:1.038"
    fifth_cell_info_frame = Info_img(pv_cells_type_frame.frame, 0.43, 0.79, fifth_cell_info_txt, info, width=0.1,height=100)
    #Date
    yesterday = datetime.today()- timedelta(1)
    date1_frame = FrameBuilder(tab1_main, 0.53 , 0.3 ,"Please choose start date" )
    start_calender = Calendar(date1_frame.frame, year=yesterday.year, month=yesterday.month, firstweekday="sunday",
                    maxdate=yesterday, date_pattern="y-mm-dd", selectmode="day", background="midnightblue",
                    headersbackground="cornflowerblue",
                    selectbackground="darkgreen", normalbackground="azure")
    start_calender.pack()
    date2_frame = FrameBuilder(tab1_main, 0.755 , 0.3 ,"Please choose end date" )
    end_calender = Calendar(date2_frame.frame, year=yesterday.year, month=yesterday.month, firstweekday="sunday",
                    mindate=start_calender.selection_get(), maxdate=yesterday, date_pattern="y-mm-dd", selectmode="day",
                    background="midnightblue", headersbackground="cornflowerblue",
                    selectbackground="darkgreen", normalbackground="azure")
    end_calender.pack()

    #Run and Reset
    run_btn = Button(tab1_main, text="Run",height = 1, width = 6, font = ("Gishal",10, "bold"),command = check_entries)
    run_btn.place(anchor='w', relx=0.93, rely=0.97)
    rst_btn = Button(tab1_main, text="Reset",height = 1, width = 6, font = ("Gishal",10, "bold"), command=reset)
    rst_btn.place(anchor='w', relx=0.88, rely=0.97)

    window.mainloop()

