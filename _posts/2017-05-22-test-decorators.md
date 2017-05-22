---
layout: post
title:  "Decorating Nose Tests"
date:   2017-05-22 13:05:08 -0700
categories: snippets
---

Was introduced to an interesting problem today when decorating tests that need to be discovered by the [nose](https://pypi.python.org/pypi/nose/1.3.7) runner. By default, nose explores a directory looking for things named `test` or `tests` and then executes those functions, classes, modules, etc. as tests. A standard test suite for me looks something like:

```python
import unittest


class MyTests(unittest.TestCase):

    def test_undecorated(self):
        """
        assert undecorated works
        """
        self.assertEqual(2+2, 4)
```

The problem came up when we wanted to decorate a test with some extra functionality, for example loading a fixture:

```python
def load_fixture(func):
    def wrapper(*args, **kwargs):
        # Load a fixture
        return func(*args, **kwargs)
    return wrapper


class MyTests(unittest.TestCase):

    @load_fixture
    def test_decorated(self):
        """
        assert a decorated test works
        """
        self.assertEqual(2+2, 4)
```

The key to remember is that you must wrap the function so that the name and docstring are added to the internal wrapper, thus allowing the nose test discovery function to work:

```python
from functools import wraps

def load_fixture(func):

    @wraps(func)
    def wrapper(*args, **kwargs):
        # Load a fixture
        return func(*args, **kwargs)

    return wrapper
```

Thanks to [@ndanielsen](https://github.com/ndanielsen/) for pointing this out, it's going to save me a bit of trouble in the future, I expect. 
