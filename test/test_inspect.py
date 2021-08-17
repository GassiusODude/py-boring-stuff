from boring_stuff.projects import map_with_inspect as MWI


def test_class_map():
    from boring_stuff.class_helper.setter import Setter
    setter_dict = MWI.map_class(Setter)
    print(setter_dict)

    assert setter_dict["type"] == "class"
    assert setter_dict["name"] == "Setter"

    # check methods
    methods = setter_dict["methods"]
    assert len(methods) == 2, "Expecting methods __init__ and __call__"

