import pandas as pd
import json
import os
from django.contrib import messages
import mysql.connector
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from datetime import datetime
from .utilities import *
import requests
obj={}
excelarr=[]
template = {
    "name": "",
    "dob": "",
    "address": "",
    "mobile": "",
    "Gender": "",
    "Pan No": "",
    "Voter ID": "",
    "Passport No": "",
    "Driving License": "",
    "Aadhar": 0,
    "PIN Code": 0,
    "Income": 0,
}
casesss=set()
def get_template(row):
    new_template = template.copy() 
    new_template["name"] = row["Consumer Name"]
    new_template["dob"] = row["Date of Birth"]
    new_template["address"] = row["Address1"]
    new_template["mobile"] = row["Mobile No"]
    new_template["Gender"] = row["Gender"]
    new_template["Pan No"] = row["Pan No"] if not pd.isna(row["Pan No"]) else ""
    new_template["Voter ID"] = row["Voter ID"] if not pd.isna(row["Voter ID"]) else ""
    new_template["Passport No"] = row["Passport No"] if not pd.isna(row["Passport No"]) else ""
    new_template["Driving License"] = row["Driving License"] if not pd.isna(row["Driving License"]) else ""
    new_template["Aadhar"] = int(row["Universal ID Number"]) if not pd.isna(row["Universal ID Number"]) else 0
    new_template["PIN Code"] = row["PIN Code"] if not pd.isna(row["PIN Code"]) else 0
    new_template["Income"] = int(row["Income"])
    return new_template
created=[]
data={}
def process_excel(folder_path):
    file=os.listdir(folder_path)[0]
    filepath=os.path.join(folder_path,file)
    try:
        df = pd.read_excel(filepath)
    except Exception as e:
        return f"Error reading file '{filepath}': {str(e)}"
    for _, row in df.iterrows():
        if row["Curr/New Account No"] in created:
            continue
        if row["Curr/New Account No"] not in obj:
            obj[row["Curr/New Account No"]] = {"Coapplicant": [], "Guarantor": []}
        if int(row["Ownership Indicator"]) == 1:
            casesss.add(row["Curr/New Account No"])
        if int(row["Ownership Indicator"]) == 4:
            excelarr.append(row)
            created.append(row["Curr/New Account No"])
            obj[row["Curr/New Account No"]]["Coapplicant"].append(get_template(row))
        elif int(row["Ownership Indicator"]) == 3:
            excelarr.append(row)
            created.append(row["Curr/New Account No"])
            obj[row["Curr/New Account No"]]["Guarantor"].append(get_template(row))
    json_file_path = os.path.join(folder_path, f'{file.replace(".xlsx", "")}.json')
    with open(json_file_path, "w") as f:
        data.update(obj)
        json.dump(data, f, indent=4)
    os.remove(filepath)
    return None

