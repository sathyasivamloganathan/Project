from io import BytesIO
from tkinter import Canvas
from flask import Flask, request, send_file, jsonify, make_response
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from gridfs import GridFS
import gridfs
import letter
from mongo_config import initialize_mongo
from datetime import datetime, timedelta
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_mail import Mail, Message
from random import randint
from flask_cors import CORS
from pymongo import MongoClient


from bson.json_util import dumps
from bson.objectid import ObjectId


import numpy as np
from torch_utils import get_prediction_axial , get_prediction_cor , get_prediction_sag
from reportlab.pdfgen import canvas
from gridfs import GridFS
from reportlab.lib.pagesizes import letter

import mimetypes
from retrive import retrieve_file
from collections import defaultdict
import os
import shutil
from datetime import datetime
from bson import ObjectId

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.colors import Color, black

app = Flask(__name__)
initialize_mongo(app)
mongo = PyMongo(app)
bcrypt = Bcrypt(app)
CORS(app, supports_credentials=True, methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])


app.config['JWT_SECRET_KEY'] = '62362tyeucuyJHBJH&**YGY54@*@NNBu2w87yhib'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=5)
jwt = JWTManager(app)



app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'testing12345development@gmail.com'
app.config['MAIL_PASSWORD'] = 'jpxu cfsh hkgd eeih'
app.config['MAIL_DEFAULT_SENDER'] = 'testing12345development@gmail.com'
mail = Mail(app)



# User Registration
class User:
    def __init__(self, name, email, password, mobile, role):
        self.name = name
        self.email = email
        self.password = password
        self.mobile = mobile
        self.role = role

def save_user_to_db(user):
    try:
        hashed_password = bcrypt.generate_password_hash(user.password).decode('utf-8')

        user_data = {
            'name': user.name,
            'email': user.email,
            'password': hashed_password,
            'mobile': user.mobile,
            'role': user.role,
            'timestamp': datetime.utcnow(),
        }
        mongo.db.userData.insert_one(user_data)

        return True, None 
    except Exception as e:
        return False, str(e)

@app.route('/api/user_register', methods=['POST'])
def user_register():
    data = request.get_json()

    if 'name' not in data or 'email' not in data or 'password' not in data or 'mobile' not in data or 'role' not in data:
        return jsonify({'message': 'All fields (name, email, password, mobile, role) are required'}), 400

    valid_roles = ['user']
    if data['role'] not in valid_roles:
        return jsonify({'message': 'Invalid role. Allowed roles: user'}), 400

    existing_user = mongo.db.userData.find_one({'email': data['email']})
    if existing_user:
        return jsonify({'message': 'Email already exists. Choose a different one.'}), 400

    new_user = User(
        name=data['name'],
        email=data['email'],
        password=data['password'],
        mobile=data['mobile'],
        role=data['role']
    )

    success, error_message = save_user_to_db(new_user)

    if success:
        return jsonify({
            'message': 'User registered successfully'}), 201
    else:
        return jsonify({'message': f'Error registering user: {error_message}'}), 500


# Admin Registration

class Admin:
    def __init__(self, hospitalName, name, email, password, mobile, role):
        self.hospitalName = hospitalName,
        self.name = name
        self.email = email
        self.password = password
        self.mobile = mobile
        self.role = role

def save_admin_to_db(admin):
    try:
        hashed_password = bcrypt.generate_password_hash(admin.password).decode('utf-8')

        admin_data = {
            'hospitalName': admin.hospitalName,
            'name': admin.name,
            'email': admin.email,
            'password': hashed_password,
            'mobile': admin.mobile,
            'role': admin.role,
            'timestamp': datetime.utcnow(),
        }
        mongo.db.adminData.insert_one(admin_data)

        return True, None 
    except Exception as e:
        return False, str(e)

