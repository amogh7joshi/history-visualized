#!/usr/bin/env python3
# -*- coding = utf-8 -*-
import os
import re
import json
import tqdm
import shutil
import wikipedia as wk

# Country parsing functions.
import pycountry as pc

# Webpage parsing functions.
import requests
from bs4 import BeautifulSoup

from query import process_page
from query import is_valid_country
from query import InformationLoader
from query import BASE_WIKI_REQUEST_URL
from query import get_base_path_name

from graphics import svg_to_png
from graphics import convert_path_extension

def nation_founding_date_processing_function(term):
   """The nation founding date list (for usage in the list_of_items method)."""
   # Construct webpage.
   page = requests.get(wk.page(term).url)
   soup = BeautifulSoup(page.content, 'html.parser')

   # Create the dictionary of dates.
   founding_dates = {}

   # Create a tracker list of nations to see what has already been found.
   _nation_tracker = []
   _date_tracker = []

   # Find all rows within tables containing nation data.
   tables = soup.find_all('tr')
   for table in tables:
      # Search for <td> tags containing actual data.
      data_values = table.find_all('td')

      # Tracker for determining whether a nation has been parsed yet, and
      # if so, then we need to determine the date.
      is_nation = False

      # Iterate over the discovered values and determine if each is a country.
      for indx, value in enumerate(data_values):
         # Get the text from the value.
         current_value = value.text.split('\n')
         _current_tracker = current_value.copy()

         # Remove blank spaces.
         for val in _current_tracker:
            if val == '':
               current_value.remove(val)

         # If we have already found a nation.
         if is_nation:
            # Manual skip for certain cases.
            if is_nation == 'Iceland':
               _date_tracker.append('1 July 1845')
               break
            # Otherwise, undertake usual checks.
            if indx == 1:
               try:
                  # Sometimes, the second column might contain a continent
                  # rather than a date. So, we determine if it is.
                  _is_potential_continent = bool(re.search(r'\d', current_value[0]))
                  if _is_potential_continent:
                     _date_tracker.append(current_value[0])
                     break
                  else:
                     continue
               except IndexError:
                  # Otherwise, continue iterating through the table
                  # columns until we arrive at an equivalent date.
                  continue
            elif indx == 2:
               # Manual skip for certain cases.
               if is_nation == 'China':
                  continue
               # Otherwise, undertake usual checks.
               try:
                  # Sometimes, the third column might contain a continent
                  # rather than a date. So, we determine if it is.
                  _is_potential_continent = re.findall('\\d', current_value[0])
                  if len(_is_potential_continent) > 0:
                     _date_tracker.append(current_value[0])
                     break
                  else:
                     continue
               except IndexError:
                  # Continue iterating if this causes an issue.
                  continue
            elif indx == 3:
               try:
                  # Now, try the next possible value.
                  _date_tracker.append(current_value[0])
               except Exception as e:
                  raise e
            else: # Continue parsing until we find the date.
               continue

         # If there is no value in the list, automatically break.
         if len(current_value) == 0:
            break

         # Extract the potential nation from the list.
         potential_nation = re.sub('\xa0', '', current_value[0]).strip()
         potential_nation = re.sub('\\[(.*?)\\]', '', potential_nation)
         potential_nation = re.sub(r'[^\x00-\x7F]+', '', potential_nation)

         # Parse the value for a country.
         if is_valid_country(potential_nation.strip()):
            # Break if nation is already discovered.
            if potential_nation in _nation_tracker:
               break
            else: # Otherwise, add to the tracker.
               # Manual case which we need to account for.
               if potential_nation.strip() == 'Cabo Verde':
                  potential_nation = 'Cape Verde'

               # Add potential nation to nation tracker.
               _nation_tracker.append(potential_nation)
               is_nation = potential_nation

      # Return nation tracker back to False.
      is_nation = False

   for nation, date in zip(_nation_tracker, _date_tracker):
      # Some repeats that we need to manually skip.
      if nation in ['Czechia', 'Palestine']:
         continue
      
      # Get the year from the provided date.
      try:
         _founding_date = re.findall('\\d{4}', date)[0]
      except IndexError as ie:
         raise ie

      # Add the nation and date to the dictionary.
      founding_dates[nation] = _founding_date

   # Return the complete dictionary.
   return founding_dates

# Construct the list of dates.
founding_dates = process_page('sovereign states formation', processing_function = nation_founding_date_processing_function)

