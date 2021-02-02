#===========================================
# import modules, defs and variables
#===========================================
exec(open("./external.py").read())
exec(open("./defs.py").read())
exec(open("./config.py").read())

print('Finish modules, defs and variables import')

#===========================================
# L1.2.0 import data 
#===========================================
# input data
df_pixel = pd.read_csv(InputDir, header = None)
pixel = df_pixel.values
# mass list data
df_MassList = pd.read_csv(MassList_FileDir, header = None)
MassList = df_MassList.values
# L0 output PCA
df_pixel_rep = pd.read_csv(L0outputDir)
# L1.0 output labels
df_pixel_label = pd.read_csv(L1outputDir)

print('Finish pixel raw data import, next step: L1.2.1 raw data process')

#===========================================
# L1.2.1 raw data process
#===========================================
# 1. make folder for results
OutputFolder = locate_OutputFolder2(L0outputDir)
OutputFolder = locate_OutputFolder3(OutputFolder, 'outlier pattern detection')
os.mkdir(OutputFolder)
os.mkdir(OutputFolder + '\\clustered ion images')
os.mkdir(OutputFolder + '\\sorted average ion images')

# 2. trace nPCs
nPCs = retrace_columns(df_pixel_rep.columns.values, 'PC')

# 3. parse dimension
NumLine = np.max(df_pixel_label.iloc[:,0])+1
NumSpePerLine = np.max(df_pixel_label.iloc[:,1])+1

# 4. parameter for plotting
aspect = AspectRatio*NumSpePerLine/NumLine

# 5. digest the input 'glass_slide_labels' to generate indices of pixels on glass slide
boolean = np.zeros(NumLine*NumSpePerLine, dtype=bool)
for i in range(len(glass_slide_labels)):
    entry = glass_slide_labels[i]
    key_list = list(entry.keys())
    for j in key_list: # in each series
        # j -> key df_pixel_label[j] -> df series, segments[i][j] -> value (all selected labels in that df series) 
        current_segmentation = np.isin(df_pixel_label[j], glass_slide_labels[i][j])
        boolean = boolean|current_segmentation # update boolean

# export the mask to confirm the computation
binary_pixels = np.zeros((NumLine*NumSpePerLine))+1
binary_pixels[boolean] = 0

# plot the mask result
binary_map = binary_pixels.reshape((NumLine, NumSpePerLine))
plt.imshow(binary_map, cmap='hot', interpolation='none', aspect=25)

SaveDir = OutputFolder + '\\tissue mask.png'
plt.savefig(SaveDir, dpi=dpi)
plt.close()

# 6. data process for image clustering
#=======================================
pixel_features = pixel[:,2:][binary_pixels==1]

# 7. threshold and normalize pixel intensities for features
pixel_features_modi = np.zeros_like(pixel_features)
scale_up = round(pixel_features.shape[0]*thre_percent)

for i in range(pixel_features.shape[1]):
    # get pixels in the column
    pixels = pixel_features[:, i]
    # get threshold for the column
    thre = pixels[np.argsort(pixels)[scale_up]]
    
    # threshold and populate data
    pixels[pixels>thre] = thre
    # normalize data to 0-1
    pixels = (pixels - np.min(pixels)) / (np.max(pixels) - np.min(pixels))
    
    # populate the features
    pixel_features_modi[:, i] = pixels
    
    #break
# features_modi for HC
features_modi = pixel_features_modi.T


# 8. then repeat the previsou PCA
# feature
df_pixel_feature=df_pixel.drop([0,1],axis=1)
pixel_feature=df_pixel_feature.values.astype(np.float64)
pixel_feature_std = SS().fit_transform(pixel_feature)
# pca
pca = PCA(random_state=RandomState, n_components=nPCs)
pcs = pca.fit_transform(pixel_feature_std)

### PCA loadings
loadings = pca.components_.T
# sum of squared loadings
SSL = np.sum(loadings**2, axis = 1)

