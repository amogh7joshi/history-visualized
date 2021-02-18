#!/usr/bin/env python3
# -*- coding = utf-8 -*-
import os
import re

import datetime
import wikipedia as wk

# For figure development.
import numpy as np
import matplotlib
from matplotlib import style
style.use('seaborn-darkgrid')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatch
from matplotlib.lines import Line2D

# Webpage parsing functions.
import requests
from bs4 import BeautifulSoup

def get_gwp_data():
   """Gets gross world product (GWP) data and returns a list over time."""
   # Construct webpage.
   page = requests.get(wk.page('Gross World Product', auto_suggest = False).url)
   soup = BeautifulSoup(page.content, 'html.parser')

   # Construct return dict of GWP data.
   gwp_data = {}

   # Parse main table content.
   # We need the second table.
   table = soup.find_all('table', class_= re.compile('wikitable'))[1]
   for row in table.find_all('tr'):
      # Create a candidate list.
      _candidate_list = []

      # Parse over each row.
      for indx, item in enumerate(row.find_all('td')):
         # Notable instances which need to be skipped.
         if item.text.strip() in ['Sources:']:
            continue

         # Skip any data past 9999 BC, since the 'world's economy'
         # back then wasn't really existent, and is therefore unnecessary
         # since all data is basically extreme predictions.
         if len(re.findall('\\d{2,3},\\d{3}\\sBC', item.text.strip())) > 0:
            break

         # Parse the item for links, parenthesis, commas, and spaces.
         parsed_item = re.sub('\\[(.*?)\\]', '', item.text.strip())
         parsed_item = re.sub('\\((.*?)\\)', '', parsed_item)
         parsed_item = re.sub(',', '', parsed_item)
         parsed_item = re.sub(' ', '', parsed_item)

         # Reintroduce the space between the number and "AD"/"BC", and add dots.
         parsed_item = re.sub('(\\d{1,4})(AD|BC)', '\\1 \\2', parsed_item)
         parsed_item = re.sub('([AB])([DC])', '\\1.\\2.', parsed_item)

         # Get the year.
         if indx == 0:
            # Add the month and day (Jan 1) to ease SpiceyPy in parsing.
            _candidate_list.append(parsed_item)

         # Get the total GWP.
         if indx == 1:
            _candidate_list.append(float(parsed_item))

      # Add the items in the candidate list to the GWP data dict.
      if len(_candidate_list) == 2:
         gwp_data[_candidate_list[0]] = _candidate_list[1]

   # Reverse the dictionary.
   _return_dict = {}
   for key, value in zip(reversed(list(gwp_data.keys())), reversed(list(gwp_data.values()))):
      _return_dict[key] = value

   # Return the data.
   return _return_dict

# Construct the world's GWP data.
world_gwp_data = get_gwp_data()

def convert_years_to_scale(data):
   """Converts the actual years in B.C./A.D. to a scale usable in a plot."""
   # Get the years.
   return {key: value for key, value in zip(data.keys(), range(len(data.keys())))}

def plot_world_gwp_trend(savefig = True):
   """Plots the world GWP over a period of ~10,000 years."""
   # Construct the figure.
   fig, ax = plt.subplots(figsize = (20, 5))

   # Construct mappings between a plottable x- and y- axis.
   x_axis_data = np.array(list(convert_years_to_scale(world_gwp_data).values()))
   y_axis_data = np.array(list(world_gwp_data.values()))

   # Plot the x- and y- axis data.
   ax.plot(x_axis_data, y_axis_data)

   # Change the x-axis labels.
   plt.xticks(x_axis_data, list(convert_years_to_scale(world_gwp_data).keys()),
              fontsize = 10,  rotation = 45)

   # Final configurations of the plot.
   plt.title("$\\bf{World\\,\\:GDP\\,\\:Over\\,\\:10,000\\,\\:Years}$")

   # Display the plot.
   savefig = plt.gcf()
   plt.show()

   # Save the figure.
   if savefig:
      savefig.savefig('images/world-gwp-over-time.png')


