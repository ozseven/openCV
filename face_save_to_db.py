from datetime import datetime
import sqlite3
import time
from cv2 import VideoCapture
import face_recognition
import cv2
from textToSpeech import textToSpeech
from database import faceSave 
import numpy as np

# Haarcascade dosyalarının yolu
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
video_capture =cv2.VideoCapture(0)

face_location =[]
face_encoding=[]
face_names=[]
process_this_frame=True

# SQLite veritabanından yüz verilerini ve isimlerini al
conn = sqlite3.connect("users.db")
c = conn.cursor()
c.execute("SELECT FaceEncode, Name , UpdatedDate FROM Users")
rows = c.fetchall()
known_face_encoding = [np.frombuffer(row[0], dtype=np.float64) for row in rows]
known_face_names = [row[1] for row in rows]
known_face_updated_date = [datetime.strptime(row[2].split('.')[0], '%Y-%m-%d %H:%M:%S') for row in rows]


while True:
    ret,frame =video_capture.read()
    if process_this_frame:
        small_frame =cv2.resize(frame,(0,0),fx=0.25,fy=0.25)
        rgb_small_frame =small_frame[:,:,::-1]

        face_location=face_recognition.face_locations(rgb_small_frame)
        face_encoding =face_recognition.face_encodings(rgb_small_frame,face_location)

        face_names = []

        for face_encodings in face_encoding:
            matches =face_recognition.compare_faces(known_face_encoding,face_encodings)
            name ='Unkown'

            face_distances =face_recognition.face_distance(known_face_encoding,face_encodings)
            best_match_index =np.argmin(face_distances)
            if matches[best_match_index]:
                name =known_face_names[best_match_index]
                
                
                
            else:
                textToSpeech("How about we get to know each other since I don't know you yet?",'en')
                boolTanisma = int(input())
                if boolTanisma ==1:
                    name = input()
                    surname = input()
                    createdDate =datetime.now()
                    updatedDate=datetime.now()
                    faceSave('users.db','Users',[name,surname,createdDate,updatedDate,face_encodings],['Name','Surname','CreatedDate','UpdatedDate','FaceEncode'])
                    textToSpeech("I have successfully registered you in the program.",'en')
                    conn = sqlite3.connect("users.db")
                    c = conn.cursor()
                    c.execute("SELECT FaceEncode, Name FROM Users")
                    rows = c.fetchall()
                    known_face_encoding = [np.frombuffer(row[0], dtype=np.float64) for row in rows]
                    known_face_names = [row[1] for row in rows]
                    
                else:
                    textToSpeech('Peki size kişisel konularda yardımcı olamayacağım.','tr')

            face_names.append(name)
            

    process_this_frame = not process_this_frame

    # Display the results
    for (top, right, bottom, left), name in zip(face_location, face_names):
        # Scale back up face locations since the frame we detected in was scaled to 1/4 size
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

        # Draw a box around the face
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

        # Draw a label with a name below the face
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
        # Eğer kişi belirlenmişse ve son selamlaşmadan 60 saniye geçmişse

        
        conn = sqlite3.connect("users.db")
        c = conn.cursor()   
        now = datetime.now()
        c.execute("SELECT FaceEncode, Name , UpdatedDate FROM Users")
        rows = c.fetchall()
        known_face_encoding = [np.frombuffer(row[0], dtype=np.float64) for row in rows]
        known_face_names = [row[1] for row in rows]
        known_face_updated_date = [datetime.strptime(row[2].split('.')[0], '%Y-%m-%d %H:%M:%S') for row in rows]
        time_diff = now - known_face_updated_date[best_match_index]
        seconds_diff = time_diff.total_seconds()
        c.execute("UPDATE Users SET UpdatedDate=? WHERE Name=?", (now, name))
        conn.commit()
        
        if seconds_diff > 300:
            textToSpeech('Hello ' + name + ', how can I help you?', 'en')
            updated_date = datetime.now()
            # Update the database
           
            

        

    # Display the resulting image
    cv2.imshow('Video', frame)
    

    # Hit 'q' on the keyboard to quit!
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release handle to the webcam
VideoCapture.release()
cv2.destroyAllWindows()

conn.close()