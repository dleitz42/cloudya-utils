#!/usr/bin/env python3
'''This file contains classes and methods to automate the web-api for Cloudya (by NFON)'''

import logging
import json
import requests

# Setup Logger
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s %(levelname)s %(message)s"
logging.basicConfig(format=LOG_FORMAT)
logger = logging.getLogger(__name__)
logger.setLevel(logging.getLevelName(LOG_LEVEL))


class Cloudya():
    '''Cloudy web-api automate class

    Args:
        auth_user: cloudya login user
        auth_pass: cloudya login password

    Return:
        nothing
    '''

    # Base Cloudya Urls
    CLOUDYA_URL = 'https://start.cloudya.com'
    CLOUDYA_URL_LOGIN = f'{CLOUDYA_URL}/api/user/login'
    CLOUDYA_URL_LOGOUT = f'{CLOUDYA_URL}/api/user/logout'
    CLOUDYA_URL_CFP = f'{CLOUDYA_URL}/api/callforwards/profiles'
    CLOUDYA_URL_PN = f'{CLOUDYA_URL}/api/phonenumber'

    def __init__(self, auth_user=None, auth_pass=None):
        self._auth_user = auth_user
        self._auth_pass = auth_pass
        self.session = self.CloudyaSession()

    def setup_cfp(self, cfp_alias, cfp_number, cfp_phonenumber):
        '''Setup a new or update an exising callforwards profile and activate it

        Args:
            cfp_alias: profile alias name
            cfp_number: profile number [1-9]
            cfp_phonenumber: phonenumber to redirect

        Return:
            nothing
        '''
        logger.debug('Updating CallforwardsProfile Alias: %s, Number %s, PhoneNumber %s',
            cfp_alias, cfp_number, cfp_phonenumber)
        self.login()
        cfp = self.CloudyaCallforwardsProfiles(self)
        cfp.log_active_profiles()
        if cfp.profile_number_exists(cfp_number):
            if cfp.is_active_profile(cfp_number):
                cfp.activate_default_profile()
                cfp.log_active_profiles()
            cfp.delete_profile_by_number(cfp_number)
        cfp.create_and_activate_cfp(number=cfp_number,
            alias=cfp_alias,
            phonenumber=cfp_phonenumber)
        cfp.log_active_profiles()
        self.logout()

    def login(self):
        """Method to login into Cloudya account

        Args:
            Nothing

        Return:
            Nothing
        """
        url = self.CLOUDYA_URL_LOGIN
        payload = json.dumps({"username": self._auth_user,
            "password": self._auth_pass,
            "rememberMe": False,
            "captchaResponse": None,
            "captchaType": "FriendlyCaptcha"})
        logger.debug('Sending request url %s, method POST, headers %s, payload %s', url,
            self.session.get_headers(), payload)
        req = requests.post(url=url, headers=self.session.get_headers(), data=payload)
        if req.status_code == 200:
            logger.info('Login successful')
        else:
            raise Exception('Unable to login')
        json_data = req.json()
        logger.debug('fetched json data: %s', json_data)
        token=json_data["access_token"]
        self.session.set_token(token)
        logger.debug('login token set: %s', token)

    def logout(self):
        """Method to logout from Cloudya account

        Args:
            Nothing

        Return:
            Nothing
        """
        url = self.CLOUDYA_URL_LOGOUT
        logger.debug('Sending request url %s, method POST, headers %s', url,
            self.session.get_headers())
        req = requests.post(url=url, headers=self.session.get_headers())
        if req.status_code == 204:
            logger.info('Logout successful')
        else:
            raise Exception('Unable to logout')
        self.session.remove_token()
        logger.debug('login token removed')


    class CloudyaCallforwardsProfiles():
        '''Cloudy Callforwards Profiles automate class

        Args:
            cloudya object

        Return:
            nothing
        '''

        def __init__(self, parent):
            self._parent = parent
            self._profiles = None
            self._profile_default_id = None
            self._profile_active_number = None
            self._profile_active_name = None
            self._profile_active_pn = None
            self.get_profiles()

        def get_profiles(self):
            """Method to get the current Callforwards Profiles from Cloudya account

            Args:
                Nothing

            Return:
                Nothing
            """
            url = self._parent.CLOUDYA_URL_CFP
            logger.debug('Sending request url %s, method GET, headers %s', url,
                self._parent.session.get_headers())
            req = requests.get(url=url, headers=self._parent.session.get_headers())
            if req.status_code == 200:
                logger.info('Callforwards profile list analysed')
            else:
                raise Exception('Unable to analysed callforwards profile')
            json_data = req.json()
            logger.debug('fetched json data: %s', json_data)
            self._profiles = json_data

            for profile in self._profiles:
                if profile['number'] == 0:
                    self._profile_default_id=profile['id']
                if profile['active']:
                    self._profile_active_number=profile['number']
                    self._profile_active_name=profile['name']
                    phn=profile['rules'][0]['unconditionalDestination']['phoneNumberFormatDisplay']
                    self._profile_active_pn=phn

        def log_active_profiles(self):
            """Method to write information about the current active
               Callforwards Profile into logger.

            Args:
                Nothing

            Return:
                Nothing
            """
            logger.info('Currently Active: Profile #%s, Name "%s", Phone "%s"',
                self._profile_active_number,
                self._profile_active_name,
                self._profile_active_pn)

        def is_active_profile(self, number):
            """Method to check if a given profile number is active or not.

            Args:
                number: profile number to check

            Return:
                Boolean: is give profile number active
            """
            return bool(number == self._profile_active_number)

        def profile_number_exists(self, number):
            """Method to check if a given profile number exists.

            Args:
                number: profile number to check

            Return:
                Boolean: exists the give profile
            """
            boolean_out=False
            for profile in self._profiles:
                if profile["number"]==number:
                    boolean_out=True
            return boolean_out

        def activate_default_profile(self):
            """Method activate the default profile.

            Args:
                Nothing

            Return:
                Nothing
            """
            self.activate_profile (profile_id=self._profile_default_id)

        def activate_profile(self, profile_id):
            """Method activate a given profile and re-get profile list.

            Args:
                profile_id: profile to active

            Return:
                Nothing
            """
            url = f'{self._parent.CLOUDYA_URL_CFP}/{profile_id}/activate'
            logger.debug('fetching url %s, method PUT, headers %s',
                url, self._parent.session.get_headers())
            req = requests.put(url=url,
                headers=self._parent.session.get_headers())
            if req.status_code == 200:
                logger.info('Callforwards profile %s activated', profile_id)
            else:
                raise Exception('Unable to activate callforwards profile')
            self.get_profiles()

        def get_profile_by_number(self, number):
            """Method to fetch a profile_id by a given profile number.

            Args:
                number: profile number

            Return:
                profile_id
            """
            out = None
            for profile in self._profiles:
                if profile["number"]==number:
                    out = profile["id"]
            if not out:
                raise Exception('Profile at number not found')
            return out

        def delete_profile_by_number(self, number):
            """Method to delete a profile by a given profile number.

            Args:
                number: profile number

            Return:
                Nothing
            """
            profile_id = self.get_profile_by_number(number)
            self.delete_profile(profile_id)

        def delete_profile(self, profile_id):
            """Method to delete a profile by a given profile_id.

            Args:
                profile_id: profile_id of profile to delete

            Return:
                Nothing
            """
            url = f'{self._parent.CLOUDYA_URL_CFP}/{profile_id}'
            logger.debug('fetching url %s, method DELETE, headers %s', url,
                self._parent.session.get_headers())
            req = requests.delete(url=url,
                headers=self._parent.session.get_headers())
            if req.status_code == 204:
                logger.info('Callforwards profile removed')
            else:
                raise Exception('Unable to remove callforwards profile')

        def create_and_activate_cfp(self, number, alias, phonenumber):
            """Method to create and activate a new callforwards profile.

            Args:
                number: profile number
                alias: profile name
                phonenumber: phonenumber for callforwards

            Return:
                profile_id of the new created profile
            """
            cfp_id = self.create_cfp(number, alias, phonenumber)
            self.activate_profile(cfp_id)

        def create_cfp(self, number, alias, phonenumber):
            """Method to create new callforwards profile.

            Args:
                number: profile number
                alias: profile name
                phonenumber: phonenumber for callforwards

            Return:
                Nothing
            """
            payload = json.dumps({"id":None,
                "name": alias,
                "number": number,
                "active": False,
                "immutable": False,
                "color_index": 2,
                "rules":[]})
            url = self._parent.CLOUDYA_URL_CFP
            logger.debug('fetching url %s, method POST, headers %s', url,
                self._parent.session.get_headers())
            req = requests.post(url=url, data=payload,
                headers=self._parent.session.get_headers())
            if req.status_code == 201:
                logger.info('Callforwards profile added')
            else:
                raise Exception('Unable to add callforwards profile')
            json_data_profile = req.json()
            logger.debug('fetched json data: %s', json_data_profile)

            new_profile_id=json_data_profile['id']
            new_profile_rule_id=json_data_profile['rules'][0]['id']

            pn_id = self.add_phonenumber(phonenumber)
            self.link_phonenumber_to_profile(phonenumber_id=pn_id,
                profile_id=new_profile_id,
                profile_rule_id=new_profile_rule_id)

            return new_profile_id

        def add_phonenumber(self, phonenumber):
            """Method to add a phonenumber

            Args:
                phonenumber: phonenumber to add

            Return:
                afd_id: id to use for relationship between phonenumber and cfp
            """
            payload = json.dumps({'phonenumber': phonenumber})
            url = self._parent.CLOUDYA_URL_PN
            logger.debug('fetching url %s, method POST, headers %s', url,
                self._parent.session.get_headers())
            req = requests.post(url=url, data=payload,
                headers=self._parent.session.get_headers())
            if req.status_code == 201:
                logger.info('Phonenumber created')
            else:
                raise Exception('Unable to add phonenumber')
            json_data = req.json()
            logger.debug('fetched json data: %s', json_data)
            afd_id = json_data['afd_id']
            return afd_id

        def link_phonenumber_to_profile(self, phonenumber_id, profile_id, profile_rule_id):
            """Method to enable to callforwarding function in a profile

            Args:
                phonenumber_id: phonenumber id (afd_id)
                profile_id: profile id
                profile_rule_id: profile rule id

            Return:
                Nothing
            """
            payload = json.dumps({'id': f'{profile_rule_id}',
                'source': 0,
                'profileId': f'{profile_id}',
                'unconditionalDestinationId': phonenumber_id,
                'unconditionalDestinationActive': True,
                'busyDestinationActive': True,
                'notRegisteredDestinationActive': True,
                'noAnswerDestinationActive': True,
                'noAnswerTimeout': 15})
            url = f'{self._parent.CLOUDYA_URL_CFP}/{profile_id}/rules/{profile_rule_id}'
            logger.debug('fetching url %s, method PUT, headers %s, payload %s',
                url, self._parent.session.get_headers(), payload)
            req = requests.put(url=url, data=payload, headers=self._parent.session.get_headers())
            if req.status_code == 200:
                logger.info('Phonenumber added to cfp')
            else:
                raise Exception('Unable to add phonenumber to cfp')

    class CloudyaSession():
        """Cloudya Session Class to handle the login state

        Args:
            access_token: access token to use for bearer token

        Return:
            Nothing
        """

        _DEFAULT_HEADERS = {"Accept": "application/json",
            "Content-Type": "application/json"}

        def __init__(self, access_token=None):
            self._token = access_token

        def get_headers(self):
            """Method to get a set of header for requests parameter
               when token is given the Bearer Authorization will added

            Args:
                Nothing

            Return:
                Headers
            """
            headers = self._DEFAULT_HEADERS
            if self._token:
                headers["Authorization"] = "Bearer " + self._token
            return headers

        def set_token(self, accesstoken):
            """Method to set the accesstoken

            Args:
                accesstoken: token for auth

            Return:
                Nothing
            """
            self._token = accesstoken

        def remove_token(self):
            """Method to remove the token

            Args:
                Nothing

            Return:
                Nothing
            """
            self._token = None
