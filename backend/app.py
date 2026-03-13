from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import os
import io
from salary_prediction import SalaryPredictor

app = FastAPI(title="Workforce Salary Prediction API")

# Setup CORS to allow React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CURRENT_DIR = os.path.dirname(__file__)
DATASET_PATH = os.path.join(CURRENT_DIR, 'dataset.csv')
MODEL_PATH = os.path.join(CURRENT_DIR, 'model.joblib')

predictor = None
try:
    if os.path.exists(MODEL_PATH):
        predictor = SalaryPredictor('model.joblib')
except Exception as e:
    print(f"Error loading model: {e}")

class EmployeeData(BaseModel):
    Age: int
    Gender: str
    Education_Level: str
    Years_of_Experience: int
    Job_Role: str
    Department: str
    Location: str
    Performance_Rating: int
    Skills: str
    Company_Tier: str
    Certifications: str
    Past_Companies: int

@app.get("/api/status")
def get_status():
    return {
        "model_loaded": predictor is not None,
        "dataset_exists": os.path.exists(DATASET_PATH)
    }

@app.get("/api/options")
def get_options():
    if not os.path.exists(DATASET_PATH):
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    df = pd.read_csv(DATASET_PATH)
    
    return {
        "job_roles": sorted(df['Job Role'].dropna().unique().tolist()) if 'Job Role' in df.columns else [],
        "departments": sorted(df['Department'].dropna().unique().tolist()) if 'Department' in df.columns else [],
        "locations": sorted(df['Location'].dropna().unique().tolist()) if 'Location' in df.columns else [],
        "skills": sorted(df['Skills'].dropna().unique().tolist()) if 'Skills' in df.columns else [],
        "company_tiers": sorted(df['Company Tier'].dropna().unique().tolist()) if 'Company Tier' in df.columns else ["Startup", "Mid-Size", "Enterprise"],
        "certifications": sorted(df['Certifications'].dropna().unique().tolist()) if 'Certifications' in df.columns else ["None", "Basic", "Advanced"],
        "genders": ["Male", "Female", "Other"],
        "education_levels": ["High School", "Bachelor", "Master", "PhD"]
    }

@app.post("/api/predict")
def predict_salary(data: EmployeeData):
    if predictor is None:
        raise HTTPException(status_code=500, detail="Model not loaded")
    
    input_dict = {
        'Age': data.Age,
        'Gender': data.Gender,
        'Education Level': data.Education_Level,
        'Years of Experience': data.Years_of_Experience,
        'Job Role': data.Job_Role,
        'Department': data.Department,
        'Location': data.Location,
        'Performance Rating': data.Performance_Rating,
        'Skills': data.Skills,
        'Company Tier': data.Company_Tier,
        'Certifications': data.Certifications,
        'Past Companies': data.Past_Companies
    }
    
    try:
        prediction = predictor.predict(input_dict)
        return {"predicted_salary": float(prediction)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/predict_batch")
async def predict_batch(file: UploadFile = File(...)):
    if predictor is None:
        raise HTTPException(status_code=500, detail="Model not loaded")
        
    try:
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
        
        required_cols = ['Age', 'Gender', 'Education Level', 'Years of Experience', 'Job Role', 'Department', 'Location', 'Performance Rating', 'Skills', 'Company Tier', 'Certifications', 'Past Companies']
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            raise HTTPException(status_code=400, detail=f"Missing columns: {', '.join(missing_cols)}")
            
        predictions = predictor.model.predict(df)
        df['Predicted Salary (₹)'] = predictions
        
        # We can format directly or return the raw array
        # Return as JSON records so React can render a table
        formatted_df = df.copy()
        formatted_df['Predicted Salary (₹)'] = formatted_df['Predicted Salary (₹)'].apply(lambda x: f"₹{x:,.2f}")
        
        return {"results": formatted_df.to_dict(orient="records")}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/visualization_data")
def get_visualization_data():
    if not os.path.exists(DATASET_PATH):
        raise HTTPException(status_code=404, detail="Dataset not found")
        
    df = pd.read_csv(DATASET_PATH)
    
    # Pre-aggregate data to send minimal payload
    # 1. Salary Distribution (histogram bins approx)
    hist, bin_edges = pd.cut(df['Salary'].dropna(), bins=30, retbins=True)
    salary_dist = hist.value_counts().sort_index().tolist()
    bin_labels = [f"{int(e)}k" for e in bin_edges[:-1]/1000]
    
    # 2. Average Salary by Job Role
    role_salary = df.groupby('Job Role')['Salary'].mean().sort_values(ascending=False).to_dict()
    
    # 3. Average Salary by Location
    loc_salary = df.groupby('Location')['Location'].count().to_dict() # Wait, need salary mean
    loc_salary = df.groupby('Location')['Salary'].mean().sort_values(ascending=False).to_dict()

    return {
        "role_salary": [{"role": k, "salary": v} for k, v in role_salary.items()],
        "location_salary": [{"location": k, "salary": v} for k, v in loc_salary.items()],
        "salary_dist_labels": bin_labels,
        "salary_dist_values": salary_dist
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
