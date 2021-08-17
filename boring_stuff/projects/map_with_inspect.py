#!/usr/bin/env python
from collections import OrderedDict
import importlib
import inspect
from pprint import pprint
import sys


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

    # initialize variables
    module_dict = {}
    class_dict = {}
    func_dict = {}
    dependencies_dict = {}
    variable_dict = {}

    # ----------------------  inspect current  ------------------------------
    # inspect the module
    members = inspect.getmembers(mod, inspect.modulesbyfile)

    for member in members:
        # member is a tuple
        if member[0][:2] == "__" and member[0][-2:] == "__":
            # ignore 'private' members
            continue

        elif inspect.ismodule(member[1]):
            # ----------------------  a module type  ------------------------
            if member[1].__name__[:len(name)] == name:
                # submodule
                module_dict[member[1].__name__] = member[1]
            else:
                # external library...an import
                dependencies_dict[member[1].__name__] = member[1]

        elif inspect.isfunction(member[1]):
            if member[1].__module__ == name:
                # member of this module
                func_dict[member[0]] = member[1]
            else:
                # imported function
                dependencies_dict[member[1].__module__] = \
                    inspect.getmodule(member[1])

        elif inspect.isclass(member[1]):
            if member[1].__module__ == name:
                # member of this module
                class_dict[member[0]] = member[1]
            else:
                # imported class
                dependencies_dict[member[1].__module__] = \
                    inspect.getmodule(member[1])
        else:
            variable_dict[member[0]] = type(member[1])

    has_m = len(module_dict) > 0
    has_c = len(class_dict) > 0
    has_f = len(func_dict) > 0
    has_v = len(variable_dict) > 0

    c_package = {}
    if has_m and not(any([has_c, has_f, has_v])):
        # pure package
        c_package = {
            "type": "package",
            "name": name,
            "subpackages": [],
            "modules": [],
            "misc": [],
        }
        add_modules(c_package, module_dict)
    else:
        # module with some form of variable/function/class
        c_package = {
            "type": "module",
            "name": name,
            "subpackages": [],
            "class_list": [],
            "methods": [],
            "variables": []
        }
        add_modules(c_package, module_dict)
        add_classes(c_package, class_dict)

        for c_method in func_dict:
            c_package["methods"].append(
                map_function(func_dict[c_method])
            )

    return c_package


def add_modules(c_package, mod_dict):
    for c_mod in mod_dict:
        try:
            tmp_mod = map_module(mod_dict[c_mod])
            if tmp_mod["type"] == "package":
                c_package["subpackages"].append(tmp_mod)
            else:
                c_package["modules"].append(tmp_mod)

        except Exception as e:
            print("Caught exception: %s" % str(e))


def add_classes(c_package, class_dict):
    for c_class in class_dict:
        c_package["class_list"].append(
            map_class(class_dict[c_class])
        )


def map_class(cls):
    """Map a class

    Scans the class for methods and functions.  Track the parent class if
    available.

    Parameters
    ----------
    cls : class
        The class to map.
    """
    # ------------------------  get class methods  --------------------------
    methods = dict(inspect.getmembers(cls, inspect.ismethod))
    method_list = []
    for method in methods:
        method_list.append(map_function(methods[method]))

    # ---------------------  get class function  ----------------------------
    # NOTE: this should include classmethod and staticmethods
    funcs = dict(inspect.getmembers(cls, inspect.isfunction))
    func_list = []
    for func in funcs:
        func_list.append(map_function(funcs[func]))

    # -------------------------  identify parent class  ---------------------
    try:
        if len(cls.__bases__) == 0:
            parent = None
        else:
            parent = [i.__name__ for i in cls.__bases__]

    except Exception as e:
        parent = None
        print(e)
        import pdb; pdb.set_trace()

    # --------------------------  initialize class spec  --------------------
    cls_spec = OrderedDict([
        ["type", "class"],
        ["name", cls.__name__],
        ["parent", parent],
        ["attributes", []],  # FIXME: how to identify attributes?
        ["methods", method_list],
        ["functions", func_list],
    ])
    return cls_spec


def map_function(fnc):
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

    # use appropriate inspect method
    if sys.version_info.major == 3:
        # use getfullargspec, not available in Python2
        func_spec = inspect.getfullargspec(fnc)

        if func_spec.varargs:
            fnc_dict["var_params"] = func_spec.varargs
        if func_spec.varkw:
            fnc_dict["varkw_params"] = func_spec.varkw

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
    args = parser.parse_args()

    c_package = map_module(
        importlib.import_module(args.module)
    )
    pprint(c_package)

    # ---------------------  draw class diagram  ----------------------------
    from boring_stuff.uml.class_diagram import write_class_diagram
    write_class_diagram(c_package, output=args.output)
