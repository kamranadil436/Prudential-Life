import pandas as pd
import numpy as np
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
# Load data file #

class DataLoader:
    """
    This class provides method to load data
    """

    def __init__(self, path):
        self.path = path
        # print('in DataLoader')

    def loader(self):
        # print('Loading data.')
        file = pd.read_csv(self.path)
        # print('Finish loading')
        return file


train = DataLoader(path='train.csv')
train_data = train.loader()
test = DataLoader(path='test.csv')
test_data = test.loader()
data = train_data.append(test_data)


# Preprocess data #

# factorize categorical variables
data['Product_Info_2'] = pd.factorize(data['Product_Info_2'])[0]

# drop id variable
data = data.drop('Id', axis=1)

# drop response variable
data = data.drop('Response', axis=1)

# data.to_csv('complete_data.csv')

# feature scaling and standardisation/ normalisation
def feature_scale(df):
    scale_df = (df - df.mean()) / df.std(ddof=1)
    return scale_df


data = feature_scale(data)


#  dealing missing value

def check_missing(df):
    # Explore missing data
    missing_data = df.isnull().sum()
    # print(missing_data.dtypes)
    # print(type(missing_data))
    total_data = len(df)
    df_missing_data = missing_data.to_frame()
    df_missing_data.columns = ['counts']
    # Identify missing categories
    df_missing_data = df_missing_data[df_missing_data.counts != 0]
    # Calculate missing percentage
    df_missing_data['missing_percent'] = df_missing_data.counts / total_data
    print(df_missing_data)
    print(len(df_missing_data))
    return df_missing_data


# check_missing(data)

# Create list of variable types

cont_variable_list = ['Product_Info_4', 'Ins_Age', 'Ht', 'Wt', 'BMI', 'Employment_Info_1', 'Employment_Info_4',
                      'Employment_Info_6', 'Insurance_History_5', 'Family_Hist_2', 'Family_Hist_3', 'Family_Hist_4',
                      'Family_Hist_5']

dis_variable_list = ['Medical_History_1', 'Medical_History_10', 'Medical_History_15', 'Medical_History_24',
                     'Medical_History_32']

for i in range(48):
    i += 1
    dis_variable_list.append('Medical_Keyword_' + str(i))

cat_variable_list = []
for header in data.columns:
    if header in cont_variable_list and dis_variable_list:
        pass
    else:
        cat_variable_list.append(header)

missing_list = ['Employment_Info_1', 'Employment_Info_4', 'Employment_Info_6', 'Family_Hist_2', 'Family_Hist_3',
                'Family_Hist_4', 'Family_Hist_5', 'Insurance_History_5', 'Medical_History_1', 'Medical_History_10',
                'Medical_History_15', 'Medical_History_24', 'Medical_History_32']


# recommend method : pca, interpolation,svd, boosting

class MissingMethod:
    """
    This class will provide various method to handle missing values
    """

    def __init__(self, data):
        self.df = data

    def drop_response(self):
        self.df = self.df.drop('Response', axis=1, inplace=True)
        return self.df

    def fill_mode(self):
        for var in missing_list:
            if var in dis_variable_list and cat_variable_list:
                self.df[var] = self.df[var].fillna(self.df[var].mode()[0])
        return self.df

    def fill_avg(self):
        for var in missing_list:
            self.df[var] = self.df[var].fillna(self.df[var].mean())
        return self.df

    def drop_col(self):
        self.df = self.df.drop(['Medical_History_10', 'Medical_History_24',
                                'Medical_History_32'])
        return self.df


# preprocess = MissingMethod(data).fill_mode()
# preprocess = MissingMethod(data).fill_avg()
# check_missing(preprocess)
# preprocess = MissingMethod(data)

# use SVD to fill missing data
# pls normalise the data before using this function
# 1. if filling missing data, pls drop response
# 2. if use it to predict response, pls keep response
def fill_svd(df):
    col_mean = np.nanmean(df, axis=0, keepdims=1)
    valid = np.isfinite(df)
    df0 = np.where(valid, df, col_mean)
    halt = True
    maxiter = 100
    ii = 1
    normlist = []
    while halt == True:
        U, s, V = np.linalg.svd(df0, full_matrices=False)
        s1 = [(i * 0 if i <= 30 else i) for i in s]
        df1 = U.dot(np.diag(s1).dot(V))
        df2 = np.where(~valid, df1, df0)
        norm = np.linalg.norm(df2 - df1)
        normlist.append(norm)
        #        print(norm)
        df0 = df2
        if norm < 0.00001 or ii >= maxiter:
            halt = False
            error = np.nansum((df1 - df) ** 2)
        ii += 1
        print(ii)
    return df2, normlist, error



# my code
# add BMI*Ins_age
data['BMI_Ins_age'] = data['BMI']*data['Ins_Age']
#chose features
#      3. use LinearSVC with L2 C=0.01
features =  ['Product_Info_1', 'Product_Info_4', 'Product_Info_5', 'Ins_Age', 'Ht', 'Wt', 'BMI', 'Employment_Info_1', 'InsuredInfo_2',
 'InsuredInfo_5', 'Insurance_History_2', 'Family_Hist_2', 'Family_Hist_3', 'Family_Hist_4', 'Family_Hist_5', 'Medical_History_4',
 'Medical_History_5', 'Medical_History_17', 'Medical_History_18', 'Medical_History_20', 'Medical_History_26', 'Medical_History_27',
 'Medical_History_28', 'Medical_History_30', 'Medical_History_35', 'Medical_History_38', 'Medical_History_40', 'Medical_Keyword_3',
 'Medical_Keyword_6', 'Medical_Keyword_9', 'Medical_Keyword_12', 'Medical_Keyword_15', 'Medical_Keyword_35', 'Medical_Keyword_38',
 'Medical_Keyword_41', 'Medical_Keyword_45', 'Medical_Keyword_48', 'BMI_Ins_age']

data_3 = data[features]
# print(data_3.head())


data, list, error = fill_svd(data)
data = pd.DataFrame(data)
data.to_csv('complete_data.csv')

# dataclass = MissingMethod(data)
# datasvg = dataclass.fill_avg()
# data = MissingMethod.fill_avg(data)
# print(datasvg)

# # SVM
# cols = datasvg.columns  # features
# # transfer dataframe to matrix
# train_data = datasvg[list(cols)].values
# y = train_data[:, len(cols)-1]
# X = train_data[:, 0:(len(cols)-1)]
#
# clf = SVC(C=1, kernel='rbf')
# clf.fit(X, y)
# print(clf.score(X,y))

