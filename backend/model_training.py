import os
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib

from data_preprocessing import load_data, get_preprocessor, prepare_data

def train_and_evaluate():
    """Trains multiple models, evaluates them, and saves the best one."""
    
    current_dir = os.path.dirname(__file__)
    dataset_path = os.path.join(current_dir, 'dataset.csv')
    
    print("Loading data...")
    if not os.path.exists(dataset_path):
        print(f"Dataset not found at {dataset_path}. Please run generate_data.py first.")
        return
        
    df = load_data(dataset_path)
    
    print("Preparing data and creating preprocessing pipeline...")
    X_train, X_test, y_train, y_test = prepare_data(df)
    preprocessor = get_preprocessor()
    
    # Define candidate models
    models = {
        'Linear Regression': LinearRegression(),
        'Decision Tree': DecisionTreeRegressor(random_state=42),
        'Random Forest': RandomForestRegressor(n_estimators=100, random_state=42),
        'Gradient Boosting': GradientBoostingRegressor(random_state=42)
    }
    
    best_model = None
    best_r2 = -float('inf')
    best_model_name = ""
    
    print("\nTraining and Evaluating Models:")
    print("-" * 35)
    
    for name, model in models.items():
        print(f"Training {name}...")
        
        # Create pipeline: preprocessor -> model
        clf = Pipeline(steps=[
            ('preprocessor', preprocessor),
            ('model', model)
        ])
        
        # Train model
        clf.fit(X_train, y_train)
        
        # Predict on test set
        y_pred = clf.predict(X_test)
        
        # Evaluate model performance
        mae = mean_absolute_error(y_test, y_pred)
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        print(f"Performance for {name}:")
        print(f"  MAE: ₹{mae:,.2f}")
        print(f"  MSE: {mse:,.2f}")
        print(f"  R2:  {r2:.4f}\n")
        
        # Track the best model based on R-squared score
        if r2 > best_r2:
            best_r2 = r2
            best_model = clf
            best_model_name = name
            
    print("-" * 35)
    print(f"🏆 Best Model Selected: {best_model_name} with R2 = {best_r2:.4f}")
    
    # Save the best model
    model_path = os.path.join(current_dir, 'model.joblib')
    joblib.dump(best_model, model_path)
    print(f"💾 Model successfully saved to {model_path}")

if __name__ == '__main__':
    train_and_evaluate()
