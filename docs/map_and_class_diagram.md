# Project Map and Class Diagrams

Whether to document your own Python project or to learn the organization of a Python library, py-boring-stuff supports the use of the 'inspect' module to analyze a Python library and map modules and classes.

A class diagram can be generated from the mapped library.  This provides a visualization of the organization of the library.

## In Python

In a Python console, the individual libraries may be called to map a given module/package.

~~~python
import boring_stuff
from boring_stuff.projects.map_with_inspect import map_module

# use inspect to analyze boring_stuff library
module_dict = map_module(boring_stuff)

# write class diagram
from boring_stuff.uml.class_diagram import write_class_diagram
write_class_diagram(module_dict, output="/tmp/boring_stuff.puml")
~~~

## In Command-line

Once installed, the main method of boring_stuff.projects.map_with_inspect
can be called directly

~~~bash
# assuming boring_stuff is already installed.
python -m boring_stuff.projects.map_with_inspect boring_stuff --output
~~~