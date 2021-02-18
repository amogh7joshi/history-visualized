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
Utility methods for search queries through the Wikipedia API.

A top-level module, since it is used by all individual research
directories as an API-searching and information processing resource.
"""
import os
import sys
import re
import abc
import copy
import logging
import pickle
import inspect

# Wikipedia API.
import wikipedia as wk

# Webpage Parsing Modules.
import requests
from bs4 import BeautifulSoup

# Country Processing Modules.
import pycountry as pc

# Top-Level Resource Lists: Updated in the validation methods below.
_SUPPORTED_LIST_QUERIES = []
_REPLACEMENT_QUERIES = []
_ALLOWED_SPACED_QUERIES = []
_NATION_DICT = {}
_VALIDATED_CACHE = {}

# Additional Constants.
BASE_WIKI_URL = "https://en.wikipedia.org/wiki/"
BASE_WIKI_API_URL = "https://en.wikipedia.org/w/api.php"
BASE_WIKI_REQUEST_URL = 'http://en.wikipedia.org/w/api.php?action=query&prop=pageimages&format=json&piprop=original&titles='

# GENERATION METHODS:
# Internal methods to construct the above resource lists and dictionaries.

def _generate_nation_dict():
   """Generates the _NATION_DICT resource dictionary."""
   global _NATION_DICT

   # Append items to the dictionary.
   for indx, item in enumerate(pc.countries):
      # Parse the nation name, splitting it where there is a comma.
      if ',' in item.name and (item.name.endswith('of') or item.name.endswith('of the')):
         country_name, country_official_name = item.name.split(', ')
         country_official_name = ' '.join([country_official_name, country_name])
      else:
         country_name = item.name
         country_official_name = item.name

      # Create a sub-list.
      _sublist = list({country_name, country_official_name, item.alpha_2, item.alpha_3})
      _sublist = [it.lower() for it in _sublist]

      # Manual additions as necessary.
      if country_official_name == 'Brunei Darussalam':
         _sublist.append('brunei')
      if country_official_name == "Democratic People's Republic of Korea":
         _sublist.append('north korea')
      if country_official_name == "Republic of Korea":
         _sublist.append('south korea')
      if country_official_name == 'Cabo Verde':
         _sublist.append('cape verde')

      # Append to dictionary.
      _NATION_DICT[indx] = _sublist

   # Add a manual item.
   _NATION_DICT[indx + 1] = ['East Timor']
   _NATION_DICT[indx + 2] = ['Timor-Leste']

def _generate_replacement_queries():
   """Generates the _REPLACEMENT_QUERIES list."""
   global _REPLACEMENT_QUERIES

   # Add items to the list.
   _REPLACEMENT_QUERIES.append(['nation', 'country', 'countries', 'nations', 'sovereign states'])
   _REPLACEMENT_QUERIES.append(['president', 'presidents', 'prime minister', 'prime ministers'])

def _generate_allowed_spaced_queries():
   """Generates the _ALLOWED_SPACED_QUERIES list."""
   global _ALLOWED_SPACED_QUERIES

   # Add items to the list.
   _ALLOWED_SPACED_QUERIES.extend(['prime minister', 'prime ministers'])
   _ALLOWED_SPACED_QUERIES.extend(['united states'])

def _generate_resources():
   """Generates the resource lists before anything gets imported."""
   # Generate list of nations and relevant codes.
   _generate_nation_dict()
   # Generate list of replacement queries.
   _generate_replacement_queries()
   # Generate list of queries allowed to have spaces.
   _generate_allowed_spaced_queries()

# OS METHODS:
# These methods allow for path manipulation and processing.

def get_base_path_name(file):
   """Get the base filename, without the directory tree and file extension."""
   return os.path.splitext(os.path.basename(file))[0]

# TOP-LEVEL QUERY VALIDATION METHODS:
# These methods are basic query validation methods, to determine whether a query is appropriate.

def is_valid_country(term):
   """Determines if an input nation is a valid nation."""
   # Construct a cache so we don't have to perform a dictionary comprehension every time.
   global _VALIDATED_CACHE
   try:
      term = term.lower()
   except TypeError:
      return False # If the input is not a string.
   except AttributeError:
      return False # If the input is not a string.

   # Iterate over dictionary's values.
   for value in _NATION_DICT.values():
      if term in value:
         # If term is valid, add it to the cache and return it.
         _VALIDATED_CACHE[term] = True
         return _VALIDATED_CACHE[term]

   # Otherwise, set it to False and return it.
   _VALIDATED_CACHE[term] = False
   return _VALIDATED_CACHE[term]

# WIKIPEDIA API INTERACTION METHODS:
# These methods conduct the actual searching of the Wikipedia API.

def _merge_query_results(*terms, output_thresh = 20):
   """Converts provided query terms into a list of outputs."""
   # Construct list of outputs.
   output_values = []

   for term in terms:
      # Validate query term.
      if not isinstance(term, str):
         raise TypeError(f"Received invalid term {term} of type {type(term)}.")

      # Get search query.
      try:
         _search_query = term.lower() # Reduce issues with case-sensitivity.
         _output_items = wk.search(term, results = output_thresh)
      finally:
         del _search_query

      # Add output to results.
      output_values.extend(_output_items)

   # Return results.
   return output_values

def search_multiple_words(*words, output_thresh = 20):
   """Gets the output result of multiple words and returns values which contain each input term."""
   if len(words) == 1: # If there is only one search query.
      return wk.search(words[0], results = output_thresh)

   # Get complete list of outputs.
   complete_output = _merge_query_results(*words, output_thresh = output_thresh)
   _tracker_output = [word.lower() for word in complete_output] # For actual tracking.

   # Create list of final outputs.
   final_output = []

   # Filter list of outputs.
   for _lower_output, output in zip(_tracker_output, complete_output):
      # Set tracker.
      _track = True

      # Iterate over search queries.
      for term in words:
         _term = term.lower() # Convert term to lowercase.
         if _term not in _lower_output:
            # One term is missing from output.
            _track = False

      # Add to final output list.
      if _track:
         final_output.append(output)

   # Return final outputs.
   return final_output

def _parse_query_for_conditions(*terms, **kwargs):
   """Certain queries have allotted replacements which need to all be tried."""
   # Determine if one of the provided terms is a nation.
   global _NATION_DICT
   _filter_terms = list(copy.deepcopy(terms))
   for term in _filter_terms:
      # Iterate over _NATION_DICT.
      for _value_pair in _NATION_DICT.values():
         if term in _value_pair:
            # Remove the code from the list.
            _filter_terms.remove(term)

            # If term is a nation, then gather a list of all possible outputs for
            # each possible version of the nation's name.
            _output = []
            for _nation_code in _value_pair:
               # Replace the index of the code with a different code.
               _filter_terms.append(_nation_code)

               # Add the list of result items to the current output list.
               _output.extend(list_of_search_results(*_filter_terms, bypass=False))

               # Remove the index code.
               _filter_terms.remove(_nation_code)

            # Return the final output list.
            return _output

   # Determine if one of the provided terms is a replaceable term.
   if 'skip_replacement_queries' not in kwargs:
      global _REPLACEMENT_QUERIES
      _filter_terms = list(copy.deepcopy(terms))
      for term in _filter_terms:
         # Iterate over _REPLACEMENT_QUERIES.
         for _query_matches in _REPLACEMENT_QUERIES:
            if term in _query_matches:
               # Remove the replaceable term from the list.
               _filter_terms.remove(term)

               # If the term is replaceable, then gather a list of all possible outputs for
               # each of the different replacement queries.
               _output = []
               for _generated_query in _query_matches:
                  # Replace the index of the term with a different term.
                  _filter_terms.append(_generated_query)

                  # Add the list of result items to the current output list.
                  _output.extend(list_of_search_results(*_filter_terms, bypass=False))

                  # Remove the index term.
                  _filter_terms.remove(_generated_query)

               # Return the final output list.
               return _output

   # If nothing has been returned, then return the original method.
   return list_of_search_results(*terms, bypass = False)

def list_of_search_results(*terms, bypass = True, **kwargs):
   """Returns a list of search result items from a specific query, such as 'list of nations'."""
   # The bypass argument should only be changed by this function itself.
   # Determine if it is changed by the user.
   if not bypass:
      # Get current and outer frame.
      current_frame = inspect.currentframe()
      call_frame = inspect.getouterframes(current_frame, 2)
      if call_frame[1][3] not in ['list_of_search_results', '_parse_query_for_conditions']:
         raise PermissionError("The `bypass` keyword argument was changed by an external function, which "
                               "should never be done. Edit your code to leave the argument unchanged. ")

   # See if the provided term has multiple words.
   _validation_list = list(copy.deepcopy(terms))
   terms = []
   for term in _validation_list:
      global _ALLOWED_SPACED_QUERIES
      if " " in term and term not in _ALLOWED_SPACED_QUERIES:
         terms.extend(term.split(' '))
      else:
         terms.append(term)

   # Parse for certain conditions.
   if bypass:
      return _parse_query_for_conditions(*terms, **kwargs)

   # Either have a list of terms, or a single term.
   if len(terms) == 1:
      # Get an output list of query terms.
      try:
         _query_term = terms[0].lower() # Reduce issues with case-sensitivity.
         output_list = search_multiple_words(_query_term, 'list', output_thresh = 100)
      finally:
         del _query_term
   else:
      # Get an output list of query terms.
      try:
         _query_terms = [term.lower() for term in terms] # Reduce issues with case-sensitivity.
         output_list = search_multiple_words(*_query_terms, 'list', output_thresh = 100)
      finally:
         del _query_terms

   # Return the list of query terms (filtered for uniqueness).
   return list(set(output_list))

def process_page(*search_terms, specific_query = None, processing_function = None):
   """Returns the result of a search, such as 'list of countries', from a given processing function.
   Uses a provided processing function, so it must be overwritten for a specific purpose."""
   # Determine whether the search term is supported (e.g. has a special case).
   global _SUPPORTED_LIST_QUERIES
   _SUPPORTED_LIST_QUERIES = ['us presidents', 'sovereign states formation']
   for search_term in search_terms:
      if search_term in _SUPPORTED_LIST_QUERIES:
         if search_term == 'us presidents':
            # Special case of U.S. Presidents.
            return processing_function('List of presidents of the United States')
         if search_term == 'sovereign states formation':
            # Special case of Sovereign States by Formation.
            return processing_function('List of sovereign states by dates of formation')

   # Get the Wikipedia pages.
   # There might be multiple lists, so this option allows to search for a specific list.
   if specific_query:
      for _check_list in list_of_search_results(*search_terms, skip_replacement_queries = True):
         # Parse for a substring.
         if specific_query in _check_list:
            _valid_list = _check_list
            break
         # Parse for a complete string.
         if specific_query.lower() == _check_list.lower():
            _valid_list = _check_list
            break

      # Determine if a result exists.
      try:
         _x = _valid_list
      except:
         _valid_list = list_of_search_results(*search_terms, skip_replacement_queries = True)
   else:
      # Otherwise, just use the first list result.
      _valid_list = list_of_search_results(*search_terms, skip_replacement_queries = True)[0]

   # Validate processing function.
   if not processing_function:
      raise ValueError("You need to provide a specific processing function in order to process the "
                       "data provided by the Wikipedia API result.")

   # Apply processing function to the data.
   return processing_function(_valid_list)

def _pretty_parse(item):
   """Prettifies an inputted string containing Wikipedia page content."""
   if not isinstance(item, str):
      raise TypeError(f"Expected a string containing Wikipedia page content, got {type(item)}")

   # Remove all header/footer links from page.
   item = re.sub('\\[.{0,3}\\]', '', item)

   # Add spaces after periods if necessary.
   item = re.sub('\\.(?!\\s|$|"|\')', '. ', item)

   # Turn escaped apostrophes into literal apostrophes.
   item = item.replace("\'", "'")

   # Remove \u200 unicode characters.
   item = re.sub(r'[^\x00-\x7F]+', '', item)

   # Turn newlines into commas and spaces.
   item = re.sub('\n', ', ', item)

   return item

def parse_page_information(term):
   """Returns the page information from a parsed term."""
   if not isinstance(term, str):
      raise TypeError("You must provide a pre-parsed string to get the page information, if you are searching "
                      "using an arbitrary term then you need to get the specific term first.")

   # Get the specific page URL.
   try:
      page_url = wk.page(term, auto_suggest = False).url
   except wk.DisambiguationError:
      raise ValueError("Arrived at a Wikipedia disambiguation. Try again with a pre-parsed specific term.")
   except Exception as e:
      raise e

   # Get the page content from the URL.
   page = requests.get(page_url)
   soup = BeautifulSoup(page.content, 'html.parser')

   # Set up the string containing the complete description.
   complete_information = ""

   # Get all of the paragraph content in the page.
   table = soup.find('div', class_ = re.compile('mw-content-ltr'))
   for item in table.find_all('p'):
      # Notable instances which need to be skipped.
      if item.text.strip() in ['Sources:']:
         continue

      # Add to list of presidents.
      complete_information += item.text.strip()

   # Parse and prettify the content before returning.
   return _pretty_parse(complete_information)

# INFORMATION RETENTION METHODS AND CLASSES:
# These methods and classes allow for information retention, e.g. saving already parsed
# information into a binary file in order for easy and efficient storage and re-usage.

class InformationLoader(object, metaclass = abc.ABCMeta):
   """Abstract base class which facilitates the easy storage and reuse of parsed Wikipedia
   page content through binary files which are opened and rewritten as necessary. For usage,
   this base class should be subclassed and the saving operation should be overwritten.

   When processing data, use:

   >>> info_holder = InformationLoader()
   >>> with info_holder as info:
   ...   pass

   """
   def __init__(self, save_location, overwrite_data = False):
      if not save_location:
         raise ValueError("You need to provide a save location where the saved "
                          "information files will reside.")

      # Verify the save file and set it to the class.
      if not os.path.exists(os.path.dirname(save_location)):
         raise NotADirectoryError("The directory of the provided path does not exist, "
                                  "you need to provide an existing path directory.")
      else:
         self.save_location = save_location
         self.overwrite_data = overwrite_data
         self._is_loaded = False

      # Class data.
      self.data = None

      # Load optional data.
      self._external_attributes = []
      self.set_external_data()

   def set_external_data(self, **kwargs):
      """A method allowing the user to set additional data to the class if necessary."""
      for key, value in kwargs.items():
         setattr(self, key, value)
         self._external_attributes.append(key)

   def __sizeof__(self):
      _self_data = sys.getsizeof(self.data)
      for item_name in self._external_attributes:
         _self_data += sys.getsizeof(getattr(self, item_name))
      return _self_data

   def __getattr__(self, item):
      if item not in self._external_attributes:
         raise AttributeError(f"You have provided an invalid attribute, expected either "
                              f"an inbuilt attribute or one provided in "
                              f"set_external_class_data: ({self._external_attributes}).")

   def __enter__(self):
      return self._load_or_parse()

   def __exit__(self, exc_type, exc_val, exc_tb):
      try:
         if not os.path.exists(self.save_location):
            with open(self.save_location, 'wb') as save_file:
               pickle.dump(self.data, save_file)
         elif os.path.exists(self.save_location) and self.overwrite_data:
            with open(self.save_location, 'wb') as save_file:
               pickle.dump(self.data, save_file)
      except Exception as e:
         raise e

   def _load_or_parse(self):
      """Either loads data from an existing file (self.save_location) or re-processes."""
      if self._is_loaded: # Lazy Loading.
         return self.data
      if self.overwrite_data:
         logging.warning("Re-processing data for future overwriting.")
         self.data = self.process_function()
         self._is_loaded = True
         return self.data
      else:
         if os.path.exists(self.save_location):
            with open(self.save_location, 'rb') as save_file:
               self.data = pickle.load(save_file)
            self._is_loaded = True
            return self.data
         else:
            logging.warning("Pre-parsed data file not found, re-processing data.")
            self.data = self.process_function()
            self._is_loaded = True
            return self.data

   @abc.abstractmethod
   def process_function(self, *args, **kwargs):
      """The primary method which processes the provided information. Needs to be implemented."""
      raise NotImplementedError("The process_function method needs to be overwritten for usage.")

if __name__ == '__main__':
   # If running this file directly, then user is debugging.
   logging.basicConfig(format = '%(levelname)s - %(name)s: %(message)s')

   # Warn the user that they are in debugging mode.
   logging.warning("You are now directly running the query file. Unless you are debugging, do not edit this file.")

   # Configure global resource lists.
   _generate_resources()

   # WORKING CODE HERE:
   print(list_of_search_results('nations', 'formation'))

else:
   # Set up logging configuration for the InformationLoader class.
   logging.basicConfig(format = '%(levelname)s - %(name)s: %(message)s')

   # Otherwise, something is being imported. In that case, initialize the global resource lists.
   _generate_resources()