@app.route('/api/admin_register', methods=['POST'])
def admin_register():
    data = request.get_json()

    if 'hospitalName' not in data or 'name' not in data or 'email' not in data or 'password' not in data or 'mobile' not in data or 'role' not in data:
        return jsonify({'message': 'All fields (hospitalName, name, email, password, mobile, role) are required'}), 400

    valid_roles = ['admin']
    if data['role'] not in valid_roles:
        return jsonify({'message': 'Invalid role. Allowed roles: admin'}), 400

    existing_user = mongo.db.adminData.find_one({'email': data['email']})
    if existing_user:
        return jsonify({'message': 'Email already exists. Choose a different one.'}), 400

    new_admin = Admin(
        hospitalName=data['hospitalName'],
        name=data['name'],
        email=data['email'],
        password=data['password'],
        mobile=data['mobile'],
        role=data['role']
    )

    success, error_message = save_admin_to_db(new_admin)

    if success:
        return jsonify({
            'message': 'Amin registered successfully'}), 201
    else:
        return jsonify({'message': f'Error registering admin: {error_message}'}), 500



# Login

@app.route("/api/login", methods=['POST'])
def login():
    data = request.get_json()

    if 'email' not in data:
        return jsonify({'message': 'Email is required'})
    if 'password' not in data:
        return jsonify({'message': 'Password is required'})
    
    user = mongo.db.userData.find_one({'email': data['email']})

    if user is None:
        user = mongo.db.adminData.find_one({'email': data['email']})

    if user and bcrypt.check_password_hash(user['password'], data['password']):
        access_token = create_access_token(identity={'email': user['email'], 'role': user['role']})
        return jsonify({'message': 'Login Successful', 'access_token': access_token, 'user': {'email': user['email'], 'role': user['role'], 'name': user['name']}}), 200
    
    else:
        return jsonify({'message': 'Invalid email or password'}), 401
    



# Forget password 
@app.route("/api/forget-password", methods=['POST'])
def forget_password():
    data = request.get_json()
    email = data.get('email')

    user = mongo.db.userData.find_one({'email': email})
    if user:
        otp = str(randint(1000, 9999))
        send_otp_email(email, otp)
        mongo.db.userData.update_one({'email': email}, {'$set': {'otp': otp}})
        return jsonify({'message': 'OTP sent successful'}),200

    if user is None:
        user = mongo.db.adminData.find_one({'email': email})
        if user:
            otp = str(randint(1000, 9999))
            send_otp_email(email, otp)
            mongo.db.adminData.update_one({'email': email}, {'$set': {'otp': otp}})
            return jsonify({'message': 'OTP sent successful'}),200
    
    else:
        return jsonify({'message': 'User not found'}),404


def send_otp_email(email, otp):
    msg = Message('Password Reset OTP', recipients=[email])
    msg.body = f'Your OTP for password reset is: {otp}'
    mail.send(msg)


@app.route("/api/verify-otp", methods=['POST'])
def verify_otp():
    data = request.get_json()
    email = data.get('email')
    user_otp = data.get('otp')
    new_password = data.get('new_password')
    
    user = mongo.db.userData.find_one({'email': email, 'otp': user_otp})
    if user:
        hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
        mongo.db.userData.update_one({'email': email}, {'$set': {'password': hashed_password, 'otp': None}})
        return jsonify({'message': 'Password reset successful'}),200

    if user is None:
        user = mongo.db.adminData.find_one({'email': email, 'otp': user_otp})
        if user:
            hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
            mongo.db.adminData.update_one({'email': email}, {'$set': {'password': hashed_password, 'otp': None}})
            return jsonify({'message': 'Password reset successful'}),200
    else:
        return jsonify({'message': 'Invalid Otp'}), 401




# class AdminMessage: 
#     def __init__(self, hospitalName, sender_email, sender_name, receiver_email, message):
#         self.sender_email = sender_email,
#         self.sender_name = sender_name,
#         self.receiver_email = receiver_email
#         self.message = message
#         self.hospitalName = hospitalName
#         self.timestamp = datetime.utcnow()

