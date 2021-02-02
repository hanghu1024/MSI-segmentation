#===========================================
# import modules, defs and variables
#===========================================
exec(open("./external.py").read())
exec(open("./defs.py").read())
exec(open("./config.py").read())

print('Finish modules, defs and variables import')

#===========================================
# import data 
#===========================================
df_pixel_label = pd.read_csv(EnOutputDir)

print('Finish pixel raw data import')

#===========================================
# L3.2 data process
#===========================================
pixel_label = df_pixel_label.values.astype(int)

# parse dimension
NumLine = np.max(pixel_label[:,0])+1
NumSpePerLine = np.max(pixel_label[:,1])+1
# parameter for plotting
aspect = AspectRatio*NumSpePerLine/NumLine
# relabel pixels

# organize img
img = pixel_label.T.reshape(pixel_label.shape[1], NumLine, NumSpePerLine)

# make folders for final segmentation
OutputFolder = locate_OutputFolder2(EnOutputDir)
OutputFolder = locate_OutputFolder3(OutputFolder, 'final segmentation')
os.mkdir(OutputFolder)

# process the selection input
names = []
labels = []
segments = []
for i in selection_ensem:
    names.append(i['name'])
    labels.append(i['label'])
    segments.append(i['segment'])
    
print('Finish L3 data process, next step: assembly and plotting')

#===========================================
# L3.2 assembly the final segmentation and plot
#===========================================
# 1. initiate the canvas
img_seg=np.zeros(shape=(NumLine, NumSpePerLine))
img_seg[:,] = np.nan
    
# 2. segments[k] is a dic for that segment, do all works in each segment
for k in range(len(segments)): 
    StaTime = time.time()
    
    key_list = list(segments[k].keys())
    
    # organize the boolean index for a segment by traversing
    # initiate the zeros boolean, then accumulate orset for all dics 
    boolean = np.zeros(NumLine*NumSpePerLine, dtype=bool)
    # then traverse
    for i in key_list: # in each series
        # i -> key df_pixel_label[i] -> df series, segments[k][i] -> value (all selected labels in that df series) 
        current_segmentation = np.isin(df_pixel_label[i], segments[k][i])
        boolean = boolean|current_segmentation # update boolean
        
    # initiate the meta_seg for despike, which deals with 2d array
    if RemoveSpike == 1:
        meta_seg = np.zeros(shape=(NumLine, NumSpePerLine))
        meta_seg[boolean.reshape(NumLine, NumSpePerLine)] = 1 # draw out segments you selected
        meta_seg_despike = despike.clean(meta_seg)
        # transfer the despike segment onto canvas
        img_seg[meta_seg_despike == 1] = labels[k]
    else:
        img_seg[boolean.reshape(NumLine, NumSpePerLine)] = labels[k]
    
    SpenTime = (time.time() - StaTime)
    print('{}/{}, finish processing "{}" segment, running time is: {} s'.format(k+1, len(segments), names[k], round(SpenTime, 2)))

# 3. remove the np.nan if existing
try:
    indice = np.where(np.isnan(img_seg))

    # loop in the np.nan list
    for i in range(indice[0].shape[0]):       
        #current_pixel = img_seg[indice[0][i], indice[1][i]]
        # find the neighborhood
        current_window = img_seg[indice[0][i]-1 : indice[0][i]+2, indice[1][i]-1 : indice[1][i]+2]  # no padding
        
        # take the majority vote
        values, counts = np.unique(current_window, return_counts=True)
        img_seg[indice[0][i], indice[1][i]] = values[np.argmax(counts)]
except:
    pass

# 4. plot 
fig = plt.figure()
fig.subplots_adjust(hspace= 0, wspace=0.01, right=0.75)
ax = fig.add_subplot()
im = ax.imshow(img_seg, cmap=cm.tab20, aspect = aspect, vmin=0,vmax=19)
ax.set_xticks([])
ax.set_yticks([])

# colorbar
cbar_ax = fig.add_axes([0.76,0.1,0.01,0.8])
cbar = fig.colorbar(im, cax=cbar_ax, ticks=[0.5,1.4,2.3,3.3,4.3,5.1,6.2,7,8.1,9,10,10.9,11.8,12.7,13.6,14.7,15.6,16.6,17.5,18.5])
# take care tick labels
ticklabels = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19]
for i in labels:
    index = labels.index(i)
    title = str(i) + '_' + names[index]
    ticklabels[ticklabels.index(i)] = title
cbar.ax.set_yticklabels(ticklabels) #hard code 
cbar.ax.tick_params(labelsize= 8)

SaveDir = OutputFolder + '\\final_segmentation_map.png'
plt.savefig(SaveDir, dpi=300)
plt.close()

print('final segmentation map is ready, please check output results at: \n{}'.format(OutputFolder))
