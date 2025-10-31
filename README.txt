AgriMarket PH - ready-to-run Flask prototype (Shopee-style, farming theme)

How to run:
1. (optional) Create and activate a virtualenv:
   python -m venv venv
   venv\Scripts\activate   (Windows)
   source venv/bin/activate  (Mac/Linux)

2. Install requirements:
   pip install -r requirements.txt

3. Run the app:
   python app.py

4. Open browser at http://127.0.0.1:5000/

Notes:
- Use /register-admin to create the farmer/admin account first.
- Uploaded images are stored in static/uploads/
- The SQLite database file agrimarket.db is created automatically.