# def save_adminMessage_to_db(admin_message):
#     try:
#         admin_message_data = {
#         'sender_email': admin_message.sender_email,
#         'hospitalName': admin_message.hospitalName, 
#         'sender_name': admin_message.sender_name,
#         'receiver_email': admin_message.receiver_email,
#         'message': admin_message.message,
#         'timestamp': admin_message.timestamp
#         }
#         mongo.db.adminMessages.insert_one(admin_message_data)
#         return True, None
#     except Exception as e:
#         return False, str(e)

# def get_hospitalName(sender_email):
#     user_data = mongo.db.adminData.find_one({'email': sender_email})
#     if user_data:
#         return user_data.get('hospitalName')
#     return None

# def user_exists(user_email):
#     return mongo.db.userData.find_one({'email': user_email})

# @app.route("/api/adminUser-saves", methods=['POST'])
# @jwt_required()
# def sendMessage():
#     data = request.get_json()

#     if 'receiver_email' not in data or 'message' not in data:
#         return jsonify({'message': 'Receiver email and message is required'})

#     receiver_email = data['receiver_email']
#     sender_email = data['sender_email']
#     sender_name = data['sender_name']

#     if not user_exists(receiver_email):
#         return jsonify({'message': f'User with email {receiver_email} does not exist'}), 400

#     hospitalName = get_hospitalName(sender_email)

#     admin_message = AdminMessage(
#         sender_email=sender_email,
#         sender_name = sender_name,
#         receiver_email = receiver_email,
#         message = data['message'],
#         hospitalName = hospitalName,
#     )

#     success, error_message = save_adminMessage_to_db(admin_message)

#     if success:
#         return jsonify({'message': 'Message sent successful'}), 201
#     else:
#         return jsonify({'message': f'Error at sending message: {error_message}'}), 500




# @app.route('/api/get_user_saves/<email>', methods=['GET'])
# def get_user_saves(email):
#     query = {"receiver_email": email}
#     cursor = mongo.db.adminMessages.find(query, {"message": 1, "sender_name": 1, "hospitalName": 1, "_id": 0})
#     user_messages = [{"message": msg["message"], "sender_name": msg["sender_name"], "hospitalName": msg["hospitalName"]} for msg in cursor]
#     return jsonify({"messages":user_messages})


# @app.route('/api/admin_get_report_sends/<email>', methods=['GET'])
# def admin_get_report_sends(email):
#     query = {"sender_email": email}
#     cursor = mongo.db.adminMessages.find(query, {"message": 1, "receiver_email": 1, "_id": 1})
#     user_messages = [{"message": msg["message"], "receiver_email": msg["receiver_email"], "_id":str(msg["_id"])} for msg in cursor]
#     return jsonify({"messages":user_messages})



# @app.route("/api/upload", methods=['POST'])
# def upload_file():
#     files = request.files.getlist('files')
#     for file in files:
#         save_file_to_mongoDb(file)
#     return jsonify({'message': 'File uploaded successfully'})

# def save_file_to_mongoDb(file):
#     mongo.db.saveFiles.insert_one({'filename': file.filename, 'data': file.read()})



# ---------------------------
from gridfs import GridFS
from flask import Flask, request, jsonify
import numpy as np
from reportlab.pdfgen import canvas
import io


def get_admin_details(email):
    admin_details = mongo.db.adminData.find_one({'email':email})
    return admin_details

# ---------------------------------------------------
# Admin saves the report api

