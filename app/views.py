from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate, login
from .forms import AppUserForm, LoginForm, FileUploadForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.contrib import messages
from .handler.losmigrationhandler import *
from .handler.SOP_Automation_Handler.main import *
import mysql.connector
import os
import json
import pandas as pd   
from django.http import JsonResponse
from django.http import HttpResponse
from django.conf import settings
from traits.trait_types import false

# Login view accessible without login
def login_view(request):
    
    request.session['loggedin']=False
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                next_url = request.GET.get('next', 'tasks')
                request.session['loggedin'] = True
                return redirect(next_url)
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid form submission. Please check the form fields.")
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})

# Apply the login_required decorator to these views

def tasks(request):
    if not request.session.get('loggedin'):
        return redirect('login')
    else:
        return render(request, 'tasks.html')


def losmigration(request):
    if not request.session.get('loggedin'):
        # If the user hasn't visited step1, redirect them back to step1
        return redirect('login')
    else:
        return render(request, 'losmigrationpage.html')


def create_user(request):
    if not request.session.get('loggedin'):
        # If the user hasn't visited step1, redirect them back to step1
        return redirect('login')
    if request.method == 'POST':
        form = AppUserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.password = make_password(user.password)
            user.save()
            return redirect('success')
    else:
        form = AppUserForm()
    return render(request, 'create_user.html', {'form': form})

def success(request):
    if not request.session.get('loggedin'):
        # If the user hasn't visited step1, redirect them back to step1
        return redirect('login')
    return render(request, 'success.html')

# Losmigration page with file upload functionality, also protected by login_required

def handle_file_upload(request):
    """Handles the file upload and returns the result."""
    uploaded_file = request.FILES['file']
    
    if not uploaded_file.name.endswith('.xlsx'):
        messages.error(request, "Please upload an Excel file.")
        return None

    fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'uploads'))
    filename = fs.save(uploaded_file.name, uploaded_file)
    return filename

def convert_excel_to_json(folderpath):
    """Converts all Excel files in the folder to JSON format."""
    excel_files = [f for f in os.listdir(folderpath) if f.endswith('.xlsx')]
    if not excel_files:
        return "No Excel files found to convert."

    for excel_file in excel_files:
        excel_file_path = os.path.join(folderpath, excel_file)
        try:
            df = pd.read_excel(excel_file_path)
        except Exception as e:
            return f"Error reading file '{excel_file}': {str(e)}"
        
        json_file_path = os.path.join(folderpath, f'{excel_file.replace(".xlsx", "")}.json')
        df.to_json(json_file_path, orient='records', lines=True)
        os.remove(excel_file_path)
    
    return None
def get_tenants_for_server(server):
    """Fetch tenants from the database based on the selected server."""
    tenants = []
    
    if server:
        try:
            # Connect to the database based on the selected server
            mydb = mysql.connector.connect(
                host=server,
                database='fineract_tenants',
                user='root',
                password='root'
            )
            cursor = mydb.cursor()

            # Fetch tenants from the database
            cursor.execute("SELECT id, identifier FROM tenants")  # Assuming you want 'identifier' and 'name'
            tenants_data = cursor.fetchall()  # This will return all rows in the query result
            
            # Format the tenants data into a list of dictionaries
            tenants = [{'id': tenant[0], 'name': tenant[1]} for tenant in tenants_data]
            cursor.close()
            mydb.close()
        
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            return []

    return tenants

def losmigration_view(request):
    """Main view for handling file uploads and server/tenant selection."""
    if not request.session.get('loggedin'):
        return redirect('login')

    uploaded_file = None
    tenants = []
    selected_server = request.session.get('selected_server', None)
    selected_tenant = request.session.get('selected_tenant', None)
    form = FileUploadForm() 

    if request.method == 'POST':
        if 'file' in request.FILES:
            # Handle file upload
            form = FileUploadForm(request.POST, request.FILES)
            if form.is_valid():
                uploaded_file=handle_file_upload(request)
                process_excel(os.path.join(settings.MEDIA_ROOT, 'uploads'))
                messages.success(request, 'File uploaded successfully.')
        elif 'server' in request.POST:
            selected_server = request.POST.get('server')
            request.session['selected_server'] = selected_server 
            tenants = get_tenants_for_server(selected_server)
            messages.success(request, f"Tenants fetched for server: {selected_server}")
        
        elif 'los_migration_start' in request.POST:
            selected_tenant = request.POST.get('tenant')
            request.session['selected_tenant'] = selected_tenant  
            start_los_migration(os.path.join(settings.MEDIA_ROOT, 'uploads'),selected_server, selected_tenant,request)
            messages.success(request, f"Migration completed for tenant: {selected_tenant}")
            
        else:
            form = FileUploadForm()
    
    else:
        form = FileUploadForm()
    output_body={
        'form': form,
    }
    if uploaded_file:
        output_body['uploaded_file'] = uploaded_file
    if tenants:
        output_body['tenants'] = tenants
    if selected_server:
        output_body['selected_server'] = selected_server
    return render(request, 'losmigrationpage.html',output_body)
def get_tenants(request):
    server_type = request.GET.get('server_type')
    server = request.GET.get('server')

    tenants = get_tenants_for_server(server)
    
    return JsonResponse({'tenants': [tenant["name"] for tenant in tenants]})
def sopauomation(request):
    if not request.session.get('loggedin'):
        return redirect('login')
    
    source_tenants = []
    selected_source_server = None
    destination_tenants=[]
    selected_destination_server=None
    if request.method == 'POST':
        if 'source-server' in request.POST:
            selected_source_server = request.POST.get('source-server')
            if selected_source_server:
                # Store selected server in session
                request.session['selected_source_server'] = selected_source_server
                source_tenants = get_tenants_for_server(selected_source_server)
                messages.success(request, f"Tenants fetched for server: {selected_source_server}")
        if 'destinaion-server' in request.POST:
            selected_destination_server = request.POST.get('destinaion-server')
            if selected_destination_server:
                # Store selected server in session
                request.session['selected_destination_server'] = selected_destination_server
                destination_tenants = get_tenants_for_server(selected_destination_server)
                messages.success(request, f"Destination server selected: {selected_destination_server}")
        if "start-sop-automation" in request.POST:
            source_tenant = request.POST.get('source-tenant')
            source_server = request.POST.get('source-server')
            destination_server = request.POST.get('destinaion-server')
            destination_tenant = request.POST.get('destinaion-tenant')
            print(source_tenant, source_server, destination_server,destination_tenant)
            messages.success(request, f"SOP automation started from {source_server} to {destination_server}")
            sopautomationbegin(source_server,source_tenant,destination_server,destination_tenant)
    output_body = {
        'source_tenants': source_tenants,
        'selected_source_server': selected_source_server,
        'selected_destination_server':selected_destination_server,
        'destination_tenants': destination_tenants
    }
    
    return render(request, 'sopautomation.html', output_body)