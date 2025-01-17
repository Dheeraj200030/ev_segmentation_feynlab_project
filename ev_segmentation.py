# -*- coding: utf-8 -*-
"""ev_segmentation.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1DZw3iAFQ4xlvTtDkEJhKnaH4zjgepSkv

# IMPORTING LIBRARIES
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
scalar=StandardScaler()
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans,AgglomerativeClustering,DBSCAN,SpectralClustering
from sklearn.mixture import GaussianMixture
from sklearn.metrics import silhouette_samples, silhouette_score
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn import tree
from sklearn import metrics

import warnings
warnings.filterwarnings("ignore")

"""LOADING  DATASET"""

df = pd.read_csv("/content/indian-ev-data.csv")

df.head(10)

"""EDA"""

df.shape

df.info()

df.describe()

df.isnull().sum()

# filling mean value in place of missing values in the dataset
df["Power (HP or kW)"] = df["Power (HP or kW)"].fillna(df["Power (HP or kW)"].mean())
df["Top Speed (km/h)"] = df["Top Speed (km/h)"].fillna(df["Top Speed (km/h)"].mean())
df["Year of Manufacture"] = df["Year of Manufacture"].fillna(df["Year of Manufacture"].mean())
df["Price"] = df["Price"].fillna(df["Price"].mean())
df["Charging Time"] = df["Charging Time"].fillna(df["Charging Time"].mean())

df.isnull().sum()

# checking for duplicate rows in the dataset
df.duplicated().sum()

df.columns

import pandas as pd
from sklearn.preprocessing import LabelEncoder, OneHotEncoder

def convert_to_numerical(df):
    # Create a copy to avoid altering the original DataFrame
    df_numerical = df.copy()

    # Convert categorical columns to numerical using label encoding or one-hot encoding
    for col in df_numerical.columns:
        if df_numerical[col].dtype == 'object':  # Check if column is categorical (object type)
            # Apply Label Encoding if the column has two unique values
            if df_numerical[col].nunique() == 2:
                le = LabelEncoder()
                df_numerical[col] = le.fit_transform(df_numerical[col])
            else:
                # Apply One-Hot Encoding for columns with more than two categories
                df_numerical = pd.get_dummies(df_numerical, columns=[col], drop_first=True)

    # Handle missing values (optional, can be customized as needed)
    df_numerical.fillna(df_numerical.mean(), inplace=True)

    return df_numerical

plt.figure(figsize=(30,45))
for i, col in enumerate(df.columns):
    if df[col].dtype != 'object':
        ax = plt.subplot(9, 2, i+1)
        sns.kdeplot(df[col], ax=ax)
        plt.xlabel(col)

plt.show()

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

# Assuming df is your DataFrame
plt.figure(figsize=(5,15))

for i in range(0, 10):
    # Check if the column is numeric before plotting
    if pd.api.types.is_numeric_dtype(df[df.columns[i]]):
        plt.subplot(10, 1, i+1)
        sns.distplot(df[df.columns[i]], kde_kws={'color':'b','bw': 0.1,'lw':3,'label':'KDE'},
                     hist_kws={'color':'g'})
        plt.title(df.columns[i])
    else:
        print(f"Skipping non-numeric column: {df.columns[i]}")

plt.tight_layout()
plt.show()

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

# Select only numeric columns
df_numeric = df.select_dtypes(include=['number'])

# Plot the heatmap
plt.figure(figsize=(12,12))
sns.heatmap(df_numeric.corr(), annot=True, cmap='coolwarm')

plt.show()

"""**scaling the dataframe**"""

from sklearn.preprocessing import StandardScaler
import pandas as pd

# Assuming df is your DataFrame
# Select only numeric columns for scaling
df_numeric = df.select_dtypes(include=['number'])

# Initialize the scaler
scaler = StandardScaler()

# Fit and transform only the numeric columns
scaled_df_numeric = scaler.fit_transform(df_numeric)

# Optionally, convert the scaled array back to a DataFrame with the original column names
scaled_df_numeric = pd.DataFrame(scaled_df_numeric, columns=df_numeric.columns)

# If you want to retain non-numeric columns, you can concatenate them back:
df_non_numeric = df.select_dtypes(exclude=['number'])
scaled_df = pd.concat([scaled_df_numeric, df_non_numeric.reset_index(drop=True)], axis=1)

# Now `scaled_df` contains scaled numeric columns and untouched non-numeric columns

from sklearn.decomposition import PCA
import pandas as pd

# Ensure `scaled_df` only contains numeric columns
scaled_df_numeric = scaled_df.select_dtypes(include=['number'])

# Initialize PCA with the desired number of components
pca = PCA(n_components=2)

# Fit and transform the numeric data using PCA
principal_components = pca.fit_transform(scaled_df_numeric)

# Create a DataFrame for the principal components
pca_df = pd.DataFrame(data=principal_components, columns=["PCA1", "PCA2"])

# Display the result
pca_df.head()

"""# Hyperparameter tuning
## Finding 'k' value by Elbow Method
"""

# Select only numeric columns
numeric_df = scaled_df.select_dtypes(include=[float, int])

inertia = []
range_val = range(1, 15)

for i in range_val:
    kmean = KMeans(n_clusters=i)
    kmean.fit_predict(pd.DataFrame(numeric_df))  # Fit on numeric columns only
    inertia.append(kmean.inertia_)

plt.plot(range_val, inertia, 'bx-')
plt.xlabel('Values of K')
plt.ylabel('Inertia')
plt.title('The Elbow Method using Inertia')
plt.show()

"""# Model Building using KMeans"""