print('Finish raw data processing, next step: L1.2.2 ion image clustering')

#===========================================
# L1.2.2 ion image clustering
#===========================================
## 1. HC_clustering
Y = sch.linkage(features_modi, method=HC_method, metric=HC_metric)
Z = sch.dendrogram(Y, no_plot = True)
HC_idx = Z['leaves']
HC_idx = np.array(HC_idx)

# plot it
plt.figure(figsize=(15,10))
Z = sch.dendrogram(Y, color_threshold = thre_dist)
plt.title('hierarchical clustering of ion images \n method: {}, metric: {}, threshold: {}'.format(
            HC_method, HC_metric, thre_dist))

SaveDir = OutputFolder + '\\HC_dendrogram.png'
plt.savefig(SaveDir, dpi=dpi)
plt.close()

## 2. sort features with clustering results
features_modi_sorted = features_modi[HC_idx]

# plot it
fig=plt.figure(figsize=(10,10))
axmatrix = fig.add_axes([0.10,0,0.80,0.80])
im = axmatrix.matshow(features_modi_sorted, aspect='auto', origin='lower', cmap=cm.YlGnBu, interpolation='none')
fig.gca().invert_yaxis()

# colorbar
axcolor = fig.add_axes([0.96,0,0.02,0.80])
cbar=plt.colorbar(im, cax=axcolor)
axcolor.tick_params(labelsize=10) 

SaveDir = OutputFolder + '\\clustered_ion_image_features.png'
plt.savefig(SaveDir, dpi=dpi)
plt.close()

## 3. organize clusters with SSL
# 1. organize ion images according to labels 2. generate average ion images 
HC_labels = fcluster(Y, thre_dist, criterion='distance')

# prepare label data
elements, counts = np.unique(HC_labels, return_counts=True)
# prepare imgs_std data
imgs_std = pixel_feature_std.T.reshape(120, NumLine, NumSpePerLine)
# prepare accumulators
mean_imgs = []
total_SSLs = []

for label in elements:
    idx = np.where(HC_labels == label)[0]
    
    # total SSL
    total_SSL = np.sum(SSL[idx])
    # imgs in the cluster
    current_cluster = imgs_std[idx]
    # average img
    mean_img = np.mean(imgs_std[idx], axis=0)

    # accumulate data
    total_SSLs.append(total_SSL)
    mean_imgs.append(mean_img)

print('Finish ion image clustering, next step: L1.2.3 sort clusters and plot')

#===========================================
# L1.2.3 sort clusters and plot
#===========================================
## plot individual clustered images
plot_idx = 0
for label in elements:
    idx = np.where(HC_labels == label)[0]
    
    # cluster imgs
    current_cluster = imgs_std[idx]
    # show imgs
    for i in range(current_cluster.shape[0]):
        plt.imshow(current_cluster[i], cmap = 'hot', aspect=25, interpolation='none')
        
        # title
        if MassList_FileDir == 0: 
            title = 'Cluster:'+str(label) + '  Og_idx:' + str(idx[i]) + '  SSL:' + str(round(SSL[idx[i]], 4))
        else: 
            title = 'Cluster:'+str(label) + '  Og_idx:' + str(idx[i]) + '  SSL:' + str(round(SSL[idx[i]], 4)) + '  m/z:' + str(round(MassList[idx[i]][0], 4))
        SaveTitle = 'No.' + str(plot_idx)
        
        # theme
        plt.title(title)
        if colorbar != 0: plt.colorbar()
        if ticks == 0: plt.xticks([]), plt.yticks([])
        
        SaveDir = OutputFolder + '\\clustered ion images\\' + SaveTitle + '.png'
        plt.savefig(SaveDir)
        plt.close()

        ### progressbar
        if (plot_idx+1) % 20 ==0:
            print('Finish generating {}/{} ion images'.format(plot_idx+1, imgs_std.shape[0]))
        if (plot_idx+1) % (imgs_std.shape[0]+1) ==0:
            print('Finish clustered ion image generation')
        plot_idx += 1
        
