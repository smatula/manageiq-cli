# Copyright (C) 2017 Red Hat, Inc.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
"""
miqcli.constants values will differ from installation to installation.
"""
import os
import pkg_resources

import click


#: name of miqcli package
PACKAGE = 'miqcli'

try:
    #: Installed version of miqcli
    _miqcli_distribution = pkg_resources.get_distribution(PACKAGE)
    VERSION = str(_miqcli_distribution.parsed_version)
except pkg_resources.DistributionNotFound:
    # This should be very unlikely, as it means this module is being
    # imported without the miqcli package being installed
    VERSION = '0.0.0dev1'

#: base URL of PyPI
PYPI = 'https://pypi.python.org/pypi'

#: current filesystem root of miqcli source
PROJECT_ROOT = os.path.dirname(__file__)

#: current filesystem root of miqcli.collections package
COLLECTIONS_ROOT = os.path.join(PROJECT_ROOT, 'collections')

#: miqcli collections package name
COLLECTIONS_PACKAGE = PACKAGE + '.' + 'collections'

#: expected basedir for systemwide miqcli config file
CFG_DIR = '/etc/miqcli'

#: expected name for miqcli config file
CFG_NAME = 'miqcli'

#: acceptable file extensions for config file
CFG_FILE_EXT = ['.yml', '.yaml']

#: default config for miqcli API client
DEFAULT_CONFIG = {
    'username': 'admin',
    'password': 'smartvm',
    'url': 'https://localhost:8443',
    'enable_ssl_verify': False
}

#: filesystem root for miqcli authentication store
AUTHDIR = os.path.join(os.path.expanduser('~'), ".miqcli/auth")

#: cli entry point click parameters
GLOBAL_PARAMS = [
    click.Option(
        param_decls=['--version'],
        is_flag=True,
        help='Show version and exit.'
    ),
    click.Option(
        param_decls=['--token'],
        help='Token used for authentication to the server.'
    ),
    click.Option(
        param_decls=['--url'],
        help='URL for the ManageIQ appliance.'
    ),
    click.Option(
        param_decls=['--username'],
        help='Username used for authentication to the server.'
    ),
    click.Option(
        param_decls=['--password'],
        help='Password used for authentication to the server.'
    ),
    click.Option(
        param_decls=['--enable-ssl-verify/--disable-ssl-verify'],
        default=None,
        help='Enable or disable ssl verification, default is on.'
    ),
    click.Option(
        param_decls=['--verbose'],
        is_flag=True,
        help='Verbose mode.'
    )
]
