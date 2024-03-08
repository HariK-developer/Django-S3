# views.py
from django.shortcuts import render
from django.http import HttpResponseRedirect
from .forms import UploadFileForm
import boto3
from botocore.exceptions import NoCredentialsError
from django.conf import settings

def success_view(request, file_name):
    # Get the S3 file URL with the desired content type
    s3_file_url = get_s3_file_url(file_name, content_type='image/jpeg')

    return render(request, 'success.html', {'s3_file_url': s3_file_url, 'file_name': file_name})

def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            # Access the file name
            file_name = request.FILES['file'].name

            # Process the uploaded file
            handle_uploaded_file(request.FILES['file'], file_name)

            # Redirect to the success view with the file name
            return HttpResponseRedirect(f'/success/{file_name}/')
    else:
        form = UploadFileForm()

    return render(request, 'upload_file.html', {'form': form})

def handle_uploaded_file(file, file_name):
    # Save the file to S3
    s3 = boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME,
    )

    try:
        s3.upload_fileobj(file, settings.AWS_STORAGE_BUCKET_NAME, file_name)
    except NoCredentialsError:
        print("Credentials not available")

def display_uploaded_file(request, file_name):
    s3_file_url = get_s3_file_url(file_name)

    if s3_file_url:
        return render(request, "display_file.html", {"s3_file_url": s3_file_url})
    else:
        return render(request, "file_not_found.html")

def get_s3_file_url(file_name, content_type=None):
    s3 = boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME,
    )

    try:
        response = s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": settings.AWS_STORAGE_BUCKET_NAME, "Key": file_name, 'ResponseContentType': content_type},
            ExpiresIn=3600,
        )  # URL expiration time in seconds
        return response
    except NoCredentialsError:
        print("Credentials not available")
        return None
