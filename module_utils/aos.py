#
# Copyright (c) 2017 Apstra Inc, <community@apstra.com>
#
# This code is part of Ansible, but is an independent component.
# This particular file snippet, and this file snippet only, is BSD licensed.
# Modules you write using this snippet, which is embedded dynamically by
# Ansible still belong to the author of the module, and may assign their own
# license to the complete work.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#

"""
This module adds shared support for Apstra AOS modules

In order to use this module, include it as part of your module

from ansible.module_utils.aos import *

"""
import json
import requests
import urllib3


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

MAX_ATTEMPTS = 3


def aos_get(session, endpoint):
    """
    GET request aginst aos RestApi
    :param session: dict
    :param endpoint: string
    :return: dict
    """
    aos_url = "https://{}/api/{}".format(session['server'], endpoint)
    headers = {'AUTHTOKEN': session['token'],
               'Accept': "application/json",
               'Content-Type': "application/json",
               'cache-control': "no-cache"}
    resp_data = {}

    for attempt in range(MAX_ATTEMPTS):
        try:
            response = requests.get(aos_url, headers=headers, verify=False)

            if response.ok:
                return response.json()
            else:
                response.raise_for_status()

        except (requests.ConnectionError,
                requests.HTTPError,
                requests.Timeout) as e:
            return "Unable to connect to server {}: {}".format(aos_url, e)

    return resp_data


def aos_post(session, endpoint, payload):
    """
    POST request aginst aos RestApi
    :param session: dict
    :param endpoint: string
    :param payload: string
    :return: dict
    """
    aos_url = "https://{}/api/{}".format(session['server'], endpoint)
    headers = {'AUTHTOKEN': session['token'],
               'Accept': "application/json",
               'Content-Type': "application/json",
               'cache-control': "no-cache"}
    resp_data = {}

    for attempt in range(MAX_ATTEMPTS):
        try:
            response = requests.post(aos_url,
                                     data=json.dumps(payload),
                                     headers=headers,
                                     verify=False)

            if response.ok:
                return response.json()
            else:
                response.raise_for_status()

        except (requests.ConnectionError,
                requests.HTTPError,
                requests.Timeout) as e:
            return "Unable to connect to server {}: {}".format(aos_url, e)

    return resp_data


def aos_put(session, endpoint, payload):
    """
    PUT request aginst aos RestApi
    :param session: dict
    :param endpoint: string
    :param payload: string
    :return: dict
    """
    aos_url = "https://{}/api/{}".format(session['server'], endpoint)
    headers = {'AUTHTOKEN': session['token'],
               'Accept': "application/json",
               'Content-Type': "application/json",
               'cache-control': "no-cache"}
    resp_data = {}

    for attempt in range(MAX_ATTEMPTS):
        try:
            response = requests.put(aos_url,
                                    data=json.dumps(payload),
                                    headers=headers,
                                    verify=False)

            if response.ok:
                return response.json()
            else:
                response.raise_for_status()

        except (requests.ConnectionError,
                requests.HTTPError,
                requests.Timeout) as e:
            return "Unable to connect to server {}: {}".format(aos_url, e)

    return resp_data


def aos_delete(session, endpoint, aos_id):
    """
    DELETE request aginst aos RestApi
    :param session: dict
    :param endpoint: string
    :param aos_id: string
    :return: dict
    """
    aos_url = "https://{}/api/{}/{}".format(session['server'],
                                            endpoint,
                                            aos_id)
    headers = {'AUTHTOKEN': session['token'],
               'Accept': "application/json",
               'Content-Type': "application/json",
               'cache-control': "no-cache"}
    resp_data = {}

    for attempt in range(MAX_ATTEMPTS):
        try:
            response = requests.delete(aos_url, headers=headers, verify=False)

            if response.ok:
                return response.json()
            else:
                response.raise_for_status()

        except (requests.ConnectionError,
                requests.HTTPError,
                requests.Timeout) as e:
            return "Unable to connect to server {}: {}".format(aos_url, e)

    return resp_data


def find_resource_by_name(resource_data, name):

    my_dict = next((item for item in resource_data['items']
                    if item['display_name'] == name), None)

    if my_dict:
        return my_dict
    else:
        return {}


def find_resource_by_id(resource_data, id):

    my_dict = next((item for item in resource_data['items']
                    if item['id'] == id), None)

    if my_dict:
        return my_dict
    else:
        return {}


def find_resource_item(session, endpoint,
                       resource_name=None,
                       resource_id=None):
    """
    Find an existing resource based on name or id from a given endpoint
    :param session: dict
    :param endpoint: string
    :param resource_name: string
    :param resource_id: string
    :return: Returns collection item (dict)
    """
    resource_data = aos_get(session, endpoint)

    if resource_name:
        return find_resource_by_name(resource_data, resource_name)
    elif resource_id:
        return find_resource_by_id(resource_data, resource_id)
    else:
        return {}