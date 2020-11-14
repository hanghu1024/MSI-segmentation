#====================================================================
# MSI-segmentation CONFIGURATION
#====================================================================

#====================================================================
# general
#====================================================================
# Locate the main input .csv data. 2d array pixel.csv, read 'kidney.csv' in example folder by default
path = os.path.abspath(os.path.dirname(os.getcwd()))
InputDir = os.path.join(path, 'example', 'kidney.csv')

# Locate the MassList .csv data (Default seeting: 0 -> no mass list), read 'kidney_MassList' in example folder by default
MassList_FileDir = os.path.join(path, 'example', 'kidney_MassList.csv')

# Locate the output folder. (Default setting: 0 -> use parent directory) 
OutputFolder = 0

# For the whole image, AspectRatio = height/width. (Default setting: 1)
AspectRatio = 4.5/7

# Assign a colormap for ion images. (Default setting: 'hot')
colormap = 'hot'

# Assign a colorbar for single ion image. (Default setting: 0, no colorbar)
colorbar = 0

# Assign ticks for single ion image. (Default setting: 0, no ticks)
ticks = 0

# dpi for mosaic plot saving. (Default setting: 600)
dpi = 600

# Random seed: assgin a constant to get repeatable result. (Default setting: 0)
RandomState = 20200808

#====================================================================
# L0: exploratory analysis
#====================================================================

# L0.0 show ion images
#=====================
# Assign number of images per row for mosaic visualization. (Default setting: 15)
ncols_L0 = 15

# L0.1 PCA
#=====================
# Threshold condition 1: number of PCs. (Default setting: 50)
MaxPCs = 50

# Threshold condition 2: cumulative percentage of variance explained. (Default setting: 75%)
threshold = 0.85

# L0.2 UMAP
#=====================
# Default hyperparameters: as follows. More info see: https://umap-learn.readthedocs.io/en/latest/
n_neighbors = 15
min_dist = 0.1

#====================================================================
# L1: multivariate clustering
# could be tuned with different parameters
#====================================================================
# Locate the L0 output pixel_rep.csv data, *need hard-coding
L0outputDir = os.path.join(path, 'example', 'output', 'exploratory results', 'pixel_rep.csv')

# Number of mixture components in GMM. Please estimate from UMAP plot. (Default setting: 10) 
n_components = 10

# Span. (Default setting: 5 around the n_components)
span = 5 # odd number

# Repeat. (Default setting: only do once)
repeat = 1 # integer

# Assign number of images per row for mosaic visualization. (Default setting: same as span)
ncols_L1 = span

#====================================================================
# L1.3: interactively show the ensemble results
#====================================================================
# Locate the L1 output pixel_label.csv data, *need hard-coding
L1outputDir = os.path.join(path, 'example', 'output', 'multivariate clustering', 'pixel_label.csv')

# Define the size of canvas. Default is 1000. Since aspect_ratio is fixed, so it defines both width and length
canvas_width_L13 = 1000  

# number of imgs per row. Default is the same as span
ncols_L13 = span 

#====================================================================
# L2: univariate thresholding and interactively show the results
#====================================================================
# number of segments in multi-Otsu, default is 5. A parameter higher than 5 will make calculation very very slow!!
n_classes = 5

# select ion images, input a list of No. 
index = [118, 119]

# colormap for segments in this section
colormap_thresholding = 'Paired'

# define the size of canvas. Default is 800. Since aspect_ratio is fixed, so it defines both width and length
canvas_width_L2 = 1000

#====================================================================
# L2.3: assembly univariate thresholding results
#====================================================================
# Locate the L2 and L1 output pixel_label.csv data, *need hard-coding
L2outputDir = os.path.join(path, 'example', 'output', 'univariate thresholding', 'pixel_label.csv')
# make sure L1.3 and L2.3 are on the same page 
L1outputDir = os.path.join(path, 'example', 'output', 'multivariate clustering', 'pixel_label.csv')



# segment selection using one dictionary. *need hard-coding
'''
fix your format

selection = {'118': [4],
             '119': [2, 3, 4]}

keys: strs of ion image index. values: a list of indexes of segments to be labeled as 1.
'''

selection_thre = {
    '118': [4],
    '119': [2, 3, 4]
}


#====================================================================
# L3.1: visualize ensemble results
#====================================================================
# Locate the ensemble results dir: 1. ensemble clustering reuslts and/or 2. thresholding results, *need hard-coding 
EnOutputDir = os.path.join(path, 'example', 'output', 'ensemble results', 'pixel_ensemble_label.csv')

# Define the size of canvas. Default is 1000. Since aspect_ratio is fixed, so it defines both width and length
canvas_width = 1000  

# number of imgs per row. Default is the same as span
ncols_L3 = span 


#====================================================================
# L3.2: assemble ensemble results
#====================================================================
# if despike. (Default setting: 1 -> yes/ or 0 -> no)
RemoveSpike = 1

# selection. *need hard-coding
'''
principle 1: from top to bottom, overwrite pixels when go down
principle 2: when multiple segments are selected, take the union set
principle 3: fix your format as follows
selection = [
    {'name': 'GlassSlide',   'label': 1, 'segment': {'No.4_11_0': [0, 5, 8]}},
    {'name': 'OuterLayer',   'label': 2, 'segment': {'No.15_12_2': [5]}},
    {'name': 'OuterCortex',  'label': 3, 'segment': {'No.15_12_2': [1,2]}},
    {'name': 'InnerCortex',  'label': 6, 'segment': {'thresholding_119': [1], 
                                                     'No.2_9_0': [2]}}
]
selection is a list of dictionaries. 
Each dictionary represents a segment, with 3 keys: 'name', 'label' and 'segment':
'name' value is a str. 
'label' value is an int. This is the label you assign to this group of pixels. The corresponding color is shown in colorbar. 
'segment' value is another dictionary, where keys are column names in pixel_label dataframe columns, values are labels you select there. 
'''
selection_ensem = [
    {'name': 'GlassSlide',   'label': 1, 'segment': {'No.3_10_0': [0, 5, 8]}},
    {'name': 'OuterLayer',   'label': 2, 'segment': {'No.4_11_0': [8]}},
    {'name': 'OuterCortex',  'label': 3, 'segment': {'No.4_11_0': [1, 4, 5, 10]}},
    {'name': 'InnerCortex',  'label': 6, 'segment': {'thresholding_119': [1], 
                                                     'No.2_9_0': [2, 5]}},
    {'name': 'OuterMedulla', 'label': 7, 'segment': {'No.4_11_0': [6,2]}},
    {'name': 'InnerMedulla', 'label': 9, 'segment': {'No.5_12_0': [2, 9]}},
    {'name': 'Pelvis',       'label': 8, 'segment': {'No.3_10_0': [9]}},
    {'name': 'Unknown',      'label': 10,'segment': {'No.2_9_0': [8]}},
    {'name': 'Lvessels',     'label': 0, 'segment': {'thresholding_118': [1]}}
]

