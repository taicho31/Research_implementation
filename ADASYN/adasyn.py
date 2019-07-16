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
        nec_data_no = (m_l - m_s) * beta
        min_class_index = list(np.where(y == min_class))[0]
        knn = NearestNeighbors(n_neighbors=neighbors)
        knn.fit(x)
        majority_ratio= []
        add_data_no = []

        for i in min_class_index:
            count = 0
            sample = x[i].reshape(1, -1)
            nearest_cand = knn.kneighbors(sample)[1][0] # neighbors for each point (output: (dist, indices))
            #list(knn.kneighbors(sample, return_distance=False))[0]

            for j in y[nearest_cand]:
                if j == max_class:
                    count +=1
            majority_ratio.append(count / neighbors)

        # normalize
        total = sum(majority_ratio)
        for i in range(len(majority_ratio)):
            majority_ratio[i] /= total

        # number of necessary additional samples
        for i in range(len(majority_ratio)):
            add_data_no.append(int(majority_ratio[i] * nec_data_no))

        for i in range(len(min_class_index)):
            sample = x[min_class_index[i]].reshape(1, -1)
            nearest_cand = knn.kneighbors(sample)[1][0]
            #list(knn.kneighbors(sample, return_distance=False))[0]

            for j in range(add_data_no[i]): # repeat [add_data_no] times for each element in [min_class_index]
                y_label = y[nearest_cand] # target value of k nearest neighbors

                minor_index = [i for i in range(len(y_label)) if y_label[i] == min_class]
                select = x[nearest_cand[np.random.choice(minor_index)]].reshape(1,-1)

                x_new = np.array(sample) + (np.array(select) - np.array(sample)) * lamda
                y_new = min_class

                #concatenation
                x_org = np.vstack([x_org, x_new])
                y_org = np.hstack([y_org, y_new])
        return x_org, y_org

    else:
        print("No augmentation is necessary.")
        return x, y
