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
A specific implementation of a graph representing the United States
Imports and Exports before/during/after World War I, as part of a project
on the influence of WWI on U.S. globalism.
"""

import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# Configure the style.
from matplotlib import style
style.use('fivethirtyeight')

def build_us_import_export_graph(savefig = True):
   """Builds the U.S. imports/exports graph from 1913-1924."""
   # Construct the figure.
   fix, ax = plt.subplots(figsize = (10, 5))

   # Construct the data first.
   exports = [2465884, 2412835, 2741177, 4317040,
              3521758, 3169633, 3844866, 3640715,
              3051041, 2571662, 2706164, 3060656]
   imports = [1813008, 1932577, 1657594, 1883177,
              1668061, 1562480, 1895323, 2335611,
              1706903, 2089091, 2462380, 2406642]

   # Scale to a smaller range.
   exports = [item / 1e6 for item in exports]
   imports = [item / 1e6 for item in imports]

   # Plot the data.
   plt.plot(
      np.arange(1913, len(exports) + 1913, 1),
      np.array(exports), color = 'tab:cyan',
      label = 'Exports')
   plt.plot(
      np.arange(1913, len(imports) + 1913, 1),
      np.array(imports), color = 'tab:green',
      label = 'Imports')

   # Add the plot title.
   plt.suptitle(
      "$\\bf{U.S.\\,\\:Economy\\,\\:From\\,\\:1913-1924}$", fontsize = 20)

   # Add the axis titles.
   plt.xlabel('Year')
   plt.ylabel('$USD (in billions)', labelpad = 10)

   # Final formatting.
   plt.ticklabel_format(useOffset = False)
   plt.ylim(1.0, 4.5)
   plt.legend()

   # Display the plot.
   fig = plt.gcf()
   plt.show()

   # Save the figure.
   if savefig:
      fig.savefig('images/us-economy-ww1.png')


if __name__ == '__main__':
   # Build the graph.
   build_us_import_export_graph()
