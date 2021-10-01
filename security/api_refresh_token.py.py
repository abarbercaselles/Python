from amazon_api.security.proxies import proxies

import time
import requests
import os


class AuthManager:

    def __init__(self):

        """
        Client initialization.
        :param client_id: Login with Amazon client Id that has been whitelisted
            for cpc_advertising:campaign_management
        :type client_id: string
        :param client_secret: Login with Amazon client secret key.
        :type client_id: string
        :param region: Region code for endpoint. See regions.py.
        :type region: string
        :param access_token: The access token for the advertiser account.
        :type access_token: string
        :param refresh_token: The refresh token for the advertiser account.
        :type refresh_token: string
        :param sandbox: Indicate whether you are operating in sandbox or prod.
        :type sandbox: boolean
        :param gcp: Indicate whether you are using GCP (requiring proxies) or working locally.
        :type gcp: boolean
        """

        self.token_url = 'api.amazon.com/auth/o2/token'
        self.gcp = False
        self.access_token_expiration = False
        self.session = requests.Session()

        self.initialized = 0
        self.client_id = None
        self.region = None
        self.client_secret = None
        self._access_token = None
        self.refresh_token = None

    def initialize(self, region):

        self.region = region
        self.client_id = os.environ.get(f"AMZ_{self.region.upper()}_CLIENT_ID")
        self.client_secret = os.environ.get(f"AMZ_{self.region.upper()}_CLIENT_SECRET")
        self.refresh_token = os.environ.get(f"AMZ_{self.region.upper()}_REFRESH_TOKEN")

        if self.client_id is None or self.refresh_token is None or self.client_secret is None:
            raise TypeError("Environment variables not found for the region provided")

        self.initialized = 1

    def last_update_token(self):

        """
        Check the expiration time for the access token
        :return True  - We need to refresh the access token
        :return False  - The access token is still valid
        """
        if self.access_token_expiration:
            elapsed_time = time.time() - self.access_token_expiration
            if elapsed_time > 3600:
                return True
            else:
                return False
        else:
            return True

    def do_refresh_token(self):

        """
        Use refresh token to get a new access token
        """

        self.access_token_expiration = time.time() + 3600
        if self.refresh_token is None:
            return {'success': False,
                    'code': 0,
                    'response': 'refresh_token is empty.'}

        params = {
            'grant_type': 'refresh_token',
            'refresh_token': self.refresh_token,
            'client_id': self.client_id,
            'client_secret': self.client_secret}

        url = 'https://{}'.format(self.token_url)

        try:
            if self.gcp:
                response = requests.post(url, data=params, proxies=proxies)
            else:
                response = requests.post(url, data=params)

            if 'access_token' in response.text:
                self._access_token = response.json()['access_token']

                return {'success': True,
                        'code': response,
                        'response': self._access_token}
            else:
                return {'success': False,
                        'code': response,
                        'response': 'access_token not in response.'}
        except requests.HTTPError as e:
            return {'success': False,
                    'code': e.response,
                    'response': e}

    def create_auth_session(self,region,profile_id=None) -> requests.Session():

        """
        Starts access token management proccess. Access token will be constantly refreshed with timeout delay
        :return the session with updated headers
        """
        if self.initialized == 0:
            self.initialize(region)

        if self.region != region:
            self.access_token_expiration = False
            self.initialize(region)

        api_expire = self.last_update_token()
        if api_expire:
            self.do_refresh_token()
        if self._access_token is None:
            raise Exception('Access token is empty')

        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + self._access_token,
            'Amazon-Advertising-API-ClientId': self.client_id,
        }

        if profile_id is not None and profile_id != '':
            headers['Amazon-Advertising-API-Scope'] = profile_id
        else:
            headers['Amazon-Advertising-API-Scope'] = None
        self.session.headers.update(headers)

        return self.session

