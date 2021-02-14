# To install pymongo, type the following command in terminal
    # pip install pymongo[srv]
# To run this script type the following command in terminal
    # bokeh serve --show scratch_10.py
# Load libraries
from pymongo import MongoClient
#from datetime import datetime, timedelta
import math
import datetime
from os.path import dirname, join
import pandas as pd
from scipy.signal import savgol_filter
from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, DataRange1d, Select
from bokeh.palettes import Blues4
from bokeh.plotting import figure
from bokeh.models import Range1d
# Select Tree
treeSelected = 'TS015'
savgol_window = 51
savgol_order = 3
savgol_deriv = 0
# Load MongoDB
client = MongoClient('mongodb+srv://read_only:passw0rd@tree-system-1.0x4wa.azure.mongodb.net/sensors?retryWrites=true&w=majority')
db = client.sensors
col = db["sensors"]
# Function to split list into same length segments
def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]
# Functions for loading data and plotting data
def get_dataset(src, name, distribution, savgol_window, savgol_order, savgol_deriv):
    df = src[src.treeID == name].copy()
    del df['treeID']
    df['date'] = pd.to_datetime(df.date)
    # timedelta here instead of pd.DateOffset to avoid pandas bug < 0.18 (Pandas issue #11925)
    df['left'] = df.date - datetime.timedelta(days=0.001)
    df['right'] = df.date + datetime.timedelta(days=0.001)
    df = df.set_index(['date'])
    df.sort_index(inplace=True)
    if distribution == 'Smoothed':
        window, order = savgol_window, savgol_order
        deriv = savgol_deriv
        for key in STATISTICS:
            df[key] = savgol_filter(df[key], window, order, deriv)

    return ColumnDataSource(data=df)
def make_plotX(source, title):
    plot = figure(x_axis_type="datetime", plot_width=550, tools="", toolbar_location=None)
    plot.title.text = title

    plot.quad(top='xMax', bottom='xMin', left='left', right='right',
              color=Blues4[2], source=source, legend_label="roll")
    #plot.quad(top='yMax', bottom='yMin', left='left', right='right',
    #          color=Blues4[1], source=source, legend_label="pitch")
    #plot.quad(top='zMax', bottom='zMin', left='left', right='right',
    #          color=Blues4[0], alpha=0.5, line_color="black", source=source, legend_label="yaw")

    # fixed attributes
    plot.xaxis.axis_label = None
    plot.yaxis.axis_label = "Degrees"
    plot.axis.axis_label_text_font_style = "bold"
    plot.x_range = DataRange1d(range_padding=0.0)
    plot.y_range = DataRange1d(range_padding=3.0)
    plot.grid.grid_line_alpha = 0.3

    return plot
def make_plotY(source, title):
    plot = figure(x_axis_type="datetime", plot_width=550, tools="", toolbar_location=None)
    plot.title.text = title

    #plot.quad(top='xMax', bottom='xMin', left='left', right='right',
    #         color=Blues4[2], source=source, legend_label="roll")
    plot.quad(top='yMax', bottom='yMin', left='left', right='right',
              color=Blues4[1], source=source, legend_label="pitch")
    #plot.quad(top='zMax', bottom='zMin', left='left', right='right',
    #          color=Blues4[0], alpha=0.5, line_color="black", source=source, legend_label="yaw")

    # fixed attributes
    plot.xaxis.axis_label = None
    plot.yaxis.axis_label = "Degrees"
    plot.axis.axis_label_text_font_style = "bold"
    plot.x_range = DataRange1d(range_padding=0.0)
    plot.y_range = DataRange1d(range_padding=3.0)
    plot.grid.grid_line_alpha = 0.3

    return plot
def make_plotZ(source, title):
    plot = figure(x_axis_type="datetime", plot_width=550, tools="", toolbar_location=None)
    plot.title.text = title

    #plot.quad(top='xMax', bottom='xMin', left='left', right='right',
    #         color=Blues4[2], source=source, legend_label="roll")
    #plot.quad(top='yMax', bottom='yMin', left='left', right='right',
    #          color=Blues4[1], source=source, legend_label="pitch")
    plot.quad(top='zMax', bottom='zMin', left='left', right='right',
              color=Blues4[0], alpha=0.5, line_color="black", source=source, legend_label="yaw")

    # fixed attributes
    plot.xaxis.axis_label = None
    plot.yaxis.axis_label = "Degrees"
    plot.axis.axis_label_text_font_style = "bold"
    plot.x_range = DataRange1d(range_padding=0.0)
    plot.y_range = DataRange1d(range_padding=3.0)
    plot.grid.grid_line_alpha = 0.3

    return plot
