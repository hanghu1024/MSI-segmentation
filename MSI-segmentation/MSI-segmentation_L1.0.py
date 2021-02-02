#===========================================
# import modules, defs and variables
#===========================================
exec(open("./external.py").read())
exec(open("./defs.py").read())
exec(open("./config.py").read())

print('Finish modules, defs and variables import')

#===========================================
# L1.0 import data 
#===========================================
df_pixel_rep = pd.read_csv(L0outputDir)
pixel_rep = df_pixel_rep.values.astype(np.float64)

print('Finish pixel raw data import')  

#===========================================
# L1.0 data processing and manipulate
#===========================================
nPCs = retrace_columns(df_pixel_rep.columns.values, 'PC')
pcs = pixel_rep[:, 2:nPCs + 2]

# make folders for multivariate analysis
OutputFolder = locate_OutputFolder2(L0outputDir)
OutputFolder = locate_OutputFolder3(OutputFolder, 'multivariate clustering')
os.mkdir(OutputFolder)

# initiate a df for labels
df_pixel_label = pd.DataFrame(data=df_pixel_rep[['line_index', 'spectrum_index']].values.astype(int), columns = ['line_index','spectrum_index'])

print('Finish raw data processing')

#===========================================
# L1.0 GMM ensemble clustering
#===========================================
n_component = generate_nComponentList(n_components, span)

for i in range(repeat):                        # may repeat several times
    for j in range(n_component.shape[0]):      # ensemble with different n_component value
        StaTime = time.time()
        
        gmm = GMM(n_components = n_component[j], max_iter = 500) # max_iter does matter, no random seed assigned
        labels = gmm.fit_predict(pcs)
        
        # save data
        index = j+1+i*n_component.shape[0]
        title = 'No.' + str(index) + '_' +str(n_component[j]) + '_' + str(i)
        df_pixel_label[title] = labels
        
        SpenTime = (time.time() - StaTime)
        
        # progressbar
        print('{}/{}, finish classifying {}, running time is: {} s'.format(index, repeat*span, title, round(SpenTime, 2)))

print('Finish L1.0 GMM ensemble clustering, next step: L1.1 data process, plot and export data')

#===========================================
# L1.1 data processing and manipulate
#===========================================
pixel_label = relabel(df_pixel_label)

# parse dimension
NumLine = np.max(df_pixel_label.iloc[:,0])+1
NumSpePerLine = np.max(df_pixel_label.iloc[:,1])+1
# parameter for plotting
aspect = AspectRatio*NumSpePerLine/NumLine

# organize img
img = pixel_label.T.reshape(pixel_label.shape[1], NumLine, NumSpePerLine)

print('Finish L1.1 data process')

#===========================================
# L1.1 ensemble results in mosaic plot, save images 
#===========================================
# mosaic img show
# parameters:
w_fig = 20 # default setting
ncols = ncols_L1
nrows = math.ceil((img.shape[0]-2)/ncols)
h_fig = w_fig * nrows * (AspectRatio + 0.16) / ncols # 0.2 is the space for title parameters
columns = df_pixel_label.columns.values

fig = plt.figure(figsize=(w_fig, h_fig))
fig.subplots_adjust(hspace= 0, wspace=0.01, right=0.95)
for i in range(1, img.shape[0]+1):
    ax = fig.add_subplot(nrows, ncols, i)
    im = ax.imshow(img[i-1], cmap=cm.tab20, aspect = aspect, vmin=0,vmax=19, interpolation='none')
    ax.set_xticks([])
    ax.set_yticks([])
    
    # title
    title = columns[i+1]
    ax.set_title(title, pad=8, fontsize = 15)

# colorbar
cbar_ax = fig.add_axes([0.96,0.1,0.01,0.8])
cbar = fig.colorbar(im, cax=cbar_ax, ticks=[0.5,1.4,2.3,3.3,4.3,5.1,6.2,7,8.1,9,10,10.9,11.8,12.7,13.6,14.7,15.6,16.6,17.5,18.5])
cbar.ax.set_yticklabels([0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19]) #hard code 
cbar.ax.tick_params(labelsize=10)

SaveDir = OutputFolder + '\\ensemble_clustering_plot.png'
plt.savefig(SaveDir, dpi=dpi)
plt.close()

print('Finish L1.1 GMM ensemble clustering result plotting, saving .csv file')

#===========================================
# save data
#===========================================
# organize a dataframe for relabel data
df_pixel_relabel = pd.DataFrame(pixel_label.astype(int), columns = df_pixel_label.columns.values[2:df_pixel_label.shape[1]])
df_pixel_relabel.insert(0, 'spectrum_index', df_pixel_label.iloc[:,1])
df_pixel_relabel.insert(0, 'line_index', df_pixel_label.iloc[:,0])

SaveDir = OutputFolder + '\\pixel_label.csv'
df_pixel_relabel.to_csv(SaveDir, index=False, sep=',')

print('L1 is done, please check output results at: \n{}'.format(OutputFolder))
