import os
import sys
import json
import laspy
import runpy
from src.helpers import logger,classify

logger = logger.setup_custom_logger('myapp')

filename = sys.argv[1]
today_date=sys.argv[2]
previous_date=sys.argv[3]


if not(os.path.exists('./data/'+filename+'/interim')):
    os.mkdir('./data/'+filename+'/interim')

if not(os.path.exists('./data/'+filename+'/interim/extracted_images')):
    os.mkdir('./data/'+filename+'/interim/extracted_images')

if not(os.path.exists('./data/'+filename+'/interim/classified_images')):
        os.mkdir('./data/'+filename+'/interim/classified_images')



################################################################################################################

#Structural progress

logger.info('Structural progress Calculation: Started')

if not(os.path.exists('./data/'+filename+'/interim/boundaries.json')):
   runpy.run_path(path_name='src/helpers/structural_progress.py')
    


logger.info('Structural progress Calculation: Finished')
################################################################################################################

#Finding Best BIM images

logger.info('Finding Best BIM Images: Started')

if not(os.path.exists('./data/'+filename+'/interim/best_image.json')):
    runpy.run_path(path_name='src/helpers/bim_image.py')
   

logger.info('Finding Best BIM Images: Finished')
################################################################################################################

#Extracting Best BIM images

logger.info('Extracting Best BIM Images: Started')

runpy.run_path(path_name='src/helpers/extract_image.py')


logger.info('Extracting Best BIM Images: Finished')
################################################################################################################

#Classifying Extracted BIM images
logger.info('Classifying Best BIM Images : Started')
if not(os.path.exists('./data/external/'+filename+'.json')):
    runpy.run_path(path_name='src/helpers/classify_multi.py')

logger.info('Classifying Best BIM Images : Finished')

################################################################################################################

#Updating Construction Dates

logger.info('Updating Construction Dates: Started')

exec(open('./src/helpers/adding_dates.py').read())

logger.info('Updating Construction Dates: Finished')

################################################################################################################

#Providing Analysis based on Project Plan

logger.info('Project Paln Analysis: Started')

if not(os.path.exists('./reports'+filename+'.txt')):
    exec(open('./src/helpers/insight.py').read())

logger.info('Project Plan: Finished')