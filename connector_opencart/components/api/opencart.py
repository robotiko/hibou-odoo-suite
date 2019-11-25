# © 2019 Hibou Corp.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import requests
from urllib.parse import urlencode
from json import loads, dumps
import logging

_logger = logging.getLogger(__name__)


class Opencart:

    def __init__(self, base_url, restadmin_token):
        self.base_url = str(base_url) + '/api/rest_admin/'
        self.restadmin_token = restadmin_token
        self.session = requests.Session()
        self.session.headers['X-Oc-Restadmin-Id'] = self.restadmin_token

    @property
    def orders(self):
        return Orders(connection=self)

    @property
    def stores(self):
        return Stores(connection=self)

    def get_headers(self, url, method):
        headers = {}
        if method in ('POST', 'PUT', ):
            headers['Content-Type'] = 'application/json'
        return headers

    def send_request(self, method, url, params=None, body=None):
        encoded_url = url
        if params:
            encoded_url += '?%s' % urlencode(params)
        headers = self.get_headers(encoded_url, method)

        if method == 'GET':
            return loads(self.session.get(url, params=params, headers=headers).text)
        elif method == 'PUT' or method == 'POST':
            return loads(self.session.put(url, data=body, headers=headers).text)


class Resource:
    """
    A base class for all Resources to extend
    """

    def __init__(self, connection):
        self.connection = connection

    @property
    def url(self):
        return self.connection.base_url + self.path


class Orders(Resource):
    """
    Retrieves Order details
    """

    path = 'orders'

    def all(self, id_larger_than=None):
        url = self.url
        if id_larger_than:
            url += '/id_larger_than/%s' % id_larger_than
        return self.connection.send_request(method='GET', url=url)

    def get(self, id):
        url = self.url + ('/%s' % id)
        return self.connection.send_request(method='GET', url=url)

    def ship(self, id, tracking):
        url = self.connection.base_url + ('trackingnumber/%s' % id)
        res = self.connection.send_request(method='PUT', url=url, body=self.get_tracking_payload(tracking))
        return self.connection.send_request(method='POST', url=url, body=self.get_status_payload('Shipped'))


    def cancel(self, id):
        url = self.connection.base_url + ('order_status/%s' % id)
        return self.connection.send_request(method='POST', url=url, body=self.get_status_payload('Canceled'))

    def get_status_payload(self, status):
        """
        {
          "status": "Canceled"
        }
        """
        payload = {
            "status": status,
        }
        return dumps(payload)

    def get_tracking_payload(self, tracking):
        """
        {
          "tracking": "5559994444"
        }
        """
        payload = {
            "tracking": tracking,
        }
        return dumps(payload)


class Stores(Resource):
    """
    Retrieves Store details
    """

    path = 'stores'

    def all(self):
        return self.connection.send_request(method='GET', url=self.url)

    def get(self, id):
        url = self.url + ('/%s' % id)
        return self.connection.send_request(method='GET', url=url)
