import pandas as pd          
from ..utils import *
file_path = r'D:\UTILS\app\handler\SOP_Automation_Handler\fromdbconnection.txt' 
toconnection=establish_connection(r'D:\UTILS\app\handler\SOP_Automation_Handler\todbconnection.txt')
from_connection = establish_connection(file_path)

def m_kyc_document():
    from_cursor = from_connection.cursor()
    to_cursor = toconnection.cursor()
    to_cursor.execute("SET foreign_key_checks = 0;")
    to_cursor.execute("truncate table `m_kyc_document`")
    from_cursor.execute("SELECT * FROM `m_kyc_document`")
    rows = from_cursor.fetchall()
    columns = [desc[0] for desc in from_cursor.description]
    insert_query = f"INSERT INTO `m_kyc_document` ({', '.join(columns)}) VALUES ({', '.join(['%s'] * len(columns))})"
    to_cursor.executemany(insert_query, rows)
    toconnection.commit()
    to_cursor.execute("SET foreign_key_checks = 1;")
    from_cursor.close()
    to_cursor.close()
    print("Data transfer for m_kyc_document complete.")

def m_kyc_pack():
    from_cursor = from_connection.cursor()
    to_cursor = toconnection.cursor()
    to_cursor.execute("SET foreign_key_checks = 0;")
    to_cursor.execute("truncate table `m_kyc_pack`")
    from_cursor.execute("SELECT * FROM `m_kyc_pack`")
    rows = from_cursor.fetchall()
    columns = [desc[0] for desc in from_cursor.description]
    insert_query = f"INSERT INTO `m_kyc_pack` ({', '.join(columns)}) VALUES ({', '.join(['%s'] * len(columns))})"
    to_cursor.executemany(insert_query, rows)
    toconnection.commit()
    to_cursor.execute("SET foreign_key_checks = 1;")
    from_cursor.close()
    to_cursor.close()
    print("Data transfer for m_kyc_pack complete.")

def m_kyc_pack_value():
    from_cursor = from_connection.cursor()
    to_cursor = toconnection.cursor()
    to_cursor.execute("SET foreign_key_checks = 0;")
    to_cursor.execute("truncate table `m_kyc_pack_value`")
    from_cursor.execute("SELECT * FROM `m_kyc_pack_value`")
    rows = from_cursor.fetchall()
    columns = [desc[0] for desc in from_cursor.description]
    insert_query = f"INSERT INTO `m_kyc_pack_value` ({', '.join(columns)}) VALUES ({', '.join(['%s'] * len(columns))})"
    to_cursor.executemany(insert_query, rows)
    toconnection.commit()
    to_cursor.execute("SET foreign_key_checks = 1;")
    from_cursor.close()
    print("Data transfer for m_kyc_pack_value_complete ")
    
def kyc_pack():
    m_kyc_document()
    m_kyc_pack()
    m_kyc_pack_value()
    