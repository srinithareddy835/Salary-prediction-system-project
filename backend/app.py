from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import pandas as pd
import os
import io
import requests
import PyPDF2
from dotenv import load_dotenv
from salary_prediction import SalaryPredictor

load_dotenv()

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
        predicted_salary = float(prediction)
        
        real_time_insight = None
        current_api_key = os.getenv("GROK_API_KEY")
        if current_api_key:
            try:
                import json
                
                context_data = "No dataset available."
                if os.path.exists(DATASET_PATH):
                    df_ctx = pd.read_csv(DATASET_PATH)
                    similar = df_ctx[(df_ctx['Job Role'] == data.Job_Role) & (df_ctx['Location'] == data.Location)]
                    if len(similar) < 5:
                        similar = df_ctx[(df_ctx['Job Role'] == data.Job_Role)]
                    if similar.empty:
                        similar = df_ctx
                    context_data = similar[['Job Role', 'Years of Experience', 'Location', 'Skills', 'Salary']].head(15).to_csv(index=False)
                
                prompt = (
                    f"Act as a top-tier HR compensation expert. Use the following sample dataset data precisely for baseline context:\n"
                    f"{context_data}\n\n"
                    f"Given this context, predict the EXACT salary for a {data.Job_Role} in {data.Location} with "
                    f"{data.Years_of_Experience} years of experience. Skills: {data.Skills}, Tier: {data.Company_Tier}, Rating: {data.Performance_Rating}.\n"
                    f"Return ONLY a strictly valid JSON object without markdown formatting. It must contain exactly two keys:\n"
                    f'"predicted_salary": (integer strictly representing the final predicted salary amount based on the dataset baseline)\n'
                    f'"insight": (a 1-sentence real-time market insight regarding salary trends and demand for this role)'
                )
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {current_api_key}"
                }
                data_payload = {
                    "model": "grok-beta",
                    "messages": [{"role": "user", "content": prompt}]
                }
                if current_api_key == "your_grok_api_key_here":
                    res_text = '{"predicted_salary": ' + str(predicted_salary) + ', "insight": "Mock AI Insight: Market aligned estimate based on your provided data. (Replace default GROK_API_KEY to see real insights)"}'
                else:
                    response = requests.post("https://api.x.ai/v1/chat/completions", headers=headers, json=data_payload)
                    response.raise_for_status()
                    res_text = response.json()["choices"][0]["message"]["content"].strip()
                
                if res_text.startswith("```json"):
                    res_text = res_text[7:-3].strip()
                elif res_text.startswith("```"):
                    res_text = res_text[3:-3].strip()
                    
                ai_data = json.loads(res_text)
                if "predicted_salary" in ai_data:
                    predicted_salary = float(ai_data["predicted_salary"])
                real_time_insight = ai_data.get("insight", "")
            except Exception as ai_e:
                print(f"Grok AI Error: {ai_e}")
                
        return {
            "predicted_salary": predicted_salary,
            "real_time_insight": real_time_insight
        }
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

