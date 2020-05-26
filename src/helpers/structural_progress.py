import os
import sys
import json
import laspy
import time
import shapely.ops
import numpy as np
import multiprocessing
import shapely.geometry
from scipy.spatial import ConvexHull
from shapely.geometry import Polygon,Point






filename = sys.argv[1]

def pnt_to_coords(proj_mat,x,y,z):
    """ 
    Converts local coordinates to global coordinates with the help of 
    transformation matrix and gives the coordinates as the result.This equation is 
    just simple form of matrix multiplication of Proj matrix * inverse([x,y,z,1])
    """

    w=1/(proj_mat[12]*x+proj_mat[13]*y+proj_mat[14]*z+proj_mat[15])

    X=(proj_mat[0]*x+proj_mat[1]*y+proj_mat[2]*z+proj_mat[3])*w
    Y=(proj_mat[4]*x+proj_mat[5]*y+proj_mat[6]*z+proj_mat[7])*w
    Z=(proj_mat[8]*x+proj_mat[9]*y+proj_mat[10]*z+proj_mat[11])*w

    return X,Y,Z

def inputs(filename):
    """ 
    This is to input the BIM coordinates, progress json, point cloud and extract the required data.
    Two sets of data are being extracted. One set of data named obj_names,obj_vertices is extracted 
    to calculate structural progressand etract the boundaries of changed structure. Another set of
    data named rem_names,rem_vertices,rem_types is to get boundary of structural completed objects 
    whose further stages have not yet been completed
    """

    #Open the transformation matrix and extract the matrix as an array
    with open('./data/bim/tm.json') as f:
        proj_mat = json.load(f)
    proj_mat=proj_mat['tm']

    # Extract the required data from point cloud and the progrss from json file
    for fname in os.listdir('data/'+filename):
        if fname.endswith('.json') and 'tm' not in fname:
            ifc=open('data/'+filename+'/'+fname)
            ifc=json.load(ifc)
        if fname.endswith('.las'):
            infile=laspy.file.File('data/'+filename+'/'+fname)
            point_3d=np.vstack([infile.x,infile.y,infile.z,infile.red,infile.green,infile.blue]).T
        if fname.endswith('.json') and 'tm' in fname:
            f=open('data/'+filename+'/'+fname)
            proj_mat2 = json.load(f)
            proj_mat2=proj_mat2['tm']
    
    bim=open('./data/bim/bim.obj', 'r')                                                                                             #Opening BIM
    bim=bim.read()                                                                                                                  #Reading BIM                
    bim=bim.split('o ')                                                                                                             #Separating BIM to array of objects
    obj_names,obj_vertices,rem_names,rem_vertices,rem_types=[],[],[],[],[]                                                          #Initializing arrays to extract the data to
    for i in bim:                                                                                                                   #Reading each object from BIM
        k=i.splitlines()                                                                                                            #Separating each object to array of lines
    
        vertices=[]                                                                                                                 #Initialize array to add vertices of BIM object to
        for j in k:                                                                                                                 #Reading each line from object                    
            try:
                if j[0]=='v' and j[1]!='n':                                                                                         #Checking if line contains vertices
                    v=j.split(' ')                                                                                                  #Converting to array of coordinates                                                                                   
                    x,y,z=pnt_to_coords(proj_mat,float(v[1]),float(v[2]),float(v[3]))                                               #Convertng local coorinates to BIM coordinates
                    x,y,z=pnt_to_coords(proj_mat2,x,y,z-183)
                    vertices.append([x,y,z])                                                                                        #Appending the converted coordinates to vertices array
            except:
                pass
        try:
            if ifc[k[0]]['children'][0]['progress']!=100:                                                                           #Check if structure of object in progress json has not been completed
                obj_names.append(k[0])                                                                                              #Add BIM object id to obj_names array
                obj_vertices.append(vertices)                                                                                       #Add vertices to obj_vertices
            elif ifc[k[0]]['children'][0]['progress']==100 and ifc[k[0]]['progress']!=0 and 'slab' in ifc[k[0]]['type']:            #Check if structure is completed and if the other stages have not been completed
                rem_names.append(k[0])                                                                                              #Append obj id to rem_names
                rem_vertices.append(vertices)                                                                                       #Append vertices to rem_vertices
                rem_types.append(ifc[k[0]]['type'])                                                                                 #Append types from progress json to rem_types

        except:
            pass
    

    return obj_names,obj_vertices,point_3d,ifc,infile.header,rem_names,rem_vertices,rem_types





