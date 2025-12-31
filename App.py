from pydoc import describe
from flask import Flask, flash, request, redirect, url_for, render_template
import urllib.request
import os
from werkzeug.utils import secure_filename
import cv2
import numpy as np




app = Flask(__name__)

good_good = [] 
retured_csv = []


UPLOAD_FOLDER = 'static/uploads/'      #main path

app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER        #main folder

app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
 
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
 
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
     
 
@app.route('/')
def home():

    return render_template('home.html')
 
@app.route("/en")
def english():
    return render_template("en/english.html")
@app.route('/en', methods=['GET','POST'])
def upload_image_enlish():
    images=[]           #this will stored the BGR images of dataset
    path = r"English dataset/dataset"
    classes_name = []

    #csv added
    csv_list = []
    csv_file = open(r"English dataset/describe.csv", "r")


    #list for correct
    flag_name = []
    #SIFT
    sift=cv2.SIFT_create()

    #another way
    index_par = dict(algorithm=0, trees=5)
    serach_par = dict()
    flann = cv2.FlannBasedMatcher(index_par, serach_par)

    def listToString(s): 
        
        
        str1 = " " 
        
          
        return (str1.join(s))

    def two(images):
            train_key=[]
            train_des=[]
            csv_list_two = []
            for img, i in zip(images, csv_file):
                img = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
                
                trainKeypoints, trainDescriptors = sift.detectAndCompute(img,None)
                train_key.append(trainKeypoints)
                train_des.append(trainDescriptors)
                csv_list_two.append(i)
                print(i)                                    ## print i value
            return train_key, train_des, csv_list_two

    def one(ttt_des,ttt,ttt_key):
        good_good.clear()
        dataset = os.listdir(path)
        for i in dataset:
            print(i)
            curImg = cv2.imread("{}/{}".format(path,i))     #curImg == current Image
            images.append(curImg)
            classes_name.append(os.path.splitext(i)[0])

        global retured_csv 
        
        train_key, train_des, retured_csv = two(images)  #invoke called function

     
        nn=0
        stat=False
        global checky
        checky = False

        #good_points = [] 
        for ii,jj in zip(images,train_key):
            good_points = []
            
            matches = flann.knnMatch(ttt_des,train_des[nn],k=2)
            for m, n in matches:
                if m.distance < 0.6* n.distance:
                    good_points.append(m)
                    if len(good_points) > 25:   #must break at firt time if its repated
                        print("Normal Browse English > 100")
                        #good_good.clear()
                        good_good.extend([len(good_points),nn])
                        print(classes_name[nn])
                        checky = True
                       
                        print(len(retured_csv[nn].split(",")))
                        print("Good points = ",len(good_points)) ##number of good matches point
                        #break
                    else:
                        pass
                        print("Less than 25 = ", len(good_points))
                        print("Normal Browse English Less than")
                        continue
        
            
            final_img = cv2.drawMatches(ttt, ttt_key, ii, jj, good_points,ii)   ##for less matches [:20] 
            cv2.putText(final_img,classes_name[nn],(20,20),cv2.FONT_HERSHEY_PLAIN,2,(0,255,0),2)
            nn=nn+1
            print(nn)
            
            print(classes_name)
            final_img = cv2.resize(final_img, (1000,650))
            cv2.imshow("wind",final_img)
            cv2.waitKey(1)
            cv2.destroyAllWindows()


    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No image selected for uploading')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))


        input_two = "static/uploads/{}".format(filename)
        ttt=cv2.imread(input_two)
        ttt_gray = cv2.cvtColor(ttt,cv2.COLOR_BGR2GRAY)


        ttt_key, ttt_des = sift.detectAndCompute(ttt_gray,None)
       
        one(ttt_des,ttt,ttt_key)
        print(checky)
        
        if checky == True:
            print(flag_name)

            print("good good = ", good_good)
            print("MAX = ", max(good_good))
            print("NN = ", good_good[good_good.index(max(good_good))+1])
            nn=good_good[good_good.index(max(good_good))+1]
            flag_name.append(retured_csv[nn].split(",")[0])
            csv_list.append(retured_csv[nn].split(",")[1:len(retured_csv[nn].split(","))])
            print(retured_csv)
            cv2.putText(ttt,"Found Match {}".format(flag_name[0]),(20,20),cv2.FONT_HERSHEY_PLAIN,2,(0,255,0),2)
            cv2.putText(ttt,"{}".format(csv_list[0]),(20,70),cv2.FONT_HERSHEY_PLAIN,2,(0,255,0),2)
            cv2.imshow("wind",ttt)
            cv2.waitKey(1)
            cv2.destroyAllWindows()
            return render_template('en/english.html', filename=filename,describe_name="Name : " + flag_name[0],descrip= "Descrition : " + listToString(csv_list[0]))
        elif checky == False:
            print("Not found match")
            cv2.putText(ttt,"Not Found Match",(20,20),cv2.FONT_HERSHEY_PLAIN,2,(0,0,255),2)
            cv2.imshow("Not found", ttt)
            cv2.waitKey(1)
            cv2.destroyAllWindows()
            return render_template('en/english.html', filename=filename,describe_name="Name : Not Found",descrip="Decrition : Not found")
        ##End openCV part


    else:
        flash('incorrect type Allowed types are - png, jpg, jpeg, gif')
        return redirect(request.url)
    

