#!/usr/bin/env python
# coding: utf-8

# ### Import all the modules required


import requests
import os
import json


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


endpoint = f"{base_url}/agents.json"


headers = {"Content-Type": "application/json",
               "Accept": "application/json"}


response = session.get(endpoint, auth=(TE_USER, TE_SECRET), headers=headers)


data = json.loads(response.text)


data['agents']


def get_enterprise_agents_dict(session):
    
    endpoint = f"{base_url}/agents.json"
    response = session.get(endpoint, auth=(TE_USER, TE_SECRET), headers=headers)
    
    data = json.loads(response.text)
    
    agents_dict = {}
    
    for agents in data['agents']:
        if "Enterprise" in agents['agentType']:
            countryID = agents['countryId']
            try:
                agents_dict[agents['clusterMembers'][0]['targetForTests']] = [agents['agentId'],countryID]
            except:
                agents_dict[agents['targetForTests']] = [agents['agentId'],countryID]
        
    return agents_dict

agents = get_enterprise_agents_dict(session)
