#===========================================
# import modules, defs and variables
#===========================================
exec(open("./external.py").read())
exec(open("./defs.py").read())
exec(open("./config.py").read())

print('Finish modules, defs and variables import')

#===========================================
# L3.0.0 import data 
#===========================================
# L1 output GMM
df_pixel_label_clustering = pd.read_csv(L1outputDir)
# L2 output ensemble segments
df_pixel_label_ensemble = pd.read_csv(EnOutputDir)

print('Finish pixel raw data import, next step: L3.0.1 raw data process')

#===========================================
# L3.0.1 raw data process
#===========================================
# 1. populate results in ensamble results folder
OutputFolder = locate_OutputFolder4(EnOutputDir)

# 2. parse dimension
NumLine = np.max(df_pixel_label_clustering.iloc[:,0])+1
NumSpePerLine = np.max(df_pixel_label_clustering.iloc[:,1])+1

# 4. parameter for plotting
aspect = AspectRatio*NumSpePerLine/NumLine

# 5. get clustering labels
pixel_label = df_pixel_label_clustering.values.astype(np.int64)[:,2:]
n_clusters = pixel_label.shape[1]
pixel_seg_maps = pixel_label.T.reshape(n_clusters, NumLine, NumSpePerLine)

print('Finish raw data processing, next step: L3.0.2 construct co-occurrence matrix')

#===========================================
# L3.0.2 construct co-occurrence matrix
#===========================================
dim = pixel_label.shape[0]
co_matrix = np.zeros((dim, dim), dtype=np.uint8)

for k in range(pixel_label.shape[1]):
    label = pixel_label[:,k]
    # count time
    StaTime = time.time()

    clusterid_list = np.unique(label)
    for clusterid in clusterid_list:
        itemidx = np.where(label == clusterid)
        for i, x in enumerate(itemidx[0][0: -1]):
            ys = itemidx[0][i+1:]    # improve performance a lot by only vecterizing this 
            co_matrix[x, ys] += 1
            co_matrix[ys, x] += 1

    SpenTime = time.time() - StaTime
    print('running time for {}th label: {}'.format(k, round(SpenTime, 2)))

print('converting to sparse matrix...')
co_matrix = sparse.coo_matrix(co_matrix)
print('Finish co-occurrence matrix construction, next step: L3.0.3 Truncated SVD dimensionality reduction')

#===========================================
# L3.0.3 Truncated SVD dimensionality reduction
# could run for several mins
#===========================================
StaTime = time.time()

svd = TruncatedSVD(n_components = 51)   # n_iter = 10 may help, but computation gets more expensive
pcs_all = svd.fit_transform(co_matrix)

SpenTime = time.time() - StaTime
print('running time for TruncatedSVD: {}'.format(round(SpenTime, 2)))

# calculate evr
pca_range = np.arange(1, 51, 1)
evr = svd.explained_variance_ratio_
evr_cumsum = np.cumsum(evr)

cut_evr = find_nearest(evr_cumsum, SVD_threshold)
nPCs = np.where(evr_cumsum == cut_evr)[0][0] + 1
if nPCs >= 50: # 2 conditions to choose nPCs.
    nPCs = 50

df_pixel_rep = pd.DataFrame(data = pcs_all[:,0:nPCs], columns= ['PC_%d' % (i+1) for i in range(nPCs)])

print('all done')


# scree plot
### save ion images main code
fig, ax = plt.subplots(figsize=(20,8))
ax.bar(pca_range[0:MaxPCs], evr[0:MaxPCs]*100, color="steelblue")
ax.set_xlabel('Principal component number', fontsize = 30)
ax.set_ylabel('Percentage of \nvariance explained', fontsize = 30)
ax.set_ylim([-0.5,100])
ax.set_xlim([-0.5,50.5])

ax2 = ax.twinx()
ax2.plot(pca_range[0:MaxPCs], evr_cumsum[0:MaxPCs]*100, color="tomato", marker="D", ms=7)
ax2.scatter(nPCs, cut_evr*100, marker='*', s = 500, facecolor = 'blue')
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

SaveDir = OutputFolder + '\\PCA_scree_plot.png'
plt.savefig(SaveDir) 
plt.close()

print('Finish TruncatedSVD, next step: L3.0.4 GMM batching')

#===========================================
# L3.0.4 GMM batching
# this step still quite expensive... 
#===========================================
StaTime = time.time()

