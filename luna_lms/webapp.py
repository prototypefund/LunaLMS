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
from luna_lms import VERSION
from luna_lms import MODI
from luna_lms.storage import SQLiteStorage
import cherrypy
import subprocess
import os.path
import uuid

try:
	fossil_status = subprocess.run(["fossil", "info"], capture_output=True, text=True)
	items = dict([line.split(":", maxsplit=1)
				  for line in fossil_status.stdout.splitlines()
				  if line.find(":") > -1])
	VERSION += "+{}.{}".format(items["tags"].strip()[:3], items["checkout"].strip()[:6])
except:
	pass

# L is letter #12, U is #21 in the alphabet.
#
#PORT = 1221
PORT = 10064
"""The TCP port luna_lms will listen on.
"""

THREADS = 4
""" The number of simultaneous CherryPy server threads.
"""

AUTORELOAD = True
"""Flag whether CherryPy should watch the source file, and reload upon changes.
Should be disabled for production use.
"""

CSS = '''
/* "Bunny Fonts is an open-source, privacy-first web font platform designed to
	put privacy back into the internet."
	https://fonts.bunny.net/about
*/
@import url(https://fonts.bunny.net/css?family=source-sans-3:400,700) ;
@import url(https://fonts.bunny.net/css?family=alata:400) ;

/* rem size is set here */
html {
	font-size: 24px ;
}

body {
	background: rgb(253, 253, 250) ;
	color: black ;
	font-family: 'Source Sans 3', sans-serif;
	font-weight: 400 ;
	font-size: inherit ;
}

/* Padding adds up to 1rem column separation */
.w3-row-padding, .w3-row-padding > .w3-half, .w3-row-padding > .w3-third, .w3-row-padding > .w3-twothird, .w3-row-padding > .w3-threequarter, .w3-row-padding > .w3-quarter, .w3-row-padding > .w3-col {
	padding: 0 0.5rem ;
}

/* For debugging */

/*
div,p,nav,header,main,article,footer {border: solid 1px green;}
*/

#gridcheck {
	display: none ;
}

.gridcheck-odd {
	background: rgb(86,86,86) ;
	width: 100% ;
	min-height: 2rem ;
}

.gridcheck-even {
	background: rgb(170,170,170) ;
	width: 100% ;
	min-height: 2rem ;
}

.half-col-pad {
	/* 0.5/12 */
	padding-left: 4.17% !important ;
}

/* Actually we want 3rem margin, but we have to account for the padding */
header {
	margin: 2.5rem 2.5rem 0rem 2.5rem ;
	height: 5rem ;
}

header #logo a {
	height: 5rem ;
	display: table-cell ;
	vertical-align: bottom ;
	position: relative ;
	bottom: 2px ;
	line-height: 1 ;
}

header #logo img {
	width: 100% ;
	max-height: 100% ;
}

header h1 {
	margin: 0px ;
	display: table-cell ;
	vertical-align: bottom ;
	height: 5rem ;
	position: relative ;
	bottom: -0.56rem ;
	font-size: 1.48rem ;
}

.spacer {
	min-height: 1rem ;
}

h1, h2, h3, h4, h5, h6, em, strong {
	font-family: 'Source Sans 3', sans-serif;
	font-weight: 700 ;
}

em {
	font-style: normal ;
}

.tooltip {
	display: block ;
	position: absolute ;
	padding: 0.6rem ;
	border-radius: 10px ;
	background: black ;
	color: white ;
	font-weight: normal ;
	font-size: 0.82rem ;
	text-align: left ;
}

.tooltip img {
	position: absolute ;
}

.button, .button_inactive {
	display: inline-block ;
	width: 10.6rem ;
	margin: 0px 2rem 1.9rem 0px ;
	padding: 0.94rem 0.6rem 0.75rem 1.25rem ;
}

/* No margin on ever other button */
.button:nth-of-type(2n), .button_inactive:nth-of-type(2n) {
	margin: 0px 0px 1.9rem 0px ;
}

.button {
	border: solid 1.5px black ;
	border-radius: 30px ;
	box-shadow: 6px 6px 4px 0px rgba(0, 0, 0, 0.2);
}

.button:hover, .button:focus {
	background: #fcd4e3 ;
	box-shadow: 6px 6px 4px 0px rgba(0, 0, 0, 0.2);
}

.button_inactive {
	border: dotted 2px black ;
	border-radius: 30px ;
	box-shadow: none ;
}

.button_inactive:hover, .button_inactive:focus {
	box-shadow: none ;
}

.button .image_spacer, .button_inactive .image_spacer {
	display: inline-block ;
	width: 2.2rem ;
}

.button img, .button_inactive img {
	height: 1.75rem ;
	margin-top: -0.25rem ;
}

.browse {
	display: inline-block ;
	margin: 3.1rem 1.6rem 1.9rem 0px ;
	padding: 0.6rem 0.94rem 0.5rem 0.94rem ;
	border: solid 1.5px black ;
	border-radius: 20px ;
	box-shadow: 4px 4px 4px 0px rgba(204,204,204);
	font-weight: 700 ;
	font-size: 0.75rem ;
}

.browse:hover, .browse:focus {
	background: #fcd4e3 ;
	box-shadow: 4px 4px 4px 0px rgba(204,204,204);
}

.browse .image_spacer {
	display: inline-block ;
	width: 1.25rem ;
}

.browse img {
	height: 0.8rem ;
	margin-top: -0.25rem ;
}

#login_wrapper {
	text-align: right ;
	vertical-align: bottom ;
}

.header_login {
	height: 100% ;
	margin: 3.44rem 0px 0px auto ;
}

.header_login a {
	font-weight: 700 ;
	text-decoration: none ;
}

.header_login img {
	width: 1.25rem ;
	vertical-align: baseline ;
	margin-right: 1ex ;
}

nav.course_navigation {
}

nav.course_navigation a {
	text-decoration: none ;
	border-bottom: none ;
	box-shadow: none ;
	transition: none ;
}

nav.course_navigation a:hover span, nav.course_navigation a:focus span {
	box-shadow: none ;
	border-bottom: solid 1.5px black ;
}

nav.course_navigation p {
	font-weight: 700 ;
	font-size: 0.85rem ;
	line-height: 0.94rem ;
	margin-top: 0px ;
	margin-bottom: 1.9rem ;
	width: 14rem ;
}

nav.course_navigation .bookmark {
	border-bottom:solid 1.5px black;
	font-size: 0.7rem ;
	padding-bottom: 1.25rem ;
	width: 14rem ;
}

nav.course_navigation .bookmark_icon div {
	width: 2.5rem ;
	height: 2.5rem ;
	padding: 0.3rem ;
	border: solid 1.5px black;
	border-radius: 30px ;
}

nav.course_navigation .bookmark_icon img {
	height: 1.9rem ;
}

nav.course_navigation .bookmark_text {
	vertical-align: middle;
	padding-left: 0.6rem ;
}

nav.course_navigation > .nav_line > .nav_line_offset > ol, nav.course_navigation ul {
	font-size: 0.7rem ;
}

/* Inspired by https://stackoverflow.com/a/489002/1132250 */

nav.course_navigation > .nav_line > .nav_line_offset > ol {
	font-weight: 700 ;
	counter-reset: item ;
	margin-top: -0.3rem ;
	margin-bottom: -1.44rem ;
	padding-left: 0px ;
}

nav.course_navigation > .nav_line > .nav_line_offset > ol > li {
	position: relative ;
	display: block ;
}

nav.course_navigation > .nav_line > .nav_line_offset > ol > li:before {
	content: counter(item) ;
	counter-increment: item ;
	font-family: 'Alata', sans-serif;
	font-size: 1.1rem ;
	display: inline-block ;
	position: relative ;
	top: 0.2rem ;
	border: solid 1.5px black;
	border-radius: 30px ;
	background: white ;
	text-align: center ;
	padding: 0.25rem 0rem 0rem 0rem ;
	width: 2.5rem ;
	height: 2.5rem ;
	margin-right: 0.75rem ;
}

nav.course_navigation > .nav_line > .nav_line_offset > ol > li > a {
	display: inline-block;
	padding-left: 3.1rem;
	position: relative;
	top: -2.1rem;
	height: 2.6rem;
	padding-top: 0.6rem;
	width: 14rem ;
	margin-bottom: -1.25rem ;
}

nav.course_navigation > .nav_line > .nav_line_offset > ol > li:nth-of-type(1)::before {
	margin-top: 0px ;
}

nav.course_navigation .nav_line .nav_line_offset ol a, nav.course_navigation ul a {
/*	text-decoration: none ;*/
}

nav.course_navigation > .nav_line > .nav_line_offset > ol > ul {
	font-weight: normal ;
	padding-left: 0.5rem ;
}

/* Adapted from https://www.geeksforgeeks.org/how-to-set-indent-the-second-line-of-paragraph-using-css/ */

nav.course_navigation > .nav_line > .nav_line_offset > ol > ul li {
	list-style: none;
}

nav.course_navigation > .nav_line > .nav_line_offset > ol > ul li a {
	display: inline-block;
	padding-left: 2.6rem;
	position: relative;
	top: -1.25rem;
	padding-top: 0.38rem;
	width: 12.6rem;
	margin-bottom: -0.6rem;
}

nav.course_navigation > .nav_line > .nav_line_offset > ol > ul > li:nth-of-type(1) {
	margin-top: -0.6rem;
}

nav.course_navigation > .nav_line > .nav_line_offset > ol > ul > li:last-of-type {
	margin-bottom: -0.3rem;
}

/* Adapted from https://stackoverflow.com/a/7990793/1132250 */

nav.course_navigation > .nav_line > .nav_line_offset > ol > ul li:before {
	content: "" ;
	background-image: url(/static/dot_black.svg) ;
	background-size: contain ;
	background-repeat: no-repeat ;
	display: inline-block ;
	width: 0.7rem ;
	height: 0.7rem ;
	vertical-align: middle ;
	margin-right: 1.7rem ;
	margin-left: 0.4rem ;
}

nav.course_navigation ul ul {
	padding-left: 0px ;
}

nav.course_navigation > .nav_line > .nav_line_offset > ol > ul > ul li:before {
	content: "" ;
	background-image: url(/static/diamond_black.svg) ;
	background-size: contain ;
	background-repeat: no-repeat ;
	display: inline-block ;
	width: 0.81rem ;
	height: 0.81rem ;
	vertical-align: middle ;
	margin-left: 0.33rem ;
	margin-right: 1.7rem ;
}

nav.course_navigation li.current {
	font-weight:700;color:#c81150;
}

nav.course_navigation > .nav_line > .nav_line_offset > ol > ul li.current:before {
	background-image: url(/static/dot_raspberry.svg) ;
}

nav.course_navigation > .nav_line > .nav_line_offset > ol > ul > ul li.current:before {
	background-image: url(/static/diamond_raspberry.svg) ;
}

.nav_line {
	border-left: solid 1.5px black ;
	border-top: solid 1.5px rgba(0,0,0,0) ;
	border-bottom: solid 1.5px rgba(0,0,0,0) ;
	width: 13.5rem ;
	position: relative ;
	left: 1.25rem ;
	margin-top: 1.6rem ;
	margin-bottom: 4.1rem ;
}

.nav_line_offset {
	position: relative ;
	left: -1.25rem ;
}

/* Actually we want 3rem margin, but we have to account for the padding */
main {
	margin: 0rem 2.5rem ;
}

main a {
	text-decoration: none ;
	border-bottom: solid 2px rgb(211, 65, 115) ;
}

main p {
	margin-top: 0px ;
}

.rounded_hover_border {
	border: 1.5px solid rgba(0, 0, 0, 0) ;
	border-radius: 8px ;
}

.rounded_hover_border:hover, .rounded_hover_border:focus {
	border: 1.5px solid black ;
	border-radius: 8px ;
}

form.search {
	margin-bottom: 1.6rem ;
}

form.search input:nth-of-type(1) {
	width: 100% ;
	border-radius: 30px ;
	color: rgb(191,191,191) ;
	padding: 0.31rem 1.1rem ;
}

form.search button {
	border: none ;
	background: none ;
	margin-left: -2.5rem ;
}

form.search button img {
	width: 0.94rem ;
}

form.inactive input:nth-of-type(1) {
	box-shadow: none ;
	border: dotted 2px black ;
}

select {
	border-radius: 30px ;
	padding: 0.31rem 1.1rem ;
	background: none ;
	font-weight: 700 ;
	margin-bottom: 1.9rem ;
	/* https://stackoverflow.com/a/20464860/1132250 */
	-webkit-appearance: none;
	-moz-appearance: none;
}

select:nth-of-type(n+2) {
	margin-left: 1.25rem ;
}

select.inactive {
	box-shadow: none ;
	border: dotted 2px black ;
}

.course_hover {
	border: 0.31rem solid rgba(0, 0, 0, 0);
	border-radius:27px;
	margin-bottom: 2.2rem ;
	transition: 0.4s;
}

.course_hover:hover, .course_hover:focus {
	border: 0.31rem solid rgba(200, 17, 80, 0.225);
	border-radius:27px;
	margin-bottom: 2.2rem ;
}

.course_listing {
	border: solid 1px rgb(191,191,191) ;
	border-radius: 20px ;
	box-shadow: 4px 4px 4px 0px rgba(204,204,204);
	padding: 0.94rem 1.25rem 1.6rem 1.25rem ;
	transition: 0.4s;
}

.course_hover:hover .course_listing, .course_hover:focus .course_listing {
	border: solid 1px black ;
	border-radius: 20px ;
	box-shadow: none ;
}

.course_listing h2 {
	margin: 0px 0px 0.94rem 0px ;
	font-size: 1rem ;
}

.course_listing img {
	width: 8.1rem ;
	border: solid 1.5px black ;
	border-radius: 40px ;
}

.course_listing .w3-cell:nth-of-type(2) {
	vertical-align: top ;
	padding-left: 1.9rem ;
}

.course_listing p {
	margin: 0.31rem 0px 0px 0px ;
}

.redaktionssystem h2,
.redaktionssystem h3 {
	border-radius: 10px 10px 0px 0px ;
	margin-top: 1.9rem ;
	margin-bottom: 0px ;
}

.redaktionssystem li {
	line-height: 1.25rem ;
}

.redaktionssystem form {
	border-radius: 0px 0px 10px 10px ;
	line-height: 0.94rem;
}

.redaktionssystem form input {
	font-size: 0.67rem ;
}

.redaktionssystem th {
	text-align: left ;
}

.redaktionssystem .w3-ul {
	list-style-type: decimal ;
	list-style-position: inside ;
}

/* Actually we want 3rem margin, but we have to account for the padding */
footer {
	margin: 0rem 2.5rem ;
}

footer p {
	line-height: 2.5rem ;
}

footer a {
	text-decoration: none ;
}

footer a:hover, footer a:focus {
	border-bottom: solid 1.5px black ;
}

a.nav {
	line-height: 1.25rem ;
	color: rgb(0, 0, 64) ;
	text-decoration: none ;
}

/* Default width: desktop screen */
@media only screen and (min-width: 1024px)
{

.lerninhalt .previousnext a {
	margin: 0px 2.5rem ;
}

}

/* A little smaller: tablets, small laptops etc. */
@media only screen and (min-width: 480px) and (max-width: 1023px)
{

.lerninhalt .previousnext a {
	margin: 0px 0.6rem ;
}

}

/* Very small: mobile phones etc. */
@media only screen and (max-width: 479px)
{

#login_wrapper {
	text-align: left ;
	margin-left: -0.31rem ;
}

.header_login {
	margin: 0px 0px 2em 0px ;
}

nav.course_navigation {
	width: auto ;
	margin-left: 0.6rem ;
}

.tooltip {
	display: none !important ;
}

select:nth-of-type(n+2) {
  margin-left: 0.31rem;
}

.button, .button_inactive {
	width: 100% ;
}

.browse {
	width: 100% ;
}

.course_hover {
	border: none ;
}

.course_listing .w3-cell:nth-of-type(2) {
	padding-left: 0px ;
	padding-top: 0.6rem ;
}

.lerninhalt .previousnext a {
	margin: 0px 1ex ;
}

footer a {
	border-bottom: solid 1.5px black ;
}

}

/* High resolution displays such as Apple Retina render larger font sizes,
   so we downsize rem here.
   Query by https://css-tricks.com/snippets/css/retina-display-media-query/
*/
@media
only screen and (-webkit-min-device-pixel-ratio: 2),
only screen and (   min--moz-device-pixel-ratio: 2),
only screen and (     -o-min-device-pixel-ratio: 2/1),
only screen and (        min-device-pixel-ratio: 2),
only screen and (                min-resolution: 192dpi),
only screen and (                min-resolution: 2dppx)
{ 
	html {
		font-size: 20px !important ;
	}
}
'''
"""Additional CSS for all luna_lms HTML pages.
"""

