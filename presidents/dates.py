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
import re

import datetime
import dateutil.relativedelta
import wikipedia as wk

# For figure development.
import numpy as np
from matplotlib import style
style.use('seaborn-deep')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.patches as mpatch

from query import parse_page_information
from query import InformationLoader

from presidents.info import presidents
from presidents.info import president_parties
from presidents.info import president_office_terms
from presidents.info import _MONTH_TO_ABBREVIATION

# Construct the information loader for presidential data.
class PresidentialInformationLoader(InformationLoader):
   def process_function(self):
      """Constructs a list containing Wikipedia information about each president."""
      # Set up information holding list.
      info_list = []

      # Add information about each president to list.
      for president in presidents:
         # Append the parsed page content (term information).
         info_list.append(parse_page_information(president))

      return info_list

# Construct object holding presidential information.
president_info = PresidentialInformationLoader(save_location = './data/president_data.pickle')
president_info.set_external_data(presidents = presidents)

# Get list of dates of presidents' lives.
def get_presidential_dates():
   """Constructs a list of the dates of presidents' lives."""
   with president_info as info:
      # List of president birthdate strings.
      birthdate_strings = []

      for info_string in info:
         # Construct a list of potential candidate strings.
         candidate_date_strings = []

         # Parse strings in parenthesis, then parse strings with years in them.
         _current_candidates = re.findall('(?<=\\()(?:[^()]+|\\([^)]+\\))+', info_string)
         for item in _current_candidates:
            if len(re.findall('^(?:.*?\\b(\\d{4})\\b){$n}', item)) >= 0:
               candidate_date_strings.append(item)

         # The first string will always be the dates of the president.
         birthdate_strings.append(candidate_date_strings[0])

   # Construct dict of final dates.
   final_dates = {}
   final_datetime_objects = {}

   # Parse birthdate strings to get birth (and potentially death) dates.
   for president, date in zip(president_info.presidents, birthdate_strings):
      # Find all four-digit numbers (years).
      _current_dates = [int(num) for num in re.findall('\\b\\d{4}\\b', date)]

      # For presidents without a death-date, add a '9999' placeholder.
      if len(_current_dates) == 1:
         _current_dates.append(9999)

      # Append presidential dates to dictionary.
      final_dates[president] = _current_dates

      # Now, parse all of the actual dates and turn them into datetime objects.
      _current_date_objects = []

      # Create the pattern to parse for Month, Day, Year.
      _date_search_pattern = re.compile("(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|"
                                        "Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|"
                                        "Dec(?:ember)?)\\s\\d{1,2},\\s\\d{4}")

      # Search over the string.
      for date_pattern in re.finditer(_date_search_pattern, date):
         # Convert to date object.
         date_pattern = date_pattern.group()

         # Parse the date pattern into a datetime objects.
         date_objects = [i[:-1] if i[-1] == ',' else i for i in date_pattern.split(' ')]

         # Convert the month into an abbreviation.
         date_objects[0] = _MONTH_TO_ABBREVIATION[date_objects[0]]

         # Create a datetime object from the list.
         date_obj = datetime.datetime.strptime(' '.join(date_objects), "%b %d %Y")

         # Append the object to the current list.
         _current_date_objects.append(date_obj)

      # If there is only one date (i.e. president is living), then add today's date.
      if len(_current_date_objects) == 1:
         # Get today's date.
         today_date = str(datetime.datetime.today())[:10]
         today_date = datetime.datetime.strptime(today_date, "%Y-%m-%d")

         # Add today to the list.
         _current_date_objects.append(today_date)

      # Create complete date object.
      final_datetime_objects[president] = _current_date_objects

   # Return the date objects.
   return final_datetime_objects

# Set the president birth dates to the class.
president_info.set_external_data(dates = get_presidential_dates())

def get_president_ages(date_dict):
   """Constructs a list of presidents' ages."""
   president_age_dict = {}

   # Iterate over president birth/death dates.
   for president, dates in date_dict.items():
      # Get the president's age.
      president_age = dateutil.relativedelta.relativedelta(dates[1], dates[0])

      # Add president age to dictionary.
      president_age_dict[president] = president_age

   # Return age dictionary.
   return president_age_dict

def get_president_parties():
   """Wraps the name of a president along with their political party affiliation into a dictionary."""
   party_dict = {}

   # Iterate over presidents and parties.
   for president, party in zip(presidents, president_parties):
      # Wrap the president and party together.
      party_dict[president] = party

   # Return party dictionary.
   return party_dict

