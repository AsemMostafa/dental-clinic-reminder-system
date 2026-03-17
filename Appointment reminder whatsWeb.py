import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timedelta
import pywhatkit
import time

# --- Google Sheets Setup ---
scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/drive"]

creds = ServiceAccountCredentials.from_json_keyfile_name(
    "credentials.json", scope)

client = gspread.authorize(creds)

sheet = client.open("Patients").sheet1
data = sheet.get_all_records()

print("Starting WhatsApp reminder system...")

# --- Loop through patients ---
for idx, patient in enumerate(data, start=2):

    name_ar = patient['First Name (arabic)']
    name_en = patient['First Name (english)']
    whatsapp_number = str(patient['WhatsApp_Number'])

# Ensure number starts with +
    if not whatsapp_number.startswith("+"):
       whatsapp_number = "+20" + whatsapp_number.lstrip("0")
    
    last_visit = datetime.strptime(patient['Last_Visit_Date'], '%d/%m/%Y')
    Gender = patient['Gender'].upper()
    last_reminder = patient.get('Last_Reminder_Date', '')
    today = datetime.today().date()
    six_months_after = (last_visit + timedelta(days=180)).date()

    # Check reminder condition
    if today >= six_months_after:
        if last_reminder:
                continue

        # Arabic greeting
        if Gender == 'M':
            arabic_msg = "نأمل أن تكون بخير!"
        elif Gender == 'F':
            arabic_msg = "نأمل أن تكوني بخير!"
        else:
            arabic_msg = "نأمل أن تكون/ي بخير!"

        # Message
        message_text = f"""
مرحباً {name_ar} 🌸
معك د. عاصم مصطفي -أخصائي تجميل الأسنان
{arabic_msg} مرّ حوالي ٦ أشهر منذ آخر زيارة لك، وحان وقت جلسة تنظيف الأسنان والمتابعة.
دعنا نحافظ على ابتسامتك الجميلة 😁
يمكنك الرد على هذه الرسالة لتحديد موعد مناسب لك.

Hi, {name_en} 🌸
This is Dr. Assem Mostafa - Cosmetic Dentistry Specialist
Hope you’re doing well! It’s been about 6 months since your last visit — time for your dental cleaning and check-up.
Let’s keep that beautiful smile shining! 😁
You can reply here to book your appointment.
"""

        try:
            # --- Send WhatsApp Message using pywhatkit ---
            pywhatkit.sendwhatmsg_instantly(
                whatsapp_number,
                message_text,
                wait_time=20,
                tab_close=True
            )

            print(f"Reminder sent to {name_en}")

            # Update reminder date in sheet
            sheet.update_cell(idx, 9, today.strftime('%d/%m/%Y'))

            time.sleep(15)  # avoid WhatsApp rate limits

        except Exception as e:
            print(f"Failed to send message to {name_en}: {e}")

print("Process finished.")