# Escape for format()
#
CSS = CSS.replace("{", "{{").replace("}", "}}")

# TODO: Make lang an option
#
HTML_HEAD = '''<!DOCTYPE html>
<html lang="de">
<head>
	<meta charset="utf-8"/>
	<meta http-equiv="content-type" content="text/html; charset=UTF-8">
<!-- https://developers.google.com/speed/docs/insights/ConfigureViewport -->
	<meta name=viewport content="width=device-width, initial-scale=1">
<title>{title}</title>
	<!-- by evilmartians.com -->
	<link rel="icon" href="/static/favicon.ico" sizes="32x32">
	<link rel="icon" href="/static/favicon.svg" type="image/svg+xml">
	<link rel="apple-touch-icon" href="/static/apple-touch-favicon.png"><!-- 180×180 -->
	<link rel="manifest" href="/static/manifest.webmanifest">
	<link rel="stylesheet" href="/static/w3.css">
	<link rel="stylesheet" href="/static/custom.css">
	<style type="text/css">''' + CSS + '''
	</style>
</head>
<body>
'''
"""The general HTML head for all luna_lms pages, including the opening <body> tag.
"""

HTML_HEADER = '''	<div id="gridcheck" class="w3-row-padding" style="margin:0rem 2.5rem;">
		<div class="w3-col m1">
			<div class="gridcheck-odd"></div>
		</div>
		<div class="w3-col m1">
			<div class="gridcheck-even"></div>
		</div>
		<div class="w3-col m1">
			<div class="gridcheck-odd"></div>
		</div>
		<div class="w3-col m1">
			<div class="gridcheck-even"></div>
		</div>
		<div class="w3-col m1">
			<div class="gridcheck-odd"></div>
		</div>
		<div class="w3-col m1">
			<div class="gridcheck-even"></div>
		</div>
		<div class="w3-col m1">
			<div class="gridcheck-odd"></div>
		</div>
		<div class="w3-col m1">
			<div class="gridcheck-even"></div>
		</div>
		<div class="w3-col m1">
			<div class="gridcheck-odd"></div>
		</div>
		<div class="w3-col m1">
			<div class="gridcheck-even"></div>
		</div>
		<div class="w3-col m1">
			<div class="gridcheck-odd"></div>
		</div>
		<div class="w3-col m1">
			<div class="gridcheck-even"></div>
		</div>
	</div>

	<header class="w3-row-padding">
		<div id="logo" class="w3-col m2">
			<a href="/"><img src="/static/{logo_file}" alt="Logo"></a>
		</div>

		<div class="w3-col m1 spacer">
		</div>

		<div class="w3-col m5 half-col-pad">
			<h1>{heading}</h1>
		</div>

		<div class="w3-col m1 spacer">
		</div>

		<div class="w3-col m3" style="text-align:right;">
			<div class="w3-tooltip header_login" aria-describedby="tooltip-login">
				<a href="/account" class="rounded_hover_border" style="padding: 0.75rem 0.44rem 0.25rem 0.5rem;">
					<img src="/static/account.svg" alt=""> Anmelden
				</a>
				<div class="w3-text w3-animate-opacity tooltip"
					 style="top:-0.44rem;right:12.2rem;width:11.9rem;"
					 id="tooltip-login">
					<em>Nutzer*innen-Konto</em>
					<br>
					<span style="color:#fc9e4f;">Diese Funktion ist gerade im
					Bau.</span> Bald kannst du deinen Lern-Fortschritt und deine
					Einstellungen auch in deinem Konto speichern.
					<img src="/static/tooltip-pointer.svg" alt="" style="top:0.75rem;right:-1rem;">
				</div>
			</div>
		</div>
	</header>
'''
"""The <header> for all luna_lms pages, including logo, heading and login status.
"""

