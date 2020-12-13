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

import argparse, os
from .version import __version__
from .build import setupSite

def checkPath(path):
    if not path or not os.path.exists(path):
        raise argparse.ArgumentTypeError(path + "is not a valid path")
    return path
    
def checkDir(path):
    checkPath(path)
    
    if not os.path.isdir(path): 
        raise argparse.ArgumentTypeError(path + "is not a directory")
    return path
    
def main():
    parser = argparse.ArgumentParser(prog="trakai", description="a simple blog generator designed specially to integrate into existing sites")
    
    parser.add_argument("path", nargs="?", default=os.getcwd(), type=checkDir, help="the path of the site; defaults to the current directory")
    parser.add_argument("-v","--version", action="version", version="trakai v" + __version__, help="outputs the installed version")
    parser.add_argument("-s","--silent", action="store_true", help="generates the site without printing information to stdout")
    parser.add_argument("-a", "--cache", action="store_true", help="always use the cache, regardless of config, and only write changed files")
    parser.add_argument("-n", "--nocache", action="store_false", help="never use the cache, regardless of config, and write all files")
    parser.add_argument("-c", "--config", default=None, type=checkPath, help="specifies an alternate location for configuration files")
    
    args = vars(parser.parse_args())
    
    if args["cache"] and not args["nocache"]:
        print("trakai: error: cache and nocache are mutually exclusive")
        exit(1)
    
    elif args["config"] is None: 
        args["config"] = "resources/trakai.json"
        
    setupSite(**args)
    
if __name__ == "__main__": main()