@app.post("/api/predict_resume")
async def predict_resume(file: UploadFile = File(...)):
    current_api_key = os.getenv("GROK_API_KEY")
    if not current_api_key:
        raise HTTPException(status_code=500, detail="GROK_API_KEY not configured in backend")
        
    try:
        contents = await file.read()
        filename = file.filename.lower()
        
        resume_text = ""
        if filename.endswith(".pdf"):
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(contents))
            for page in pdf_reader.pages:
                text = page.extract_text()
                if text:
                    resume_text += text + "\n"
        else:
            resume_text = contents.decode('utf-8', errors='ignore')
            
        if not resume_text.strip():
            raise HTTPException(status_code=400, detail="Could not extract text from the file")
            
        import re
        resume_keywords = [
            r"experience", r"education", r"skills", r"projects", r"profile", 
            r"resume", r"cv", r"objective", r"summary", r"work history", r"employment",
            r"bachelor\b", r"master\b", r"degree", r"university", r"college"
        ]
        matches = sum(1 for kw in resume_keywords if re.search(kw, resume_text, re.I))
        if matches < 2:
            raise HTTPException(
                status_code=400, 
                detail="The uploaded file does not appear to be a valid Resume or CV. Please upload a document containing professional experience, skills, and education."
            )
            
        import json
        
        context_data = "No dataset available."
        if os.path.exists(DATASET_PATH):
            df_ctx = pd.read_csv(DATASET_PATH)
            context_data = df_ctx[['Job Role', 'Years of Experience', 'Location', 'Skills', 'Salary']].sample(min(15, len(df_ctx))).to_csv(index=False)
            
        prompt = (
            f"You are a top-tier HR recruiter and compensation expert. I am providing you with a raw resume text.\n\n"
            f"RESUME TEXT:\n---\n{resume_text[:4000]}\n---\n\n"
            f"Please extract the core professional features from this resume in order to predict the candidate's market salary.\n"
            f"Then, using your expertise and the following baseline dataset summary, predict the exact salary for this candidate.\n"
            f"DATASET BASELINE:\n{context_data}\n\n"
            f"Return ONLY a strictly valid JSON object without markdown formatting. It must contain the following keys:\n"
            f'"extracted_profile": an object with keys "Job_Role", "Years_of_Experience" (integer), "Location", "Skills" (comma separated string), "Education_Level". Guess reasonably if missing.\n'
            f'"predicted_salary": integer strictly representing the final predicted salary amount.\n'
            f'"insight": a 2-sentence market insight justifying the salary based on the extracted profile and market conditions.'
        )
        
        ai_data = {}
        if current_api_key == "your_grok_api_key_here" or not current_api_key:
            import re
            
            job_role = "Software Engineer"
            if re.search(r"(Data\s+Scientist|Machine\s+Learning)", resume_text, re.I):
                job_role = "Data Scientist"
            elif re.search(r"Manager", resume_text, re.I):
                job_role = "Manager"
                
            experience = 2
            exp_match = re.search(r"(\d+)\+?\s*years?(?:\s+of)?\s+experience", resume_text, re.I)
            if exp_match:
                experience = int(exp_match.group(1))
                
            education = "Bachelor"
            if re.search(r"(Master|M\.S\.|MBA|M\.Tech)", resume_text, re.I):
                education = "Master"
            elif re.search(r"(PhD|Doctorate)", resume_text, re.I):
                education = "PhD"
                
            location = "Bangalore"
            loc_match = re.search(r"(Mumbai|Delhi|Hyderabad|Pune|Chennai)", resume_text, re.I)
            if loc_match:
                location = loc_match.group(1).title()
                
            skills = "Python"
            if re.search(r"JavaScript|React", resume_text, re.I):
                skills = "JavaScript, React"
                
            ai_data = {
                "extracted_profile": {
                    "Job_Role": job_role,
                    "Years_of_Experience": experience,
                    "Location": location,
                    "Skills": skills,
                    "Education_Level": education
                },
                "insight": "Mock insight: Regex parsed. (Add real GROK_API_KEY for true AI extraction)"
            }
        else:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {current_api_key}"
            }
            data_payload = {
                "model": "grok-beta",
                "messages": [{"role": "user", "content": prompt}]
            }
            response = requests.post("https://api.x.ai/v1/chat/completions", headers=headers, json=data_payload)
            response.raise_for_status()
            res_text = response.json()["choices"][0]["message"]["content"].strip()
            
            if res_text.startswith("```json"):
                res_text = res_text[7:-3].strip()
            elif res_text.startswith("```"):
                res_text = res_text[3:-3].strip()
                
            ai_data = json.loads(res_text)
            
        profile = ai_data.get("extracted_profile", {})
        input_dict = {
            'Age': 30,
            'Gender': 'Male',
            'Education Level': profile.get('Education_Level', 'Bachelor'),
            'Years of Experience': int(profile.get('Years_of_Experience', 2)),
            'Job Role': profile.get('Job_Role', 'Software Engineer'),
            'Department': 'Engineering',
            'Location': profile.get('Location', 'Bangalore'),
            'Performance Rating': 3,
            'Skills': profile.get('Skills', 'Python'),
            'Company Tier': 'Mid-Size',
            'Certifications': 'None',
            'Past Companies': 1
        }
        
        if predictor is not None:
            prediction = float(predictor.predict(input_dict))
            ai_data["predicted_salary"] = prediction
        else:
            if "predicted_salary" not in ai_data:
                ai_data["predicted_salary"] = 1500000 
                
        return ai_data
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
