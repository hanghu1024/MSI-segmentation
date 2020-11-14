#===========================================
# DEFS MSI-segmentation
#===========================================

## General functions
# 0. locate output folders 
'''
Series of defs work for different circumstances, some return 'parent directory', some make 
a folder in 'parent directory', and some avoid overwirting when making folders. Could be organized.
1. return an output folder directory by locating the parent directory of 'input .csv', profilerate if same name folder exists.
   hard code with respect to 'output'
2. return the parent parent diretory (namely 'output') of 'input directory', input is usually an output of program
3. return an output folder directory in 'a designed folder', profilerate if same name folder exists.
   soft code
4. return the parent directory of 'input directory', input is usually an output of program
'''
def locate_OutputFolder1(InputDir): 
    InputFolder = InputDir.replace(InputDir.split('\\')[-1], '')
    f = []
    for (dirpath, dirnames, filenames) in os.walk(InputFolder):
        f.extend(dirnames)
        break
    
    # check if 'ouput' name exsits
    ii = 0 
    for foldernames in f:
        if foldernames.split('_')[0] == 'output':
            ii += 1
    # determine the OutputFolder dir
    if ii == 0:
        OutputFolder = InputFolder + 'output'
    else:
        OutputFolder = InputFolder + 'output' + '_' + str(ii)
    return OutputFolder

def locate_OutputFolder2(L0outputDir):
    L0outputDir = L0outputDir.replace('\\'+L0outputDir.split('\\')[-1], '')
    OutputFolder = L0outputDir.replace('\\'+L0outputDir.split('\\')[-1], '')
    return OutputFolder

def locate_OutputFolder3(OutputFolder, folder_name): # folder_name = 'univariate thresholding' or 'multivariate clustering'
    f = []
    for (dirpath, dirnames, filenames) in os.walk(OutputFolder):
        f.extend(dirnames)
        break
        
    # check if folder_name exsits
    ii = 0 
    for foldernames in f:
        if foldernames.split('_')[0] == folder_name: 
            ii += 1
    # determine the folder_name dir
    if ii == 0:
        OutputFolder = OutputFolder + '\\' + folder_name
    else:
        OutputFolder = OutputFolder + '\\' + folder_name + '_' + str(ii)
    return OutputFolder

def locate_OutputFolder4(L0outputDir):
    OutputFolder = L0outputDir.replace('\\'+L0outputDir.split('\\')[-1], '')
    return OutputFolder

# 1. locate the nearest element from an array with respect to a specific value
def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return array[idx]

# 2. count the strs which exist in df columns, but decorated by '_' (and usually index)
def retrace_columns(df_columns, keyword): # df_columns: nparray of df_columns. keyword: str
    counts = 0
    for i in df_columns:
        element = i.split('_')
        for j in element:
            if j == keyword:
                counts +=1
    return counts

# 3. relabel segments with respec to pixel number per segment
'''
input is df_pixel_label, with spatial index
output is np array, without spatial index
'''
def relabel(df_pixel_label):
    pixel_relabel = np.empty([df_pixel_label.shape[0],0])
    
    for i in range(2, df_pixel_label.shape[1]):
        column = df_pixel_label.iloc[:,i].value_counts() # pd.series
        labels_old = column.index.values.astype(int)
        labels_new = np.linspace(0,labels_old.shape[0]-1,labels_old.shape[0]).astype(int)
        column_new = df_pixel_label.iloc[:,i].replace(labels_old, labels_new) # pd.series
        pixel_relabel = np.append(pixel_relabel, column_new.values.astype(int).reshape(df_pixel_label.shape[0],1), axis = 1)
    return pixel_relabel

## L1
# 0. generate n_component np.array, with respect to the estimated n_class and assigned span
def generate_nComponentList(n_class, span):
    n_component = np.linspace(n_class-int(span/2), n_class+int(span/2), span).astype(int)
    return n_component

# plottings are not written as defs
#===========================================