HTML_FOOT = '''	<footer class="w3-row-padding">
		<div class="w3-col m12 spacer" style="height:2.5rem;border-bottom:solid black 1.5px;margin-bottom:0.6rem;"></div>
		<div class="w3-col m3">
			<p>
				<a href="/faq">{}</a>
				<br>
				<a href="/report">{}</a>
			</p>
		</div>
		<div class="w3-col m3">
			<p>
				<a href="/privacy">{}</a>
				<br>
				<a href="/imprint">{}</a>
			</p>
		</div>
		<div class="w3-col m3">
			<p>
				<a href="/about">{}</a>
				<br>
				<a href="/contact">{}</a>
			</p>
		</div>
		<div class="w3-col m3">
			<p style="text-align:right;">
				<a href="https://luna-lms.de/">
					Luna&nbsp;LMS,
				</a>
				Version&nbsp;{}
				<br>
				<a href="#"><img src="/static/pen.svg" alt="{}" style="height:1.1rem;margin-bottom:0.25rem;margin-right:0.44rem;">{}</a>
			</p>
		</div>
	</footer>
</body>
</html>
'''.format(_("Häufige Fragen"),
			_("Einen Fehler melden"),
			_("Daten-Schutz"),
			_("Impressum"),
			_("Über uns"),
			_("Kontakt"),
			VERSION,
			_("Stift-Symbol"),
			_("Redaktions-Zugang"))
"""The general HTML footer for all luna_lms pages, including the closing <body> tag.
"""

