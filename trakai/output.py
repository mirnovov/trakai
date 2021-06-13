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

import os, time, math, html, json, hashlib
from html.parser import HTMLParser
from .parsing import readContent
from .utils import log, fread, fwrite

def checkCache(env,cache,content):	
	name = content["name"]
	hash = hashlib.md5(str(content).encode("utf-8")).hexdigest()
	path = content["path"][1:]
	
	if name in cache and cache[name] == hash and os.path.isfile(path): 
		log(env,"Rendering skipped for {} (cached) ...", path)
		return True
	
	cache[name] = hash
	return False
	
def initCache(path):
	if not os.path.isfile(path):
		fwrite(path,"")
		return {}
	with open(path, "r") as file: 
		return json.load(file)
		
def updateCache(cache,path):
	with open(path, "w") as file: 
		json.dump(cache,file)

def makePages(env, src, dst, layout):
	items = []
	tags = set([])
	temp = env.get_template(layout)
	cache = initCache(env.globals["cache_path"]) if env.globals["has_caching"] else None
	
	# Load layouts.
	with os.scandir(src) as folder:
		for item in folder:
			if not item.is_file() or item.name == ".DS_Store": continue
			
			content = readContent(env,item.path)
			items.append(content)
			if "tags" in content and env.globals["has_tags"]: tags.update(content["tags"])
			
		if env.globals["has_tags"]: 
			env.globals["all_tags"] = sorted(tags)
			
		for content in items:			
			content["path"] = os.path.join("/",dst,"{}.html".format(content["name"]))
			
			if env.globals["has_caching"] and checkCache(env,cache,content): 
				continue
				
			output = temp.render(content)

			log(env,"Rendering => {} ...", content["path"][1:])
			fwrite(content["path"][1:], output)
			
	if env.globals["has_caching"]:
		updateCache(cache,env.globals["cache_path"])

	return sorted(items, key=lambda x: x["date"], reverse=True)

def makeList(env, posts, dst, layout, **params):
	temp = env.get_template(layout) 
	   
	page_params = {
		"posts": posts,
		"path": "/" + dst,
		"name": "blogindex",
		**params
	}
	output = temp.render(page_params)
	
	log(env,"Rendering list => {} ...", dst)
	fwrite(dst, output)
	
def makePaginatedList(env, posts, dst, layout, **params): 
	i, r, pagenum = 0, 2, 1
	pages = [os.path.join(dst,"index.html")]

	while r <= math.ceil(len(posts) / env.globals["page_limit"]):
		pages.append(os.path.join(dst,"pages","{}.html".format(r)))
		r += 1

	while i < len(posts):
		makeList(env,
				posts[i:i + env.globals["page_limit"]],
				pages[pagenum - 1],
				"list.html",
				name="blogindex{}".format(pagenum),
				pagenum=pagenum,
				pages=pages,
				pagecount=len(pages),
				**params)
		
		i += env.globals["page_limit"]
		pagenum += 1
		
def insertPreview(env, post, dst, layout):
	class PreviewFinder(HTMLParser):
		start, end, tag, nest = None, None, None, 0
		
		def handle_starttag(self, tag, attrs):
			if env.globals["preview_class"] in self.getClasses(attrs): 
				self.start = self.getpos()[0] - 1
				self.tag = tag 
				
			elif tag == self.tag: self.nest += 1
	
		def handle_endtag(self, tag):
			if self.tag is not None and self.tag == tag:
				if self.nest == 0: self.end = self.getpos()[0] - 1
				elif self.nest > 0: self.nest -= 1
		
		def getClasses(self,attrs):
			classes = list(filter(lambda x: x[0] == "class", attrs))
			return classes[0][1].split(" ") if classes else []
	
	page = fread(dst)
	fwrite(os.path.join(env.globals["backup_path"],"index." + str(time.time())[:7] + ".html"), page)
	
	parser = PreviewFinder()
	parser.feed(page)
	page = page.split("\n")    
	page[parser.start] += "\n" + env.get_template(layout).render(post=post)
	
	del page[parser.start + 1 : parser.end] #delete remaining old lines
	log(env,"Inserting preview => {} ...", dst)
	fwrite(dst,"\n".join(page))
	
def getTaggedPosts(env,posts):
	tags = { tag : [] for tag in list(env.globals["all_tags"]) }
	
	for post in posts: 
		if "tags" not in post: continue
		for tag in post["tags"]:
			tags[tag].append(post)
				
	return tags