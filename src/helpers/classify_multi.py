import os
import sys
import cv2
import json
import numpy as np
from PIL import Image
import multiprocessing
from src.helpers.model import get_dilated_unet

filename=sys.argv[1]

def calc(p):
    y=np.zeros((3648,5472,3)) 
    predict=np.array(predicts[p])
    y[np.where(predict[0,:,:,0]>0.50)]=[255,0,0]
    y[np.where(predict[0,:,:,1]>0.50)]=[0,255,0]
    y[np.where(predict[0,:,:,2]>0.50)]=[0,0,255]
    im = Image.open('./data/'+filename+'/interim/extracted_images/'+imgs[p])
    x_train = np.array(im,'f')
    y[np.where(x_train[:,:,3]==0)]=[0,0,0]
    cv2.imwrite('./data/'+filename+'/interim/classified_images/'+imgs[p],y)
    blue=np.count_nonzero(y[:,:,0]>0)                                                                                                          #Extract rgb totals from image
    green=np.count_nonzero(y[:,:,1]>0)
    red=np.count_nonzero(y[:,:,2]>0)
    if red+green+blue==0:
        rp,cp=0,0
    else:
        rp=(red/(red+blue+green))*100
        cp=(blue/(red+blue+green))*100
    return rp,cp

pathinput2=os.listdir('./data/'+filename+'/interim/extracted_images')
input_file = open ('./data/'+filename+'/interim/progress_structural.json')
my_json = json.load(input_file)

component_names,reinforcement_progress,concrete_progress=[],[],[]

for img in pathinput2:
    result = str(img).split('_')
    component_names.append(result[0])  
component_names=list(set(component_names))                                                                                                      #Remove duplicates
for i in range(len(component_names)):                                                                                                           #Create two array of arrys equal to number of ids
    reinforcement_progress.append([])                                                                                                           
    concrete_progress.append([]) 



imgs,predicts=[],[]
model = get_dilated_unet(input_shape=(912,912, 3), mode='cascade', filters=64,n_class=4)                                                        #Initalize CNN
model.load_weights('./models/slabs_model_weights.hdf5')
comp=[]
print(len(pathinput2))
for img in pathinput2:
    comp.append(img)
    if not(os.path.exists('./data/'+filename+'/interim/classified_images/'+img)):
        im = Image.open('./data/'+filename+'/interim/extracted_images/'+img)
        x_train = np.array(im,'f')
        x=np.zeros((1,x_train.shape[0],x_train.shape[1],4))
        width=0
        img_size=912
        while width<x_train.shape[1]:                                                                                                           #Crop image to remove memory errors
            height=0
            while height<x_train.shape[0]:
                x_traintest=np.reshape(x_train[height:height+img_size,width:width+img_size,0:3],(1,912,912,3))                                  #reshape data for cnn
                x_train1=model.predict(x_traintest)
                x[0,height:height+img_size,width:width+img_size,:4]=x_train1
                height=height+912
            width=width+912
        imgs.append(img)
        predicts.append(x)
        if len(imgs)==multiprocessing.cpu_count() or len(pathinput2)==len(comp):
            pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())     # Create a multiprocessing Poolfor div in range(division):
            result=pool.map(calc, range(len(predicts)),chunksize=1)
            pool.close()
            pool.terminate()
            for i in range(len(result)):
                r = str(imgs[i]).split('_')
                ind=component_names.index(r[0])
                reinforcement_progress[ind].append(result[i][0])
                concrete_progress[ind].append(result[i][1])
            imgs,predicts=[],[]
            
    else:
        r = str(img).split('_')
        ind=component_names.index(r[0]) 
        x=cv2.imread('./data/'+filename+'/interim/classified_images/'+img)
        blue=np.count_nonzero(x[:,:,0]>0)                                                                                                          #Extract rgb totals from image
        green=np.count_nonzero(x[:,:,1]>0)
        red=np.count_nonzero(x[:,:,2]>0)
        try:                                                                                                                                       #calculate progress based on colors
            reinforcement_progress[ind].append(((red+blue)/(green+red+blue))*100)
        except:
            reinforcement_progress[ind].append(0)
        try:
            concrete_progress[ind].append(((blue)/(green+red+blue))*100)
        except:
            concrete_progress[ind].append(0)

reinforcement,concrete=[],[]
for i in range(len(reinforcement_progress)):                                                                                                   #Make  the array of arrays to single array
    reinforcement.append(sum(reinforcement_progress[i])/len(reinforcement_progress[i]))
    concrete.append(sum(concrete_progress[i])/len(concrete_progress[i]))


for j in range(len(component_names)):                                                                                                           #Add the calculated values to json file
    for i in my_json:
        if i== component_names[j]:
            for k in range(len(my_json[i]['children'])):
                if my_json[i]['children'][k]['name']=='reinforcement' :
                    my_json[i]['children'][k]['progress']=reinforcement[j]*(float(my_json[i]['progress'])/100)
                elif my_json[i]['children'][k]['name']=='concrete':
                    my_json[i]['children'][k]['progress']=concrete[j]*(float(my_json[i]['progress'])/100)

for i in my_json:
    progress=0
    for j in range(len(my_json[i]['children'])):
        progress=my_json[i]['children'][j]['progress']+progress
    my_json[i]['progress']=int(progress/len(my_json[i]['children']))                                                                            #Adjust progress of object based on childrens progress

with open('./data/external/'+filename+'.json', 'w') as outfile:                                                                                 #Save the json file
    json.dump(my_json, outfile)  