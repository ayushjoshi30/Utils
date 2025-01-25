import pandas as pd   
from ..utils import *
import requests 
import json
import urllib3
import warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
file_path = r'D:\UTILS\app\handler\SOP_Automation_Handler\fromdbconnection.txt' 
from_connection = establish_connection(file_path)
toconnection=establish_connection(r'D:\UTILS\app\handler\SOP_Automation_Handler\todbconnection.txt')
url_actiongroups=get_api_url("sop/actionGroup")
def get_actionroles_json(roles_dict):
    action_dict={}
    from_cursor=from_connection.cursor()
    select_query="select * from r_sop_actions_roles"
    from_cursor.execute(select_query)
    results=from_cursor.fetchall()
    columns = [desc[0] for desc in from_cursor.description]
    df_actions = pd.DataFrame(results, columns=columns)
    for index,row in df_actions.iterrows():
        if int(row["action_group_id"]) not in action_dict.keys():
            action_dict[int(row["action_group_id"])]={}
        if int(row["action_id"]) not in action_dict[int(row["action_group_id"])]:
            action_dict[int(row["action_group_id"])][int(row["action_id"])] =[]
        if get_new_role_id(roles_dict,int(row["role_id"])) is not None:
            action_dict[int(row["action_group_id"])][int(row["action_id"])].append(get_new_role_id(roles_dict,int(row["role_id"])))
                    
    with open("json_actions.json","w") as f:
        json.dump(action_dict,f,indent=4)
    return action_dict

def get_action_groups_dict():
    from_cursor=from_connection.cursor()
    select_query="select * from r_sop_action_groups"
    from_cursor.execute(select_query)
    results=from_cursor.fetchall()
    columns = [desc[0] for desc in from_cursor.description]
    df_action_groups = pd.DataFrame(results, columns=columns)
    action_groups_dict = df_action_groups.set_index('id')["name"].to_dict()
    return action_groups_dict
def action_groups(headers,roles_dict):
    action_groups_dict=get_action_groups_dict()
    actionsdict=get_actionroles_json(roles_dict)
    for d in actionsdict.keys():
        payload_actions_groups={
            "permittedActions":[],
            "actionGroupName":action_groups_dict[d]
        }
        
        val=actionsdict.get(d)
        for v in val.keys():
            arr=val.get(v)
            body={
            "actionId": str(v),
            "permittedRoles": [],
            "permittedRolesNames": "",
            "actionName": get_action_name(int(v))
            }
            for a in arr:
                body["permittedRoles"].append({
                    "id": str(a),
                    "name": get_role_name(int(a),toconnection)
                })
                body["permittedRolesNames"]+=f"{get_role_name(int(a),toconnection)}," if a!=arr[-1] else f"{get_role_name(int(a),toconnection)}"
            payload_actions_groups["permittedActions"].append(body)
        
        # with open("payload_action_groups.json","w") as f:
        #     json.dump(payload_actions_groups,f,indent=4)
        response_actiongroups = requests.request("POST", url_actiongroups, headers=headers, json=payload_actions_groups,verify=False)
        if response_actiongroups.status_code==200:
            print(f"Action Group '{action_groups_dict[d]}' created successfully.")
        else:
            print(f"Failed to create Action Group '{action_groups_dict[d]}'. Error: {response_actiongroups.text}")
        
    