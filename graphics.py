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
Utility methods for graphics processing.

A top-level module, since it is used by all individual research
directories for processing images and other related graphics.
"""

import os
import logging

import cairo
import cairosvg


# GRAPHICS CONVERSION METHODS:
# Methods for converting graphic filetypes, notable instances include
# svg to (png, jpg), since these are not possible through high-level libraries.


def svg_to_png(*paths, delete = False):
   """Converts a list of images from svg to png files."""
   # Create a return list for future usage.
   return_list = []

   # Iterate over the provided paths.
   for path in paths:
      # Get the image name and create the final filepath.
      filename, _ = os.path.splitext(path)
      save_path = filename + ".png"

      # Weird issues which sometimes arise.
      if os.path.exists(save_path):
         continue

      # Append the new path to the return list.
      return_list.append(save_path)

      # Convert the image.
      try:
         cairosvg.svg2png(url = path, write_to = save_path)
      except Exception as e:
         raise Exception(f"Error while attempting to parse {filename}", e)
      finally:
         del save_path

      # Delete the original image if requested to.
      if delete:
         os.remove(path)

   # Return the return list.
   return return_list


# PATH MANIPULATION METHODS:
# Methods for path manipulation that make manipulating paths
# a lot simpler from their initial methods.


def convert_path_extension(path, conversion = '.png'):
   """Converts a path extension to a different one (as provided)."""
   # Get the image name and create the final filepath.
   filename, _ = os.path.splitext(path)
   save_path = filename + conversion

   # Append the new path to the return list.
   return save_path


if __name__ == '__main__':
   # If running this file directly, then user is debugging.
   logging.basicConfig(format = '%(levelname)s - %(name)s: %(message)s')

   # Warn the user that they are in debugging mode.
   logging.warning("You are now directly running the query file. Unless you are debugging, do not edit this file.")

   # WORKING CODE HERE:

else:
   # Set up logging configuration for the InformationLoader class.
   logging.basicConfig(format = '%(levelname)s - %(name)s: %(message)s')


