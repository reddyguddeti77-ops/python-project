UPI Transaction Reconciliation

This is our mini project on UPI transaction reconciliation for a payment aggregator. We made a small web app that compares the transactions recorded by the merchant with the settlement file that NPCI sends, and then shows which transactions have problems.

We are beginners, so we kept the project simple and used Python, Flask and SQLite.

Team Members
Name	Role
(Member 1)	Data loading and database
(Member 2)	Reconciliation logic
(Member 3)	Frontend / dashboard
What is the problem?

When a customer pays through UPI, two records are created:

Merchant record - saved by our own system when the payment happens.
NPCI settlement file - sent by NPCI the next day (T+1) showing what was actually settled.

Reconciliation means checking that both records match. Our app finds:

Unsettled transactions - merchant has the payment but NPCI never settled it
Double settled transactions - NPCI settled the same payment two times
Problems we had to solve
Different reference format: the merchant ID and the NPCI reference number (RRN) are not written the same way, so we clean both (remove spaces, make uppercase, etc.) before comparing them.
Refunds look like new transactions: in the settlement file a refund comes as a separate new row. We link it back to the original payment using original_rrn and mark the original as REVERSED instead of UNSETTLED.
Status labels used
Status	Meaning
MATCHED	Found in settlement file with the same amount
UNSETTLED	Not found in settlement file
DOUBLE_SETTLED	Found two or more times in settlement file
REVERSED	A refund was made for this payment
AMOUNT_MISMATCH	Found but the amount is different
Technologies Used
Python
Flask (backend)
SQLite (database)
pandas (reading CSV files)
HTML, CSS, JavaScript (frontend)
PyInstaller (to make the .exe)
Folder Structure
upi_project/
├── paths.py
├── data/
│   └── generate_sample_data.py
├── db/
│   └── load_data.py
├── engine/
│   └── reconcile.py
└── frontend/
    ├── server.py
    ├── templates/
    │   └── index.html
    └── static/
        ├── style.css
        └── script.js
generate_sample_data.py - makes fake merchant and NPCI CSV files for testing
load_data.py - creates the database and loads the CSV files into it
reconcile.py - the main matching logic
server.py - Flask server that connects the logic to the webpage
index.html, style.css, script.js - the dashboard page
paths.py - keeps file paths correct (needed so the .exe works properly)
How to Run
Install Python from python.org (tick "Add Python to PATH" while installing).
Install the libraries:
   python -m pip install flask pandas
Make the sample data:
   python data/generate_sample_data.py
Start the app:
   python frontend/server.py
Open http://localhost:5000 in the browser (it should open automatically).
Upload merchant_transactions.csv and npci_settlement.csv from the data folder and click Run reconciliation.
Output we got with the sample data
MATCHED          20
UNSETTLED        1
DOUBLE_SETTLED   1
REVERSED         1
AMOUNT_MISMATCH  1
TOTAL            24
Making the .exe file (Windows only)
python -m pip install pyinstaller
python -m PyInstaller --onefile --name run_app --add-data "frontend/templates;frontend/templates" --add-data "frontend/static;frontend/static" --hidden-import=flask --hidden-import=pandas --hidden-import=numpy frontend/server.py

The file will be created at dist/run_app.exe. Double click it and the dashboard opens in the browser. Keep the black console window open while using the app.

Problems we faced
"No module named flask" - we had to install flask using python -m pip install flask.
"run_app.exe is not recognized" - we were not inside the dist folder. In PowerShell we also have to type .\run_app.exe.
PermissionError while building - the old exe was still running and OneDrive was locking the file. We closed it and paused OneDrive.
Browser not opening from the exe - webbrowser.open did not work inside the exe, so we used os.startfile instead.
Reference numbers became 402500001023.0 - pandas read them as numbers, so we forced those columns to be read as text.
What we learned
How UPI settlement and reconciliation works
Reading and cleaning CSV files with pandas
Making a small Flask API and connecting it to a webpage
Using SQLite as a database
Converting a Python project into an .exe
Future Improvements
Match transactions using amount + time when the reference number is missing
Add charts to the dashboard
Export report to Excel
Add test cases
Note

This project uses fake sample data only. It is not connected to the real NPCI system.
