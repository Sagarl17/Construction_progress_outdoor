# Construction progress-outdoor module

This repository contains the code for predicting the outdoor progress of each component in BIM

# Steps For Installation:

```bash
git clone https://git.xyzinnotech.com/gopinath/construction_progress_outdoor.git
cd construction_progress_outdoor
pip install -r requirements-cpu.txt (If GPU is not available)
               or
pip install -r requirements-gpu.txt (If GPU is available)

```


# Initial setup:
```bash
1.Download the model from the following link and place it in models folder
    https://drive.google.com/open?id=1nXq75Aru5HouRyEmAWzHceMe4jRo3ptv

2.Download the bim folder from the following link and replace the bim folder in data:
    https://drive.google.com/open?id=1_FKSmM0Q1EdYP0PbxfQUbbe0YwUNVgoR

3.Create a dataset folder inside the "data" folder and place the following data inside the dataset folder
    *  "Images" folder containing all drone images pertaining to the date
    *  Progress of construction in json format upto previous date
    *  Pointcloud of the construction in ".las" format
    *  Offset file generated by pix4d
    *  P-matrix file generated by pix4d
    *  Transformation matrix of the pointcloud for that date

```

# How to test for the new dataset:

```bash
python main.py "dataset_folder_name" "date of dataset" "previous tracked date"

If the dataset folder is named 'oct4',the date of dataset is october 4,2019 and previous tracked date is october 1,2019,then it should be run in following way:

    python main.py oct4 04-10-2019 01-10-2019
```
# Where are my results stored :

```bash
The progress output will generated in data/external as "oct4.json".The report will be genearted in reports as "oct4.txt". (assuming the dataset folder name is oct4 )
```


