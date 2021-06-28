
#Author:Prasad Katankot
#Partner Solution Desk
#Date:20-05-2021
#V1.0
#Merge RPA PDF converted images 
#merge_images.bat E:\Projects\Python\Regex INFO E:\Projects\Ey_Merk\Germany\OneDrive_2021-05-13\dreg E:\Projects\Ey_Merk\Germany\OneDrive_2021-05-13\output

# import required module
import os
import sys
import pathlib
import re
import cv2
import logging


# assign directory through arguments
directory = sys.argv[3]
output_directory = sys.argv[4]
if sys.argv[2]== "INFO":
	debugLevel = logging.INFO
elif sys.argv[2] == 'DEBUG':
	debugLevel = logging.DEBUG

logging.basicConfig(filename=sys.argv[1]+'\\'+'merge.txt', encoding='utf-8', level= debugLevel) 
logging.info(sys.argv[1])
logging.info(sys.argv[2])
logging.info(sys.argv[3])
# iterate over files in that directory
for filename in os.listdir(directory):
    f = os.path.join(directory, filename)
    # checking if it is a file
    if os.path.isfile(f):
        #print(f)
        x = f.split(".pdf")
        #print(x[0]+".png")
        x=x[0]
        y=x.split(directory)
        y=output_directory+y[1] 
        #print(y)
       
        #y = re.escape(y)
        
        # if os.path.exists(y):
        # 	print (y+"-File exist using OS path")
        fileExists = True
        counter=1
        while fileExists:
        	img_page = y +'_'+str(counter)+'.png'
        	#print("File to check--" + img_page)
        	logging.debug("File to check--" + img_page)
	        file = pathlib.Path(img_page)
	        if file.exists ():
	        	#print (img_page + "-File exist")
	        	logging.debug(img_page +"-File exist")
	        	logging.info(img_page +"-File exist")
	        	fileExists = True
	        	if counter == 2:
	        		img1 = cv2.imread(img_page_prev)
	        		img2 = cv2.imread(img_page)
	        		im_v = cv2.vconcat([img1,img2])
	        		pathlib.Path(y +'_'+str(counter-1)+'.png').unlink() 
	        		file.unlink()
	        	elif counter > 2:
	        		#img1 = cv2.imread(img_page_prev)
	        		img2 = cv2.imread(img_page)
	        		im_v = cv2.vconcat([im_v, img2])
	        		file.unlink()
	        	counter=counter+1
	        	img_page_prev = img_page
	        else:
	        	#print ( img_page +"-File does not exist")
	        	logging.debug(img_page +"-File does not exist")
	        	logging.info(img_page +"-File does not exist")
	        	fileExists = False
	        	if counter > 1:
	        		cv2.imwrite(y + '.png', im_v)
	        		#im_v.save(y + '_combined.png')