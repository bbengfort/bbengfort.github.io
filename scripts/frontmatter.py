#!/usr/bin/env python3

import os
import re
import glob
import yaml
import argparse

from copy import deepcopy
from datetime import datetime
from collections import Counter


# Path helpers
PROJECT = os.path.relpath(os.path.join(os.path.dirname(__file__), ".."))
CONTENT = os.path.join(PROJECT, "content")
POSTS = os.path.join(CONTENT, "posts")
MDRE = re.compile(r'^(\d{4}-\d{2}-\d{2})-([a-zA-Z0-9\-]+)\.md$', re.I)


class Frontmatter(object):
    """
    A front-matter object that knows how to read and write front-matter from documents.
    """

    def __init__(self, path, outpath=None):
        self.path = path
        self.outpath = outpath or path
        self.updated = False
        self._frontmatter = {}
        self._content = []

    @property
    def frontmatter(self):
        return self._frontmatter

    @frontmatter.setter
    def frontmatter(self, fm):
        self.updated = self._frontmatter != fm
        self._frontmatter = fm

    def _pathparse(self):
        match = MDRE.match(os.path.basename(self.path))
        if match is None:
            self._pathslug = None
            self._pathdate = None
            return
        dt, self._pathslug = match.groups()
        self._pathdate = datetime.strptime(dt, "%Y-%m-%d").date()

    @property
    def pathdate(self):
        if not hasattr(self, "_pathdate"):
            self._pathparse()
        return self._pathdate

    @property
    def pathslug(self):
        if not hasattr(self, "_pathslug"):
            self._pathparse()
        return self._pathslug

    def __enter__(self):
        fm = []
        infe = False

        with open(self.path, 'r') as f:
            for line in f:
                if line.strip() == "---":
                    infe = not infe
                    continue

                if infe:
                    fm.append(line)
                else:
                    self._content.append(line)

        self._frontmatter = yaml.safe_load("\n".join(fm))
        return self

    def __exit__(self, *args, **kwargs):
        if self.updated:
            with open(self.outpath, 'w') as f:
                f.write("---\n")
                yaml.dump(self.frontmatter, f)
                f.write("---\n")
                for line in self._content:
                    f.write(line)
        return None


def expandpaths(*paths):
    for path in paths:
        if os.path.isdir(path):
            for child in glob.glob(os.path.join(path, "*.md")):
                yield child
        elif os.path.isfile(path):
            yield path


def audit(args):
    counts = Counter()
    for path in expandpaths(*args.src):
        counts["files"] += 1
        with Frontmatter(path) as f:
            for key in f.frontmatter:
                counts[key] += 1

            if f.pathdate is not None:
                counts["pathdate"] += 1

            if f.pathslug is not None:
                counts["pathslug"] += 1

    nfiles = counts.pop("files")
    print(f"audited {nfiles} files")
    for key, count in counts.most_common():
        print(f"  - {key}: {count} ({(count/nfiles)*100:0.2f}%)")


def update(args):
    nfiles = 0
    for path in expandpaths(*args.src):
        outpath = None
        if args.outdir:
            outpath = os.path.join(args.outdir, os.path.basename(path))

        with Frontmatter(path, outpath=outpath) as f:
            fm = deepcopy(f.frontmatter)

            if not args.no_defaults:
                fm["showtoc"] = False
                fm["draft"] = False

            if not f.pathdate or not f.pathslug:
                print(f"unhandled path components in '{path}'")
                continue

            if not args.no_slug:
                fm["slug"] = f.pathslug

            if not args.no_alias:
                category = fm.get("categories", None)
                if not category or not isinstance(category, str):
                    print(f"unhandled category in '{path}'")
                    continue

                datepath = f.pathdate.strftime("%Y/%m/%d")

                fm["aliases"] = [
                    os.path.join("/", category, datepath, f"{f.pathslug}.html"),
                ]

            f.frontmatter = fm

        nfiles += 1

    print(f"updated {nfiles} files")


if __name__ == "__main__":
    cmds = {
        "audit": {
            "func": audit,
            "help": "audit the front-matter in posts",
            "args": {
                "src": {
                    "nargs": "*", "default": [POSTS],
                    "help": "specify the directory to audit front-matter for",
                },
            },
        },
        "update": {
            "func": update,
            "help": "update the front-matter to sane defaults",
            "args": {
                ("-S", "--no-slug"): {
                    "action": "store_true", "help": "do not update slug field",
                },
                ("-A", "--no-alias"): {
                    "action": "store_true", "help": "do not update aliases",
                },
                ("-D", "--no-defaults"): {
                    "action": "store_true", "help": "do not update draft/showtoc defaults",
                },
                ("-o", "--outdir"): {
                    "default": None, "metavar": "DIR", "type": str,
                    "help": "write modified files to specified path",
                },
                "src": {
                    "nargs": "*", "default": [POSTS],
                    "help": "specify the directory to audit front-matter for",
                },
            },
        },
    }


    parser = argparse.ArgumentParser(
        description="global site management utilities for frontmatter",
        epilog="this tool may edit posts, please check git diffs carefully!"
    )
    subparsers = parser.add_subparsers(
        title="commands", description="frontmatter utilities and helpers"
    )

    for cmd, cargs in cmds.items():
        subparser = subparsers.add_parser(cmd, help=cargs["help"])
        subparser.set_defaults(func=cargs["func"])
        for pargs, kwargs in cargs["args"].items():
            if isinstance(pargs, str):
                pargs = (pargs,)
            subparser.add_argument(*pargs, **kwargs)


    args = parser.parse_args()
    try:
        args.func(args)
    except Exception as e:
        parser.error(str(e))
