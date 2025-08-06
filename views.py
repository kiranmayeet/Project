from django.shortcuts import render,redirect
from . models import *
from django.contrib import messages
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from .models import UsersModel
import os
from .aes import *
from django.http import HttpResponse
from django.conf import settings
from django.core.mail import send_mail
import random
import re
from datetime import datetime
from django.core.files.storage import FileSystemStorage

def is_strong_password(password):
    """
    Validate password:
    - At least 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character
    """
    
    pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{8,}$'
    return re.match(pattern, password)

def calculate_age(dob_str):
    dob = datetime.strptime(dob_str, "%Y-%m-%d")
    today = datetime.today()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

def index(request):  
    return render(request, 'index.html')

def register(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        dob = request.POST.get('dob')
        gender = request.POST.get('gender')
        #contact = request.POST.get('contact')
        #address = request.POST.get('address')
        profile_file = request.FILES.get('profile')

        if not is_strong_password(password):
            messages.error(request, 'Password must be at least 8 characters long and include uppercase, lowercase, number, and special character.')
            return redirect('register')
        
        age = calculate_age(dob)
        if age < 18:
            messages.error(request, 'You must be at least 18 years old to register.')
            return redirect('register')
        
        if profile_file:
            static_user_dir = os.path.join(settings.BASE_DIR, 'static', 'userprofiles')
            os.makedirs(static_user_dir, exist_ok=True)  # Ensure directory exists
            fs = FileSystemStorage(location=static_user_dir)
            filename = fs.save(profile_file.name, profile_file)
            profile_path = f'static/userprofiles/{filename}'
        else:
            profile_path = ''  # or some default path

        request.session['name'] = name
        request.session['Remail'] = email
        request.session['password'] = password
        request.session['dob'] = dob
        request.session['gender'] = gender
        #request.session['contact'] = contact
        #request.session['address'] = address
        request.session['profile_path'] = profile_path  # Only the path, not the file

        return redirect('otpRegistration', mail=email)

    return render(request, 'register.html')


def deletefile(request, cloud_id):
    data = A_Cloud.objects.get(id=cloud_id)
    data.delete()
    return redirect('viewfile')

# def delete_user(request, user_id):
#     if request.user.is_superuser or request.user.is_staff:  # optional: restrict to admin users
#         user = get_object_or_404(UsersModel, id=user_id)
#         user.delete()
#         messages.success(request, "User has been deleted successfully.")
#     else:
#         messages.error(request, "You do not have permission to delete users.")
#     return redirect('viewusers')

def delete_user(request, user_id):
    user = get_object_or_404(UsersModel, id=user_id)
    user.delete()
    messages.success(request, "User has been deleted successfully.")
    return redirect('viewusers')


def otpRegistration(request, mail):
    print('----------------', mail)
    
    otp_session = request.session.get('email_otp')
    
    if otp_session:
        print(f"OTP already sent: {otp_session}")
    else:
        otp = str(random.randint(100000, 999999))
        request.session['email_otp'] = otp
        request.session['otp_email'] = mail
        
        subject = 'Your OTP Code'
        message = f'Your OTP for registration is: {otp}'
        recipient_list = [mail]
        send_mail(subject, message, settings.EMAIL_HOST_USER, recipient_list, fail_silently=False)
        print('OTP Sent:', otp)
    
    if request.method == 'POST':
        otp_input = request.POST.get('otp')
        name = request.session['name'] 
        email = request.session['Remail'] 
        password = request.session['password'] 
        dob = request.session['dob'] 
        gender = request.session['gender']
        profile = request.session['profile_path'] 

        if otp_input != otp_session:
            messages.error(request, 'Invalid email or OTP.')
            return redirect('register')

        if UsersModel.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
            return redirect('register')

        UsersModel.objects.create(
            name=name, email=email, password=password,
            dob=dob, gender=gender, profile=profile
        )

        messages.success(request, 'Registration successful!')
        request.session.pop('email_otp', None)
        request.session.pop('otp_email', None)
        request.session.pop('name', None)
        request.session.pop('Remail', None)
        request.session.pop('password', None)
        request.session.pop('dob', None)
        request.session.pop('gender', None)
        request.session.pop('profile_path', None)

        return redirect('register')
    if UsersModel.objects.filter(email=mail).exists():
        messages.error(request, 'Email already exists.')
        return redirect('register')   

    return render(request, 'otp.html', {'mail': mail})


def resend_otp(request, mail):
    otp_session = request.session.get('email_otp')

    if otp_session:
        otp = otp_session
    else:
        otp = str(random.randint(100000, 999999))
        request.session['email_otp'] = otp
        request.session['otp_email'] = mail
    
    subject = 'Your OTP Code'
    message = f'Your OTP for registration is: {otp}'
    recipient_list = [mail]
    send_mail(subject, message, settings.EMAIL_HOST_USER, recipient_list, fail_silently=False)
    
    return redirect('otpRegistration', mail=mail)

def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        if UsersModel.objects.filter(email=email,status='pending').exists():
            messages.error(request, 'Admin Not Accepted Your Registration')
            return redirect('login')
        data = UsersModel.objects.filter(email=email, password=password).exists()
        if data:
            request.session['email']=email
            request.session['login']='user'
            return redirect('home')
        else:
            messages.success(request, 'Invalid Email or Password')
            return redirect('login')
    return render(request, 'login.html')

def cloudlogin(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        print(email,password)
        if email == 'admin@gmail.com' and password == 'admin':
            request.session['login'] = 'cloud'
            return redirect('home')
        else:
            messages.error(request, 'Invalid Credentials')
            return redirect('cloudlogin')
    return render(request, 'cloudlogin.html')



def home(request):
    login = request.session['login']
    return render(request, 'home.html',{'login':login})

def logout(request):
    del request.session['login']
    return redirect('index')

def viewusers(request):
    users = UsersModel.objects.all()
    login =request.session['login']
    return render(request, 'viewusers.html',{'data':users,'login':login})

def authorize(request,id):
    users = UsersModel.objects.get(id=id)
    login =request.session['login']
    users.status='Authorized'
    users.save()
    messages.success(request, 'User Authorized Sucessfully!')
    return redirect('viewusers')

def unauthorize(request,id):
    users = UsersModel.objects.get(id=id)
    login =request.session['login']
    users.status='Un Authorized'
    users.save()
    messages.success(request, 'User Un Authorized Sucessfully!')
    return redirect('viewusers')

def uploadfile(request):
    if request.method == 'POST':
        filename = request.POST['filename']
        file = request.FILES['file']
        
        temp_file_path = os.path.join('static', 'EncryptedFiles', file.name)
        with open(temp_file_path, 'wb') as temp_file:
            for chunk in file.chunks():
                temp_file.write(chunk)

        with open(temp_file_path, 'r') as f:
            message = f.read()
        
        
        key = get_random_bytes(16) 
        encrypted_message = encrypt_AES(message, key)
        with open(temp_file_path, 'wb') as f:
            f.write(encrypted_message)
    
        data = encrypted_message.hex()
        l = len(data)
        encmsg1 = data[:l//2]
        encmsg2 = data[l//2:]

        
        ca = A_Cloud(
            email=request.session['email'],
            filename=filename,
            key=key,
            filedata=encmsg1,  
            file=temp_file_path
        )
        ca.save()
        cadata = A_Cloud.objects.get(id=ca.id)
        cb = B_Cloud(
            cloud = cadata,
            filedata = encmsg2

        )
        cb.save()

        messages.success(request, 'File Uploaded and Encrypted Successfully')
        return redirect('uploadfile')
    
    login = request.session.get('login', '')
    return render(request, 'uploadfile.html', {'login': login})


def viewfile(request):
    # RequestFileModel.objects.all().delete()
    login = request.session['login']
    email = request.session['email']
    data = B_Cloud.objects.filter(cloud__email=email)
    return render(request, 'viewfiles.html', {'login': login,'data':data,'email':email})



def viewdecryptedfile(request):
    login = request.session['login']
    email = request.session['email']
    data = DecryptModel.objects.filter(data__cloud__email=email)
    return render(request, 'decryptedfiles.html', {'login': login,'data':data})


def decryptfile(request,id):
    email =request.session['email']
    cbdata = B_Cloud.objects.get(id=id)
    if DecryptModel.objects.filter(data=cbdata).exists():
        messages.success(request, 'File Decrypyted already sent')
        return redirect('viewfile')
    else:
        # file = FilesUploadModel.objects.get(id=id)

        msg1 = bytes.fromhex(cbdata.cloud.filedata)
        msg2 = bytes.fromhex(cbdata.filedata)
        msg = msg1+msg2
        decrypted_message = decrypt_AES(msg, cbdata.cloud.key)

        DecryptModel.objects.create(
            data = cbdata,
            decrypted_data = decrypted_message
            ).save()
        messages.success(request, 'File Decrypted  Successfully!')
        return redirect('viewfile')


def download(request, id):
    
    context = DecryptModel.objects.get(id=id)

    plain_data = context.decrypted_data  # e.g., "Hello, this is the decrypted message."
    file_name = context.data.cloud.filename.split('/')[-1]  # e.g., "message.txt"

    response = HttpResponse(plain_data, content_type='text/plain')
    response['Content-Disposition'] = f'attachment; filename="{file_name}"'

    return response




def viewallfiles(request):
    login=request.session['login']
    data = B_Cloud.objects.all()
    return render(request, 'viewallfiles.html',{'login':login,'data':data})

def user_profile(request, ):
    login = request.session['login']
    email = request.session['email']
    user = get_object_or_404(UsersModel, email=email)
    return render(request, 'profile.html', {'user': user, 'login':login, 'email':email})

def update_profile(request):
    login = request.session['login']
    email = request.session['email']
    user = get_object_or_404(UsersModel, email=email)
    
    if request.method == 'POST':
        user.name = request.POST.get('name')
        user.email = request.POST.get('email')
        user.dob = request.POST.get('dob')
        user.gender = request.POST.get('gender')
        
        if 'profile' in request.FILES:
            user.profile = request.FILES['profile']
        
        user.save()
        return redirect('user_profile')

    return render(request, 'update_profile.html', {'user': user, 'login':login, 'email':email})