def create_president_birth_timeline(save_figure = True):
   """Creates a timeline figure showing the birth of each president."""
   # Setup timeline figure.
   fig, ax = plt.subplots(figsize = (40, 6))
   plt.title(r"$\bf{Birth\:\,Dates\:\,of\:\,U.S.\:\,Presidents}$")

   # Plot actual president birthdate info onto the figure.
   with president_info:
      # Gather president names and birth dates.
      names = list(president_info.dates.keys())
      dates = [date_list[0] for date_list in president_info.dates.values()]

      # Create levels (e.g. the length of the lines showing dates).
      levels = np.tile([-7, 7, -5, 5, -3, 3, -1, 1], int(np.ceil(len(names)/6)))[:len(names)]

      # Extend the graph to the year 1700 and 20 years from the last president.
      # Get the date 20 years from the latest president's birth.
      longest_date = max(dates) + dateutil.relativedelta.relativedelta(years = +20)
      # Add today's date and the year 1720 to dates.
      dates.append(longest_date); dates.insert(0, datetime.datetime.strptime('1720', '%Y'))
      names.append(0); names.insert(0, 0)
      # Add level 0 for the year 1720 and today's date
      levels = [item for item in levels]
      levels.append(0); levels.insert(0, 0)
      levels = np.array(levels, dtype = int)

      # Plot the vertical lines.
      ax.vlines(dates, 0, levels, color = 'tab:cyan')
      ax.plot(dates, np.zeros_like(dates), "-o", color = "k", markerfacecolor = "w")

      # Annotate the lines with the president names.
      for number, (date, level, name) in enumerate(zip(dates, levels, names)):
         # Create the string containing the president's name & number (Grover Cleveland is an exception).
         if name != 0:
            if number < 24:
               name_and_num = f"{name} " + (r"$\bf{" + r"(22, 24)" + r"}$"
                                            if name == "Grover Cleveland"
                                            else r"$\bf{" + f"({number})" + r"}$")
            else:
               name_and_num = f"{name} " + (r"$\bf{" + r"(22, 24)" + r"}$"
                                            if name == "Grover Cleveland"
                                            else r"$\bf{" + f"({number + 1})" + r"}$")
         else:
            name_and_num = ''

         # Annotate the lines with the president names.
         ax.annotate(name_and_num, xy = (date, level),
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
         savefig.savefig('images/us-president-timeline.png')

def plot_age_distribution(save_figure = True):
   """Plots the age distributions of different presidents."""
   # Change style specifically for this graph.
   style.use('seaborn-dark')

   # Get the ages of each president.
   president_ages = get_president_ages(president_info.dates)

   # Get the number of unique ages (in years).
   actual_year_ages = [date.years for date in president_ages.values()]
   average_age = np.average(actual_year_ages)

   # Recreate the number of ages (rounded to the nearest 5).
   rounded_ages = []
   for item in actual_year_ages:
      # Create a helper function for rounding to the nearest fifth.
      def helper_round(x, base = 5):
         return base * round(x / base)

      # Add the rounded age.
      rounded_ages.append(helper_round(item))

   # Find the unique members and counts of the rounded ages.
   rounded_ages, rounded_counts = np.unique(rounded_ages, return_counts = True)

   # Set the plot configuration.
   plt.xlim([42.5, 102.5])
   plt.xticks(np.arange(47.5, 100, 5),
              [f"{int(item - 2.5)}-{int(item + 2.5)}" for item in np.arange(47.5, 100, 5)])
   plt.title(r"$\bf{Age\;Distribution\;Of\;U.S.\;Presidents}$")
   # Plot the actual bar plot (and adjust colors).
   plt.bar(rounded_ages, rounded_counts, width = 4.9, align = 'edge')

   # Draw an arrow pointing to the average age.
   plt.bar(average_age, 7, width = 0.5, align = 'edge')
   plt.annotate(text = "Average Age: {:.1f}".format(average_age),
                xy = (average_age, 6.8), xycoords = 'data',
                xytext = (85, 7.5), textcoords = 'data',
                horizontalalignment = 'center',
                arrowprops = dict(arrowstyle = "-|>",
                                  connectionstyle = 'arc3'))

   # Display the plot.
   savefig = plt.gcf()
   plt.show()

   # Save the figure.
   if save_figure:
      savefig.savefig('images/us-president-age-distribution.png')

   # Change the style back to its original setting.
   style.use('seaborn-deep')

def plot_president_life_party_timeline(save_figure = True):
   """Plots the life of each president simultaneously, with their political party affiliation."""
   # Change style specifically for this graph.
   style.use('seaborn-darkgrid')
   plt.rcParams['figure.facecolor'] = 'whitesmoke'

   # Configure the plot figure.
   plt.figure(figsize = (25, 15))

   # Get the start and end years of each president's life.
   start_years = []
   end_years = []

   # Iterate over presidents and their dates.
   with president_info:
      for indx, (president, dates) in enumerate(president_info.dates.items()):
         # Get the start date.
         start_years.append(dates[0].year)
         # Get the end date.
         end_years.append(dates[1].year)

   # Remove Grover Cleveland (Duplicate President).
   president_labels = presidents.copy()
   president_labels.pop(23)
   office_terms = president_office_terms.copy()
   office_terms[21].extend(office_terms.pop(23))
   
   # Reverse the lists (going from first to last, not last to first).
   start_years, end_years, president_labels = \
      list(reversed(start_years)), list(reversed(end_years)), list(reversed(president_labels))

   # Convert the lists to NumPy arrays so we can subtract.
   start_years = np.array(start_years)
   end_years = np.array(end_years)
   president_labels = president_labels
   party_affiliations = get_president_parties()
   office_terms = list(reversed(office_terms))

   # Construct the party-to-color dictionary.
   PARTY_TO_COLOR = {
      'Unaffiliated': 'darkgrey', 'Federalist': 'peru', 'Democratic-Republican': 'forestgreen',
      'Whig': 'gold', 'Democratic': 'blue', 'Republican': 'red', 'National Union': 'darkred'
   }

   # Some presidents have had terms shorter than one year.
   # For those presidents, we can iterate to a one-month schedule
   # (since William Henry Harrison had only 1 month in office)
   # We create a tracker here to know that if we have a certain president
   # who needs a term boost, the president after will have a slight reduction.
   _president_skip_tracker = None

   # Create the bar plot.
   for indx, (start_year, end_year, president_name, term) in \
         enumerate(zip(start_years, end_years, president_labels, office_terms)):
      # Plot the president's life.
      plt.barh(indx + 1, [end_year - start_year], left = [start_year],
               height = 0.8, color = PARTY_TO_COLOR[party_affiliations[president_name]])

      # Check if president's term was shorter than one year.
      if indx == 0:
         # If the incumbent president has only been in office for < 1 year, then
         # we need to write a separate parsing function since there is no 'future' president.
         if term[1].year - term[0].year < 1:
            # Calculate the delta.
            delta = (term[1].month - term[0].month + 1) / 12
            # Create new term.
            term_length = [term[1].year - term[0].year + delta]
            # Set tracker to next president.
            _president_skip_tracker = [president_labels[indx + 1], delta]
         else:
            # Otherwise, just use the regular term length.
            term_length = [term[1].year - term[0].year]
      elif indx < len(start_years) - 1:
         # This is the general case for all presidents except the first and the last.
         # We look ahead at the next president to see if they have any anomalies.
         future_president_terms = office_terms[indx + 1]
         if future_president_terms[1].year - future_president_terms[0].year < 1:
            # Calculate the delta which needs to be changed.
            delta = (future_president_terms[1].month - future_president_terms[0].month + 1) / 12
            # Create new current term.
            term_length = [term[1].year - term[0].year + delta]
            # Set tracker to next president.
            _president_skip_tracker = [president_labels[indx + 1], delta]
         else:
            # Otherwise, just use the regular term length.
            term_length = [term[1].year - term[0].year]
      else:
         # We know that the first president (George Washington) has no anomalies
         # so we can safely set his term length to be normal (since John Adams has no anomalies either).
         term_length = [term[1].year - term[0].year]

      # Check if president's name is in tracker.
      if _president_skip_tracker is not None:
         if _president_skip_tracker[0] == president_name:
            term_length = [term_length[0] - _president_skip_tracker[1]]
            # Reset tracker.
            _president_skip_tracker = None

      # Plot the president's term in office.
      # Grover Cleveland serves two non-consecutive terms so he needs to be accounted for.
      if indx == 23:
         # Luckily, there are no anomalies before or after Grover Cleveland so we can
         # semi-automatically fix this case with a simple exception.
         plt.barh(indx + 1, [term[1].year - term[0].year], left = [term[0].year],
                  height = 0.8, color = 'k')
         plt.barh(indx + 1, [term[3].year - term[2].year], left = [term[2].year],
                  height = 0.8, color = 'k')
      else:
         # Otherwise, plot as usual.
         plt.barh(indx + 1, term_length, left = [term[0].year],
                  height = 0.8, color = 'k')

      # print(indx, president_name, term_length, term, term[1].year - term[0].year)

   # Set the start and end years of the plot and the plot labels.
   plt.yticks([i + 1 for i in range(len(start_years))], president_labels)
   plt.xlim([start_years[-1] - 1, end_years[0] + 1])

   # Create the custom legend.
   different_parties = set(party_affiliations.values())
   legend_items = [mpatch.Patch(color = PARTY_TO_COLOR[p], label = p) for p in different_parties]
   legend_items.append(mpatch.Patch(color = 'k', label = "President's Term"))
   plt.legend(handles = legend_items, prop = {'size': 15})

   # Any additional formatting.
   plt.xticks([i for i in range(1725, datetime.datetime.today().year + 5, 10)])
   plt.ylim([0, len(start_years) + 1])
   plt.suptitle("$\\bf{Timeline\\,\\:Of\\,\\:U.S.\\,\\:Presidents}$", fontsize = 20)

   # Copyright.
   plt.text(1740, 2, '@amogh7joshi', fontsize = 30, alpha = 0.7, color = 'slategrey')

   # Display the figure.
   savefig = plt.gcf()
   plt.show()

   # Save the figure.
   if save_figure:
      savefig.savefig('images/us-president-life-and-terms.png')

   # Change the style back to original.
   style.use('seaborn-deep')
   plt.rcParams['figure.facecolor'] = 'white'


