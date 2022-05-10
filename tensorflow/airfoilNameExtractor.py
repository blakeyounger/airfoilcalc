import os
import numpy as np
import matplotlib.pyplot as plt
import shutil
import re
import requests
import csv
import pandas as pd

stringsToDelete = ['<url>', '</url>', '<loc>', '</loc>'
    'http://airfoiltools.com/', '']

with open('data/rawXMLdata.txt', 'r') as f:
    output = ""
    lines = f.readlines()
    f.close()
    for line in lines:
        for string in stringsToDelete:
            line = line.replace(string, '')
        if '<loc>' in line:
            line = ''
        if '<lastmod>' in line:
            line = ''
        if 'priority' in line:
            line = ''
        #remove the line if it is empty
        if not line.isspace():
            output += line
    #replace \n with comma
    output = output.replace('\n', ', ').replace('http://airfoiltools.com/', '').replace('plotter/index?airfoil=', '').replace('</loc>', '').replace('airfoil/details?airfoil=', '').replace('search/list?', '')
    #print(output)
    splitText = output.split(', ')
    #remove the really long strings
    airfoilNames = []
    for string in splitText:
        if len(string) < 20 and len(string) > 2 and 'page' not in string and 'compare' not in string and 'index' not in string and 'generated' not in string:
            airfoilNames.append(string)
    airfoilNamesNoDuplicates = list(set(airfoilNames))
    
    print(airfoilNamesNoDuplicates)
    csvFileBaseURL = 'http://airfoiltools.com/polar/csv?polar=xf-'

    reynoldsNumbers = ['50000', '100000', '200000', '500000', '1000000']
    nCrit = ['n5', 'n9']

    listOfURLs = []

    for airfoilName in airfoilNamesNoDuplicates:
        #join the base url with the airfoil name
        url = csvFileBaseURL + airfoilName
        #loop through each reynolds number
        for reynoldsNumber in reynoldsNumbers:  
            #join the url with the reynolds number
            reynoldsURL = url + '-' + reynoldsNumber
            listOfURLs.append(reynoldsURL)
    
    

    print('number of airfoils: ' + str(len(airfoilNamesNoDuplicates)))
    print('number of URLS: ' + str(len(listOfURLs)))

    #make a list of all of the airfoil .dat file names
    airfoilPlots = []
    airfoilPlotDirectory = 'data/airfoilPlots/'
    for airfoil in os.listdir(airfoilPlotDirectory):
        #fill this in later 

    

