import os
import sys
import cv2
import json
from math import cos
import numpy as np
import multiprocessing
from src.helpers.utils import best_fitting_plane,angle
from scipy.spatial import ConvexHull
from shapely.geometry import Polygon


filename = sys.argv[1]

def inputs(filename):
    img_names=[]
    pmatrix=[]  

    for fname in os.listdir('data/'+filename):                                                                                                          #creating list of files in the folder
        if fname.endswith('.txt'):                                                                                                                      #checking if the file ends with .txt
            with open('data/'+filename+'/'+fname) as file:                                                                                              
                for line in file:                                                                                                                       #getting line from txt file
                    line=line.split(' ')
                    img_names.append(line[0])                                                                                                           #extracting image name
                    for i in range(1,len(line)-1):
                        line[i]=float(line[i])                                                                                                              
                    pmatrix.append(np.array([[line[1],line[2],line[3],line[4]], [line[5],line[6],line[7],line[8]],[line[9],line[10],line[11],line[12]]]))   #extracting pmatrix for the image name

            
    for fname in os.listdir('data/'+filename):
        if fname.endswith('.xyz'):
            with open('data/'+filename+'/'+fname) as file:
                for line in file:
                    line=line.split(' ')
                    offset=[float(line[0]),float(line[1]),float(line[2])]                                                                               #extracting offset



    boundaries=json.load(open('./data/'+filename+'/interim/boundaries.json'))                                                                           #Opening boundaries json file to boundaries

    return pmatrix,img_names,offset,boundaries



def bim_to_img(b):
    obj=boundaries[b]
    bim_pixels=[]
    bim_img=[]
    bim_id=[]
    bim_type=[]
    bim_number=[]
    for i in list(range(len(obj['boundary']))):                                                                                                         #getting each point from list of boundary points
        bim_points=obj['boundary'][i]
        for bp in range(len(bim_points)):
            bim_points[bp][0]=bim_points[bp][0]-offset[0]                                                                                               #Subtracting offset from coordinates
            bim_points[bp][1]=bim_points[bp][1]-offset[1]
            bim_points[bp][2]=bim_points[bp][2]-offset[2]
        
        img_pixels=[]
        img_name=[]
        camera_coords=[]
        for m in range(len(pmatrix)):
            pixel_count=0
            pixels=[]
            cc=[]
            for point in bim_points:
                point_np=np.array([[point[0]],[point[1]],[point[2]],[1]])
                pixel_point=np.matmul(pmatrix[m],point_np)                                                                                              #multiplying pmatrix with point
                u=int(pixel_point[0]/pixel_point[2])                                                                                                    #Extracting pixel values from point
                v=int(pixel_point[1]/pixel_point[2])
                if u>=0 and 5472>u and v>=0 and 3648>v:                                                                                                 #Checking if pixel values are in range of the image
                    pixel_count=pixel_count+1                                                                                                           
                    pixels.append([u,v])
                    cc.append([float(pixel_point[0]),float(pixel_point[1]),float(pixel_point[2])])                                                      #Appending to array

            
            
            if pixel_count==len(bim_points):                                                                                                            #Checking if number of appended pixels are equal to points
                img_pixels.append(pixels)                                                                                                               #appending all the data
                img_name.append(img_names[m])
                camera_coords.append(cc)
                
            
        maxp=0
        for p in range(len(img_pixels)):
            try:
                sp_xy=[]
                hull=ConvexHull(img_pixels[p])                                                                                                          #Create hull of pixels
                for h_v in hull.vertices:
                    sp_xy.append(img_pixels[p][h_v])                                                                                                    #Extract boundary of pixels
                pix_poly=Polygon(sp_xy)                                                                                                                 #form polygon from pixels
                plane1,normal1=best_fitting_plane(bim_points)                                                                                           #Get normal from bim_points
                plane2,normal2=best_fitting_plane(np.array(camera_coords[p]))                                                                           #Get normal from camera coordiantes
                ang=angle(normal1,normal2)                                                                                                              #Measure angle between the two normals 
                if pix_poly.area*abs(cos(ang))>maxp:                                                                                                    #Check if area of pixels is more than max
                    maxp=pix_poly.area*abs(cos(ang))                                                                                                    #replace max pixels with present pixels
                    best_pixels=sp_xy
                    best_img_name=img_name[p]
            except:
                pass
            
        try:                                                                                                                                            #add data to arrays
            bim_pixels.append(best_pixels)
            bim_img.append(best_img_name)
            bim_id.append(obj['bim_id'])
            bim_type.append(obj['type'])
            bim_number.append(i)
        except:
            pass
    
    return bim_pixels,bim_img,bim_id,bim_type,bim_number


def outputs(result):
    bim_pixels,bim_img,bim_id,bim_type,bim_number=[],[],[],[],[]
    for divo in range(len(result)):                                                                                                                     #Extract data to arrays
            try:
                bim_pixels=bim_pixels+result[divo][0]
                bim_img=bim_img+result[divo][1]
                bim_id=bim_id+result[divo][2]
                bim_type=bim_type+result[divo][3]
                bim_number=bim_number+result[divo][4]
            except:
                pass

    array=[]
    for i in range(len(bim_pixels)):
        new_dict={'id':bim_id[i],'number':bim_number[i],'type':bim_type[i],'img':bim_img[i],'pixels':bim_pixels[i]}                                     #Create new dict object frfom data
        array.append(new_dict)
    
    with open('./data/'+filename+'/interim/best_image.json', 'w') as outfile:                                                                           #Create best image json file
        json.dump(array, outfile)




pmatrix,img_names,offset,boundaries=inputs(filename)
pool = multiprocessing.Pool(processes=8)     # Create a multiprocessing Poolfor div in range(division):
result=pool.map(bim_to_img, range(len(boundaries)),chunksize=1)  # process data_inputs iterable with pool
outputs(result)

    
        

        






