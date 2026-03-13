# Workforce Salary Prediction System

This is a complete end-to-end Machine Learning project that predicts an employee's expected salary based on their workforce data, constructed with Python and Streamlit.

## Features
- **Data Preprocessing**: Handles missing values, performs one-hot encoding on categorical data, and scales numerical values.
- **Machine Learning**: Evaluates Multiple models (Linear Regression, Random Forest, Decision Tree) and selects the one with the highest R² score to utilize.
- **Prediction System**: Saves and loads the trained model using `joblib` for rapid inference.
- **Web UI & Visualization**: Interactive user interface via Streamlit. Provides intuitive charts and dynamic predictions directly on the browser.

## Project Structure
- `generate_data.py`: A utility script to generate the `dataset.csv` with synthetic workforce data. 
- `dataset.csv`: Example dataset with columns such as Age, Job Role, Experience, Location, and Salary.
- `data_preprocessing.py`: Contains the `scikit-learn` ColumnTransformer and Pipeline objects handling encoding, interpolation, and feature scaling.
- `model_training.py`: Model loader which fits regressors using preprocessed data, evaluates them using MAE, MSE, & R², and saves `model.joblib`.
- `salary_prediction.py`: Loads the model and wraps it into a Python backend API logic for usage.
- `app.py`: Streamlit User Interface allowing user inputs and visualization plotting.

## Step-by-Step Instructions to Run the Project

1. **Install Dependencies**
Ensure you have Python installed, then install the required libraries:
```bash
pip install pandas numpy scikit-learn streamlit matplotlib seaborn joblib
```

2. **Generate Dataset**
Generate the synthetic `dataset.csv` file:
```bash
python generate_data.py
```

3. **Train the ML Model**
Run the training module which will process the dataset, evaluate multiple models, pick the best one, and save it as `model.joblib`:
```bash
python model_training.py
```

4. **Run the User Interface / Streamlit App**
Start the application to see the visualizations and make predictions:
```bash
streamlit run app.py
```
This will open a new tab in your browser with the prediction system!
