# cf-configuration-exporter

`cf-configuration-exporter` is a simple utility whose aim is to generate a 
configuration manifest from a live installation of CloudFoundry.

The utility is meant to be used either in combination with the CF configurator project:

- https://github.com/SpringerPE/python-cfconfigurator
- https://github.com/SpringerPE/ansible-cloudfoundry-role

or with the following terraform provider:

- https://github.com/mevansam/terraform-provider-cf

and helps you get started with an initial manifest or terraform resources without having to extract manually
all the information needed.

The code is compatible with Python 3

Documentation of the APIs used:

* https://apidocs.cloudfoundry.org
* https://docs.cloudfoundry.org/api/uaa

#INSTALLATION

## Example

Install via pip: `pip install cf-configuration-exporter`

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

#USAGE

```
Define the following env variables:

`EXPORTER_API_URL` = the endpoint of the Cloudfoundry API
`EXPORTER_ADMIN_USER` = username used for logging in to CloudFoundry
`EXPORTER_ADMIN_PASSWORD` = password used for logging in to Cloudfoundry
`EXPORTER_EXCLUDE_ENV_VARS` = list of `,` separated strings. The env variables whose name starts by
                                                         one of the prefixes listed will not be exported.
```

You can run the utility by executing the run script:

```
./run
```

or after installing the pip package

```
python setup.py install
```

by running

```
cf_export_configuration
```

## Author

Springer Nature Platform Engineering, Claudio Benfatto (claudio.benfatto@springer.com)

Copyright 2017 Springer Nature