##Camera English Start
@app.route("/cam_en")
def camera_english():
    return render_template("cam_en/cam english.html")
@app.route('/cam_en', methods=['GET','POST'])
def camera_upload_image_enlish():
    images=[]
    path = r"English dataset/dataset"
    classes_name = []

    #csv added
    csv_list = []
    csv_file = open(r"English dataset/describe.csv", "r")


    #list for correct
    flag_name = []
    #SIFT
    sift=cv2.SIFT_create()

    #another way
    index_par = dict(algorithm=0, trees=5)
    serach_par = dict()
    flann = cv2.FlannBasedMatcher(index_par, serach_par)

    def listToString(s): 
        
        # initialize an empty string
        str1 = " " 
        
        # return string  
        return (str1.join(s))

    def two(images):
            train_key=[]
            train_des=[]
            csv_list_two = []
            for img, i in zip(images, csv_file):
                img = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
                
                trainKeypoints, trainDescriptors = sift.detectAndCompute(img,None)
                train_key.append(trainKeypoints)
                train_des.append(trainDescriptors)
                csv_list_two.append(i)
                print(i)                                    ## print i value
            return train_key, train_des, csv_list_two

    def one(ttt_des,ttt,ttt_key):
        good_good.clear()
        dataset = os.listdir(path)
        for i in dataset:
            print(i)
            curImg = cv2.imread("{}/{}".format(path,i))
            images.append(curImg)
            classes_name.append(os.path.splitext(i)[0])
        
        global retured_csv
        train_key, train_des, retured_csv = two(images)  #invoke called function

        
        nn=0
        stat=False
        global checky
        checky = False
        print("TYYYYYYYYYYYYYYYYYYYYYY",type(retured_csv))

        
        for ii,jj in zip(images,train_key):
            
            good_points = []
                
            matches = flann.knnMatch(ttt_des,train_des[nn],k=2)
            for m, n in matches:
                if m.distance < 0.6* n.distance:
                    good_points.append(m)
                    if len(good_points) > 40:   #must break at firt time if its repated
                        print("Camera English > 100")
                        good_good.extend([len(good_points),nn])
                        
                        print(classes_name[nn])
                        checky = True
                        
                        print(len(retured_csv[nn].split(",")))
                        print("Good points = ",len(good_points)) ##number of good matches point
                        #break
                    else:
                        pass
                        print("Less than 10 = ", len(good_points))
                        print("Camera English less than")
                        continue
                        
            
            final_img = cv2.drawMatches(ttt, ttt_key, ii, jj, good_points,ii)   ##for less matches [:20]
             
            cv2.putText(final_img,classes_name[nn],(20,20),cv2.FONT_HERSHEY_PLAIN,2,(0,255,0),2)
            
            nn=nn+1
            print(nn)
            
            print(classes_name)
            final_img = cv2.resize(final_img, (1000,650))
            cv2.imshow("wind",final_img)
            cv2.waitKey(1)
            cv2.destroyAllWindows()


    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No image selected for uploading')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        flash('Image successfully uploaded and displayed below')

        test_iii = "onee.jpg"
        
        input_two = "static/uploads/{}".format(filename)
        ttt=cv2.imread(input_two)
        ttt_gray = cv2.cvtColor(ttt,cv2.COLOR_BGR2GRAY)


        ttt_key, ttt_des = sift.detectAndCompute(ttt_gray,None)
       
        one(ttt_des,ttt,ttt_key)
        print(checky)
        
        if checky == True:
            print(flag_name)
            print("good good = ", good_good)
            print("MAX = ", max(good_good))
            print("NN = ", good_good[good_good.index(max(good_good))+1] )
            nn=good_good[good_good.index(max(good_good))+1]
            flag_name.append(retured_csv[nn].split(",")[0])
            csv_list.append(retured_csv[nn].split(",")[1:len(retured_csv[nn].split(","))])
            print(retured_csv)

            cv2.putText(ttt,"Found Match {}".format(flag_name[0]),(20,20),cv2.FONT_HERSHEY_PLAIN,2,(0,255,0),2)
            cv2.putText(ttt,"{}".format(csv_list[0]),(20,70),cv2.FONT_HERSHEY_PLAIN,2,(0,255,0),2)
            cv2.imshow("wind",ttt)
            cv2.waitKey(1)
            cv2.destroyAllWindows()
            return render_template('cam_en/cam english.html', filename=filename,describe_name=flag_name[0],descrip=listToString(csv_list[0]))
        elif checky == False:
            print("Not found match")
            cv2.putText(ttt,"Not Found Match",(20,20),cv2.FONT_HERSHEY_PLAIN,2,(0,0,255),2)
            cv2.imshow("Not found", ttt)
            cv2.waitKey(1)
            cv2.destroyAllWindows()
            return render_template('cam_en/cam english.html', filename=filename,describe_name="Not Found",descrip="Not found")
        ##End openCV part


    else:
        flash('Allowed image types are - png, jpg, jpeg, gif')
        return redirect(request.url)
    
