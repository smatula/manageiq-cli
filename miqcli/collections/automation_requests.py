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
from collections import OrderedDict
from manageiq_client.api import APIException

from miqcli.constants import OSP_FIP_PAYLOAD, SUPPORTED_AUTOMATE_REQUESTS
from miqcli.decorators import client_api
from miqcli.provider import Networks, Tenant
from miqcli.utils import log, get_input_data


class Collections(object):
    """Automation requests collections."""

    @click.option('--method', type=click.Choice(SUPPORTED_AUTOMATE_REQUESTS),
                  required=True, help='automation request method.')
    @click.option('--payload', type=str,
                  help='automation request payload data.')
    @click.option('--payload_file', type=str,
                  help='filename containing JSON formatted payload data for '
                       'automation request.')
    @client_api
    def create(self, method, payload, payload_file,):
        """Create an automation request

        ::
        Builds the payload data for the request (performing all necessary id
        lookups) and then submits the automation request to the server.

        :param method: automation request to run
        :type method: str
        :param payload: json data in str format
        :type payload: str
        :param payload_file: file location of the payload
        :type payload_file: str
        :return: automation request ID
        :rtype: str
        """
        _payload = None

        log.info("Attempt to create an automation request")

        # get the data from user input
        input_data = get_input_data(payload, payload_file)

        # RFE: make generic as possible, remove conditional if possible
        if method == SUPPORTED_AUTOMATE_REQUESTS[0]:
            # generic request, default behavior passthrough payload data
            _payload = input_data
        elif method == SUPPORTED_AUTOMATE_REQUESTS[1]:
            # set the floating ip if set by the user
            if 'fip_pool' in input_data:
                # lookup cloud network resource to get the id
                # TODO: need to have user set the provider
                networks = Networks('OpenStack', self.api, 'public')
                OSP_FIP_PAYLOAD['parameters']['cloud_network_id'] = \
                    networks.get_id(input_data['fip_pool'])

                # lookup cloud tenant
                # TODO: need to have user set the provider
                tenant = Tenant('OpenStack', self.api)
                OSP_FIP_PAYLOAD['parameters']['cloud_tenant_id'] = \
                    tenant.get_id(input_data['tenant'])

            _payload = OSP_FIP_PAYLOAD

        try:
            # BUG: #93
            outcome = self.action(_payload)
            req_id = outcome[0].id
            log.info('Automation request created: %s.' % req_id)
            return req_id
        except APIException as ex:
            log.abort('Unable to create automation request: %s' % ex)

    @client_api
    def approve(self):
        """Approve."""
        raise NotImplementedError

    @client_api
    def deny(self):
        """Deny."""
        raise NotImplementedError

    @click.argument('req_id', metavar='ID', type=str, default='')
    @client_api
    def status(self, req_id):
        """Print the status for a automation request.

        ::
        Handles getting information for an existing automation request and
        displaying/returning back to the user.

        :param req_id: id of the automation request
        :type req_id: str
        :return: automation request object or list of automation request
            objects
        """
        status = OrderedDict()

        if req_id:
            automation_requests = self.api.basic_query(
                self.collection, ("id", "=", req_id))

            if len(automation_requests) < 1:
                log.warning('Automation request id: %s not found!' % req_id)
                return

            req = automation_requests[0]
            status['state'] = req.request_state
            status['status'] = req.status
            status['message'] = req.message
            log.info('-' * 50)
            log.info('Automation request'.center(50))
            log.info('-' * 50)
            log.info(' * ID: %s' % req_id)
            for key, value in status.items():
                log.info(' * %s: %s' % (key.upper(), value))
            log.info('-' * 50)

            return req
        else:
            automation_requests = self.api.basic_query(
                self.collection, ("request_state", "!=", "finished"))

            if len(automation_requests) < 1:
                log.warning('No active automation requests at this time.')
                return None

            log.info('-' * 50)
            log.info(' Active automation requests'.center(50))
            log.info('-' * 50)

            for item in automation_requests:
                log.info(' * ID: %s\tINSTANCE: %s\t STATE: %s\t STATUS: %s' %
                         (item.id, item.options, item.request_state,
                          item.status))
            log.info('-' * 50)

            return automation_requests
