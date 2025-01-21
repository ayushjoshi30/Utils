from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate, login
from .forms import AppUserForm, LoginForm, FileUploadForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.contrib import messages
import os
import json
import pandas as pd   
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
def losmigration_view(request):
    if not request.session.get('loggedin'):
        return redirect('login')
    
    uploaded_file = None  # Default value if no file is uploaded
    print(request)
    if request.method == 'POST':
        # Handle file upload
        form = FileUploadForm(request.POST, request.FILES)

        if 'file' in request.FILES:  # Check if file is uploaded
            if form.is_valid():
                uploaded_file = request.FILES['file']
                if not uploaded_file.name.endswith('.xlsx'):
                    messages.error(request, "Please upload an Excel file.")
                    return render(request, 'losmigrationpage.html', {'form': form})

                fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'uploads'))
                filename = fs.save(uploaded_file.name, uploaded_file)
                file_url = fs.url(filename)

                # Add a success message for file upload
                messages.success(request, f"File '{filename}' uploaded successfully!")

                return render(request, 'losmigrationpage.html', {'form': form, 'uploaded_file': True})

        elif 'convert_to_json' in request.POST:  # Handle conversion to JSON if the button is pressed
            folderpath = os.path.join(settings.MEDIA_ROOT, 'uploads')
            excel_files = [f for f in os.listdir(folderpath) if f.endswith('.xlsx')]
            if not excel_files:
                messages.error(request, "No Excel files found to convert.")
                return render(request, 'losmigrationpage.html', {'form': form})
            # Process each Excel file
            for excel_file in excel_files:
                excel_file_path = os.path.join(folderpath, excel_file)
                # Read the Excel file using pandas
                try:
                    df = pd.read_excel(excel_file_path)
                except Exception as e:
                    messages.error(request, f"Error reading file '{excel_file}': {str(e)}")
                    os.remove(excel_file_path)
                    return redirect('losmigration')
                json_file_path = os.path.join(folderpath, f'{excel_file.replace(".xlsx", "")}.json')
                df.to_json(json_file_path, orient='records', lines=True)
                os.remove(excel_file_path)
            messages.success(request,"Format is correct")
            return redirect('losmigration')  # Redirect after conversion to the same page or another page

    else:
        form = FileUploadForm()

    return render(request, 'losmigrationpage.html', {'form': form, 'uploaded_file': uploaded_file})