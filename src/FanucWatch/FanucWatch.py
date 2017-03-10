'''
Created on Sep 16, 2016

@author: evan.jensen

Evanmj@gmail.com
'''
from lxml import html
from lxml import etree
import requests        # pip install requests
import time
import os
import random

from bokeh.plotting import figure, output_file, show
from bokeh.models import Range1d

custom_y_scale = []

#RegistersToMonitor = [302,303,304,305]  # wings runout
#RegistersToMonitor = [308,309]  # Stem runout
#RegistersToMonitor = [306,307]  # Diameter Stem
#RegistersToMonitor = [331]  # Oven Conveyor Index Accuracy
RegistersToMonitor = [252,253]
#RegistersToMonitor = [336]  # oven conv clmpl

#custom_y_scale = [18000,20000]  #wings runout
#custom_y_scale = [45000,55000]  #Stem runout
#custom_y_scale = [125500,126500]  #Stem Diameter
#custom_y_scale = [30,40]  #Stem Diameter

clear = lambda: os.system('cls')

random.seed()

free_run = False

data_points_stored = 0

prog_start_time = time.time() * 1000



#setup dict
myData = {}
myData2 = {}
for r in RegistersToMonitor:
    myData[str(r)] = {}

print(myData)

def plot_now(data,use_measured_time=False):
    
    # build bokeh graph    
    TOOLS = 'box_zoom,box_select,hover,resize,reset,save'
    if use_measured_time:
        x_label = 'Time'
    else:
        x_label = 'Data Collection Request #'
    
    p = figure(title="Fanuc Data", x_axis_label=x_label, y_axis_label='Value',plot_width=1300, plot_height=500, tools=TOOLS)
    if custom_y_scale != []:
        p.y_range = Range1d(custom_y_scale[0],custom_y_scale[1]) # force scale for now (TEMPORARY!!!!)
        
    for trace in data:
        #print(data[trace])
        i = 1  #start at fake time 1
        color = (random.random()*170,random.random()*170,random.random()*170,1)
        color_line = (color[0],color[1],color[2],0.25)
        print(color)

        trace_name = data[trace]['NAME']
        
        this_trace_x = []
        this_trace_y = []
        
        for pt in data[trace]['DATA']:
            
            # now pt is a (time,value) tuple.
            if use_measured_time:
                this_trace_x.append(pt[0])
            else:
                this_trace_x.append(i)
                i = i + 1
            this_trace_y.append(pt[1])
            
        
        print("x: " + repr(this_trace_x))
        print("y: " + repr(this_trace_y))
        
        # build a trace for this point.
        p.circle(this_trace_x, this_trace_y, fill_color="white", size=8, line_color = color)
        p.line(this_trace_x, this_trace_y, legend=trace_name, line_width=2, line_color = color_line)
        
        
        
    # output to static HTML file
    output_file("lines.html", title="Fanuc Data")
    
    # show the results
    show(p)


while True:
    
    if not free_run:

        print()
        users_input = input("Data Points Stored: %d, Press Enter to pull a data field, F to free run, Y for y scale, or P for plot stored data..." % data_points_stored)
        
        if users_input == 'f' or users_input == 'F':
            print("Starting Free Run.")
            free_run = True
        elif users_input == 'p' or users_input == 'P':
            print("Plotting Data.")
            plot_now(myData2)
        elif users_input == 'y' or users_input == 'Y':
            users_input = input("Enter new Min Y...")
            custom_y_scale[0] = int(users_input)
            cusers_input = input("Enter new Max Y...") 
            custom_y_scale[1] = int(users_input)
            print("Got it.")
        else:
            #grab new data now.
            page = requests.get('http://192.168.3.11/karel/ComGet?sFc=28')
            
            tree = html.fromstring(page.text)  
            
            clear() # clear monitor
            
            this_data = {}
            time_now = int((time.time() * 1000) - prog_start_time)
            
            for R in RegistersToMonitor:
                
                time_series = {}
                time_series[time_now] = ''
                
                td_row = R + 1 #avoid header.
                
                Comment_Val = tree.xpath('//*[@id="formTable"]/table/tr[' + str(td_row) + ']/td[2]/p/input')
                InputBox = tree.xpath('//*[@id="formTable"]/table/tr[' + str(td_row) + ']/td[3]/p/input')
                if Comment_Val[0].value != '':
                    Comment_Val[0].value = ':' + Comment_Val[0].value
                
                point_name = 'R[' + str(R) + Comment_Val[0].value + ']'
                point_value = InputBox[0].value
        
                this_data['value'] = point_value
                this_data['name'] = point_name
                
                time_series[time_now] = this_data
                
                print(time_series)
                
                if R in myData2:
                    myData2[R]['NAME']=point_name
                else:
                    #print ("Initializing for %d" % R)
                    #print ("Name is: " + point_name)
                    myData2[R]={'NAME':point_name, 'DATA':[]}
                if 'DATA' in myData2[R]:
                    myData2[R]['DATA'].append((time_now, point_value))
                
                
            data_points_stored = data_points_stored + 1    
            #print(myData)
            #print(myData2)                   
    else:
        
        page = requests.get('http://192.168.3.11/karel/ComGet?sFc=28')
            
        tree = html.fromstring(page.text)  
        
        clear() # clear monitor
        
        for R in RegistersToMonitor:
            
            td_row = R + 1 #avoid header.
            
            Comment_Val = tree.xpath('//*[@id="formTable"]/table/tr[' + str(td_row) + ']/td[2]/p/input')
            InputBox = tree.xpath('//*[@id="formTable"]/table/tr[' + str(td_row) + ']/td[3]/p/input')
            if Comment_Val[0].value != '':
                Comment_Val[0].value = ':' + Comment_Val[0].value
            
            print('R[' + str(R) + Comment_Val[0].value + '] = ' + InputBox[0].value)
        
        time.sleep(2)





