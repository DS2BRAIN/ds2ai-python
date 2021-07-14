from .util import Util, Asynctask, Instance
import requests as req
import json


class Labelproject(object):
    def __init__(self, info, user):
        if not isinstance(info, dict):
            raise Exception(str(info))
        if info.get('error'):
            raise Exception(info['message_en'])
        self.__dict__.update(info)
        self.id = info['id']
        self.workapp = info['workapp']
        self.url = Util().url
        self.user = user
        self.user_token = self.user.token
        labelclasses = []
        if info.get("labelclasses"):
            for labelclass_raw in info.get("labelclasses"):
                labelclasses.append(Labelclass(labelclass_raw, user))
        self.labelclasses = labelclasses

    def __repr__(self):
        return str(self.id)

    def delete(self):
        req.delete(f"{self.url}/labelprojects/{self.id}/",params={"token": self.user_token})

    def get_labels(self):
        labels_raw = req.get(f"{self.url}/labels-by-labelproject/{self.id}/", params={"token": self.user_token}).json()
        labels = []
        for label_raw in labels_raw:
            labels.append(Label(label_raw, self.user))

        return labels

    def get_labelclasses(self):
        return self.labelclasses

    def get_labelfiles(self, sorting="created_at", tab="all", count=10, desc=False, searching="", workAssignee=None):
        labelfiles_raw = req.get(f"{self.url}/listobjects/", params={
                                                                    "token": self.user_token,
                                                                    "labelprojectId": self.id,
                                                                    "sorting": sorting,
                                                                    "tab": tab,
                                                                    "count": count,
                                                                    "desc": desc,
                                                                    "searching": searching,
                                                                    "workAssignee": workAssignee,
                                                                     }).json()
        labelfiles = []
        for label_raw in labelfiles_raw.get('file',[]):
            labelfiles.append(Labelfile(label_raw, self.user, self.labelclasses))

        return labelfiles

    def create_labelclass(self, name, color="#000000"):
        for labelclass in self.labelclasses:
            if name == labelclass.name:
                raise("You can not create same label class name.")

        return Labelclass(req.post(f"{self.url}/labelclasses/",
                         params={"token": self.user_token},
                         data=json.dumps({
                                          'name': name,
                                          'labelproject': self.id,
                                          'color': color
                                          })).json(), self.user)

    def create_labelfile(self, data_file):
        return req.post(f"{self.url}/add-object/", files={'files': open(data_file, "rb")}, data={
                        'token': self.user_token,
                        'labelprojectId': self.id,
                        'frame_value': 0
                    }, stream=True).json()

    def create_custom_ai(self, custom_ai_type="box", use_class_info={},
                         valueForPredictColumnId=None, trainingColumnInfo={}):
        """

            `Create Custom Ai`

            :param item
            - **token**: str = user token

            :json item
            - **custom_ai_type**: str = labeling type. Example, "polygon" or "box"
            - **use_class_info**: dict = labelClass to use for Autolabeling
            - **labelproject_id**: int = target label project id

            \f
        """

        return req.post(f"{self.url}/customai/",
                         params={"token": self.user_token},
                         data=json.dumps({
                                          'custom_ai_type': custom_ai_type,
                                          'use_class_info': use_class_info,
                                          'valueForPredictColumnId': valueForPredictColumnId,
                                          'trainingColumnInfo': trainingColumnInfo,
                                          'labelproject_id': self.id,
                                          })).json()
        pass


    def autolabeling(self, amount, ai_type="general", autolabeling_type="box", general_ai_type="person",
                    model_id=None, custom_ai_stage=0, preprocessing_ai_type={}, labeling_class=None ):
        """
            `Create AutoLabeling`

            - **ai_type**: int =  autolabelingAiType (custom or general or inference)
            - **autolabeling_type**: str = autolabeling type (For example, box or polygon)
            - **custom_ai_stage**: int = CustomAi Count
            - **general_ai_type**: str = None or generalAiType (For example person or road or animal or fire)
            - **preprocessing_ai_type**: dict = autolabeling preprocessingType. For example, {"faceblur": true}
            - **autolabeling_amount**: int = Number of images to autolabeling
            - **labeling_class**: List[str] = List of label classes

            \f
        """

        return req.post(f"{self.url}/autolabeling/",
                         params={"token": self.user_token},
                         data=json.dumps({
                                          'autolabeling_amount': amount,
                                          'autolabeling_ai_type': ai_type,
                                          'autolabeling_type': autolabeling_type,
                                          'custom_ai_stage': custom_ai_stage,
                                          'general_ai_type': general_ai_type,
                                          'preprocessing_ai_type': preprocessing_ai_type,
                                          'labeling_class': labeling_class,
                                          'model_id': model_id,
                                          'labelproject_id': self.id,
                                          })).json()
        pass

    def export(self, is_get_image=False):
        if self.workapp in ['object_detection', 'image']:
            return Asynctask(req.post(f"{self.url}/export-coco/{self.id}/",
                            params={"token": self.user_token, 'is_get_image': is_get_image},
                            ).json(), self.user)
        else:
            return Asynctask(req.post(f"{self.url}/export-data/{self.id}/",
                           params={"token": self.user_token},
                           ).json(), self.user)


