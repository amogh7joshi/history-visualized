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


# NATIONS/INFO.PY
# PARSER FOR THE NATIONFLAGINFORMATIONLOADER CLASS

# Create a nation tracker (for a similar reason as above).
# _nation_tracker = []

# Change the image file paths to just the nation name.
# _save_image_list = []
# _svg_images_parsed = []
# for path_item in svg_images:
#    # Get the actual pathname.
#    path, filename = os.path.split(path_item)
#    filename = convert_path_extension(filename, conversion = '.png')
#
#    # Parse string to find the nation name.
#    for nation in self.founding_dates.keys():
#       # Turn the nation into its underscored representation.
#       _parsed_nation = nation.replace(' ', '_')
#
#       # Search through filename.
#       if _parsed_nation in filename and _parsed_nation not in _nation_tracker:
#          # Append to nation tracker.
#          _nation_tracker.append(_parsed_nation)
#
#          # Add items to the lists.
#          os.rename(path_item, os.path.join(path, (_parsed_nation + '.svg')))
#          _save_image_list.append(os.path.join(path, (_parsed_nation + '.png')))
#          _svg_images_parsed.append(os.path.join(path, (_parsed_nation + '.svg')))
#          break

