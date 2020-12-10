# The MIT License (MIT)
#
# Copyright (c) 2018 Sunaina Pai, 2020 novov
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the "Software"), to deal in the
# Software without restriction, including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom
# the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or
# substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT
# NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT
# OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import os, json, shutil, datetime, argparse
from os import path
from jinja2 import Environment, FileSystemLoader
from .output import *
from .parsing import fread, log
from .version import __version__

def main():
    # Default parameters.
    params = {
        "site_path": os.getcwd(),
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
        "has_feed": True
    }
    parampath = params["site_path"] + "/resources/trakai.json"
    
    # Set working directory, and if params.json exists, load it
    if path.isfile(parampath): 
        params.update(json.loads(fread(parampath)))
    
    params["markdown_extensions"].append("meta") #meta should always be loaded
    
    # Set up Jinja, and load layouts.
    env = Environment(
        loader = FileSystemLoader(params["templates_path"]),
        autoescape = False
    )
    env.globals = params 
    
    # Create a new blog directory from scratch, and create blog posts
    if path.isdir(env.globals["output_path"]): 
        shutil.rmtree(env.globals["output_path"])
    
    posts = makePages(env,env.globals["posts_path"], path.join(env.globals["output_path"],"posts"), "post.html")

    # Create blog indices.    
    if env.globals["has_pagination"]: 
        makePaginatedList(env,posts, env.globals["output_path"], "list.html", page_mode="regular")
    else: 
        makeList(env,posts, path.join(env.globals["output_path"],"index.html"), "list.html", page_mode="regular")
   
    if env.globals["has_feed"]: 
        makeList(env,posts,path.join(env.globals["output_path"],"feed.xml"),"feed.xml",page_mode="feed")
        
    if env.globals["has_archive"]: 
        makeList(env,posts,path.join(env.globals["output_path"],"archive.html"), "list.html", page_mode="archive")
        
    if env.globals["has_preview"]: 
        insertPreview(env,posts[0],"index.html","excerpt.html")
    
    if env.globals["has_tags"]:
        tags = getTaggedPosts(env,posts)
        for tag in tags:
            if env.globals["has_tag_pagination"]: 
                 makePaginatedList(tags[tag], path.join(env.globals["output_path"],"tags/{}/".format(tag.lower())), "list.html", page_mode="tags", current_tag=tag)
            else:  
                makeList(env,tags[tag], path.join(env.globals["output_path"],"tags/{}.html".format(tag.lower())), "list.html", page_mode="tags", current_tag=tag)
    

if __name__ == "__main__": main()