##Camera English End

@app.route("/ar")
def arabic():
    return render_template("ar/arabic.html")
@app.route('/ar', methods=['GET','POST'])
def upload_image_arabic():
    images=[]
    path = r"Arabic dataset/dataset"
    classes_name = []

    #csv added
    csv_list = []
    csv_file = open(r"Arabic dataset/describe.csv", "r", encoding="utf-8")


    #list for correct
    flag_name = []
    #SIFT
    sift=cv2.SIFT_create()

    #another way
    index_par = dict(algorithm=0, trees=5)
    serach_par = dict()
    flann = cv2.FlannBasedMatcher(index_par, serach_par)

    
    def two(images):
            train_key=[]
            train_des=[]
            csv_list_two = []
            for img, i in zip(images, csv_file):
                img = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
                
                trainKeypoints, trainDescriptors = sift.detectAndCompute(img,None)
                train_key.append(trainKeypoints)
                train_des.append(trainDescriptors)
                csv_list_two.append(i)               
                print(i)                                        ##print i value
            return train_key, train_des, csv_list_two

    def one(ttt_des,ttt,ttt_key):
        good_good.clear()
        dataset = os.listdir(path)
        for i in dataset:
            print(i)
            curImg = cv2.imread("{}/{}".format(path,i))
            images.append(curImg)
            classes_name.append(os.path.splitext(i)[0])
        
        global retured_csv
        train_key, train_des, retured_csv = two(images)  #invoke called function

        
        nn=0
        stat=False
        global checky
        checky = False

        
        for ii,jj in zip(images,train_key):
            good_points = []
            
            matches = flann.knnMatch(ttt_des,train_des[nn],k=2)
            for m, n in matches:
                if m.distance < 0.6* n.distance:
                    good_points.append(m)
                    if len(good_points) > 25:   #must break at firt time if its repated
                        print("Normal Browse Arabic > 100")
                        good_good.extend([len(good_points),nn])
                        print(classes_name[nn])
                        checky = True
                        
                        print(csv_list)
                        print("Good Point = ",len(good_points)) ##number of good matches point
                        #break
                    else:
                        pass
                        print("Less than 10 = ", len(good_points))
                        print("Normal Browse Arabic Less Than")
                        continue
                        
           
            final_img = cv2.drawMatches(ttt, ttt_key, ii, jj, good_points,ii)   ##for less matches [:20] 
            cv2.putText(final_img,classes_name[nn],(20,20),cv2.FONT_HERSHEY_PLAIN,2,(0,255,0),2)
            nn=nn+1
            print(nn)
            
            print(classes_name)
            final_img = cv2.resize(final_img, (1000,650))
            cv2.imshow("wind",final_img)
            cv2.waitKey(1)
            cv2.destroyAllWindows()


    if 'file' not in request.files:
        flash(':( لا يوجد ملف ')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('لم يتم تحديد اي صورة ')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        test_iii = "onee.jpg"
        input_two = "static/uploads/{}".format(filename)
        ttt=cv2.imread(input_two)
        ttt_gray = cv2.cvtColor(ttt,cv2.COLOR_BGR2GRAY)


        ttt_key, ttt_des = sift.detectAndCompute(ttt_gray,None)
       
        one(ttt_des,ttt,ttt_key)
        print(checky)
        
        if checky == True:
            print(flag_name)
            print("good good = ", good_good)
            print("MAX = ", max(good_good))
            print("NN = ", good_good[good_good.index(max(good_good))+1])
            nn=good_good[good_good.index(max(good_good))+1]
            flag_name.append(retured_csv[nn].split(",")[0])
            #csv_list.append(retured_csv[nn].split(",")[1:len(retured_csv[nn].split(","))]) #this just for english to show what after comma ,
            csv_list.append(retured_csv[nn])
            print(retured_csv)

            cv2.putText(ttt,"Found Match {}".format(flag_name[0]),(20,20),cv2.FONT_HERSHEY_PLAIN,2,(0,255,0),2)
            cv2.putText(ttt,"{}".format(csv_list[0]),(20,70),cv2.FONT_HERSHEY_PLAIN,2,(0,255,0),2)
            cv2.imshow("wind",ttt)
            cv2.waitKey(1)
            cv2.destroyAllWindows()
            print("hhhhhhhhhhhhhhhhhhhhhhhhhhh",csv_list)
            return render_template('ar/arabic.html', filename=filename,describe_name=flag_name[0],descrip=csv_list[0])
        elif checky == False:
            print("Not found match")
            cv2.putText(ttt,"Not Found Match",(20,20),cv2.FONT_HERSHEY_PLAIN,2,(0,0,255),2)
            cv2.imshow("Not found", ttt)
            cv2.waitKey(1)
            cv2.destroyAllWindows()
            return render_template('ar/arabic.html', filename=filename,describe_name="الاسم : غير معروف",descrip="الوصف : غير معروف")
        ##End openCV part


        #return render_template('en/english.html', filename=filename,describe_name=flag_name[0],descrip=csv_list[0])
    else:
        flash('png,jpg,jpeg,gif الصيغة مرفوضة استخدم')
        return redirect(request.url)

