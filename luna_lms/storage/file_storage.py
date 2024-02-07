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
from luna_lms import ADDITIONAL_CONFIG
from luna_lms.storage.storage import Storage
import sys
import os

class FileStorage(Storage):
	"""This class stores data in a folder hierarchy on disk.
	"""

	def __init__(self):
		"""Initialise FileStorage.
		"""

		LOGGER.info("Initialising FileStorage in working directory {}".format(sys.path[0]))

		# Note: This exposes the whole courses directory world-readable,
		# once the file URLs are known. Directories are not listed.
		#
		config = {"/static" : {"tools.staticdir.on" : True,
								"tools.staticdir.dir" : os.path.join(os.getcwd(),
																		"Kurse")}}

		# A simple update may overwrite settings.
		# So, update sub-dicts first.
		#
		keys_to_pop = []

		for key in config.keys():

			if key in ADDITIONAL_CONFIG.keys():

				ADDITIONAL_CONFIG[key].update(config[key])

				keys_to_pop.append(key)

		for key in keys_to_pop:

			config.pop(key)

		ADDITIONAL_CONFIG.update(config)

		return

	def find_courses(self):
		"""Search for courses, and return a dict mapping their titles to their IDs, and IDs to titles.
		"""

		# TODO: This is a very expensive operation. Titles and IDs should be cached somehow.

		result = {}

		# Yes, Unix-style paths are okay for glob
		#
		for path in glob.glob("Kurse/*"):

			title = path.replace("Kurse/", "")

			json_path = os.path.join("Kurse", title, title + ".json")

			if os.path.exists(json_path):

				with open(json_path, mode="rt", encoding="utf8") as f:

					LOGGER.debug("Attempting to parse " + json_path)

					# We're using type UUID, not string, here, since,
					# in theory, one could use an UUID as a title,
					# which would confuse the dict.
					# Doing it that way, it's always mapping of
					# UUID -> string, and string -> UUID.
					#
					identifier = uuid.UUID(json.loads(f.read())["identifier"])

					result[title] = identifier
					result[identifier] = title

		return result

	def get_image(self, course_title, learning_content_id):
		"""Return the URI to the first image found in the learning content, or an empty string.
		"""

		LOGGER.debug("get_image(course_title = '{}', learning_content_id = '{}')".format(course_title, learning_content_id))

		image_path = ""

		# We do not trust file suffixes, and use the MIME type
		# as stored in the meta file.

		meta_paths = glob.glob("Kurse/"
								+ course_title
								+ "/Lern-Inhalte/"
								+ learning_content_id
								+ "/*.meta")

		while len(meta_paths) and not image_path:

			current_path = meta_paths.pop()

			with open(current_path, mode="rt", encoding="utf8") as f:

				LOGGER.debug("Attempting to parse " + current_path)

				meta_data = json.loads(f.read())

				# TODO: Don't inconsistently check for required fields. Either they are there, or we are in trouble, and should fail and report.
				#
				if "format" in meta_data and meta_data["format"] in IMAGE_TYPES:

					# Fix for URI usage
					#
					image_path = current_path.replace("Kurse/", "/static/").replace(".meta", "")

		return image_path

	def get_html(self, course_title, learning_content_id):
		"""Return the content of the first HTML file found in the learning content, or an empty string.
		"""

		LOGGER.debug("get_html(course_title = '{}', learning_content_id = '{}')".format(course_title, learning_content_id))

		html = ""

		# Yes, Unix-style paths are okay for glob.
		#
		html_paths = glob.glob("Kurse/"
								+ course_title
								+ "/Lern-Inhalte/"
								+ learning_content_id
								+ "/*.html")

		if len(html_paths):

			with open(html_paths[0], mode="rt", encoding="utf8") as f:

				html = f.read()

		return html

	def get_directory(self, course_title, learning_content_id):
		"""Return a tuple (directory_name, html) with the name of the first directory found in the learning content, and the content of the first HTML file found in there.
		   Both elements may be empty.
		"""

		LOGGER.debug("get_directory(course_title = '{}', learning_content_id = '{}')".format(course_title, learning_content_id))

		directory_name = ""

		directories = [os.path.split(path)[1] for path in glob.glob("Kurse/"
																	+ course_title
																	+ "/Lern-Inhalte/"
																	+ learning_content_id
																	+ "/*")
						if os.path.isdir(path)]

		if len(directories):

			directory_name = directories[0]

		html = ""

		if directory_name:

			# Yes, Unix-style paths are okay for glob.
			#
			html_paths = glob.glob("Kurse/"
									+ course_title
									+ "/Lern-Inhalte/"
									+ learning_content_id
									+ "/"
									+ directory_name
									+ "/*.html")

			if len(html_paths):

				with open(html_paths[0], mode="rt", encoding="utf8") as f:

					html = f.read()

		return (directory_name, html)

	def get_course_titles(self):
		"""Return a list of titles of existing courses.
		"""

		return [os.path.split(path)[1] for path in glob.glob("Kurse/*")
				if os.path.isdir(path)]

	def get_learning_contents(self, course_title):
		"""Return a list of learning contents identifiers for a course in arbitrary order.
		"""

		# Yes, Unix-style paths are okay for glob.
		#
		return [os.path.split(path)[1] for path in glob.glob("Kurse/"
																+ course_title
																+ "/Lern-Inhalte/*")
				if os.path.isdir(path)]

	def get_learning_contents_ordered(self, course_title):
		"""Return a list of learning contents identifiers for a course in order.
		"""

		json_path = os.path.join("Kurse",
									course_title,
									course_title + ".json")

		with open(json_path, mode="rt", encoding="utf8") as f:

			LOGGER.debug("Attempting to parse " + json_path)

			return json.loads(f.read())["Lern-Inhalte"]

	def get_learning_contents_titles(self, course_title):
		"""Return a dictionary mapping learning contents identifiers to their titles.
		"""

		kurs = {}

		json_path = os.path.join("Kurse",
									course_title,
									course_title + ".json")

		with open(json_path, mode="rt", encoding="utf8") as f:

			LOGGER.debug("Attempting to parse " + json_path)

			kurs = json.loads(f.read())

		# TODO: This is super expensive and must be replaced.
		#
		lerninhalte = {}

		for existing_id in kurs["Lern-Inhalte"]:

			json_path = os.path.join(os.path.join("Kurse",
											course_title,
											"Lern-Inhalte",
											existing_id,
											existing_id + ".meta"))

			if os.path.exists(json_path):

				with open(json_path, mode="rt", encoding="utf8") as f:

					LOGGER.debug("Attempting to parse " + json_path)

					lerninhalte[existing_id] = json.loads(f.read())["title"]
			
		return lerninhalte

	def get_variants(self, course_title, learning_content_id):
		"""Return a list of all variants for a learning content in a course.
		"""

		# First, consider all files variants that have an extension
		# and a meta file.
		#
		# Yes, Unix-style paths are okay for glob.
		#
		variantn = [os.path.splitext(os.path.split(path)[1])[0] for path in glob.glob("Kurse/"
															+ course_title
															+ "/Lern-Inhalte/"
															+ learning_content_id
															+ "/*.meta")
							if "." in os.path.splitext(os.path.split(path)[1])[0]]

		# Add variants that are a directory

		variantn.extend([os.path.split(path)[1] for path in glob.glob("Kurse/"
															+ course_title
															+ "/Lern-Inhalte/"
															+ learning_content_id
													   		+ "/*")
								if os.path.isdir(path)])

		return variantn

	def get_variants_ids(self, course_title, learning_content_id):
		"""Return a list of identifiers of all variants for a learning content in a course.
		"""

		existing_ids = []

		# TODO: This is super expensive and must be replaced.

		# Yes, Unix-style paths are okay for glob.
		#
		meta_paths = glob.glob("Kurse/"
								+ course_title
								+ "/Lern-Inhalte/"
								+ learning_content_id
								+ "/*.meta")

		# Also catch meta files in directories
		#
		meta_paths.extend(glob.glob("Kurse/"
								+ course_title
								+ "/Lern-Inhalte/"
								+ learning_content_id
								+ "/*"
								+ "/*.meta"))

		for path in meta_paths:

			with open(path, mode="rt", encoding="utf8") as f:

					LOGGER.debug("Attempting to parse " + path)

					existing_ids.append(json.loads(f.read())["identifier"])

		return existing_ids

	def get_variant_metadata(self, course_title, learning_content_id, variant):
		"""Return the metadata of the variant as a dict.

		Example:
		
		{
			"identifier": "aa2835f3-c3e4-495a-bea8-3e283979e6e6",
			"format": "text/html",
			"type": "variant"
		}
		"""

		meta_data = {}

		meta_path = os.path.join("Kurse",
									course_title,
									"Lern-Inhalte",
									learning_content_id,
									variant + ".meta")

		if os.path.isdir(os.path.join("Kurse",
									course_title,
									"Lern-Inhalte",
									learning_content_id,
									variant)):

			meta_path = os.path.join("Kurse",
									course_title,
									"Lern-Inhalte",
									learning_content_id,
									variant,
									variant + ".meta")

		with open(meta_path, mode="rt", encoding="utf8") as f:

			LOGGER.debug("Attempting to parse " + meta_path)

			meta_data = json.loads(f.read())

		return meta_data

	def delete_variant(self, course_title, learning_content_id, variant_id):
		"""Attempt to delete the variant identified by variant_id.
		   Return a message in case of success.
		"""

		message = ""

		# First, consider all files variants that have an extension
		# and a meta file.
		#
		# Yes, Unix-style paths are okay for glob.
		#
		variantn = [os.path.splitext(os.path.split(path)[1])[0] for path in glob.glob("Kurse/"
													+ course_title
													+ "/Lern-Inhalte/"
													+ learning_content_id
													+ "/*.meta")
							if "." in os.path.splitext(os.path.split(path)[1])[0]]

		for variant in variantn:

			# Get metadata from meta file

			meta_data = {}

			meta_path = os.path.join("Kurse",
										course_title,
										"Lern-Inhalte",
										learning_content_id,
										variant + ".meta")

			with open(meta_path, mode="rt", encoding="utf8") as f:

				LOGGER.debug("Attempting to parse " + meta_path)

				meta_data = json.loads(f.read())

			if meta_data["identifier"] == variant_id:

				path = os.path.join("Kurse",
										course_title,
										"Lern-Inhalte",
										learning_content_id,
										variant)

				LOGGER.info("Removing file {}".format(path))

				os.remove(path)

				message = _("Datei {} gelöscht.").format(path)

				path += ".meta"

				LOGGER.info("Removing meta file {}".format(path))

				os.remove(path)

				message += '<br>'
				message += _("Datei {} gelöscht.").format(path)

		# Use message as an indicator whether we found something to delete
		#
		if not message:

			# Check variants that are a directory

			variantn = [os.path.split(path)[1] for path in glob.glob("Kurse/"
														+ course_title
														+ "/Lern-Inhalte/"
														+ learning_content_id
														+ "/*")
								  if os.path.isdir(path)]

			for variant in variantn:

				# Get metadata from meta file

				meta_data = {}

				meta_path = os.path.join("Kurse",
												course_title,
												"Lern-Inhalte",
												learning_content_id,
												variant,
												variant + ".meta")

				with open(meta_path, mode="rt", encoding="utf8") as f:

					LOGGER.debug("Attempting to parse " + meta_path)

					meta_data = json.loads(f.read())

				if meta_data["identifier"] == variant_id:

					path = os.path.join("Kurse",
											course_title,
											"Lern-Inhalte",
											learning_content_id,
											variant)

					LOGGER.info("Removing directory {} and all of its contents".format(path))

					shutil.rmtree(path)

					message = _("Verzeichnis der Variante {} gelöscht.").format(path)

		return message

	def delete_course(self, course_title):
		"""Delete the course identified by course_title.
		   Return a message in case of success.
		"""

		path = os.path.join("Kurse", course_title)

		LOGGER.info("Removing directory {} and all of its contents".format(path))

		shutil.rmtree(path)

		return _("Kurs {} gelöscht.").format(path)

	def delete_learning_content(self, course_title, learning_content_id):
		"""Delete the learning content identified by learning_content_id.
		   Return a message in case of success.
		"""

		path = os.path.join("Kurse",
								course_title,
								"Lern-Inhalte",
								learning_content_id)

		LOGGER.info("Removing directory {} and all of its contents".format(path))

		shutil.rmtree(path)

		# The learning content is still referenced in the course, so remove it there

		kurs = {}

		json_path = os.path.join("Kurse",
									course_title,
									course_title + ".json")

		with open(json_path, mode="rt", encoding="utf8") as f:

			LOGGER.debug("Attempting to parse " + json_path)

			kurs = json.loads(f.read())

		LOGGER.info("Removing learning content {} from course '{}'".format(learning_content_id, course_title))

		kurs["Lern-Inhalte"].remove(str(learning_content_id))

		# Note that this is still not thread or multi process safe, as
		# it ignores the current state of the file on disk or in
		# parallel threads / processes.
		#
		with WRITE_LOCK:

			with open(os.path.join("Kurse",
									course_title,
									course_title + ".json"),
						mode="wt",
						encoding="utf8") as f:

				f.write(json.dumps(kurs, indent = "\t"))

		return _("Lern-Inhalt {} und Verzeichnis {} gelöscht.").format(learning_content_id, path)

	def write_course(self, title):
		"""Create a new course.
		   Return a message indicating success or failure.
		"""

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

	def write_learning_content(self, course_title, learning_content_title):
		"""Create a new learning content.
		   Return a message indicating success or failure.
		"""

		message = ""

		new_id = uuid.uuid4()

		# UUIDs are almost guaranteed to be never identical, but, you
		# know ... almost.
		#
		while new_id in [uuid.UUID(existing_id) for existing_id in self.get_learning_contents(course_title)]:

			new_id = uuid.uuid4()

		# NOTE: While courses are stored by title, learning contents
		# are stored by identifier. So, technically, we dont have
		# to check for duplicates. Which allows for learning contents with
		# the same title. Which will probably confuse users. Let's see
		# if they complain.
		#
		LOGGER.info("Creating directory structure and files for learning content '{}' with id {}".format(learning_content_title, new_id))

		# Note that this is still not thread or multi process safe, as
		# it ignores the current state of the file on disk or in
		# parallel threads / processes.
		#
		with WRITE_LOCK:

			os.mkdir(os.path.join("Kurse",
									course_title,
									"Lern-Inhalte",
									str(new_id)))

			with open(os.path.join("Kurse",
									course_title,
									"Lern-Inhalte",
									str(new_id),
									str(new_id) + ".meta"),
						mode="wt",
						encoding="utf8") as f:

				# Note that {{ and }} are escapes for
				# literal { and } in format strings.
				#
				f.write("""{{
"identifier": "{}",
"type": "Lern-Inhalt",
"title": "{}"
}}
""".format(str(new_id), learning_content_title))

			kurs = {}

			json_path = os.path.join("Kurse",
										course_title,
										course_title + ".json")

			with open(json_path, mode="rt", encoding="utf8") as f:

				LOGGER.debug("Attempting to parse " + json_path)

				kurs = json.loads(f.read())

			kurs["Lern-Inhalte"].append(str(new_id))

			with open(json_path, mode="wt", encoding="utf8") as f:

				f.write(json.dumps(kurs, indent = "\t"))

		LOGGER.info("Directory structure created, and id added to course.")
		message = _("Lern-Inhalt angelegt und zum Kurs hinzugefügt.")

		return message

	def write_learning_contents_list(self, course_title, learning_contents_list):
		"""Write an re-ordered list of learning contents into the course.
		   Return a message indicating success or failure.
		"""

		# All learning contents in the list must exist.
		# Apart from that, we accept any order.

		existing_lerninhalte = self.get_learning_contents(course_title)

		# Right now, lerninhalte is a string representation of a list,
		# so convert it to an actual list.
		#
		# List parsing is a smart hint from https://www.geeksforgeeks.org/python-convert-a-string-representation-of-list-into-list/
		#
		# Replace the ' quotes by " before.
		#
		learning_contents_list = json.loads(learning_contents_list.replace("'", '"'))

		for requested_lerninhalt in learning_contents_list:

			if requested_lerninhalt not in existing_lerninhalte:

				error = _("Umsortierung nicht möglich: Den Lern-Inhalt '{}' gibt es nicht mehr.").format(requested_lerninhalt)

				LOGGER.error(error)

				raise cherrypy.HTTPError(500, error)

		kurs = {}

		json_path = os.path.join("Kurse",
									course_title,
									course_title + ".json")

		with open(json_path, mode="rt", encoding="utf8") as f:

			LOGGER.debug("Attempting to parse " + json_path)

			kurs = json.loads(f.read())

		kurs["Lern-Inhalte"] = learning_contents_list

		# Note that this is still not thread or multi process safe, as
		# it ignores the current state of the file on disk or in
		# parallel threads / processes.
		#
		with WRITE_LOCK:

			with open(os.path.join("Kurse",
									course_title,
									course_title + ".json"),
						mode="wt",
						encoding="utf8") as f:

				f.write(json.dumps(kurs, indent = "\t"))

		return _("Lern-Inhalte umsortiert.")

	def write_variant(self, course_id, learning_content_id, content, filename):
		"""Write a variant consisting of a single or multiple files, and create the according meta files.

		   Return the MIME type of the last file written.
		"""

		LOGGER.info("Creating variant with filename(s) '{}'".format(filename))

		course_title = self.find_courses()[uuid.UUID(course_id)]

		# Note that this is still not thread or multi process safe, as
		# it ignores the current state of the file on disk or in
		# parallel threads / processes.
		#
		with WRITE_LOCK:

			if content.__class__ == str:

				# Verbatim HTML sent via form.

				with open(os.path.join("Kurse",
										course_title,
										"Lern-Inhalte",
										learning_content_id,
										filename),
							mode="wt",
							encoding="utf8") as f:

					f.write(content)

			elif filename.__class__ == list:

				# Uploaded multiple files in a directory.

				# Create directory, guessing the name from the first
				# file. Filenames should be directory + filename .

				directory_path = os.path.join("Kurse",
										course_title,
										"Lern-Inhalte",
										learning_content_id,
										os.path.split(filename[0])[0])

				os.mkdir(directory_path)

				# Now for the files.

				for upload in content:

					with open(os.path.join(directory_path,
											os.path.basename(upload.filename)),
								mode="wb") as f:

						# Taken from https://docs.cherrypy.dev/en/latest/_modules/cherrypy/tutorial/tut09_files.html#FileDemo.upload
						#
						data = upload.file.read(8192)

						while data:

							f.write(data)

							data = upload.file.read(8192)

			else:

				# Uploaded single file.

				with open(os.path.join("Kurse",
										course_title,
										"Lern-Inhalte",
										learning_content_id,
										filename),
							mode="wb") as f:

					# Taken from https://docs.cherrypy.dev/en/latest/_modules/cherrypy/tutorial/tut09_files.html#FileDemo.upload
					#
					data = content.file.read(8192)

					while data:

						f.write(data)

						data = content.file.read(8192)

		# Now create the meta file(s).

		existing_ids = self.get_variants_ids(course_title, learning_content_id)

		if filename.__class__ == list:

			# Handle files from directory upload

			new_id = uuid.uuid4()

			# UUIDs are almost guaranteed to be never identical, but, you
			# know ... almost.
			#
			while new_id in existing_ids:

				new_id = uuid.uuid4()

			existing_ids.append(new_id)

			directory = os.path.split(filename[0])[0]

			with WRITE_LOCK:

				with open(os.path.join("Kurse",
										course_title,
										"Lern-Inhalte",
										learning_content_id,
										directory,
										directory + ".meta"),
							mode="wt",
							encoding="utf8") as f:

					# Note that {{ and }} are escapes for
					# literal { and } in format strings.
					#
					f.write("""{{
"identifier": "{}",
"format": "inode/directory",
"type": "Variante"
}}
""".format(new_id))

			# Now for the files.

			for upload in content:

				new_id = uuid.uuid4()

				while new_id in existing_ids:

					new_id = uuid.uuid4()

				existing_ids.append(new_id)

				file_format = upload.content_type

				with WRITE_LOCK:

					with open(os.path.join("Kurse",
											course_title,
											"Lern-Inhalte",
											learning_content_id,
											os.path.split(filename[0])[0],
											os.path.basename(upload.filename) + ".meta"),
								mode="wt",
								encoding="utf8") as f:

						# Note that {{ and }} are escapes for
						# literal { and } in format strings.
						#
						f.write("""{{
"identifier": "{}",
"format": "{}",
"type": "Datei"
}}
""".format(new_id, file_format))

		else:

			# Handle single file

			new_id = uuid.uuid4()

			while new_id in existing_ids:

				new_id = uuid.uuid4()

			file_format = "text/html"

			if content.__class__ != str:

				file_format = content.content_type

			with WRITE_LOCK:

				with open(os.path.join("Kurse",
										course_title,
										"Lern-Inhalte",
										learning_content_id,
										filename + ".meta"),
							mode="wt",
							encoding="utf8") as f:

					# Note that {{ and }} are escapes for
					# literal { and } in format strings.
					#
					f.write("""{{
"identifier": "{}",
"format": "{}",
"type": "Variante"
}}
""".format(new_id, file_format))

		LOGGER.info("File(s) written.")

		return file_format
