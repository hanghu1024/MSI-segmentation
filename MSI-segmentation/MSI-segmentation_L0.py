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
df_pixel = pd.read_csv(InputDir, header = None) # use pandas, cause the print is interpretable
if MassList_FileDir != 0: 
    df_MassList = pd.read_csv(MassList_FileDir, header = None)
    MassList = df_MassList.values.astype(np.float64)

print('Finish pixel raw data import')

#===========================================
# data processing and manipulate
#===========================================
# data organization
pixel = df_pixel.values.astype(np.float64)

# feature
df_pixel_feature=df_pixel.drop([0,1],axis=1)
pixel_feature=df_pixel_feature.values.astype(np.float64)
pixel_feature_std = SS().fit_transform(pixel_feature)

# parse info
NumLine = int(np.max(df_pixel[0]) + 1)
NumSpePerLine = int(np.max(df_pixel[1]) + 1)

# organize img
img = pixel.T.reshape(pixel.shape[1], NumLine, NumSpePerLine)

# parameter for plotting
aspect = AspectRatio*NumSpePerLine/NumLine

# make folders for following modules
if OutputFolder == 0:
    OutputFolder = locate_OutputFolder1(InputDir)

os.mkdir(OutputFolder)                            # make output folder
os.mkdir(OutputFolder + '\\ion images')           # make a sub ion image folder
os.mkdir(OutputFolder + '\\exploratory results') # make an exploratory analysis sub folder
    
print('Finish raw data processing')

#===========================================
# L0.0.0 save single images
#===========================================
for i in range(2, img.shape[0]):        
    ### plot save
    plt.figure(figsize=[20,10])
    plt.imshow(img[i], aspect = aspect, cmap=colormap)
    
    # title and save path
    if MassList_FileDir == 0: title = 'No.' + str(i-2)
    else: title = 'No.' + str(i-2) + '  ' + str(round(MassList[i-2][0],4))
    SaveDir = OutputFolder + '\\ion images\\' + title + '.png'
    #plt.title(title, fontsize = 25)
    
    # theme
    if colorbar != 0: plt.colorbar()
    if ticks == 0: plt.xticks([]), plt.yticks([])
    
    #plt.show()
    plt.savefig(SaveDir)
    plt.close()
    
    ### progressbar
    if i % 20 ==0:
        print('Finish generating {}/{} ion images'.format(i, img.shape[0]-2))
    if i % (img.shape[0]-1) ==0:
        print('Finish L0.0.0 ion image generation, next step: L0.0.1 show mosaic ion images')

#===========================================
# plot mosaic
#===========================================
# parameters:
w_fig = 20 # default setting
ncols = ncols_L0
nrows = math.ceil((img.shape[0]-2)/ncols)
h_fig = w_fig * nrows * (AspectRatio + 0.2) / ncols # 0.2 is the space for title parameters

#star = time.time()

fig = plt.figure(figsize=(w_fig,h_fig))
fig.subplots_adjust(hspace= -0.2, wspace=0)
for i in range(1, img.shape[0]-1):
    ax = fig.add_subplot(nrows, ncols, i)
    ax.imshow(img[i+1], cmap=colormap, aspect = aspect)
    ax.set_xticks([])
    ax.set_yticks([])
    
    # title
    if MassList_FileDir == 0: title = str(i-1)
    else: title = str(i-1) + '_' + str(round(MassList[i-2][0],4))
    ax.set_title(title, pad=3, fontsize = 7)
    
SaveDir = OutputFolder + '\\ion images\\ion_image_mosaic.png'
plt.savefig(SaveDir, dpi=dpi)
plt.close()

print('Finish L0.0.1 show mosaic ion images, next step: L0.1 PCA')

#===========================================
# L0.1 PCA
#===========================================
pca_all=PCA(random_state=RandomState) 
pcs_all=pca_all.fit_transform(pixel_feature_std)  

# calculate evr
pca_range = np.arange(1, pca_all.n_components_, 1)
evr = pca_all.explained_variance_ratio_
evr_cumsum = np.cumsum(evr)

cut_evr = find_nearest(evr_cumsum, threshold)
nPCs = np.where(evr_cumsum == cut_evr)[0][0] + 1
if nPCs >= 50: # 2 conditions to choose nPCs.
    nPCs = 50

df_pixel_rep = pd.DataFrame(data = pcs_all[:,0:nPCs], columns= ['PC_%d' % (i+1) for i in range(nPCs)])
df_pixel_rep.insert(0, 'spectrum_index', df_pixel[1])
df_pixel_rep.insert(0, 'line_index', df_pixel[0])

