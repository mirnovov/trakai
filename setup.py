"""
The MIT License (MIT)

Copyright (c) 2020 novov

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the "Software"), to deal in the
Software without restriction, including without limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom
the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or
substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT
NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT
OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import re, os, setuptools

def getVersion():
	path = os.path.join(os.path.dirname(__file__),"trakai","version.py")
	with open(path, "r", encoding="utf-8") as file:
		version = re.search("__version__ = ['\"]((\d|\w|\.)+)[\"']",file.read())
		
		if version: return version[1]
		else: return None
		
def getReadMe():
	path = os.path.join(os.path.dirname(__file__),"README.md")
	with open(path, "r", encoding="utf-8") as file:
		return file.read()

setuptools.setup(
	name = "trakai",
	version = getVersion(),
	author = "novov",
	author_email = "anon185441@gmail.com",
	description = "A simple blog generator designed specially to integrate into existing sites.",
	long_description = getReadMe(),
	long_description_content_type = "text/markdown",
	url = "https://novov.neocities.org/projects/trakai.html",
	packages = ["trakai"],
	package_data = {
		"trakai": ["templates/*.html", "templates/*.xml"],
	},
	license = "MIT",
	classifiers = [
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
		"Development Status :: 3 - Alpha",
		"Topic :: Internet :: WWW/HTTP",
		"Topic :: Internet :: WWW/HTTP :: Site Management"
	],
	python_requires = ">=3.6",
	install_requires = [
		"jinja2>=2.11.0",
		"markdown>=3.3.0"
	],
	entry_points = {
		"console_scripts": [
			"trakai=trakai.__main__:main"
		]
	}
)