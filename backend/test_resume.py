import requests
import json

try:
    with open('../frontend/public/dummy_resume.txt', 'rb') as f:
        res = requests.post('http://localhost:8000/api/predict_resume', files={'file': f})
        print("Status:", res.status_code)
        
        data = res.json()
        with open('out2.txt', 'w', encoding='utf-8') as fw:
            fw.write(f"ML Predicted Salary: {data.get('predicted_salary')}")
except Exception as e:
    print("Error:", e)
