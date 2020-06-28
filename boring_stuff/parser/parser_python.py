#!/usr/bin/env python
from collections import namedtuple, OrderedDict
import os
from pprint import pprint
import re

CLASS_TUPLE = namedtuple("Class", ["name", "extension", "functions"])

RE_IMPORTS = re.compile(r"import ")

# class ($CLASSNAME)($EXTENSION):\n($BODY)
RE_CLASS = re.compile(r"class ([\w\d]+)(\([\w\d]+\))?\:[\n]")
RE_CLASS_FUNC = re.compile(r"    def ([\w\d]+)[\(]([\w\d\,\s]+)[\)\:]")
RE_FUNC = re.compile(r"def ([\w\d]+)[\(]([\w\d\,\s]+)[\)\:]")
RE_TABBED = re.compile(r"(([ ]{4}.*)+\n+)+")
RE_LINE = re.compile(r"[/w/d].*\n")
RE_DOCSTRING = re.compile(r"[\"]{3}[^[\"]{3}]*[\"]{3}")
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

def parse_file(filename):
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
    """
    # ------------------  initialize  variables  ------------------------
    mod_name = filename[:-3]    # drop .py
    mod_name = mod_name.replace(".", "_")
    mod_name = mod_name.replace("/", "_")
    module = OrderedDict([
        ["type", "module"],
        ["name", mod_name],
        ["class_list", []],         #
        ["methods", []],            # methods not in a class
    ])
    class_list = []
    last_class_loc = None

    with open(filename, 'r') as file_in:
        txt  = file_in.read()
        import_matches = RE_IMPORTS.finditer(txt)
        class_matches = RE_CLASS.finditer(txt)


        for cls1 in class_matches:
            # update last class with class methods
            if last_class_loc:
                class_list[-1]["methods"] = parse_functions(\
                    txt[last_class_loc[1]:cls1.start()], True)

            # get parent, or fill with None
            try:
                parent = cls1.group(2)
                parent = parent[1:-1] # trim parenthesis
            except:
                parent = None

            # append class description
            class_list.append(OrderedDict([
                ["type","class"],
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