# Construct the information loader for nation flags.
class NationFlagInformationLoader(InformationLoader):
   def process_function(self, *args, **kwargs):
      """Gets svg images of nations' flags and converts them to a usable png format."""
      storage_dir = self.storage_dir

      # Determine if self.founding_dates exists.
      if not hasattr(self, 'founding_dates'):
         raise AttributeError("The Nation Flag Information loader is missing the `founding_dates` dictionary, "
                              "set the dictionary as an external class attribute before using it.")

      # Get a list of existing images.
      svg_images = []
      png_images = []
      for item in os.listdir(storage_dir):
         if item.endswith('.svg'):
            svg_images.append(os.path.join(storage_dir, item))
         if item.endswith('.png'):
            png_images.append(os.path.join(storage_dir, item))

      # Determine if png or svg images already exist.
      # If so, orchestrate the necessary processing steps.
      if len(png_images) == len(self.founding_dates.keys()):
         # The png images already exist, so everything has been processed.
         self.data = [os.path.join(storage_dir, image) for image in png_images]
         return self.data
      elif len(svg_images) == len(self.founding_dates.keys()):
         # If the svg images exist but not the png images, then just process the png images.
         # But first, remove the png images.
         for image in [os.path.join(storage_dir, image) for image in png_images]:
            os.remove(image)
         return self.convert_images()
      else:
         # Otherwise, remove all existing png/svg images and re-process.
         for image in [os.path.join(storage_dir, image) for image in svg_images]:
            os.remove(image)
         for image in [os.path.join(storage_dir, image) for image in png_images]:
            os.remove(image)
         return self.download_images()

   def download_images(self):
      """Stage 1 of self.process_function, downloads the svg files containing flag images."""
      # Construct the return list.
      link_list = []

      # Iterate over each nation.
      for nation in tqdm.tqdm(list(self.founding_dates.keys())):
         # Some pages are odd, so we need to manually parse for certain keywords.
         if nation == 'Ireland':
            nation = 'Republic of Ireland'
         if nation == 'Georgia':
            nation = 'Georgia (country)'

         # Parse for page data.
         try:
            url = wk.page(nation, auto_suggest = False).url
         except wk.DisambiguationError as wkd:
            raise wkd

         nation_name = list(item.group() for item in re.finditer('([^/]*)$', url))[0]

         # Get the image link.
         base_page_data = requests.get(BASE_WIKI_REQUEST_URL + nation_name)
         json_page_data = json.loads(base_page_data.text)

         # Return the image source.
         link_list.append(list(json_page_data['query']['pages'].values())[0]['original']['source'])

      # A tracker to ensure that nations which have names which contain the names of
      # other nations are not duplicated in the final list of links.
      _nation_tracker = []

      # Parse through links and download the image.
      for link in link_list:
         # Get the image from source.
         response = requests.get(link, stream = True)

         # Save the image to a local image file.
         nation_name = list(item.group() for item in re.finditer('([^/]*)$', link))[0]
         for nation in self.founding_dates.keys():
            # Manual replacement for certain countries.
            if nation_name == 'Flag_of_East_Timor.svg':
               nation_name = 'Flag_of_Timor-Leste.svg'

            # Regular parsing check.
            if nation.replace(' ', '_') in nation_name and nation.replace(' ', '_') not in _nation_tracker:
               nation_name = nation.replace(' ', '_')
               _nation_tracker.append(nation_name)
               break

         nation_file_name = nation_name + '.svg' if str(link).endswith('.svg') else nation_name + '.png'
         with open(os.path.join(self.storage_dir, nation_file_name), 'wb') as write_file:
            write_file.write(response.content)

      # Return the complete list.
      return self.convert_images()

   def convert_images(self):
      """Stage 2 of self.process_function, converts the svg files to png files."""
      # Get a list of existing images.
      svg_images = []
      for item in os.listdir(self.storage_dir):
         if item.endswith('.svg'):
            svg_images.append(os.path.join(self.storage_dir, item))
      png_images = []
      for item in os.listdir(self.storage_dir):
         if item.endswith('.png'):
            png_images.append(os.path.join(self.storage_dir, item))

      # Check for errors (and add countries which are exceptions).
      svg_image_len = len(svg_images)
      svg_image_len += (1 if os.path.join(self.storage_dir, 'Kyrgyzstan.png') in png_images else 0)
      if svg_image_len != len(self.founding_dates.values()):
         raise ValueError("Missing svg images for conversion, retry and check the processing function.")

      _svg_images_parsed = svg_images

      # Convert images from svg to png.
      _image_paths = svg_to_png(*_svg_images_parsed, delete = True)

      # Add countries which are already .png files to the list.
      _image_paths.append(os.path.join(self.storage_dir, 'Kyrgyzstan.png'))

      # Convert the list into a dictionary, for easy mapping between nation names and flag image paths.
      _image_paths_dict = {}
      for image_path in _image_paths:
         # Get the country name.
         _image_paths_dict[get_base_path_name(image_path)] = image_path

      # Set class data.
      self.data = _image_paths_dict
      return self.data

# Construct the nation flag information loader.
nation_flag_info = NationFlagInformationLoader(
   save_location = os.path.join(os.path.dirname(__file__), 'data', 'flag_data.pickle'))
nation_flag_info.set_external_data(founding_dates = founding_dates,
                                   storage_dir = os.path.join(os.path.dirname(__file__), 'flag_image_storage'))


