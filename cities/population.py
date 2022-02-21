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

import os
import json

import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import shape

from query import parse_page_information, clean_escape_sequences


def plot_top_k_contiguous_us_city_populations(k = 50, savefig = True):
    # Read a map with U.S. state boundaries, and remove Alaska, Hawaii,
    # and any territories, to conform to the contiguous U.S.
    world = gpd.read_file('data/us-state-boundaries.csv')
    world = world[~world.name.isin([
        'Guam', 'American Samoa', 'United States Virgin Islands',
        'Puerto Rico', 'Commonwealth of the Northern Mariana Islands',
        'Alaska', 'Hawaii'])]

    # Get the geometry of the states and create a new dataframe with them.
    fig, ax = plt.subplots(figsize = (20, 15))
    geometries = [shape(json.loads(x)) for x in world['St Asgeojson'].tolist()]
    world = gpd.GeoDataFrame(
        {'name': world.name, 'geometry': geometries, 'region': world.region})
    ax = world.plot(ax = ax, edgecolor = 'black', column = 'region')
    ax.set_axis_off()

    # Read in the population data and create a geo dataframe.
    df = pd.read_csv('data/us_cities_population_contiguous.csv')
    gdf = gpd.GeoDataFrame(
        df, geometry = gpd.points_from_xy(df.Longitude, df.Latitude))

    # Select the top-k cities to show and create the plot.
    gdf[:k].plot(ax = ax, color = 'chartreuse',
                 markersize = gdf['Population'] // 5000)
    plt.title(f"Largest {k} Cities by Population in "
              f"Contiguous U.S. States", fontdict = {'size': 30})

    # Copyright.
    plt.text(-120, 27, '@amogh7joshi', fontsize = 30, alpha = 0.7, color = 'slategrey')

    # Finalize and display plot.
    plt.xlim(-130, -60)
    plt.tight_layout()
    fig = plt.gcf()
    plt.show()

    # Save the figure if requested to.
    if savefig:
        fig.savefig(f'images/us_top_{k}_cities_population_contiguous.png')


def us_city_population_processing_function(term):
    # Get all of the page's HTML content.
    soup = parse_page_information(term)

    # Get the table with the list of cities.
    info_table = soup.find_all('table', {'class': 'wikitable sortable'})[0]
    info_table = info_table.find_all('tbody')[0]

    # Compile together each of the tags which reference a city.
    contents = np.array(info_table.find_all('td'), dtype = object)
    contents = contents.reshape((-1, 10))

    # Get all of the cities, their populations, and their location.
    name, state, population, long, lat = [], [], [], [], []
    for item in contents:
        city_name = item[0].a.string
        city_state = item[1].a.string
        population_2020 = int(
            clean_escape_sequences(item[2].string).replace(',', ''))
        location = item[-1].find_all(
            'span', {'class': 'geo'})[0].string.split('; ')
        location = tuple([float(i) for i in location])

        # Skip Alaska and Hawaii (only contiguous states).
        if city_state.lower() in ['alaska', 'hawaii']:
            continue

        # Add the contents to the overall list.
        name.append(city_name)
        state.append(city_state)
        population.append(population_2020)
        lat.append(location[0])
        long.append(location[1])

    # Create a DataFrame from the information.
    df = pd.DataFrame({'Name': name, 'State': state,
                       'Population': population,
                       'Latitude': lat,
                       'Longitude': long})

    # Save the DataFrame.
    os.makedirs('data', exist_ok = True)
    df.to_csv('data/us_cities_population_contiguous.csv')


if __name__ == '__main__':
    plot_top_k_contiguous_us_city_populations()

