import smtplib

EMAIL = "daveogara87@gmail.com"
PASSWORD = "ivvm oenl txfc uftw"

try:
    server = smtplib.SMTP("smtp.gmail.com", 587)  # Or your SMTP server
    server.starttls()
    server.login(EMAIL, PASSWORD)
    print("✅ SMTP Login successful!")
    server.quit()
except Exception as e:
    print("❌ SMTP Error:", e)
