#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Load and plot the discharge, precipitation, and water level data

Parameters
----------
fig_title : str
        Str containing the name of the study site
old_SA : int
        Int containing surface area of the lake in previous years
old_elevation : int
        Int containing elevation of the lake in previous years
current_SA :
       Int containing current surface area of lake 
    


@author = Kaylee Molan
@date = 2023-03-27
@license = MIT -- https://opensource.org/licenses/MIT
"""

import os
import pandas as pd
from datetime import datetime, timedelta
from scipy import stats
import matplotlib.pyplot as plt
import numpy as np

#%% Specify parameters 
# Primary and secondary precipitation data (with extension)
infile_names = 'GSL-precip.csv', 'GSL-waterlevel.csv', 'WeberRiver-Q.csv', 'JordanRiver-Q.csv', 'BearRiver-Q.csv'

# Text for figure title
fig_title = "Great Salt Lake, Utah"

old_SA= 2300
old_elevation= 4211.85
current_SA= 950

#%% Load and examine data

#Precipitation data
datap=pd.read_csv(infile_names[0],parse_dates=['Date'], 
                 index_col=['Date'], skiprows=4)
datap.index=pd.to_datetime(datap.index, format='%Y12')
datap.drop(columns = {"Anomaly"},inplace = True)
datap=datap.rename(columns={"Value":"Precipitation (in/year)"})

#Water level data
dataw=pd.read_csv(infile_names[1], comment="#", delimiter="\t", header=1,
                  parse_dates=['4s'],index_col=['4s'])
dataw.drop(columns = {"15s", "5s.1", "5s", "3n"},inplace = True)
dataw=dataw.rename(columns={"12n":"Water Level (feet)"})
dataw = dataw.rename_axis('Date')

#Discharge data
#Weber River
dataqw=pd.read_csv(infile_names[2], comment="#", delimiter="\t", header=1,
                  parse_dates=['4s'],index_col=['4s'])
dataqw.drop(columns = {"15s", "5s.1", "5s", "3n"},inplace = True)
dataqw=dataqw.rename(columns={"12n":"Weber Discharge (cfs)"})
dataqw = dataqw.rename_axis('Date')

#Jordan River
dataqj=pd.read_csv(infile_names[3], comment="#", delimiter="\t", header=1,
                  parse_dates=['4s'],index_col=['4s'])
dataqj.drop(columns = {"15s", "5s.1", "5s", "3n"},inplace = True)
dataqj=dataqj.rename(columns={"12n":"Jordan Discharge (cfs)"})
dataqj = dataqj.rename_axis('Date')

#Bear River
dataqb=pd.read_csv(infile_names[4], comment="#", delimiter="\t", header=1,
                  parse_dates=['4s'],index_col=['4s'])
dataqb.drop(columns = {"15s", "5s.1", "5s", "3n"},inplace = True)
dataqb=dataqb.rename(columns={"12n":"Bear Discharge (cfs)"})
dataqb = dataqb.rename_axis('Date')

#%% Merge all data frames into one singular data frame

#Merged based on index columns
merged_df = pd.merge(dataqw,dataqb,left_index=True, right_index=True)
merged_df = pd.merge(merged_df, dataqj, left_index=True, right_index=True)
merged_df = pd.merge(merged_df, dataw, left_index=True, right_index=True)
merged_df = pd.merge(merged_df, datap, left_index=True, right_index=True)
data= merged_df


#%%Figure 1

#Plot raw data w/ 3 subpanels (precipitation, water level, discharge) to visualize relationship
#Create plot to display data
fig, (ax1,ax2,ax3)= plt.subplots(3,1,figsize=(10,16), sharex=True)

#Plot precipitation
ax1.plot(data['Precipitation (in/year)'],'r-', label='Annual Precipitation')
ax1.set_ylabel('Precipitation (in/year)')
ax1.set_title(fig_title)

#Plot water level data
ax2.plot(data['Water Level (feet)'], 'b-', label= 'Water Level')
ax2.set_ylabel('Water Level (feet)')
ax2.set_title(fig_title)

#Plot precipitation over entire period of study
ax3.plot(data['Weber Discharge (cfs)'], 'y-', label= 'Weber River')
ax3.plot(data['Jordan Discharge (cfs)'], 'g-', label= 'Jordan River')
ax3.plot(data['Bear Discharge (cfs)'], 'c-', label= 'Bear River')
ax3.legend()
ax3.set_ylabel('Discharge (cfs)')
ax3.set_title(fig_title)

#%% Additional plotting
#Plot precipitation over the entire available study period to see if drought is a driving variable (Figure 2)
fig, ax1= plt.subplots()

ax1.plot(datap['Precipitation (in/year)'],'r-', label='Annual Precipitation')
ax1.set_ylabel('Precipitation (in/year)')
ax1.set_title(fig_title)

#Plot water level over entire available study period (only shows 1990 onward) (Figure 3)
fig, ax1= plt.subplots()

ax1.plot(dataw['Water Level (feet)'],'b-', label='Annual Water Level')
ax1.set_ylabel('Water Level (feet)')
ax1.set_title(fig_title)
#Create line of best fit
x = np.arange(len(dataw['Water Level (feet)']))
coef = np.polyfit(x, dataw['Water Level (feet)'], 1)
line = coef[0] * x + coef[1]
#Plot the line of best fit
ax1.plot(dataw.index, line, 'r-', label='Line of Best Fit')
eqn = f'y = {coef[0]:.4f}x + {coef[1]:.4f}'
ax1.text(0.02, 0.95, eqn, transform=ax1.transAxes, fontsize=12, verticalalignment='top')
#Add the legend and show the plot
ax1.legend()
plt.show()

#Create a figure with two subplots for the histogram and box plot for precipitation (Figure 4)
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 8))

#Plot the box plot
ax1.boxplot(datap['Precipitation (in/year)'])
ax1.set_ylabel('Precipitation (inches/year)')
ax1.set_title('Variability of Precipitation')
#Plot the histogram
ax2.hist(datap['Precipitation (in/year)'], bins=10)
ax2.set_xlabel('Precipitation (inches/year)')
ax2.set_ylabel('Frequency')
#Show plots
plt.show()

#%% Find evaporation over the last 20 years assuming change in storage is negligible 
oldcs= 0
evap= ((datap['Precipitation (in/year)'].loc['1966-01-01':'1986-01-01'].mean()/12 +(dataqb['Bear Discharge (cfs)'].loc['1966-01-01':'1986-01-01'].mean()+ dataqw['Weber Discharge (cfs)'].loc['1966-01-01':'1986-01-01'].mean() + dataqj['Jordan Discharge (cfs)'].loc['1966-01-01':'1986-01-01'].mean())/(old_SA*2.788e7))-oldcs)

#Mass balance of lake currently based from 1990 to 2022
newcs= ((datap['Precipitation (in/year)'].loc['1990-01-01':'2022-01-01'].mean()/12) +(dataqb['Bear Discharge (cfs)'].loc['1990-01-01':'2022-01-01'].mean()+ dataqw['Weber Discharge (cfs)'].loc['1990-01-01':'2022-01-01'].mean() + dataqj['Jordan Discharge (cfs)'].loc['1990-01-01':'2022-01-01'].mean())/(current_SA*2.788e7))-evap

#%% Lake dry up date
# Extrapolate data to estimate the theoretical date the lake will dry up
days_to_dry = data['Water Level (feet)'].iloc[-1]  / -newcs
dry_date = data.index[-1] + timedelta(days=days_to_dry)

# Print date to screen
print(f"The theoretical dry-up date of the Great Salt Lake is {dry_date}")