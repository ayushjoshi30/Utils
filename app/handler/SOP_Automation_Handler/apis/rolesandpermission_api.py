import requests
import pandas as pd 
from ..utils import *
 # Path to your .txt file
file_path = r'D:\UTILS\app\handler\SOP_Automation_Handler\fromdbconnection.txt' 
toconnection=establish_connection(r'D:\UTILS\app\handler\SOP_Automation_Handler\todbconnection.txt')
from_connection = establish_connection(file_path)
def get_roles(from_connection):
    cursor=from_connection.cursor()
    query = "SELECT * FROM m_role;"
    cursor.execute(query)
    result=cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    roles = pd.DataFrame(result, columns=columns)
    return roles
def create_roles(headers):
    role_to_new_role_dict={}
    create_role_url=get_api_url("roles")
    rolesdf=get_roles(from_connection)
    for index, row in rolesdf.iterrows():
        role_to_new_role_dict[1]=1
        role_to_new_role_dict[2]=2
        if index in [0,1]:
            continue
        payload_role={
            "name": row["name"],
            "description":row["description"],
        }
        response_create_role = requests.request("POST", create_role_url, headers=headers, json=payload_role,verify=False)
        if response_create_role.status_code==200:
            role_to_new_role_dict[row["id"]]=response_create_role.json().get("resourceId")
            print(f"Role '{row['name']}' created successfully.")
        else:
            print(f"Failed to create role '{row['name']}'. Error: {response_create_role.text}")
    return role_to_new_role_dict
    
def m_permission():
    from_cursor = from_connection.cursor()
    to_cursor = toconnection.cursor()
    to_cursor.execute("SET foreign_key_checks = 0;")
    to_cursor.execute("truncate table `m_permission`")
    from_cursor.execute("SELECT * FROM `m_permission`")
    rows = from_cursor.fetchall()
    columns = [desc[0] for desc in from_cursor.description]
    insert_query = f"INSERT INTO `m_permission` ({', '.join(columns)}) VALUES ({', '.join(['%s'] * len(columns))})"
    to_cursor.executemany(insert_query, rows)
    toconnection.commit()
    to_cursor.execute("SET foreign_key_checks = 1;")
    from_cursor.close()
    print("Data transfer for m_permission_complete ")
    
def m_role_permission(roles_dict):
    from_cursor = from_connection.cursor()
    to_cursor = toconnection.cursor()
    to_cursor.execute("SET foreign_key_checks = 0;")
    to_cursor.execute("truncate table `m_role_permission`")
    from_cursor.execute("SELECT * FROM `m_role_permission`")
    rows = from_cursor.fetchall()
    columns = [desc[0] for desc in from_cursor.description]
    role_id_index = columns.index("role_id")
    modified_rows = []
    for row in rows:
        old_action_group_id = row[role_id_index]
        new_action_group_id = roles_dict[old_action_group_id]
        modified_row = row[:role_id_index] + (new_action_group_id,) + row[role_id_index + 1:]
        modified_rows.append(modified_row)
    insert_query = f"INSERT INTO `m_role_permission` ({', '.join(columns)}) VALUES ({', '.join(['%s'] * len(columns))})"
    to_cursor.executemany(insert_query, modified_rows)
    toconnection.commit()
    to_cursor.execute("SET foreign_key_checks = 1;")
    from_cursor.close()
    print("Data transfer for m_role_permission_complete ")
    

    