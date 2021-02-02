#====================================================================
# MSI-segmentation CONFIGURATION
#====================================================================

#====================================================================
# general
#====================================================================
# Locate the main input .csv data for pixel data and mass list import.  
# read data in example folder for demonstration. Change them for your application. 
path = os.path.abspath(os.path.dirname(os.getcwd()))
InputDir = os.path.join(path, 'example', 'kidney.csv')  # PCA input
#InputDir_umap =                                        # UMAP input

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
RandomState = 20210131

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

# L0.2 UMAP + HDBSCAN
#=====================
# Default hyperparameters: as follows. More info see: https://umap-learn.readthedocs.io/en/latest/
n_neighbors = 12
min_dist = 0.025

# HDBSCAN hyperparameters: more info see: https://hdbscan.readthedocs.io/en/latest/parameter_selection.html
min_cluster_size = 2550
min_samples = 30
cluster_selection_method = 'leaf'

# run with soft clustering mode? More info see: https://hdbscan.readthedocs.io/en/latest/soft_clustering.html
HDBSCAN_soft = False

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

# Assign number of images per row for montage visualization. (Default setting: same as span)
ncols_L1 = span

### Outlier pattern detection (Ward's hierarchical clustering (HC) + PCA loadings):
# a thresholding to remove hotspots for HC
thre_percent = 0.99

# exclude pixels on glass slide for features for HC
# this has to be hardcoded, a list of dictionaries. index of results: labels
glass_slide_labels = [{'No.3_10_0': [0, 4]}]  

# HC parameter
HC_method='ward'
HC_metric='euclidean'

# threshoding to trim the dendrogram
# this has to be determined from the dendrogram
thre_dist = 78

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

# select ion images, input a list of No. (original index in L1.2 results)
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
# L3.0: Majority vote based finishing
# 1. construction of co-occurrence matrix 2. hirarichical clustering (HC)
# -> constructe co-occurrence with sparse matrix
# -> TruncatedSVD dimensionality reduction
# -> GMM batching
# -> HC 
# -> HC visualization & finishing
#====================================================================
# Locate the ensemble results dir: 1. ensemble clustering reuslts and/or 2. thresholding results, *need hard-coding 
EnOutputDir = os.path.join(path, 'example', 'output', 'ensemble results', 'pixel_ensemble_label.csv')

# threshold for TruncatedSVD component selection
SVD_threshold = 0.99

# this is estimated from the binary co-occurrence matrix
n_cluster = 9

#====================================================================
# L3.1: visualize ensemble results
#====================================================================
# Locate the updated ensemble results dir: 1. ensemble clustering reuslts and/or 2. thresholding results, 3. auto finishing result *need hard-coding 
EnOutputDir = os.path.join(path, 'example', 'output', 'ensemble results', 'pixel_ensemble_label2.csv')

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

# simplify the auto_assemble results 
selection_ensem = [
    {'name': 'GlassSlide',   'label': 1, 'segment': {'auto_assemble': [0, 1]}},
    {'name': 'OuterLayer',   'label': 2, 'segment': {'auto_assemble': [4]}},
    {'name': 'Cortex',       'label': 3, 'segment': {'auto_assemble': [2, 3]}},
    {'name': 'Medulla',      'label': 7, 'segment': {'auto_assemble': [6]}},
    {'name': 'Pelvis',       'label': 8, 'segment': {'auto_assemble': [5]}},
    {'name': 'Unknown',      'label': 10,'segment': {'auto_assemble': [7]}},
    {'name': 'InnerCortex',  'label': 6, 'segment': {'thresholding_119': [1],
                                                     'auto_assemble': [8]}},
    {'name': 'Lvessels',     'label': 0, 'segment': {'thresholding_118': [1]}}
]

# one example to manually select segments from ensemble results
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
'''