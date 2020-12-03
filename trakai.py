#!/usr/bin/env python3

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

import os, shutil, re, sys, json, datetime, time, math, pathlib, markdown, html
from jinja2 import Environment, FileSystemLoader
from html.parser import HTMLParser

def fread(filename):
    with open(filename, 'r') as f: return f.read()

def fwrite(filename, text):
    basedir = os.path.dirname(filename)
    if not os.path.isdir(basedir) and basedir != '':
        os.makedirs(basedir)
    with open(filename, 'w') as f: f.write(text)

def log(msg, *args):
    sys.stderr.write(msg.format(*args) + '\n')
    
def readHeaders(text):
    for match in re.finditer(r'\s*<!--\s*(.+?)\s*:\s*(.+?)\s*-->\s*|.+', text):
        if not match.group(1): break
        yield match.group(1), match.group(2), match.end()

def formatDate(date_str,kind):
    d = datetime.datetime.strptime(date_str, '%Y-%m-%d')
    
    if kind == "rfc822": return d.strftime('%a, %d %b %Y %H:%M:%S +0000')
    elif kind == "rfc3399": return d.isoformat()
    else: return '{} {}, {}'.format(d.day,d.strftime("%B"),d.year)

def readContent(filename):
    text = fread(filename)
    content = {}
    
    if filename.endswith(('.md', '.markdown')):
        md = markdown.Markdown(extensions=gl("markdown_extensions"))
        try:
            text = md.convert(text)
            for k, v in md.Meta.items(): 
                if len(v) > 1: content[k] = "\n".join(v)
                else: content[k] = v[0]
        except ImportError as e:
            log('WARNING: Cannot render Markdown in {}: {}', filename, str(e))
            
    if 'tags' in content and gl('has_tags'): 
        content['tags'] = list(map(lambda x: x.strip().replace(" ",""),content['tags'].split(",")))
            
    elif filename.endswith(('.html', '.htm')):
         e = 0
         for k, v, e in readHeaders(text): content[k] = v
         text = text[e:]
         
    if "<!-- nvpr -->" in text:
        content["preview"] = re.sub("<a ?.*?>|<\/a>","",text.split("<!-- nvpr -->")[0])

    return {
        **content,
        'name': os.path.splitext(os.path.split(filename)[1])[0],
        'prose': text,
        'rfc822_date': formatDate(content['date'],"rfc822"),
        'rfc3399_date': formatDate(content['date'],"rfc3399"),
        'neat_date': formatDate(content['date'],"neat"),
        'page_mode': "post"
    }

def makePages(src, dst, layout):
    items = []
    tags = set([])
    temp = env.get_template(layout) 

    # Load layouts.
    with os.scandir(src) as folder:
        for item in folder:
            if not item.is_file() or item.name == '.DS_Store': continue
            
            content = readContent(item.path)
            items.append(content)
            if 'tags' in content and gl('has_tags'): tags.update(content['tags'])
            
        if gl('has_tags'): 
            env.globals['all_tags'] = sorted(tags)
            
        for content in items:
            dst_path = os.path.join(dst,'{}.html'.format(content['name']))
            
            content['path'] = '/' + dst_path
            output = temp.render(content)

            log('Rendering {} => {} ...', item.path, dst_path)
            fwrite(dst_path, output)

    return sorted(items, key=lambda x: x['date'], reverse=True)

def makeList(posts, dst, layout, **params):
    temp = env.get_template(layout) 
       
    page_params = {
        'posts': posts,
        'path': '/' + dst,
        'name': 'blogindex',
        **params
    }
    output = temp.render(page_params)
    
    log('Rendering list => {} ...', dst)
    fwrite(dst, output)
    
def makePaginatedList(posts, dst, layout, **params): 
    i, r, pagenum = 0, 2, 1
    pages = [os.path.join(dst,'index.html')]
    
    while r < math.ceil(9 / gl('page_limit')):
        pages.append(os.path.join(dst,'pages','{}.html'.format(r)))
        r += 1

    while i < len(posts):
       makeList(posts[i:i + gl('page_limit')],
                 pages[pagenum - 1],
                 'list.html',
                 name='blogindex{}'.format(pagenum),
                 pagenum=pagenum,
                 pages=pages,
                 pagecount=len(pages),
                 **params)
        
       i += gl('page_limit')
       pagenum += 1
   
