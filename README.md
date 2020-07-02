# py-boring-stuff

This project contains some functionality that I commonly use.

| Packages | Description |
| :-: | :- |
| Class Helper | Decorator for executing param testing for set methods |
| Parser | Parse and map Python modules |
| Projects | Map a project, and create class diagram |
| UML | Generation code for UML |

## Installation

This project uses setuptools.

~~~bash
python3 setup.py install --user
~~~

## Documentation
Documentation can be generated using the setup.py

~~~bash
$ python3 setup.py build_sphinx
~~~

### Update Sphinx
When adding modules or adding new files, the .rst files in the docs folder need to be updated.

~~~bash
# goto the top level of this project
$ cd py-boring-stuff

# force to update the rst files
$ sphinx-apidoc -o docs/source/ boring_stuff -f
~~~

## Test
Tests are stored in the "test" folder.  It can be run using the following comand.

~~~bash
# install pytest
$ pip3 install pytest --user

# run all tests in test directory
$ python3 -m pytest test
~~~