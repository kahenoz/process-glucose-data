--python3.12 

python -m venv venv
pip install -r requirements.txt
uvicorn app:app --reload

API CALLS
-----
POST
http://127.0.0.1:8000/upload-data

Body -->> form-data -->> key:file, value:sample_glucose_data.csv

------
GET
http://127.0.0.1:8000/metrics/101

no params needed

------
GET
http://127.0.0.1:8000/trends/101

no params needed

