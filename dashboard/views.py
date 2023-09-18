from django.shortcuts import render
from django.shortcuts import render,redirect
import csv
from .inferenceModel import ImageToWordModel
from django.contrib.auth import authenticate,login,logout 
from django.contrib.auth.decorators import login_required
import Levenshtein
from django.contrib.auth.models import User
from django.core.files.storage import  default_storage
import pyttsx3
from django.contrib import messages
import cv2
import numpy as np
import imutils
from . import page
from . import words
from PIL import Image
# Create your views here.
from django.http import HttpResponse
from .models import process,HandwritingPerception
from PIL import Image
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
import os
from .forms import userForm
@csrf_exempt
def image_crop_view(request):
    if request.method == 'POST':
        image_file = request.FILES.get('cropped_image')
        if image_file:
            # Save the cropped image
            save_path = 'path/to/save/cropped_image.jpg'
            with open(save_path, 'wb') as f:
                for chunk in image_file.chunks():
                    f.write(chunk)
            return HttpResponse('Cropped image saved successfully.')
    else:
        return render(request, 'image_cropper.html')
@login_required(login_url='login')
def ocrPage(request):
    if request.method == "POST": 
       
       
       
        # Django image API
        #
        file = request.FILES["imageFile"]
        file_name = default_storage.save(file.name, file)
        file_url = default_storage.path(file_name)
        # User input page image 
        image = cv2.cvtColor(cv2.imread(file_url), cv2.COLOR_BGR2RGB)

        # Crop image and get bounding boxes
        crop = page.detection(image)
        boxes = words.detection(crop)
        lines = words.sort_words(boxes)
       
         # Saving the bounded words from the page image in sorted way
        i = 0
        c=0
        for line in lines:
            text = crop.copy()
            for (x1, y1, x2, y2) in line:
                # roi = text[y1:y2, x1:x2]
                save = Image.fromarray(text[y1:y2, x1:x2])
                # print(i)
                save.save("static/persc/segment" + str(i) + ".png")
                i += 1
                c += 1
                print("done")
            
        list=[]
        simdrugs=[]
        acuuracy_list=[]    
        for j in range(c):
                image = cv2.imread(r"static/persc/segment{}.png".format(j))
                # Create an instance of the ImageToWordModel class
                model = ImageToWordModel(model_path="dashboard/Models/08_handwriting_recognition_torch/202303142139/model.onnx")
                # Call the predict method with the input image
                prediction_text = model.predict(image)

                # Print the predicted text
                print(prediction_text)
                #If certified_drugs is a csv file ----------> change the name of the CSV!!!!!!!!!!!!!!!
                # Open the CSV file
                
                with open(r'dashboard/dataSet/dataSet/10K Egypt Medicine + Price.csv', 'r') as csvfile:
                         # Use the csv reader to read the contents of the file
                    reader = csv.reader(csvfile)
                    # Create an empty list to store the drug names
                    certified_drugs = []
                    # Loop over each row in the CSV file
                    for row in reader:
                        # Add the drug name to the list
                        certified_drugs.append(row[0])

                similarity_scores = [(drug, Levenshtein.distance(prediction_text.lower(), drug.lower())) for drug in certified_drugs]
                sorted_scores = sorted(similarity_scores, key=lambda x: x[1])
                most_similar_drug = sorted_scores[0][0]
                if most_similar_drug=="a" or most_similar_drug=="is":
                    continue
           
                missing_characters_count = sum(1 for x, y in zip(prediction_text.lower(), most_similar_drug.lower()) if x != y)
                missing_characters_percentage = (missing_characters_count / len(most_similar_drug)) * 100 if len(most_similar_drug) > 0 else 0
                acuuracy_list.append(missing_characters_percentage)
                perception = HandwritingPerception(
                    input_image=file,
                    output_text=prediction_text,
                    missing_characters_count=missing_characters_count,
                    missing_characters_percentage=missing_characters_percentage
                )
                perception.save()

                list.append(prediction_text)
                simdrugs.append(most_similar_drug)
                print("OCR Output: ",prediction_text)
                print("Most Similar Drug: ", most_similar_drug)      
                # Print the list of drug names
        
        total=0
        k=0
        for acc in acuuracy_list:
           print(acc)
           total=total+int(acc)
           
           k +=1

        total=total/k
        context={
            'Model_Prediction':simdrugs,
            'Simimlariy':simdrugs,
            'crop':crop,
            'boxes':boxes,
            'accurracy':total,
        }
       
    else:  
       return render(request,'main.html')
    return render(request,'main.html',context) 
def voice(request):
    if request.method == 'GET':
        values = request.GET.getlist('inp')
        if values:
            engine = pyttsx3.init()
            for value in values:
                engine.say(value)
            engine.runAndWait()
    return redirect('ocr')
   
def logoutPage(request):
    logout(request)
    messages.info(request, "Logged out successfully!")
    return redirect('login')

def registerPage(request):  
    if request.method=='POST': 
        form = userForm(request.POST)  
        if form.is_valid():  
            form.save() 
            return redirect('home') 
    else:  
        form = userForm()  
    context = {  
        'form':form  
    }  
    return render(request, 'register.html', context)  
def LoginPage(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method=='POST':
       username=request.POST.get('username')
       password=request.POST.get('password')
       try:
          username=User.objects.get(username=username)
       except:
          messages.error(request, "this user dose not exist")
                
       user=authenticate( request, username=username,password=password)
       if user is not None:
           login(request,user)
           return redirect('home')
       else:
        messages.error(request, "the user name or password is not exist")
 
    context={
     
    }
    return render(request,"login.html",context)
@login_required(login_url='login')
def handwriting_dashboard(request):
    perceptions = HandwritingPerception.objects.all()
    sum=0
    J=1
    for i in perceptions:
        sum=sum+int(i.missing_characters_percentage)
        J+=1
    sum=sum/J
    return render(request, 'ocrPage.html', {'perceptions': sum})

