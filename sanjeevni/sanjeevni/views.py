from django.shortcuts import render
import pyrebase
from django.contrib import auth
from django.http import JsonResponse
import re
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
import time



firebaseConfig = {
"apiKey": "AIzaSyDMicSpS3XgbDU5dkmcOpiRIgx6CFUY0rQ",
  "authDomain": "dev-sanjeevni.firebaseapp.com",
  "databaseURL": "https://dev-sanjeevni.firebaseio.com",
  "projectId": "dev-sanjeevni",
  "storageBucket": "dev-sanjeevni.appspot.com",
  "messagingSenderId": "235860833440",
  "appId": "1:235860833440:web:c651ac4051082af9ccc5c5",
  "measurementId": "G-D15TTT5LR2"
  }

firebase = pyrebase.initialize_app(firebaseConfig)

authentication = firebase.auth()
database = firebase.database()

def signIn(request):
    return render(request, "signIn.html")

def postsign(request):
    email = request.POST.get('email')
    password = request.POST.get('password')

    try:
      user = authentication.sign_in_with_email_and_password(email, password)
      message = "OK"  
      code = 200
      print(user)
      session_id=user['idToken']
      request.session['uid'] = str(session_id)

      return render(request, "welcome.html", {"email":email, "message":message, "code":code})

    except:
      message = "Invalid Credentials"
      code = 404
      return render(request, "signIn.html", {"email":email, "message":message, "code":code})

def postsignup(request):
  name = request.POST.get('name')
  email = request.POST.get('email')
  password = request.POST.get('password')
  cpassword = request.POST.get('cpassword') # ! serverside validation 
  try:
    if str(password) == str(cpassword):
      if len(str(name)) > 3:
        regex = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'
        if re.search(regex, str(email)):
          user = authentication.create_user_with_email_and_password(email, password)
          uid = user['localId']
          data = {"name":name, "status":"0"}
          
          database.child("users").child(uid).child("details").set(data)

          return render(request, "signIn.html", {"message":"success", "code":200})
        else:
          return render(request, "signUp.html", {"message":"invalid email", "code":404})

      else:
        return render(request, "signUp.html", {"message":"invalid name", "code":404})

    else:
      return render(request, "signUp.html", {"message":"password does not match", "code":404})

  except:
    message = "enter valid credentials"
    return render(request, "signUp.html", {"message":message, "code":404})


def signUp(request):
  return render(request, "signUp.html")

def logOut(request):
    auth.logout(request)
    return render(request, "signIn.html")

@csrf_exempt
@require_http_methods(["POST"])
def api_signin(request):
    print(request.body)
    response = json.loads(request.body)
    email = response['email']
    password = response['password']
    print(email, password)
    response["Access-Control-Allow-Origin"] = "*"


    try:
      user = authentication.sign_in_with_email_and_password(email, password)
      message = "OK"  
      code = 200
      session_id=user['localId']
      request.session['uid'] = str(session_id)
      data = {"statusCode": 200, "message":message, "token":session_id}
      print(data)
      return JsonResponse(data)

    except:
      message = "Invalid Credentials"
      code = 404
      data = {"statusCode": 404, "message":message}
      print(data)
      return JsonResponse(data)

@csrf_exempt
@require_http_methods(["POST"])
def apiTask(request):
  response = json.loads(request.body)
  userId = response['userId']
  response["Access-Control-Allow-Origin"] = "*"

  try:
    if response['type'] == 'add':
      
      for task_obj in response['tasks']:
        task = task_obj['task']
        priority = task_obj['priority']

        ms = int(time.time()*1000.0)
        data = {"task":task, "priority":str(priority), "status":str(0)}
        database.child("todolist").child(userId).child(str(ms)).set(data)

      message="OK"
      json_data = {"statusCode": 200, "message":message,"tasks":response['tasks']}

      return JsonResponse(data)

    if response['type'] == 'get':
      tasks_id = list(database.child("todolist").child(userId).get().val())
      tasks = list(database.child("todolist").child(userId).get().val().values())
      json_data = []
      for _id in range(len(tasks_id)):
        json_data.append({tasks_id[_id]:tasks[_id]})

      message="OK"
      dat = {"statusCode": 200, "message":message,"tasks":json_data}
      
      return JsonResponse(dat)
    
    if response['type'] == 'delete':
      for task_id in response['tasks']:
        database.child("todolist").child(userId).child(task_id).remove()

      json_data = response['tasks']
      message="OK"
      dat = {"statusCode": 200, "message":message,"tasks":json_data}

      return JsonResponse(dat)

    if response['type'] == 'update':
      for task_obj in response['tasks']:
        key = list(response['tasks'][0].keys())[0]
        task = task_obj[key]['task'] 
        priority = task_obj[key]['priority']
        update_data = {"task":task, "priority":str(priority), "status":str(0)}
        database.child("todolist").child(userId).child(key).update(update_data)

      message="OK"
      json_data = {"statusCode": 200, "message":message,"tasks":response['tasks']}
      return JsonResponse(json_data)
    
  except:
    message = "Invalid Credentials"
    code = 404
    dat = {"statusCode": 404, "message":message}

    return JsonResponse(dat)
