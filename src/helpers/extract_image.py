import os
import cv2
import sys
import json
import numpy as np
import multiprocessing
from PIL import Image,ImageDraw


filename=sys.argv[1]

def extract_image(img):
    if not(os.path.exists('./data/'+filename+'/interim/extracted_images/'+img['id']+'_'+img['type']+'_'+str(img['number'])+'.png')):        #check if image alrready exists

        if 'slab' in img['type']:                                                                                                           #filter to remove unnecessary images
            image= Image.open('./data/'+filename+'/images/'+img['img']).convert("RGBA")                                                     #open original image
            imArray = np.asarray(image)
            polygon=[]
            for i in img['pixels']:
                polygon.append((i[0],i[1]))
            maskIm = Image.new('L', (imArray.shape[1], imArray.shape[0]), 0)                                                                #Create mask for empty image
            ImageDraw.Draw(maskIm).polygon(polygon, outline=1, fill=1)                                                                      #Draw the polygon using pixels as coordinates
            mask = np.array(maskIm)
            newImArray = np.empty(imArray.shape,dtype='uint8')                                                                              #Create empty image using old image dimensions
            newImArray[:,:,:3] = imArray[:,:,:3]                                                                                            #Copy rgb values from old image
            newImArray[:,:,3] = mask*255                                                                                                    #Copy mask to new image
            newIm = Image.fromarray(newImArray, "RGBA")                                                                                     #Create image from array
            datas = newIm.getdata()                                                                                                         #Extract dats from new image

            newData = []
            for item in datas:
                if item[3]==0:                                                                                                              #Check if alpha value is 0
                    newData.append((0, 0, 0, 0))                                                                                            #Convert pixel to black
                else:
                    newData.append(item)

            newIm.putdata(newData)                                                                                                          #Convert cahnged dats to image
            newIm.save('./data/'+filename+'/interim/extracted_images/'+img['id']+'_'+img['type']+'_'+str(img['number'])+'.png',optimize=True)#Save image
    

imgs=json.load(open('./data/'+filename+'/interim/best_image.json'))
pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())     # Create a multiprocessing Poolfor div in range(division):
result=pool.map(extract_image,imgs,chunksize=1)