# main.py
from .apis.configuration_api import *
from .apis.rolesandpermission_api import *
from .apis.codeandcodevalues_api import *
from .apis.actiongroups_api import *
from .apis.datatables_api import *
from .apis.sop_api import *
from .apis.kycpack_api import *
from .utils import *

# file_path = r'D:\SOP AUTOMATION\dbconnection.txt'

def sopautomationbegin(source_server,source_tenant,destination_server,destination_tenant):
    write_to_dbconn(destination_server,destination_tenant)
    write_from_dbconn(source_server,source_tenant)
    headers = read_headers_from_file("headers.txt",destination_tenant)
    update_configuration_family_member_option(headers)
    enable_configuration_family_member_option(headers)
    enable_configuration_loan_entity(headers)
    roles_dict=create_roles(headers)
    m_permission()
    m_role_permission(roles_dict)
    m_code()
    m_code_value()
    action_groups(headers,roles_dict)
    data_tables()
    sop()
    kyc_pack()
    update_datables()
# if __name__ == "__main__":
#     main("UAT","ss","localhost","uyuy")
