import os
import numpy as np
import matplotlib.pyplot as plt
import shutil

#this script downloads all of the airfoil data from airfoiltools.com and puts the csv files into a directory
#airfoiltools.com is a website that has a large amount of airfoil data
#the data is in the form of csv files



#list all of the airfoil options to piece together the urls, then loop through them
reynoldsNumbers = ['50000', '100000', '200000', '500000', '1000000']
nCrit = ['n5', 'n9']

airfoilNames = ['n0012']

baseURL = 'airfoiltools.com/polar/csv?polar=xf-'

for airfoilName in airfoilNames:
