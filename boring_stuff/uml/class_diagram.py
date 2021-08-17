#!/usr/bin/env python
"""Writing up a class diagram

This module uses Plantuml as the UML format.
The boring_stuff.projects.map_with_inspect methods are used to
discover the modules, classes, functions and methods,
connections of a given package.

Examples
--------

>>> import boring_stuff
>>> # map the package
>>> from boring_stuff.projects import map_with_inspect as MWI
>>> package_dict = MWI.map_module(boring_stuff)

Now draw with class diagram (Plantuml format)

>>> from boring_stuff.uml.class_diagram import write_class_diagram
>>> write_class_diagram(package_dict, "/tmp/output.puml")
"""
# import libraries
import time
import numpy as np
CONNECTION = {
    "EXTENSION": " <|-down- ",
    "COMPOSITION": " *-down- ",
    "AGGREGRATION": " o-down- ",
}
"""Types of CONNECTION

Types
    AGGREGATION
    COMPOSITION
    EXTENSION: B extends A
"""

ACCESS = {
    "PRIVATE": "-",
    "PROTECTED": "#",
    "PUBLIC": "+",
}
"""Types of Access"""

MODIFIERS = {
    "ABSTRACT": "{abstract}",
    "STATIC": "{static}",
}
"""Modifiers"""

TAB = "    "
"""Tab"""


def creator_note(out_file):
    """Add note to PlantUML file

    Add a note that this is autogenerated by py-boring-stuff
    and add a timestamp.

    Parameters
    ----------
    out_file : output file
        PlantUML file to write.
    """
    # add a detached note with the info
    out_file.write("note as autonote\n")
    out_file.write("Autogenerated by py-boring-stuff\n")
    out_file.write("%s\n" % time.ctime())
    out_file.write("end note\n\n")


def write_package(package, file_out, n_tab=0):
    """Write the package

    Parameters
    ----------
    package : dict
        The package specification with fields
        'name', 'modules', 'subpackages'

    file_out : file handle
        Output file handle

    n_tab : int
        Number of tabs to indent
    """
    if package["type"] == "module":
        write_module(package, file_out, n_tab)
        return

    # opening of package
    file_out.write(
        TAB * n_tab + \
        "package %s {\n" % package.get("name")
    )

    modules = package.get("modules")
    if modules:
        for module in modules:
            write_module(module, file_out, n_tab + 1)

    subpackages = package.get("subpackages")
    if subpackages:
        for subpackage in subpackages:
            write_package(subpackage, file_out, n_tab + 1)

    # close of package
    file_out.write(TAB * n_tab + "}\n")


def write_module(module, file_out, n_tab=0):
    """Write the module as a package in the class diagram

    Parameters
    ----------
    module : dict
        Module specification with fields 'methods', 'class_list'

    file_out : file handle
        Output file handle

    n_tab : int
        Number of tabs to indent
    """

    class_list = module.get("class_list", [])
    func_list = module.get("methods", [])
    var_list = module.get("variables", [])

    # ignore empty modules (like __init__.py)
    if len(class_list) == 0 and len(func_list) == 0 and len(var_list) == 0:
        return

    # write module
    file_out.write("\n%spackage %s {\n" % (n_tab*TAB, module.get("name")))

    if len(var_list) > 0 or len(func_list) > 0:
        # write a class to describe the variables and functions
        file_out.write("\n%sclass %s {\n" % \
            ((n_tab + 1) * TAB, module.get("name") + ".module")
        )

        # write variables
        for var_spec in var_list:
            write_variable(var_spec, file_out, n_tab+2)


        # write functions
        for func_spec in func_list:
            write_function(func_spec, file_out, n_tab+2)

        # finish this class
        file_out.write((n_tab + 1) * TAB + "}\n")

    # ------------------  write classes  ----------------------------
    list_ext = []
    for class_spec in class_list:
        write_class(class_spec, file_out, n_tab + 1)

        # check parent and perhap update list_ext
        parent_list = class_spec.get("parent")
        if parent_list:
            if np.isscalar(parent_list):
                list_ext.append("{}{}{}".format(
                    parent_list,
                    CONNECTION.get("EXTENSION"),
                    class_spec.get("name")))
            else:
                for parent in parent_list:
                    list_ext.append("{}{}{}".format(
                        parent,
                        CONNECTION.get("EXTENSION"),
                        class_spec.get("name")))

    # draw links between extensions
    for ext in list_ext:
        file_out.write(TAB * (n_tab + 1) + ext + "\n")

    file_out.write(n_tab * TAB + "}\n")


def write_class(class_spec, file_out, n_tab=0):
    """Write the class object

    Examples
    --------
    The output would be:
    class CLASSNAME {
        + void method1(param1, param2)
        - void method2(param1)
    }

    Parameters
    ----------
    class_spec : dict
        The class specification

    file_out : file handle
        Output file handle

    n_tab : int
        Number of tabs to indent
    """
    file_out.write("\n%sclass %s {\n" % (n_tab*TAB, class_spec.get("name")))

    # TODO: write attributes/properties of the class
    #       Currently detection of the internal properties has not been done

    # -----------------------  write method signatures  ---------------------
    for method in class_spec.get("methods", []):
        write_function(method, file_out, n_tab + 1)

    # -----------------------  write function signatures  ---------------------
    list_funcs = class_spec.get("functions", [])
    if list_funcs:
        file_out.write((n_tab + 1) * TAB + "-- static methods --\n")
        for func in list_funcs:
            write_function(func, file_out, n_tab + 1)

    file_out.write(n_tab * TAB + "}\n")  # write complete class


def write_function(method_spec, file_out, n_tab=1):
    """Write function signature

    Parameters
    ----------
    method_spec : dict
        Method specification.  Should have fields 'params' and
        'access'

    file_out : file handle
        Output file handle

    n_tab : int
        Number of tabs to indent
    """
    # list the parameters with comma separation
    param_str = ", ".join(method_spec.get("params", []))

    file_out.write(TAB*n_tab + "{} {} {}({})\n".format(
        # public(+), protected(#), private(-)
        ACCESS[method_spec.get("access").upper()],

        # NOTE: Python returns is dynamic, hard to determine return type
        "void",

        # name of the method
        method_spec.get("name"),

        # parameter
        param_str)
    )


def write_variable(var_spec, file_out, n_tab):

    file_out.write(TAB*n_tab + "{} {}:{}\n".format(
        # public(+), protected(#), private(-)
        ACCESS[var_spec.get("access").upper()],

        # name of the method
        var_spec.get("name"),

        # parameter
        var_spec.get("type")
    ))


def write_class_diagram(package, output="/tmp/gen.wsd"):
    """Write a class diagram

    Draw the class diagram provided the description from
    class_list

    Parameters
    ----------
    package : dict
        Dictionary with field of subpackages and modules

    output : str
        The output file path for the WSD file.
    """
    with open(output, "w") as file_out:
        # -------------------  write WSD UML file  --------------------------
        # initialize UML
        file_out.write("@startuml\n")

        # add a note
        creator_note(file_out)

        # -------------------  write module  --------------------------------
        write_package(package, file_out)

        # finalize UML
        file_out.write("@enduml\n")