# Filter the DataFrame to include only numeric columns
numeric_df = scaled_df.select_dtypes(include=[float, int])

# Perform KMeans clustering
kmeans_model = KMeans(4)
kmeans_model.fit_predict(numeric_df)  # Fit on numeric columns only

# Add the cluster labels to the PCA DataFrame
pca_df_kmeans = pd.concat([pca_df, pd.DataFrame({'cluster': kmeans_model.labels_})], axis=1)

# View the result
pca_df_kmeans.head()

"""# Visualizing the clustered dataframe"""

plt.figure(figsize=(5,5))
ax=sns.scatterplot(x="PCA1",y="PCA2",hue="cluster",data=pca_df_kmeans,palette=['red','green','blue','black'])
plt.title("Clustering using K-Means Algorithm")
plt.show()

# Ensure the scaler was fitted properly
scalar = StandardScaler()
scaled_data = scalar.fit_transform(numeric_df)

# Get the cluster centers
cluster_centers = pd.DataFrame(data=kmeans_model.cluster_centers_, columns=numeric_df.columns)

# Try inverse transforming the data to the original scale
try:
    cluster_centers = scalar.inverse_transform(cluster_centers)
except AttributeError:
    print("Scaler has no attribute 'scale_'. Ensure it was fitted correctly and standard scaling was used.")

# Convert cluster centers back to a DataFrame
cluster_centers = pd.DataFrame(data=cluster_centers, columns=numeric_df.columns)

# Display the cluster centers
cluster_centers

# Creating a target column "Cluster" for storing the cluster segment
cluster_df = pd.concat([df,pd.DataFrame({'Cluster':kmeans_model.labels_})],axis=1)
cluster_df

cluster_1_df = cluster_df[cluster_df["Cluster"]==0]
cluster_1_df

cluster_2_df = cluster_df[cluster_df["Cluster"]==1]
cluster_2_df

cluster_3_df = cluster_df[cluster_df["Cluster"]==2]
cluster_3_df

cluster_4_df = cluster_df[cluster_df["Cluster"] == 3]
cluster_4_df

#Visualization
sns.countplot(x='Cluster', data=cluster_df)

for c in cluster_df.drop(['Cluster'],axis=1):
    grid= sns.FacetGrid(cluster_df, col='Cluster')
    grid= grid.map(plt.hist, c)
plt.show()

"""# Saving the kmeans clustering model and the data with cluster label"""

#Saving Scikitlearn models
import joblib
joblib.dump(kmeans_model, "kmeans_model.pkl")

cluster_df.to_csv("Clustered_Customer_Data.csv")

"""# Training and Testing the model accuracy using decision tree"""

#Split Dataset
X = cluster_df.drop(['Cluster'],axis=1)
y= cluster_df[['Cluster']]
X_train, X_test, y_train, y_test =train_test_split(X, y, test_size=0.3)

X_train

X_test

#decision tree

# Adjust the split to ensure all labels are in both train and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)