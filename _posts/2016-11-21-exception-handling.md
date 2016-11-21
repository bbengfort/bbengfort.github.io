---
layout: post
title:  "Exception Handling"
date:   2016-11-21 12:53:30 -0500
categories: tutorials
---

This short tutorial is intended to demonstrate the basics of exception handling and the use of context management in order to handle standard cases. These notes were originally created for a training I gave, and the notebook can be found at [Exception Handling](https://github.com/DistrictDataLabs/ceb-training/blob/master/notes/Exception%20Handling.ipynb). I'm happy for any comments or pull requests on the notebook.

## Exceptions

**Exceptions** are a tool that programmers use to describe errors or faults that are _fatal_ to the program; e.g. the program cannot or should not continue when an exception occurs. Exceptions can occur due to programming errors, user errors, or simply unexpected conditions like no internet access. Exceptions themselves are simply objects that contain information about what went wrong. Exceptions are usually defined by their `type` - which describes broadly the class of exception that occurred, and by a `message` that says specifically what happened. Here are a few common exception types:

- `SyntaxError`: raised when the programmer has made a mistake typing Python code correctly.
- `AttributeError`: attempting to access an attribute on an object that does not exist
- `KeyError`: attempting to access a key in a dictionary that does not exist
- `TypeError`: raised when an argument to a function is not the right type (e.g. a `str` instead of `int`)
- `ValueError`: when an argument to a function is the right type but not in the right domain (e.g. an empty string)
- `ImportError`: raised when an import fails
- `IOError`: raised when Python cannot access a file correctly on disk

Exceptions are defined in a class hierarchy - e.g. every exception is an object whose class defines it's type. The base class is the `Exception` object. All `Exception` objects are initialized with a message - a string that describes exactly what went wrong. Constructed objects can then be "raised" or "thrown" with the `raise` keyword:

```python
raise Exception("Something bad happened!")
```

The reason the keyword is `raise` is because Python program execution creates what's called a "stack" as functions call other functions, which call other functions, etc. When a function (at the bottom of the stack) raises an Exception, it is propagated up through the call stack so that every function gets a chance to "handle" the exception (more on that later). If the exception reaches the top of the stack, then the program terminates and a _traceback_ is printed to the console. The traceback is meant to help developers identify what went wrong in their code.

Let's take a look at a simple example:

```python
def main(badstep=None, **kwargs):
    """
    This function is the entry point of the program, it does
    work on the arguments by calling each step function, which
    in turn call substep functions.

    Passing in a number for badstep will cause whichever step
    that is to raise an exception.
    """

    step = 0 # count the steps

    # Execute each step one at a time.
    step = first(step, badstep)
    step = second(step, badstep)

    # Return a report
    return "Sucessfully executed {} steps".format(step)


def first(step, badstep=None):
    # Increment the step
    step += 1

    # Check if this is a bad step
    if badstep == step:
        raise ValueError("Failed after {} steps".format(step))

    # Call sub steps in order
    step = first_task_one(step, badstep)
    step = first_task_two(step, badstep)

    # Return the step that we're on
    return step


def first_task_one(step, badstep=None):
    # Increment the step
    step += 1

    # Check if this is a bad step
    if badstep == step:
        raise ValueError("Failed after {} steps".format(step))

    # Call sub steps in order
    step = first_task_one_subtask_one(step, badstep)

    # Return the step that we're on
    return step


def first_task_one_subtask_one(step, badstep=None):
    # Increment the step
    step += 1

    # Check if this is a bad step
    if badstep == step:
        raise ValueError("Failed after {} steps".format(step))

    # Return the step that we're on
    return step


def first_task_two(step, badstep=None):
    # Increment the step
    step += 1

    # Check if this is a bad step
    if badstep == step:
        raise ValueError("Failed after {} steps".format(step))

    # Return the step that we're on
    return step


def second(step, badstep=None):
    # Increment the step
    step += 1

    # Check if this is a bad step
    if badstep == step:
        raise ValueError("Failed after {} steps".format(step))

    # Call sub steps in order
    step = second_task_one(step, badstep)

    # Return the step that we're on
    return step


def second_task_one(step, badstep=None):
    # Increment the step
    step += 1

    # Check if this is a bad step
    if badstep == step:
        raise ValueError("Failed after {} steps".format(step))

    # Return the step that we're on
    return step
```

The above example represents a fairly complex piece of code that has lots of functions that call lots of other functions. The question is then, _how do we know where our code went wrong?_ The answer is the _traceback_ - which deliniates exactly the functions that the exception was raised through. Let's trigger the exception and the traceback:


```python
main(3)
```

```text
---------------------------------------------------------------------------

ValueError                                Traceback (most recent call last)

<ipython-input-5-e46a77400742> in <module>()
----> 1 main(3)


<ipython-input-4-03153844a5cc> in main(badstep, **kwargs)
     12
     13     # Execute each step one at a time.
---> 14     step = first(step, badstep)
     15     step = second(step, badstep)
     16


<ipython-input-4-03153844a5cc> in first(step, badstep)
     28
     29     # Call sub steps in order
---> 30     step = first_task_one(step, badstep)
     31     step = first_task_two(step, badstep)
     32


<ipython-input-4-03153844a5cc> in first_task_one(step, badstep)
     44
     45     # Call sub steps in order
---> 46     step = first_task_one_subtask_one(step, badstep)
     47
     48     # Return the step that we're on


<ipython-input-4-03153844a5cc> in first_task_one_subtask_one(step, badstep)
     56     # Check if this is a bad step
     57     if badstep == step:
---> 58         raise ValueError("Failed after {} steps".format(step))
     59
     60     # Return the step that we're on


ValueError: Failed after 3 steps
```

The way to read the traceback is to start at the very bottom. As you can see it indicates the type of the exception, followed by a colon, and then the message that was passed to the exception constructor. Often, this information is enough to figure out what is going wrong. However, if we're unsure where the problem occurred, we can step back through the traceback in a bottom to top fashion.

The first part of the traceback indicates the exact line of code and file where the exception was raised, as well as the name of the function it was raised in. If you called `main(3)` than this indicates that `first_task_one_subtask_one` is the function where the problem occurred. If you wrote this function, then perhaps that is the place to change your code to handle the exception.

However, many times you're using third party libraries or Python standard library modules, meaning the location of the exception raised is not helpful, since you can't change that code. Therefore, you will continue up the call stack until you discover a file/function in the code you wrote. This will provide the surrounding context for why the error was raised, and you can use `pdb` or even just `print` statements to debug the variables around that line of code. Alternatively you can simply handle the exception, which we'll discuss shortly. In the example above, we can see that `first_task_one_subtask_one` was called by `first_task_one` at line 46, which was called by `first` at line 30, which was called by `main` at line 14.

## Catching Exceptions

If the exception was caused by a programming error, the developer can simply change the code to make it correct. However, if the exception was created by bad user input or by a bad environmental condition (e.g. the wireless is down), then you don't want to crash the program. Instead you want to provide feedback and allow the user to fix the problem or try again. Therefore in your code, you can catch exceptions at the place they occur using the following syntax:

```python
try:
    # Code that may raise an exception
except AttributeError as e:
    # Code to handle the exception case
finally:
    # Code that must run even if there was an exception
```

What we're basically saying is `try` to do the code in the first block - hopefully it works. If it raises an `AttributeError` save that exception in a variable called `e` (the `as e` syntax) then we will deal with that exception in the `except` block. Then `finally` run the code in the `finally` block even if an exception occurs. By specifying exactly the type of exception we want to catch (`AttributeError` in this case), we will not catch all exceptions, only those that are of the type specified, including subclasses. If we want to catch _all_ exceptions, you can use one of the following syntaxes:

```python
try:
    # Code that may raise an exception
except:
    # Except all exceptions
```

or

```python
try:
    # Code that may raise an exception
except Exception as e:
    # Except all exceptions and capture in variable e
```

However, it is best practice to capture _only_ the type of exception you expect to happen, because you could accidentaly create the situation where you're capturing fatal errors but not handling them appropriately. Here is an example:


```python
import random


class RandomError(Exception):
    """
    A custom exception for this code block.
    """
    pass


def randomly_errors(p_error=0.5):
    if random.random() <= p_error:
        raise RandomError("Error raised with {:0.2f} likelihood!".format(p_error))


try:
    randomly_errors(0.5)
    print("No error occurred!")
except RandomError as e:
    print(e)
finally:
    print("This runs no matter what!")
```

This code snippet demonstrates a couple of things. First you can define your own, program-specific exceptions by defining a class that extends `Exception`. We have done so and created our own `RandomError` exception class. Next we have a function that raises a `RandomError` with some likelihood which is an argument to the function. Then we have our exception handling block that calls the function and handles it.

Try the following the code snippet:

- Change the likelihood of the error to see what happens
- except `Exception` instead of `RandomError`
- except `TypeError` instead of `RandomError`
- Call `randomly_errors` again inside of the `except` block
- Call `randomly_errors` again inside of the `finally` block

Make sure you run the code multiple times since the error does occur randomly!

## LBYL vs. EAFP

One quick note on exception handling in Python. You may wonder why you must use a `try/except` block to handle exceptions, couldn't you simply do a check that the exception won't occur before it does? For example, consider the following code:

```python
if key in mydict:
    val = mydict[key]
    # Do something with val
else:
    # Handle the fact that mydict doesn't have a required key.
```

This code checks if a key exists in the dictionary before using it, then uses an else block to handle the "exception". This is an alternative to the following code:

```python
try:
    val = mydict[key]
    # Do something with val
except KeyError:
    # Handle the fact that mydict doesn't have a required key.
```

Both blocks of code are valid. In fact they have names:

1. Look Before You Leap (LBYL)
2. Easier to Ask Forgiveness than Permission (EAFP)

For a variety of reasons, the second example (EAFP) is more _pythonic_ &mdash; that is the prefered Python Syntax, commonly accepted by Python developers. For more on this, please see Alex Martelli's excellent PyCon 2016 talk, [Exception and error handling in Python 2 and Python 3](https://www.youtube.com/watch?v=frZrBgWHJdY).

## Context Management

Python does provide a syntax for embedding common `try/except/finally` blocks in an easy to read format called context management. To motivate the example, consider the following code snippet:

```python
try:
    fobj = open('path/to/file.txt, 'r')
    data = fobj.read()
except FileNotFoundError as e:
    print(e)
    print("Could not find the necessary file!)
finally:
    fobj.close()
```

This is a very common piece of code that opens a file and reads data from it. If the file doesn't exist, we simply alert the user that the required file is missing. No matter what, the file is closed. This is critical because if the file is not closed properly, it can be corrupted or not available to other parts of the program. Data loss is not acceptable, so we need to ensure that no matter what the file is closed when we're done with it. So we can do the following:

```python
with open('path/to/file.txt', 'r') as fobj:
    data = fobj.read()
```

The `with as` syntax implements context management. On `with`, a function called the `enter` function is called to do some work on behalf of the user (in this case open a file), and the return of that function is saved in the `fobj` variable. When this block is complete, the finally is called by implementing an `exit` function. (Note that the `except` part is not implemented in this particular code). In this way, we can ensure that the `try/finally` for opening and reading files is correctly implemented.

Writing your own context managers is possible, but beyond the scope of this note (though I may write something on it shortly). Suffice it to say, you should always use the `with/as` syntax for opening files!