def calc(i):
    cloud_hulls,cloud_objs,cloud_vol,boundary,obj_type,vertices,set_points_xy=[],[],[],[],[],[],[]                                  #Initialize arrays                              
    maxx,minx,maxy,miny,maxz,minz=0,1000000000,0,10000000000,0,10000000000                                                          #Initialize max,min variables
    for j in obj_vertices[i]:                                                                                                       #Extracting x,y coordinates and max,min variables
        set_points_xy.append([j[0],j[1]])
        if j[2]>maxz:
            maxz=j[2]
        if j[2]<minz:
            minz=j[2]
        if j[0]<minx:
            minx=j[0]
        if j[0]>maxx:
            maxx=j[0]
        if j[1]<miny:
            miny=j[1]
        if j[1]>maxy:
            maxy=j[1]
    
    
            

    set_points_xy=list(set([tuple(sorted(t)) for t in set_points_xy]))                                                              #Set of points to eliminate duplicates
    sp_xy=[]
    hull=ConvexHull(set_points_xy)                                                                                                  #Applying convex hull to set of points
    for h_v in hull.vertices:                                                                                                       #Extracting coordinates of hull to an array
        sp_xy.append(set_points_xy[h_v])
    poly_xy=Polygon(sp_xy)                                                                                                          #Create polygon of extracted coordiantes


    point_3ds=point_3d[(point_3d[:,2]>= minz) & (point_3d[:,2]<=maxz)]                                                              #Filtering point cloud based on z coordinate
    point_3ds=point_3ds[(point_3ds[:,0]>= minx) & (point_3ds[:,0]<=maxx)]                                                           #Filtering point cloud based on x coordinate
    point_3ds=point_3ds[(point_3ds[:,1]>= miny) & (point_3ds[:,1]<=maxy)]                                                           #Filtering point cloud based on y coordinate                
    
    grid_maxz,grid_maxx,grid_maxy,grid_minz,grid_minx,grid_miny=maxz,maxx,maxy,minz,minx,miny                                       #Creating backups fro max,min variables                                                                                   
    points=[]
    volume=0
    

    if 'wall' in  ifc[obj_names[i]]['type'] or 'column' in ifc[obj_names[i]]['type']:                                               #Checking if object is vertical BIM element
        for point in point_3ds:                                                                                                     #Checking if each point lies within polygon
            ppp_xy=Point(point[0],point[1])

        
            if ppp_xy.within(poly_xy) == True:
                if minz<=point[2] and point[2]<=maxz:
                    points.append([point[0],point[1],point[2]])                                                                     #adding points to list if it lies within polygon
        
        dif=(grid_maxz-grid_minz)/50                                                                                                #Dividing vertical length into 50 grids
        
        
        volume=0
        points_boundary=[]
        if len(points)>0:                                                                                                           #Checking if points exist in the element
            grid_minz=grid_minz+dif
            points=np.array(points)                                                                                                 #Converting list of points to numpy array
            while grid_minz<grid_maxz:                                                                                              #Checking for each grid
                point_grid=points[(grid_minz-dif<=points[:,2]) & (points[:,2]<=grid_minz)]                                          #Extracting all points from grid
                if point_grid.shape[0]>0:                                                                                           #Checking points exist in grid
                    
                    points_boundary=points_boundary+point_grid[:,0:2].tolist()                                                      #Adding points to list
                    volume=volume+2                                                                                                 #Adding to volume 
                grid_minz=grid_minz+dif
        
        if len(points_boundary)>10 and volume<90:                                                                                  #Checking f points exist in element
            list_x,list_y=poly_xy.exterior.coords.xy                                                                               # Extrating x,y coordinates
            faces=[]
            for ext in range(len(list_x)-1):                                                                                       #Appending all sides of vertical element to list
                face=[]                                                                                                                 
                face.append([list_x[ext],list_y[ext],minz])                                                                                 
                face.append([list_x[ext],list_y[ext],(volume/100)*maxz])
                face.append([list_x[ext+1],list_y[ext+1],minz])
                face.append([list_x[ext+1],list_y[ext+1],(volume/100)*maxz])
                faces.append(face)
                

            
            boundary.append(faces)                                                                                                 #Adding all the data to initliazed arrays at the start
            obj_type.append(ifc[obj_names[i]]['type'])                                                                              
            cloud_vol.append(int(volume))                                                                                          
            cloud_hulls.append(vertices)                                                                                           
            cloud_objs.append(obj_names[i])                                                                                             



    
    elif ifc[obj_names[i]]['type']=='beam' or ifc[obj_names[i]]['type']=='slab':                                                    #Checking BIM element is horizontal element
        for point in point_3ds:                                                                                                     #Checking if each point lies within polygon
            ppp_xy=Point(point[0],point[1])

        
            if ppp_xy.within(poly_xy) == True:
                if minz<=point[2] and point[2]<=maxz:
                    vertices.append(point)
                    points.append([point[0],point[1],point[2]])
        dif_x=(grid_maxx-grid_minx)/10                                                                                              #Dividing x coordinates into 10 grids
        test_min=grid_miny
        test_max=grid_maxy
        volume=0
        cv=0
        points_boundary=[]
        if len(points)>0:
            points=np.array(points)
            grid_minx=grid_minx+dif_x
            while grid_minx<grid_maxx:
                point_grid_x=points[(grid_minx-dif_x<=points[:,0]) & (points[:,0]<=grid_minx)]
                grid_miny=test_min
                grid_maxy=test_max
                dif_y=(grid_maxy-grid_miny)/10                                                                                    #Dividing y coordinates into 10 grids
                grid_miny=grid_miny+dif_y
                while grid_miny<grid_maxy:
                    point_grid_y=point_grid_x[(grid_miny-dif_y<=point_grid_x[:,1]) & (point_grid_x[:,1]<=grid_miny)]
                    poly_grid=Polygon([[grid_minx,grid_miny],[grid_minx,grid_miny-dif_y],[grid_minx-dif_x,grid_miny-dif_y],[grid_minx-dif_x,grid_miny]])
                    poly_grid=poly_grid.intersection(poly_xy)
                    if poly_grid.geom_type=='Polygon':
                        cv=cv+1
                        if point_grid_y.shape[0]>0:                                                                              #Checking if point exists in grid
                            volume=volume+1                                                                                      #Adding to volume
                            points_boundary=points_boundary+point_grid_y[:,0:2].tolist()                                         #Adding points to list
                        
                            
                    grid_miny=grid_miny+dif_y
                grid_minx=grid_minx+dif_x
            
            if cv==0:
                volume=0
            else:
                volume=volume*(100/cv)                                                                                          #Adjusting volume based on number of viable grids
            if len(points_boundary)>10:                                                                                         #Filtering based on number of points in points_boundary
                bp=[]
                boundary_hull=ConvexHull(points_boundary)                                                                       #Extracting hull of boundary points
                for h_v in boundary_hull.vertices:
                    bp.append(points_boundary[h_v])                                                                             #Extracting boundary of hull
                poly_points=Polygon(bp)                                                                                         #Creating polygon of boundary hull
                b_p=poly_points.intersection(poly_xy)                                                                           #intersecting boundary polygon and bim polygon to elimnate no existent polygon area
                list_x,list_y=b_p.exterior.coords.xy                                                                            #Getting x,y coordinates as lists
                bp=[]
                

                """ 
                If the boundary of some elements is too large to exist in one image,then the boundary is to be 
                divided into smaller sections so that each section can be extracted separately.
                 """
                if ifc[obj_names[i]]['type']=='slab':
                    minbound_x=min(list_x)
                    maxbound_x=max(list_x)
                    minbound_y=min(list_y)
                    maxbound_y=max(list_y)
                    lx=maxbound_x-minbound_x
                    ly=maxbound_y-minbound_y
                    dif_boundx=(maxbound_x-minbound_x)/(lx//50+1)
                    dif_boundy=(maxbound_y-minbound_y)/(ly//50+1)
                    while minbound_x<maxbound_x: 
                        minbound_y=min(list_y)
                        while minbound_y<maxbound_y:
                            poly_bound=Polygon([[minbound_x,minbound_y],[minbound_x+dif_boundx,minbound_y],[minbound_x+dif_boundx,minbound_y+dif_boundy],[minbound_x,minbound_y+dif_boundy]])
                            bp_small=poly_bound.intersection(b_p)
                            try:
                                xb,yb=bp_small.exterior.coords.xy
                                bp_small=[]
                                for ext in range(len(xb)):
                                    bp_small.append([xb[ext],yb[ext],grid_maxz])                                                            #Etracting each section of slab
                                bp.append(bp_small)
                            except:
                                pass
                            minbound_y=minbound_y+dif_boundy
                        minbound_x=minbound_x+dif_boundx
                    
                
                else:
                    for ext in range(len(list_x)):
                        bp.append([list_x[ext],list_y[ext],grid_maxz])
                    bp=[bp]
                boundary.append(bp)
                obj_type.append(ifc[obj_names[i]]['type'])
                cloud_vol.append(int(volume))
                cloud_hulls.append(vertices)
                cloud_objs.append(obj_names[i])
            

    else:
        pd=0
        for point in point_3ds:
            ppp_xy=Point(point[0],point[1])

            if ppp_xy.within(poly_xy) == True:
                if minz<=point[2] and point[2]<=maxz:
                    pd=pd+1
                    if point[2]>grid_maxz:
                        grid_maxz=point[2]
                    if point[2]<grid_minz:
                        grid_minz=point[2]
                    if point[0]>grid_maxx:
                        grid_maxx=point[0]
                    if point[0]<grid_minx:
                        grid_minx=point[0]
                    if point[1]>grid_maxy:
                        grid_maxy=point[1]
                    if point[1]<grid_miny:
                        grid_miny=point[1]
        if pd>0:
            total=((grid_maxz-grid_minz)/(maxz-minz))+((grid_maxx-grid_minx)/(maxx-minx))+((grid_maxy-grid_miny)/(maxy-miny))
            volume=(total/3)*100
            boundary.append(["NULL"])
            obj_type.append(ifc[obj_names[i]]['type'])
            cloud_vol.append(int(volume))
            cloud_hulls.append(vertices)
            cloud_objs.append(obj_names[i])

                
        
    return cloud_objs,cloud_vol,cloud_hulls,obj_type,boundary



def outputs(result,ifc,header):
    cloud_hulls,cloud_objs,cloud_vol,obj_type,boundary=[],[],[],[],[]                                                                                       #Initializing arrays

    for divo in range(len(result)):                                                                                                                         #Extract results to necessary arrays
        cloud_objs=cloud_objs+result[divo][0]
        cloud_vol=cloud_vol+result[divo][1]
        cloud_hulls=cloud_hulls+result[divo][2]
        obj_type=obj_type+result[divo][3]
        boundary=boundary+result[divo][4]

    x,y,z,red,blue,green,object_id=[],[],[],[],[],[],[]                                                                                                     #Extarct values required fro point cloud
    for i in  range(len(cloud_objs)):
        for j in cloud_hulls[i]:
            x.append(j[0])
            y.append(j[1])
            z.append(j[2])
            red.append(j[3])
            green.append(j[4])
            blue.append(j[5])
            object_id.append(i)

        percentage=cloud_vol[i]                                                                                                                            #Adjusting percenatge for error 
        if percentage>=90:
            percentage=100

        
        ifc[cloud_objs[i]]['progress']=int(percentage/len(ifc[cloud_objs[i]]['children']))                                                                  #Adding progress for json file
        ifc[cloud_objs[i]]['children'][0]['progress']=percentage
    
    header = header                                                                                                                                         
    outfile=laspy.file.File('./data/'+filename+'/interim/bim_changes.las',mode='w',header=header)                                                           #Creating pont cloud and adding values to it
    outfile.define_new_dimension(name = 'object_id',data_type = 5, description = 'Object_id')
    outfile.object_id=object_id
    outfile.x = np.array(x)
    outfile.y = np.array(y)
    outfile.z = np.array(z)
    outfile.red = np.array(red)
    outfile.green= np.array(green)
    outfile.blue= np.array(blue)
    outfile.close()

    final=[]

    for i in range(len(cloud_objs)):                                                                                                                      #Creating json file to store boundaries
        new_object={'bim_id':cloud_objs[i],'type':obj_type[i],'boundary':boundary[i]}                                                                     #Creating object to be added to json file
        final.append(new_object)
    
    return ifc,final

def bim_boundary(final,rem_names,rem_vertices,rem_types):
    """ 
    This function is just a customized version of part of code from 'calc' function to get boundaries of 
    bim objects from progres file where the structural progress is already 100% but further stages have not been 
    completed.
     """
    for i in range(len(rem_names)):
        set_points_xy=[]
        maxx,minx,maxy,miny,maxz,minz=0,1000000000,0,10000000000,0,10000000000
        for j in rem_vertices[i]:
            set_points_xy.append([j[0],j[1]])
            if j[2]>maxz:
                maxz=j[2]
            if j[2]<minz:
                minz=j[2]
            if j[0]<minx:
                minx=j[0]
            if j[0]>maxx:
                maxx=j[0]
            if j[1]<miny:
                miny=j[1]
            if j[1]>maxy:
                maxy=j[1]


        

        set_points_xy=list(set([tuple(sorted(t)) for t in set_points_xy]))
        sp_xy=[]
        hull=ConvexHull(set_points_xy)
        for h_v in hull.vertices:
            sp_xy.append(set_points_xy[h_v])
        poly_xy=Polygon(sp_xy)
        if 'slab' in rem_types[i] or 'beam' in rem_types[i]:
            
            list_x,list_y=poly_xy.exterior.coords.xy
            bp=[]
            
            if 'slab' in rem_types[i]:
                minbound_x=min(list_x)
                maxbound_x=max(list_x)
                minbound_y=min(list_y)
                maxbound_y=max(list_y)
                lx=maxbound_x-minbound_x
                ly=maxbound_y-minbound_y
                dif_boundx=(maxbound_x-minbound_x)/(lx//50+1)
                dif_boundy=(maxbound_y-minbound_y)/(ly//50+1)
                while minbound_x<maxbound_x: 
                    minbound_y=min(list_y)
                    while minbound_y<maxbound_y:
                        poly_bound=Polygon([[minbound_x,minbound_y],[minbound_x+dif_boundx,minbound_y],[minbound_x+dif_boundx,minbound_y+dif_boundy],[minbound_x,minbound_y+dif_boundy]])
                        bp_small=poly_bound.intersection(poly_xy)
                        try:
                            xb,yb=bp_small.exterior.coords.xy
                            bp_small=[]
                            for ext in range(len(xb)):
                                bp_small.append([xb[ext],yb[ext],grid_maxz])
                            bp.append(bp_small)
                        except:
                            pass
                        minbound_y=minbound_y+dif_boundy
                    minbound_x=minbound_x+dif_boundx
                
            
            else:
                for ext in range(len(list_x)):
                    bp.append([list_x[ext],list_y[ext],maxz])
                bp=[bp]
            new_object={'bim_id':rem_names[i],'type':rem_types[i],'boundary':bp}
            final.append(new_object)
        if 'column' in rem_types[i] or 'wall' in rem_types[i]:
            list_x,list_y=poly_xy.exterior.coords.xy
            faces=[]
            for ext in range(len(list_x)-1):
                face=[]
                face.append([list_x[ext],list_y[ext],minz])
                face.append([list_x[ext],list_y[ext],maxz])
                face.append([list_x[ext+1],list_y[ext+1],minz])
                face.append([list_x[ext+1],list_y[ext+1],maxz])
                faces.append(face)
            new_object={'bim_id':rem_names[i],'type':rem_types[i],'boundary':faces}
            final.append(new_object)  

    return final


obj_names,obj_vertices,point_3d,ifc,header,rem_names,rem_vertices,rem_types=inputs(filename)                                                     #Calling input function

pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())     # Create a multiprocessing Poolfor div in range(division):
result=pool.map(calc, range(len(obj_names)),chunksize=1)  # process data_inputs iterable with pool
ifc,final=outputs(result,ifc,header)
final=bim_boundary(final,rem_names,rem_vertices,rem_types)
with open('./data/'+filename+'/interim/progress_structural.json', 'w') as outfile:                                                               #Writing to structural json file
    json.dump(ifc, outfile)
with open('./data/'+filename+'/interim/boundaries.json', 'w') as outfile:                                                                          #Writing to boundaries json file
    json.dump(final, outfile)










                        











