import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder

def load_data(filepath):
    """
    Load dataset using pandas.
    """
    df = pd.read_csv(filepath)
    return df

def get_preprocessor():
    """
    Creates a data preprocessing pipeline for numerical and categorical features.
    Handles missing values, encoding, and normalization.
    """
    numeric_features = ['Age', 'Years of Experience', 'Performance Rating', 'Past Companies']
    categorical_features = ['Gender', 'Education Level', 'Job Role', 'Department', 'Location', 'Skills', 'Company Tier', 'Certifications']

    # Preprocessing for numerical data: Impute missing values with median, then scale
    numeric_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])

    # Preprocessing for categorical data: Impute missing with constant, then one-hot encode
    categorical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='constant', fill_value='missing')),
        ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
    ])

    # Bundle preprocessing for numerical and categorical data
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_features),
            ('cat', categorical_transformer, categorical_features)
        ])
    
    return preprocessor

def prepare_data(df):
    """
    Splits data into train and test sets.
    """
    # Exclude target from predictors
    X = df.drop('Salary', axis=1)
    y = df['Salary']
    
    # Split into 80% train and 20% test data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    return X_train, X_test, y_train, y_test
