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




def folderIsExist(path):
    isFolderExist = os.path.isdir(path);
    if not isFolderExist:
        os.mkdir(path);

def checkAliases(aliases,text,texts,index):
    status = 0;
    finalPointX = texts[index].bounding_poly.vertices[0].x;
    finalPointY = texts[index].bounding_poly.vertices[0].y;
    for field in aliases:
        if field.lower() ==  text.lower():
        #if field.lower() in text.lower():
            status =1;
    if status == 0:
        for field in aliases:
            print(field)
            if " " in field:
                splitted = field.split(" ");
                print(splitted)
                length =len(splitted);
                print(length)
                fieldWithoutSpace = "".join(splitted);
                upcomingTextsConcatenated = "";
                for i in range(length):
                	if index + i < length:
                		upcomingTextsConcatenated = upcomingTextsConcatenated + texts[index + i].description;
                if upcomingTextsConcatenated.lower() ==  fieldWithoutSpace.lower():
                    status =1;
                    finalPointX = texts[index+length-1].bounding_poly.vertices[2].x;
                    finalPointY = texts[index+length-1].bounding_poly.vertices[2].y;
    response = dict();
    response['status'] = status;
    response['finalPointX'] = finalPointX;
    response['finalPointY'] = finalPointY;
    return response;

def checkAliasesTable(aliases,text):
    status = 0;
    for field in aliases:
        if field.lower() ==  text.lower():
            status =1;
    return status;

