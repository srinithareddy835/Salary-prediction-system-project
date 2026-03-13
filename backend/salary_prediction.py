import joblib
import pandas as pd
import os

class SalaryPredictor:
    def __init__(self, model_filename='model.joblib'):
        """
        Loads the trained machine learning model from disk.
        """
        current_dir = os.path.dirname(__file__)
        model_path = os.path.join(current_dir, model_filename)
        
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Trained model not found at {model_path}. Please run model_training.py first.")
            
        self.model = joblib.load(model_path)
        
    def predict(self, employee_details):
        """
        Accepts dictionary containing employee details and predicts expected salary.
        """
        # Convert the dictionary exactly to a 2D DataFrame (1 row, N columns)
        df = pd.DataFrame([employee_details])
        
        # The scikit-learn pipeline performs both data preprocessing (missing values, 
        # encoding, scaling) and predicting using the loaded trained weights.
        prediction = self.model.predict(df)
        
        # Since prediction returns an array, we grab the first element
        return prediction[0]

# --- Testing code to demonstrate how to use it programmatically ---
def test_prediction():
    try:
        predictor = SalaryPredictor()
        
        # Example employee format
        sample_employee = {
            'Age': 28,
            'Gender': 'Female',
            'Education Level': 'Master',
            'Years of Experience': 5,
            'Job Role': 'Data Scientist',
            'Department': 'IT',
            'Location': 'Mumbai',
            'Performance Rating': 5,
            'Skills': 'Python',
            'Company Tier': 'Enterprise',
            'Certifications': 'Advanced',
            'Past Companies': 2
        }
        
        salary = predictor.predict(sample_employee)
        print("\n=== Programmatic Prediction Example ===")
        print(f"Given Employee Details: {sample_employee}")
        print(f"➡️  Predicted Expected Salary: ₹{salary:,.2f}")
        
    except Exception as e:
        print(f"Error test_prediction(): {e}")

if __name__ == "__main__":
    test_prediction()
