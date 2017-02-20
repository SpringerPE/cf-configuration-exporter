# cf-configuration-exporter

`cf-configuration-exporter` is a simple utility whose aim is to generate a 
configuration manifest from a live installation of CloudFoundry.

The utility is meant to be used in combination with 2 other projects:

- https://github.com/SpringerPE/python-cfconfigurator
- https://github.com/SpringerPE/ansible-cloudfoundry-role

and helps you get started with an initial manifest without having to extract manually
all the information needed.

The code is compatible with Python 3

Documentation of the APIs used:

* https://apidocs.cloudfoundry.org
* https://docs.cloudfoundry.org/api/uaa


## Example

Install via pip: `pip install cfconfigurator`

## Upload to PyPI

1. Create a `.pypirc` configuration file. This file holds your information for authenticating with PyPI.

   ```
   [distutils]
   index-servers = pypi
   
   [pypi]
   repository=https://pypi.python.org/pypi
   username=your_username
   password=your_password
   ```
2. Login and upload it to PyPI

   ```
   python setup.py register -r pypi
   python setup.py sdist upload -r pypi
   ```

## Author

Springer Nature Platform Engineering, Claudio Benfatto (claudio.benfatto@springer.com)

Copyright 2017 Springer Nature