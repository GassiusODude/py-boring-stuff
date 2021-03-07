from setuptools import setup, find_packages
from setuptools.extension import Extension
#from Cython.Build import cythonize
name = "py-boring-stuff"
release = "1.0"
version = "0.1"
extensions = []

setup(
    name=name,
    version=version,
    description="Keith Chow's library to handle the boring stuff",
    url="",
    author="Keith Chow",
    license="MIT",
    packages=find_packages(),
    tests_require=["pytest"],
    setup_requires=[],
    install_requires=[
        #private repo
        ],
    dependency_links=[
      #'git+ssh://git@github.com/username/private_repo.git#egg=private_package_name-1.1',
        ],
    #ext_modules = cythonize(extensions),
    command_options={
        'build_sphinx': {
            'project': ('setup.py', name),
            'version': ('setup.py', version),
            'release': ('setup.py', release),
            'source_dir': ('setup.py', 'docs/source')
            }
        },
    )