print('Finish L0.1 PCA calculation, plotting results.')

#===========================================
# L0.1 PCA scree plot
#===========================================
fig, ax = plt.subplots(figsize=(20,8))
ax.bar(pca_range[0:MaxPCs], evr[0:MaxPCs]*100, color="steelblue")
ax.yaxis.set_major_formatter(mtl.ticker.PercentFormatter())
ax.set_xlabel('Principal component number', fontsize = 30)
ax.set_ylabel('Percentage of \nvariance explained', fontsize = 30)
ax.set_ylim([-0.5,100])
ax.set_xlim([-0.5,50.5])

ax2 = ax.twinx()
ax2.plot(pca_range[0:MaxPCs], evr_cumsum[0:MaxPCs]*100, color="tomato", marker="D", ms=7)
ax2.scatter(nPCs, cut_evr*100, marker='*', s = 500, facecolor = 'blue')
ax2.yaxis.set_major_formatter(mtl.ticker.PercentFormatter())
ax2.set_ylabel('Cumulative percentage', fontsize = 30)
ax2.set_ylim([-0.5,100])

# axis and tick theme
ax.tick_params(axis="y", colors="steelblue")
ax2.tick_params(axis="y", colors="tomato")
ax.tick_params(size=10, color='black', labelsize=25)
ax2.tick_params(size=10, color='black', labelsize=25)

ax.tick_params(width=3)
ax2.tick_params(width=3)

ax=plt.gca() # Get the current Axes instance

for axis in ['top','bottom','left','right']:
    ax.spines[axis].set_linewidth(3)

SaveDir = OutputFolder + '\\exploratory results\\PCA_scree_plot.png'
plt.savefig(SaveDir) 
plt.close()

#===========================================
# L0.1 PCA score plot
#===========================================
plt.figure(figsize=(12,10))
plt.scatter(df_pixel_rep.PC_1,df_pixel_rep.PC_2,facecolors='None',edgecolors=cm.tab20(0),alpha=0.1)
plt.xlabel('PC1 ({}%)'.format(round(evr[0]*100,2)), fontsize=30)
plt.ylabel('PC2 ({}%)'.format(round(evr[1]*100,2)), fontsize=30)
plt.tick_params(size=10, color='black')

# tick and axis theme
plt.xticks(fontsize=20)
plt.yticks(fontsize=20)

ax=plt.gca() # Get the current Axes instance

for axis in ['top','bottom','left','right']:
    ax.spines[axis].set_linewidth(2)
ax.tick_params(width=2)

SaveDir = OutputFolder + '\\exploratory results\\PCA_score_plot.png'  
plt.savefig(SaveDir) 
plt.close()

print('Finish L0.1 PCA, next step: L0.2 UMAP')

#===========================================
# L0.2 UMAP
#===========================================
UMAP_components_2=umap.UMAP(n_components=2, n_neighbors=n_neighbors, min_dist=min_dist,
                          random_state=RandomState, metric='cosine', verbose=True, spread=1.0,
                          n_epochs=None, init='spectral', a=None, b=None).fit_transform(pixel_feature_std)

#===========================================
# L0.2 UMAP plot
#===========================================
plt.figure(figsize=(12,10))
plt.scatter(UMAP_components_2[:,0],UMAP_components_2[:,1],facecolors='None',edgecolors=cm.tab20(0),alpha=0.1)
plt.xlabel('UMAP1',fontsize = 30) #only difference part from last one
plt.ylabel('UMAP2',fontsize = 30)

# theme
plt.xticks(fontsize=20)
plt.yticks(fontsize=20)
plt.tick_params(size=10, color='black')

ax=plt.gca() # Get the current Axes instance

for axis in ['top','bottom','left','right']:
    ax.spines[axis].set_linewidth(3)
ax.tick_params(width=3)

SaveDir = OutputFolder + '\\exploratory results\\UMAP_plot.png'  
plt.savefig(SaveDir)
plt.close()

print('Finish L0.2 UMAP, saving .csv file')

#===========================================
# save data
#===========================================
df_pixel_rep['UMAP_1'] = UMAP_components_2[:,0]
df_pixel_rep['UMAP_2'] = UMAP_components_2[:,1]
SaveDir = OutputFolder + '\\exploratory results\\pixel_rep.csv'
df_pixel_rep.to_csv(SaveDir, index=False, sep=',')

print('L0 is done, please check output results at: \n{}'.format(OutputFolder+'\\exploratory results'))