from django.shortcuts import render,redirect,HttpResponse
from . forms import NewUserForm,FileForm,LoginForm,ProfileForm,EmailResetConfirmForm
from .models import User,SharedFiles,DownloadFile,UserFiles
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate,logout
import sweetify
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from datetime import datetime,timedelta
from .tasks import remove_userfile
import json
import io
import os
import zipfile
import mimetypes
from django.core.mail import EmailMultiAlternatives

# Create your views here.

def bad_request(request,exception):
    return render(request,'fileshare/page_400.html',{})

def permission_denied(request, exception=None):
    return render(request,'fileshare/page_403.html',{})

def page_not_found(request,exception):
    return render(request,'fileshare/page_404.html',{})

def server_error(request,exception=None):
    return render(request,'fileshare/page_500.html',{})


def redirect_after_login(request):
    nxt = request.GET.get("next", None)
    if nxt is None:
        return redirect(settings.LOGIN_REDIRECT_URL)
    else:
        return redirect(nxt)

def register(request):
    form=NewUserForm()
    if request.method == 'POST':
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.add_message(request, messages.SUCCESS, 'Thank You to Join Us!')
            return redirect('/login')
        else:
            return render(request, 'fileshare/register.html', {'form': form})
    return render(request,'fileshare/register.html',{'form':form})

def login_request(request):
    if request.method == 'POST':

        form = LoginForm(request.POST)

        if form.is_valid():
            username=form.cleaned_data.get('username')
            password=form.cleaned_data.get('password')
            user=authenticate(username=username,password=password)
            
            if user is not None:
                login(request,user)
                return redirect_after_login(request)
            else:
                print("<<<<")
                # sweetify.error(request, "Please Enter Password and Email/Username Doesn't Match!", persistent=':(')
                messages.add_message(request, messages.ERROR, "Please Enter Password and Email/Username Doesn't Match!")
            # else:
            #     sweetify.error(request, "Please Enter Password and Email/Username Doesn't Match!", persistent=':(')
                # messages.add_message(request, messages.ERROR, "Please Enter Password and Email/Username Doesn't Match!")
        else:
            print("<<<<1111111",form.data,form.errors)

            # sweetify.error(request, "Please Enter Valid Credentials", persistent=':(')
            messages.add_message(request, messages.ERROR, "Please Enter Valid Credentials")
    form = LoginForm()
    return render(request,'fileshare/login.html')

@login_required
def logout_request(request):
    logout(request)
    # sweetify.info(request, 'Logged out successfully!', button='Ok', timer=3000)
    messages.info(request, "Logged out successfully!")
    return redirect("/")

@login_required
def update_profile(request):
    total_users_files=UserFiles.objects.filter(user=request.user)
    total_shared_with_user_files=UserFiles.objects.filter(sharedfiles__email_to=request.user.email).distinct()


    if request.method == 'POST':

        profile_form = ProfileForm(request.POST,request.FILES, instance=request.user.profile)
        if profile_form.is_valid():
            profile_form.save()
            messages.add_message(request,messages.SUCCESS,'Your profile was successfully updated!')
            return render(request, 'fileshare/update_profile_form.html', {'profile_form': profile_form})
        else:
            messages.add_message(request,messages.ERROR,'Please Validate Your Entered Data')

            # sweetify.error(request, 'Please Add Valid Data', persistent=':(')
    else:
        profile_form = ProfileForm(instance=request.user.profile)
        print('total_users_files',total_users_files.count(),'total_shared_with_user_files',total_shared_with_user_files.count())

        return render(request, 'fileshare/update_profile_form.html', {
            'profile_form': profile_form,
            'total_users_files':total_users_files,
            'total_shared_with_user_files':total_shared_with_user_files
        })
    return render(request, 'fileshare/update_profile_form.html', {
        'profile_form': profile_form,
        'total_users_files':total_users_files,
        'total_shared_with_user_files':total_shared_with_user_files
    })

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.add_message(request,messages.SUCCESS, 'Your password was successfully updated!')
            return redirect('change_password')
        # else:
        #     messages.add_message(request,messages.ERROR, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'fileshare/change_password.html', {'form': form})


@login_required
def home(request):
    if request.POST:
        form = FileForm(request.POST, request.FILES)
        if form.is_valid():
            my_files = request.FILES
            title=request.POST.get('title',False)

            if not title:
                for file in my_files:
                    uploaded_file = my_files.get(file)
                    title = uploaded_file.name and uploaded_file.name.split('.')[0]

            message = request.POST.get('message',False)

            userfiles=UserFiles(title=title,message=message)
            userfiles.user=request.user
            userfiles.save()
            #-----------task create---------------------------#
            date_auto_delete=datetime.utcnow() + timedelta(days=1)
            remove_userfile.apply_async((userfiles.id,), eta=date_auto_delete)
            #------------------task in queue -------------------#

            for file in my_files:
                uploaded_file = my_files.get(file)
                file_name=uploaded_file.name
                is_image = False
                if file_name.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):
                    is_image=True
                current_document=DownloadFile(userfile=userfiles,uploads=uploaded_file,file_name=file_name,is_image=is_image)
                current_document.save()
            # email_with_attachment(userfiles.unique_file_num)
            # sweetify.success(request, 'Your File has been Saved Successfully')

            return HttpResponse(json.dumps({'new_created': str(userfiles.unique_file_num)}), content_type="application/json")

        else:
            # sweetify.info(request, 'Please enter valid Files', button='Ok', timer=3000)
            return HttpResponse(json.dumps({'errors': str(form.errors)}), content_type="application/json")
    else:
        form = FileForm()
    return render(request,'fileshare/home.html', {'form':form})