## plot clustered images in a montage
w_fig = 20 # default setting
ncols = ncols_L0
nrows = math.ceil((imgs_std.shape[0]-2)/ncols)
h_fig = w_fig * nrows * (AspectRatio + 0.2) / ncols # 0.2 is the space for title parameters

fig = plt.figure(figsize=(w_fig,h_fig))
fig.subplots_adjust(hspace= -0.2, wspace=0)
plot_loc = 1

for label in elements:
    idx = np.where(HC_labels == label)[0]
    
    # cluster imgs
    current_cluster = imgs_std[idx]
    for i in range(current_cluster.shape[0]):
        ax = fig.add_subplot(nrows, ncols, plot_loc)
        plt.imshow(current_cluster[i], cmap = 'hot', aspect=25, interpolation='none')
        ax.set_xticks([])
        ax.set_yticks([])
        
        # title
        if MassList_FileDir == 0: 
            title = 'Cluster:'+str(label) + '  Og_idx:' + str(idx[i]) + '  SSL:' + str(round(SSL[idx[i]], 4))
        else: 
            title = 'Cluster:'+str(label) + '  Og_idx:' + str(idx[i]) + '  SSL:' + str(round(SSL[idx[i]], 4)) + '  m/z:' + str(round(MassList[idx[i]][0], 4))
        ax.set_title(title, pad=3, fontsize = 3)
        
        plot_loc += 1
        #break
    
SaveDir = OutputFolder + '\\clustered ion images\\clustered_ion_image_montage.png'
plt.savefig(SaveDir, dpi=dpi)
plt.close()

print('Finish generating clustered ion images, next step: generate sorted average ion images')

## plot individual average images
# sort on clusters based on total SSL
rank_idx = np.argsort(total_SSLs)
# plot together
for i in range(elements.shape[0]):
    idx = rank_idx[i]
    # retrieve values
    total_SSL = total_SSLs[idx]
    mean_img = mean_imgs[idx]
    count = counts[idx]
    
    # plot
    plt.imshow(mean_img, cmap = 'hot', aspect=25, interpolation='none')
    
    # title
    title = 'Rank No.'+str(i) + '  # of images:' + str(count) + '  total_SSL:' + str(round(total_SSL, 4))
    SaveTitle = 'No.' + str(i)
        
    # theme
    plt.title(title)
    if colorbar != 0: plt.colorbar()
    if ticks == 0: plt.xticks([]), plt.yticks([])
    
    SaveDir = OutputFolder + '\\sorted average ion images\\' + SaveTitle + '.png'
    plt.savefig(SaveDir)
    plt.close()

## finally plot average images in a montage
ncols = ncols_L0
fig = plt.figure(figsize=(w_fig,h_fig))
fig.subplots_adjust(hspace= -0.2, wspace=0)
plot_loc = 1

for i in range(elements.shape[0]):
    idx = rank_idx[i]
    # retrieve values
    total_SSL = total_SSLs[idx]
    mean_img = mean_imgs[idx]
    count = counts[idx]
    
    # plot
    ax = fig.add_subplot(nrows, ncols, plot_loc)
    plt.imshow(mean_img, cmap = 'hot', aspect=25, interpolation='none')
    ax.set_xticks([])
    ax.set_yticks([])
    
    # title
    title = 'Rank No.'+str(i) + '  # of images:' + str(count) + '  total_SSL:' + str(round(total_SSL, 4))
    ax.set_title(title, pad=3, fontsize = 3)
    plot_loc += 1
    
SaveDir = OutputFolder + '\\sorted average ion images\\sorted_average_ion_image_montage.png'
plt.savefig(SaveDir, dpi=dpi)
plt.close()

print('L1.2.3 is done, please check output results at: \n{}'.format(OutputFolder))