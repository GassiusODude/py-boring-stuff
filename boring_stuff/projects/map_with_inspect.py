#!/usr/bin/env python
from collections import OrderedDict
import importlib
import inspect
import logging
import sys

logger = logging.getLogger("boring_stuff.projects.map_with_inspect")


def is_private(name):
    """Check if variable name infers that variable is private.

    Parameters
    ----------
    name : str
        The name of the variable in question

    Returns
    -------
    private : bool
        True if it fits "__xxxxx__" format
    """
    assert isinstance(name, str), "Expecting name to be a string"
    return len(name) > 4 and "__" == name[:2] and "__" == name[-2:]


def map_module(mod):
    """Map a module

    Use inspect to map the following:

    * package
      * module
        * class
          * methods
          * variables
        * variables
        * functions

    Parameters
    ----------
    mod : module
        The module to be examined.

    Returns
    -------
    c_package : dict
        The dictionary describing the package.
    """
    # ----------------------  initialize variables  -------------------------
    # extract name of the current module
    name = mod.__name__
    logger.info("Running map_module(%s)" % name)

    # initialize variables
    module_dict = {}
    class_dict = {}
    func_dict = {}
    dependency_list = []
    variable_list = []

    # ----------------------  inspect current  ------------------------------
    # inspect the module
    members = inspect.getmembers(mod)

    for member in members:
        try:
            # member is a tuple
            if member[0][:2] == "__" and member[0][-2:] == "__":
                # ignore 'private' members
                continue

            elif inspect.ismodule(member[1]):
                # --------------------  a module type  ----------------------
                if member[1].__name__ == name and member[1] == mod:
                    # same module? avoid infinite recursion
                    logger.warning("Module (%s) references itself" % name)
                    continue

                elif member[1].__name__[:len(name)] == name:
                    # submodule
                    module_dict[member[1].__name__] = member[1]
                else:
                    # external library...an import
                    dependency_list.append([name, member[1].__name__])

            elif inspect.isfunction(member[1]):
                if member[1].__module__ == name:
                    # member of this module
                    func_dict[member[0]] = member[1]
                else:
                    # imported function
                    dependency_list.append([name, member[1].__name__])

            elif inspect.isclass(member[1]):
                if member[1].__module__ == name:
                    # member of this module
                    class_dict[member[0]] = member[1]

                else:
                    # imported class
                    dependency_list.append([name, member[1].__name__])

            else:
                if is_private(member[0]):
                    c_access = "private"

                else:
                    c_access = "public"

                variable_list.append({
                    "name": member[0],
                    "type": type(member[1]),
                    "access": c_access
                })
        except Exception as e:
            logger.error("Exception in map_module() caught %s" % str(e))

    has_m = len(module_dict) > 0
    has_c = len(class_dict) > 0
    has_f = len(func_dict) > 0
    has_v = len(variable_list) > 0

    c_package = {}
    try:
        if has_m and not(any([has_c, has_f, has_v])):
            # pure package
            c_package = {
                "type": "package",
                "name": name,
                "subpackages": [],
                "modules": [],
                "misc": [],
                "dependencies": dependency_list
            }
            add_modules(c_package, module_dict)

        else:
            # module with some form of variable/function/class
            c_package = {
                "type": "module",
                "name": name,
                "subpackages": [],
                "modules": [],
                "class_list": [],
                "methods": [],
                "variables": variable_list,
                "dependencies": dependency_list
            }
            add_modules(c_package, module_dict)
            add_classes(c_package, class_dict)

            for c_method in func_dict:
                c_package["methods"].append(
                    map_function(func_dict[c_method])
                )
    except Exception as e:
        logger.error("Exception caught in map_module(): %s" % str(e))

    return c_package