class WebApp:
	"""Web application main class, suitable as cherrypy root.
	"""

	def __init__(self):
		"""Initialise WebApp.
		"""

		self.storage = SQLiteStorage()

		if not os.path.isdir("pages"):

			LOGGER.warning("Directory 'pages' does not exist, creating")

			os.mkdir("pages")

		if not os.path.isdir("static"):

			LOGGER.warning("Directory 'static' does not exist, creating")

			os.mkdir("static")

		# Note: This exposes the directory world-readable, once the file URLs
		# are known. Directories are not listed.
		#
		config = {"/static" : {"tools.staticdir.on" : True,
								"tools.staticdir.dir" : os.path.join(os.getcwd(),
																		"static")}}

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

		# Nesting methods for CherryPy dispatching according to the API

		# self.courses.view()
		#
		self.courses.__dict__["view"] = self.view

		# Make self.__call__ visible to cherrypy
		#
		self.exposed = True

		return

	def _cp_dispatch(self, vpath):
		"""Custom dispatch for static pages in the 'pages' directory.
		"""

		#LOGGER.debug("_cp_dispatch(vpath = {})".format(vpath))
		
		# Taken from https://docs.cherrypy.dev/en/latest/advanced.html#the-special-cp-dispatch-method

		# Check for static page
		#
		if len(vpath) == 1:

			if vpath[0].isalnum():

				if os.path.exists(os.path.join("pages",
												vpath[0] + ".html")):

					cherrypy.request.params["page"] = vpath.pop()

				elif os.path.exists(os.path.join("pages",
													vpath[0] + ".default.html")):

					cherrypy.request.params["page"] = vpath.pop()  + ".default"

				return self.static_page

			else:

				LOGGER.info("Page {} does not exist, passing on".format(os.path.join("pages",
																	vpath[0] + ".html")))

		return vpath

	@cherrypy.expose
	def static_page(self, page):
		"""Read a static page from the directory 'pages', and render it.

		This method is meant to be called from _cp_dispatch() only.
		It will redirect when called directly.
		"""

		LOGGER.debug("static_page(page = {})".format(page))

		path = cherrypy.request.path_info

		if path.find("static_page") > -1:

			# This is not meant to be called directly
			#
			raise cherrypy.HTTPRedirect("/{}".format(path.split("static_page/")[-1]),
										301)

		return_str = HTML_HEAD.format(title = "Luna LMS: {}".format(page))

		heading = ""
		content = ""

		# _cp_dispatch() has already checked that the page exists.
		#
		with open(os.path.join("pages", page + ".html"), "rt") as f:

			for line in f.readlines():

				if line.strip().startswith('<h1'):

					# NOTE: Yes, one should always use a full-blown SGML parser.
					# We play dirty here for that single line.
					# This will fail in a lot of valid cases, but do the
					# right thing in most.
					#
					heading = line.split('>')[1].split('</')[0]

				else:
					content += line

		return_str += self._format_header(heading)

		return_str += '<div class="w3-row-padding" style="margin:0rem 2.5rem;"><div class="w3-col m12 spacer" style="height:2.5rem;"></div></div>'

		return_str += '<main class="w3-row-padding">'

		return_str += '<div class="w3-col m3 spacer"></div>'

		return_str += '<div class="w3-col m7 half-col-pad">'

		return_str += content

		return_str += '</div>'

		return_str += '<div class="w3-col m2 spacer"></div>'

		return_str += '</main>'

		return_str += HTML_FOOT

		return return_str

	def cached_item(self, course_id, path, file_format, data):
		"""Return a cached item in the response.

		This method is meant to be called from _cp_dispatch() only.
		It will redirect when called directly.
		"""

		LOGGER.debug("cached_item(course_id = {}, path = {})".format(course_id, path))

		request_path = cherrypy.request.path_info

		if request_path.find("cached_item") > -1:

			# This is not meant to be called directly
			#
			raise cherrypy.HTTPRedirect("/courses/{}/{}".format(course_id, path),
										301)

		# Adapted from https://stackoverflow.com/a/41581093/1132250
		#
		cherrypy.response.headers["Content-Type"] = file_format

		cherrypy.response.headers["Content-Disposition"] = 'inline;filename="{}"'.format(path.split("/")[-1])

		return data

	def _format_header(self, heading = '<!-- no heading provided -->'):
		"""Compute format string replacements forthe HTML_HEADER template, apply them, and return it.
		"""

		result = ""

		if os.path.exists(os.path.join("static", "logo.svg")):

			result = HTML_HEADER.format(logo_file = "logo.svg", heading = heading)

		else:
			result = HTML_HEADER.format(logo_file = "logo.default.svg", heading = heading)

		return result


	def __call__(self):
		"""Called by cherrypy for the / root page.
		"""

		return_str = HTML_HEAD.format(title = _("Luna LMS: Start"))

		heading = _("Willkommen!")
		welcome = ""

		path = ""

		if os.path.exists(os.path.join("pages", "welcome.html")):

			path = os.path.join("pages", "welcome.html")

		elif os.path.exists(os.path.join("pages", "welcome.default.html")):

			path = os.path.join("pages", "welcome.default.html")

		if path:

			with open(path, "rt") as f:

				for line in f.readlines():

					if line.strip().startswith('<h1'):

						# NOTE: Yes, one should always use a full-blown SGML parser.
						# We play dirty here for that single line.
						# This will fail in a lot of valid cases, but do the
						# right thing in most.
						#
						heading = line.split('>')[1].split('</')[0]

					else:
						welcome += line

		return_str += self._format_header(heading)

		return_str += '<div class="w3-row-padding" style="margin:0rem 2.5rem;"><div class="w3-col m12 spacer" style="height:2.5rem;"></div></div>'

		return_str += '<main class="w3-row-padding">'

		return_str += '<div class="w3-col m3 spacer"></div>'

		return_str += '<div class="w3-col m7 half-col-pad">'

		return_str += welcome

		return_str += '<a class="button" href="/courses"><div class="image_spacer"><img src="/static/course_start.svg" alt=""></div>{}</a>'.format(_("Kurs beginnen"))

		return_str += '<a class="button" href="/continue"><div class="image_spacer"><img src="/static/course_continue.svg" alt=""></div>{}</a>'.format(_("Kurs fortsetzen"))

		return_str += '<br>'

		return_str += '<a class="button_inactive"><div class="image_spacer"><img src="/static/account_add.svg" alt=""></div>{}</a>'.format(_("Konto anlegen"))

		return_str += '</div>'

		return_str += '<div class="w3-col m2 spacer"></div>'

		return_str += '</main>'

		return_str += HTML_FOOT

		return return_str

	@cherrypy.expose
	def courses(self, *args, **kwargs):
		"""The entry point for all paths starting with /courses .
		"""

		LOGGER.debug("courses(args = {}, kwargs = {})".format(args, kwargs))

		# Check for cached item below /courses
		#
		if len(args) > 1:

			# Cached items belong to a specific course, so there must be a
			# course identifier in the request path.
			#
			# Typical cached request paths would look like:
			#
			# /courses/view/d220804a-3166-4b42-82d7-e856ce75fe33/ad80or
			# /courses/d220804a-3166-4b42-82d7-e856ce75fe33/media/audio/chimes.opus

			course_id = None

			path = "/".join(args[1:])

			try:
				course_id = uuid.UUID(args[0])

				item = self.storage.get_cached_item(course_id, path)

				if item:

					return self.cached_item(course_id, path, item["format"], item["data"])

			except ValueError:

				LOGGER.error("Path component is not an UUID: '{}'".format(args[0]))
				raise cherrypy.NotFound()

			LOGGER.error("Path '{}' is not cached in course {}, and does not point to a valid resource".format(course_id, path))
			raise cherrypy.NotFound()
		
		return_str = HTML_HEAD.format(title = _("Luna LMS: Kurs-Übersicht"))

		return_str += self._format_header(_("Kurs-Übersicht"))

		return_str += '<div class="w3-row-padding" style="margin:0rem 2.5rem;"><div class="w3-col m12 spacer" style="height:2.5rem;"></div></div>'

		return_str += '<main class="w3-row-padding">'

		return_str += '<div class="w3-col m3 spacer"></div>'

		return_str += '<div class="w3-col m6 half-col-pad">'

		return_str += '<form class="search inactive">'
		desc = _("Suche nach Kurs-Titeln, Schlagworten und mehr...")
		return_str += '<input name="terms" type="text" value="{0}" title="{0}" disabled>'.format(desc)
		return_str += '<button type="submit" disabled><img src="/static/search-inactive.svg" alt="{}"></button>'.format(_("Suchen"))
		return_str += '</form>'

		return_str += '<div>'

		return_str += '''	<select name="sort" class="inactive" disabled>
		<option value="sort">{}</option>
	</select>
'''.format(_("Sortieren"))

		return_str += '''	<select name="filter" class="inactive" disabled>
		<option value="filter">{}</option>
	</select>
'''.format(_("Alle Filter"))

		return_str += '</div>'

		courses = self.storage.find_courses()

		# Create a list to be able to sort
		#
		titles = [key for key in courses.keys() if key.__class__ == str]

		titles.sort()

		for title in titles:

			course_id = courses[title]

			meta_data = self.storage.get_course_metadata(course_id)

			alt = self.storage.get_cached_item(course_id, meta_data["relation"])["description"]

			return_str += '<div class="course_hover">'

			return_str += '<a href="/courses/view/{}">'.format(course_id)

			return_str += '<div class="course_listing">'

			return_str += '<h2>{}</h2>'.format(meta_data["title"])

			return_str += '<div class="w3-cell-row">'

			return_str += '<div class="w3-cell w3-mobile">'

			return_str += '<img src="/courses/{}/{}" alt="{}">'.format(course_id,
																		meta_data["relation"],
																		alt)

			return_str += '</div>'

			return_str += '<div class="w3-cell w3-mobile w3-container">'

			return_str += '<p>{}</p>'.format(meta_data["description"])

			return_str += '</div>'

			return_str += '</div>'

			return_str += '</div>'

			return_str += '</a>'

			return_str += '</div>'

		return_str += '<a href="/" class="browse"><div class="image_spacer"><img src="/static/back.svg" alt=""></div>{}</a>'.format(_("Zurück zur Start-Seite"))

		return_str += '</div>'

		return_str += '<div class="w3-col m3 spacer"></div>'

		return_str += '</main>'

		return_str += HTML_FOOT

		return return_str

	@cherrypy.expose
	def view(self, course_id, learning_content_id = "", modus = ""):
		"""The view for Luna LMS, displaying learning content.

		By default, a learning content will display any HTML file present
		as a variant.
		"""

		LOGGER.debug("view(course_id = '{}', learning_content_id = '{}', modus = '{}')".format(course_id, learning_content_id, modus))

		try:
			course_id = uuid.UUID(course_id)

		except ValueError:

			LOGGER.info("course_id '{}' is not a valid UUID".format(course_id))
			raise cherrypy.NotFound()

		# If called with a raw course_id, redirect to the first learning content.

		if course_id and not learning_content_id:

			# Getting the first item via iter()'s __next__() seems more
			# efficient than building a list just to get the first element.
			#
			first_learning_content_id = iter(self.storage.get_learning_contents_ordered(course_id)).__next__().identifier

			raise cherrypy.HTTPRedirect("/courses/view/{}/{}".format(course_id,
																		first_learning_content_id),
																		301)

		# Generate page content

		course_title = self.storage.find_courses()[course_id]

		learning_contents = self.storage.get_learning_contents_ordered(course_id)

		def get_identifiers(d):
			result = {}
			for key in d.keys():
				result[key.identifier] = key.title
				if d[key]:
					result.update(get_identifiers(d[key]))
			return result
		
		# TODO: This should be returned alongside the OrderedDict by
		# get_learning_contents_ordered()
		#
		ids_identifiers_flat = get_identifiers(learning_contents)

		ids_flat = list(ids_identifiers_flat.keys())

		if learning_content_id not in ids_flat:

			LOGGER.error("learning content '{}' is not listed for course '{}'".format(learning_content_id, course_title))
			raise cherrypy.NotFound()

		# If there is no variant for the current step, skip to the next step.
		# TODO: Actually check for missing variant/content
		#
		if not self.storage.get_html(course_id, learning_content_id) and len(ids_flat) > ids_flat.index(learning_content_id) + 1:

			next_id = ids_flat[ids_flat.index(learning_content_id) + 1]

			raise cherrypy.HTTPRedirect("/courses/view/{}/{}".format(course_id,
																		next_id),
																		302)

		return_str = HTML_HEAD.format(title = "Luna LMS: {}".format(course_title))

		# Precompute Headings

		def get_hierarchy(d, identifier, results = []):
			if identifier in [key.identifier for key in d.keys()]:
				results.append(ids_identifiers_flat[identifier])
				return results
			else:
				for key in d.keys():
					if d[key] and identifier in get_identifiers(d[key]).keys():
						results.append(key.title)
						get_hierarchy(d[key], identifier, results)
			return results
		
		# TODO: This should be returned alongside the OrderedDict by
		# get_learning_contents_ordered()
		#
		heading_hierarchy = get_hierarchy(learning_contents, learning_content_id)

		first_heading = ""
		other_headings = ""

		level = 1

		for heading in heading_hierarchy:

			if level == 1:

				first_heading = heading

			else: 
				other_headings += '<h{0}>{1}</h{0}>'.format(level, heading)

			level += 1

		return_str += self._format_header(first_heading)

		return_str += '<div class="w3-row-padding" style="margin:0rem 2.5rem;">'
		return_str += '	<div class="w3-col m10 spacer"></div>'
		return_str += '	<div class="w3-col m2" style="height:4.45rem;text-align:right;">'
		return_str += '		<a class="rounded_hover_border" style="padding: 0.1rem 0.2rem;position:relative;top: 0.5rem;" href="#">'
		return_str += '			<img src="/static/modes.svg" style="height:1rem;" alt="{}">'.format(_("Modus-Menü-Symbol"))
		return_str += '		</a>'
		return_str += '	</div>'
		return_str += '</div>'

		return_str += '<main class="w3-row-padding">'

		return_str += '	<div class="w3-col m3">'
		return_str += '	<nav class="course_navigation">'

		return_str += '		<p>{}</p>'.format(course_title)
		
		return_str += '		<div class="bookmark">'
		return_str += '			<div class="w3-cell bookmark_icon">'
		return_str += '				<div>'
		return_str += '					<img src="/static/bookmark.svg" alt="">'
		return_str += '				</div>'
		return_str += '			</div>'
		return_str += '			<div class="w3-cell bookmark_text">'
		return_str += '{}:<br><strong>{}</strong>'.format(_("Mein Lese-Zeichen"), "DreiWortCode")
		return_str += '</div>'
		return_str += '		</div>'

		return_str += '		<div class="nav_line">'
		return_str += '			<div class="nav_line_offset">'

		def display_steps(d, level = 0):
			list_type = "ol"
			if level > 0:
				list_type = "ul"
			result = "<{}>".format(list_type)
			for key in d.keys():
				title = key.title
				if level == 0 and len(key.title) > 33:
					title = "{}...".format(title[:30])
				style = ""
				if key.identifier == learning_content_id:
					style=' class="current"'
				result += '<li{}><a href="/courses/view/{}/{}"><span>{}</span></a></li>'.format(style, course_id, key.identifier, title)
				# Only display a sub-level if the current step is part of it, at any level
				if d[key] and learning_content_id in get_identifiers(d[key]).keys():
					result += display_steps(d[key], level + 1)
			result += "</{}>".format(list_type)
			return result

		return_str += display_steps(learning_contents)

		return_str += '			</div>'
		
		return_str += '		</div>'
		
		return_str += '	</nav>'

		return_str += '	</div>'

		return_str += '<article class="w3-col m7 half-col-pad">'

		return_str += other_headings

		# Display content according to mode.
		# text is the fallback mode.

		content_str = ""

		if modus == MODI.TEXT_ZUSATZ:

			# Use the first directory we find, with the first HTML file we
			# find in there.

			(directory_name, html) = self.storage.get_directory(course_id, learning_content_id)

			if directory_name:

				replacement_path = "/static/{}/Lern-Inhalte/{}/{}/".format(course_title,
																learning_content_id,
																directory_name)

				# Correct local path for img tags
				#
				html = html.replace('src="', 'src="{}'.format(replacement_path))

				# Correct local path for CSS images
				#
				html = html.replace("url('","url('{}".format(replacement_path))

				content_str = html

		if modus == MODI.BILD:

			# Embed the first image file we find.

			image_path = self.storage.get_image(course_id, learning_content_id)

			if image_path:

				content_str = '<p><img style="max-width:100%;" src="{}" alt=""></p>'.format(image_path)

		if modus == MODI.TEXT_BILD:

			# Combine first HTML and image file

			html = self.storage.get_html(course_id, learning_content_id)

			if html:

				content_str = '<div style="float:left;">' +  html + '</div>'

			image_path = self.storage.get_image(course_id, learning_content_id)

			if image_path:

				content_str += '<div style="float:left;"><img style="max-width:100%;" src="{}" alt=""></div>'.format(image_path)

			content_str += '<div style="clear:both;"></div>'

		if not content_str:

			# Fallback: Embed the first HTML file we find.

			content_str = self.storage.get_html(course_id, learning_content_id)

		return_str += content_str

		return_str += '<div>'

		index = ids_flat.index(learning_content_id)

		if index > 0:

			previous_id = ids_flat[index - 1]

			# If there is no variant for the previous step, skip back two steps
			# TODO: Actually check for missing variant/content
			#
			if index > 1 and not self.storage.get_html(course_id, previous_id):

				previous_id = ids_flat[index - 2]

			return_str += '<div class="w3-cell w3-mobile" style="width:8.1rem;">'

			html = '<a href="/courses/view/{}/{}" class="browse"><div class="image_spacer"><img src="/static/back.svg" alt=""></div>{}</a>'
			
			return_str += html.format(course_id,
										previous_id,
										_("Zurück"))

			return_str += '</div>'

			return_str += '<div class="w3-cell w3-mobile" style="width:6.25rem;">'
			return_str += '</div>'

		if index < len(ids_flat) - 1:

			return_str += '<div class="w3-cell w3-mobile" style="width:8.1rem;">'

			html = '<a href="/courses/view/{}/{}" class="browse" style=""><div class="image_spacer"><img src="/static/forward.svg" alt=""></div>{}</a>'

			return_str += html.format(course_id,
										ids_flat[index + 1],
										_("Weiter"))

			return_str += '</div>'

		return_str += '</div>'

		return_str += '</article>'

		return_str += '<div class="w3-col m1 spacer"></div>'
		
		return_str += '<div class="w3-col m1 spacer"></div>'
		
		return_str += '</main>'

		return_str += HTML_FOOT

		return return_str

	@cherrypy.expose
	def redaktion(self, *args, title = "", filename = "", content = "", _method = "", learning_contents = ""):
		"""The content management frontend for Luna LMS, and a dispatcher for all subordinate endpoints.

		This method will dispatch any requests to subordinate endpoints to appropriate handlers.
		"""

		LOGGER.debug("redaktion(args = {}, title = '{}', filename = '{}', content = {}, _method='{}', learning_contents='{}')".format(args, title, filename, content.__class__, _method, learning_contents))

		# This method does not follow the CherryPy idea very well, since it does
		# its own dispatching. CherryPy normally expects Python objects that
		# it can traverse using their __dict__. Usually, we would build such
		# an object from data on disk, populate it, and sync back any changes
		# to disk. However, Luna follows a "disk first" approach, with the
		# normative state of the application in the files. Hence, we currently
		# always read the current state from disk anyway, and so it does not
		# make much sense to build an object that may not reflect the current
		# state correctly. So, we use this entry point as a dispatcher, and
		# check the disk state for whatever comes in. Sorry for the mess.

		# Dispatch by number of parameters, i. e. endpoint
		#
		# Before we do anything, check if this is for a subordinate endpoint.
		#
		if len(args):

			if len(args) == 1:

				LOGGER.info("1 argument, dispatching to kurs_redaktion()")

				return self.kurs_redaktion(args[0], title, _method)

			if len(args) == 2 and args[1] == "Lern-Inhalte":

				LOGGER.info("2nd argument is 'Lern-Inhalte', dispatching to learning_contents_redaktion_put()")

				return self.learning_contents_redaktion_put(args[0], learning_contents, _method)

			if len(args) == 2:

				LOGGER.info("2 arguments, dispatching to lerninhalt_redaktion()")

				return self.lerninhalt_redaktion(args[0], args[1], filename, content, _method)

			if len(args) == 3:

				LOGGER.info("2 arguments, dispatching to variant_redaktion()")

				return self.variant_redaktion(args[0], args[1], args[2], filename, content, _method)

			LOGGER.error("Can not handle endpoint /redaktion/" + "/".join(args))
			raise cherrypy.NotFound()

		# Dispatch by method
		#
		# Luna aims at being a REST application, so we explicitly check the HTTP
		# method.
		#
		if _method.upper() == "GET" or (cherrypy.serving.request.method == "GET" and _method.upper() in ("", "GET")):

			return self.redaktion_get(args)

		elif _method.upper() == "POST" or (cherrypy.serving.request.method == "POST" and _method.upper() in ("", "POST")):

			return self.redaktion_post(args, title)

		else:

			# Request has not been handled, so the method is unsupported.
			# 
			method = _method.upper()

			if not method:

				method = cherrypy.serving.request.method

			error = _("Die angefragte Ressource /redaktion/{} unterstützt die Methode '{}' nicht.").format("/".join(args), method)

			LOGGER.error(error)

			raise cherrypy.HTTPError(501, error)


	def redaktion_get(self, message = ""):
		"""Handler method to be called by redaktion().

		GET: Display the content management frontend.
		"""
		# Handle the Redaktion

		return_str = HTML_HEAD.format(title = _("Redaktionssystem"))

		return_str += '<div class="redaktionssystem">'

		return_str += '<header class="w3-content">'

		return_str += '<h1 class="w3-padding w3-khaki">{}</h1>'.format(_("Redaktionssystem"))

		return_str += '<nav class="w3-padding">'

		return_str += '<p><a href="/" class="nav w3-light-blue w3-padding w3-round-xlarge">&lt;&nbsp;{}</a></p>'.format(_("Zur Startseite"))

		return_str += '</nav>'

		return_str += '</header>'

		return_str += '<main class="w3-content">'

		if message:
			return_str += '<p><strong>{}</strong></p>'.format(message)

		# List courses

		return_str += '<h2 class="w3-padding w3-khaki">{}</h2>'.format(_("Kurse"))

		courses = self.storage.find_courses()

		# Create a list to be able to sort
		#
		titles = [key for key in courses.keys() if key.__class__ == str]

		titles.sort()

		for title in titles:

			return_str += '''<form action="/redaktion/{0}"
								method="post"
								style="padding: 0px;background: none;border-radius: 0px;">
	<p>
		<a href="/redaktion/{0}">{1}&nbsp;&gt;</a>
		<input type="hidden" name="_method" value="DELETE">
		<input type="submit" value="{2}">
	</p>
</form>'''.format(courses[title], title, _("Löschen"))

		# Form to create a course

		return_str += '<h2 class="w3-padding w3-khaki">{}</h2>'.format(_("Kurs anlegen"))

		return_str += '<form action="/redaktion" method="post" class="w3-padding-large w3-light-grey">'

		return_str += '<p><label for="title">{}</label>: '.format(_("Titel"))

		return_str += '<input type="text" name="title" id="title">'

		return_str += '<br>{}</p>'.format(_("Erlaubte Zeichen: Buchstaben, Zahlen, Leerzeichen, Bindestrich, Unterstrich"))

		return_str += '<input type="submit" value="{}">'.format(_("Anlegen"))
		return_str += '</form>'

		return_str += '<!-- Ende redaktionssystem --></div>'

		return_str += '</main>'

		return_str += HTML_FOOT

		return return_str


	def redaktion_post(self, args, title):
		"""Handler method to be called by redaktion().

		POST: Create a new course using the title, and then display the content management frontend.
		"""

		LOGGER.debug('POST redaktion(title = "{}")'.format(title))

		message = check_title(title)

		if message:

			# This is an error, stop here.

			# After processing POST, render the page as if GET was called,
			# plus a message.
			#
			return self.redaktion_get(args, message)

		# Remove possible surrounding whitespace
		#
		title = title.strip()

		message = self.storage.write_course(title)

		if message:
			message = '{}: {}'.format(title, message)

		# After processing POST, render the page as if GET was called,
		# plus a message.
		#
		return self.redaktion_get(message)


	def kurs_redaktion(self, course_id, learning_content_title = "", _method=""):
		"""Content management of a course.

		This method will dispatch the handling of the request by method.
		"""

		LOGGER.debug("kurs_redaktion(course_id = '{}', learning_content_title = '{}', _method='{}')".format(course_id, learning_content_title, _method))

		# Luna aims at being a REST application, so we explicitly check the HTTP
		# method.
		#
		if _method.upper() == "GET" or (cherrypy.serving.request.method == "GET" and _method.upper() in ("", "GET")):

			return self.kurs_redaktion_get(course_id, message = "")

		elif _method.upper() == "POST" or (cherrypy.serving.request.method == "POST" and _method.upper() in ("", "POST")):

			return self.kurs_redaktion_post(course_id, learning_content_title)

		elif _method.upper() == "DELETE" or (cherrypy.serving.request.method == "DELETE" and _method.upper() in ("", "DELETE")):

			return self.kurs_redaktion_delete(course_id)

		else:

			# Request has not been handled, so the method is unsupported.
			# 
			method = _method.upper()

			if not method:

				method = cherrypy.serving.request.method

			error = _("Die angefragte Ressource /redaktion/{} unterstützt die Methode '{}' nicht.").format(course_id, method)

			LOGGER.error(error)

			raise cherrypy.HTTPError(501, error)

	def kurs_redaktion_get(self, course_id, message):
		"""Handler method to be called by kurs_redaktion().

		GET: Display the content management frontend.
		"""

		courses = self.storage.find_courses()

		if uuid.UUID(course_id) not in courses.keys():

			LOGGER.error("course {} requested, but does not exist".format(course_id))
			raise cherrypy.NotFound()
			LOGGER.error("course {} requested, but does not exist".format(course_id))
			raise cherrypy.NotFound()

		course_title = courses[uuid.UUID(course_id)]

		# Build the page

		return_str = HTML_HEAD.format(title = course_title)

		return_str += '<div class="redaktionssystem">'

		return_str += '<header class="w3-content">'

		return_str += '<h1 class="w3-padding w3-khaki">{1}: {0}</h1>'.format(course_title, _("Kurs"))

		return_str += '<nav class="w3-padding">'

		return_str += '<p><a href="/redaktion" class="nav w3-light-blue w3-padding w3-round-xlarge">&lt;&nbsp;{}</a></p>'.format(_("Zur Kurs-Übersicht"))

		return_str += '</nav>'

		return_str += '</header>'

		return_str += '<main class="w3-content">'

		if message:
			return_str += '<p><strong>{}</strong></p>'.format(message)

		return_str += '<h2 class="w3-padding w3-khaki">{}</h2>'.format(_("Lern-Inhalte"))

		# List learning contents

		learning_contents = self.storage.get_learning_contents_titles(course_title)

		return_str += '<ol class="w3-ul w3-section">'

		position = 0

		for existing_id in self.storage.get_learning_contents_ordered(course_id):

			return_str += '<li>'

			return_str += '<a href="/redaktion/{0}/{1}">{2}&nbsp;&gt;</a>'.format(course_id, existing_id, learning_contents[existing_id])

			return_str += '''<form action="/redaktion/{0}/{1}"
	method="post"
	style="padding: 0px;background: none;border-radius: 0px;display:inline;">
		<input type="hidden" name="_method" value="DELETE">
		<input type="submit" value="{2}">
</form>'''.format(course_id,
				existing_id,
				_("Löschen"))

			if position > 0:

				# Make a copy to be able to change the list
				#
				changed_list = list(self.storage.get_learning_contents_ordered(course_id))

				changed_list[position - 1], changed_list[position] = changed_list[position], changed_list[position - 1]

				return_str += '''<form action="/redaktion/{0}/Lern-Inhalte"
	method="post"
	style="padding: 0px;background: none;border-radius: 0px;display:inline;">
		<input type="hidden" name="_method" value="PUT">
		<input type="hidden" name="learning_contents" value="{1}">
		<input type="submit" value="{2}">
</form>'''.format(course_id,
				changed_list,
				_("Nach oben"))

			if position < len(learning_contents.keys()) - 1:

				changed_list = list(self.storage.get_learning_contents_ordered(course_id))

				changed_list[position], changed_list[position + 1] = changed_list[position + 1], changed_list[position]

				return_str += '''<form action="/redaktion/{0}/Lern-Inhalte"
	method="post"
	style="padding: 0px;background: none;border-radius: 0px;display:inline;">
		<input type="hidden" name="_method" value="PUT">
		<input type="hidden" name="learning_contents" value="{1}">
		<input type="submit" value="{2}">
</form>'''.format(course_id,
				changed_list,
				_("Nach unten"))

			return_str += '</li>'

			position += 1

		return_str += '</ol>'

		# Form to create a learning content

		return_str += '<h2 class="w3-padding w3-khaki">{}</h2>'.format(_("Lern-Inhalt hinzufügen"))

		return_str += '<form action="/redaktion/{}" method="post" class="w3-padding-large w3-light-grey">'.format(course_id)

		return_str += '<p><label for="title">{}</label>: '.format(_("Titel"))

		return_str += '<input type="text" name="title" id="title">'

		return_str += '<br>{}</p>'.format(_("Erlaubte Zeichen: Buchstaben, Zahlen, Leerzeichen, Bindestrich, Unterstrich"))

		return_str += '<input type="submit" value="{}">'.format(_("Anlegen"))
		return_str += '</form>'

		return_str += '<!-- Ende redaktionssystem --></div>'

		return_str += '</main>'

		return_str += HTML_FOOT

		return return_str


	def kurs_redaktion_post(self, course_id, learning_content_title):
		"""Handler method to be called by kurs_redaktion().

		POST: Create a new learning content using the learning_content_title, and then display the content management frontend.
		"""

		LOGGER.debug('POST kurs_redaktion(course_id = "{}", learning_content_title = "{}")'.format(course_id, learning_content_title))

		message = check_title(learning_content_title)

		if message:

			# This is an error, stop here.

			# After processing POST, render the page as if GET was called,
			# plus a message.
			#
			return self.kurs_redaktion_get(course_id, message)

		# Remove possible surrounding whitespace
		#
		learning_content_title = learning_content_title.strip()

		course_title = self.storage.find_courses()[uuid.UUID(course_id)]

		message = self.storage.write_learning_content(course_title, learning_content_title)

		if message:
			message = '{}: {}'.format(learning_content_title, message)

		# After processing POST, render the page as if GET was called,
		# plus a message.
		#
		return self.kurs_redaktion_get(course_id, message)


	def kurs_redaktion_delete(self, course_id):
		"""Handler method to be called by kurs_redaktion().

		DELETE: Check and handle a deletion.
		"""

		# Start building the page

		return_str = HTML_HEAD.format(title = _("Lern-Inhalt löschen"))

		message = ""

		courses = self.storage.find_courses()

		course_title = ""

		if uuid.UUID(course_id) in courses.keys():

			course_title = courses[uuid.UUID(course_id)]

		if not course_title or course_title not in self.storage.get_course_titles():

			# This is an error, stop here.

			message = _("Kurs {} nicht gefunden").format(course_id)

			return_str += '<p><strong>{}</strong></p>'.format(message)

			return_str += '<p><a href="/redaktion">Zurück zum Redaktions-System</a></p>'.format(course_id)

			return_str += HTML_FOOT

			return return_str

		message = self.storage.delete_course(course_title)

		return_str += '<main class="w3-content">'

		return_str += '<p><strong>{}</strong></p>'.format(message)

		return_str += '<p><a href="/redaktion">{}</a></p>'.format(course_id, _("Zurück zum Redaktions-System"))

		return_str += '</main>'

		return_str += HTML_FOOT

		return return_str


	def learning_contents_redaktion_put(self, course_id, learning_contents, _method):
		"""PUT: Update the learning contents list of a course.
		"""

		LOGGER.debug("learning_contents_redaktion_put(course_id = '{}', learning_contents = '{}', _method='{}')".format(course_id, learning_contents, _method))

		# Luna aims at being a REST application, so we explicitly check the HTTP
		# method.
		#
		if not (_method.upper() == "PUT" or (cherrypy.serving.request.method == "PUT" and _method.upper() in ("", "PUT"))):

			# Method is unsupported.
			# 
			method = _method.upper()

			if not method:

				method = cherrypy.serving.request.method

			error = _("Die angefragte Ressource /redaktion/{}/Lern-Inhalte unterstützt die Methode '{}' nicht.").format(course_id, method)

			LOGGER.error(error)

			raise cherrypy.HTTPError(501, error)

		# Start building the page

		return_str = HTML_HEAD.format(title = _("Lern-Inhalte umsortieren"))

		course_title = self.storage.find_courses()[uuid.UUID(course_id)]

		message = self.storage.write_learning_contents_list(course_title, learning_contents)

		return_str += '<main class="w3-content">'

		return_str += '<p><strong>{}</strong></p>'.format(message)

		return_str += '<p><a href="/redaktion/{}">{}</a></p>'.format(course_id, _("Zurück zum Kurs"))

		return_str += '</main>'

		return_str += HTML_FOOT

		return return_str


	def lerninhalt_redaktion(self, course_id, learning_content_id, filename = "", content = "", _method=""):
		"""Content management of a learning content.

		This method will dispatch the handling of the request by method.
		"""

		LOGGER.debug("lerninhalt_redaktion(course_id = '{}', learning_content_id = '{}', filename = '{}', content = {}, _method='{}')".format(course_id, learning_content_id, filename, content.__class__, _method))

		# Luna aims at being a REST application, so we explicitly check the HTTP
		# method.
		#
		if _method.upper() == "GET" or (cherrypy.serving.request.method == "GET" and _method.upper() in ("", "GET")):

			return self.lerninhalt_redaktion_get(course_id, learning_content_id, message = "")

		elif _method.upper() == "POST" or (cherrypy.serving.request.method == "POST" and _method.upper() in ("", "POST")):

			return self.lerninhalt_redaktion_post(course_id, learning_content_id, filename, content)

		elif _method.upper() == "DELETE" or (cherrypy.serving.request.method == "DELETE" and _method.upper() in ("", "DELETE")):

			return self.lerninhalt_redaktion_delete(course_id, learning_content_id)

		else:

			# Request has not been handled, so the method is unsupported.
			# 
			method = _method.upper()

			if not method:

				method = cherrypy.serving.request.method

			error = _("Die angefragte Ressource /redaktion/{} unterstützt die Methode '{}' nicht.").format("/".join((course_id, learning_content_id)), method)

			LOGGER.error(error)

			raise cherrypy.HTTPError(501, error)


	def lerninhalt_redaktion_get(self, course_id, learning_content_id, message):
		"""Handler method to be called by lerninhalt_redaktion().

		GET: Display the content management frontend.
		"""

		course_title = self.storage.find_courses()[uuid.UUID(course_id)]

		learning_content_title = self.storage.get_learning_contents_titles(course_title)[learning_content_id]

		# Start building the page

		return_str = HTML_HEAD.format(title = learning_content_title)

		return_str += '<div class="redaktionssystem">'

		return_str += '<header class="w3-content">'

		return_str += '<h1 class="w3-padding w3-khaki">{1}: {0}</h1>'.format(learning_content_title,
										_("Lern-Inhalt"))

		return_str += '<nav class="w3-padding">'

		return_str += '<p><a href="/redaktion/{0}" class="nav w3-light-blue w3-padding w3-round-xlarge">&lt;&nbsp;{1}: {2}</a></p>'.format(course_id,
										_("Zum Kurs"),
										course_title)

		return_str += '</nav>'

		return_str += '</header>'

		return_str += '<main class="w3-content">'

		if message:
			return_str += '<p><strong>{}</strong></p>'.format(message)

		return_str += '<h2 class="w3-padding w3-khaki">{}</h2>'.format(_("Varianten"))

		# List variants

		variantn = self.storage.get_variants(course_title, learning_content_id)

		if not variantn:

			return_str += '<p>{}</p>'.format(_("Noch keine Varianten vorhanden."))
			return_str += '<p>{}</p>'.format(_("Lege mindestens einen Variante an, damit Luna den Lern-Inhalt darstellt."))

		else:

			modes_not_covered = [MODI.TEXT, MODI.TEXT_ZUSATZ, MODI.BILD]

			variantn.sort()

			return_str += '''<table style="width:100%;" class="w3-section">
	<thead>
		<tr>
			<th>{}</th>
			<th>{}</th>
			<th>{}</th>
			<th>{}</th>
		</tr>
	</thead>
	<tbody>'''.format(_("Datei / Ordner"), _("Format"), _("Modus"), _("Löschen"))

			for variant in variantn:

				meta_data = self.storage.get_variant_metadata(course_title,
																	learning_content_id,
																	variant)

				mode = _("Text")

				if meta_data["format"] in IMAGE_TYPES:

					mode = _("Bild")

					if MODI.BILD in modes_not_covered:

						modes_not_covered.remove(MODI.BILD)

				elif meta_data["format"] == "inode/directory":

					mode = _("Verschönerter Text")

					if MODI.TEXT_ZUSATZ in modes_not_covered:

						modes_not_covered.remove(MODI.TEXT_ZUSATZ)

				else:

					if MODI.TEXT in modes_not_covered:

						modes_not_covered.remove(MODI.TEXT)

				# TODO: Tabelle anlegen, mit Vorschau

				return_str += '''<tr>
	<td>{}</td>
	<td>{}</td>
	<td>{}</td>
	<td>
		<form action="/redaktion/{}/{}/{}"
				method="post"
				style="padding: 0px;background: none;border-radius: 0px;">
			<input type="hidden" name="_method" value="DELETE">
			<input type="submit" value="{}">
		</form>
	</td>
</tr>'''.format(variant,
				meta_data["format"],
				mode,
				course_id,
				learning_content_id,
				meta_data["identifier"],
				_("Löschen"))

			return_str += '</tbody></table>'

			if modes_not_covered:

				return_str += '<p>{}: {}</p>'.format(_("Diese Varianten fehlen noch"),
														", ".join([{MODI.TEXT: _("Text"),
																	MODI.TEXT_ZUSATZ: _("Verschönerter Text"),
																	MODI.BILD: _("Bild")}[current_mode] for current_mode in modes_not_covered]))

		# Form to create a variant

		return_str += '<h2 class="w3-padding w3-khaki">{}</h2>'.format(_("Variante anlegen"))

		return_str += '<h3 class="w3-padding w3-khaki">{}</h3>'.format(_("HTML-Datei direkt anlegen"))

		return_str += '<form action="/redaktion/{}/{}" method="post" class="w3-padding-large w3-light-grey">'.format(course_id, learning_content_id)

		return_str += '<p><label for="filename">{}</label>: '.format(_("Dateiname"))

		return_str += '<input type="text" name="filename" id="filename" value=".html"><br>{}</p>'.format(_("Erlaubte Zeichen: Buchstaben, Zahlen, Leerzeichen, Bindestrich, Unterstrich, Punkt"))

		return_str += '<p><label for="content">{}</label>:<br>'.format(_("Inhalt"))

		return_str += '<textarea name="content" id="content" rows="10" cols="80"></textarea></p>'

		return_str += '<input type="submit" value="{}">'.format(_("Anlegen"))
		return_str += '</form>'

		# Form to upload a file as variant

		return_str += '<h3 class="w3-padding w3-khaki">{}</h3>'.format(_("Datei hochladen"))

		return_str += '<form action="/redaktion/{}/{}" method="post" enctype="multipart/form-data" class="w3-padding-large w3-light-grey">'.format(course_id, learning_content_id)

		return_str += '<p><label for="file">{}</label>: '.format(_("Datei auswählen"))

		return_str += '<input type="file" name="content" id="file"></p>'

		return_str += '<p>Dann diesen Knopf klicken:</p>'

		return_str += '<input type="submit" value="{}">'.format(_("Jetzt hochladen"))
		return_str += '</form>'

		# Form to upload a directory as variant

		return_str += '<h3 class="w3-padding w3-khaki">{}</h3>'.format(_("Verzeichnis hochladen"))

		return_str += '<form action="/redaktion/{}/{}" method="post" enctype="multipart/form-data" class="w3-padding-large w3-light-grey">'.format(course_id, learning_content_id)

		return_str += '<p><label for="directory">{}</label>: '.format(_("Verzeichnis auswählen"))

		return_str += '<input type="file" name="content" id="directory" directory="" webkitdirectory=""></p>'

		return_str += '<p>Dann diesen Knopf klicken:</p>'

		return_str += '<input type="submit" value="{}">'.format(_("Jetzt hochladen"))
		return_str += '</form>'

		return_str += '<!-- Ende redaktionssystem --></div>'

		return_str += '</main>'

		return_str += HTML_FOOT

		return return_str


	def lerninhalt_redaktion_post(self, course_id, learning_content_id, filename, content):
		"""Handler method to be called by lerninhalt_redaktion().

		POST: Create a new variant using filename and content, and then display the content management frontend.
			content can be used to upload a file, or a directory of files.
			In this case, filename will be taken from content.filename .
		"""

		LOGGER.debug('POST lerninhalt_redaktion(course_id = "{}", learning_content_id = "{}", filename = "{}", content = {})'.format(course_id, learning_content_id, filename, content.__class__))

		message = ""

		if not content or (content.__class__ == str and not content.strip()):

			# This is an error, stop here.

			message = _("Kann Variante nicht anlegen: Kein Inhalt.")

			# After processing POST, render the page as if GET was called,
			# plus a message.
			#
			return self.lerninhalt_redaktion_get(course_id, learning_content_id, message)

		# Apparently we have content.
		#
		if filename:

			message = check_title(os.path.splitext(filename)[0])

		else:
			# So it's a file, or multiple files in a directory.

			# Check the filename(s) first.

			if content.__class__ == list:

				# Got a directory

				filename = []

				# Every filename must obey the rules
				#
				for upload in content:

					result = check_title(os.path.splitext(os.path.basename(upload.filename))[0])

					if result:

						message = result

					else:

						filename.append(upload.filename)

			else:

				# Infer filename from the object given.
				#
				filename = content.filename

				message = check_title(os.path.splitext(filename)[0])

		if message:

			# This is an error, stop here.

			# After processing POST, render the page as if GET was called,
			# plus a message.
			#
			return self.lerninhalt_redaktion_get(course_id, learning_content_id, message)

		# Next, write the file(s) to disk.

		file_format = self.storage.write_variant(course_id, learning_content_id, content, filename)

		# TODO: Could be beautified if filename is a list
		#
		message = '{}: {} ({})'.format(filename, _("Variante angelegt:"), file_format)

		# After processing POST, render the page as if GET was called,
		# plus a message.
		#
		return self.lerninhalt_redaktion_get(course_id, learning_content_id, message)


	def lerninhalt_redaktion_delete(self, course_id, learning_content_id):
		"""Handler method to be called by lerninhalt_redaktion().

		DELETE: Check and handle a deletion.
		"""

		# Start building the page

		return_str = HTML_HEAD.format(title = _("Lern-Inhalt löschen"))

		message = ""

		course_title = self.storage.find_courses()[uuid.UUID(course_id)]

		if learning_content_id not in self.storage.get_learning_contents(course_title):

			# This is an error, stop here.

			message = _("Lern-Inhalt {} nicht gefunden").format(learning_content_id)

			return_str += '<p><strong>{}</strong></p>'.format(message)

			return_str += '<p><a href="/redaktion/{}">Zurück zum Kurs</a></p>'.format(course_id)

			return_str += HTML_FOOT

			return return_str

		message = self.storage.delete_learning_content(course_title, learning_content_id)

		return_str += '<main class="w3-content">'

		return_str += '<p><strong>{}</strong></p>'.format(message)

		return_str += '<p><a href="/redaktion/{}">{}</a></p>'.format(course_id, _("Zurück zum Kurs"))

		return_str += '</main>'

		return_str += HTML_FOOT

		return return_str


	def variant_redaktion(self, course_id, learning_content_id, variant_id, filename = "", content = "", _method=""):
		"""Content management of a variant.

		This method will dispatch the handling of the request by method.

		DELETE: Delete the variant.
		"""

		# Luna aims at being a REST application, so we explicitly check the HTTP
		# method.
		#
		if _method.upper() == "DELETE" or (cherrypy.serving.request.method == "DELETE" and _method.upper() in ("", "DELETE")):

			return self.variant_redaktion_delete(course_id, learning_content_id, variant_id)

		else:

			# Request has not been handled, so the method is unsupported.
			# 
			method = _method.upper()

			if not method:

				method = cherrypy.serving.request.method

			error = _("Die angefragte Ressource /redaktion/{} unterstützt die Methode '{}' nicht.").format("/".join((course_id, learning_content_id, variant_id)), method)

			LOGGER.error(error)

			raise cherrypy.HTTPError(501, error)


	def variant_redaktion_delete(self, course_id, learning_content_id, variant_id):
		"""Handler method to be called by variant_redaktion().

		DELETE: Check and handle a deletion.
		"""

		# Start building the page

		return_str = HTML_HEAD.format(title = _("Variante löschen"))

		LOGGER.debug("variant_redaktion_delete(course_id = '{}', learning_content_id = '{}', variant_id = '{}')".format(course_id, learning_content_id, variant_id))

		course_title = self.storage.find_courses()[uuid.UUID(course_id)]

		message = self.storage.delete_variant(course_title, learning_content_id, variant_id)

		if not message:

			LOGGER.info("Attempting to delete non-existing variant: {}".format(variant_id))

			message = _("Variante nicht gefunden!")

		return_str += '<main class="w3-content">'

		return_str += '<p><strong>{}</strong></p>'.format(message)

		return_str += '<p><a href="/redaktion/{}/{}">{}</a></p>'.format(course_id, learning_content_id, _("Zurück zum Lern-Inhalt"))

		return_str += '</main>'

		return_str += HTML_FOOT

		return return_str

