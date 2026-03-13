import pandas as pd
import numpy as np
import os

def generate_synthetic_data(n=1000):
    """Generates synthetic workforce data and saves it to a CSV."""
    np.random.seed(42)

    # Core demographics
    age = np.random.randint(22, 60, n)
    experience = np.maximum(0, age - np.random.randint(18, 25, n))
    gender = np.random.choice(['Male', 'Female', 'Other'], n, p=[0.5, 0.45, 0.05])
    education = np.random.choice(['High School', 'Bachelor', 'Master', 'PhD'], n, p=[0.1, 0.5, 0.3, 0.1])
    
    # Work details
    job_roles = ['Software Engineer', 'Data Scientist', 'HR Manager', 'Sales Rep', 'Marketing Specialist']
    role = np.random.choice(job_roles, n)

    # Map roles to departments
    dept_map = {
        'Software Engineer': 'IT', 
        'Data Scientist': 'IT', 
        'HR Manager': 'HR', 
        'Sales Rep': 'Sales', 
        'Marketing Specialist': 'Marketing'
    }
    department = [dept_map[r] for r in role]
    location = np.random.choice(['Mumbai', 'Bangalore', 'Delhi', 'Hyderabad', 'Chennai', 'Kolkata', 'Remote'], n)
    rating = np.random.randint(1, 6, n)  # 1 to 5 performance rating
    skills = np.random.choice(['Python', 'SQL', 'Communication', 'Marketing', 'Management'], n)
    
    company_tier = np.random.choice(['Startup', 'Mid-Size', 'Enterprise'], n, p=[0.4, 0.4, 0.2])
    certifications = np.random.choice(['None', 'Basic', 'Advanced'], n, p=[0.6, 0.3, 0.1])
    past_companies = np.random.randint(0, 6, n)

    # Base salary calculation rules
    base_salary = 300000 + experience * 150000 + (rating - 3) * 50000
    
    # Salary modifiers
    edu_mod = {'High School': 0.8, 'Bachelor': 1.0, 'Master': 1.25, 'PhD': 1.5}
    base_salary = [s * edu_mod[e] for s, e in zip(base_salary, education)]
    
    role_mod = {
        'Software Engineer': 1.25, 
        'Data Scientist': 1.4, 
        'HR Manager': 1.0, 
        'Sales Rep': 0.85, 
        'Marketing Specialist': 0.95
    }
    base_salary = [s * role_mod[r] for s, r in zip(base_salary, role)]
    
    loc_mod = {'Mumbai': 1.2, 'Bangalore': 1.35, 'Delhi': 1.1, 'Hyderabad': 1.25, 'Chennai': 1.15, 'Kolkata': 1.05, 'Remote': 0.9}
    base_salary = [s * loc_mod[l] for s, l in zip(base_salary, location)]
    
    tier_mod = {'Startup': 0.85, 'Mid-Size': 1.0, 'Enterprise': 1.3}
    base_salary = [s * tier_mod[t] for s, t in zip(base_salary, company_tier)]
    
    cert_mod = {'None': 1.0, 'Basic': 1.1, 'Advanced': 1.25}
    base_salary = [s * cert_mod[c] for s, c in zip(base_salary, certifications)]
    
    base_salary = [s * (1 + (p * 0.05)) for s, p in zip(base_salary, past_companies)]

    # Add realistic random noise
    salary = [s + np.random.normal(0, 50000) for s in base_salary]
    salary = np.round(salary, 2)

    # Create DataFrame
    df = pd.DataFrame({
        'Age': age,
        'Gender': gender,
        'Education Level': education,
        'Years of Experience': experience,
        'Job Role': role,
        'Department': department,
        'Location': location,
        'Performance Rating': rating,
        'Skills': skills,
        'Company Tier': company_tier,
        'Certifications': certifications,
        'Past Companies': past_companies,
        'Salary': salary
    })

    # Inject a few missing values to test preprocessing pipelines
    for col in ['Gender', 'Skills', 'Performance Rating']:
        df.loc[df.sample(frac=0.03).index, col] = np.nan

    # Save format example
    file_path = os.path.join(os.path.dirname(__file__), 'dataset.csv')
    df.to_csv(file_path, index=False)
    print(f"Generated synthetic data format and saved to {file_path}")
    print(df.head())

if __name__ == '__main__':
    generate_synthetic_data()
