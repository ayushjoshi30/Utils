# utils.py
import os
import mysql.connector
file_path = r'D:\UTILS\app\handler\SOP_Automation_Handler\fromdbconnection.txt' 

def get_db_config(file_path):
    """Reads the database configuration from a file."""
    config = {}
    with open(file_path, 'r') as file:
        for line in file:
            if line.strip():  # Skip empty lines
                key, value = line.strip().split('=')
                config[key.strip()] = value.strip().strip("'")
    return config
def get_credentials(server):
    password_dict={
        "localhost": "root",
        "demo":"demoip",
        "prod":"prodip",
        "UAT": "UATip"
    }
    user_dict={
        "localhost": "root",
        "demo":"demo",
        "prod":"prod",
        "UAT": "UAT"
    }
    return user_dict[server], password_dict[server]
def write_to_dbconn(destination_server,destination_tenant):
    to_user ,to_password=get_credentials(destination_server)
    with open(r'D:\UTILS\app\handler\SOP_Automation_Handler\todbconnection.txt',"w") as f:
        f.write(f"host={destination_server}\n")
        f.write(f"user={to_user}\n")
        f.write(f"password={to_password}\n")
        f.write(f"database=fineract_{destination_tenant}")

def write_from_dbconn(source_server,source_tenant):
    from_user,from_password=get_credentials(source_server)
    with open(r'D:\UTILS\app\handler\SOP_Automation_Handler\fromdbconnection.txt',"w") as f:
        f.write(f"host={source_server}\n")
        f.write(f"user={from_user}\n")
        f.write(f"password={from_password}\n")
        f.write(f"database=fineract_{source_tenant}")
def establish_connection(file_path):
    """Establishes a connection to the MySQL database using the configuration file."""
    # Read the configuration from the file
    config = get_db_config(file_path)

    # Establish the connection using the configuration
    try:
        connection = mysql.connector.connect(
            host=config['host'],
            database=config['database'],
            user=config['user'],
            password=config['password']
        )
        
        if connection.is_connected():
            print("Connection successful")
            return connection
        else:
            print("Failed to connect")
            return None
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None
def read_headers_from_file(file_path,destination_tenant):
    headers = {}
    with open(file_path, 'r') as file:
        for line in file:
            key, value = line.strip().split(":", 1)
            headers[key.strip()] = value.strip()
    headers["Fineract-Platform-TenantId"]=destination_tenant
    return headers

def get_api_url(endpoint):
    base_url = os.getenv("API_BASE_URL", f"https://localhost:8443/fineract-provider/api/v1")
    return f"{base_url}/{endpoint}"
def get_new_role_id(roles_dict,old_role_id):
    return roles_dict.get(old_role_id)

def get_role_name(id,connection):
    cursor=connection.cursor()
    query=f"select name from m_role where id={id};"
    cursor.execute(query)
    result=cursor.fetchone()
    return result[0]
def get_old_to_new_action_group_id():
    from_connection = establish_connection(file_path)
    to_connection=establish_connection(r'D:\UTILS\app\handler\SOP_Automation_Handler\todbconnection.txt')
    from_cursor=from_connection.cursor()
    to_cursor=to_connection.cursor()
    select_query="select id from r_sop_action_groups"
    from_cursor.execute(select_query)
    from_result=from_cursor.fetchall()
    from_ids=[row[0] for row in from_result]
    to_cursor.execute(select_query)
    to_result=to_cursor.fetchall()
    to_ids=[row[0] for row in to_result]
    mapping_dict=dict(zip(from_ids,to_ids))
    return mapping_dict
def get_action_name(action_id):
    actions_dict={1:"activity complete",2:"approve",3:"reject",4:"skip",5:"start over"}
    return actions_dict.get(action_id)

