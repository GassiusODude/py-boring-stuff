#!/usr/bin/env python
"""Test inspection with boring_stuff project

Use the knowledge of the structure of boring_stuff
to test various parts of the inspection process.

.. warning:: inspect.ismethod (for Python3) fails to
    separate methods from functions.
"""
import sys
from boring_stuff.projects import map_with_inspect as MWI


def test_class_map():
    from boring_stuff.class_helper.setter import Setter
    setter_dict = MWI.map_class(Setter)
    print("Python version = ", sys.version)
    print(setter_dict)

    assert setter_dict["type"] == "class"
    assert setter_dict["name"] == "Setter"

    # check methods
    methods = setter_dict["methods"]
    assert len(methods) == 2, "Expecting methods __init__ and __call__"


def test_module_with_class():
    from boring_stuff.class_helper import setter
    setter_mod = MWI.map_module(setter)

    # assert mod name and type
    assert setter_mod["name"] == "boring_stuff.class_helper.setter"
    assert setter_mod["type"] == "module"

    # assert class
    c_list = setter_mod["class_list"]
    assert c_list[0]["type"] == "class"
    assert c_list[0]["name"] == "Setter"


def test_pure_package():
    import boring_stuff
    bs_mod = MWI.map_module(boring_stuff)

    assert bs_mod["name"] == "boring_stuff"
    assert bs_mod["type"] == "package"

    subpackages = [
        "boring_stuff.class_helper",
        "boring_stuff.parser",
        "boring_stuff.projects",
        "boring_stuff.uml"
    ]
    for sub_mod in bs_mod["subpackages"]:
        assert sub_mod["name"] in subpackages