class Labelfile(object):
    def __init__(self, info, user, label_classes):
        if not isinstance(info, dict):
            raise Exception(str(info))
        if info.get('error'):
            raise Exception(info['message_en'])
        self.__dict__.update(info)
        self.id = info['id']
        self.file_name = info['originalFileName']
        self.status = info['status']
        self.file_url = info['s3key']
        self.width = info['width']
        self.height = info['height']
        self.labelproject = info['labelproject']
        self.label_classes = label_classes
        self.url = Util().url
        self.user = user
        self.user_token = self.user.token

    def __repr__(self):
        return str(self.file_name)

    def download(self, file_path=""):

        if not file_path:
            file_path = self.file_name

        response = req.get(self.file_url)
        with open(file_path, 'wb') as output:
            output.write(response.content)

        return file_path

    def set_done(self, workAssignee=None):
        self.status = "done"
        return self.set_status("done", workAssignee=workAssignee)

    def set_status(self, status, workAssignee=None):
        self.status = status
        return req.put(f"{self.url}/sthreefiles/{self.id}/",
                 params={"token": self.user_token},
                 data=json.dumps({
                     'status': status,
                     'workAssignee': workAssignee,
                 })).json()

    def create_label(self, label, class_name=None, color=None, box=[], polygon=[], structuredData=None):

        if isinstance(label, Instance):
            return self.create_labels([label])
        return self.create_labels([{
                     'labeltype': label,
                     'class_name': class_name,
                     'sthreefile': self.id,
                     'color': color,
                     'box': box,
                     'polygon': polygon,
                     'structuredData': structuredData,
                     'labelproject': self.id,
                     'highlighted': False,
                     'locked': True,
                     'status': "done",
                 }])[0]

    def create_labels(self, labels_raw):
        labels = []
        for label_raw in labels_raw:
            if isinstance(label_raw, Instance):
                label_raw = label_raw.__dict__

            label_class_id = None
            label_class_name = label_raw.get("class_name")
            for label_class in self.label_classes:
                if label_class.name == label_class_name:
                    label_class_id = label_class.id

            if not label_class_id:
                raise Exception("You need to create a label class first.")

            processed_points = []
            for point in label_raw.get("polygon", []):
                label_raw['labeltype'] = "polygon"
                processed_points.append([point[0] / self.width, point[1] / self.height])

            if label_raw.get("box", []):
                label_raw['labeltype'] = "box"
                label_raw['x'] = round(label_raw['box'][0] / self.width, 8)
                label_raw['w'] = round((label_raw['box'][2] - label_raw['box'][0]) / self.width, 8)
                label_raw['y'] = round(label_raw['box'][1] / self.height, 8)
                label_raw['h'] = round((label_raw['box'][3] - label_raw['box'][1]) / self.height, 8)

            label_raw.update({
                              'labelproject': self.labelproject,
                              'labelclass': label_class_id,
                              'sthreefile': self.id,
                              'points': processed_points,
                              'highlighted': False,
                              'locked': True,
                              'status': "done"
                              })
            labels.append(label_raw)

        response = req.post(f"{self.url}/labels/",
                 params={"token": self.user_token, "info": True},
                 data=json.dumps(labels)).json()

        if response.get("result", "") == "success":
            self.set_done()

        return response

    def delete(self):
        return req.delete(f"{self.url}/sthreefiles/",
                          params={"token": self.user_token},
                          data={"sthreefilesId": [str(self.id)]})

class Label(object):
    def __init__(self, info, user):
        if not isinstance(info, dict):
            raise Exception(str(info))
        if info.get('error'):
            raise Exception(info['message_en'])
        self.__dict__.update(info)
        self.id = info['id']
        self.labeltype = info['labeltype']
        self.url = Util().url
        self.user = user
        self.user_token = self.user.token

    def __repr__(self):
        return str(f"{self.labeltype}: {self.id}")

    def delete(self):
        req.delete(f"{self.url}/labels/{self.id}/",params={"token": self.user_token})


class Labelclass(object):
    def __init__(self, info, user):
        if not isinstance(info, dict):
            raise Exception(str(info))
        if info.get('error'):
            raise Exception(info['message_en'])
        self.__dict__.update(info)
        self.id = info['id']
        self.labelproject = info['labelproject']
        self.url = Util().url
        self.user = user
        self.name = info['name']
        self.user_token = self.user.token

    def __repr__(self):
        return str(self.name)

    def modify(self, name=None, color=None):
        return Labelclass(req.put(f"{self.url}/labelclasses/{self.id}/",
                            params={"token": self.user_token},
                            data=json.dumps({
                                'name': name,
                                'color': color,
                            })).json(), self.user)

    def delete(self):
        req.delete(f"{self.url}/labelclasses/{self.id}/",params={"token": self.user_token})
