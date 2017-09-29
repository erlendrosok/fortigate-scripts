#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

Author:         Erlend Røsok
Mail:           erlendr@met.no
Date:           27.09.2017
Description:    Gets the supported configuration from
                one fortigate via API calls, and pushes
                the configuration to another via API calls

Supported configurations:

* vdom,
* interface
* zone
* static routes
* policy routes
* address
* address groups
* service
* service-groups
* policies

"""

import sys
import getpass
import json
import fgapi
import argparse

# ArgParse

parser = argparse.ArgumentParser()
parser.add_argument('-s',
                    action="store",
                    dest="source",
                    help="The fortigate you wish to copy from")
parser.add_argument('-d',
                    action="store",
                    dest="destination",
                    help="The fortigate you wish to copy to")
args = parser.parse_args()

pri = args.source
sec = args.destination

# Get username and password
username = input('Username: ')
password = getpass.getpass('Password: ')


def move_to_front(key, mylist):
    """ move element to front of list """

    for i in range(len(mylist[:mylist.index(key)]), -1, -1):
        mylist[i] = mylist[i - 1]
    mylist[0] = key


def main():
    """ Copy configuration from one fortigate to another """

    login_pri = fgapi.Fortigate(ip=pri,
                                vdom='root',
                                user=username,
                                passwd=password)
    login_sec = fgapi.Fortigate(ip=pri,
                                vdom='root',
                                user=username,
                                passwd=password)
    # VDOM

    # Get vdom configurations
    vdom_error_codes = []
    pri_vdoms = json.loads(login_pri.GetVdom())
    sec_vdoms = json.loads(login_sec.GetVdom())

    pri_vdoms = pri_vdoms['results']
    sec_vdoms = sec_vdoms['results']
    pri_vdom_list = list(map(lambda x: x['name'], pri_vdoms))
    sec_vdom_list = list(map(lambda x: x['name'], sec_vdoms))

    # Push vdom configration
    for vdom in pri_vdoms:
        if vdom['name'] not in sec_vdom_list:
            payload = {'json': vdom}
            add_vdom = login_sec.ApiAdd('cmdb/system/vdom/', payload)
            if add_vdom != 200:
                vdom_error_codes.append(add_vdom)
                print('ERROR ' + add_vdom + ':', 'vdom:', vdom['name'])
    if not vdom_error_codes:
        print('\n')
        print('VDOM CONFIGURATION SUCCESSFULL!')
    else:
        print('Number of errors: ', len(vdom_error_codes))
        sys.exit(1)

    # Logout of global
    login_pri.Logout()
    login_sec.Logout()

    # Move root vdom to front so we configure this vdom first
    move_to_front('root', pri_vdom_list)

    # Loop over all vdoms
    for vdom in pri_vdom_list:

        print('\n')
        print('-------------------------')
        print('CONFIGURING', vdom.upper())
        print('-------------------------', '\n')

        # List to contain result, empty is successfull
        result = []

        def push_config(obj, path):
            """ Push configuration to API and return error_code_list """

            error_code_list = []
            payload = {'json': obj}
            r = login_sec_vdom.ApiAdd(path, payload)
            if r != 200:
                error_code_list.append(r)
                print('ERROR ' + str(r) + ':', key)
            return error_code_list

        def report(err_list, term):
            """ Print out the result """

            if not err_list:
                print(term.upper() + ':', 'SUCCESS!')
            else:
                print(term.upper() + ':', 'Number of errors: ', len(err_list))

        # Log into the fortigates
        login_pri_vdom = fgapi.Fortigate(ip=pri,
                                         vdom=vdom,
                                         user=username,
                                         passwd=password)
        login_sec_vdom = fgapi.Fortigate(ip=sec,
                                         vdom=vdom,
                                         user=username,
                                         passwd=password)

        # Get all the json objects from the primary fortigate
        pri_interfaces = login_pri_vdom.GetInterface()
        pri_zones = login_pri_vdom.GetZones()
        pri_s_routes = login_pri_vdom.GetRouterStatic()
        pri_p_routes = login_pri_vdom.GetRouterPolicy()
        pri_addresses = login_pri_vdom.GetAddress()
        pri_addrgrp = login_pri_vdom.GetAddressGroup()
        pri_services = login_pri_vdom.GetServices()
        pri_servicegrp = login_pri_vdom.GetServiceGroup()
        pri_policies = login_pri_vdom.GetPolicies()

        # Get all the json objects from the secondary fortigate
        sec_interfaces = login_sec_vdom.GetInterface()
        sec_zones = login_sec_vdom.GetZones()
        sec_s_routes = login_sec_vdom.GetRouterStatic()
        sec_p_routes = login_sec_vdom.GetRouterPolicy()
        sec_addresses = login_sec_vdom.GetAddress()
        sec_addrgrp = login_sec_vdom.GetAddressGroup()
        sec_services = login_sec_vdom.GetServices()
        sec_servicegrp = login_sec_vdom.GetServiceGroup()
        sec_policies = login_sec_vdom.GetPolicies()

        # Make lists of unique keys to check if objects already exists
        exist_interfaces = list(map(lambda x: x['name'], sec_interfaces))
        exist_zones = list(map(lambda x: x['name'], sec_zones))
        exist_s_routes = list(map(lambda x: x['seq-num'], sec_s_routes))
        exist_p_routes = list(map(lambda x: x['seq-num'], sec_p_routes))
        exist_addresses = list(map(lambda x: x['name'], sec_addresses))
        exist_addrgrp = list(map(lambda x: x['name'], sec_addrgrp))
        exist_services = list(map(lambda x: x['name'], sec_services))
        exist_servicegrp = list(map(lambda x: x['name'], sec_servicegrp))
        exist_policies = list(map(lambda x: x['policyid'], sec_policies))

        # INTERACES
        for interface in pri_interfaces:
            key = interface['name']
            path = 'cmdb/system/interface/'
            if key not in exist_interfaces:
                result = push_config(interface, path)
        report(result, 'interface')
        result = []

        # ZONES
        for zone in pri_zones:
            key = zone['name']
            path = 'cmdb/system/zone/'
            if key not in exist_zones:
                result = push_config(zone, path)
        report(result, 'zone')
        result = []

        # STATIC ROUTES
        for static_route in pri_s_routes:
            key = static_route['seq-num']
            path = 'cmdb/router/static/'
            if key not in exist_s_routes:
                result = push_config(static_route, path,)
        report(result, 'static route')
        result = []

        # POLICY ROUTES
        for policy_route in pri_p_routes:
            key = policy_route['seq-num']
            path = 'cmdb/router/policy/'
            if key not in exist_p_routes:
                result = push_config(policy_route, path)
        report(result, 'policy route')
        result = []

        # ADDRESSES
        for address in pri_addresses:
            key = address['name']
            path = 'cmdb/firewall/address'
            if key not in exist_addresses:
                result = push_config(address, path)
        report(result, 'address')
        result = []

        # ADDRESSES GROUPS
        for addrgrp in pri_addrgrp:
            key = addrgrp['name']
            path = 'cmdb/firewall/addrgrp'
            if key not in exist_addrgrp:
                result = push_config(addrgrp, path)
        report(result, 'address group')
        result = []

        # SERVICES
        for service in pri_services:
            key = service['name']
            path = 'cmdb/firewall.service/custom'
            if key not in exist_services:
                result = push_config(service, path)
        report(result, 'services')
        result = []

        # SERVICES GROUPS
        for servicegrp in pri_servicegrp:
            key = servicegrp['name']
            path = 'cmdb/firewall.service/group'
            if key not in exist_servicegrp:
                result = push_config(servicegrp, path)
        report(result, 'service groups')
        result = []

        # POLICIES
        for policy in pri_policies:
            key = policy['policyid']
            path = 'cmdb/firewall/policy'

            """ Uncomment to enable logging on all policies """
            # policy['logtraffic'] = 'all'
            # policy['logtraffic-start'] = 'enable'

            """ Uncomment to remove comments.
                You might want to do this is you have
                issues with special characters """
            # policy.pop('comments', None)

            """ Since this script doesn't configure
                any webfilter, ips, antivirus profiles
                we change them to the default profiles """
            if policy['application-list']:
                policy['application-list'] = 'default'
            if policy['profile-protocol-options']:
                policy['profile-protocol-options'] = 'default'
            if policy['ips-sensor']:
                policy['ips-sensor'] = 'default'
            if policy['webfilter-profile']:
                policy['webfilter-profile'] = 'default'

            # Then push
            if key not in exist_policies:
                result = push_config(policy, path)
        report(result, 'policies')
        result = []

        # Logout of vdom
        login_pri_vdom.Logout()
        login_sec_vdom.Logout()


if __name__ == '__main__':
    main()
