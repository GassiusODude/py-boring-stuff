from collections import OrderedDict
import importlib
import inspect
from pprint import pprint

def map_module(mod):
    """Map Module

    Parameters
    ----------
    mod : Python module
        Module to map.

    Returns
    -------
    c_package : dict
        Dictionary describing the interconnecting classes and packages
    """
    # scan for submodules
    mod_dict = dict(inspect.getmembers(mod, inspect.ismodule))

    # scan for classes
    class_dict = dict(inspect.getmembers(mod, inspect.isclass))

    # scan for functions
    method_dict = dict(inspect.getmembers(mod, inspect.isfunction))

    if len(class_dict) > 0 or len(method_dict) > 0:
        c_package = OrderedDict([
            ["type", "module"],
            ["name", mod.__name__],
            ["class_list", []],         #
            ["methods", []],            # methods not in a class
        ])

        for c_class in class_dict:

            if mod.__name__ in class_dict[c_class].__module__:
                c_package["class_list"].append(
                    map_class(class_dict[c_class])
                )

        for c_method in method_dict:
            c_package["methods"].append(
                map_function(method_dict[c_method])
            )

    #elif mod_dict:
    else:
        c_package = OrderedDict([
            ["type", "package"],
            ["name", mod.__name__],
            ["subpackages", []],
            ["modules", []],
            ["misc", []],
        ])
        for c_mod in mod_dict:
            try:
                if mod_dict[c_mod].__package__ is None or \
                    mod.__name__ in mod_dict[c_mod].__package__:
                    tmp_mod = map_module(mod_dict[c_mod])
                    if tmp_mod["type"] == "package":
                        c_package["subpackages"].append(tmp_mod)
                    else:
                        c_package["modules"].append(tmp_mod)

            except Exception as e:
                print("Caught exception: %s"%str(e))


    return c_package

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
        parent = cls.__bases__[0].__name__
        print("Parent of %s is %s"%(str(cls), str(parent)))

    except:
        parent = None

    # --------------------------  initialize class spec  --------------------
    cls_spec = OrderedDict([
        ["type","class"],
        ["name", cls.__name__],
        ["parent", parent],
        ["attributes", []],#FIXME: how to identify attributes?
        ["methods", method_list],
        ["functions", func_list],
    ])
    return cls_spec

def map_function(fnc):
    func_spec = inspect.getargspec(fnc)
    fnc = OrderedDict([
        ["type", "function"],
        ["name", fnc.__name__],
        ["access", "PUBLIC"],
        ["params", func_spec.args],
    ])
    return fnc

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

    from boring_stuff.uml.class_diagram import write_class_diagram
    write_class_diagram(c_package, output=args.output)