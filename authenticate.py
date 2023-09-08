import pyrebase

config = {
    'apiKey': "AIzaSyBWQXbSBC6oKNZk96jMP53qvHJqekG0T1Q",
    'authDomain': "summer-2023-396400.firebaseapp.com",
    'projectId': "summer-2023-396400",
    'storageBucket': "summer-2023-396400.appspot.com",
    'messagingSenderId': "900862315561",
    'appId': "1:900862315561:web:fa9f9ccf3f5f2b4f6b6038",
    'measurementId': "G-XYTJ9FBMVG",
    'databaseURL': " "
}

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()

email="test@gmail.com"
password="123456"

#user = auth.create_user_with_email_and_password(email, password)
user = auth.sign_in_with_email_and_password(email, password)
print(user)