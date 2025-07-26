# predictor/views.py

import os
import numpy as np
from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages

from tensorflow.keras.models import load_model
from tensorflow.keras.applications.resnet50 import preprocess_input, decode_predictions
from tensorflow.keras.preprocessing import image

from .models import PredictionRecord

# Load the model (make sure the model path is correct)
model_path = os.path.join(os.path.dirname(__file__), 'model', 'resnet50_model')
model = load_model(model_path)

# ------------------- Prediction View -------------------

@login_required
def predict_image(request):
    if request.method == 'POST' and request.FILES['image']:
        img_file = request.FILES['image']
        fs = FileSystemStorage()
        file_path = fs.save(img_file.name, img_file)
        full_path = fs.path(file_path)

        # Load and preprocess image
        img = image.load_img(full_path, target_size=(224, 224))
        x = image.img_to_array(img)
        x = np.expand_dims(x, axis=0)
        x = preprocess_input(x)

        # Predict
        preds = model.predict(x)
        results = decode_predictions(preds, top=3)[0]

        # Save result to database
        top_result = ', '.join([f"{label} ({prob:.2f})" for (_, label, prob) in results])
        PredictionRecord.objects.create(
            user=request.user,
            image=file_path,
            prediction=top_result
        )

        return render(request, 'predictor/result.html', {
            'results': results,
            'image_url': fs.url(file_path)
        })

    return render(request, 'predictor/upload.html')

# ------------------- Auth System -------------------

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
        else:
            User.objects.create_user(username=username, password=password)
            messages.success(request, 'Registration successful. Please login.')
            return redirect('login')
    return render(request, 'predictor/register.html')


def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('predict')
        else:
            messages.error(request, 'Invalid credentials')
    return render(request, 'predictor/login.html')


def user_logout(request):
    logout(request)
    return redirect('login')

# ------------------- Admin Dashboard -------------------

def is_admin(user):
    return user.is_superuser


@user_passes_test(is_admin)
def dashboard(request):
    users = User.objects.all()
    return render(request, 'predictor/dashboard.html', {'users': users})

def home(request):
    return render(request, 'predictor/home.html')