def insertPreview(post, dst, layout):
    class PreviewFinder(HTMLParser):
        start, end, tag, nest = None, None, None, 0
        
        def handle_starttag(self, tag, attrs):
            if gl('preview_class') in self.getClasses(attrs): 
                self.start = self.getpos()[0] - 1
                self.tag = tag 
                
            elif tag == self.tag: self.nest += 1
    
        def handle_endtag(self, tag):
            if self.tag is not None and self.tag == tag:
                if self.nest == 0: self.end = self.getpos()[0] - 1
                elif self.nest > 0: self.nest -= 1
        
        def getClasses(self,attrs):
            classes = list(filter(lambda x: x[0] == 'class', attrs))
            return classes[0][1].split(" ") if classes else []
    
    page = fread(dst)
    fwrite(os.path.join(gl('backup_path'),"index." + str(time.time())[:7] + ".html"), page)
    
    parser = PreviewFinder()
    parser.feed(page)
    page = page.split("\n")    
    page[parser.start] += "\n" + env.get_template(layout).render(post=post)
    
    del page[parser.start + 1 : parser.end] #delete remaining old lines
    log('Inserting preview => {} ...', dst)
    fwrite(dst,"\n".join(page))
    
def getTaggedPosts(posts):
    tags = { tag : [] for tag in list(gl('all_tags')) }
    
    for post in posts: 
        if 'tags' not in post: continue
        for tag in post['tags']:
            tags[tag].append(post)
                
    return tags
    
def gl(key,path=False):
    return env.globals[key]

def main():
    global env
    
    # Default parameters.
    params = {
        'site_path': os.path.split(os.path.split(os.path.realpath(__file__))[0])[0],
        'posts_path': 'resources/content',
        'templates_path': 'resources/templates',
        'backup_path': 'resources/backup',
        'output_path': 'blog',
        'blog_title': 'Blog',
        'site_url': 'http://www.example.com',
        'feed_description': 'Placeholder Description',
        'current_year': datetime.datetime.now().year,
        'has_pagination': False,
        'has_tag_pagination': False,
        'page_limit': 5,
        'markdown_extensions': ['def_list','admonition','tables'], #meta is always loaded, see below
        'has_preview': False,
        'preview_class': None,
        'has_archive': False,
        'has_tags': False,
        'has_feed': True
    }
    parampath = os.path.split(os.path.realpath(__file__))[0] + '/trakai.json'
    
    # Set working directory, and if params.json exists, load it
    if os.path.isfile(parampath): params.update(json.loads(fread(parampath)))
    
    params['markdown_extensions'].append('meta') #meta should always be loaded
    if params['site_path'] is not None: os.chdir(params['site_path'])
    
    # Set up Jinja, and load layouts.
    env = Environment(
        loader = FileSystemLoader(params['templates_path']),
        autoescape = False
    )
    env.globals = params 
    
    # Create a new blog directory from scratch, and create blog posts
    if os.path.isdir(gl('output_path')): shutil.rmtree(gl('output_path'))
    posts = makePages(gl('posts_path'),os.path.join(gl('output_path'),'posts'), 'post.html')

    # Create blog indices.    
    if gl('has_pagination'): makePaginatedList(posts, gl('output_path'), 'list.html', page_mode="regular")
    else: makeList(posts, os.path.join(gl('output_path'),'index.html'), 'list.html', page_mode="regular")
   
    if gl('has_feed'): makeList(posts,os.path.join(gl('output_path'),'feed.xml'),'feed.xml',page_mode="feed")
    if gl('has_archive'): makeList(posts,os.path.join(gl('output_path'),'archive.html'), 'list.html', page_mode="archive")
    if gl('has_preview'): insertPreview(posts[0],'index.html','excerpt.html')
    
    if gl('has_tags'):
        tags = getTaggedPosts(posts)
        for tag in tags:
            if gl('has_tag_pagination'): 
                 makePaginatedList(tags[tag], os.path.join(gl('output_path'),'tags/{}/'.format(tag.lower())), 'list.html', page_mode='tags', current_tag=tag)
            else:  
                makeList(tags[tag], os.path.join(gl('output_path'),'tags/{}.html'.format(tag.lower())), 'list.html', page_mode='tags', current_tag=tag)
    

if __name__ == '__main__': main()