def start_los_migration(folder_path,server,tenant,request):
    messages.success(request, f"Migration completed for tenant: {tenant}")
    url=get_url(server)
    headers=get_headers(tenant)
    premadeloans=[]
    file=os.listdir(folder_path)[0]
    filepath=os.path.join(folder_path,file)
    with open(filepath, "r") as f:
        data = json.load(f)
    mydb,cursor=getdb_connection(server,tenant)
    for d in data.keys():
        mydb.reconnect()
        cursor=mydb.cursor()
        print(d)
        external_id=d
        # if external_id !="KFPL1141":
        #     continue
        getclientid=f"select client_id,id from m_loan where external_id='{external_id}'"
        cursor.execute(getclientid)
        result = cursor.fetchall()
        clientid = result[0][0]  # client_id is the first value
        loanid = result[0][1]
        if loanid in premadeloans:
            continue
        else:
            premadeloans.append(loanid)
        
        coappdata=data.get(d).get("Coapplicant")
        guarrdata=data.get(d).get("Guarantor")
        urlfamilymember=url+f"clients/{clientid}/familymembers"
        if len(coappdata)>0:
            for c in coappdata:
                nameparts=c.get("name").split(" ")
                firstname = nameparts[0]
                lastname = nameparts[-1] if len(nameparts) > 1 else "."
                dob=str(c.get("dob"))
                if len(dob)==7:
                    dob="0"+dob
                date_obj = datetime.strptime(dob, "%d%m%Y")
                formatted_dob = date_obj.strftime("%d %B %Y")
                today = datetime.today()
                age = today.year - date_obj.year - ((today.month, today.day) < (date_obj.month, date_obj.day))
                if c.get("Gender")==2:
                    genderid=102
                else:
                    genderid=103
                address=c.get("address").split(" ")
                address_line_1=""
                for a in address[0:int(len(address)//2)]:
                    address_line_1+=a
                address_line_2=""
                for a in address[int(len(address)//2):]:
                    address_line_2+=a
                pincode=c.get("PIN Code")
                pincodeurl=f"https://api.postalpincode.in/pincode/{str(pincode)}"
                responsepincode = requests.request("GET", pincodeurl, headers={}, json={},verify=False)
                if responsepincode.status_code==200:
                    pincodedata=responsepincode.json()[0].get("PostOffice")[0]
                    state=pincodedata.get("State")
                    District=pincodedata.get("District")
                queryforclient=f"select id from m_client where mobile_no={c.get('mobile')}"
                cursor.execute(queryforclient)
                resultclient = cursor.fetchall()
                if resultclient:
                    attachedclientid=resultclient[0][0]
                payload_coapp={
                    "mobileNo": str(c.get("mobile")),
                    "kycData": [],
                    "firstName": firstname,
                    "lastName": lastname,
                    "dateOfBirth": formatted_dob,
                    "age": age,
                    "genderId": genderid,
                    "familyMemberTypeEnum": 1,
                    "isCoApplicant": True,
                    "locale": "en",
                    "dateFormat": "dd MMMM yyyy",
                    "assets": [],
                    "incomes": [],
                    "kyc": [],
                    "liabilities": [],
                    "loanId": str(loanid),
                    "address": [
                        {
                            "country": "India",
                            "addressTypeId": 0,
                            "ownerName": None,
                            "ownerNumber": None,
                            "occupiedSinceYears": None,
                            "occupiedSinceMonths": None,
                            "relationWithApplicant": None,
                            "addressSubTypeId": 1,
                            "addressLine1": address_line_1,
                            "addressLine2": address_line_2,
                            "state": state,
                            "city": District,
                            "district": District,
                            "postalCode": str(pincode),
                            "locale": "en",
                            "dateFormat": "dd MMMM yyyy"
                        }
                    ],
                    "isConsolidate": False
                }
                if resultclient:
                    payload_coapp["attachedClientId"]=attachedclientid
                responsefamilymember = requests.request("POST", urlfamilymember, headers=headers, json=payload_coapp,verify=False)
                if responsefamilymember.status_code==200:
                    print("Coapplicant created successfully")
                else:
                    print("Failed to create Coapplicant")
                    print(responsefamilymember.text)
        if len(guarrdata)>0:
            for c in guarrdata:
                nameparts=c.get("name").split(" ")
                firstname = nameparts[0]
                lastname = nameparts[-1] if len(nameparts) > 1 else "."
                dob=str(c.get("dob"))
                if len(dob)==7:
                    dob="0"+dob
                date_obj = datetime.strptime(dob, "%d%m%Y")
                formatted_dob = date_obj.strftime("%d %B %Y")
                today = datetime.today()
                age = today.year - date_obj.year - ((today.month, today.day) < (date_obj.month, date_obj.day))
                if c.get("Gender")==2:
                    genderid=102
                else:
                    genderid=103
                address=c.get("address").split(" ")
                address_line_1=""
                for a in address[0:int(len(address)//2)]:
                    address_line_1+=a
                address_line_2=""
                for a in address[int(len(address)//2):]:
                    address_line_2+=a
                pincode=c.get("PIN Code")
                pincodeurl=f"https://api.postalpincode.in/pincode/{str(pincode)}"
                responsepincode = requests.request("GET", pincodeurl, headers={}, json={},verify=False)
                if responsepincode.status_code==200:
                    pincodedata=responsepincode.json()[0].get("PostOffice")[0]
                    state=pincodedata.get("State")
                    District=pincodedata.get("District")
                else:
                    print(responsepincode.text)
                payload_guar={
                    "mobileNo": str(c.get("mobile")),
                    "kycData": [],
                    "firstName": firstname,
                    "lastName": lastname,
                    "dateOfBirth": formatted_dob,
                    "age": age,
                    "genderId": genderid,
                    "familyMemberTypeEnum": 1,
                    "isGuarantor": True,
                    "locale": "en",
                    "dateFormat": "dd MMMM yyyy",
                    "assets": [],
                    "incomes": [],
                    "kyc": [],
                    "liabilities": [],
                    "loanId": str(loanid),
                    "address": [
                        {
                            "country": "India",
                            "addressTypeId": 0,
                            "ownerName": None,
                            "ownerNumber": None,
                            "occupiedSinceYears": None,
                            "occupiedSinceMonths": None,
                            "relationWithApplicant": None,
                            "addressSubTypeId": 1,
                            "addressLine1": address_line_1,
                            "addressLine2": address_line_2,
                            "state": state,
                            "city": District,
                            "district": District,
                            "postalCode": str(pincode),
                            "locale": "en",
                            "dateFormat": "dd MMMM yyyy"
                        }
                    ],
                    "isConsolidate": False
                }
                responsefamilymember = requests.request("POST", urlfamilymember, headers=headers, json=payload_guar,verify=False)
                if responsefamilymember.status_code==200:
                    print("Guarantor created successfully")
                else:
                    print("Failed to create Guarantor")
                    print(responsefamilymember.text)
    