def main():
	"""Main function, for IDE convenience.
	"""

	root = WebApp()

	config_dict = {"/" : {"tools.sessions.on" : True,
							"tools.sessions.timeout" : 60},
					"global" : {"server.socket_host" : "127.0.0.1",
								"server.socket_port" : PORT,
								"server.thread_pool" : THREADS,
								"request.show_tracebacks" : False}}

	if ADDITIONAL_CONFIG:

		LOGGER.debug("Updating config with additional config: {}".format(ADDITIONAL_CONFIG))

		# A simple update may overwrite settings.
		# So, update sub-dicts first.
		#
		keys_to_pop = []

		for key in ADDITIONAL_CONFIG.keys():

			if key in config_dict.keys():

				config_dict[key].update(ADDITIONAL_CONFIG[key])

				keys_to_pop.append(key)

		for key in keys_to_pop:

			ADDITIONAL_CONFIG.pop(key)

		config_dict.update(ADDITIONAL_CONFIG)

	LOGGER.info("Final CherryPy config: {}".format(config_dict))

	# Conditionally turn off Autoreloader
	#
	if not AUTORELOAD:

		cherrypy.engine.autoreload.unsubscribe()

	cherrypy.quickstart(root, config=config_dict)

	return

if __name__ == "__main__":

	main()
