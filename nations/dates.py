#!/usr/bin/env python3
# -*- coding = utf-8 -*-
import os
import re
import json
import shutil

import datetime
import dateutil.relativedelta
import wikipedia as wk

import requests

# For image parsing.
import cv2

# For figure development.
import numpy as np
from matplotlib import style
style.use('seaborn-deep')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from nations.info import founding_dates

def convert_dates_to_date_objects(date_dict):
   """Converts founding dates into datetime objects."""
   # Construct returnable dictionary.
   return_dict = {}

   # Iterate over dictionary.
   for key, value in date_dict.items():
      # Convert string date into datetime object.
      date = datetime.datetime.strptime(value, '%Y')

      # Append date object to new dictionary.
      return_dict[key] = date

   # Return dictionary.
   return return_dict

# Construct object holding date information.
founding_dates = convert_dates_to_date_objects(founding_dates)

def create_nation_founding_timeline(dates, save_figure = True):
   """Creates a timeline figure showing the founding of each country."""
   # Create levels (e.g. the length of the lines showing dates).
   levels = np.tile([-9, 9, -7, 7, -5, 5, -3, 3, -1, 1],
                    int(np.ceil(len(dates.keys())/10)))[:len(dates.keys())]

   # Create list of names and dates.
   names = list(dates.keys())
   nation_dates = list(dates.values())

   # Extend the graph to 20 years before the earliest nation and either
   # 20 years past the latest nation or to today, if it is that recent.
   # Get the date 20 years before the founding of the earliest nation.
   earliest_date = min(dates.values()) + dateutil.relativedelta.relativedelta(years = -20)
   # Get the date 20 years after the founding of the latest nation or today's date.
   if datetime.datetime.today().year - max(dates.values()).year < 20:
      latest_date = datetime.datetime.strptime(str(datetime.datetime.today().year), '%Y')
   else:
      latest_date = max(dates.values()) + dateutil.relativedelta.relativedelta(years = +20)

   # Add today's date and the year 1720 to dates.
   nation_dates.append(latest_date); nation_dates.insert(0, earliest_date)
   # Add placeholder values to names.
   names.append(0); names.insert(0, 0)
   # Add placeholders to levels.
   levels = [item for item in levels]
   levels.append(0); levels.insert(0, 0)
   levels = np.array(levels, dtype = int)

   # Setup timeline figure.
   fig, ax = plt.subplots(figsize = (50, 6))
   plt.title(r"$\bf{Date\,\:of\,\:Establishment\,\:of\,\:The\,\:Current\,"
             r"\:Government\,\:of\,\:the\,\:World's\,\:Nations}}$")

   # Plot the vertical lines.
   ax.vlines(nation_dates, 0, levels, color = 'tab:cyan')
   ax.plot(nation_dates, np.zeros_like(nation_dates), "-o", color = "k", markerfacecolor = "w")
   
   # Annotate the lines with the nation names.
   for number, (date, level, name) in enumerate(zip(nation_dates, levels, names)):
      ax.annotate(name, xy = (date, level),
                  xytext = (-3, np.sign(level) * 3),
                  textcoords = 'offset points',
                  horizontalalignment = 'center',
                  verticalalignment = 'bottom' if level > 0 else 'top',
                  backgroundcolor = 'w')

   # Format the figure.
   ax.get_xaxis().set_major_locator(mdates.YearLocator(10))
   ax.get_xaxis().set_major_formatter(mdates.DateFormatter(r"$\bf{%Y}$"))
   plt.setp(ax.get_xticklabels(), rotation = 0, ha = "right")

   # Remove the y-axis and graph spines.
   ax.get_yaxis().set_visible(False)
   for spine in ["top", "left", "right"]:
      ax.spines[spine].set_visible(False)

   # Display plot.
   ax.margins(y = 0.1)
   savefig = plt.gcf()
   plt.show()

   # Save figure.
   if save_figure:
      savefig.savefig('images/nation-founding-timeline.png')