def add_modules(c_package, mod_dict):
    """Add modules to c_package

    This uses map_module to dive deeper into detected moddules.
    If the module only has references to other modules, it is
    labeled as a "package".  Otherwise it is a 'module' with
    variables, functions, and/or classes.

    Parameters
    ----------
    c_package : dict
        The current package from map_module.
        .. note:: This parameter is update by this function

    See Also
    --------
    map_module :
        Function to map a module.
    """
    for c_mod in mod_dict:
        try:
            logger.debug("Add %s from %s" % (c_mod, c_package["name"]))
            tmp_mod = map_module(mod_dict[c_mod])
            if tmp_mod["type"] == "package":
                c_package["subpackages"].append(tmp_mod)
            else:
                c_package["modules"].append(tmp_mod)

        except Exception as e:
            logger.error(
                "Caught exception(%s) in add_modules(%s)" %
                (str(e), str(c_mod)))


def add_classes(c_package, class_dict):
    """Add details about classes

    This function dives deeper into the package to
    update the list of classes.

    Parameters
    ----------
    c_package : dict
        The current package from map_module.

    class_dict : dict
        The classes found in map_module

    See Also
    ---------
    map_module :
        Function that calls this function

    map_class :
        Function to map a class
    """
    for c_class in class_dict:
        try:
            c_package["class_list"].append(
                map_class(class_dict[c_class])
            )
        except Exception as e:
            logger.error("Exception caught in add_classes: %s" % str(e))


def get_parent(cls):
    """Get the parent of the class

    Parameters
    ----------
    cls : class
        The class being analyzed

    Returns
    -------
    parent : None, list, class
        The parent can be None.
        It can be a list of classes or a single class
    """
    try:
        if len(cls.__bases__) == 0:
            parent = None
        else:
            parent = [i.__name__ for i in cls.__bases__]

    except Exception as e:
        parent = None
        logger.error("Error caught in get_parent(), %s" % str(e))
    return parent


def map_class_python3(cls):
    """Map class with Python3

    Parameters
    ----------
    cls : class
        The class being analyzed

    Returns
    -------
    class_spec : dict
        Dictionary describing the parent, attributes, methods,
        staticmethods, and classmethods
    """
    cls_spec = {
        "type": "class",
        "name": cls.__name__,
        "parent": get_parent(cls),
        "attributes": [],
        "classmethods": [],
        "staticmethods": [],
        "methods": [],
    }
    # get members of the class
    members = inspect.getmembers(cls)

    # prepate list of members to ignore
    obj_fields = dir(object)
    ignore_fields = ["__class__", "__dict__", "__module__", "__weakref__"]
    for member in members:
        try:
            if member[0] == "__init__":
                cls_spec["methods"].append(map_function(member[1]))

            elif member[0] in obj_fields or member[0] in ignore_fields:
                pass

            elif inspect.ismethod(member[1]):
                # class method
                cls_spec["classmethods"].append(map_function(member[1]))

            elif inspect.isfunction(member[1]):
                # class method
                c_func = map_function(member[1])
                c_params = c_func["params"]
                if len(c_params) > 0 and c_params[0] == "self":
                    cls_spec["methods"].append(c_func)

                else:
                    cls_spec["staticmethods"].append(c_func)

            elif inspect.isroutine(member[1]):
                pass
            else:
                if is_private(member[0]):
                    c_access = "private"
                else:
                    c_access = "public"
                cls_spec["attributes"].append({
                    "name": member[0],
                    "type": type(member[1]),
                    "access": c_access,
                })
        except Exception as e:
            logger.error(
                "Exception in map_class_python3 for %s of class %s with %s" %
                (member[0], cls.__name__, str(e)))

    return cls_spec