n_batches = 1000
gmm = GMM(n_components=n_batches)    # max_iter = 1000 may help, but computation gets more expensive
labels = gmm.fit_predict(pcs_all[:, :nPCs])

SpenTime = time.time() - StaTime
print('running time for GMM: {}'.format(round(SpenTime, 2)))
print('next step: L3.0.5 hierarchical clustering')

#===========================================
# L3.0.5 HC
#===========================================
# 1.1 organize the average data for each batch
elements, counts = np.unique(labels, return_counts=True)

features = []

for label in elements:
    idx = np.where(labels == label)
    feature = np.mean(pcs_all[:, :nPCs][idx[0], :], axis=0)
    features.append(feature)
    
features = np.array(features)

# 1.2 HC sort average batch features
Y = sch.linkage(features, method = 'average', metric='cosine')
Z = sch.dendrogram(Y, no_plot = True)
HC_idx = Z['leaves']
HC_idx = np.array(HC_idx)

# 1.3 combine HC indices with GMM batches
co_matrix_idx = []

for i in HC_idx:
    label = elements[i]
    idx = np.where(labels == label)[0].tolist()
    co_matrix_idx.extend(idx)
    
co_matrix_idx = np.array(co_matrix_idx)

print('finishing HC, plotting the sorted co-occurrence matrix')

### sort and visualize comatrix with it, expensive...
co_matrix_sorted = co_matrix[co_matrix_idx, :]
co_matrix_sorted = co_matrix_sorted[:, co_matrix_idx]
co_matrix_sorted_small = cv2.resize(co_matrix_sorted, (5000, 5000))

## plot sorted co-occurrence matrix
fig=plt.figure(figsize=(10,10))

# plot the heatmap
axmatrix = fig.add_axes([0.10,0,0.80,0.80])
im = axmatrix.matshow(co_matrix_sorted_small, aspect='auto', origin='lower', cmap=cm.YlGnBu, interpolation='none')
fig.gca().invert_yaxis()

# Plot colorbar
axcolor = fig.add_axes([0.96,0,0.02,0.80])
cbar=plt.colorbar(im, cax=axcolor)
axcolor.tick_params(labelsize=10) 

SaveDir = OutputFolder + '\\sorted co_occurrence matrix.png'
plt.savefig(SaveDir) 
plt.close()

## plot binary sorted co-occurrence matrix (majority vote)
# majority vote condition
co_matrix_thre = 0.6
co_matrix_sorted_small_thre3 = co_matrix_sorted_small/np.max(co_matrix_sorted_small)
co_matrix_sorted_small_thre3[co_matrix_sorted_small_thre3<co_matrix_thre] = 0
co_matrix_sorted_small_thre3[co_matrix_sorted_small_thre3>=co_matrix_thre] = 1

### plot to visulize it
fig=plt.figure(figsize=(10,10))

# plot the heatmap
axmatrix = fig.add_axes([0.10,0,0.80,0.80])
im = axmatrix.matshow(co_matrix_sorted_small_thre3, aspect='auto', origin='lower', cmap=cm.YlGnBu, interpolation='none')
fig.gca().invert_yaxis()

# Plot colorbar
axcolor = fig.add_axes([0.96,0,0.02,0.80])
cbar=plt.colorbar(im, cax=axcolor)
axcolor.tick_params(labelsize=10) 

SaveDir = OutputFolder + '\\binary sorted co_occurrence matrix.png'
plt.savefig(SaveDir) 
plt.close()

print('finishing plotting, next step: L3.0.6 update the ensemble results')

#===========================================
# L3.0.6 update the ensemble results
#===========================================
final_labels_HC = fcluster(Y, n_cluster, criterion = 'maxclust')-1

# 5.2 orgaize the pixel labels
final_labels = np.empty((NumLine*NumSpePerLine))

# extend labels to entries in batches
for i in range(elements.shape[0]):                            # lets loop along the batch (features' sequence) 
    label = elements[i]                                       # batch label
    final_label_HC = final_labels_HC[i]                      # labels for this batch given by HC
    idx = np.where(labels == label)[0]                     # find out pixel locations in the batch
    final_labels[idx] = final_label_HC                      # attach HC labels to GMM batch
    #break

df_pixel_label_ensemble['auto_assemble'] = final_labels
SaveDir = OutputFolder + '\\pixel_ensemble_label2.csv'
df_pixel_label_ensemble.to_csv(SaveDir, index=False, sep=',')
print('auto finishing is updated, please check output results at: \n{}'.format(OutputFolder_final))