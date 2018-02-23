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

import click
from manageiq_client.api import APIException
from miqcli.collections import CollectionsMixin
from miqcli.decorators import client_api
from miqcli.utils import log


class Collections(CollectionsMixin):
    """Providers collections."""

    @client_api
    def query(self):
        """Query."""
        raise NotImplementedError

    @client_api
    def create(self):
        """Create."""
        raise NotImplementedError

    @client_api
    def edit(self):
        """Edit."""
        raise NotImplementedError

    @click.argument('prov_id', metavar='PROV_ID', type=int, default='')
    @client_api
    def refresh(self, prov_id):
        """Refresh provider.

        :param prov_id: id of the provider
        :type prov_id: int
        :return: id of the task created to refresh the provider
        :rtype: int
        """
        prov = None
        if prov_id:
            prov = self.collection.__call__(prov_id)
            if prov is None:
                log.abort('Provider with ID: {0} not found!' % prov_id)
            else:
                try:
                    result = prov.action.refresh()
                    log.info(
                        "Task to refresh provider with ID: "
                        "{0} created: {1}".format(
                            prov_id, result["task_id"]))
                    return result["task_id"]
                except APIException as ex:
                    log.abort(
                        'Unable to create a task: refresh provider with ID: '
                        '{0}: {1}'.format(prov_id, ex))
        else:
            log.abort('Set a provider ID to be refreshed.')

    @client_api
    def delete(self):
        """Delete."""
        raise NotImplementedError
