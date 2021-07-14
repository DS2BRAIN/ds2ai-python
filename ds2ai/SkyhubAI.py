from .DS2dataset import Dataconnector
from .util import Util
import requests as req
import json

class Opsproject(object):
    utilClass = Util()

    def __init__(self, info, user):
        if not isinstance(info, dict):
            raise Exception(str(info))
        if info.get('error'):
            raise Exception(info['message_en'])
        self.__dict__.update(info)
        self.id = info['id']
        self.url = self.utilClass.url
        if info.get('model'):
            self.opsModel = Opsmodel(info['model'], user)
            self.token = self.opsModel.token
            if info.get('trainingMethod'):
                self.app_url = f"https://ds2.ai/service_app.html/?modeltoken={self.token}&modelid={self.id}"
            else:
                self.app_url = None
        self.ops_server_groups = []
        if info.get('opsServerGroupsInfo'):
            for ops_server_group in info.get('opsServerGroupsInfo', []):
                self.ops_server_groups.append(Opsservergroup(ops_server_group, user))
        self.user = user
        self.status = info['status']
        self.dataconnectorsList = info['dataconnectorsList']
        self.user_token = self.user.token
        if isinstance(self.dataconnectorsList[0], int):
            self.main_dataconnector = self.get_dataconnector(self.dataconnectorsList[0])
        else:
            self.main_dataconnector = Dataconnector(self.dataconnectorsList[0], self.user)

    def __repr__(self):
        return str(self.id)

    def get_app_url(self):
        if self.app_url:
            return self.app_url
        else:
            print("Currently we don't support the app url for the loaded model.")

    def delete(self):
        return req.delete(f"{self.url}/opsprojects/{self.id}/",params={"token": self.user_token})

    def get_server_status(self):
        return req.get(f"{self.url}/ops-servers-status/",
                                 params={"token": self.user_token, "opsProjectId": self.id}).json()

    def refresh(self):
        return Opsproject(req.get(f"{self.url}/opsprojects/{self.id}/",
                                 params={"token": self.user_token}).json(), self.user)

    def predict(self, data, return_type="info"):

        if self.status != 100:
            raise("This model is not ready yet.")

        request_data = {
            "apptoken": self.user.appTokenCode,
            "modelid": self.model['id'],
            "modeltoken": self.token,
            "userId": self.user.id,
        }
        predict_url = {
            "predict": f"{self.url}/inference/inferenceops{self.id}/",
            "predictimagebyurl": f"{self.url}/inferenceimagebyurl/inferenceops{self.id}/",
            "predictimagebyurlxai": f"{self.url}/inferenceimagebyurlxai/inferenceops{self.id}/",
            "predictimagebyurlinfo": f"{self.url}/inferenceimagebyurlinfo/inferenceops{self.id}/",
            "predictall": f"{self.url}/inferenceall/inferenceops{self.id}/",
            "predictimage": f"{self.url}/inferenceimage/inferenceops{self.id}/",
            "predictimagexai": f"{self.url}/inferenceimagexai/inferenceops{self.id}/",
            "predictimageinfo": f"{self.url}/inferenceimageinfo/inferenceops{self.id}/",
        }

        if type(data) == dict:
            data_processed = {}
            for key, item in data.items():
                if f"__{self.main_dataconnector.dataconnectorName}" not in key:
                    data_processed[f"{key}__{self.main_dataconnector.dataconnectorName}"] = item
                else:
                    data_processed[key] = item
            data = data_processed

        return self.utilClass.predict(request_data, predict_url, data, return_type=return_type)

    def get_dataconnector(self, dataconnector_id):
        return Dataconnector(req.get(f"{self.url}/dataconnectors/{dataconnector_id}/",
                                     params={"token": self.user_token}).json(), self.user)

class Opsmodel(object):
    utilClass = Util()

    def __init__(self, info, user):
        if not isinstance(info, dict):
            raise Exception(str(info))
        if info.get('error'):
            raise Exception(info['message_en'])
        self.__dict__.update(info)
        self.id = info['id']
        self.token = info['token']
        self.url = self.utilClass.url
        self.user = user
        self.user_token = self.user.token

    def __repr__(self):
        return str(self.id)

class Opsservergroup(object):
    def __init__(self, info, user):
        if not isinstance(info, dict):
            raise Exception(str(info))
        if info.get('error'):
            raise Exception(info['message_en'])
        self.__dict__.update(info)
        self.id = info['id']
        self.url = Util().url
        self.user = user
        self.user_token = self.user.token

    def __repr__(self):
        return str(self.id)

    def edit_autoscaling(self, min_server_size=None, max_server_size=None, start_server_size=None):
        data = {}
        if min_server_size:
            data['minServerSize'] = min_server_size
        if max_server_size:
            data['maxServerSize'] = max_server_size
        if start_server_size:
            data['startServerSize'] = start_server_size

        return req.put(f"{self.url}/opsservergroups/{self.id}/",
                        params={"token": self.user_token},
                        data = json.dumps(data)
                       ).json()

    def stop(self):
        return req.put(f"{self.url}/opsservergroups/{self.id}/",
                       params={"token": self.user_token},
                       data=json.dumps({
                           'minServerSize': 0,
                           'maxServerSize': 0,
                           'startServerSize': 0,
                       })
                       ).json()

    def resume(self):
        return req.put(f"{self.url}/opsservergroups/{self.id}/",
                       params={"token": self.user_token},
                       data=json.dumps({
                           'minServerSize': 1,
                           'maxServerSize': 1,
                           'startServerSize': 1,
                       })
                       ).json()

    def delete(self):
        return req.delete(f"{self.url}/opsservergroups/{self.id}/",params={"token": self.user_token})
