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


from luna_lms import VERSION, LOGGER
from luna_lms.storage.storage import Storage
import sys
import os.path
import cherrypy
from cherrypy.process.plugins import SignalHandler
import glob
import sqlite3
import threading
import uuid
import collections


IdTitle = collections.namedtuple('IdTitle', ['identifier', 'title'])


class SQLiteStorage(Storage):
	"""This class stores data in a sqlite database on disk.

	SQLiteStorage.connections
		A dict mapping UUID ids of a course to a tuple (sqlite3.Connection,
		threading.Lock). By convention, the Lock must be acquired to write
		data.
	"""

	def __init__(self):
		"""Initialise SQLiteStorage.
		"""

		LOGGER.info("Initialising SQLiteStorage in working directory {}".format(sys.path[0]))

		# We use persistent connections instead of persistent cursors because of
		# https://stackoverflow.com/a/54410755 :
		# "If you're aiming to support DB-API 2.0 compatible drivers, I suggest
		# just use the cursor() method to create a cursor for every query
		# execution. I would recommend to NEVER have a singleton or shared
		# cursor."
		#
		self.connections = {}

		if not os.path.isdir("courses"):

			LOGGER.warning("Directory 'courses' does not exist, creating")

			os.mkdir("courses")

		# Taken from https://stackoverflow.com/a/65974899
		#
		LOGGER.debug("Adding signal handler to close connections at application quit")

		signalhandler = SignalHandler(cherrypy.engine)
		
		signalhandler.handlers['SIGTERM'] = self.close_sqlite_connections
		signalhandler.handlers['SIGHUP'] = self.close_sqlite_connections
		signalhandler.handlers['SIGQUIT'] = self.close_sqlite_connections
		signalhandler.handlers['SIGINT'] = self.close_sqlite_connections

		signalhandler.subscribe()

		return

	def find_courses(self):
		"""Search for courses, and return a dict mapping their titles to their IDs, and IDs to titles.

		Found courses with a reqired MAJOR Luna version larger than the current one will be omitted.
		"""

		# Yes, Unix-style paths are okay for glob
		#
		course_files = glob.glob("courses/*.sqlite")

		if not course_files:

			LOGGER.info("No sqlite course files in directory 'courses'")

			return {}

		course_dict = {}

		for course_file in course_files:

			connection = sqlite3.connect(course_file, check_same_thread = False)

			cursor = connection.cursor()

			cursor.execute("PRAGMA foreign_keys = ON")

			result = cursor.execute('SELECT identifier,title FROM course')

			identifier, title = result.fetchone()

			# We're using type UUID, not string, here, since,
			# in theory, one could use an UUID as a title,
			# which would confuse the dict.
			# Doing it that way, it's always mapping of
			# UUID -> string, and string -> UUID.
			#
			identifier = uuid.UUID(identifier)

			LOGGER.debug("Course found: '{}', identifier == {}".format(title, identifier))

			if identifier in self.connections:

				LOGGER.debug("Course {} already in connections, returning and closing temporary connection".format(identifier))

				course_dict[identifier] = title
				course_dict[title] = identifier

				connection.close()

			else:

				self.connections[identifier] = (connection, threading.Lock())

				LOGGER.debug("Checking course {} for compatibility".format(identifier))

				# String is "Luna LMS MAJOR.MINOR.PATCH"
				#
				required_version = self.get_course_metadata(identifier)["requires"].split("Luna LMS ")[1]

				if int(required_version.split(".")[0]) > int(VERSION.split(".")[0]):

					msg = "Can not use found course {} ('{}'): course requires Luna LMS version {}, but the running version is {}"

					LOGGER.warning(msg.format(identifier,
												title,
												required_version,
												VERSION))

					del self.connections[identifier]

				else:
					course_dict[identifier] = title
					course_dict[title] = identifier

		return course_dict

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

		meta_data = {}

		if course.__class__ is not uuid.UUID:

			LOGGER.error("Only UUIDs are currently supported as a course identifier, received class is {}".format(course.__class__))

			return meta_data

		if course not in self.connections.keys():

			self.find_courses()

			if course not in self.connections.keys():

				LOGGER.error("Course id {} not found in available courses".format(course))

				return meta_data

		cursor = self.connections[course][0].cursor()

		keys = ["title",
				"description",
				"relation",
				"created",
				"modified",
				"dateAccepted",
				"issued",
				"contributor",
				"requires"]

		result = cursor.execute('SELECT {} FROM course;'.format(",".join(keys)))

		result = list(result.fetchone())

		for key in keys:

			meta_data[key] = result.pop(0)

		return meta_data

	def get_html(self, course, learning_content_id):
		"""Return the content of the first HTML file found in the learning content, or an empty string.

		course can be an identifier or the course title. An identifier is
		recommended, since titles may not be unique.
		"""

		content = ""

		if course.__class__ is not uuid.UUID:

			LOGGER.error("Only UUIDs are currently supported as a course identifier, received class is {}".format(course.__class__))

			return content

		# Better check this before we pass unsafe input to a SQL query.
		#
		if len(learning_content_id) != 6 or not learning_content_id.isalnum():

			LOGGER.error("Malformed identifier: '{}'".format(learning_content_id))

			return content

		if course not in self.connections.keys():

			self.find_courses()

			if course not in self.connections.keys():

				LOGGER.error("Course id {} not found in available courses".format(course))

				return result

		cursor = self.connections[course][0].cursor()

		query = '''SELECT variants.data from
						variants,
						mapping,
						steps
			   		WHERE
						steps.identifier = "{}"
						and
						steps.content_id = mapping.content_id
						and
						mapping.variant_id = variants.identifier
						and
						variants.format = "text/html"'''

		result = cursor.execute(query.format(learning_content_id))

		result = result.fetchone()

		if result:

			content = result[0]

		return content

	def get_learning_contents_ordered(self, course):
		"""Return a nested OrderedDict of learning content identifiers and titles.

		course can be an identifier or the course title. An identifier is
		recommended, since titles may not be unique.
		"""

		result = collections.OrderedDict()

		if course.__class__ is not uuid.UUID:

			LOGGER.error("Only UUIDs are currently supported as a course identifier, received class is {}".format(course.__class__))

			return result

		if course not in self.connections.keys():

			self.find_courses()

			if course not in self.connections.keys():

				LOGGER.error("Course id {} not found in available courses".format(course))

				return result

		cursor = self.connections[course][0].cursor()

		# Build a list of all steps that are groups,
		# i.e. that are parent to other steps.

		all_parents = []

		command = 'SELECT parent FROM steps WHERE parent is not NULL'

		for row in cursor.execute(command):

			if row not in all_parents:

				all_parents.append(row[0])

		# At the start, there is no parent
		#
		current_parent = None

		# Start level is 1
		#
		current_level = 1

		# Consider all steps of the current group.
		# This will recurse into subgroups as necessary.
		#
		result.update(self.parse_group(current_level,
								current_parent,
								cursor,
								all_parents))

		LOGGER.debug("All elements processed")

		return result

	def parse_group(self, current_level, current_parent, cursor, all_parents):
		"""Scan the current group of learning contents, build output, and recurse into subgroups.

		This method is meant to be called from build_steps().
		"""

		msg = "parse_group(current_level = {}, current_parent = {}, cursor = {}, all_parents = {})"

		LOGGER.debug(msg.format(current_level,
								current_parent,
								cursor.__class__,
								all_parents))

		result = collections.OrderedDict()

		matching_elements = {}

		condition = 'is NULL'

		if current_parent is not None:

			condition = '= "{}"'.format(current_parent)

		command = 'SELECT identifier,title,successor FROM steps WHERE parent ' + condition

		for row in cursor.execute(command):

			matching_elements[row[0]] = {"title": row[1],
											"successor": row[2],
											"group": row[0] in all_parents}

		LOGGER.debug("Found {} matching elements at level {}".format(len(matching_elements), current_level))

		# Find the element in the current group that is not a successor of any other
		# element, and use it as first element

		successors = [value["successor"]
						for value in matching_elements.values()
						if value["successor"] is not None]

		first_element = None

		for identifier in matching_elements.keys():

			if identifier not in successors:

					first_element = identifier

		if first_element:

			msg = "Element {} is not successor of any other element, using as start"

			LOGGER.debug(msg.format(first_element))

		else:

			raise Exception("No starting element found at level {}".format(current_level))

		# Build a ordered list of successors

		identifiers_ordered = []

		current_identifier = first_element

		current_successor = "dummy"

		while current_successor is not None:

			current_successor = matching_elements[current_identifier]["successor"]

			identifiers_ordered.append(current_identifier)

			current_identifier = matching_elements[current_identifier]["successor"]

		count = 1

		# For each element of the ordered list of successors:
		#
		for identifier in identifiers_ordered:

			msg = "Adding element {} (group == {}) to result"

			LOGGER.debug(msg.format(identifier, matching_elements[identifier]["group"]))

			# Add the element to the result
			#
			key = IdTitle(identifier, matching_elements[identifier]["title"])

			result[key] = collections.OrderedDict()

			# If the element is a group:
			#
			if matching_elements[identifier]["group"]:

				LOGGER.debug("Element {} is a group, starting recursion".format(identifier))

				# Increase heirarchy depth
				#
				current_level += 1

				old_parent = current_parent

				# Set the current parent group to the current element
				#
				current_parent = identifier

				# Recurse
				#
				result[key].update(self.parse_group(current_level,
										current_parent,
										cursor,
										all_parents))

				# Restore the former parent
				#
				current_parent = old_parent

				# Decrease heirarchy depth to former depth
				#
				current_level -= 1

				msg = "Recursion done, returning to parent {} at level {}"

				LOGGER.debug(msg.format(current_parent, current_level))

			count += 1

		LOGGER.debug("Returning:\n{}".format(result).replace("), ", "),\n"))

		return result

	def write_course(self, title):
		"""Create a new SQLite database representing the course.
		Return a message indicating success or failure.
		"""
		# !!!

		message = ""

		if not os.path.isdir("Kurse"):

			LOGGER.warning("Directory 'Kurse' does not exist, creating")

			os.mkdir("Kurse")

			LOGGER.info("Copying static CSS to directory 'Kurse'")

			shutil.copyfile("w3.css", os.path.join("Kurse", "w3.css"))

		if os.path.isdir(os.path.join("Kurse", title)):

			LOGGER.warning("course already exists.")
			message = _("Diesen Kurs gibt es schon.")

		else:
			LOGGER.info("Creating directory structure and files for course '{}'".format(title))

			os.mkdir(os.path.join("Kurse", title))
			os.mkdir(os.path.join("Kurse", title, "Lern-Inhalte"))
			os.mkdir(os.path.join("Kurse", title, "Lern-Pfade"))

			# Note that this is still not thread or multi process safe, as
			# it ignores the current state of the file on disk or in
			# parallel threads / processes.
			#
			with WRITE_LOCK:

				with open(os.path.join("Kurse", title, title + ".json"),
							mode="wt",
							encoding="utf8") as f:

					# Note that {{ and }} are escapes for
					# literal { and } in format strings.
					#
					# TODO: This only checks for duplicate names, but not for duplicate UUIDs, as the other functions do
					#
					f.write("""{{
"identifier": "{}",
"type": "Kurs",
"title": "{}",
"Lern-Inhalte": []
}}
""".format(str(uuid.uuid4()), title))

			LOGGER.info("Directory structure created.")
			message = _("Kurs angelegt.")
		
		return message

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

		item = {}

		if course.__class__ is not uuid.UUID:

			LOGGER.error("Only UUIDs are currently supported as a course identifier, received class is {}".format(course.__class__))

			return item

		if course not in self.connections.keys():

			self.find_courses()

			if course not in self.connections.keys():

				LOGGER.error("Course id {} not found in available courses".format(course))

				return meta_data

		cursor = self.connections[course][0].cursor()

		keys = ["path",
				"data",
				"format",
				"description"]

		result = cursor.execute('SELECT {} FROM cache WHERE path = "{}";'.format(",".join(keys), path))

		result = result.fetchone()

		if result:

			result = list(result)

			for key in keys:

				item[key] = result.pop(0)

			# Make sure data always returns bytes
			#
			if item["data"].__class__ == str:

				item["data"] = bytes(item["data"], encoding = "utf-8")

		return item

	def close_sqlite_connections(self):
		"""Close all connections present in SQLiteStorage.connections .
		"""

		# Make a copy to be able to change the dict in the loop
		#
		identifiers = list(self.connections.keys())

		for identifier in identifiers:

			LOGGER.debug("Acquiring Lock for {}".format(identifier))

			self.connections[identifier][1].acquire()
			
			LOGGER.info("Committing, closing and removing sqlite connection for {}".format(identifier))

			# close() does not implicitly commit, so we commit
			# just to be sure.
			#
			self.connections[identifier][0].commit()

			self.connections[identifier][0].close()

			del self.connections[identifier]

		# The handler replaces the original exit routine, so we have to
		# exit manually.
		# See also https://stackoverflow.com/a/8210435
		#
		cherrypy.engine.exit()

		return
