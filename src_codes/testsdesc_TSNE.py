# -*- coding: utf-8 -*-
"""
Created on Mon Sep 24 15:37:11 2018

@author: asthasyal
"""

import csv            
import pandas as pd
from tabulate import tabulate
from io import StringIO
import sys
import numpy as np
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler
import seaborn as sns
from sklearn import manifold, datasets
import datetime
from time import time
from sklearn.decomposition import PCA
from sklearn.cluster import DBSCAN
from sklearn import metrics
from sklearn.datasets.samples_generator import make_blobs
from sklearn.preprocessing import StandardScaler


def file_read(dataPath,fileName):
    with open (dataPath+fileName+'.csv', mode='r') as f:
      newDF = pd.read_csv(f,sep=',',header='infer')
      newDF = newDF.dropna(axis='rows')
    f.close()
    return newDF

def main():
    np.set_printoptions(suppress=True,formatter={'float_kind':'{0.4f}'.format})
    #dataPath = sys.argv[1]   
    #outputPath = sys.argv[2]
    dataPath = r'C:\\Users\\asthasyal\\Documents\\TstatProject\\data\\'
    outpath=r'C:\\Users\\asthasyal\\Documents\\TstatProject\\result\\summary_tests.txt'
    #fileNames = ['tstat.dtn01.nersc.gov', 'tstat.dtn02.nersc.gov', 'tstat.dtn03.nersc.gov',
                # 'tstat.dtn04.nersc.gov', 'tstat.dtn05.nersc.gov', 'tstat.dtn06.nersc.gov', 
                 #'tstat.dtn07.nersc.gov', 'tstat.dtn08.nersc.gov', 'dtn-tstat-2018.01','dtn-tstat-2018.07',
                # 'tstat.dtn05.nersc.gov.testb', 'tstat.dtn05.nersc.gov.tests']
    fileName = 'tstat.dtn05.nersc.gov.tests'
newDF = file_read(dataPath,fileName)
list(newDF)


newDF['first:29']=pd.to_numeric(newDF['first:29']/1000).round(0).astype(int) 
newDF['first:29']=pd.to_datetime(newDF['first:29'],unit='s')
 
newDF['last:30']=pd.to_numeric(newDF['last:30']/1000).round(0).astype(int)
newDF['last:30']=pd.to_datetime(newDF['last:30'],unit='s')
 
newDF=newDF.set_index(pd.DatetimeIndex(newDF['first:29'])).sort_index()
dateFrom = datetime.datetime(2018, 1, 1, 5, 0, 0) #8 to 7 30
dateTo = datetime.datetime(2018, 1, 1, 23, 0, 0)

 
dateFrom = newDF['first:29'].iloc[0] # first date and time in the column
dateTo = newDF['first:29'].iloc[-1]# last date and time
 
selDF=newDF.set_index(pd.DatetimeIndex(newDF['first:29'])).sort_index().loc[dateFrom:dateTo]
selDF['throughput']=(selDF['s_bytes_all:23']*8) / (selDF['durat:31'] / 1000)
selDF['throughput']=selDF['throughput'].round(2)
 
selDF['throughput'] = selDF['throughput']+1
selDF['throughput'] = selDF['throughput'].apply(np.log10)

# computing short lived and long lived flows
selDF['flows_permin']=(selDF['throughput']/8) *(60*1000)
selDF['flows_permin']=selDF['flows_permin'].round(2)
threshold=selDF['flows_permin'].mean()



