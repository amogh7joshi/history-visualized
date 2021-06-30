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
A standalone implementation demonstrating the growth of the world's population
currently and its future projections (until the year 2100) from UN data.
"""
import os
import re
import datetime

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def get_population_estimates():
   """Load in and parse the population data from the data file."""
   # Construct the path to the file.
   file_path = os.path.join(
      os.path.dirname(__file__), 'data', 'historical-and-projected-population-by-region.csv')
   # Read in the file.
   df = pd.read_csv(file_path)

   # Select the columns containing the world's projections.
   world_data = df.loc[df['Entity'] == 'World']

   # Find the column containing the word "population" and choose that.
   population_column = None
   for column in world_data.columns:
      if "Population" in str(column):
         population_column = column
         break

   # Select the `Year` column and turn it into an array.
   years = np.array(world_data['Year'])
   # Select the `Population` column and turn it into an array.
   population = np.array(world_data[population_column])

   # Shrink the data to the period 1800-2100 as opposed to -10000-2100.
   shrink_value = int(np.where(years == 1800)[0])
   years = years[shrink_value:]
   population = population[shrink_value:]

   # Return the data.
   return years, population

def plot_population_estimates(x_data, y_data):
   """Plots a graph visualizing past, current, and projected population."""
   # Configure the plot style.
   from matplotlib import style
   style.use('seaborn-pastel')

   # Construct the figure.
   plt.figure(figsize = (10, 5))

   # Plot the data.
   sns.lineplot(x = x_data, y = y_data, linewidth = 5, label = "Population", color = 'blue')

   # Fill the region under the graph.
   x = plt.gca().lines[0].get_xydata()[:, 0]
   y = plt.gca().lines[0].get_xydata()[:, 1]
   plt.gca().fill_between(x, y, color = 'blue', alpha = 0.3)

   # Shrink the plot boundaries to fit the graph.
   plt.xlim(1800, 2100)
   plt.ylim(0)

   # Display the plot.
   plt.show()


if __name__ == '__main__':
   # Parse the data.
   x, y = get_population_estimates()

   # Create the visualization.
   plot_population_estimates(x, y)


