import os
import numpy as np
import matplotlib.pyplot as plt
import shutil
import re
import requests
import csv
import pandas as pd
from csv import writer

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
    
    #print(airfoilNamesNoDuplicates)
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
        if airfoil.endswith('.dat'):
            airfoilPath = airfoilPlotDirectory + airfoil
            airfoilPlots.append(airfoilPath)
        
    print(airfoilPlots)    
    
    #read in all the airfoilPlots .dat files and find the max number of columns
    maxNumberOfColumns = 0
    longestAirfoilDat = ''
    airfoilDatLengthArray = []
    for airfoilPlot in airfoilPlots:
        with open(airfoilPlot, 'r') as f:
            lines = f.readlines()
            f.close()
            numLines = len(lines)
        airfoilDatLengthArray.append(numLines)
        if numLines > maxNumberOfColumns:
            maxNumberOfColumns = numLines
            longestAirfoilDat = airfoilPlot
            
    print('max number of columns: ' + str(maxNumberOfColumns))
    print('longest airfoil dat: ' + str(longestAirfoilDat))

    #plt.hist(airfoilDatLengthArray, bins=maxNumberOfColumns)
    #plt.show()

    #The airfoilPlots .dat files are not all the same length, and have inconsistent step sizes. 
    #To include this date into the input layer of the neural network, we need to make sure that the data is the same length and has the same step size across all airfoils.
    #A polynomial fit will be applied to each airfoilPlot .dat file data
    #To do this, first the x and y data from the .dat file will be read in
    #Then a polynomial fit will be found from the x and y data
    #Then, the polynomial fit will be used to calculate approximate y values from the x values
    #Across all airfoils, consistent x values will be used 

    #for each airfoil, find the x and y data
    upperSurfaceRSquaredArray = []
    lowerSurfaceRSquaredArray = []

    #min R squared value
    minUpperSurfaceRSquared = 1
    minLowerSurfaceRSquared = 1

    #clear contents of combinedAirfoilData.csv file before writing new data
    with open('data/combinedAirfoilData.csv', 'w') as f:
        f.truncate()

    for airfoilPlot in airfoilPlots:

        #if airfoilPlot == 'data/airfoilPlots/cap21c.dat':
            #continue
        print(airfoilPlot)
        with open(airfoilPlot, 'r') as f:
            lines = f.readlines()
            f.close()
        #restructure lines to be one list
        xData = []
        xDataMin = 0
        yData = []
        
        for line in lines:
            #skip the first line
            if lines.index(line) == 0:
                continue
            #split the line into x and y data
            line = line.split()
            #print('X: ' + line[0])
            #print('Y: ' + line[1])
            xData.append(line[0])
            yData.append(line[1])

        
        #the xData and yData contain the values of both the upper and lower surfaces of the airfoil
        #to do an accurate polynomial fit of these surfaces, we need to separate the data into two lists
        #one for the upper surface and one for the lower surface
        #xData and yData start with the upper surface. xData should always start with 1 (verify this) and decrease to about 0.
        #once xData starts increasing, the lower surface is reached
        #compare the current x value in xData to the previous x value in xData, and if the current xData is greater than the previous xData, the lower surface is reached
        upperSurfaceXData = []
        upperSurfaceYData = []
        lowerSurfaceXData = []
        lowerSurfaceYData = []
        #find the polynomial fit
        xData = np.array(xData)
        yData = np.array(yData)
        xData = xData.astype(np.float)
        yData = yData.astype(np.float)
        #loop through xData to find index of the last data point on the upper surface
        for i in range(len(xData)):
            #skip the first data point
            if i == 0:
                continue
            if xData[i] > xData[i-1]:
                upperSurfaceXData = xData[0:i]
                upperSurfaceYData = yData[0:i]
                lowerSurfaceXData = xData[i+1:]
                lowerSurfaceYData = yData[i+1:]
                break



        #fit a polynomial to the data
        upperSurfacePolyfit = np.polyfit(upperSurfaceXData, upperSurfaceYData, 30)
        lowerSurfacePolyfit = np.polyfit(lowerSurfaceXData, lowerSurfaceYData, 30)
        

        for reynoldsNumber in reynoldsNumbers:
            #write lines and reynolds number to the combinedAirfoilData file
            with open('data/combinedAirfoilData.csv', 'a') as f:
                #f.write(lines + ',' + reynoldsNumber + '\n')
                combinedDataString = str(upperSurfacePolyfit) + ' ' + str(lowerSurfacePolyfit) + ' ' + str(reynoldsNumber)
                #add commas between each value so it can be read in as a csv
                combinedDataString = combinedDataString.replace('\n', '')
                combinedDataString = combinedDataString.replace('[', '')
                combinedDataString = combinedDataString.replace(']', '')
                combinedDataString = combinedDataString.replace('  ', ' ')
                combinedDataString = combinedDataString.strip()
                combinedDataString = combinedDataString.replace(' ', ', ')
                f.write(combinedDataString + '\n')
                f.close() 



        #find the R square value
        upperSurfaceRSquared = np.corrcoef(upperSurfaceYData, np.polyval(upperSurfacePolyfit, upperSurfaceXData))[0,1]
        if upperSurfaceRSquared < minUpperSurfaceRSquared:
            minUpperSurfaceRSquared = upperSurfaceRSquared
            airfoilWithLowestUpperSurfaceRSquared = airfoilPlot
        upperSurfaceRSquaredArray.append(upperSurfaceRSquared)
        lowerSurfaceRSquared = np.corrcoef(lowerSurfaceYData, np.polyval(lowerSurfacePolyfit, lowerSurfaceXData))[0,1]
        if lowerSurfaceRSquared < minLowerSurfaceRSquared:
            minLowerSurfaceRSquared = lowerSurfaceRSquared
            airfoilWithLowestLowerSurfaceRSquared = airfoilPlot
        lowerSurfaceRSquaredArray.append(lowerSurfaceRSquared)
        #print('rSquare: ' + str(rSquare))
    print('upperSurfaceRSquaredArray Average: ' + str(np.average(upperSurfaceRSquaredArray)))
    print('lowerSurfaceRSquaredArray Average: ' + str(np.average(lowerSurfaceRSquaredArray)))
    
    print('upperSurfaceRSquaredArray Min: ' + str(np.amin(upperSurfaceRSquaredArray)))
    print('lowerSurfaceRSquaredArray Min: ' + str(np.amin(lowerSurfaceRSquaredArray)))

    print('airfoilWithLowestUpperSurfaceRSquared: ' + str(airfoilWithLowestUpperSurfaceRSquared))
    print('airfoilWithLowestLowerSurfaceRSquared: ' + str(airfoilWithLowestLowerSurfaceRSquared))

    print('Upper Surface Polyfit: ' + str(upperSurfacePolyfit))
    print('Lower Surface Polyfit: ' + str(lowerSurfacePolyfit))
    plt.hist(upperSurfaceRSquaredArray, bins = 100)
    plt.show()

    plt.hist(lowerSurfaceRSquaredArray, bins = 100)
    plt.show()


""" # loop through airfoilPlots, read the .dat file, and add it to the combinedAirfoilData.csv in a new column. Repeat this for each reynolds number
    for airfoilPlot in airfoilPlots:
        restructuredLines = ""
        with open(airfoilPlot, 'r') as f:
            lines = f.readlines()
            #restructure lines to be one list  
            for line in lines:
                restructuredLines = restructuredLines + ", " + line.strip()

            f.close()
        for reynoldsNumber in reynoldsNumbers:
            #write lines and reynolds number to the combinedAirfoilData file
            with open('data/combinedAirfoilData.csv', 'w') as f:
                #f.write(lines + ',' + reynoldsNumber + '\n')
                f.write(restructuredLines)
                f.close() 
"""

    
            






    

