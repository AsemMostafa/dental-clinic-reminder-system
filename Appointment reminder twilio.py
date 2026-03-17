import gspread
from oauth2client.service_account import ServiceAccountCredentials
from twilio.rest import Client
from datetime import datetime, timedelta

# --- Google Sheets Setup ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

sheet = client.open("Patients").sheet1  # Change to your sheet name
data = sheet.get_all_records()

# --- Twilio Setup ---
account_sid = 'AC0fd020a105177ac43603e8431cec5aaf'
auth_token = '**************************'
twilio_client = Client(account_sid, auth_token)
twilio_whatsapp_number = 'whatsapp:+14155238886'  # Twilio Sandbox Number

# --- Loop through patients ---
for idx, patient in enumerate(data, start=2):  # start=2 because row 1 is header
    name_ar = patient['First Name (arabic)']
    name_en = patient['First Name (english)']
    whatsapp_number = patient['WhatsApp_Number']
    last_visit = datetime.strptime(patient['Last_Visit_Date'], '%d/%m/%Y')
    Gender = patient['Gender'].upper()
    last_reminder = patient.get('Last_Reminder_Date', '')

    # Check if 6 months passed and reminder not sent today
    today = datetime.today().date()
    six_months_after = (last_visit + timedelta(days=180)).date()
    
    if today >= six_months_after:
        if last_reminder:
            continue
        
        # Arabic greeting adjustment based on sex
        if Gender == 'M':
            arabic_msg = f"نأمل أن تكون بخير!"
        elif Gender == 'F':
            arabic_msg = f"نأمل أن تكوني بخير!"
        else:
            arabic_msg = "نأمل أن تكون/ي بخير!"
        
        # Build message
        message_text = f"""
مرحباً {name_ar} 🌸
معك د. عاصم مصطفي -أخصائي تجميل الأسنان
{arabic_msg} مرّ حوالي ٦ أشهر منذ آخر زيارة لك، وحان وقت جلسة تنظيف الأسنان والمتابعة.
دعنا نحافظ على ابتسامتك الجميلة 😁
يمكنك الرد على هذه الرسالة لتحديد موعد مناسب لك. 

Hi, {name_en}🌸
This is Dr.Assem Mostafa-Cosmetic dentistry Specialist 
Hope you’re doing well! It’s been about 6 months since your last visit — time for your dental cleaning and check-up.
Let’s keep that beautiful smile shining! 😁
You can reply here to book your appointment.
"""
        # Send WhatsApp Message
        twilio_client.messages.create(
            body=message_text,
            from_=twilio_whatsapp_number,
            to=f'whatsapp:{whatsapp_number}'
        )
        print(f"Reminder sent to {name_en}")
        
        # Update Last_Reminder_Date in Google Sheet
        sheet.update_cell(idx, 9, today.strftime('%Y-%m-%d'))  # column 9 = Last_Reminder_Date
    
  