def checkAliases1(aliases,text):
    status = 0;
    for field in aliases:
        if field.lower() in text.lower():
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
    addToDebuggerLogs("Google Vision Text extraction started: " +imagePath , outputFolderPath);
    with io.open(imagePath, 'rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)
	
    response = client.text_detection(image=image)
    texts = response.text_annotations
    addToDebuggerLogs("Extracted Texts are "  ,outputFolderPath);
    addToDebuggerLogs(texts ,outputFolderPath);

    #Reading an image in default mode
    requiredFieldsCount = 0;
    image = cv2.imread(imagePath)
    imageOriginal = cv2.imread(imagePath)

    count=0;
    yCoordinates = [];
    counter=0;
    textsCounter1 = 0;
    if len(texts) == 0:
    	addToDebuggerLogs("No Text extracted by Google Vision for " +imagePath ,outputFolderPath);
    else:
	    with open(fieldsCsvFilePath, "r") as f:
	        reader = csv.reader(f, delimiter=",")
	        for i, field in enumerate(reader):
	            #print(line[1]);
	            if field[2] == 'table':
	                aliases = field[0].split('|');
	                for text in texts:
	                    textsCounter1 += 1;
	                    if checkAliases1(aliases,text.description) :
	                        yCoordinates.append(int(text.bounding_poly.vertices[0].y));
	        sum = 0;
	        for i in range(len(yCoordinates)):
	            sum += yCoordinates[i];
	        if len(yCoordinates) != 0:
	            average = sum / len(yCoordinates);   
	            print(average);
	        
	    
	    
	    addToDebuggerLogs("Looping through Required/Optional fields ", outputFolderPath);
	    #print(texts[0]);
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
	            #addToDebuggerLogs(texts,outputFolderPath);
	            textsCounter = 0;
	            for text in texts:
	                textsCounter += 1;
	                checkAliasesResponse = checkAliases(aliases,text.description,texts,textsCounter-1);
	                print("checkAliasesResponse")
	                print(checkAliasesResponse);
	                if checkAliasesResponse['status']:
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
	                                #end_point = (int(text.bounding_poly.vertices[2].x),int(text.bounding_poly.vertices[2].y)) 
	                                end_point = (int(checkAliasesResponse['finalPointX']),int(checkAliasesResponse['finalPointY'])) 
	                                color = (255, 0, 0);
	                                thickness = 2
	                                print("startpoint")
	                                print(start_point)
	                                print("end_point")
	                                print(end_point)
	                                print("end_point actual")
	                                print((int(text.bounding_poly.vertices[2].x),int(text.bounding_poly.vertices[2].y)))
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
	                        vertices = (['({},{})'.format(int(vertex.x), int(vertex.y))
	                                for vertex in text.bounding_poly.vertices]) 
	                        addToDebuggerLogs("Drawing bounding box : " + field[0] + " - " + requiredStatus + " - ", outputFolderPath);
	                        addToDebuggerLogs(vertices ,outputFolderPath);

	                        try:
	                            # Start coordinate ,represents the top left corner of rectangle
	                            start_point =(int(text.bounding_poly.vertices[0].x),int(text.bounding_poly.vertices[0].y))
	                            # Ending coordinate , represents the bottom right corner of rectangle
	                            #end_point = (int(text.bounding_poly.vertices[2].x),int(text.bounding_poly.vertices[2].y)) 
	                            end_point = (int(checkAliasesResponse['finalPointX']),int(checkAliasesResponse['finalPointY'])) 
	                            print("startpoint")
	                            print(start_point)
	                            print("end_point")
	                            print(end_point)
	                            print("end_point actual")
	                            print((int(text.bounding_poly.vertices[2].x),int(text.bounding_poly.vertices[2].y)))
	                            color = (255, 0, 0);
	                            thickness = 2
	                            # Using cv2.rectangle() method
	                            # Draw a rectangle with blue line borders of thickness of 2 px
	                            image = cv2.rectangle(image, start_point, end_point, color, thickness)
	                            break;
	                        except Exception as e: 
	                            addToDebuggerLogs("Exception : " +e.message , outputFolderPath);

	            cv2.imwrite("output.png", image);    
	            if isExist == 0:
	                addToDebuggerLogs("Missing field  -" + requiredStatus + "-" + "|".join(aliases), outputFolderPath);
	                #addToLogs("Missing field  -" + requiredStatus + "-" + "|".join(aliases), outputFolderPath);
	


   
    if requiredFieldsCount > 0 or len(texts) == 0:
        addToDebuggerLogs(fileName + "output image saved in  :  " + outputFolderPath + "/UnQualified/", outputFolderPath);
        path = outputFolderPath + "/UnQualified";
        folderIsExist(path);
        cv2.imwrite(path+"/"+fileName , image);    
        result = fileName + " IS NOT QUALIFIED FOR IQ BOT";
        addToDebuggerLogs(result, outputFolderPath);
        #addToLogs(result, outputFolderPath);
        return result;
    else:
        addToDebuggerLogs(fileName + "output image saved in  :  " + outputFolderPath + "/Qualified/", outputFolderPath);
        addToDebuggerLogs("     ", outputFolderPath);
        path = outputFolderPath + "/Qualified";
        folderIsExist(path);
        cv2.imwrite(path+"/"+fileName, imageOriginal);   
        result = fileName + " IS QUALIFIED FOR IQ BOT";
        addToDebuggerLogs(result, outputFolderPath);
        #addToLogs(result, outputFolderPath);
        return result;

 
imagePath_ = sys.argv[1];#"C:/Users/Sikha.P/PROJECTS/GoogleVision/test1.png";
fieldsCsvFilePath_ =sys.argv[2]; #"C:/Users/Sikha.P/PROJECTS/GoogleVision/fields.csv";
outputFolderPath_ =sys.argv[3] ;#"C:/Users/Sikha.P/PROJECTS/GoogleVision/output";
# imagePath_ = "C:/Users/Sikha.P/PROJECTS/GoogleVision/001_1.png";
# fieldsCsvFilePath_ ="C:/Users/Sikha.P/PROJECTS/GoogleVision/fields.csv";
# outputFolderPath_ ="C:/Users/Sikha.P/PROJECTS/GoogleVision/output";

CheckDocument(imagePath_ ,fieldsCsvFilePath_,outputFolderPath_);



