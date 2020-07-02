#!/usr/bin/env python
from collections import OrderedDict
import os
from boring_stuff.parser.parser_python import parse_file

def map_python(in_dir, base_name=None):
    """Map a python package

    Recursively scan directories and map classes / functions

    Parameters
    ----------
    in_dir : str
        The input directory to scan

    base_name : str or None
        If not provided, use the directory as the base name.
    """
    # -----------------------  initialize variables  ------------------------
    c_dir = os.path.abspath(in_dir)
    base = c_dir[c_dir.rfind("/") + 1:]
    if base_name is None:
        base_name = base

    c_package = OrderedDict([
        ["type", "package"],
        ["name", base_name.replace("/", ".")],
        ["subpackages", []],
        ["modules", []],
        ["misc", []],
    ])
    files = os.listdir(c_dir)

    # ------------------  map current and subdirectories  -------------------

    for tmp_file in files:
        c_file = c_dir + "/" + tmp_file
        if os.path.isdir(c_file):
            # directory
            c_package["subpackages"].append(
                map_python(c_file, base_name=base_name+"."+tmp_file)
            )
        else:
            # files
            if c_file[-3:] == ".py":
                # python module
                c_package["modules"].append(
                    parse_file(c_file, base_name))
            else:
                c_package["misc"].append(c_file)

    return c_package

if __name__ == "__main__":
    # --------------------------  parse commands  ---------------------------
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument("project_dir", help="Project directory")
    parser.add_argument("output", default="/tmp/class_diagram.wsd",
        help="Location to generate the class diagram")
    args = parser.parse_args()


    tmp = map_python(args.project_dir)


    from boring_stuff.uml.class_diagram import write_class_diagram
    write_class_diagram(tmp, output=args.output)
