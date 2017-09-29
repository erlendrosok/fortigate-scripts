#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Code taken from: https://github.com/DavidChayla/FortigateApi
"""

import requests
import json
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class Fortigate:

    def __init__(self, ip, vdom, user, passwd):
        ipaddr = 'https://' + ip

        # URL definition
        self.login_url = ipaddr + '/logincheck'
        self.logout_url = ipaddr + '/logout'
        self.api_url = ipaddr + '/api/v2/'
        self.vdom = vdom

        # Start session to keep cookies
        self.s = requests.Session()

        # Login
        payload = {'username': user, 'secretkey': passwd}
        self.r = self.s.post(self.login_url, data=payload, verify=False)

        for cookie in self.s.cookies:
            if cookie.name == 'ccsrftoken':
                csrftoken = cookie.value[1:-1]
                self.s.headers.update({'X-CSRFTOKEN': csrftoken})

    def Logout(self):
        req = self.s.get(self.logout_url)
        return req.status_code

    def ApiGet(self, url):
        req = self.s.get(self.api_url + url, params={'vdom': self.vdom})
        return req

    def ApiAdd(self, url, data=None):
        req = self.s.post(self.api_url + url,
                          params={'vdom': self.vdom},
                          data=repr(data))
        return req.status_code

    def GetVdom(self, name=''):
        '''
        Return the json vdom object, when the
        param name is defined it returns
        the selected object
        without name: return all the objects.
        Parameters
        ----------
        name: the vdom object name (type string)

        Returns
        -------
        Return the json object
        '''
        req = self.ApiGet('cmdb/system/vdom/' + name)
        return req.text

    def GetPolicies(self):
        """
        Parameters
        ----------
        vdom: the vdom you want to fetch from

        Returns
        -------
        The IPv4 policies of a vdom
        """
        req = self.ApiGet('cmdb/firewall/policy')
        data = json.loads(req.text)
        return data['results']

    def GetAddress(self):
        """
        Parameters
        ----------
        vdom: the vdom you want to fetch from

        Returns
        -------
        The Address Objects of a vdom
        """
        req = self.ApiGet('cmdb/firewall/address')
        data = json.loads(req.text, encoding='utf-8')
        return data['results']

    def GetAddressGroup(self):
        """
        Parameters
        ----------
        vdom: the vdom you want to fetch from

        Returns
        -------
        The Address Group Objects of a vdom
        """
        req = self.ApiGet('cmdb/firewall/addrgrp')
        data = json.loads(req.text, encoding='utf-8')
        return data['results']

    def GetServices(self):
        """
        Parameters
        ----------
        vdom: the vdom you want to fetch from

        Returns
        -------
        The IPv4 Service Objects of a vdom
        """
        req = self.ApiGet('cmdb/firewall.service/custom')
        data = json.loads(req.text, encoding='utf-8')
        return data['results']

    def GetServiceGroup(self):
        """
        Parameters
        ----------
        vdom: the vdom you want to fetch from

        Returns
        -------
        The IPv4 Service Group Objects of a vdom
        """
        req = self.ApiGet('cmdb/firewall.service/group')
        data = json.loads(req.text, encoding='utf-8')
        return data['results']

    def GetInterface(self, name=''):
        """
        Return the json interface object,
        when the param id is defined it returns the
        selected object, without id: return all the objects

        Parameters
        ----------
        name: the object name or nothing (type string)

        Returns
        -------
        Return the json fw interface object
        """
        req = self.ApiGet('cmdb/system/interface/' + name)
        result = []
        data = json.loads(req.text)

        # search for current vdom only
        for y in range(0, len(data['results'])):
            if self.vdom == data['results'][y]['vdom']:
                result.append(data['results'][y])
        return result

    def GetZones(self, name=''):
        """
        Return the json zone object,
        when the param id is defined it returns the
        selected object, without id: return all the objects

        Parameters
        ----------
        name: the object name or nothing (type string)

        Returns
        -------
        Return the json fw interface object
        """
        req = self.ApiGet('cmdb/system/zone/' + name)
        result = []
        data = json.loads(req.text)

        # search for current vdom only
        for y in range(0, len(data['results'])):
            if self.vdom == data['vdom']:
                result.append(data['results'][y])
        return result

    def GetRouterStatic(self, name=''):
        """
        Return the json static routes objects

        Parameters
        ----------
        name: the object name or nothing (type string)

        Returns
        -------
        Return the json fw interface object
        """
        req = self.ApiGet('cmdb/router/static/')
        data = json.loads(req.text)
        return data['results']

    def GetRouterPolicy(self, name=''):
        """
        Return the json policy routes objects

        Parameters
        ----------
        name: the object name or nothing (type string)

        Returns
        -------
        Return the json fw interface object
        """
        req = self.ApiGet('cmdb/router/policy/')
        data = json.loads(req.text)
        return data['results']
