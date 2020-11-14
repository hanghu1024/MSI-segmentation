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
df_pixel_label_thresholding = pd.read_csv(L2outputDir)
df_pixel_label_clustering = pd.read_csv(L1outputDir)

print('Finish pixel raw data import')

#===========================================
# L2.3 data preprocess
#===========================================
# parse info
NumLine = int(np.max(df_pixel_label_thresholding['line_index']) + 1)
NumSpePerLine = int(np.max(df_pixel_label_thresholding['spectrum_index']) + 1)

# parameter for plotting
aspect = AspectRatio*NumSpePerLine/NumLine

# data organization
pixel_label_thresholding = df_pixel_label_thresholding.values.astype(np.int)
img = pixel_label_thresholding.T.reshape(pixel_label_thresholding.shape[1], NumLine, NumSpePerLine)
columns = df_pixel_label_thresholding.columns.values
keys = list(selection_thre.keys())

# locate Output folder
OutputFolder_thresholding = locate_OutputFolder4(L2outputDir)
OutputFolder = locate_OutputFolder2(L2outputDir)
# make a file for next step, ensemble results
OutputFolder_final = locate_OutputFolder3(OutputFolder, 'ensemble results')
os.mkdir(OutputFolder_final)

print('Finish L2.3 data processing, next step: select segments and despike')

#===========================================
# L2.3 select (merge) segments and despike
#===========================================
img_binary_segs = np.empty([0, NumLine, NumSpePerLine])

for i in keys:
    # binary it
    img_work = img[np.where(columns==i)[0][0]].copy()  # with [0][0], it returns an integer then 
    img_work[~np.isin(img_work, selection_thre[i])] = 0 
    img_work[np.isin(img_work, selection_thre[i])] = 1
    
    #despike
    img_work_despike = despike.clean(img_work)
    img_binary_segs = np.append(img_binary_segs, img_work_despike.reshape(1, NumLine, NumSpePerLine), axis=0)
    print('{}/{} img is done'.format(i, keys))
    
print('Finish L2.3 image processing, binary segments are ready')

#===========================================
# L2.3 plot and save
#===========================================
# parameters for plt.plot:
w_fig = 10 # default setting
ncols = 3 # default setting
nrows = math.ceil((img_binary_segs.shape[0])/ncols)
h_fig = w_fig * nrows * (AspectRatio + 0.16) / ncols # 0.2 is the space for title parameters

fig = plt.figure(figsize=(w_fig, h_fig))                 
fig.subplots_adjust(hspace= 0, wspace=0.01, right=0.95)
for i in range(img_binary_segs.shape[0]):
    ax = fig.add_subplot(nrows, ncols, i+1)
    im = ax.imshow(img_binary_segs[i], cmap=colormap_thresholding, aspect = aspect, vmin=0,vmax=11)
    ax.set_xticks([])
    ax.set_yticks([])
    
    # title
    ax.set_title(keys[i], pad=5, fontsize = 10)

# colorbar
cbar_ax = fig.add_axes([0.96,0.1,0.01,0.8])
cbar = fig.colorbar(im, cax=cbar_ax, ticks=[0.5,1.4,2.3,3.2,4.1,5,5.9,6.85,7.8,8.7,9.6,10.5, 11.4])
cbar.ax.set_yticklabels([0,1,2,3,4,5,6,7,8,9,10,11]) #hard code 
cbar.ax.tick_params(labelsize=10)

# save
SaveDir = OutputFolder_thresholding + '\\univariate thresholding results.png'
plt.savefig(SaveDir, dpi=dpi)
plt.close()

print('L2.3 plotting is done, please check output results at: \n{}'.format(OutputFolder_thresholding))

#===========================================
# L2.3 conbine results with multivariate clustering and save .csv file
#===========================================
# flatten the data
pixel_thresholding_binary_labels = img_binary_segs.reshape(img_binary_segs.shape[0], -1).T

# combine labels from clustering and thresholding
df_pixel_label_ensemble = df_pixel_label_clustering.copy()

for i in range(len(keys)):
    title = 'thresholding_'+keys[i]
    df_pixel_label_ensemble[title] = pixel_thresholding_binary_labels[:,i]

# save it
SaveDir = OutputFolder_final + '\\pixel_ensemble_label.csv'
df_pixel_label_ensemble.to_csv(SaveDir, index=False, sep=',')

print('ensemble results for both multivariate and univariate analysis is ready, please check output results at: \n{}'.format(OutputFolder_final))

