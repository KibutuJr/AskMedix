# cancel_service.py
import os
from dotenv import load_dotenv
from flask import Flask, redirect, url_for, render_template_string
from sheets_utils import get_sheet

load_dotenv()
app = Flask(__name__)

@app.route("/cancel/<token>")
def cancel(token):
    sheet = get_sheet()
    records = sheet.get_all_records()
    for i, rec in enumerate(records, start=2):  # header row is 1
        if rec.get("cancel_token") == token:
            sheet.update_cell(i, 5, "CANCELLED")
            return render_template_string("""
                <h2>✅ Appointment Cancelled</h2>
                <p>Your appointment has been successfully cancelled.</p>
            """)
    return render_template_string("""
        <h2>❌ Invalid Cancellation Link</h2>
        <p>Sorry, we couldn't find your appointment.</p>
    """), 404

if __name__ == "__main__":
    app.run(port=5000, debug=True)
