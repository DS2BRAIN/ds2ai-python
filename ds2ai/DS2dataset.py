import json
from .util import Util
import requests as req


class Dataconnector(object):
    def __init__(self, info, user):
        if not isinstance(info, dict):
            raise Exception(str(info))
        if info.get('error'):
            raise Exception(info['message_en'])
        self.__dict__.update(info)
        self.id = info['id']
        self.name = info['dataconnectorName']
        self.url = Util().url
        self.user = user
        self.status = info['status']
        self.user_token = self.user.token

    def __repr__(self):
        return f"{str(self.id)}: {str(self.name)}"

    def delete(self):
        req.delete(f"{self.url}/dataconnectors/{self.id}/",params={"token": self.user_token})

    def get_magic_code(self, training_method, value_for_predict, file_path="output.ipynb"):

        if self.status != 100:
            raise ("The training data is being processed now. Please retry with dataconnector.get_magic_code() when the data is ready. When it is ready, dataconnector.status will return 100.")


        response = req.post(f"{self.url}/get-magic-code/",
                         params={"token": self.user_token},
                         data=json.dumps({
                             'dataconnector': self.id,
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