features=['c_rst_cnt:4','c_ack_cnt:5', 'c_ack_cnt_p:6', 'c_pkts_retx:10', 'c_bytes_retx:11', 'c_pkts_ooo:12', 'c_syn_cnt:13','c_fin_cnt:14', \
          's_rst_cnt:18','s_ack_cnt:19', 's_ack_cnt_p:20', \
          's_pkts_retx:24','s_bytes_retx:25',  's_pkts_ooo:26', 's_syn_cnt:27', 's_fin_cnt:28', \
          'c_first:32', 's_first:33', 'c_last:34','s_last:35', 'c_first_ack:36', 's_first_ack:37', 'c_isint:38','s_isint:39', 'c_iscrypto:40','s_iscrypto:41','con_t:42',  'p2p_t:43','http_t:44','c_rtt_avg:45','c_rtt_min:46','c_rtt_max:47', \
          'c_rtt_std:48', 'c_rtt_cnt:49', 'c_ttl_min:50', 'c_ttl_max:51', 's_rtt_avg:52', 's_rtt_min:53', \
          's_rtt_max:54', 's_rtt_std:55', 's_rtt_cnt:56', 's_ttl_min:57', 's_ttl_max:58','c_f1323_opt:59','c_tm_opt:60', \
           'c_win_scl:61','c_sack_opt:62','c_sack_cnt:63', 'c_mss:64', 'c_mss_max:65', 'c_mss_min:66', 'c_win_max:67', 'c_win_min:68', \
          'c_win_0:69','c_cwin_max:70', 'c_cwin_min:71', 'c_cwin_ini:72', 'c_pkts_rto:73','c_pkts_fs:74', 'c_pkts_reor:75', \
          'c_pkts_dup:76','c_pkts_unk:77', 'c_pkts_fc:78', 'c_pkts_unrto:79', 'c_pkts_unfs:80', 'c_syn_retx:81', 's_f1323_opt:82',\
          's_tm_opt:83','s_win_scl:84', 's_sack_opt:85', 's_sack_cnt:86', 's_mss:87', 's_mss_max:88', \
          's_mss_min:89', 's_win_max:90', 's_win_min:91', 's_win_0:92','s_cwin_max:93', 's_cwin_min:94','s_cwin_ini:95',\
          's_pkts_rto:96', 's_pkts_fs:97', 's_pkts_reor:98', 's_pkts_dup:99', 's_pkts_unk:100', 's_pkts_fc:101',\
          's_pkts_unrto:102', 's_pkts_unfs:103', 's_syn_retx:104' ]


datadf = selDF[features]
x=selDF.loc[:,features].values
scaler = MinMaxScaler()
scaler.fit(x) 
scaleDF=scaler.transform(x)

X = scaleDF
y_pred = pd.DataFrame(KMeans(n_clusters=2, random_state=10).fit_predict(X))
y_pred.columns=['cluster']
n_neighbors = 10
n_components = 2
   
y_pred = y_pred.reset_index(drop=True)  
datadf = datadf.reset_index(drop=True) 
datadf['label']=0
datadf['cluster']= y_pred['cluster'].values
datadf['label']=datadf.reset_index(drop=True)
color = datadf['label']
color.loc[color>=1]='Yes'
color.loc[color==0]='No'
color=pd.DataFrame(color)
color = color.reset_index(drop=True)

y=datadf.loc[:,['cluster']].values

#ISOMAP
t0 = time()
Y = manifold.Isomap(n_neighbors, n_components).fit_transform(X)
t1 = time()
print("Isomap: %.2g sec" % (t1 - t0))
Y=pd.DataFrame(Y)
Y.columns = ['x', 'y']
#Y=pd.concat([Y,color], axis=1)
Y=pd.concat([Y,y_pred], axis=1)
myp=sns.lmplot(data=Y, x='x', y='y',hue='cluster',palette="Set1",markers=["o", "x"],
                 fit_reg=False, legend=True, legend_out=True)
new_title = 'Cluster'
myp._legend.set_title(new_title)
plt.title("Isomap (%.2g sec)" % (t1 - t0))
plt.axis('tight')
#MDS
t0 = time()
mds = manifold.MDS(n_components, max_iter=100, n_init=1)
Y = mds.fit_transform(X)
t1 = time()
print("MDS: %.2g sec" % (t1 - t0))
Y=pd.DataFrame(Y)
Y.columns = ['x', 'y']
#Y=pd.concat([Y,color], axis=1)
Y=pd.concat([Y,y_pred], axis=1)
myp=sns.lmplot(data=Y, x='x', y='y',hue='cluster',palette="Set1",markers=["o", "x"],
                 fit_reg=False, legend=True, legend_out=True)
new_title = 'Cluster'
myp._legend.set_title(new_title)
plt.title("MDS (%.2g sec)" % (t1 - t0))
plt.axis('tight')

