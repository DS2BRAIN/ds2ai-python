# Copyright 2020 The DS2AI Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

__version__ = "1.0.0"

import time
from .util import Util, Asynctask, User, MarketModel
from .LabelingAI import Labelproject, Labelfile
from .ClickAI import Project, Model, Jupyterproject
from .SkyhubAI import Opsproject
from .DS2dataset import Dataconnector
import requests as req
import json

class DS2():

    def __init__(self, apptoken):
        self.utilClass = Util()
        self.url = self.utilClass.url
        self.apptoken = apptoken
        self.user = self.get_user_info()
        self.user_token = self.user.token

    def get_user_info(self):
        return User(req.get(f"{self.url}/auth/", params={"apptoken": self.apptoken}).json())

    def create_project(self, data_file, predict_column_name=None, frame=None, training_method=None):

        dataconnector = self.create_dataconnector(data_file, predict_column_name=predict_column_name, frame=frame)
        return self.create_project_by_dataconnector(dataconnector, training_method)

    def create_project_by_dataconnector(self, dataconnector, training_method):

        if isinstance(dataconnector, int):
            dataconnector_id = dataconnector
        else:
            dataconnector_id = dataconnector.id

        return Project(req.post(f"{self.url}/projectfromdataconnectors/",
                                    params={"token": self.user_token},
                                    data=json.dumps({
                                          'dataconnectors': [dataconnector_id],
                                          'trainingMethod': training_method
                                          })).json(), self.user)

    def load_model(self, model_file):

        with open(model_file, "rb") as f:
            file_content = f.read()
            return Project(req.post(f"{self.url}/projectswithmodelfile/",
                                    params={"token": self.user_token}, files={'file': file_content},
                                    data={'filename': model_file.split("/")[-1] if "/" in model_file else model_file},
                                    stream=True).json(), self.user)

    def get_projects(self, count=25, start=1, desc=True):
        items = []
        items_raw = req.get(f"{self.url}/projects/",
                params={"token": self.user_token, "start": start, "page": count, "desc": desc}).json()['projects']
        for item_raw in items_raw:
            items.append(Project(item_raw, self.user))
        return items

    def get_project(self, project_id):
        return Project(req.get(f"{self.url}/projects/{project_id}/", params={"token": self.user_token}).json(), self.user)

    def get_model(self, model_id):
        return Model(req.get(f"{self.url}/models/{model_id}/", params={"token": self.user_token}).json(), self.user)

    def get_quick_models(self, count=25, start=1, desc=True):
        items = []
        items_raw = req.get(f"{self.url}/market-models/",
                    params={"token": self.user_token, "start": start, "page": count, "desc": desc, "is_quick_model":True}
                    ).json()['market_models']
        for item_raw in items_raw:
            items.append(MarketModel(item_raw, self.user))
        return items

    def get_quick_model_by_slug_name(self, slug_name):
        return MarketModel(req.get(f"{self.url}/marketmodels/slug/{slug_name}/",
                                   params={"token": self.user_token}).json(), self.user)

    def create_dataconnector(self, data_file, has_label_data=False, predict_column_name=None, frame=60):
        with open(data_file, "rb") as f:
            file_content = f.read()
            return Dataconnector(req.post(f"{self.url}/dataconnectorswithfile/",
                                    files={'file': file_content},
                                    data={'token': self.user_token,
                                          'filename': data_file.split("/")[-1] if "/" in data_file else data_file,
                                          'dataconnectorName': data_file.split("/")[-1] if "/" in data_file else data_file,
                                          'hasLabelData': has_label_data,
                                          'predictColumnName': predict_column_name,
                                          'frameValue': frame,
                                          }, stream=True).json(), self.user)

    def get_dataconnectors(self, count=25, start=1, desc=True):
        items = []
        items_raw = req.get(f"{self.url}/dataconnectors/",
                params={"token": self.user_token, "start": start, "page": count, "desc": desc}).json()['dataconnectors']
        for item_raw in items_raw:
            items.append(Dataconnector(item_raw, self.user))
        return items

    def get_dataconnector(self, dataconnector_id):
        return Dataconnector(req.get(f"{self.url}/dataconnectors/{dataconnector_id}/",
                                     params={"token": self.user_token}).json(), self.user)

    def create_labelproject(self, data_file=None, dataconnector=None, dataconnectors=None,
                            training_method=None, name=None, frame=60):

        if dataconnector:
            if isinstance(dataconnector, int):
                dataconnector = self.get_dataconnector(dataconnector)
            dataconnectors = [dataconnector.id]

            if not training_method:
                if dataconnector.dataconnectorName.endswith('.csv'):
                    training_method = "normal_regression"
                else:
                    training_method = "object_detection"

        if dataconnectors:

            if not name:
                name = f"Label Project from dataconnectors : {str(dataconnectors)}"

            return Labelproject(req.post(f"{self.url}/labelproject-from-dataconnectors/",
                                    params={"token": self.user_token},
                                    data=json.dumps({'dataconnectors': dataconnectors,
                                          'workapp': training_method,
                                          'name': name,
                                          'frame_value': frame,
                                          })).json(), self.user)

        elif data_file:
            if not name:
                name = f"Label Project from file : {str(data_file.split('/')[-1] if '/' in data_file else data_file)}"

            file_content = open(data_file, "r")
            return Labelproject(req.post(f"{self.url}/labelprojects/",
                                    params={"token": self.user_token},
                                    files={'files': file_content},
                                    data={
                                          'workapp': training_method,
                                          'frame_value': frame,
                                          'name': name,
                                          }, stream=True).json()['labelproject'], self.user)


        else:
            raise("You need to choose dataconnectors or files.")

    def get_labelprojects(self, count=25, start=1, desc=True):
        items = []
        items_raw = req.get(f"{self.url}/labelprojects/",
                params={"token": self.user_token, "start": start, "page": count, "desc": desc}).json()['projects']
        for item_raw in items_raw:
            items.append(Labelproject(item_raw, self.user))
        return items

    def get_labelproject(self, labelproject_id):
        return Labelproject(req.get(f"{self.url}/labelprojects/{labelproject_id}/",
                                     params={"token": self.user_token}).json(), self.user)

    def get_opsprojects(self, count=25, start=1, desc=True):
        items = []
        items_raw = req.get(f"{self.url}/opsprojects/",
                params={"token": self.user_token, "start": start, "page": count, "desc": desc}).json()['projects']
        for item_raw in items_raw:
            items.append(Opsproject(item_raw, self.user))
        return items

    def get_opsproject(self, opsproject_id):
        return Opsproject(req.get(f"{self.url}/opsprojects/{opsproject_id}/",
                                     params={"token": self.user_token}).json(), self.user)

    def get_jupyterprojects(self, count=25, start=1, desc=True):
        items = []
        items_raw = req.get(f"{self.url}/jupyterprojects/",
                params={"token": self.user_token, "start": start, "page": count, "desc": desc}).json()['projects']
        for item_raw in items_raw:
            items.append(Jupyterproject(item_raw, self.user))
        return items

    def get_jupyterproject(self, jupyterproject_id):
        return Jupyterproject(req.get(f"{self.url}/jupyterprojects/{jupyterproject_id}/",
                                     params={"token": self.user_token}).json(), self.user)

    def get_asynctasks(self, count=25, start=1, desc=True, tasktype="all"):
        items = []
        items_raw = req.get(f"{self.url}/asynctaskall/",
                params={"token": self.user_token, "start": start, "page": count, "desc": desc,
                        "tasktype": tasktype}).json()
        for item_raw in items_raw['asynctasks']:
            items.append(Asynctask(item_raw, self.user))
        return items

    def get_asynctask(self, asynctask_id):
        return Asynctask(req.get(f"{self.url}/asynctasks/{asynctask_id}/",
                                     params={"token": self.user_token}).json(), self.user)

    def start_auto_labeling(self, data_file, amount, has_label_data=False, predict_column_name=None, frame=60,
                          ai_type="general", autolabeling_type="box", general_ai_type="person",
                          model_id=None, custom_ai_stage=0, preprocessing_ai_type={}, labeling_class=[],
                          training_method="object_detection", name='', description=''
                          ):

        dataconnector = self.create_dataconnector(data_file, has_label_data=has_label_data, predict_column_name=predict_column_name)
        print("The data is being processed now. It will take a while. (Mostly less than 5 minutes.)")
        is_uploaded = False
        for i in range(100):
            time.sleep(5)
            dataconnector = self.get_dataconnector(dataconnector.id)
            if dataconnector.status == 100:
                is_uploaded = True
                break

        if not is_uploaded:
            raise ("The training data is being processed now. Please retry with ds2.train() when the data is ready. When it is ready, dataconnector.status will return 100.")

        if not name:
            name = f"label project from dataconnector {dataconnector.id}"

        return Asynctask(req.post(f"{self.url}/start-auto-labeling/",
                                params={"token": self.user_token},
                                data=json.dumps({
                                      'dataconnectors': [dataconnector.id],
                                      'predictColumnName': predict_column_name,
                                      'frameValue': frame,
                                      'workapp': training_method,
                                      'autolabeling_amount': amount,
                                      'autolabeling_ai_type': ai_type,
                                      'autolabeling_type': autolabeling_type,
                                      'general_ai_type': general_ai_type,
                                      'model_id': model_id,
                                      'custom_ai_stage': custom_ai_stage,
                                      'preprocessing_ai_type': preprocessing_ai_type,
                                      'labeling_class': labeling_class,
                                      'name': name,
                                      'description': description,
                                      })).json(), self.user)


    def train(self, data_file, training_method, value_for_predict, option="accuracy", frame=60):

        dataconnector = self.create_dataconnector(data_file, has_label_data=True, predict_column_name=value_for_predict)
        print("The data is being processed now. It will take a while. (Mostly less than 5 minutes.)")
        is_uploaded = False
        for i in range(100):
            time.sleep(5)
            dataconnector = self.get_dataconnector(dataconnector.id)
            if dataconnector.status == 100:
                is_uploaded = True
                break

        if not is_uploaded:
            raise ("The training data is being processed now. Please retry with ds2.train() when the data is ready. When it is ready, dataconnector.status will return 100.")

        return Project(req.post(f"{self.url}/train-from-data/",
                            params={"token": self.user_token},
                            data=json.dumps({
                                  'trainingMethod': training_method,
                                  'valueForPredict': value_for_predict,
                                  'dataconnector': dataconnector.id,
                                  'option': option,
                                  'frameValue': frame,
                                  })).json(), self.user)

    def deploy(self, model_file, name=None, cloud_type="AWS", region="us-west-1", server_type="g4dn.xlarge"):

        if "AWS" != cloud_type:
            raise("Currently we support only AWS cloud for this SDK.")

        if not name:
            name = f"Ops project {str(round(time.time() * 10000000))}"

        with open(model_file, "rb") as f:
            file_content = f.read()
            return Opsproject(req.post(f"{self.url}/deploy-model-file/",
                                params={"token": self.user_token},
                                files={'file': file_content},
                                data={'token': self.user_token,
                                      'filename': model_file.split("/")[-1] if "/" in model_file else model_file,
                                      'projectName': name,
                                      'serverType': server_type,
                                      'region': region,
                                      }, stream=True).json(), self.user)

    def get_magic_code(self, training_method, data_file, value_for_predict):

        dataconnector = self.create_dataconnector(data_file, has_label_data=True, predict_column_name=value_for_predict)
        print("The data is being processed now. It will take a while. (Mostly less than 5 minutes.)")
        is_uploaded = False
        for i in range(100):
            time.sleep(5)
            dataconnector = self.get_dataconnector(dataconnector.id)
            if dataconnector.status == 100:
                is_uploaded = True
                break

        if not is_uploaded:
            raise ("The training data is being processed now. Please retry with ds2.get_magic_code() when the data is ready. When it is ready, dataconnector.status will return 100.")

        return dataconnector.get_magic_code(training_method, value_for_predict)




    def rent_custom_training_server(self, cloud_type="AWS", region="us-west-1", server_type="g4dn.xlarge",
                                    name=None):
        if not name:
            name = f"Jupyter project {str(round(time.time() * 10000000))}"

        if "AWS" != cloud_type:
            raise("Currently we support only AWS cloud for this SDK.")

        return Jupyterproject(req.post(f"{self.url}/jupyterprojects/",
                         params={"token": self.user_token},
                         data=json.dumps({
                                          'projectName': name,
                                          'region': region,
                                          'serverType': server_type,
                                          })).json(), self.user)

    def predict(self, data, model_id=None, quick_model_name="", return_type="info"):

        if isinstance(data, Labelfile):
            data = data.download()

        if not model_id and not quick_model_name:
            raise("You need to choose model id or quick model name.")

        if model_id:
            model = self.get_model(model_id)

            if model.status != 100:
                raise("This model is not ready yet.")
        else:
            model = self.get_quick_model_by_slug_name(quick_model_name)

        return model.predict(data, return_type=return_type)

    def get_server_lists(self):
        return req.get(f"{self.url}/server-pricing/", params={"token": self.user_token}).json()

