#!/usr/bin/env python
"""Python Parser Module

This module can be applied to scan a Python module and map
the classes and functions within.
"""
from collections import OrderedDict
import os
import re
import logging

logger = logging.getLogger("boring_stuff.parser.parser_python")

"""Regular expression for 'class signature"""
RE_CLASS = re.compile(r"class ([\w\d]+)(\([\w\d]+\))?\:[\n]")
RE_CLASS_FUNC = re.compile(r"    def ([\w\d]+)[\(]([\w\d\,\s]+)[\)\:]")
RE_FUNC = re.compile(r"def ([\w\d]+)[\(]([\w\d\,\=\s]+)[\)\:]")
RE_PARAMS = re.compile(r"([\w\d]+)[\,\s]*")


def parse_functions(txt, class_method=True):
    """parse_function

    Parse for a list of function.

    Parameters
    ----------
    txt : str
        This is the string of text to parse for function
        signatures.

    class_method : bool
        If true, expects four spaces prior to "def" as
        described in PEP8.

    Returns
    -------
    func_list : list
        List of functions found.  Each func description is
        a dictionary with the fields:
        type : str
            function
        name : str
            Name of the function
        access : str
            "PUBLIC", "PROTECTED", "PRIVATE" base on name
        params : list
            List of parameters (just name)
    """
    func_list = []
    if class_method:
        func_matches = RE_CLASS_FUNC.finditer(txt)
    else:
        func_matches = RE_FUNC.finditer(txt)

    for func in func_matches:
        # prep param list
        params = RE_PARAMS.finditer(func.group(2))
        param_list = []
        for param in params:
            param_list.append(param.group(1))

        # determine access by name
        f_name = func.group(1)
        if f_name[:2] == "__":
            access = "PRIVATE"
        elif f_name[:1] == "_":
            access = "PROTECTED"
        else:
            access = "PUBLIC"

        func_list.append(OrderedDict([
            ["type", "function"],
            ["name", f_name],
            ["access", access],
            ["params", param_list],
        ]))
    return func_list


def parse_file(filename, base_name=None):
    """Parse a python file

    Scans for classes and

    Parameters
    ----------
    filename : str
        The file path to the python module.

    Returns
    -------
    module : dict
        Dictionary with:
        type : str
        name : str
        class_list : list (list of class specs)
        methods : list (list of function specs)

    base_name : str or None
        If provided, the name of the module will
        follow base_name + "." + file_name.
    """
    # ------------------  initialize  variables  ------------------------
    # get file path and remove the directory
    full_path = os.path.abspath(filename)
    base = full_path[full_path.rfind("/") + 1:-3]   # drop ".py"

    if base_name is None:
        base_name = ""
        mod_name = base
    else:
        mod_name = base_name + "." + base

    # mod_name = mod_name.replace(".", "_")
    # mod_name = mod_name.replace("/", "_")
    module = OrderedDict([
        ["type", "module"],
        ["name", mod_name],
        ["class_list", []],         #
        ["methods", []],            # methods not in a class
    ])
    class_list = []
    last_class_loc = None

    with open(filename, 'r') as file_in:
        txt = file_in.read()

        # --------------------  detect classes  -----------------------------
        class_matches = RE_CLASS.finditer(txt)

        for cls1 in class_matches:
            # update last class with class methods
            if last_class_loc:
                class_list[-1]["methods"] = parse_functions(
                    txt[last_class_loc[1]:cls1.start()], True)

            # get parent, or fill with None
            try:
                parent = cls1.group(2)
                parent = parent[1:-1]  # trim parenthesis
            except Exception as e:
                logger.warn("parse_file get parent failed with %s" % str(e))
                parent = None

            # append class description
            class_list.append(OrderedDict([
                ["type", "class"],
                ["name", cls1.group(1)], ["parent", parent],
                ["signature_loc", (cls1.start(), cls1.end())],
                ["attributes", []], ["methods", []],
            ]))

            # update the last class signature  for class methods search
            last_class_loc = (cls1.start(), cls1.end())

        if last_class_loc:
            # update last class methods
            class_list[-1]["methods"] = \
                parse_functions(txt[last_class_loc[1]:], True)

            # update the module's class_list
            module["class_list"] = class_list
        else:
            # module with functions only
            module["methods"] = parse_functions(txt, False)

    return module