grid_fs_adminSaves = GridFS(mongo.db, collection='adminSavesReport')
ALLOWED_EXTENSIONS = {'npy', 'pdf'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def create_pdf_from_dictionary_and_store_to_admin_saves(data, grid_fs_adminSaves, sender_email, hospital_Name, doctor_name, doctor_email, receiver_email, receiver_name, patient_id, patient_mobile, patient_dob, patient_gender, patient_abha):
    try:
        output_filename = f"{patient_id}.pdf"
        pdf_buffer = io.BytesIO()
        pdf_canvas = canvas.Canvas(pdf_buffer, pagesize=letter)

        pdf_canvas.setFont("Helvetica", 14)

        # Drawing the hospital logo closer to the table
        logo_path = "C:\\Users\\Sathya Sivam\\Downloads\\LT\\client\\public\\hospital logo.png"  # Replace with the path to your hospital logo
        pdf_canvas.drawImage(logo_path, 250, pdf_canvas._pagesize[1] - 100, width=100, height=100, mask='auto')

        # Drawing border between doctor and patient details
        pdf_canvas.line(250, pdf_canvas._pagesize[1] - 200, 250, pdf_canvas._pagesize[1] - 360)  # Vertical line

        # Printing doctor details
        pdf_canvas.setFont("Helvetica-Bold", 14)
        pdf_canvas.drawString(60, pdf_canvas._pagesize[1] - 220, f"Doctor Name: {doctor_name}")
        pdf_canvas.setFont("Helvetica", 14)
        pdf_canvas.drawString(60, pdf_canvas._pagesize[1] - 240, f"Hospital Name: {hospital_Name}")
        pdf_canvas.drawString(60, pdf_canvas._pagesize[1] - 260, f"Doctor Email: {doctor_email}")

        # Printing patient details
        pdf_canvas.setFont("Helvetica-Bold", 14)
        pdf_canvas.drawString(260, pdf_canvas._pagesize[1] - 220, f"Patient ID: {patient_id}")
        pdf_canvas.setFont("Helvetica", 14)
        pdf_canvas.drawString(260, pdf_canvas._pagesize[1] - 240, f"Receiver Name: {receiver_name}")
        pdf_canvas.drawString(260, pdf_canvas._pagesize[1] - 260, f"Patient Mobile: {patient_mobile}")
        pdf_canvas.drawString(260, pdf_canvas._pagesize[1] - 240, f"Patient Dob: {patient_dob}")
        pdf_canvas.drawString(260, pdf_canvas._pagesize[1] - 260, f"Patient Gender: {patient_gender}")
        # Printing other data with decreased font size
        pdf_canvas.setFont("Helvetica", 12)
        pdf_canvas.setFillColor(black)  # Reset color to black
        pdf_canvas.drawString(50, pdf_canvas._pagesize[1] - 290, "Other Data:")
        pdf_canvas.line(50, pdf_canvas._pagesize[1] - 295, 300, pdf_canvas._pagesize[1] - 295)  # Underline

        y_position = pdf_canvas._pagesize[1] - 310
        for key, value in data.items():
            pdf_canvas.drawString(50, y_position, f"{key}: {value}")
            y_position -= 20

        pdf_canvas.save()

        pdf_buffer.seek(0)
        metadata = {'SenderEmail': sender_email,'HospitalName': hospital_Name, 'DoctorName': doctor_name, 'DoctorEmail': doctor_email, 'ReceiverEmail': receiver_email, 'ReceiverName': receiver_name, 'PatientAbha': patient_abha, 'PatientId': patient_id, 'PatientMobile': patient_mobile, 'PatientDob': patient_dob, 'PatientGender': patient_gender}
        pdf_id = grid_fs_adminSaves.put(pdf_buffer.read(), filename=output_filename, metadata=metadata)

        print(f"PDF and Email stored successfully in MongoDB: {output_filename}")

    except Exception as e:
        print(f"Error creating and storing PDF: {str(e)}")


@app.route('/api/adminSavedData', methods=['POST'])
def adminSavedData():
    if request.method == 'POST':
        try:
            sender_email = request.form.get("SenderEmail")
            receiver_email = request.form.get("ReceiverEmail")
            receiver_name = request.form.get("ReceiverName")
            patient_id = request.form.get("PatientId")
            patient_mobile = request.form.get("ReceiverMobile")
            patient_dob = request.form.get("ReceiverDob")
            patient_gender = request.form.get('ReceiverGender')
            patient_abha = request.form.get('ReceiverAbha')

            admin_details = get_admin_details(sender_email)

            if admin_details:
                hospital_Name = admin_details.get('hospitalName')[0]
                doctor_name = admin_details.get('name')
                doctor_email = admin_details.get('email')
            else:
                return jsonify("error")

            file_axial = request.files.get('file_0')
            file_cor = request.files.get('file_1')
            file_sag = request.files.get('file_2')

            # folder_name = file_axial.filename.split('.')[0]


            img_array_axial = np.load(file_axial)
            img_array_cor = np.load(file_cor)
            img_array_sag = np.load(file_sag)

            prediction_axial = get_prediction_axial(img_array_axial)
            prediction_cor = get_prediction_cor(img_array_cor)
            prediction_sag = get_prediction_sag(img_array_sag)

            data = {
                'probability of ACL axial': prediction_axial[0],
                'probability of Meniscus axial': prediction_axial[1],
                'probability of Abnormal axial': prediction_axial[2],
                'probability of ACL coronal': prediction_cor[0],
                'probability of Meniscus coronal': prediction_cor[1],
                'probability of Abnormal coronal': prediction_cor[2],
                'probability of ACL sagittal': prediction_sag[0],
                'probability of Meniscus sagittal': prediction_sag[1],
                'probability of Abnormal sagittal': prediction_sag[2],
            }
            
            create_pdf_from_dictionary_and_store_to_admin_saves(data, grid_fs_adminSaves, sender_email, hospital_Name, doctor_name, doctor_email, receiver_email, receiver_name, patient_id, patient_mobile, patient_dob, patient_gender, patient_abha)

            
            return success

        except Exception as e:
            return jsonify({'error': f'Error during prediction and storing PDF - {str(e)}'})

    return jsonify({'error': 'Invalid method'})



# -------------------------------------------------------



# Admin send the report to the user api

grid_fs_adminSends = GridFS(mongo.db, collection='adminSendsReport')
ALLOWED_EXTENSIONS = {'npy', 'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
# output_filename='new1 .pdf'
def create_pdf_from_dictionary_and_store_to_adminUser_saves(data, grid_fs_adminSends, sender_email, hospital_Name, doctor_name, doctor_email, receiver_email, receiver_name, patient_id, patient_mobile, patient_dob, patient_gender, patient_abha):
    try:
        output_filename = f"{patient_id}.pdf"
        pdf_buffer = io.BytesIO()
        pdf_canvas = canvas.Canvas(pdf_buffer, pagesize=(612, 792))

        pdf_canvas.setFont("Helvetica", 12)

        pdf_canvas.drawString(100, pdf_canvas._pagesize[1] - 50, f"Doctor Name: {doctor_name}")

        
        for key, value in data.items():
            pdf_canvas.drawString(100, pdf_canvas._pagesize[1] - 100, f"{key}: {value}")
            pdf_canvas.translate(0, -20)

        pdf_canvas.save()

        
        pdf_buffer.seek(0)
        metadata = {'SenderEmail': sender_email, 'HospitalName': hospital_Name, 'DoctorName': doctor_name, 'DoctorEmail': doctor_email, 'ReceiverEmail': receiver_email, 'ReceiverName': receiver_name, 'PatientAbha': patient_abha, 'PatientId': patient_id, 'PatientMobile': patient_mobile, 'PatientDob': patient_dob, 'PatientGender': patient_gender}
        pdf_id = grid_fs_adminSends.put(pdf_buffer.read(), filename=output_filename, metadata=metadata)

        print(f"PDF and Email stored successfully in MongoDB: {output_filename}")

    except Exception as e:
        print(f"Error creating and storing PDF: {str(e)}")


@app.route('/api/adminSendToUserData', methods=['POST'])
def adminSendToUserData():
    if request.method == 'POST':
        try:
            sender_email = request.form.get("SenderEmail")
            receiver_email = request.form.get("ReceiverEmail")
            receiver_name = request.form.get("ReceiverName")
            patient_id = request.form.get("PatientId")
            patient_mobile = request.form.get("ReceiverMobile")
            patient_dob = request.form.get("ReceiverDob")
            patient_gender = request.form.get('ReceiverGender')
            patient_abha = request.form.get('ReceiverAbha')

            admin_details = get_admin_details(sender_email)
            if admin_details:
                hospital_Name = admin_details.get('hospitalName')[0]
                doctor_name = admin_details.get('name')
                doctor_email = admin_details.get('email')
            else:
                return jsonify("error")

            file_axial = request.files.get('file_0')
            file_cor = request.files.get('file_1')
            file_sag = request.files.get('file_2')

            # folder_name = file_axial.filename.split('.')[0]


            img_array_axial = np.load(file_axial)
            img_array_cor = np.load(file_cor)
            img_array_sag = np.load(file_sag)

            prediction_axial = get_prediction_axial(img_array_axial)
            prediction_cor = get_prediction_cor(img_array_cor)
            prediction_sag = get_prediction_sag(img_array_sag)

            data = {
                'probability of ACL axial': prediction_axial[0],
                'probability of Meniscus axial': prediction_axial[1],
                'probability of Abnormal axial': prediction_axial[2],
                'probability of ACL coronal': prediction_cor[0],
                'probability of Meniscus coronal': prediction_cor[1],
                'probability of Abnormal coronal': prediction_cor[2],
                'probability of ACL sagittal': prediction_sag[0],
                'probability of Meniscus sagittal': prediction_sag[1],
                'probability of Abnormal sagittal': prediction_sag[2],
            }
            
            create_pdf_from_dictionary_and_store_to_adminUser_saves(data, grid_fs_adminSends, sender_email, hospital_Name, doctor_name, doctor_email, receiver_email, receiver_name, patient_id, patient_mobile, patient_dob, patient_gender, patient_abha)

            
            return success

        except Exception as e:
            return jsonify({'error': f'Error during prediction and storing PDF - {str(e)}'})

    return jsonify({'error': 'Invalid method'})


# AdminSaves.jsx
@app.route('/api/adminSaves/metadata', methods=['GET'])
def get_metadata_adminSaves():
    email = request.args.get('email')
    metadata_documents = list(mongo.db.adminSavesReport.files.find({'metadata.SenderEmail': email}, {'_id': 1, 'metadata': 1, 'filename': 1}))
    metadata = [{'_id': str(doc['_id']), 'filename': doc['filename'], **doc['metadata']} for doc in metadata_documents]
    return jsonify(metadata)


@app.route('/api/admin_report_saves', methods=['GET'])
def download_pdf_adminSaves():
    try:
        fileId = request.args.get('id')
        if not fileId:
            return 'File id not provided', 400

        # Find the file in GridFS based on filename
        pdf_file = grid_fs_adminSaves.find_one({'_id': ObjectId(fileId)})
        if pdf_file:
            # Open a stream to read the PDF data
            pdf_data = io.BytesIO(pdf_file.read())

            # Set the stream position to the beginning
            pdf_data.seek(0)

            # Return the PDF file as a response
            return send_file(pdf_data, mimetype='application/pdf')
        else:
            return 'PDF not found', 404
    except Exception as e:
        return f'Error downloading PDF: {str(e)}', 500



# admin send report saves.jsx
@app.route('/api/adminSends/metadata', methods=['GET'])
def get_metadata_adminSends():
    email = request.args.get('email')
    metadata_documents = list(mongo.db.adminSendsReport.files.find({'metadata.SenderEmail': email}, {'_id': 1, 'metadata': 1, 'filename': 1}))
    metadata = [{'_id': str(doc['_id']), 'filename': doc['filename'], **doc['metadata']} for doc in metadata_documents]
    return jsonify(metadata)


@app.route('/api/admin_report_sends', methods=['GET'])
def download_pdf_adminSends():
    try:
        fileId = request.args.get('id')
        if not fileId:
            return 'File id not provided', 400

        # Find the file in GridFS based on filename
        pdf_file = grid_fs_adminSends.find_one({'_id': ObjectId(fileId)})
        if pdf_file:
            # Open a stream to read the PDF data
            pdf_data = io.BytesIO(pdf_file.read())

            # Set the stream position to the beginning
            pdf_data.seek(0)

            # Return the PDF file as a response
            return send_file(pdf_data, mimetype='application/pdf')
        else:
            return 'PDF not found', 404
    except Exception as e:
        return f'Error downloading PDF: {str(e)}', 500


@app.route('/api/check_user_details', methods=['POST'])
def check_user_details():
    data = request.get_json()
    abha = data.get('abha')
    user = mongo.db.abha.find_one({"abhaNumber": abha})
    if user:
        return jsonify({"found": True, "user_details": {"userName": user["userName"], "userEmail": user["userEmail"], "mobile": user["userMobile"], "gender": user["gender"], "dob": user["dateOfBirth"]}})
    else:
        return jsonify({"found": False})
        



# userSaves.jsx
@app.route('/api/userSaves/metadata', methods=['GET'])
def get_metadata_UserSaves():
    email = request.args.get('email')
    metadata_documents = list(mongo.db.adminSendsReport.files.find({'metadata.ReceiverEmail': email}, {'_id': 1, 'metadata': 1, 'filename': 1}))
    metadata = [{'_id': str(doc['_id']), 'filename': doc['filename'], **doc['metadata']} for doc in metadata_documents]
    return jsonify(metadata)




# Multiple Folder

grid_fs_multipleFolder = GridFS(mongo.db, collection='multipleFolder')
def create_pdf_from_dictionary_and_store_multipleFolder(data, grid_fs_multipleFolder, sender_email, subfolder, output_filename):
    try:
        pdf_buffer = io.BytesIO()
        pdf_canvas = canvas.Canvas(pdf_buffer, pagesize=(612, 792))

        pdf_canvas.setFont("Helvetica", 12)

        pdf_canvas.drawString(100, pdf_canvas._pagesize[1] - 50, f"Patient ID: {subfolder}")

        for key, value in data.items():
            pdf_canvas.drawString(100, pdf_canvas._pagesize[1] - 100, f"{key}: {value}")
            pdf_canvas.translate(0, -20)

        pdf_canvas.save()

        pdf_buffer.seek(0)
        metadata = {"SenderEmail": sender_email, "PatientId": subfolder}
        grid_fs_multipleFolder.put(pdf_buffer.read(), metadata=metadata, filename=output_filename)

        print(f"PDF stored successfully in MongoDB: {output_filename}")

    except Exception as e:
        print(f"Error creating and storing PDF: {str(e)}")


def userDetails_ABHA(subfolder):
    user_data = mongo.db.abha.find_one({'abhaNumber': subfolder})
    return user_data


@app.route('/api/multipleFolder', methods=['POST'])
def multipleFolder():
    data = {}
    files = request.files.getlist('files[0]') 
    subfolders = request.form.getlist('subfolders[0]')
    
    sender_email = request.form.get("AdminEmail")

    files_by_subfolder = defaultdict(list)
    for file, subfolder in zip(files, subfolders):
     files_by_subfolder[subfolder].append(file)

   
    for subfolder, file_paths in files_by_subfolder.items():
       
        print(f"Processing subfolder: {subfolder}")
        if len(file_paths) >= 3:
            # Load the first three files for the current subfolder
            file1 = np.load(file_paths[0])
            file2 = np.load(file_paths[1])
            file3 = np.load(file_paths[2])


            prediction_axial = get_prediction_axial(file1)
            prediction_coronal = get_prediction_cor(file2)
            prediction_sagittal = get_prediction_sag(file3)



            data.update({
                        f'probability of ACL axial ': prediction_axial[0],
                        f'probability of Meniscus axial ': prediction_axial[1],
                        f'probability of Abnormal axial ': prediction_axial[2],
                        f'probability of ACL coronal ': prediction_coronal[0],
                        f'probability of Meniscus coronal ': prediction_coronal[1],
                        f'probability of Abnormal coronal ': prediction_coronal[2],
                        f'probability of ACL sagittal ': prediction_sagittal[0],
                        f'probability of Meniscus sagittal ': prediction_sagittal[1],
                        f'probability of Abnormal sagittal ': prediction_sagittal[2],
                    })
            output_filename = subfolder + ".pdf"
            create_pdf_from_dictionary_and_store_multipleFolder(data, grid_fs_multipleFolder, sender_email, subfolder, output_filename=output_filename )
            
            # Do something with the loaded files
            print(f"Loaded file 1 from subfolder {subfolder}: {file1.shape}")
            print(f"Loaded file 2 from subfolder {subfolder}: {file2.shape}")
            print(f"Loaded file 3 from subfolder {subfolder}: {file3.shape}")
        else:
            print(f"Not enough files in subfolder {subfolder}")

    return "Folder loaded successfully and reports are generated."


@app.route('/api/adminMultipleFolder/metadata', methods=['GET'])
def get_metadata_adminMultipleFolder():
    email = request.args.get('email')
    metadata_documents = list(mongo.db.multipleFolder.files.find({'metadata.SenderEmail': email}, {'_id': 1, 'metadata': 1, 'filename': 1}))
    metadata = [{'_id': str(doc['_id']), 'filename': doc['filename'], **doc['metadata']} for doc in metadata_documents]
    return jsonify(metadata)

@app.route('/api/adminMultipleFolder', methods=['GET'])
def download_pdf_adminMultipleFolder():
    try:
        fileId = request.args.get('id')
        if not fileId:
            return 'File id not provided', 400

        # Find the file in GridFS based on filename
        pdf_file = grid_fs_multipleFolder.find_one({'_id': ObjectId(fileId)})
        if pdf_file:
            # Open a stream to read the PDF data
            pdf_data = io.BytesIO(pdf_file.read())

            # Set the stream position to the beginning
            pdf_data.seek(0)

            # Return the PDF file as a response
            return send_file(pdf_data, mimetype='application/pdf')
        else:
            return 'PDF not found', 404
    except Exception as e:
        return f'Error downloading PDF: {str(e)}', 500






@app.route('/api/admin_saves_delete/<_id>', methods=['DELETE'])
def admin_saves_report_delete(_id):
    try:
        obj_id = ObjectId(_id)
        result = mongo.db.adminSavesReport.files.delete_one({"_id": obj_id})
        if result.deleted_count == 1:
            return jsonify({"Success": True, "message": "Message Deleted successfully"})
        else:
            return jsonify({"Success": False, "message": "Message not found"})
    except Exception as e:
        return jsonify({"Sucess": False, "message": str(e)})

@app.route('/api/admin_sends_delete/<_id>', methods=['DELETE'])
def admin_send_report_delete(_id):
    try:
        obj_id = ObjectId(_id)
        result = mongo.db.adminSendsReport.files.delete_one({"_id": obj_id})
        if result.deleted_count == 1:
            return jsonify({"Success": True, "message": "Message Deleted successfully"})
        else:
            return jsonify({"Success": False, "message": "Message not found"})
    except Exception as e:
        return jsonify({"Sucess": False, "message": str(e)})
        
@app.route('/api/adminMultipleFolderDelete/<_id>', methods=['DELETE'])
def admin_MultipleFolder_delete(_id):
    try:
        obj_id = ObjectId(_id)
        result = mongo.db.multipleFolder.files.delete_one({"_id": obj_id})
        if result.deleted_count == 1:
            return jsonify({"Success": True, "message": "Message Deleted successfully"})
        else:
            return jsonify({"Success": False, "message": "Message not found"})
    except Exception as e:
        return jsonify({"Sucess": False, "message": str(e)})



# ---------------------------
    
if __name__ == '__main__':
    app.run(debug=True)