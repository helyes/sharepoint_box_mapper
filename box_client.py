"""
 Encapsulates box api operations
"""
from pprint import pprint
import re, json, requests
from boxsdk import OAuth2, Client

class BoxClient:
    """Box client encapsulating box API operations. \n

    """

    BOX_TOKEN = None
    DEBUG = False
    client = None

    def __init__(self, token, debug):
        print('Initializing box client... Token:', token)
        self.BOX_TOKEN = token
        self.DEBUG = debug
        self.auth()

    def auth(self):
        """
        Creates api client object using the given developer token
        """
        # try:
        self.client = Client(OAuth2(None, None, access_token=self.BOX_TOKEN))
        # except:
        #     print('Could not create client')

    def get_shared_item(self, shared_url):
        """
        Returns shared item object based on the given shared url
        """
        # id_share_pattern = re.compile("https:\/\/app\.box\.com\/shared\/(.*?)\/(\d)\/(\d+)\/(\d+)\/(\d)")
        # if id_share_pattern.match(shared_url):
        #     title_search = re.search('<title>(.*)</title>', html, re.IGNORECASE)
        #     if title_search:
        #         title = title_search.group(1)
        #     print('Match:', shared_url)

        ret = self.client.get_shared_item(shared_url)

        if self.DEBUG:
            pprint(vars(ret))
        #print('ret:', ret)
        return ret

    def get_shared_item_ori(self, shared_url):
        """
        Returns shared item object based on the given shared url
        """
        ret = self.client.get_shared_item(shared_url)
        if self.DEBUG:
            pprint(vars(ret))
        print('ret:', ret)
        return ret

    def get_shared_item_by_id(self, item_id):
        """
        Returns a box item by it's id
        """
        #  curl https://api.box.com/2.0/files/123762924238 -H "Authorization: Bearer dlajvOKCxSoSldqmLo3KezGv4oPloC7i"
        url = "https://api.box.com/2.0/files/" + str(item_id)
        headers = {'Authorization': 'Bearer ' + self.BOX_TOKEN}
        
        response_raw = requests.get(url, headers=headers)
        #print(response_raw.text)
        response = json.loads(response_raw.text)
        pprint(response)        
        return response

    def sanitize_shared_url(self, shared_url):
        """
        Converts /shared/static url-s to /s urls. Box API can not
         get metadata for /shared/static url-s\n
        Example:\n
        https://app.box.com/shared/static/12345678901234567890123456789012345 \n
        turns into\n
        https://app.box.com/s/12345678901234567890123456789012345
        """
        if self.DEBUG:
            print('\nSanitizing', shared_url, '-> ', end='')

        if shared_url is None:
            return ''

        result = re.sub(r"(.*app\.box\.com\/)(shared\/static)(\/.*)", r"\1s\3", shared_url)

        if self.DEBUG:
            print(result)
        return result


    def get_user(self, userid):
        """
        Returns a user object thus later operations can be executed on behalf of this user
        """
        tsduser = self.client.user(user_id=str(userid)).get()
        print('user_login: ' + tsduser['login'])