## Camera Arabic Start
@app.route("/cam_ar")
def camera_arabic():
    return("cam_ar/cam arabic.html")
@app.route('/cam_ar', methods=['GET','POST'])
def camera_upload_image_arabic():
    images=[]
    path = r"Arabic dataset/dataset"
    classes_name = []

    #csv added
    csv_list = []
    csv_file = open(r"Arabic dataset/describe.csv", "r", encoding="utf-8")


    #list for correct
    flag_name = []
    #SIFT
    sift=cv2.SIFT_create()

    #another way
    index_par = dict(algorithm=0, trees=5)
    serach_par = dict()
    flann = cv2.FlannBasedMatcher(index_par, serach_par)

    
    def two(images):
            train_key=[]
            train_des=[]
            csv_list_two = []
            for img, i in zip(images, csv_file):
                img = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
                
                trainKeypoints, trainDescriptors = sift.detectAndCompute(img,None)
                train_key.append(trainKeypoints)
                train_des.append(trainDescriptors)
                csv_list_two.append(i)               
                print(i)                                        ##print i value
            return train_key, train_des, csv_list_two

    def one(ttt_des,ttt,ttt_key):
        dataset = os.listdir(path)
        for i in dataset:
            print(i)
            curImg = cv2.imread("{}/{}".format(path,i))
            images.append(curImg)
            classes_name.append(os.path.splitext(i)[0])
        
        global retured_csv
        train_key, train_des, retured_csv = two(images)  #invoke called function

        nn=0
        stat=False
        global checky
        checky = False

        #good_points = [] 
        for ii,jj in zip(images,train_key):
            good_points = []
            
            matches = flann.knnMatch(ttt_des,train_des[nn],k=2)
            for m, n in matches:
                if m.distance < 0.6* n.distance:
                    good_points.append(m)
                    if len(good_points) > 25:   #must break at firt time if its repated
                        print("Camera Arabic > 100")
                        good_good.extend([len(good_points),nn])
                        print(classes_name[nn])
                        checky = True
                        
                        print(csv_list)
                        print("Good Point = ",len(good_points)) ##number of good matches point
                        #break
                    else:
                        pass
                        print("Less than 10 = ", len(good_points))
                        print("Camera Arabic Less Than")
                        continue
                        
            final_img = cv2.drawMatches(ttt, ttt_key, ii, jj, good_points,ii)   ##for less matches [:20]
             
            cv2.putText(final_img,classes_name[nn],(20,20),cv2.FONT_HERSHEY_PLAIN,2,(0,255,0),2)
            nn=nn+1
            print(nn)
            
            print(classes_name)
            final_img = cv2.resize(final_img, (1000,650))
            cv2.imshow("wind",final_img)
            cv2.waitKey(1)
            cv2.destroyAllWindows()


    if 'file' not in request.files:
        flash(':( لا يوجد ملف ')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('لم يتم تحديد اي صورة ')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))


        #input_two = file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        input_two = "static/uploads/{}".format(filename)
        ttt=cv2.imread(input_two)
        ttt_gray = cv2.cvtColor(ttt,cv2.COLOR_BGR2GRAY)


        ttt_key, ttt_des = sift.detectAndCompute(ttt_gray,None)
       
        one(ttt_des,ttt,ttt_key)
        print(checky)
        
        if checky == True:
            print(flag_name)
            print("good good = ", good_good)
            print("MAX = ", max(good_good))
            print("NN = ", good_good[good_good.index(max(good_good))+1])
            nn=good_good[good_good.index(max(good_good))+1]
            flag_name.append(retured_csv[nn].split(",")[0])
            csv_list.append(retured_csv[nn].split(",")[1:len(retured_csv[nn].split(","))])
            print(retured_csv)

            cv2.putText(ttt,"Found Match {}".format(flag_name[0]),(20,20),cv2.FONT_HERSHEY_PLAIN,2,(0,255,0),2)
            cv2.putText(ttt,"{}".format(csv_list[0]),(20,70),cv2.FONT_HERSHEY_PLAIN,2,(0,255,0),2)
            cv2.imshow("wind",ttt)
            cv2.waitKey(1)
            cv2.destroyAllWindows()
            print("hhhhhhhhhhhhhhhhhhhhhhhhhhh",csv_list)
            return render_template('cam_ar/cam arabic.html', filename=filename,describe_name=flag_name[0],descrip=csv_list[0])
        elif checky == False:
            print("Not found match")
            cv2.putText(ttt,"Not Found Match",(20,20),cv2.FONT_HERSHEY_PLAIN,2,(0,0,255),2)
            cv2.imshow("Not found", ttt)
            cv2.waitKey(1)
            cv2.destroyAllWindows()
            return render_template('cam_ar/cam arabic.html', filename=filename,describe_name="غير معروف",descrip="غير معروف")
        ##End openCV part

    else:
        flash('png, jpg, jpeg, gif - صيغ الصور المسموح بها هي')
        return redirect(request.url)

## Camera Arabic    End


@app.route("/en_settings")
def english_settings():
    return render_template("en/english index.html")

@app.route("/en_contact")
def english_contact():
    return render_template("en/social media.html")

@app.route("/ar_contact")
def arabic_contact():
    return render_template("ar/support arabic.html")

@app.route("/ar_settings")
def arabic_settings():
    return render_template("ar/settings Arabic.html")



@app.route('/display/<filename>')
def display_image(filename):
    #print('display_image filename: ' + filename)
    return redirect(url_for('static', filename='uploads/' + filename), code=301)
 
if __name__ == "__main__":
    app.run(host="0.0.0.0",port=7777)   #default part 5000