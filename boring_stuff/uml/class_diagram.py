#!/usr/bin/env python
import time
"""A CONNECTION B

Types
    AGGREGATION
    COMPOSITION
    EXTENSION: B extends A

"""
CONNECTION = {
    "EXTENSION": " <|-down- ",
    "COMPOSITION": " *-down- ",
    "AGGREGRATION": " o-down- ",
}
ACCESS = {
    "PRIVATE": "-",
    "PROTECTED": "#",
    "PUBLIC": "+",
}
MODIFIERS = {
    "ABSTRACT": "{abstrac}",
    "STATIC": "{static}",
}
TAB = "    "


def creator_note(out_file):
    """Add note to WSD file

    Add a note that this is autogenerated by py-boring-stuff
    and add a timestamp.

    Parameters
    ----------
    out_file : output file
        WSD file to write.
    """
    # add a detacted note with the info
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
    # opening of package
    file_out.write(TAB*n_tab + "package %s {\n" % package.get("name"))

    modules = package.get("modules")
    if modules:
        for module in modules:
            write_module(module, file_out, n_tab)

    subpackages = package.get("subpackages")
    if subpackages:
        for subpackage in subpackages:
            write_package(subpackage, file_out, n_tab+1)

    c_list = package.get("class_list")
    if c_list:
        for c_spec in c_list:
            write_class(c_spec, file_out, n_tab)

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
    # ignore empty modules (like __init__.py)
    if not(module.get("class_list") or module.get("methods")):
        return

    class_list = module.get("class_list", [])
    if not class_list:
        if module.get("methods"):
            class_spec = {
                "type": "class",
                "name": module.get("name"),
                "methods": module.get("methods"),
            }
            class_list = [class_spec]

    # ------------------  write classes  ----------------------------
    list_ext = []
    for class_spec in class_list:
        write_class(class_spec, file_out, n_tab+1)

        # check parent and perhap update list_ext
        parent = class_spec.get("parent")
        if parent:
            list_ext.append("{}{}{}".format(
                parent,
                CONNECTION.get("EXTENSION"),
                class_spec.get("name")))

    # draw links between extensions
    for ext in list_ext:
        file_out.write(TAB * (n_tab + 1) + ext + "\n")


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
