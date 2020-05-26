import datetime
import time
import psutil
import numpy as np

def print_time():
	""" For printing DATETIME """
	return datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')

def memcalc():
	mem='RAM: '+str(psutil.virtual_memory()[2])+'%'
	return mem

def cpucalc():
	cpu='CPU: '+str(psutil.cpu_percent(interval=None, percpu=False))+'%'
	return cpu

def PCA(data, correlation = False, sort = True):
    mean = np.mean(data, axis=0)
    data_adjust = data - mean
    if correlation:
        matrix = np.corrcoef(data_adjust.T)
    else:
        matrix = np.cov(data_adjust.T) 
    eigenvalues, eigenvectors = np.linalg.eig(matrix)
    if sort:
        sort = eigenvalues.argsort()[::-1]
        eigenvalues = eigenvalues[sort]
        eigenvectors = eigenvectors[:,sort]

    return eigenvalues, eigenvectors


def best_fitting_plane(points, equation=False):
    if len(points[0])==2:
        b = np.zeros((points.shape[0],points.shape[1]+1))
        b[:,:-1] = points
        points=b
    w, v = PCA(points)
    normal = v[:,2]
    point = np.mean(points, axis=0)
    if equation:
        a, b, c = normal
        d = -(np.dot(normal, point))
        return a, b, c, d
    else:
        return point, normal   


def angle(v1, v2):
    angle = np.arccos(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)))
    return angle



