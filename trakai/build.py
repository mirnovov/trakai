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

import os, json, datetime, shutil
from os import path
from jinja2 import Environment, FileSystemLoader
from .output import makePages, makeList, makePaginatedList, insertPreview, getTaggedPosts
from .utils import fread, log
from .version import __version__

def setupSite(**args):
	os.chdir(args["path"])
	
	# default parameters
	params = {
		"posts_path": "resources/content",
		"templates_path": "resources/templates",
		"backup_path": "resources/backup",
		"output_path": "blog",
		"blog_title": "Blog",
		"site_url": "http://www.example.com",
		"feed_description": "Placeholder Description",
		"current_year": datetime.datetime.now().year,
		"has_pagination": False,
		"has_tag_pagination": False,
		"page_limit": 5,
		"markdown_extensions": ["def_list","admonition","tables"], #meta is always loaded, see below
		"has_preview": False,
		"preview_class": None,
		"has_archive": False,
		"has_tags": False,
		"has_feed": True,
		"has_caching": False,
		"cache_path": "resources/backup/trakai_cache.json",
	}
	
	# if params.json exists, load it
	if path.isfile(args["config"]):
		with open(args["config"], "r") as file: 
			params.update(json.load(file))
	
	params["markdown_extensions"].append("meta") #meta should always be loaded
	
	#add non-configurable global values. this uses the same object to save memory/effort,
	#though a bespoke solution may be a good future addition
	params.update({
		"site_path": args["path"],
		"__silent": args["silent"]
	})
	
	#override caching if set in args
	if args["cache"]:
		params["has_caching"] = True
	elif not args["nocache"]:
		params["has_caching"] = False
			
	# set up Jinja, and load layouts.
	env = Environment(
		loader = FileSystemLoader([
			params["templates_path"],
			path.dirname(__file__) + "/templates/"
		]),
		autoescape = False
	)
	env.globals = params 
	
	# create a new blog directory from scratch, and create blog posts
	if path.isdir(env.globals["output_path"]) and not env.globals["has_caching"]: 
		shutil.rmtree(env.globals["output_path"])
	
	#finally, generate site content
	generateSite(env)
	return env
	
def generateSite(env):
	feed_path = path.join(env.globals["output_path"],"feed.xml")
	archive_path = path.join(env.globals["output_path"],"archive.html")
	posts = makePages(env,env.globals["posts_path"], path.join(env.globals["output_path"],"posts"), "post.html")
	    
	if env.globals["has_pagination"]: 
		makePaginatedList(env, posts, env.globals["output_path"], "list.html", page_mode="regular")
	else: 
		makeList(env,posts,path.join(env.globals["output_path"],"index.html"), "list.html", page_mode="regular")

	if env.globals["has_feed"]: 
		makeList(env,posts,feed_path,"feed.xml",page_mode="feed")
		
	if env.globals["has_archive"]: 
		makeList(env,posts,archive_path, "list.html", page_mode="archive")
		
	if env.globals["has_preview"]: 
		insertPreview(env,posts[0],"index.html","excerpt.html")
	
	if env.globals["has_tags"]:
		tags = getTaggedPosts(env,posts)
		for tag in tags:
			if env.globals["has_tag_pagination"]: 
				 makePaginatedList(env, tags[tag], path.join(env.globals["output_path"],"tags/{}/".format(tag.lower())), "list.html", page_mode="tags", current_tag=tag)
			else:  
				makeList(env, tags[tag], path.join(env.globals["output_path"],"tags/{}.html".format(tag.lower())), "list.html", page_mode="tags", current_tag=tag)
				
	return posts
