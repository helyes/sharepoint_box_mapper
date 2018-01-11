"""
 Encapsulates sharepoint api operations
"""
import json, requests
#from pprint import pprint
from sharepoint_file import SharepointFile


class SharepointClient:
    """Encapsulates sharepoint api operations. \n
    Get onedrive id:
    https://graph.microsoft.com/v1.0/sites/mycompany.sharepoint.com:/Main Division\n
    returns { ... "id": "mycompany.sharepoint.com,12345678-1234-1234-9209-22dc5b96bb68,12345678-1234-4e92-b050-ae3da0e4a980", ... }
    then call \n
    https://graph.microsoft.com/v1.0/sites/mycompany.sharepoint.com,12345678-1234-1234-9209-22dc5b96bb68,12345678-1234-4e92-b050-ae3da0e4a980/drive \n
    returns { ...  "id": "b!piwuefhoaiwuefhpaciwu3eaeuhfaiwuehfaa-1323456", ...} \n\n

    """
    
    ONEDRIVE_ID = None
    GRAPH_BASE_URL = 'https://graph.microsoft.com/v1.0'
    sharepoint_token = None
    sharepoint_client_secret = None
    sharepoint_client_id = None
    sharepoint_scope = 'https://graph.microsoft.com/.default'
    azure_tenant_id = None

    def __init__(self, client_id, client_secret, onedrive_id, azure_tenant_id):
        print('Initializing sp client... Client id:', client_id + ", Client secret:", client_secret + ", Onedrive:", onedrive_id + ", Azure tenant id:", azure_tenant_id)
        self.sharepoint_client_id = client_id
        self.sharepoint_client_secret = client_secret
        self.ONEDRIVE_ID = onedrive_id
        self.azure_tenant_id = azure_tenant_id
        self.sharepoint_token = self.request_token()
        
        
    def request_token(self):
        """
        Returns a token to be used in subseqent calls
        """
        url = "https://login.microsoftonline.com/" + self.azure_tenant_id + "/oauth2/v2.0/token"
        headers = {'content-type': 'application/x-www-form-urlencoded'}
        payload = {'grant_type': 'client_credentials',
                   'client_id': self.sharepoint_client_id,
                   'client_secret': self.sharepoint_client_secret,
                   'scope': self.sharepoint_scope
                  }

        response_raw = requests.post(url, headers=headers, data=payload)
        #print(response_raw.text)
        response = json.loads(response_raw.text)
        #pprint(response)
        token = response['access_token']
        print('Sharepoint tkn:\t', token[:10], '...', token[-10:])
        return token

    def get_file_metadata(self, path):
        """Returns onedrive file metadata based on given path"""
        url = self.GRAPH_BASE_URL +  "/drives/" + self.ONEDRIVE_ID + "/root:/" + path
        headers = {'authorization': 'Bearer ' + self.sharepoint_token}
        response_raw = requests.request("GET", url, headers=headers)
        response = json.loads(response_raw.text)
        #print(response_raw.text)
        if 'error' in response.keys():
            raise ValueError(response['error']['message'] + ': ' +path)
        #print("Share url:", response['@microsoft.graph.downloadUrl'])
        return response

    def get_sharepoint_file(self, path):
        """Returns onedrive file metadata based on given path"""
        metadata = self.get_file_metadata(path)
        metadata['path'] = path
        ret = SharepointFile(metadata)
        return ret

    def get_shared_url_secure(self, f: SharepointFile):
        print('Getting shared url...')
        url = self.GRAPH_BASE_URL + "/drives/" + self.ONEDRIVE_ID + "/root:/" + f.get_full_path()
        headers = {'authorization': 'Bearer ' + self.sharepoint_token}
        response_raw = requests.request("GET", url, headers=headers)
        response = json.loads(response_raw.text)
        print(response_raw.text)
        #print("Secure share url:", response['@microsoft.graph.downloadUrl'])
        return response['@microsoft.graph.downloadUrl']

    def get_shared_url_public(self, f: SharepointFile):
        url = self.GRAPH_BASE_URL +  "/drives/" + self.ONEDRIVE_ID + "/items/" + f.file_id + "/createLink"
        payload = '{"type": "view","scope": "anonymous"}'
        headers = {
            'content-type': 'application/json',
            'authorization': 'Bearer ' +  self.sharepoint_token
        }
        response_raw = requests.request("POST", url, data=payload, headers=headers)
        #print(response_raw.text)
        response = json.loads(response_raw.text)
        return response['link']['webUrl']