def map_class_python2(cls):
    """Map class with Python2

    Parameters
    ----------
    cls : class
        The class being analyzed

    Returns
    -------
    class_spec : dict
        Dictionary describing the parent, attributes, methods,
        staticmethods, and classmethods
    """
    cls_spec = {
        "type": "class",
        "name": cls.__name__,
        "parent": get_parent(cls),
        "attributes": [],
        "classmethods": [],
        "staticmethods": [],
        "methods": [],
    }
    # prepare list of things to ignore
    obj_fields = dir(object)
    ignore_fields = ["__class__", "__dict__", "__module__", "__weakref__"]

    # get members of the class
    members = inspect.getmembers(cls)

    for member in members:
        try:
            if member[0] == "__init__":
                cls_spec["methods"].append(map_function(member[1]))

            elif member[0] in obj_fields or member[0] in ignore_fields:
                pass

            elif inspect.ismethod(member[1]):
                c_func = map_function(member[1])
                c_params = c_func["params"]
                if len(c_params) > 0 and c_params[0] == "self":
                    cls_spec["methods"].append(c_func)

                else:
                    cls_spec["classmethods"].append(c_func)

            elif inspect.isfunction(member[1]):
                # staticmethod
                c_func = map_function(member[1])
                cls_spec["staticmethods"].append(c_func)

            elif inspect.isroutine(member[1]):
                pass

            else:
                if is_private(member[0]):
                    c_access = "private"
                else:
                    c_access = "public"
                cls_spec["attributes"].append({
                    "name": member[0],
                    "type": type(member[1]),
                    "access": c_access,
                })
        except Exception as e:
            logger.error(
                "Exception caught in map_class_python2 with %s" % str(e))
            logger.error(
                "Failed on member(%s) from class(%s)" %
                (member[0], cls.__name__))

    return cls_spec


def map_class(cls):
    """Map a class

    Scans the class for methods and functions.  Track the parent class if
    available.

    Parameters
    ----------
    cls : class
        The class to map.
    """
    if sys.version_info.major == 3:
        return map_class_python3(cls)
    else:
        return map_class_python2(cls)


def map_function(fnc):
    """Map the function

    Identify the input parameters and access

    Parameters
    ----------
    fnc : function
        The function being analyzed

    Returns
    -------
    fnc_dict : dict
        The dictionary describing the function
    """
    # initialize output
    fnc_dict = OrderedDict([
        ["type", "function"],
        ["name", fnc.__name__],
        ["access", "PUBLIC"],
        ["params", []],
    ])

    # check name to determine if private function
    if is_private(fnc.__name__):
        fnc_dict["access"] = "PRIVATE"

    if inspect.isroutine(fnc):
        return fnc_dict

    # use appropriate inspect method
    if sys.version_info.major == 3:
        # use getfullargspec, not available in Python2
        try:
            func_spec = inspect.getfullargspec(fnc)

            if func_spec.varargs:
                fnc_dict["var_params"] = func_spec.varargs
            if func_spec.varkw:
                fnc_dict["varkw_params"] = func_spec.varkw
        except TypeError as te:
            logger.warning(
                "Exception(%s) with inspect of function %s" %
                (str(te), str(fnc.__func__.__qualname__)))

            return fnc_dict
    else:
        # use available getargspec
        func_spec = inspect.getargspec(fnc)
        if func_spec.varargs:
            fnc_dict["var_params"] = func_spec.varargs
        if func_spec.keywords:
            fnc_dict["varkw_params"] = func_spec.keywords

    fnc_dict["params"] = func_spec.args
    return fnc_dict


if __name__ == "__main__":
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument("module")
    parser.add_argument("--output", default="/tmp/output.plantuml")
    parser.add_argument(
        "--level", default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="The log level")
    parser.add_argument("--log", default="", help="Log file")
    parser.add_argument(
        "--depend", action="store_true", help="Draw dependencies")
    args = parser.parse_args()

    # set log level
    logger.parent.setLevel(args.level)

    if args.log:
        logger.parent.addHandler(logging.FileHandler(args.log, "a"))

    c_package = map_module(
        importlib.import_module(args.module)
    )

    # ---------------------  draw class diagram  ----------------------------
    from boring_stuff.uml.class_diagram import write_class_diagram
    write_class_diagram(c_package, output=args.output, draw_depend=args.depend)
