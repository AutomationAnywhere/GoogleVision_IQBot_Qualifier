#Author:Sikha P
#Partner Solution Desk
#Date:28-06-2021
#V1.0
#Text Extraction using OCR Technique Google Vision 
#google_vision.bat C:\Users\Sikha.P\PROJECTS\GoogleVision\test1.png C:\Users\Sikha.P\PROJECTS\GoogleVision\fields.csv C:\Users\Sikha.P\PROJECTS\GoogleVision

# import required module
import os
import logging
import csv
from google.cloud import vision
from PIL import Image, ImageDraw
import cv2
import io
import sys




def folderIsExist(outputFolderPath):
    isFolderExist = os.path.isdir(outputFolderPath);
    if not isFolderExist:
        os.mkdir(outputFolderPath);

def checkAliases(aliases,text):
    status = 0;
    for field in aliases:
        if field.lower() in text.lower():
            status =1;
    return status;

def checkAliasesTable(aliases,text):
    status = 0;
    for field in aliases:
        if field.lower() ==  text.lower():
            status =1;
    return status;


def checkNearest(avg,value):
    if value >= avg -1500 and value <= avg +1500:
        return 1;
    return 0;


def addToDebuggerLogs(message,folderPath):
    print(message)
    #logging.basicConfig(filename=sys.argv[1]+'\\'+'merge.txt', encoding='utf-8', level= debug
    logging.basicConfig(level=logging.DEBUG, filename=folderPath+'\\'+'log.log', encoding='utf-8',format='%(asctime)s %(levelname)s:%(message)s')
    try:
        # count the number of words in a file and log the result
       logging.debug(message)
    except OSError as e:
        logging.error("error reading the file")

def addToLogs(message,folderPath):
    logging.basicConfig(level=logging.INFO, filename=folderPath+'log.log', format='%(asctime)s %(levelname)s:%(message)s')
    try:
        # count the number of words in a file and log the result
       logging.debug(message)
    except OSError as e:
        logging.error("error reading the file")





