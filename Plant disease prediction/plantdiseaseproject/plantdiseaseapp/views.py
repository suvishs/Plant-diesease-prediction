from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth.models import User, auth
import tensorflow as tf
import numpy as np
import cv2
import matplotlib.pyplot as plt
from django.core.files.storage import default_storage
import base64
import tempfile

# Create your views here.

def login_view(request):
    if request.method == 'POST':
        username=request.POST['username']
        password=request.POST['password']
        user=auth.authenticate(username=username,password=password)
        if user is not None:
            auth.login(request,user)
            return redirect('home')
        else:
            return redirect('/')
    return render(request, 'login_view.html')

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirmpassword = request.POST.get('confirm_password')

        if password == confirmpassword:
            if User.objects.filter(username=username).exists():
                return redirect(register)
            else:
                user = User.objects.create_user(username=username, password=password)
                user.save()
                return redirect('/')
        else:
            return redirect('register')

    return render(request,'register.html')

def home(request):
    return render(request, 'home.html')


def result(request):
    if request.method == 'POST':

        # Load the saved model
        model = tf.keras.models.load_model('PlantDNet.h5')

        # Define the classes for the model

        classes = ['Pepper__bell___Bacterial_spot', 'Pepper__bell___healthy',
                'Potato___Early_blight', 'Potato___Late_blight', 'Potato___healthy',
                'Tomato_Bacterial_spot', 'Tomato_Early_blight', 'Tomato_Late_blight',
                'Tomato_Leaf_Mold', 'Tomato_Septoria_leaf_spot', 'Tomato_Spider_mites_Two_spotted_spider_mite',
                'Tomato__Target_Spot', 'Tomato__Tomato_YellowLeaf__Curl_Virus', 'Tomato__Tomato_mosaic_virus',
                'Tomato_healthy']

        # Function to preprocess the image
        def process_image(image):
            image = cv2.resize(image, (64, 64))
            # image = cv2.resize(image, (256, 256))
            image = np.array(image, dtype=np.float32)
            image /= 255.0
            image = np.expand_dims(image, axis=0)
            return image
        
        if 'my_file' not in request.FILES:
            return HttpResponse("No file was uploaded.")

        # Get the image file from Django request and preprocess it
        uploaded_file = request.FILES['my_file']
        image = cv2.imdecode(np.fromstring(uploaded_file.read(), np.uint8), cv2.IMREAD_COLOR)
        processed_image = process_image(image)

        temp_file = tempfile.NamedTemporaryFile(delete=False)
        with open(temp_file.name, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)

        # Open the saved image and read its contents as binary data
        with open(temp_file.name, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')


        # Make a prediction with the model
        prediction = model.predict(processed_image)[0]

        # Get the index of the highest confidence class
        predicted_class_index = np.argmax(prediction)

        # Get the name of the predicted class
        predicted_class_name = classes[predicted_class_index]

        # Get the confidence score for the predicted class
        confidence_score = prediction[predicted_class_index]

        # Print the result
        print(f"The image is a {predicted_class_name} leaf with a confidence of {confidence_score:.2f}.")

        return render(request, 'result.html',{'predicted_class_name':predicted_class_name, 'confidence_score':confidence_score, 'image_data':image_data})

    return render(request, 'result.html')