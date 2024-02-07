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


# Work started on 2022-04-28


import logging
import gettext
import threading

VERSION = "0.1.6"
"""The program version of luna_lms.
"""

LOGGER = logging.getLogger("luna_lms")
"""The general logger for luna_lms.
"""

LOGGER.setLevel(logging.DEBUG)

STDERR_FORMATTER = logging.Formatter("luna_lms [{levelname}] {funcName}(): {message} (l.{lineno})", style="{")
"""A logging formatter for STDERR output.
"""

STDERR_HANDLER = logging.StreamHandler()
"""A logging handler for STDERR output.
"""

STDERR_HANDLER.setFormatter(STDERR_FORMATTER)
#FILE_HANDLER = logging.FileHandler("luna_lms.log", encoding="utf8")
#FILE_HANDLER.setFormatter(STDERR_FORMATTER)
LOGGER.addHandler(STDERR_HANDLER)
#LOGGER.addHandler(FILE_HANDLER)
#
# Now user LOGGER.debug(msg), LOGGER.info(msg), LOGGER.warning(msg),
# LOGGER.error(msg), LOGGER.critical(msg)

gettext.install('luna_lms')

WRITE_LOCK = threading.Lock()
"""A lock to enforce only one thread can write data.
"""

ADDITIONAL_CONFIG = {}
"""Entries to this dict will be added to the config for CherryPy.
"""

class MODI:
	"""Class to define the valid presentation modes for learning content.
	"""
	pass

MODI.TEXT = "text"
MODI.TEXT_ZUSATZ = "text_zusatz"
MODI.BILD = "bild"
MODI.TEXT_BILD = "text_bild"

# Compiled from https://en.wikipedia.org/wiki/Comparison_of_web_browsers#Image_format_support
#
IMAGE_TYPES = ("image/jpeg",
				"image/gif",
				"image/webp",
				"image/png",
				"image/svg+xml",
				"image/bmp")
"""The MIME types of files that luna_lms will recognize as images.
"""

def check_title(s):
	"""Check if a string conforms to the title rule:
	   At least one character.
	   Alphanumeric characters, spaces, hyphens, underscore.
	   Starts with an alphanumeric character.
	   
	   Returns an empty string when the string conforms,
	   else an error message.
	"""

	LOGGER.debug("check_title(s = '{}')".format(s))

	# Remove leading and trailing whitespace
	#
	s = s.strip()

	if not len(s):
		return _("Das Feld war leer. Bitte mach eine Eingabe.")

	if not s[0].isalnum():
		return _("Ungültiger Name '{}': Der Name muss mit einem Buchstaben oder einer Zahl beginnen.").format(s)

	# Remove allowed characters, the remainder should be alnum
	#
	if not s.replace(" ", "").replace("-", "").replace("_", "").isalnum():

		invalid = []

		for character in s.replace(" ", "").replace("-", "").replace("_", ""):

			if not character.isalnum() and character not in invalid:

				invalid.append(character)
	
		return _("Ungültige Zeichen in der Eingabe: {}").format(", ".join(invalid))

	return ""
