"""
The MIT License (MIT)

Copyright (c) 2018 Sunaina Pai, 2020 novov

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

import os, re, sys, datetime, markdown
from .utils import fread, fwrite, log
	
def readHeaders(text):
	for match in re.finditer(r"\s*<!--\s*(.+?)\s*:\s*(.+?)\s*-->\s*|.+", text):
		if not match.group(1): break
		yield match.group(1), match.group(2), match.end()

def formatDate(date_str,kind):
	d = datetime.datetime.strptime(date_str, "%Y-%m-%d")
	
	if kind == "rfc822": return d.strftime("%a, %d %b %Y %H:%M:%S +0000")
	elif kind == "rfc3399": return d.isoformat()
	else: return "{} {}, {}".format(d.day,d.strftime("%B"),d.year)

def readContent(env, filename):
	text = fread(filename)
	content = {}
	
	if filename.endswith((".md", ".markdown")):
		md = markdown.Markdown(extensions=env.globals["markdown_extensions"])
		try:
			text = md.convert(text)
			for k, v in md.Meta.items(): 
				if len(v) > 1: content[k] = "\n".join(v)
				else: content[k] = v[0]
		except ImportError as e:
			log(env,"WARNING: Cannot render Markdown in {}: {}", filename, str(e))
	elif filename.endswith((".html", ".htm")):
		 e = 0
		 for k, v, e in readHeaders(text): content[k] = v
		 text = text[e:]
			
	if "tags" in content and env.globals["has_tags"]: 
		content["tags"] = list(map(lambda x: x.strip().replace(" ",""),content["tags"].split(",")))
	
	print(content)
			
	if "date" not in content:
		content["date"] = datetime.datetime.fromtimestamp(stat.ST_MTIME).strftime("%Y-%m-%d")
		 
	if "<!-- nvpr -->" in text:
		content["preview"] = re.sub("<a ?.*?>|<\/a>","",text.split("<!-- nvpr -->")[0])

	return {
		**content,
		"name": os.path.splitext(os.path.split(filename)[1])[0],
		"prose": text,
		"rfc822_date": formatDate(content["date"],"rfc822"),
		"rfc3399_date": formatDate(content["date"],"rfc3399"),
		"neat_date": formatDate(content["date"],"neat"),
		"page_mode": "post"
	}