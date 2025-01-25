import pandas as pd          
from ..utils import *
file_path = r'D:\UTILS\app\handler\SOP_Automation_Handler\fromdbconnection.txt' 
toconnection=establish_connection(r'D:\UTILS\app\handler\SOP_Automation_Handler\todbconnection.txt')
from_connection = establish_connection(file_path)
def r_sop():
    from_cursor = from_connection.cursor()
    to_cursor = toconnection.cursor()
    to_cursor.execute("SET foreign_key_checks = 0;")
    to_cursor.execute("TRUNCATE TABLE `r_sop`;")
    from_cursor.execute("SELECT * FROM `r_sop`;")
    rows = from_cursor.fetchall()
    excluded_column = 'is_active'  
    columns = [desc[0] for desc in from_cursor.description if desc[0] != excluded_column]
    insert_query = f"INSERT INTO `r_sop` ({', '.join(columns)}) VALUES ({', '.join(['%s'] * len(columns))})"
    filtered_rows = []
    for row in rows:
        filtered_row = [value for col, value in zip([desc[0] for desc in from_cursor.description], row) if col != excluded_column]
        filtered_rows.append(tuple(filtered_row))
    to_cursor.executemany(insert_query, filtered_rows)
    toconnection.commit()
    to_cursor.execute("SET foreign_key_checks = 1;")

    # Close the cursors
    from_cursor.close()
    to_cursor.close()
    print("Data transfer for r_sop complete, excluding the specified column.")


    
def r_sop_step(action_group_mapping):
    from_cursor = from_connection.cursor()
    to_cursor = toconnection.cursor()
    to_cursor.execute("SET foreign_key_checks = 0;")
    to_cursor.execute("TRUNCATE TABLE `r_sop_step`;")
    from_cursor.execute("SELECT * FROM `r_sop_step`;")
    rows = from_cursor.fetchall()
    columns = [desc[0] for desc in from_cursor.description]
    action_group_id_index = columns.index("action_group_id")
    modified_rows = []
    for row in rows:
        old_action_group_id = row[action_group_id_index]
        new_action_group_id = action_group_mapping[old_action_group_id]
        modified_row = row[:action_group_id_index] + (new_action_group_id,) + row[action_group_id_index + 1:]
        modified_rows.append(modified_row)
    insert_query = f"INSERT INTO `r_sop_step` ({', '.join(columns)}) VALUES ({', '.join(['%s'] * len(columns))})"
    to_cursor.executemany(insert_query, modified_rows)
    toconnection.commit()
    to_cursor.execute("SET foreign_key_checks = 1;")
    from_cursor.close()
    to_cursor.close()
    print("Data transfer complete for r_sop_step")
def r_sop_entity_mapping():
    from_cursor = from_connection.cursor()
    to_cursor = toconnection.cursor()
    to_cursor.execute("SET foreign_key_checks = 0;")
    to_cursor.execute("TRUNCATE TABLE `r_sop_entity_mapping`;")
    from_cursor.execute("SELECT * FROM `r_sop_entity_mapping`;")
    rows = from_cursor.fetchall()
    columns = [desc[0] for desc in from_cursor.description]
    insert_query = f"INSERT INTO `r_sop_entity_mapping` ({', '.join(columns)}) VALUES ({', '.join(['%s'] * len(columns))})"
    to_cursor.executemany(insert_query, rows)
    toconnection.commit()
    to_cursor.execute("SET foreign_key_checks = 1;")
    from_cursor.close()
    to_cursor.close()
    print("Data transfer complete for r_sop_entity_mapping")
    
def sop():
    r_sop()
    action_grop_mapping=get_old_to_new_action_group_id()
    r_sop_step(action_grop_mapping)
    r_sop_entity_mapping()