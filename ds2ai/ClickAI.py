import time

from .DS2dataset import Dataconnector
from .SkyhubAI import Opsproject
from .util import Util
import requests as req
import json

class Project(object):

    def __init__(self, info, user):
        if not isinstance(info, dict):
            raise Exception(str(info))
        if info.get('error'):
            raise Exception(info['message_en'])
        self.url = Util().url
        self.__dict__.update(info)
        self.user = user
        self.user_token = self.user.token
        self.id = info['id']
        self.status = info['status']
        self.dataconnectorsList = info['dataconnectorsList']
        if isinstance(self.dataconnectorsList[0], int):
            main_dataconnector = self.get_dataconnector(self.dataconnectorsList[0])
        else:
            main_dataconnector = Dataconnector(self.dataconnectorsList[0], self.user)
        models = []
        for model in info.get("models", []):
            models.append(Model(model, user, project=self, main_dataconnector=main_dataconnector))
        self.models = models
        self.jupyter_servers = []
        for jupyter_server in info.get('jupyterServers', []):
            self.jupyter_servers.append(Jupyterserver(jupyter_server, user))

    def __repr__(self):
        return str(self.id)

    def get_dataconnector(self, dataconnector_id):
        return Dataconnector(req.get(f"{self.url}/dataconnectors/{dataconnector_id}/",
                                     params={"token": self.user_token}).json(), self.user)

    def refresh(self):
        return Project(req.get(f"{self.url}/projects/{self.id}/",
                                 params={"token": self.user_token}).json(), self.user)

    def delete(self):
        req.delete(f"{self.url}/projects/{self.id}/",params={"token": self.user_token})

    def train(self, training_method, value_for_predict, option="speed"):

        if self.status != 0:
            raise("The training is already started.")

        return Project(req.post(f"{self.url}/train/{self.id}/",
                            params={"token": self.user_token},
                            data=json.dumps({
                                'trainingMethod': training_method,
                                'valueForPredict': value_for_predict,
                                'option': option,
                            })).json(), self.user)

    def stop(self):

        if self.status == 0:
            raise("The training is not started.")

        return Project(req.put(f"{self.url}/projects/{self.id}/",params={"token": self.user_token},
                data=json.dumps({
                                 "status": 0,
                                 "statusText": "stopped",
                                 })).json(), self.user)

    def get_magic_code(self, training_method, value_for_predict, file_path="output.ipynb"):

        response = req.post(f"{self.url}/get-magic-code/",
                            params={"token": self.user_token},
                            data=json.dumps({
                                'project': self.id,
                                'trainingMethod': training_method,
                                'valueForPredict': value_for_predict,
                            }))

        if file_path:
            with open(file_path, 'w') as output:
                text = response.json()
                if isinstance(text, dict):
                    text = json.dumps(text)
                output.write(text)

        print(response.json())

