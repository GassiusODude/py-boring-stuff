import pytest
from boring_stuff.class_helper.setter import Setter
SEXES = ["Male", "Female"]
class Person(object):
    def __init__(self, name="Bob", age=1, sex="Male"):
        self.name = name
        self.age = age
        self.sex = sex

    @Setter(min=0, max=1000, dtype=float)
    def set_age(self, new_age):
        self.age = new_age

    @Setter(enum=SEXES)
    def set_sex(self, new_sex):
        self.sex = new_sex

    def __repr__(self):
        out = "I am %s.  I am %1.1f years old"%(self.name, self.age)
        return out
p = Person()

def test_set_range():
    with pytest.raises(AssertionError):
        p.set_age(-3)
    with pytest.raises(AssertionError):
        p.set_age(1003)

def test_enum():
    with pytest.raises(TypeError):
        p.set_age("Hello")

def test_dtype():
    with pytest.raises(AssertionError):
        p.set_sex("Hello")


if __name__ == "__main__":
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument("age", type=float, help="Age")
    parser.add_argument("sex", default="Male")
    args = parser.parse_args()

    p = Person()
    p.set_age(args.age)
    p.set_sex(args.sex)
    print(p)
