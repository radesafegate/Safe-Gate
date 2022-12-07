from ast import FormattedValue
from SafeGate import app, models
from flask import  render_template,Response,request,redirect,url_for,flash
import cv2
import face_recognition
import numpy as np
import os
import re
from SafeGate.forms import RegistrationForm , LoginForm
from SafeGate.models import User
from SafeGate import db
from flask_login import login_user,logout_user



stu_data=models.Student.query.all()



known_face_encodings = []
known_face_names = []
known_faces_filenames = []
path="/Users/macbookpro/Desktop/flask/pics/"


for (dirpath, dirnames, filenames) in os.walk(path):
    known_faces_filenames.extend(filenames)
    break

# Walk in the folder
for filename in known_faces_filenames:
    # Load each file
    face = face_recognition.load_image_file(path + filename)
    # Extract the name of each student and add it to known_face_names
    known_face_names.append(re.sub('','', filename[:-5]))
    # Encode de face of every student
    known_face_encodings.append(face_recognition.face_encodings(face)[0])

# Initialize some variables
face_locations = []
face_encodings = []
face_names =[]

def generate_frames():
    video_capture=cv2.VideoCapture(0)

    while True:
    # Grab a single frame of video
        success, frame = video_capture.read()
        if not success:
            break
        else:
    # Resize frame of video to 1/4 size for faster face recognition processing
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            
    # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
            rgb_small_frame = small_frame[:, :, ::-1]
    
    # Only process every other frame of video to save time
            process_this_frame = True
            if process_this_frame:
        # Find all the faces and face encodings in the current frame of video
                face_locations = face_recognition.face_locations(rgb_small_frame)
                face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
                face_names =[]
                for face_encoding in face_encodings:
            # See if the face is a match for the known face(s)
                    matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                    name = "Unknown"

                    face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                    best_match_index = np.argmin(face_distances)
                    if matches[best_match_index]:
                        name = known_face_names[best_match_index]
                    face_names.append(name)
            process_this_frame = not process_this_frame
    # Display the results
            for (top, right, bottom, left), name in zip(face_locations, face_names):
        # Scale back up face locations since the frame we detected in was scaled to 1/4 size
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4

        # Draw a box around the face
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 0), 2)

        # Draw a label with a name below the face
                cv2.rectangle(frame, (left, bottom + 175), (right, bottom -35), (0, 0, 0), cv2.FILLED)
                font = cv2.FONT_HERSHEY_DUPLEX
               # cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
                for std in stu_data:
                    if std.id==name:
                         cv2.putText(frame,std.id , (left + 6, bottom ), font, 1.0, (255, 255, 255), 1)
                         cv2.putText(frame,std.startTime, (left + 6, bottom +45), font, 1.0, (255, 255, 255), 1)
                         cv2.putText(frame,std.finishTime , (left + 6, bottom +95   ), font, 1.0, (255, 255, 255), 1)
                         cv2.putText(frame,std.vaccine , (left + 6, bottom + 135), font, 1.0, (0, 255, 0), 1)
               
            if name=="Unknown":  
                cv2.putText(frame,"Unknown", (left + 6, bottom + 65), font, 1.0, (0 , 0 ,255), 1)
   
   
    # Display the resulting image
        ret ,buffer=cv2.imencode('.jpeg', frame)
        frame=buffer.tobytes()                      
        yield(b'--frame\r\n' 
              b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(
                attempted_password=form.password.data
        ):
            login_user(attempted_user)
            flash(f'Success! You are logged in as: {attempted_user.username}', category='success')
            return redirect(url_for('create_video_page'))
        else:
            flash('Username and password are not match! Please try again', category='danger')

    return render_template('login.html', form=form)



@app.route('/register', methods=['GET','POST'])
def register():
    form=RegistrationForm()
    if form.validate_on_submit():
        user_to_creat = User (username=form.username.data,
                              email_address=form.email_address.data,
                              password=form.password.data)
        db.session.add(user_to_creat)
        db.session.commit()
        return redirect(url_for('create_video_page'))
    if form.errors != {}: #If there are not errors from the validations
        for err_msg in form.errors.values():
            flash(f'There was an error with creating a user: {err_msg}')

    return render_template('register.html',form=form)

@app.route('/welcome')
def create_video_page():
    return render_template('video.html')

@app.route('/video')
def video():
    return Response(generate_frames(),mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def logout_page():
    logout_user()
    flash("You have been logged out!", category='info')
    return redirect(url_for('login')) 
