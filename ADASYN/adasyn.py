import sklearn.datasets
import pandas as pd
import numpy as np
import warnings
from sklearn.neighbors import NearestNeighbors
warnings.filterwarnings("ignore")

# two-class ADASYN
def ADASYN(x, y, d_th=0.7, beta=0.5, lamda = 0.2, neighbors=5): 
    x_org = x.values
    y_org = y.values
    x = x.values
    y = y.values
    unique, dist = np.unique(y, return_counts=True)
    m_s = min(dist)
    m_l = max(dist)
    min_class = unique[[i for i in range(len(dist)) if dist[i] == m_s][0]]
    max_class = unique[[i for i in range(len(dist)) if dist[i] == m_l][0]]

    degree_imbalance = m_s / m_l
    
    if degree_imbalance <= d_th:
        necessary_data_no = (m_l - m_s) * beta
        min_class_index = list(np.where(y == min_class))[0]
        knn = NearestNeighbors(n_neighbors=neighbors)
        knn.fit(x)
        majority_ratio= []
        additional_data_no = []
        
        for i in min_class_index:
            count = 0
            sample = x[i].reshape(1, -1) #形の変形が必要
            nearest_candidates = list(knn.kneighbors(sample, return_distance=False)[0])# 各サンプルの近傍点を計算
        
            for i in y[nearest_candidates]:
                if i == max_class:
                    count +=1
            majority_ratio.append(count / neighbors)
        
        # normalize
        total = sum(majority_ratio)
        for i in range(len(majority_ratio)):
            majority_ratio[i] /= total
            
        # number of necessary additional samples
        for i in range(len(majority_ratio)):
            additional_data_no.append(int(majority_ratio[i] * necessary_data_no))
        
        for i in range(len(min_class_index)):
            sample = x[min_class_index[i]].reshape(1, -1) #形の変形が必要
            nearest_candidates = list(knn.kneighbors(sample, return_distance=False)[0])# 各サンプルの近傍点を計算
            
            for j in range(additional_data_no[i]): #min_class_indexの各要素に対して、additional_data_no回繰り返す
                y_label = y[nearest_candidates] #K近傍点のターゲット値

                local_minority_index = [i for i in range(len(y_label)) if y_label[i] == min_class]
                select = x[nearest_candidates[np.random.choice(local_minority_index)]].reshape(1,-1)
                
                x_new = np.array(sample) + (np.array(select) - np.array(sample)) * lamda
                y_new = min_class
    
        #concatenation
                x_org = np.vstack([x_org, x_new])
                y_org = np.hstack([y_org, y_new])
        return x_org, y_org
        
    else:
        print("No augmentation is necessary.")
        return x, y



