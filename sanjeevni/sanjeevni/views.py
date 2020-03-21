import pyrebase
from django.http import HttpResponse

firebaseConfig = {
    "apiKey": "AIzaSyDMicSpS3XgbDU5dkmcOpiRIgx6CFUY0rQ",
    "authDomain": "dev-sanjeevni.firebaseapp.com",
    "databaseURL": "https://dev-sanjeevni.firebaseio.com",
    "projectId": "dev-sanjeevni",
    "storageBucket": "dev-sanjeevni.appspot.com",
    "messagingSenderId": "235860833440",
    "appId": "1:235860833440:web:08c35a047c53e7cbccc5c5",
    "measurementId": "G-XT9018JE69",
    "serviceAccount": "/home/rana/devsanjeev.json"
}

firebase = pyrebase.initialize_app(firebaseConfig)

authentication = firebase.auth()
database = firebase.database()
def labSignUp(request):
    email = request.POST.get('mail')
    password = request.POST.get('pass')
    cpassword = request.POST.get('cpass')
    # email="root1234@gmail.com"
    # password="12345678"
    # cpassword="12345678"
    try:
        if str(password) == str(cpassword):
            user = authentication.create_user_with_email_and_password(email, password)
            uid = user['localId']
            data = {"email": email, "status": "1"}
            database.child("users").child(uid).child("labdetails").set(data)
            return HttpResponse({"message": "true", "code": 200})
        else:
            return HttpResponse({"message": "not same password", "code": 404})
    except:
        message = "enter valid credentials pls try again"
        return HttpResponse({"message": message, "code": 404})

def labSignIn(request):
    email = request.POST.get("mail")
    passw = request.POST.get("pass")
    try:
        user = authentication.sign_in_with_email_and_password(email, passw)
    except:
        return HttpResponse({"code": 404})
    print(user['idToken'])
    session_id = user['idToken']     #this gives your app to a session for see the user is currently loged in
    request.session['uid'] = str(session_id)


