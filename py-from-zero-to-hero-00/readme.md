# Quick Introduction

## What is Python & How Does It Run Code
Python is an interpreted programming language, meaning code is not compiled "ahead of time" like C# or Go, instead, the Python interpreter reads and executes instructions line by line.

Attention!
"ahead of time" means we do not have a separate compile step that produces a final binary executable before running the program.

So, to run the code we just need this simple command line below

```
python3 app.py
```

Python performs the following tasks:
Parses the file
Transforms to bytecode (.pyc)
Executes bytecode on the Python Virtual Machine (PVM)
This makes Python flexible and great for scripting, automation, AI, and data workflows.

## Installing Python 
https://www.python.org/downloads/release/python-3132/

On MAC
```
brew install python
python3 --version
```

# The Importance of Virtual Environments (-m venv)
When working with Python you typically need isolated environments because different projects may require different dependencies (external packages)

Example:
Project A requires this package Django 3.2
Project B requires the same package but using different version Django 5.0
Without isolation, they conflict :(

As a result, before coding, we first need to prepare our house.. that means create an environment in order to isolate our dependencies from external ones

```
python3 -m venv .myenv
```

and now, active it

```
source .venv/bin/activate
```

once getting into the env, we are safe to install our external packages using

```
pip install package-name
```

for instance

```
pip install flask
```

and if we are also able to deactivate it any time using

```
deactivate
```

# First Code Concepts

### Variables

Python infers types automatically:

```python
age = 33
name = "Renato"
price = 19.99

```

### Constants

Python has no strict const keyword. Constants are defined by convention:

```python
MAX_USERS = 100
APP_NAME = "Python for code lovers"
```

### Functions - Part 1

We just need to add "def" before so then we can define our functions

```python
def greet(name):
    return f"Hello, {name}!"
```

so the, we are able to call it using

```python
print(greet("Renato"))
```

Calm down! Let´s talk about print function.. this is a really nice one

#### Simple print

```python
print("Hello")
```


#### Default and Custom separator

```python
print("Renato", "Mattos", "CGI")
```

the output is

```
Renato Mattos CGI
```

```python
print("Renato", "Mattos", "CGI", sep=" | ")
```

now the output is

```
Renato | Mattos | CGI
```

#### Changing line ending

Default ends with newline:

```python
print("Hello")
print("World")
```

now the output is

```
Hello
World
```

using Custom ending:

```python
print("Hello", end=" ")
print("World")
```

now the output is

```
Hello World
```

#### Printing To a File

```python
with open("log.txt", "w") as f:
    print("Logging something...", file=f)
```

Forcing the Immediate Output with FLUSH

```python
print("processing...", flush=True)
```


#### and remember Print can print anything

```python
print([1,2,3], {"name":"Renato"}, 55.5)
```

### Back to the Functions - Part 2

A function can accept:

✔ positional parameters
✔ keyword parameters
✔ default values
✔ variable number of arguments

```python
def register_user(name, age=18, *skills, active=True, **metadata):
    print(name, age, skills, active, metadata)
```

Attention!
The *skills parameter collects any extra positional arguments into a tuple.

calling the function

```python
register_user("Renato")
register_user("Renato", 35, "Python", "C#", active=False, country="Portugal")
```

Attention!
Python is not “pass by value” or “pass by reference” in traditional language terms.
Variables are names pointing to objects. Functions receive references to those objects.


```python
def modify(x):
    x.append(100)

lst = [1, 2, 3]
modify(lst)
print(lst)
```

that produces

```python
[1, 2, 3, 100]
```

Don´t worry, we have a very specific topic to discuss about list, tuples, etc.

Attention!
Immutable vs Mutable Types (Super Important)


Type	        Category
int	            immutable
str	            immutable
tuple	        immutable
float	        immutable
list	        mutable
dict	        mutable
set	            mutable
objects/classes	mutable unless designed otherwise


Unlike C#, Java, or Go, Python does not support traditional overloading like:

```python
void do(int x)
void do(string x)
```

If we define two functions with the same name, the last one wins :(

```python
def someFunc(x): print("name")
def someFunc(x): print("age")

someFunc("Renato")
```

it produces

```python
age
```

But for these cases we have an alternative using default parameters

```python
def area(width, height=None):
    if height is None:
        return width * width
    return width * height

print(area(10))     # square
print(area(10, 5))  # rectangle
```

Attention!
Attention again! :)
Another way to act using a pseudo-overload mechanism via runtime type dispatch:


from functools import singledispatch

```python
@singledispatch
def show(x):
    print("object:", x)

@show.register(int)
def _(x):
    print("integer:", x)

@show.register(str)
def _(x):
    print("string:", x)

show(10)
show("abc")
```

The output is

```
integer: 10
string: abc
```

Let's break it down carefully and clearly.
When using languages like C#, Java, Go allow:

```c#
void show(int x)
void show(string x)
```

Once Python does not support this natively. If we define two functions with the same name in Python, the last one overrides the first one. So Python gives us a tool called single dispatch to emulate type-based overloading.

Where singledispatch lets you register multiple implementations of the same function name, and Python will pick which one to run based on the type of the first argument.

We created a generic base function called show.
If Python receives a type it doesn't know, it uses this default implementation.

```python
from functools import singledispatch

@singledispatch
def show(x):
    print("object:", x)
```

Now we add specific implementations to the show function
so, If the argument type is int, use this version.

```python
@show.register(int)
def _(x):
    print("integer:", x)
```

and another version for string arg

```python
@show.register(str)
def _(x):
    print("string:", x)
```

finally, calling the function using different data types
```python
show(10)
show("abc")
```

we have this

```
integer: 10
string: abc
```

Wait a minute! and If we call with something unregistered????
A float input for instance?

```python
show(3.14)
```

Output (default):

```
object: 3.14
```

Why Use This Instead of if / elif?

```python
def show(x):
    if isinstance(x, int):
        ...
    elif isinstance(x, str):
        ...
```

Because adopting singledispatch:
✔ makes code modular
✔ allows extension in other files/modules
✔ follows OOP "open for extension" principle

### IF / ELIF / ELSE — Python’s Conditional Logic

In Python, conditional logic is written using:
if
elif (short for else if)
else

another words, the Basic Structure is

if condition:
    # do something
elif other_condition:
    # do something else
else:
    # fallback


```python
age = 20

if age >= 18:
    print("Adult")
elif age >= 13:
    print("Teenager")
else:
    print("Child")
```

Hey! Pay attention at this!

Like many languages, Python evaluates values in if as True or False.
Examples considered False:

```python
0
0.0
"" (empty string)
None
[] (empty list)
{} (empty dict)
False
```

Everything else is True!! :)

```python
name = ""

if name:
    print("Has name")
else:
    print("No name")
```

this produces

```
No name
```

#### Comparison Operators

Operator	Meaning
==	        equal
!=	        not equal
<	        less than
<=	        less or equal
>	        greater than
>=	        greater or equal

```python
if 10 == 10:
    print("Equal")
```

#### Logical Operators
Python uses:
- and
- or
- not

```python
age = 25
country = "PT"

if age >= 18 and country == "PT":
    print("Can drive in Portugal")
```

#### Membership Operators

```python
if "Renato" in ["Renato", "João", "Maria"]:
    print("Found")
```

