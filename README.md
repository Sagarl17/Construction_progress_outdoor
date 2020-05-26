# Construction_progress_outdoor


pip install -r requirements-cpu.txt (If GPU is not available)
               or
pip install -r requirements-gpu.txt (If GPU is available)

**This code works only with Phoenix project **

Download the model from link below and place it in the models folder

https://drive.google.com/open?id=1nXq75Aru5HouRyEmAWzHceMe4jRo3ptv

Download the bim folder from the following link and replace the bim folder in data:

https://drive.google.com/open?id=1_FKSmM0Q1EdYP0PbxfQUbbe0YwUNVgoR

A dataset folder containing the following things should be placd in the data folder:
    
*  "Images" folder containing all drone images pertaining to the date
*  Progress of construction in json format upto previous date
*  Pointcloud of the construction in ".las" format
*  Offset file generated by pix4d
*  P-matrix file generated by pix4d
*  Transformation matrix of the pointcloud for that date

    
Then the code should be run in the following way:

python main.py "dataset_folder_name" "date of dataset" "previous tracked date"

If the folder is named oct4,the date of dataset is october 4,2019 and previous tracked date is october 1,2019,then it should be run in following way:

python main.py oct4 04-10-2019 01-10-2019

The progress output will be generated in the external folder with the name of the folder in the external folder. A report with the same name will be generated in the reports folder 