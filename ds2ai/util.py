import json
import requests as req

class Util():
    url = "https://api.ds2.ai"

    def predict(self, request_data, predict_url, data, return_type="info"):

        if type(data) == dict:
            request_data["parameter"] = data
            response = {}
            response_raw = json.loads(self._predict(predict_url['predict'], request_data).json())
            if response_raw.get('이상값칼럼'):
                response['outliar'] = response_raw['이상값칼럼']
            for key, item in response_raw.items():
                if key.endswith('__예측값'):
                    response[key.replace('__예측값', '__predicted')] = item
            return response
        else:
            if data.startswith(('http://', 'https://')):
                request_data['url'] = data
                if return_type == "info":
                    inference_results_raw = self._predict(predict_url['predictimagebyurlinfo'], request_data).json()
                    inference_results = []
                    boxes = inference_results_raw.get("boxes", [])
                    masks = inference_results_raw.get("masks", [])
                    for index, inference_result_raw in enumerate(inference_results_raw.get('prediction', [])):
                        inference_result = {
                            "class_name": inference_result_raw,
                            "score": inference_result_raw,
                        }
                        if boxes:
                            inference_result['box'] = boxes[index]
                        if masks:
                            inference_result['mask'] = masks[index]
                        inference_results.append(Instance(inference_result))

                    return inference_results
                elif return_type == "xai":
                    return self._predict(predict_url['predictimagebyurlxai'], request_data).content
                else:
                    return self._predict(predict_url['predictimagebyurl'], request_data).content
            else:
                with open(data, "rb") as f:
                    file_content = f.read()
                    request_data["filename"] = data.split('/')[-1] if '/' in data else data
                    if data.endswith('.csv'):
                        return self._predict(predict_url['predictall'], request_data,
                                             file_content=file_content)
                    if data.endswith((".jpg", ".jpeg", ".png", "gif", ".mp4", ".mov")):
                        if return_type == "info":
                            inference_results_raw = self._predict(predict_url['predictimageinfo'], request_data,
                                             file_content=file_content).json()
                            inference_results = []
                            boxes = inference_results_raw.get("boxes", [])
                            polygons = inference_results_raw.get("polygons", [])
                            for index, inference_result_raw in enumerate(inference_results_raw.get('prediction', [])):
                                inference_result = {
                                    "class_name": inference_result_raw,
                                    "score": inference_results_raw['scores'][index],
                                }
                                if boxes:
                                    inference_result['box'] = boxes[index]
                                if polygons:
                                    inference_result['polygon'] = polygons[index]
                                inference_results.append(Instance(inference_result))

                            return inference_results

                        elif return_type == "xai":
                            return self._predict(predict_url['predictimagexai'], request_data,
                                             file_content=file_content).content
                        else:
                            return self._predict(predict_url['predictimage'], request_data,
                                             file_content=file_content).content

    def _predict(self, target_url, request_data, file_content=None):
        if file_content:
            return req.post(target_url, files={'file': file_content}, data=request_data, stream=True)
        else:
            return req.post(target_url, data=json.dumps(request_data))

class Asynctask(object):
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

    def refresh(self):
        return Asynctask(req.get(f"{self.url}/asynctasks/{self.id}/",
                                 params={"token": self.user_token}).json(), self.user)


class MarketModel(object):
    utilClass = Util()

    def __init__(self, info, user):
        if not isinstance(info, dict):
            raise Exception(str(info))
        if info.get('error'):
            raise Exception(info['message_en'])
        self.__dict__.update(info)
        self.id = info['id']
        self.name = info['name_en']
        self.url = self.utilClass.url
        self.user = user
        self.user_token = self.user.token

    def __repr__(self):
        return str(self.name)

    def predict(self, data, return_type="info"):
        request_data = {
            "apptoken": self.user.appTokenCode,
            "modelid": self.id,
            "userId": self.user.id,
        }

        predict_url = {
            "predict": f"{self.url}/predict/market/",
            "predictimagebyurl": f"{self.url}/predictimagebyurl/market/",
            "predictimagebyurlxai": f"{self.url}/predictimagebyurlxai/market/",
            "predictimagebyurlinfo": f"{self.url}/predictimagebyurlinfo/market/",
            "predictall": f"{self.url}/predictall/market/",
            "predictimage": f"{self.url}/predictimage/market/",
            "predictimagexai": f"{self.url}/predictimagexai/market/",
            "predictimageinfo": f"{self.url}/predictimageinfo/market/",
        }

        return self.utilClass.predict(request_data, predict_url, data, return_type=return_type)

class User(object):
    def __init__(self, info):
        if not isinstance(info, dict):
            raise Exception(str(info))
        if info.get('error'):
            raise Exception(info['message_en'])
        self.token = info['token']
        self.__dict__.update(info)

class Instance(object):

    def __init__(self, info):
        if not isinstance(info, dict):
            raise Exception(str(info))
        if info.get('error'):
            raise Exception(info['message_en'])
        self.__dict__.update(info)
        self.class_name = info['class_name']

    def __repr__(self):
        return str(self.class_name)
