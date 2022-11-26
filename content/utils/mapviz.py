import pandas as pd
import numpy
import random
import IPython
from IPython.display import display, clear_output, Javascript
from ipywidgets import HTML, Output, HBox, Layout
from ipyleaflet import Map, Marker, Popup, CircleMarker
import matplotlib.pyplot as plt
import ipywidgets as widgets
import gender_guesser.detector

from .nestedlookup import *
from .prepare_data import getJSON, avoidTupleInList, getYears, getHumboldtYears
from .widgets import createDropdown, createButton, createCheckBox

data = getJSON('data/bern_withgeo.json')
out = Output()


def allOnAMap(data):
    cities = {}
    marker = None
    coordinates = []
    m= Map(
            zoom=1.5,
            layout=Layout(width='80%', height='500px'),
            close_popup_on_click=False
            )
    
    for i in data:
            try :
                if i["pubplace"]["address"] not in cities:
                    city = i["pubplace"]["address"]
                    cities[city] = {}
                    cities[city]["message"] = "<b>"+ i["year"] + " </b> " + i["title"] + "<br><i>"+"</i><a href=\""+ i["link"] + "\" target=\"_blank\">online</a> <hr>"
                    cities[city]["coordinates"] = [i['pubplace']['coordinates'][1], i['pubplace']['coordinates'][0]] 
                elif i["pubplace"]["address"] in cities:
                    city = i["pubplace"]["address"]
                    cities[city]["message"] = cities[city]["message"] + "<b>"+ i["year"] + " </b> " + i["title"] + "<br><i>"+"</i><a href=\""+ i["link"] + "\" target=\"_blank\">online</a> <hr>"
            except : pass
        # Coordinates to create a dynamic map boundaries
    try:
        for i in cities.keys():
            if type(cities[i]["coordinates"][0]) == float and type(cities[i]["coordinates"][1]) == float:
                coordinates.append([float(cities[i]["coordinates"][0]), float(cities[i]["coordinates"][1])])
            elif type(cities[i]["coordinates"][0]) == str and type(cities[i]["coordinates"][1]) == str:
                coordinates.append([float(cities[i]["coordinates"][0]), float(cities[i]["coordinates"][1])])
    
        coordinates = numpy.array(coordinates)
        data_frame = pd.DataFrame(coordinates, columns=['Lat', 'Long'])
        sw = data_frame[['Lat', 'Long']].min().values.tolist()
        ne = data_frame[['Lat', 'Long']].max().values.tolist()
        m.fit_bounds([sw, ne])
    except: pass


    # Mapmarker and popup message
    for i in cities.keys():
            try :
                # Create the message of the popup
                message = HTML()
                if cities[i]["message"].count("<hr>") <5 :
                    message.value = cities[i]["message"]
                else : 
                    message.value = str(cities[i]["message"].count("<hr>")) + " publications. There are too many results to show them all here."
                message.description = i.upper()

                # Create the marker
                marker = CircleMarker(location=(cities[i]["coordinates"][0], cities[i]["coordinates"][1]))
                radius = cities[i]["message"].count("<hr>")+3
                if radius > 10:
                    radius = 12
                marker.radius = radius
                marker.fill_opacity = 0.8
                marker.fill_color = '#3E81B8'
                marker.stroke = False

                # Add marker on the map
                m.add_layer(marker)
                marker.popup = message
            except: pass
    display(m)


def map_by_date():
    
    def on_value_change(change):
        print(change['new'])
        output_bydate.clear_output(wait=True)
        #display(Javascript('IPython.notebook.execute_cell()'))
        results = []
        
        with output_bydate:
            for i in data:
                try:
                    if i['year']:
                        if change['new'] in i["year"]:
                            results.append(i)
                except: pass
            allOnAMap(results)

    dropdown = createDropdown('', getYears(avoidTupleInList(nested_lookup('year', data))))
    output_bydate = widgets.Output()
    display(dropdown, output_bydate)
    dropdown.observe(on_value_change, names='value')


def map_by_languages():
    
    def on_value_change(change):
        print(change['new'])
        output_bydate.clear_output(wait=True)
        results = []
        
        with output_bydate:
            for i in data:
                try:
                    if i['language'] and change['new'] in i["language"]:
                            results.append(i)
                except: pass
            allOnAMap(results)

    dropdown = createDropdown('', avoidTupleInList(nested_lookup('language', data)))
    output_bydate = widgets.Output()
    display(dropdown, output_bydate)
    dropdown.observe(on_value_change, names='value')


def map_slider():

    slider = widgets.IntRangeSlider(
        value=[1789, 1789],
        min=min(nested_lookup('year', data)),
        max=max(nested_lookup('year', data)),
        step=1,
        description='Years:',
        disabled=False,
        continuous_update=False,
        orientation='horizontal',
        readout=True,
        readout_format='d')
    
    outputslider = widgets.Output()
    display(slider, outputslider)

    def on_value_change(change):
        with outputslider:
            outputslider.clear_output(wait=True)
            results = []
            
            for i in data:
                try:
                    if i['year']:
                        if str(change['new'][0]) <= i['year'] >= str(change['new'][0]) :
                            results.append(i)
                except: pass
            allOnAMap(results)
            
    slider.observe(on_value_change, names='value')
