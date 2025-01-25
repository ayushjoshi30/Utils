import mysql.connector
def get_url(server):
    return f"https://{server}:8443/fineract-provider/api/v1/"
def getdb_connection(server,tenant):
    mydb = mysql.connector.connect(
        host=server,
        database=f'fineract_{tenant}',
        user='root',
        password='root'
    )
    cursor = mydb.cursor()
    return mydb,cursor

def get_headers(tenant):
    headers = {
        'Authorization': 'Basic bmlraXRhOm5pa2l0YUBrYW1hbDgzOA==',
        'Content-Type': 'application/json;charset=UTF-8',
        'Fineract-Platform-TenantId': tenant,
    }
    return headers