def update_plot(attrname, old, new):
    new_days_ago = int(period_select.value)
    new_window_size = int(Savitzky_Golay_window_select.value)
    new_order = int(Savitzky_Golay_order_select.value)
    new_deriv = int(Savitzky_Golay_deriv_select.value)
    today = datetime.datetime.now()
    n_days_ago = today - datetime.timedelta(days=new_days_ago)
    timestamp = datetime.datetime.timestamp(n_days_ago)
    # Select time period and Tree by Tree ID
    timestamp2 = int(timestamp) * 1000
    treedt = list()
    for x in db.sensors.find({"time": {'$gte': timestamp2}, "treeId": treeSelected}):
        treedt.append(x)
    treeTime = list()
    treeTimeStamp = list()
    for i in range(0, len(treedt)):
        temp = treedt[i]
        temp2 = int(int(temp['time']) / 1000)
        dt_obj = datetime.datetime.fromtimestamp(temp2)
        treeTimeStamp.append(temp2)
        treeTime.append(dt_obj)
        degreeX = list()
        degreeY = list()
        degreeZ = list()
    for i in range(0, len(treedt)):
        temp = treedt[i]
        ax = temp['x']
        ay = temp['y']
        az = temp['z']
        xAngle = math.atan(ax / (math.sqrt((ay ** 2) + (az ** 2))))
        yAngle = math.atan(ay / (math.sqrt((ax ** 2) + (az ** 2))))
        zAngle = math.atan(math.sqrt((ax ** 2) + (ay ** 2)) / az)
        xAngle = (xAngle * 180) / 3.1415926
        yAngle = (yAngle * 180) / 3.1415926
        zAngle = (zAngle * 180) / 3.1415926
        degreeX.append(xAngle)
        degreeY.append(yAngle)
        degreeZ.append(zAngle)
    # Split into segments
    xs = list(chunks(degreeX, 60))
    ys = list(chunks(degreeY, 60))
    zs = list(chunks(degreeZ, 60))
    treeTime = list(chunks(treeTime, 60))
    xMax = list()
    xMin = list()
    yMax = list()
    yMin = list()
    zMax = list()
    zMin = list()
    treeTime2 = list()
    for i in range(0, len(xs)):
        tempx = xs[i]
        xMax.append(max(tempx))
        xMin.append(min(tempx))
        tempy = ys[i]
        yMax.append(max(tempy))
        yMin.append(min(tempy))
        tempz = zs[i]
        zMax.append(max(tempz))
        zMin.append(min(tempz))
        treeTime2.append(treeTime[i][0])
    # Put into a Pandas Dataframe
    dfObj = pd.DataFrame(columns=['treeID', 'date', 'xMax', 'xMin', 'yMax', 'yMin', 'zMax', 'zMin'])
    for i in range(0, len(treeTime2)):
        dfObj = dfObj.append(
            {'treeID': treeSelected, 'date': treeTime2[i], 'xMax': xMax[i], 'xMin': xMin[i], 'yMax': yMax[i],
            'yMin': yMin[i], 'zMax': zMax[i], 'zMin': yMin[i]}, ignore_index=True)
    plotX.title.text = "Data for " + treeSelected
    src = get_dataset(dfObj, treeSelected, distribution_select.value, new_window_size, new_order, new_deriv)
    source.data.update(src.data)
# Decide time for plotting
N_DAYS_AGO = 1
today = datetime.datetime.now()
n_days_ago = today - datetime.timedelta(days=N_DAYS_AGO)
timestamp = datetime.datetime.timestamp(n_days_ago)
# Select time period and Tree by Tree ID
timestamp2 = int(timestamp)*1000
# Fetch data
treedt = list()
for x in db.sensors.find({"time": {'$gte': timestamp2}, "treeId": treeSelected}):
    treedt.append(x)
# Convert to time from timestamp
treeTime = list()
treeTimeStamp = list()
for i in range(0, len(treedt)):
    temp = treedt[i]
    temp2 = int(int(temp['time'])/1000)
    dt_obj = datetime.datetime.fromtimestamp(temp2)
    treeTimeStamp.append(temp2)
    treeTime.append(dt_obj)