@login_required
def success_uploaded_file(request,unique_file_num):
    last_uploaded=UserFiles.objects.get(unique_file_num=unique_file_num)
    messages.add_message(request, messages.SUCCESS, 'Your File has been Saved Successfully')
    return render(request,'fileshare/success_uploaded_file.html',{'last_uploaded':last_uploaded})


def send_attachment(request,unique_file_num):
    all_files_obj = UserFiles.objects.filter(unique_file_num=unique_file_num).first()
    subject = 'File Has Been Shared with you'
    text_content = all_files_obj.message if all_files_obj.message else 'This File has been shared by '+all_files_obj.user.username

    path=request.scheme+"://"+request.get_host()+"/download/file/"+str(all_files_obj.unique_file_num)+'/download'
    html_content = '<p>'+text_content+'</p></br>'\
        +'<p>Please Click on the link below to Download File</p><br/><br/><p> '\
        +'<a href="'+ path +'">'+path+'</a></p>'
    from_email = request.user.email
    to_email = [email[0] for email in all_files_obj.sharedfiles_set.values_list('email_to')]
    mail = EmailMultiAlternatives(
        subject,
        text_content,
        from_email,
        to_email,
    )

    mail.attach_alternative(html_content, "text/html")
    email_res = mail.send()
    return HttpResponse(email_res)

def multifile_viewer(request,unique_file_num):
    userfiles_obj=UserFiles.objects.filter(unique_file_num=unique_file_num).first()
    any_image=any([userfile['is_image'] for userfile in userfiles_obj.downloadfile_set.values('is_image') if userfile])

    return render(request,'fileshare/multifile_viewer.html',{'userfiles_obj':userfiles_obj,'any_image':any_image})

def download_single_file(request,doc_num):
    # fill these variables with real values
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    current_document=DownloadFile.objects.filter(unique_id=doc_num).first()
    fl_path =BASE_DIR + current_document.uploads.url
    filename = current_document.file_name

    fl = open(fl_path, 'rb')

    mime_type, _ = mimetypes.guess_type(fl_path)
    response = HttpResponse(fl, content_type=mime_type)
    response['Content-Disposition'] = "attachment; filename=%s" % filename
    return response

def download_file(request,unique_file_num):
    zip_io = io.BytesIO()
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    all_files_obj=UserFiles.objects.filter(unique_file_num=unique_file_num).first()
    list_files=[]
    for current_document in all_files_obj.downloadfile_set.iterator():
        fl_path =BASE_DIR + current_document.uploads.url
        list_files.append(fl_path)
    filename = all_files_obj.title
    with zipfile.ZipFile(zip_io, mode='w', compression=zipfile.ZIP_DEFLATED) as backup_zip:
        for file in list_files:
            orignal_file=file
            file = file.encode('ascii')  # convert path to ascii for ZipFile Method
            if os.path.isfile(file):
                (filepath, file_name) = os.path.split(file)
                backup_zip.write(orignal_file, file_name.decode(), zipfile.ZIP_DEFLATED)

    response = HttpResponse(zip_io.getvalue(), content_type='application/x-zip-compressed')
    response['Content-Disposition'] = 'attachment; filename=%s' % filename + ".zip"
    response['Content-Length'] = zip_io.tell()
    return response


@login_required
def delete_file(request,unique_file_num):
    userfiles=UserFiles.objects.filter(unique_file_num=unique_file_num)
    userfiles.delete()
    messages.add_message(request, messages.SUCCESS, 'Your File has been Removed Successfully')
    return redirect('users_files')

# @login_required
# def delete_single_file(request,uuid_id):
#     download_file=DownloadFile.objects.get(unique_id=uuid_id)
#     if download_file.userfile and download_file.userfile.downloadfile_set.count() <= 1:
#         download_file.userfile.delete()
#         messages.add_message(request, messages.SUCCESS, 'Your File has been Removed Successfully')

#         return redirect('/history/gallery')

#     else:
#         download_file.delete()
#     return redirect('/history/gallery')

@login_required
def users_files(request):
    userfiles=UserFiles.objects.filter(user=request.user).distinct()
    return render(request,'fileshare/users_files.html',{'userfiles':userfiles})

@login_required
def file_shared_with_user(request):
    userfiles=UserFiles.objects.filter(sharedfiles__email_to=request.user.email).distinct()
    return render(request,'fileshare/file_shared_with_user.html',{'userfiles':userfiles})

@login_required
def share_via_email(request):
    if request.POST:
        all_emails=[v for k, v in request.POST.items() if k.startswith('email_to') and v[0].strip() != '']
        user_file_id=request.POST.get('user_file_id')
        old_obj=UserFiles.objects.get(unique_file_num=user_file_id)

        for single_email in all_emails:
            shared_file=SharedFiles(user_email=request.user.email,email_to=single_email,userfile=old_obj)
            shared_file.save()
        send_attachment(request,old_obj.unique_file_num)
    messages.add_message(request, messages.SUCCESS, 'Your File has been shared Successfully')
    return redirect('users_files')


######### youtube