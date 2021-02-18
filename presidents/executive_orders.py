#!/usr/bin/env python3
# -*- coding = utf-8 -*-
# Copyright 2021 Amogh Joshi. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
A standalone implementation containing visualizations of presidents' executive orders.

Everything within this file is mostly self-contained, meaning that it is not reliant on
anything else within the `presidents` module, although it makes use of the `query` module.
"""
import os
import re
import wikipedia as wk

# Webpage parsing functions.
import requests
from bs4 import BeautifulSoup

# For figure development.
import numpy as np
import matplotlib
from matplotlib import style
style.use('fivethirtyeight')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatch
from matplotlib.lines import Line2D

def get_list_of_executive_orders():
   """Returns a list of executive orders by president."""
   # Construct the webpage.
   page = requests.get(wk.page('List of United States federal executive orders', auto_suggest=False).url)
   soup = BeautifulSoup(page.content, 'html.parser')

   # Create the list of orders.
   executive_orders = {}

   # Find all <tr> tags and parse table content.
   main_table = soup.find('table', class_ = re.compile('wikitable'))
   for row in main_table.find_all('tr'):
      # Create a tracker list (to get a president/executive orders combo).
      _tracker_list = []

      # Parse over each row.
      for indx, item in enumerate(row.find_all('td')):
         # Notable instances which need to be skipped.
         if item.text.strip() in ['Sources:']:
            continue

         # Get the president's name.
         if indx == 1:
            _tracker_list.append(item.text.strip())

         # Get the number of executive orders.
         if indx == 3:
            _tracker_list.append(int(re.sub(',', '', item.text.strip())))

         # Get the average number of executive orders per year and break.
         if indx == 5:
            _tracker_list.append(float(re.sub(',', '', item.text.strip())))
            break

      # Add the tracked list to the main dictionary and clear it.
      if len(_tracker_list) == 3:
         executive_orders[_tracker_list[0]] = [_tracker_list[1], _tracker_list[1] / _tracker_list[2]]
      del _tracker_list

   # Return the list of parties.
   return executive_orders

# Construct the dictionary mapping a president to an executive order.
president_executive_orders = get_list_of_executive_orders()

def plot_executive_orders_per_president(save_figure = True):
   """Plots a line graph containing the executive orders per president."""
   # Construct the x-axis, y-axis, and x-axis labels.
   x_axis = list(range(1, len(president_executive_orders.keys()) + 1))
   x_axis_labels = list(president_executive_orders.keys())
   y_axis_1 = [item[0] for item in president_executive_orders.values()]
   y_axis_2 = [item[1] for item in president_executive_orders.values()]

   # Insert a 0 value in the x and y axis in order to maintain continuity in the graph.
   x_axis.insert(0, 0)
   x_axis_labels.insert(0, '')
   y_axis_1.insert(0, 0)
   y_axis_2.insert(0, 0)

   # Create the first plot (of the total number of orders).
   fig, ax1 = plt.subplots(figsize = (20, 5))
   plt.title("$\\bf{Executive\\,\\:Orders\\,\\:By\\,\\:President\\,\\:}$")

   # Plot the data.
   ax1.plot(x_axis, y_axis_1, color = 'tab:cyan')

   # Create the second plot (of the average number of orders per year).
   ax2 = ax1.twinx()

   # Plot the data.
   ax2.plot(x_axis, y_axis_2, color = 'tab:green')

   # Add the important events backgrounds/legend.
   plt.axvspan(15.5, 19.25, facecolor = 'tomato', alpha = 0.5)
   plt.axvspan(27.5, 28.5, facecolor = 'lightcoral', alpha = 0.5)
   plt.axvspan(31.65, 33.15, facecolor = 'brown', alpha = 0.5)
   legend_war_items = [
      mpatch.Patch(color = 'tomato', label = 'Civil War/Reconstruction'),
      mpatch.Patch(color = 'lightcoral', label = 'World War I'),
      mpatch.Patch(color = 'brown', label = 'World War II'),
   ]
   legend_date_items = [
      Line2D([0], [0], color = 'tab:cyan', lw = 4),
      Line2D([0], [0], color = 'tab:green', lw = 4)
   ]

   # Set the y-axis.
   ax1.set_ylabel(r'Total Number of Executive Orders ', fontsize = 10,)

   # Set the x-axis.
   plt.xlim(0.5, len(president_executive_orders.keys()))
   for ax in (ax1, ax2):
      plt.sca(ax)
      plt.xticks(x_axis, x_axis_labels, fontsize = 10, rotation = 45, ha = 'right')

   # Set the y-axis.
   ax2.set_ylabel(r'Average Number of Executive Orders Per Year ',
                  fontsize = 10, rotation = 270, labelpad = 25)
   ax2.set_ylim([-25, 700])

   # Set the thickness of the axis.
   for spine in ['left', 'bottom', 'right', 'top']:
      ax1.spines[spine].set_linewidth(2)
      ax1.spines[spine].set_color('k')
      ax1.spines[spine].set_zorder(10000)
      ax2.spines[spine].set_linewidth(2)
      ax2.spines[spine].set_color('k')
      ax2.spines[spine].set_zorder(10000)

   # Set the final configuration of the plot.
   fig.tight_layout()
   savefig = plt.gcf()
   legend_1 = plt.legend(handles = legend_war_items, prop = {'size': 15}, loc = 1)
   legend_2 = plt.legend(legend_date_items, ['Total # of E.O.', 'Average # of E.O. Per Year'], loc = 2)
   ax2.add_artist(legend_1)

   # Copyright.
   ax1.text(1, 500, '@amogh7joshi', fontsize = 20, alpha = 0.7, color = 'slategrey')

   # Display the plot.
   plt.show()

   # Save the figure.
   if save_figure:
      savefig.savefig('images/us-president-executive-orders.png')

plot_executive_orders_per_president()

