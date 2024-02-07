"""luna_lms – Ein multimodales Lern-Management-System

   Copyright (c) 2022
   Florian Berger <florian.berger@posteo.de>
"""

# This file is part of luna_lms.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


from luna_lms import LOGGER

class Storage:
	"""Prototype class to handle all storage. Should be subclassed by implementations.
	"""

	def find_courses(self):
		"""Search for courses, and return a dict mapping their titles to their IDs, and IDs to titles.
		"""

		LOGGER.warning("Method is not implemented in this class, no action taken")

		return {}

	def get_course_metadata(self, course):
		"""Return the metadata of the course as a dict.

		course can be an identifier or the course title. An identifier is
		recommended, since titles may not be unique.

		Example:
		
		{
			"identifier": "e0f59465-f984-45ef-9b3d-2cf29e9edcd8",
			"title": "Example Title",
			"description": "Example description.",
			"relation": "",
			"created": "2023-08-28",
			"modified": "2023-08-28",
			"dateAccepted": "",
			"issued": "",
			"contributor": "Jane",
			"requires": "Luna LMS 1.0.0",
		}

		"""

		LOGGER.warning("Method is not implemented in this class, no action taken")

		return {}

	def get_image(self, course, learning_content_id):
		"""Return the URI to the first image found in the learning content, or an empty string.

		course can be an identifier or the course title. An identifier is
		recommended, since titles may not be unique.
		"""

		LOGGER.warning("Method is not implemented in this class, no action taken")

		return ""

	def get_html(self, course, learning_content_id):
		"""Return the content of the first HTML file found in the learning content, or an empty string.

		course can be an identifier or the course title. An identifier is
		recommended, since titles may not be unique.
		"""

		LOGGER.warning("Method is not implemented in this class, no action taken")

		return ""

	def get_directory(self, course, learning_content_id):
		"""Return a tuple (directory_name, html) with the name of the first directory found in the learning content, and the content of the first HTML file found in there.
		   Both elements may be empty.

		course can be an identifier or the course title. An identifier is
		recommended, since titles may not be unique.
		"""

		LOGGER.warning("Method is not implemented in this class, no action taken")

		return ("", "")

	def get_course_titles():
		"""Return a list of titles of existing courses.
		"""

		LOGGER.warning("Method is not implemented in this class, no action taken")

		return []

	def get_learning_contents(self, course):
		"""Return a list of learning contents identifiers for a course in arbitrary order.

		course can be an identifier or the course title. An identifier is
		recommended, since titles may not be unique.
		"""

		LOGGER.warning("Method is not implemented in this class, no action taken")

		return []

	def get_learning_contents_ordered(self, course):
		"""Return a list of learning contents identifiers for a course in order.

		course can be an identifier or the course title. An identifier is
		recommended, since titles may not be unique.
		"""

		LOGGER.warning("Method is not implemented in this class, no action taken")

		return []

	def get_learning_contents_titles(self, course):
		"""Return a dictionary mapping learning contents identifiers to their titles.

		course can be an identifier or the course title. An identifier is
		recommended, since titles may not be unique.
		"""

		LOGGER.warning("Method is not implemented in this class, no action taken")

		return {}

	def get_variants(self, course, learning_content_id):
		"""Return a list of all variants for a learning content in a course.

		course can be an identifier or the course title. An identifier is
		recommended, since titles may not be unique.
		"""

		LOGGER.warning("Method is not implemented in this class, no action taken")

		return []

	def get_variants_ids(self, course, learning_content_id):
		"""Return a list of identifiers of all variants for a learning content in a course.

		course can be an identifier or the course title. An identifier is
		recommended, since titles may not be unique.
		"""

		LOGGER.warning("Method is not implemented in this class, no action taken")

		return []

	def get_variant_metadata(self, course, learning_content_id, variant):
		"""Return the metadata of the variant as a dict.

		course can be an identifier or the course title. An identifier is
		recommended, since titles may not be unique.

		Example:
		
		{
			"identifier": "aa2835f3-c3e4-495a-bea8-3e283979e6e6",
			"format": "text/html",
			"type": "variant"
		}
		"""

		LOGGER.warning("Method is not implemented in this class, no action taken")

		return {}

	def delete_variant(self, course, learning_content_id, variant_id):
		"""Attempt to delete the variant identified by variant_id.
		Return a message in case of success.

		course can be an identifier or the course title. An identifier is
		recommended, since titles may not be unique.
		"""

		LOGGER.warning("Method is not implemented in this class, no action taken")

		return ""

	def delete_course(self, course):
		"""Delete the course identified by course.

		course can be an identifier or the course title. An identifier is
		recommended, since titles may not be unique.

		Return a message in case of success.
		"""

		LOGGER.warning("Method is not implemented in this class, no action taken")

		return ""

	def delete_learning_content(self, course, learning_content_id):
		"""Delete the learning content identified by learning_content_id.

		course can be an identifier or the course title. An identifier is
		recommended, since titles may not be unique.

		Return a message in case of success.
		"""

		LOGGER.warning("Method is not implemented in this class, no action taken")

		return ""

	def write_course(self, title):
		"""Create a new course.
		Return a message indicating success or failure.
		"""

		LOGGER.warning("Method is not implemented in this class, no action taken")

		return ""

	def write_learning_content(self, course, learning_content_title):
		"""Create a new learning content.

		course can be an identifier or the course title. An identifier is
		recommended, since titles may not be unique.

		Return a message indicating success or failure.
		"""

		LOGGER.warning("Method is not implemented in this class, no action taken")

		return ""

	def write_learning_contents_list(self, course, learning_contents_list):
		"""Write an re-ordered list of learning contents into the course.

		course can be an identifier or the course title. An identifier is
		recommended, since titles may not be unique.

		Return a message indicating success or failure.
		"""

		LOGGER.warning("Method is not implemented in this class, no action taken")

		return ""

	def write_variant(self, course, learning_content_id, content, filename):
		"""Write a variant consisting of a single or multiple files, and create the according meta files.

		course can be an identifier or the course title. An identifier is
		recommended, since titles may not be unique.

		Return the MIME type of the last file written.
		"""

		LOGGER.warning("Method is not implemented in this class, no action taken")

		return ""

	def get_cached_item(self, course, path):
		"""Return an item from the course's cache as a dict.

		course can be an identifier or the course title. An identifier is
		recommended, since titles may not be unique.

		Example:
		
		{
			"path": "square.svg",
			"data": bytes('<?xml version="1.0" encoding="UTF-8" standalone="no"?><svg width="512" height="512" viewBox="0 0 135.46666 135.46667" version="1.1" id="svg5" xmlns="http://www.w3.org/2000/svg" xmlns:svg="http://www.w3.org/2000/svg"><defs id="defs2" /><g id="layer1"><rect style="fill:#ba2bcd;fill-opacity:1;stroke:none;stroke-width:0.187088;stroke-linecap:square;stroke-linejoin:round" id="rect286" width="95.789398" height="95.789398" x="-47.894699" y="47.894699" transform="rotate(-45)" /></g></svg>', encoding = "utf-8"),
			"format": "image/svg+xml",
			"description": "A violet square, balancing on a corner."
		}
		"""

		LOGGER.warning("Method is not implemented in this class, no action taken")

		return {}
