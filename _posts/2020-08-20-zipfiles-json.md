---
layout: post
title:  "Writing JSON into a Zip file with Python"
date:   2020-08-20 11:41:14 -0400
categories: snippets
---

For scientific reproducibility, it has become common for me to output experimental results as zip files that contain both configurations and inputs as well as one or more output results files. This is similar to .epub or .docx formats which are just specialized zip files - and allows me to easily rerun experiments for comparison purposes. Recently I tried to dump some json data into a zip file using Python 3.8 and was surprised when the code errored as it seemed pretty standard. This is the story of the crazy loophole that I had to go into as a result.

First off, here is the code that didn't work:

```python
def make_archive_bad(path="test.zip"):
    with zipfile.ZipFile(path, "x") as z:
        with z.open("config.json", "w") as c:
            # This doesn't work
            json.dump(config, c, indent=2)

        with z.open("data.json", "w") as d:
            for row in data(config):
                # This doesn't work
                d.write(json.dumps(row))
                d.write("\n")
```

The exception is located in the interaction between `json.dump` and `zipfile._ZipWriteFile.write` as you can see in the traceback below.

```
  File "./zipr.py", line 144, in <module>
    make_archive_bad()
  File "./zipr.py", line 32, in make_archive_bad
    json.dump(config, c, indent=2)
  File "3.7/lib/python3.7/json/__init__.py", line 180, in dump
    fp.write(chunk)
  File "3.7/lib/python3.7/zipfile.py", line 1094, in write
    self._crc = crc32(data, self._crc)
TypeError: a bytes-like object is required, not 'str'
```

> The json module always produces str objects, not bytes objects. Therefore, fp.write() must support str input.
>
> &mdash; [json documentation](https://docs.python.org/3/library/json.html#basic-usage)

So the issue is really with the zipfile library and to make it work, you'll have to `json.dumps` and then encode your data yourself. Which is annoying:

```python
def make_archive_annoying(path="test.zip"):
    # This does work but is annoying
    # Also note, this will write to the root of the archive, and when unzipped will not
    # unzip to a directory but rather into the same directory as the zip file
    with zipfile.ZipFile(path, "x") as z:
        with z.open("config.json", "w") as c:
            c.write(json.dumps(config, indent=2).encode("utf-8"))

        with z.open("data.json", "w") as d:
            for row in data(config):
                d.write(json.dumps(row).encode("utf-8"))
                d.write("\n".encode("utf-8"))
```

For 99% of people, the above solution is the way to go. However, as soon as I realized that this was also going to write into the root of the zip file so that when you extract the contents they are in the same directory as the zip file instead of a subdirectory ... I went a little overboard. So here is a solution that is not annoying but requires some wrapper utility code in your library.

I'm sorry.

```python
class Zipr(object):

    def __enter__(self):
        # Makes this thing a context manager
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        # Makes this thing a context manager
        self.close()

    def close(self):
        self.zobj.close()


class ZipArchive(Zipr):

    def __init__(self, path, mode="r"):
        self.zobj = zipfile.ZipFile(
            path, mode, compression=zipfile.ZIP_STORED,
            allowZip64=True, compresslevel=None
        )
        self.root, _ = os.path.splitext(os.path.basename(path))

    def open(self, path, mode='r'):
        # Write into a directory instead of the root of the zip file
        path = os.path.join(self.root, path)
        return ZipArchiveFile(self.zobj.open(path, mode))


class ZipArchiveFile(Zipr):

    def __init__(self, zobj, encoding="utf-8"):
        self.zobj = zobj
        self.encoding = encoding

    def write(self, data):
        if isinstance(data, str):
            data = data.encode(self.encoding)
        self.zobj.write(data)
```

These classes are essentially just wrappers for `ZipFile` and `_ZipWriteFile`, so potentially it would just be easier to subclass these files and and override the `open` and `write` methods - but I'll leave that to the reader to make a decision. This is enough to have less annoying code:

```python
def make_archive(path="test.zip"):
    # Less annoying make archive with workaround classes
    with ZipArchive(path, "x") as z:
        with z.open("config.json", "w") as c:
            json.dump(config, c, indent=2)

        with z.open("data.json", "w") as d:
            for row in data(config):
                d.write(json.dumps(row))
                d.write("\n")
```

There are still issues, however. For example append (`'a'`) mode does not work with `_ZipWriteFile`, so if you try to stream data by opening for appending, you'll run into issues. See below:

```python
def make_archive_stream(path="test.zip"):
    # Attempts to open the internal zip file for appending, to stream data in.
    # But this doesn't work because you can't open an internal zip object for appending
    with ZipArchive(path, "x") as z:
        with z.open("config.json", "w") as c:
            json.dump(config, c, indent=2)

        cache = []
        for i, row in enumerate(data(config)):
            cache.append(json.dumps(row))

            # dump cache every 5 rows
            if i%5 == 0:
                with z.open("data.json", "a") as d:
                    for row in cache:
                        d.write(row+"\n")
                cache = []

        if len(cache) > 0:
            with z.open("data.json", "a") as d:
                for row in cache:
                    d.write(row+"\n")
```

The full code can be found on [this gist](https://gist.github.com/bbengfort/73c142188085e6b417b49d3897fa7d24).