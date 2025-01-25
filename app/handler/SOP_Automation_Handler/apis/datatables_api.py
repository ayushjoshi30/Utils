from ..utils import *
import pandas as pd    
file_path = r'D:\UTILS\app\handler\SOP_Automation_Handler\fromdbconnection.txt' 
toconnection=establish_connection(r'D:\UTILS\app\handler\SOP_Automation_Handler\todbconnection.txt')
from_connection = establish_connection(file_path)
def create_table(tablename):
    from_cursor = from_connection.cursor()
    to_cursor = toconnection.cursor()
    to_cursor.execute("SET foreign_key_checks = 0;")
    to_cursor.execute(f"drop table if exists `{tablename}`")
    from_cursor.execute(f"SHOW CREATE TABLE `{tablename}`")
    result = from_cursor.fetchone()
    ddl_command = result[1]
    to_cursor.execute("SET foreign_key_checks = 1;")
    to_cursor.execute(ddl_command)
    print(f"Table `{tablename}` created successfully")

def insert_x_registered_table():
    from_cursor = from_connection.cursor()
    to_cursor = toconnection.cursor()
    to_cursor.execute("SET foreign_key_checks = 0;")
    to_cursor.execute("truncate table `x_registered_table`")
    from_cursor.execute("SELECT * FROM `x_registered_table`")
    rows = from_cursor.fetchall()
    columns = [desc[0] for desc in from_cursor.description]
    insert_query = f"INSERT INTO `x_registered_table` ({', '.join(columns)}) VALUES ({', '.join(['%s'] * len(columns))})"
    to_cursor.executemany(insert_query, rows)
    toconnection.commit()
    to_cursor.execute("SET foreign_key_checks = 1;")
    from_cursor.close()
    to_cursor.close()
    print("Data transfer complete for x_registered_table.")
def insert_k_datatable_section_meta(tablename):
    from_cursor = from_connection.cursor()
    to_cursor = toconnection.cursor()
    from_cursor.execute(f"SELECT * FROM `k_datatable_section_meta` where x_registered_table_name ='{tablename}'")
    rows = from_cursor.fetchall()
    columns = [desc[0] for desc in from_cursor.description]
    insert_query = f"INSERT INTO `k_datatable_section_meta` ({', '.join(columns)}) VALUES ({', '.join(['%s'] * len(columns))})"
    to_cursor.executemany(insert_query, rows)
    toconnection.commit()
    from_cursor.close()
    to_cursor.close()
    print(f"Data transfer into k_datatable_section_meta for {tablename} complete.")
def insert_k_datatable_section(tablename):
    from_cursor = from_connection.cursor()
    to_cursor = toconnection.cursor()
    from_cursor.execute(f"SELECT * FROM `k_datatable_section` where x_registered_table_name ='{tablename}'")
    rows = from_cursor.fetchall()
    columns = [desc[0] for desc in from_cursor.description]
    insert_query = f"INSERT INTO `k_datatable_section` ({', '.join(columns)}) VALUES ({', '.join(['%s'] * len(columns))})"
    to_cursor.executemany(insert_query, rows)
    toconnection.commit()
    from_cursor.close()
    to_cursor.close()
    print(f"Data transfer into k_datatable_section for {tablename} complete.")
def get_x_registered_table():
    from_cursor = from_connection.cursor()
    from_cursor.execute("SELECT registered_table_name FROM x_registered_table")
    result = from_cursor.fetchall()
    table_names = [row[0] for row in result]
    return table_names


def data_tables():
    to_cursor = toconnection.cursor()
    to_cursor.execute("SET foreign_key_checks = 0;")
    to_cursor.execute("truncate table `k_datatable_section_meta`")
    to_cursor.execute("truncate table `k_datatable_section`")
    to_cursor.execute("SET foreign_key_checks = 1;")
    to_cursor.execute("ALTER TABLE `k_datatable_section_meta` MODIFY COLUMN `display_name` VARCHAR(500) CHARACTER SET utf8;")
    to_cursor.execute("ALTER TABLE `k_datatable_section` MODIFY COLUMN `name` VARCHAR(500) CHARACTER SET utf8;")
    to_cursor.execute("ALTER TABLE `k_datatable_section_meta` MODIFY COLUMN `show_when` VARCHAR(500);")
    to_cursor.execute("ALTER TABLE `k_datatable_section_meta` MODIFY COLUMN `column_name` VARCHAR(500);")
    to_cursor.execute("ALTER TABLE `k_datatable_section_meta` MODIFY COLUMN `name` VARCHAR(500) CHARACTER SET utf8;")
    toconnection.commit()
    table_names = get_x_registered_table()
    for table_name in table_names:
        create_table(table_name)
        insert_k_datatable_section_meta(table_name)
        insert_k_datatable_section(table_name)
    insert_x_registered_table()
def update_datables():
    to_cursor = toconnection.cursor()
    to_cursor.execute("SET foreign_key_checks = 0;")
    to_cursor.execute("""
        UPDATE k_datatable_section_meta
        SET x_registered_table_name = LOWER(x_registered_table_name)
    """)
    to_cursor.execute("""
        UPDATE k_datatable_section
        SET x_registered_table_name = LOWER(x_registered_table_name)
    """)
    to_cursor.execute("""
        UPDATE x_registered_table
        SET registered_table_name = LOWER(registered_table_name)
    """)
    to_cursor.execute("SET foreign_key_checks = 1;")
    toconnection.commit()
    to_cursor.close()
    print("Values in the specified columns have been converted to lowercase.")

    
    