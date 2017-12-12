from copy import copy
from functools import wraps
from importlib import import_module

try:
    from xmlrpclib import ServerProxy
except ImportError:
    from xmlrpc.client import ServerProxy

import click
from os import listdir

from miqcli.constants import COLLECTIONS_PACKAGE, COLLECTIONS_ROOT, PACKAGE, \
    PYPI, VERSION
from miqcli.utils import get_class_methods


class ManageIQ(click.MultiCommand):
    """ManageIQ command line interface.

    ::
    Class is the main entry point to the miq cli.
    """

    def list_commands(self, ctx):
        """Return a list of available commands.

        Traverses the collections package to get all module names. Module
        names are the name of the command itself.

        :param ctx: Click context.
        :type ctx: Namespace
        :return: Available commands.
        :rtype: list
        """
        collections = list()
        for filename in listdir(COLLECTIONS_ROOT):
            if '__init__' in filename:
                continue
            if filename.endswith('.py'):
                collections.append(filename[:-3])
        collections.sort()
        return collections

    def get_command(self, ctx, name):
        """Return the command (collections) object based on the command
        selected to run.

        Imports the collection module based on the command to run and creates
        a collection object. Which then returns the sub command to be run for
        that specific collection.

        :param ctx: Click context.
        :type ctx: Namespace
        :param name: Command name.
        :type name: str
        :return: Click command object.
        :rtype: object
        """
        miq_module = import_module(COLLECTIONS_PACKAGE + '.' + name)
        collection = miq_module.Collections()
        return SubCollections(collection, collection.__doc__)

    def invoke(self, ctx):
        """Invoke the command selected.

        Runs the command given with all its arguments. When no command is
        given it will display the cli with all commands/options. This method
        also checks for the version parameter. When given it will display
        version information about the cli.

        :param ctx: Click context.
        :type ctx: Namespace
        """
        if ctx.params.get('version', False):
            # miq cli version
            msg, version = '', ''

            # get ManageIQ CLI available versions from PYPI
            pypi = ServerProxy(PYPI)
            versions = pypi.package_releases(PACKAGE)

            # lets begin version message formatting
            try:
                version_index = versions.index(VERSION)
                if version_index == 0:
                    status = 'an up-to-date'
                else:
                    status = 'an out-of-date'
            except ValueError:
                status = 'a pre-release'

            # lets finalize version message formatting
            try:
                version = versions[0]
            except IndexError:
                version = 'N/A'
            finally:
                msg = 'Installed version : {0}\nLatest version    : {1}\n\n' \
                    'You are running {2} version of ManageIQ CLI!'.\
                    format(VERSION, version, status)
                click.echo(msg)
                ctx.exit()
        else:
            # invoke the collection
            super(ManageIQ, self).invoke(ctx)


class SubCollections(click.MultiCommand):
    """Sub-collections.

    Class handles creating the click sub-command for the given parent command
    (collection) with all its provided options. I.e.
        - $ miqcli <parent_command> <sub_command>
    """

    def __init__(self, collection, help):
        """Constructor.

        :param collection: Collection object.
        :type collection: object
        :param help: Sub-command help message displayed in the cli.
        :type help: str (class docstring)
        """
        super(SubCollections, self).__init__(help=help)
        self.collection = collection

    def list_commands(self, ctx):
        """Return a list of available sub-commands for the parent command.

        Traverses the collection class to get all method names. Class method
        names are the names of the sub-commands for the parent command.
        """
        return get_class_methods(self.collection.__class__)

    @staticmethod
    def convert_to_function(method):
        """Convert an instancemethod to a function.

        :param method: Instancemethod.
        :type method: object
        :return: Function.
        :rtype: object
        """
        @wraps(method)
        def func(*args, **kwargs):
            """Convert instancemethod to a function.

            :param args: Arguments.
            :type args: dict
            :param kwargs: Named arguments.
            :type kwargs: dict
            :return: Function.
            :rtype: object
            """
            return method(*args, **kwargs)
        return func

    def get_command(self, ctx, name):
        """Return the command object for the sub-command for the given parent
        to run.

        Collects the sub-commands options and sets up all needed attributes.
        Then creates a new click command to return to be run.

        :param ctx: Click context.
        :type ctx: Namespace
        :param name: Sub-command name.
        :type name: str
        :return: Click command object.
        :rtype: object
        """
        method = getattr(self.collection, name)
        new_method = self.convert_to_function(method)

        params = getattr(method, '__click_params__', [])
        new_method.__click_params__ = copy(params)

        attributes = dict()
        try:
            # removes methods documented parameters from showing in help
            attributes['help'] = method.__doc__.split('::')[0].strip()
        except AttributeError:
            # methods docstring does not container documented parameters
            attributes['help'] = method.__doc__

        cmd = click.command(name=name, **attributes)(new_method)
        return cmd


# it all begins here..
cli = ManageIQ(
    help=ManageIQ.__doc__.split('::')[0].strip(),
    params=[
        click.Option(
            param_decls=['--version'],
            is_flag=True,
            help='Show version and exit.'
        )
    ]
)