from pandas import json_normalize
from amazon_api.api_regions import regions

from amazon_api.security.auth_manager import AuthManager
auth = AuthManager()


class ApiUtils:

    def get(self, url,region, profile_id=None, params=None):
        session = auth.create_auth_session(region, profile_id)
        session.params = params
        response = session.get(url)
        self.validate_response(response)
        session.params = None
        return response.json()

    def post(self, url,region, profile_id, params=None):
        session = auth.create_auth_session(region,profile_id)
        if params is not None:
            response = session.post(url, json=params)
        else:
            response = session.post(url)
        self.validate_response(response)
        return response.json()

    def put(self,url,region,profile_id, params=None):
        session = auth.create_auth_session(region,profile_id)
        if params is not None:
            response = session.put(url, json=params)
        else:
            response = session.put(url)
        self.validate_response(response)
        return response.json()

    def delete(self, url,region, profile_id):
        session = auth.create_auth_session(region,profile_id)
        response = session.delete(url)
        return response.json()

    def get_df_from_response(self, response):
        # print(response)
        return json_normalize(response)

    def validate_response(self, response):
        if str(response.status_code).startswith("2") is False:
            raise Exception(str(response.text))

    def check(self,region):
        if region.lower() in regions:
            pass
        else:
            raise KeyError(f"Region '{region}' not found in the list of available regions.")