import pandas as pd   
from ..utils import *
file_path = r'D:\UTILS\app\handler\SOP_Automation_Handler\fromdbconnection.txt' 
from_connection = establish_connection(file_path)
toconnection=establish_connection(r'D:\UTILS\app\handler\SOP_Automation_Handler\todbconnection.txt')
def m_code():
    to_cursor=toconnection.cursor()
    to_cursor.execute("SET foreign_key_checks = 0;")
    toconnection.commit()
    truncate_query="truncate table m_code"
    to_cursor.execute(truncate_query)
    print("m_code table truncated")
    toconnection.commit()
    from_cursor=from_connection.cursor()
    query = "SELECT * FROM m_code;"
    from_cursor.execute(query)
    result=from_cursor.fetchall()
    columns = [desc[0] for desc in from_cursor.description]
    m_code_df = pd.DataFrame(result, columns=columns)
    for index,row in m_code_df.iterrows():
        insert_query=f"INSERT INTO m_code (id ,code_name,is_system_defined) VALUES ('{row['id']}','{row['code_name']}', '{row['is_system_defined']}');"
        to_cursor.execute(insert_query)
        toconnection.commit()
    print("m_code table created")
    to_cursor.execute("SET foreign_key_checks = 1;")
    toconnection.commit()
def m_code_value():
    to_cursor=toconnection.cursor()
    to_cursor.execute("SET foreign_key_checks = 0;")
    toconnection.commit()
    truncate_query="truncate table m_code_value"
    to_cursor.execute(truncate_query)
    print("m_code_value table truncated")
    from_cursor=from_connection.cursor()
    query = "SELECT * FROM m_code_value;"
    from_cursor.execute(query)
    result=from_cursor.fetchall()
    columns = [desc[0] for desc in from_cursor.description]
    m_code_value_df = pd.DataFrame(result, columns=columns)
    for index, row in m_code_value_df.iterrows():
        columns = []
        values = []
        for column, value in row.items():
            if value is not None:
                columns.append(column)
                if isinstance(value, str):
                    values.append(f"'{value}'")
                else:
                    values.append(str(value))
        columns_str = ', '.join(columns)
        values_str = ', '.join(values)
        insert_query = f"INSERT INTO m_code_value ({columns_str}) VALUES ({values_str});"
        to_cursor.execute(insert_query)
        toconnection.commit()
    print("m_code_value table created")
    to_cursor.execute("SET foreign_key_checks = 1;")
    toconnection.commit()
        

