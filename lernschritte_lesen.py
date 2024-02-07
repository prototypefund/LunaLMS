import argparse
import sys
import sqlite3
import collections
from luna_lms.storage.sqlite_storage import IdTitle

class DummyLogger:

	def debug(self, message):

		print(message, file = sys.stderr)


LOGGER= DummyLogger()


def parse_group(current_level, current_parent, cursor, all_parents):
	"""Scan the current group of Lerninhalte, build output, and recurse into subgroups.
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
			result[key].update(parse_group(current_level,
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

def build_steps(connection):

	result = collections.OrderedDict()

	cursor = connection.cursor()

	cursor.execute("PRAGMA foreign_keys = ON")

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
	result.update(parse_group(current_level,
							current_parent,
							cursor,
							all_parents))

	LOGGER.debug("All elements processed")

	return result


def main():
	"""Main function, for IDE convenience.
	"""

	parser = argparse.ArgumentParser(prog = "lernschritte_lesen.py",
										description = "Lern-Schritte aus sqlite parsen und als geschachtelte HTML-Liste ausgeben")

	parser.add_argument("sqlite_datei")

	args = parser.parse_args()

	LOGGER.debug("Connecting to database")

	connection = sqlite3.connect(args.sqlite_datei)

	result = build_steps(connection)

	LOGGER.debug("Closing database connection")

	connection.close()

	LOGGER.debug("Result:")

	log_recursive(result)

	html = '''<html>
	<head>
		<title>Luna Lernschritte</title>
	</head>
	<body>
	<h1>Luna Lernschritte</h1>
'''

	html += '<ul>\n'

	# 0: "    " * current_level,
	# 1: (current_level - 1) * 4,

	template = '''{0}<li style="list-style:none;padding-left:{1}em">
{0}    {2}{3}. <a href="{4}">{5}</a>
{0}</li>
'''

	html += '</ul>\n'

	html += '''	</body>
</html>'''

	return result

def log_recursive(d, level = 0, prefix = ""):

	count = 1

	for key in d.keys():

		LOGGER.debug("{}{}{}. {}".format("    " * level, prefix, count, key))

		if d[key]:

			log_recursive(d[key], level + 1, "{}{}.".format(prefix, count))

		count += 1

if __name__ == "__main__":

	print(main())
