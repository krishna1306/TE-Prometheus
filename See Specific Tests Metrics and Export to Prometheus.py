#!/usr/bin/env python
# coding: utf-8

# ### Import all the modules required

import requests
import os
import json
import pickle
import prometheus_client as prom


# ### Check TE Connection
# 
# #### TE Credentials
# 
# **TE_Secret** is fetched from TE Account Settings > API Token

TE_USER = "user@email.com"

TE_SECRET = "api_access_code"


# ### Prepare the HTTP Metadata
# 
# Each HTTP request must have 
# 
# 1. `Endpoint URL` - where the data lives
# 2. `auth` - authentication (Here we use API token instead of password)
# 3. `headers` - what kind of data we accept and what kind of data we are sending


base_url = "https://api.thousandeyes.com/v6"

session = requests.Session()


# Here, our `endpoint` is `tests.json` - this lists all the tests created in this account

endpoint = f"{base_url}/tests.json"

headers = {"Content-Type": "application/json",
               "Accept": "application/json"}


# ### Call the API and get data
# 
# Data gets stored in the `response` object along with the return code. 
# If the return code is not `200`, then there is something wrong with the query.


response = session.get(endpoint, auth=(TE_USER, TE_SECRET), headers=headers)


# Load the data in the response object in a text format, using `json` python library
# 
# `json` python library returns the data in a `python dictionary` format

data = json.loads(response.text)

data["test"][0]


# In the above output, it shows `'enabled': 0` - which means the test is inactive
# 
# Let us now filter for only active and GIS related tests, and capture them in `enabled_GIS_tests` list


enabled_GIS_tests = []


for test in data["test"]:
    if test['enabled'] != 0 and test['testName'][0:3]=="GIS":
        enabled_GIS_tests.append(test)


# Lets see how many total tests were there, and how many are enabled in that
# 
# ### Enabled Tests


len(enabled_GIS_tests)


# ### Total Tests

len(data["test"])


# ### Let's See First Enabled GIS Tests


for GIS_Tests in enabled_GIS_tests:
    print(f"\nTest ID is : {GIS_Tests['testId']}")
    print(f"Test Name is : {GIS_Tests['testName']}")
    print(f"Destination IP is : {GIS_Tests['server']}")
    print(f"Test URL is : {GIS_Tests['apiLinks'][1]['href']}")


# ### Create a dictionary of Enabled GIS Tests


enabled_gis_tests_dic = {}

for GIS_Tests in enabled_GIS_tests:
    enabled_gis_tests_dic[GIS_Tests['testId']] = GIS_Tests['testName']
    
enabled_gis_tests_dic

enabled_GIS_tests[0]


# ### See Metrics for a Sample GIS Tests URL


metrics_url = enabled_GIS_tests[0]['apiLinks'][1]['href']
response = session.get(metrics_url, auth=(TE_USER, TE_SECRET), headers=headers)
data = json.loads(response.text)

data['net']['test']['server']

for metrics in data['net']['metrics']:
    print(f"\n\nLoss is {metrics['loss']}")
    if "100" not in str(metrics['loss']):
          print(f"Avg. Latency is {metrics['avgLatency']}")
          print(f"Jitter is {metrics['jitter']}")
          print(f"Source Agent is {metrics['serverIp']} ")
          print(f"Source Agent ID is {metrics['agentId']}")
          print(f"Destination IP is {data['net']['test']['server']}")        


# ### A list of Tuples - This is what we will be capturing from Thousand Eyes


Watched_Metrics = [('latency','avgLatency'),('jitter','jitter'),('loss','loss'),('srcagentid','agentId'),('dstIp','serverIp')]


# ### Create a Function that gets data for each Test Agent


def get_test_data(session,testid):
    
    # Construct the metrics_URL
    metrics_url = "https://api.thousandeyes.com/v6/net/metrics/" + str(testid)
    
    # Get the response from TE using the metrics_URL supplied
    response = session.get(metrics_url, auth=(TE_USER, TE_SECRET), headers=headers)
    data = json.loads(response.text)
    
    # Initiate an empty list to store all the dictionaries for this Test Agent
    result = []
    
    for metrics in data['net']['metrics']:
        # An empty dictionary to hold the values, before adding it to result[]
        dic = {}
        
        for name, metric_name in Watched_Metrics:
            try:
                dic[name] = metrics[metric_name]
            except:
                dic[name] = -1
        
        dic['testid'] = testid
        result.append(dic)
    
    return result



enabled_gis_tests_dic



per_session_data = {}

for test_id,test_name in enabled_gis_tests_dic.items():
    per_session_data[test_id] = get_test_data(session,test_id)


per_session_data


import os

os.getcwd()

with open('session_data','wb') as file:
    pickle.dump(per_session_data,file)
