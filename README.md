
The official [DS2.ai](https://ds2.ai/) SDK for Python.  
Documentation can be found on [SDK guide](https://docs.ds2.ai/sdk_00_readme/)

# MLOps with DS2.ai

[DS2.ai](https://ds2.ai/) is an integrated AI operation solution that supports all stages from custom AI development to deployment. It is an AI-specialized platform service that collects data, builds a training dataset through data labeling, and enables automatic development of artificial intelligence and easy deployment and operation.

The Software Development Kit (SDK) consists of python functions that allow you to write your own scripts by accessing DS2.ai's features.

![Screen_Shot_2021-07-01_at_3 37 53_PM](https://user-images.githubusercontent.com/72846894/124224623-fcc39c80-db40-11eb-9737-2e384d88c300.png)

## **Installation**


Install via pip:

```
$ pip install ds2ai
```


## **Getting started**


### 1. Getting your own token

To use the SDK, you need to get a token, and you can check the token by registering as a member of [ds2.ai](https://ds2.ai/). After registering the card on the site, you can use the token.  

<center>
<img width="2000" src="https://user-images.githubusercontent.com/72846894/124224654-0b11b880-db41-11eb-8764-90dc1d2cf469.gif"/>
</center>

### 2. Activate

To use SDK function code, you have to activate your code, first.  

Run the below code with your own app token.   

```python
import ds2ai

ds2 = ds2ai.DS2(token)
```

Then you can use all functions in [SDK guide](https://docs.ds2.ai/sdk_00_readme/).

---

## **Top 5 Features of [DS2.ai](https://ds2.ai/) SDK**


The SDK is composed of 16 classes. Class DS2 provides python functions that are more generally used for AI development, whereas the others provide specific functions for each detailed steps in AI development.  

Here, we want to explain to you examples of using **Top5 function codes that are usable and easy to use.**   

### 1. Getting magic code

```python
ds2.get_magic_code(training_method, data_file, value_for_predict)
```

This function returns a the magic code for setting variable values with optimal combinations for AI training. As with the three functions above, it takes the data_file, training_method, value_for_predict as input so that after running the function, a magic code with the whole process of AI training is returned. 

<img width="2800" src="https://user-images.githubusercontent.com/72846894/129141964-fbc17082-64d5-4d13-b56c-6682dbbd50e4.gif"/>   
<br>

### 2. Auto Labeling

```python
ds2.start_auto_labeling(data_file, amount, has_label_data=False, predict_column_name=None, frame=60,
                          ai_type="general", autolabeling_type="box", general_ai_type="person",
                          model_id=None, custom_ai_stage=0, preprocessing_ai_type={}, labeling_class=[],
                          training_method="object_detection", name='', description=''
                          )
                          
```
This function executes auto-labeling immediately from loading data file without using dataconnector. The major parameters include data_file to auto-label, whether the data includes labeled data for a certain part of the dataset, and the type of auto-labeling, such as “box”, which will label using bounding boxes.

<img width="2800" src="https://user-images.githubusercontent.com/72846894/125561952-79a2e8f8-4f3f-4def-bdca-848b6d19e423.gif"/>
<br>

### 3. AI Training

```python
ds2.train(data_file, training_method, value_for_predict, option="accuracy", frame=60)
```
This function executes development of AI from CLICK AI in DS2.ai’s console immediately from loading data file without using dataconnector. According to what parameters you use when calling the function, such as data_file, training_method, value_for_predict, and option, it will generate your customized AI models.  

<img width="2800" src="https://user-images.githubusercontent.com/72846894/125380537-4c218c80-e3cd-11eb-85e7-cb8686f2cf7b.gif"/>
<br>

### 4. Deploy your AI model

```python
ds2.deploy(model_file, name=None, cloud_type="AWS", region="us-west-1", server_type="g4dn.xlarge")
```
This function deploys AI models to cloud servers with specifications under the desired hosting region. The type of the cloud server is set to “AWS” as default, but keep in mind that it also supports other cloud services such as Google Cloud. For the use of servers other than AWS, please visit our website and contact our team.
  
<img width="2800" src="https://user-images.githubusercontent.com/72846894/125379607-c7823e80-e3cb-11eb-85ce-c0cd35cfa588.gif"/>   
<br>

### 5. Rent AI training server

```python
ds2.rent_custom_training_server(cloud_type="AWS", region="us-west-1", server_type="g4dn.xlarge", name=None)
```
This function rents an inference training server in preferred cloud environment for Custom training of Click AI. The type of the cloud server is set to “AWS” as default, but keep in mind that it also supports other cloud services such as Google Cloud. For the use of servers other than AWS, please visit our website and contact our team.  

<img width="2800" src="https://user-images.githubusercontent.com/72846894/125380727-9efb4400-e3cd-11eb-824b-676d670941b5.gif"/>   
<br>

## **Getting Help**

You can interact with the ds2ai code or software by asking a question or referencing the guide from the underlying open resources.

- GitHub
    - [https://github.com/DS2BRAIN/ds2ai](https://github.com/DS2BRAIN/ds2ai)
- stackoverflow - Ask all code and software related questions here.
    - [https://stackoverflow.com/questions/tagged/ds2ai](https://stackoverflow.com/questions/tagged/ds2ai)
- CrossValidated - Ask questions about artificial intelligence algorithms and theories here.
    - [https://stats.stackexchange.com/questions/tagged/ds2ai](https://stats.stackexchange.com/questions/tagged/ds2ai)
- Documentation
    - ds2ai user guide : [https://docs.ds2.ai/](https://docs.ds2.ai/)
    - ds2ai blog : [https://blog.ds2.ai/](https://blog.ds2.ai/)
- Website
    - [https://ds2.ai/](https://ds2.ai/)

If you need help that is not specific to this SDK, please reach out to the chat "Ask us in" in our application.

## **License**

This SDK is distributed under the Apache-2.0 License, please see [LICENSE](https://github.com/DS2BRAIN/ds2ai/blob/main/LICENSE) for more information.

<br>
<br>
<br>
