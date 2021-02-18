#!/usr/bin/env python3
# -*- coding = utf-8 -*-
import os
import copy
import re

import cv2

# Figure development modules.
import numpy as np
from matplotlib import style
style.use('seaborn-deep')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

from nations.info import nation_flag_info
from nations.info import founding_dates

# Helper methods to assist in actual figure development.

def get_country_flag(country):
   """Returns the corresponding flag of a provided country."""
   with nation_flag_info as flag_path_info:
      # Validate the provided nation string.
      if country.title().replace('_', ' ') not in flag_path_info.keys() and \
         country.title().replace(' ', '_') not in flag_path_info.keys() and \
         country not in flag_path_info.keys():
         raise ValueError(f"Received invalid nation {country}, try another one.")

      # Read the flag image path and return the flag image.
      return cv2.cvtColor(cv2.imread(flag_path_info[country.replace(' ', '_')]), cv2.COLOR_BGR2RGB)

# Actual figure development methods.

def plot_flag_diagram():
   """Creates a plot showing the flags of each nation of the world."""
   # Create the figure.
   fig, ax = plt.subplots(8, 23, figsize = (20, 20))

   # Plot the actual images onto the figure.
   with nation_flag_info as info:
      # Generate a list of nations.
      countries = list(info.keys())
      
      # Display each individual image.
      tracker = 0
      for i in range(8):
         for j in range(23):
            # Plot the image.
            ax[i][j].imshow(get_country_flag(countries[tracker]))
            ax[i][j].axis('off')

            # Add the image title.
            if len(countries[tracker]) < 12:
               ax[i][j].set_title(countries[tracker], fontsize = 10)
            elif 12 < len(countries[tracker]) < 20:
               ax[i][j].set_title(countries[tracker], fontsize = 8)
            else:
               ax[i][j].set_title(countries[tracker], fontsize = 6)

            # Increment the tracker.
            tracker += 1

   # Display the plot.
   fig.subplots_adjust(bottom = 0, top = 0.1, wspace = 0.1, hspace = 0.1)
   fig.tight_layout()
   plt.show()