class Model(object):
    utilClass = Util()

    def __init__(self, info, user, project=None, main_dataconnector=None):
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
        if info.get('trainingMethod'):
            self.app_url = f"https://ds2.ai/instant_use.html/?modeltoken={self.token}&modelid={self.id}"
        else:
            self.app_url = None

        if not project:
            self.project = self.get_project(info['project'])
        if not main_dataconnector:
            self.main_dataconnector = Dataconnector(self.project.dataconnectorsList[0], self.user)

    def __repr__(self):
        return str(self.id)

    def get_project(self, project_id):
        return Project(req.get(f"{self.url}/projects/{project_id}/", params={"token": self.user_token}).json(), self.user)

    def get_dataconnector(self, dataconnector_id):
        return Dataconnector(req.get(f"{self.url}/dataconnectors/{dataconnector_id}/",
                                     params={"token": self.user_token}).json(), self.user)

    def predict(self, data, return_type="info"):

        if self.status != 100:
            raise("This model is not ready yet.")

        request_data = {
            "apptoken": self.user.appTokenCode,
            "modelid": self.id,
            "modeltoken": self.token,
            "userId": self.user.id,
        }
        predict_url = {
            "predict": f"{self.url}/{self.user.id}/predict/",
            "predictimagebyurl": f"{self.url}/{self.user.id}/predictimagebyurl/",
            "predictimagebyurlinfo": f"{self.url}/{self.user.id}/predictimagebyurlinfo/",
            "predictall": f"{self.url}/{self.user.id}/predictall/",
            "predictimage": f"{self.url}/{self.user.id}/predictimage/",
            "predictimageinfo": f"{self.url}/{self.user.id}/predictimageinfo/",
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


    def delete(self):
        req.delete(f"{self.url}/models/{self.id}/",params={"token": self.user_token})

    def get_app_url(self):
        if self.app_url:
            return self.app_url
        else:
            print("Currently we don't support the app url for the loaded model.")

    def deploy(self, cloud_type="AWS", region="us-west-1", server_type="g4dn.xlarge", name=None):
        if not name:
            name = f"Ops project {str(round(time.time() * 10000000))}"

        if "AWS" != cloud_type:
            raise("Currently we support only AWS cloud for this SDK.")

        return Opsproject(req.post(f"{self.url}/opsprojects/",
                         params={"token": self.user_token},
                         data=json.dumps({
                                          'projectName': name,
                                          'region': region,
                                          'serverType': server_type,
                                          'modelId': self.id,
                                          })).json(), self.user)


class Jupyterproject(object):
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
        jupyterservers = []
        if info.get('jupyterServers'):
            for jupyterserver_raw in info['jupyterServers']:
                jupyterservers.append(Jupyterserver(jupyterserver_raw, user))
        self.jupyterservers = jupyterservers

    def __repr__(self):
        return str(self.id)
    serverType: str = None
    jupyterProjectId: int = None
    region: str = None

    def add_server(self, cloud_type="AWS", region="us-west-1", server_type="g4dn.xlarge"):

        if "AWS" != cloud_type:
            raise("Currently we support only AWS cloud for this SDK.")

        return Jupyterserver(req.post(f"{self.url}/jupyterservers/",
                 params={"token": self.user_token},
                 data=json.dumps({
                     'jupyterProjectId': self.id,
                     'serverType': server_type,
                     'region': region,
                 })).json(), self.user)

    def get_server_status(self):
        return req.get(f"{self.url}/jupyter-servers-status/",
                                 params={"token": self.user_token, "jupyterProjectId": self.id}).json()

    def get_jupyterservers(self):
        return self.jupyterservers

    def refresh(self):
        return Jupyterproject(req.get(f"{self.url}/jupyterprojects/{self.id}/",
                                 params={"token": self.user_token}).json(), self.user)

    def delete(self):
        req.delete(f"{self.url}/jupyterprojects/{self.id}/",params={"token": self.user_token})


class Jupyterserver(object):
    def __init__(self, info, user):
        if not isinstance(info, dict):
            raise Exception(str(info))
        if info.get('error'):
            raise Exception(info['message_en'])
        self.__dict__.update(info)
        self.instanceId = info['instanceId']
        self.url = Util().url
        self.user = user
        self.user_token = self.user.token

    def __repr__(self):
        return str(self.instanceId)

    def stop(self):
        print(f"{self.instanceId} is stopped.")
        req.post(f"{self.url}/jupyterservers/{self.instanceId}/stop/",
                 params={"token": self.user_token})
        return

    def resume(self):
        print(f"{self.instanceId} is resumed.")
        req.post(f"{self.url}/jupyterservers/{self.instanceId}/resume/",
                                 params={"token": self.user_token})
        return

    def delete(self):
        print(f"{self.instanceId} is deleted. It will take a time to turn off the server.")
        req.delete(f"{self.url}/jupyterservers/{self.instanceId}/",params={"token": self.user_token})
        return
