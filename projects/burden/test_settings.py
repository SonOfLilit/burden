"""
Settings used for test automation.

Since `manage.py test` with `django_nose` does not support passing command-line
parameters to `nosetests`, we have to pass them here.
"""

from settings import *  # pylint: disable=W0403

NOSE_ARGS = ['--with-machineout', '--machine-output']