def CheckDocument(imagePath,fieldsCsvFilePath,outputFolderPath):

    folderIsExist(outputFolderPath);
    fileName = os.path.basename(imagePath);
    fileNameWithoutExtension =   os.path.splitext(fileName)[0];
    
    client = vision.ImageAnnotatorClient()

    with io.open(imagePath, 'rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)

    response = client.text_detection(image=image)
    texts = response.text_annotations


    #Reading an image in default mode
    requiredFieldsCount = 0;
    image = cv2.imread(imagePath)

    count=0;
    yCoordinates = [];
    counter=0;
    with open(fieldsCsvFilePath, "r") as f:
        reader = csv.reader(f, delimiter=",")
        for i, field in enumerate(reader):
            #print(line[1]);
            if field[2] == 'table':
                aliases = field[0].split('|');
                for text in texts:
                    if checkAliases(aliases,text.description) :
                        yCoordinates.append(int(text.bounding_poly.vertices[0].y));
        sum = 0;
        for i in range(len(yCoordinates)):
            sum += yCoordinates[i];
        average = sum / len(yCoordinates);   
        print(average);
    
    addToDebuggerLogs("Google Vision Text extraction started   : " +imagePath , outputFolderPath);
    addToDebuggerLogs("Looping through Required/Optional fields ", outputFolderPath);

    with open(fieldsCsvFilePath, "r") as f:
        reader = csv.reader(f, delimiter=",")
        for i, field in enumerate(reader):
            if field[1] == "1":
                requiredStatus =  "REQUIRED";
            else:
                requiredStatus =  "OPTIONAL";
            addToDebuggerLogs("Checking Field : " + field[0] + " - " + requiredStatus, outputFolderPath);
            if counter == 0 :
                counter += 1;
                continue;
            isExist = 0;
            aliases = field[0].split('|');
            if field[1] == "1":
                requiredFieldsCount +=1 ;

            for text in texts:
                if checkAliasesTable(aliases,text.description):
                    if(field[2] == "table"):
                        if checkNearest(average,text.bounding_poly.vertices[0].y):
                            addToDebuggerLogs("DETECTED as TABLE field : " + field[0] + " - " + requiredStatus, outputFolderPath);
                            if field[1] == "1":
                                requiredFieldsCount -= 1;
                            isExist =1 ;
                            vertices = (['({},{})'.format(int(vertex.x), int(vertex.y))
                                for vertex in text.bounding_poly.vertices])     
                            addToDebuggerLogs("Drawing bounding box : " + field[0] + " - " + requiredStatus + " - ", outputFolderPath);
                            try:
                                # Start coordinate ,represents the top left corner of rectangle
                                start_point =(int(text.bounding_poly.vertices[0].x),int(text.bounding_poly.vertices[0].y))
                                # Ending coordinate , represents the bottom right corner of rectangle
                                end_point = (int(text.bounding_poly.vertices[2].x),int(text.bounding_poly.vertices[2].y)) 
                                color = (255, 0, 0);
                                thickness = 2
                                # Using cv2.rectangle() method
                                # Draw a rectangle with blue line borders of thickness of 2 px
                                image = cv2.rectangle(image, start_point, end_point, color, thickness)
                            except Exception as e: 
                                print(e)
                    else:
                        addToDebuggerLogs("DETECTED as FORM field : " + field[0] + "- " + requiredStatus, outputFolderPath);
                        if field[1] == "1":
                            requiredFieldsCount -= 1;
                        isExist = 1;
                        try:
                            # Start coordinate ,represents the top left corner of rectangle
                            start_point =(int(text.bounding_poly.vertices[0].x),int(text.bounding_poly.vertices[0].y))
                            # Ending coordinate , represents the bottom right corner of rectangle
                            end_point = (int(text.bounding_poly.vertices[2].x),int(text.bounding_poly.vertices[2].y)) 
                            color = (255, 0, 0);
                            thickness = 2
                            # Using cv2.rectangle() method
                            # Draw a rectangle with blue line borders of thickness of 2 px
                            image = cv2.rectangle(image, start_point, end_point, color, thickness)
                            break;
                        except Exception as e: 
                            print(e)
            cv2.imwrite("output.png", image);    
            if bool(isExist):
                addToDebuggerLogs("Missing field details -" + requiredStatus + "-" + "|".join(aliases), outputFolderPath);
                addToLogs("Missing field details -" + requiredStatus + "-" + "|".join(aliases), outputFolderPath);

    
   
    if requiredFieldsCount > 0:
        addToDebuggerLogs(fileNameWithoutExtension + "_outputImage.png  " + "output image saved in  :  " + outputFolderPath + "/UnQualified/", outputFolderPath);
        path = outputFolderPath + "/UnQualified";
        folderIsExist(path);
        cv2.imwrite(path+"/"+fileName , image);    
        result = fileName + " IS NOT QUALIFIED FOR IQ BOT";
        addToDebuggerLogs(result, outputFolderPath);
        addToLogs(result, outputFolderPath);
        return result;
    else:

        addToDebuggerLogs(fileNameWithoutExtension + "_outputImage.png " + "output image saved in  :  " + outputFolderPath + "/Qualified/", outputFolderPath);
        addToDebuggerLogs("     ", outputFolderPath);
        path = outputFolderPath + "/Qualified";
        folderIsExist(path);
        cv2.imwrite(path+"/"+fileName, image);   
        result = fileName + " IS QUALIFIED FOR IQ BOT";
        addToDebuggerLogs(result, outputFolderPath);
        addToLogs(result, outputFolderPath);
        return result;


print(sys.argv[1]) ;  
imagePath_ = sys.argv[1];#"C:/Users/Sikha.P/PROJECTS/GoogleVision/test1.png";
fieldsCsvFilePath_ =sys.argv[2]; #"C:/Users/Sikha.P/PROJECTS/GoogleVision/fields.csv";
outputFolderPath_ =sys.argv[3] ;#"C:/Users/Sikha.P/PROJECTS/GoogleVision/output";
CheckDocument(imagePath_ ,fieldsCsvFilePath_,outputFolderPath_);
