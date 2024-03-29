#!/usr/bin/env python
"""Test inspection with boring_stuff project

Use the knowledge of the structure of boring_stuff
to test various parts of the inspection process.

.. warning:: inspect.ismethod (for Python3) fails to
    separate methods from functions.
"""
import sys
from boring_stuff.projects import map_with_inspect as MWI


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


def test_class_mapping():
    class MyClass(object):

        var1 = 1

        def __init__(self):
            pass

        @classmethod
        def print_name(cls, name):
            print(name)

        @staticmethod
        def display():
            print("Hello")

    cls_spec = MWI.map_class(MyClass, access_level=2)
    print(cls_spec)
    static_methods = ["display"]
    for k in cls_spec["staticmethods"]:
        assert k["name"] in static_methods

    class_methods = ["print_name"]
    for k in cls_spec["classmethods"]:
        assert k["name"] in class_methods

    var_list = ["var1"]
    for v in cls_spec["attributes"]:
        assert v["name"] in var_list