#t-sne
t0 = time()
tsne = manifold.TSNE(n_components, init='pca', random_state=0)
Y = tsne.fit_transform(X)
t1 = time()
print("t-SNE: %.2g sec" % (t1 - t0))
Y=pd.DataFrame(Y)
Y.columns = ['x', 'y']
#Y=pd.concat([Y,color], axis=1)
Y=pd.concat([Y,y_pred], axis=1)
myp=sns.lmplot(data=Y, x='x', y='y',hue='cluster',palette="Set1",markers=["o", "x"],
                 fit_reg=False, legend=True, legend_out=True)
# title
new_title = 'Cluster'
myp._legend.set_title(new_title)
plt.title("t-SNE (%.2g sec)" % (t1 - t0))
plt.axis('tight')
fig = myp.get_figure()


perplexities = (2, 5, 30, 50, 70, 90, 100)
for perp in perplexities:
    t0 = time()
    tsne = manifold.TSNE(n_components=n_components, init='pca', random_state=0, perplexity=perp)
    Y = tsne.fit_transform(X)
    t1 = time()
    print("t-SNE: %.2g sec" % (t1 - t0))
    #ax = fig.add_subplot(154)
    #tsnep=plt.scatter(Y[:, 0], Y[:, 1], c=color, cmap=myCmap,alpha=0.5, edgecolors='none')
    Y=pd.DataFrame(Y)
    Y.columns = ['x', 'y']
    #Y=pd.concat([Y,color], axis=1)
    Y=pd.concat([Y,y_pred], axis=1)
    myp=sns.lmplot(data=Y, x='x', y='y',hue='cluster',palette="Set1",markers=["o", "x"],
                     fit_reg=False, legend=True, legend_out=True)
    # title
    new_title = 'Cluster'
    myp._legend.set_title(new_title)
    plt.title("t-SNE (%.2g sec)" % (t1 - t0))
    plt.axis('tight')
 

#PCA

pca=PCA(n_components=2)
principalComponents= pca.fit_transform(X)
principalDF=pd.DataFrame(data=principalComponents,columns=['principal_components_1','principal_components_2'])
finaldf=pd.concat([principalDF,datadf[['cluster']]],axis=1)

fig = plt.figure(figsize = (8,8))
ax = fig.add_subplot(1,1,1) 
ax.set_xlabel('Principal Component 1', fontsize = 15)
ax.set_ylabel('Principal Component 2', fontsize = 15)
ax.set_title('2 component PCA', fontsize = 20)
clusters = [0,1]
colors = ['r', 'g']
for cluster, color in zip(clusters,colors):
    indicesToKeep = finaldf['cluster'] == cluster
    ax.scatter(finaldf.loc[indicesToKeep, 'principal_components_1']
               , finaldf.loc[indicesToKeep, 'principal_components_2']
               , c = color
               , s = 50)
ax.legend(clusters)
ax.grid()

# dbSCAN

db = DBSCAN(eps=1, min_samples=10).fit(X)
core_samples_mask = np.zeros_like(db.labels_, dtype=bool)
core_samples_mask[db.core_sample_indices_] = True
labels = db.labels_
n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
n_noise_ = list(labels).count(-1)

print('Estimated number of clusters: %d' % n_clusters_)
print('Estimated number of noise points: %d' % n_noise_)
print("Silhouette Coefficient: %0.3f"% metrics.silhouette_score(X, labels))

unique_labels = set(labels)
colors = [plt.cm.Spectral(each)
          for each in np.linspace(0, 1, len(unique_labels))]
for k, col in zip(unique_labels, colors):
    if k == -1:
        # Black used for noise.
        col = [0, 0, 0, 1]

    class_member_mask = (labels == k)

    xy = X[class_member_mask & core_samples_mask]
    plt.plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=tuple(col),
             markeredgecolor='k', markersize=14)

    xy = X[class_member_mask & ~core_samples_mask]
    plt.plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=tuple(col),
             markeredgecolor='k', markersize=6)

plt.title('Estimated number of clusters: %d' % n_clusters_)
plt.show()

summaryT = selDF.describe()
summaryT = summaryT.drop(summaryT.columns[0],axis=1)
with open(outpath, 'w') as f:
        f.write('Summary for: '+ fileName+'\n')
        j=0
        for i in range(9,111,9):
            whatP = summaryT.iloc[:,j:i]
            f.write(tabulate( whatP, headers= whatP.columns,tablefmt='psql',floatfmt=('.4f')))
            f.write('\n\n')
            j = i
    f.close()
