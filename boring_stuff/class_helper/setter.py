#!/usr/bin/env python
"""Set Method Helper

This module provides a class decorator to help set up
set methods.  The decorator allows specifying some
common expectations of parameters to include


Examples
--------
Range limitation on the parameter
>>> @Setter(min=1, max=12)
... def set_month(self, value):
...     self.value = value

Enumeration limitation
>>> @Setter(enum=["Head", "Tail"])
... def set_coin_toss(self, toss):
...     self.toss = toss
"""


class Setter(object):
    """Setter error checking decorator

    Helper function for creating setters

    Attributes
    ----------
    dtype : type or None
        Expected type of the property being set

    min : numeric
        Minimum value

    max : numeric
        Maximum value allowed

    enum : list
        Allowable values
    """
    def __init__(self, *args, **kwargs):
        self.dtype = kwargs.get("dtype")
        self.min = kwargs.get("min")
        self.max = kwargs.get("max")
        self.enum = kwargs.get("enum")

    def __call__(self, func):
        def wrapper(obj, value):
            if self.dtype is not None:
                try:
                    value = self.dtype(value)
                except Exception as e:
                    print(e)
                    raise TypeError(
                        "Expecting %s but got %s"
                        % (self.dtype, type(value)))

            # check min
            if self.min is not None:
                assert value >= self.min, "Minumum is %s" % str(self.min)

            # check max
            if self.max is not None:
                assert value <= self.max, "Maximum is %s" % str(self.max)

            # check enum
            if self.enum is not None:
                assert value in self.enum, \
                    ValueError("Expecting in %s" % self.enum)

            # ------------------  run function  -----------------------------
            return func(obj, value)

        return wrapper