# Calculate angles
degreeX = list()
degreeY = list()
degreeZ = list()
for i in range(0, len(treedt)):
    temp = treedt[i]
    ax = temp['x']
    ay = temp['y']
    az = temp['z']
    xAngle = math.atan(ax / (math.sqrt((ay**2) + (az**2))))
    yAngle = math.atan(ay / (math.sqrt((ax**2) + (az**2))))
    zAngle = math.atan(math.sqrt((ax**2) + (ay**2)) / az)
    xAngle = (xAngle*180)/3.1415926
    yAngle = (yAngle*180)/3.1415926
    zAngle = (zAngle*180)/3.1415926
    degreeX.append(xAngle)
    degreeY.append(yAngle)
    degreeZ.append(zAngle)
# Split into segments
xs = list(chunks(degreeX, 60))
ys = list(chunks(degreeY, 60))
zs = list(chunks(degreeZ, 60))
treeTime = list(chunks(treeTime, 60))
xMax = list()
xMin = list()
yMax = list()
yMin = list()
zMax = list()
zMin = list()
treeTime2 = list()
for i in range(0, len(xs)):
    tempx = xs[i]
    xMax.append(max(tempx))
    xMin.append(min(tempx))
    tempy = ys[i]
    yMax.append(max(tempy))
    yMin.append(min(tempy))
    tempz = zs[i]
    zMax.append(max(tempz))
    zMin.append(min(tempz))
    treeTime2.append(treeTime[i][0])
# Put into a Pandas Dataframe
dfObj = pd.DataFrame(columns=['treeID', 'date', 'xMax', 'xMin', 'yMax', 'yMin', 'zMax', 'zMin'])
for i in range(0, len(treeTime2)):
    dfObj = dfObj.append({'treeID': treeSelected, 'date': treeTime2[i], 'xMax': xMax[i], 'xMin': xMin[i], 'yMax': yMax[i], 'yMin': yMin[i], 'zMax': zMax[i], 'zMin': yMin[i]}, ignore_index=True)
# Load data
STATISTICS = ['xMax', 'xMin', 'yMax', 'yMin', 'zMax', 'zMin']
defaultDays = str(N_DAYS_AGO)
default_savgol_window = str(savgol_window)
default_savgol_order = str(savgol_order)
default_savgol_deriv = str(savgol_deriv)
distribution = 'Discrete'
periods = list()
for i in range(0, 30):
    periods.append(str(i+1))
Savitzky_Golay_window = list()
for i in range(25,76):
    if (i % 2) != 0:
        Savitzky_Golay_window.append(str(i))
Savitzky_Golay_order = list()
for i in range(1,11):
    Savitzky_Golay_order.append(str(i))
Savitzky_Golay_deriv = list()
for i in range(0,4):
    Savitzky_Golay_deriv.append(str(i))
period_select = Select(value=defaultDays, title='Select the Past ... Days', options=periods)
distribution_select = Select(value=distribution, title='Distribution', options=['Discrete', 'Smoothed'])
Savitzky_Golay_window_select = Select(value=default_savgol_window, title='Savitzky Golay Window Size', options=Savitzky_Golay_window)
Savitzky_Golay_order_select = Select(value=default_savgol_order, title='Savitzky Golay Order', options=Savitzky_Golay_order)
Savitzky_Golay_deriv_select = Select(value=default_savgol_deriv, title='Savitzky Golay Differentiating', options=Savitzky_Golay_deriv)
source = get_dataset(dfObj, treeSelected, distribution, savgol_window, savgol_order, savgol_deriv)
plotX = make_plotX(source, "Data for " + treeSelected)
plotY = make_plotY(source, "Data for " + treeSelected)
plotZ = make_plotZ(source, "Data for " + treeSelected)
period_select.on_change('value', update_plot)
distribution_select.on_change('value', update_plot)
Savitzky_Golay_window_select.on_change('value', update_plot)
Savitzky_Golay_order_select.on_change('value', update_plot)
Savitzky_Golay_deriv_select.on_change('value', update_plot)
controls = column(period_select, distribution_select, Savitzky_Golay_window_select, Savitzky_Golay_order_select, Savitzky_Golay_deriv_select)

curdoc().add_root(row(plotX, plotY, plotZ, controls))
curdoc().title = "Sensor Data"