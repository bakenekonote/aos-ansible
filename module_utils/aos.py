# Copyright (c) 2017 Apstra Inc, <community@apstra.com>

"""
This module adds shared support for Apstra AOS modules

In order to use this module, include it as part of your module

from ansible.module_utils.aos import *

"""
import os
import json
import requests
import ipaddress
from requests.adapters import HTTPAdapter
from ansible.module_utils.parsing.convert_bool import boolean


def requests_header(session):
    return {'AUTHTOKEN': session['token'],
            'Accept': "application/json",
            'Content-Type': "application/json",
            'cache-control': "no-cache"}


def set_requests_verify():
    return boolean(os.environ.get('AOS_VERIFY_CERTIFICATE', 'True'))


def requests_retry(retries=3, session=None):

    session = session or requests.Session()
    adapter = HTTPAdapter(max_retries=retries)

    session.mount('http://', adapter)
    session.mount('https://', adapter)

    return session


def requests_response(response):
    return response.json() if response.ok else response.raise_for_status()


def aos_get(session, endpoint):
    """
    GET request aginst aos RestApi
    :param session: dict
    :param endpoint: string
    :return: dict
    """
    aos_url = "https://{}/api/{}".format(session['server'], endpoint)
    headers = requests_header(session)
    response = requests_retry().get(aos_url,
                                    headers=headers,
                                    verify=set_requests_verify())

    return requests_response(response)


def aos_post(session, endpoint, payload):
    """
    POST request aginst aos RestApi
    :param session: dict
    :param endpoint: string
    :param payload: string
    :return: dict
    """
    aos_url = "https://{}/api/{}".format(session['server'], endpoint)
    headers = requests_header(session)
    response = requests_retry().post(aos_url,
                                     data=json.dumps(payload),
                                     headers=headers,
                                     verify=set_requests_verify())

    return requests_response(response)


def aos_put(session, endpoint, payload):
    """
    PUT request aginst aos RestApi
    :param session: dict
    :param endpoint: string
    :param payload: string
    :return: dict
    """
    aos_url = "https://{}/api/{}".format(session['server'], endpoint)
    headers = requests_header(session)
    response = requests_retry().put(aos_url,
                                    data=json.dumps(payload),
                                    headers=headers,
                                    verify=set_requests_verify())

    return response


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
    headers = requests_header(session)
    response = requests_retry().delete(aos_url,
                                       headers=headers,
                                       verify=set_requests_verify())

    return response


def _find_resource(resource_data, key, keyword):
    for item in resource_data['items']:
        if item[keyword] == key:
            return item
    return {}


def find_resource_by_name(resource_data, name):
    return _find_resource(resource_data, name, "display_name")


def find_resource_by_id(resource_data, uuid):
    return _find_resource(resource_data, uuid, "id")


def find_resource_item(session, endpoint,
                       name=None,
                       uuid=None):
    """
    Find an existing resource based on name or id from a given endpoint
    :param session: dict
    :param endpoint: string
    :param name: string
    :param uuid: string
    :return: Returns collection item (dict)
    """
    resource_data = aos_get(session, endpoint)

    if name:
        return find_resource_by_name(resource_data, name)
    elif uuid:
        return find_resource_by_id(resource_data, uuid)
    else:
        return {}


def find_bp_system_nodes(session, blueprint_id, nodes=None):
    """
    Find the Blueprint node ID for all nodes or the given device names
    :param session: dict
    :param blueprint_id: string
    :param nodes: list
    :return: list
    """
    endpoint = "blueprints/{}/ql".format(blueprint_id)
    device_query = {
        "query": "{ redundancy_group_nodes{id, label}, system_nodes{id, label}}"
    }

    node_data = aos_post(session, endpoint, device_query)

    resp_nodes = []

    if nodes:
        for n in node_data['data']['system_nodes']:
            if n['label'] in nodes:
                resp_nodes.append(n)
        for n in node_data['data']['redundancy_group_nodes']:
            if n['label'] in nodes:
                resp_nodes.append(n)

        return resp_nodes

    else:
        return node_data['data']['system_nodes']


def validate_vni_id(vni_id):
    """
    Validate VNI ID provided is an acceptable value
    :param vni_id: int
    :return: list
    """
    errors = []
    if vni_id < 4096 or vni_id > 16777213:
        errors.append("Invalid ID: must be a valid VNI number between 4096"
                      " and 16777214")

    return errors


def validate_vlan_id(vlan_id):
    """
    Validate VLAN ID provided is an acceptable value
    :param vlan_id: int
    :return: list
    """
    errors = []
    if vlan_id < 1 or vlan_id > 4094:
        errors.append("Invalid ID: must be a valid vlan id between 1"
                      " and 4094")

    return errors


def validate_asn_ranges(ranges):
    """
    Validate ASN ranges provided are valid and properly formatted
    :param ranges: list
    :return: bool
    """
    errors = []

    for asn_range in ranges:
        if not isinstance(asn_range, list):
            errors.append("Invalid range: must be a list")
        elif len(asn_range) != 2:
            errors.append("Invalid range: must be a list of 2 members")
        elif any(map(lambda r: not isinstance(r, int), asn_range)):
            errors.append("Invalid range: Expected integer values")
        elif asn_range[1] <= asn_range[0]:
            errors.append("Invalid range: 2nd element must be bigger than 1st")
        elif asn_range[0] < 1 or asn_range[1] > 2 ** 32 - 1:
            errors.append("Invalid range: must be a valid range between 1"
                          " and 4294967295")

    return errors


def validate_vni_ranges(ranges):
    """
    Validate VNI ranges provided are valid and properly formatted
    :param ranges: list
    :return: list
    """
    errors = []

    for vni_range in ranges:
        if not isinstance(vni_range, list):
            errors.append("Invalid range: must be a list")
        elif len(vni_range) != 2:
            errors.append("Invalid range: must be a list of 2 members")
        elif any(map(lambda r: not isinstance(r, int), vni_range)):
            errors.append("Invalid range: Expected integer values")
        elif vni_range[1] <= vni_range[0]:
            errors.append("Invalid range: 2nd element must be bigger than 1st")
        elif vni_range[0] < 4095 or vni_range[1] > 16777213:
            errors.append("Invalid range: must be a valid range between 4096"
                          " and 16777214")

    return errors


def validate_ip_format(addrs, ip_version):
    """
    Validate IP addresses or subnets provided
    :param addrs: list
    :param ip_version: str ('ipv4', 'ipv6')
    :return: bool
    """

    assert ip_version in ['ipv4', 'ipv6'], \
        "Invalid IP version: {}".format(ip_version)
    errors = []

    for addr in addrs:
        try:
            results = ipaddress.ip_network(addr)
            if results.version != int(ip_version[3]):
                errors.append("{} is not a valid {} address or subnet"
                              .format(addr, ip_version))

        except ValueError:
            errors.append("Invalid format: {}".format(addrs))

    return errors
