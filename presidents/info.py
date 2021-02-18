#!/usr/bin/env python3
# -*- coding = utf-8 -*-
import re
import datetime
import wikipedia as wk

# Webpage parsing functions.
import requests
from bs4 import BeautifulSoup

from query import process_page
from query import _pretty_parse

# Top-Level Conversion Dictionaries.
_MONTH_TO_ABBREVIATION = {'January': 'Jan', 'February': 'Feb', 'March': 'Mar',
                          'April': 'Apr', 'May': 'May', 'June': 'Jun', 'July': 'Jul',
                          'August': 'Aug', 'September': 'Sep', 'October': 'Oct',
                          'November': 'Nov', 'December': 'Dec'}

# Construct the processing function for US Presidents.
def us_president_processing_function(term):
   """The US Presidents list processing function (for usage in the process_page method)."""
   # Construct webpage.
   page = requests.get(wk.page(term, auto_suggest = False).url)
   soup = BeautifulSoup(page.content, 'html.parser')

   # Create the list of presidents.
   us_presidents = []

   # Find all <b> tags and parse table content.
   table = soup.find('table', class_ = re.compile('wikitable'))
   for item in table.find_all('b'):
      # Notable instances which need to be skipped.
      if item.text.strip() in ['Sources:']:
         continue

      # Add to list of presidents.
      us_presidents.append(item.text.strip())

   # Return the list of presidents.
   return us_presidents

# Construct list of presidents.
presidents = process_page('us presidents', processing_function = us_president_processing_function)

# Construct the processing function for US Presidents' Political Parties.
def us_president_political_parties_processing_function(term):
   """The US Presidents political parties processing function (for usage in the process_page method)."""
   # Construct webpage.
   page = requests.get(wk.page(term, auto_suggest = False).url)
   soup = BeautifulSoup(page.content, 'html.parser')

   # Create the list of political party affiliations.
   political_parties = []

   # Find all <tr> tags and parse table content.
   main_table = soup.find('table', class_ = re.compile('wikitable'))
   for row in main_table.find_all('tr'):
      for indx, item in enumerate(row.find_all('td')):
         # Notable instances which need to be skipped.
         if item.text.strip() in ['Sources:']:
            continue

         # The fourth index contains the party, add it to the list.
         if indx == 4:
            political_parties.append(re.sub('\\[(.*?)\\]', '', item.text.strip()))

   # Return the list of parties.
   return political_parties

# Construct the list of presidential political parties.
president_parties = process_page('us presidents', processing_function = us_president_political_parties_processing_function)

# Construct the processing function for US Presidents' Term in Office.
def us_president_office_term_processing_function(term):
   """The US Presidents term in office processing function (for usage in the process_page method)."""
   # Construct webpage.
   page = requests.get(wk.page(term, auto_suggest = False).url)
   soup = BeautifulSoup(page.content, 'html.parser')

   # Create the list of terms in office.
   office_terms = []

   # Find all <tr> tags and parse table content.
   main_table = soup.find('table', class_ = re.compile('wikitable'))
   for row in main_table.find_all('tr'):
      for indx, item in enumerate(row.find_all('td')):
         # Notable instances which need to be skipped.
         if item.text.strip() in ['Sources:']:
            continue

         # The first index contains the term, add it to the list.
         if indx == 0:
            # However, sometimes the first term might contain runaway information, so
            # we need to parse for these certain cases (essentially look for a valid term).
            _date_search_pattern = re.compile("(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|"
                                              "Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|"
                                              "Dec(?:ember)?)\\s\\d{1,2},\\s\\d{4}")
            if len(re.findall(_date_search_pattern, item.text.strip())) > 0:
               # Get rid of any links.
               term = re.sub('\\[(.*?)\\]', '', item.text.strip())

               # Create the candidate list.
               _candidate_term = []

               # Create a candidate list of pre-parsed dates.
               _pre_parsed_dates = []

               # Parse for start and end month/years.
               for date in re.finditer(_date_search_pattern, term):
                  _pre_parsed_dates.append(date.group())

               # Convert terms to datetime objects..
               for date_pattern in _pre_parsed_dates:
                  # Parse the date pattern into a datetime objects.
                  date_objects = [i[:-1] if i[-1] == ',' else i for i in date_pattern.split(' ')]

                  # Convert the month into an abbreviation.
                  date_objects[0] = _MONTH_TO_ABBREVIATION[date_objects[0]]

                  # Create a datetime object from the list.
                  date_obj = datetime.datetime.strptime(' '.join(date_objects), "%b %d %Y")

                  # Add to candidate term list.
                  _candidate_term.append(date_obj)

               # If the end year is empty, that's because the president is an incumbent.
               # In that case, simply add the current date to the candidate list.
               if len(_pre_parsed_dates) == 1:
                  # Get today's date in month/day/year.
                  _candidate_term.append(datetime.datetime.strptime(
                     datetime.datetime.today().strftime("%b %d %Y"), "%b %d %Y"))

               # Add the candidate list to the main list.
               office_terms.append(_candidate_term)

   # Return the list of terms.
   return office_terms

# Construct the list of presidents' terms in office.
president_office_terms = process_page('us presidents', processing_function = us_president_office_term_processing_function)

# Other useful methods:

def us_president_infobox_processing_function(term):
   """The US Presidents infobox processing function, returns a dictionary containing
   semi-processed information about a President (from the Wikipedia person infobox)."""
   # Construct webpage.
   page = requests.get(wk.page(term, auto_suggest = False).url)
   soup = BeautifulSoup(page.content, 'html.parser')

   # Create the list of presidents.
   label_dict = {}

   # Find all <th> and <td> tags and parse table content.
   table = soup.find('table', class_ = re.compile('infobox vcard'))
   label_list = table.find_all('th'); label_list.insert(0, 'Name')
   for label, item in zip(label_list, table.find_all('td')):
      # Skip if item contains no information.
      if item.text.strip() == '':
         continue

      # Parse item text.
      item = item.text.strip()
      # Remove "In Office" from the strings.
      item = re.sub('(?:In office)', '', item)
      # Remove the non-breaking space character.
      item = item.replace(u'\xa0', u' ')
      # Remove the zero-width space character.
      item = item.replace(u'\u200b', u'')
      # Add spaces between words when necessary.
      item = re.sub('(^ )(A-Z)', ' ', item)
      # Convert newlines to commas (for a list comprehension).
      item = re.sub('\n', ', ', item)
      # Wikipedia pretty-parse item.
      item = _pretty_parse(item)

      if isinstance(label, str):
         label_dict[label.strip()] = item
      else:
         label_dict[label.text.strip()] = item

   # Return the list of presidents.
   return label_dict

