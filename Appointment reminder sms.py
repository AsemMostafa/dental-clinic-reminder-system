import gspread
import requests
import time
from datetime import datetime, timedelta
from oauth2client.service_account import ServiceAccountCredentials

# ---------------------------
# GOOGLE SHEETS SETUP
# ---------------------------

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_name(
    "credentials.json", scope
)

client = gspread.authorize(creds)

sheet = client.open("Patients").sheet1
data = sheet.get_all_records()

# ---------------------------
# TEXTBEE CONFIG
# ---------------------------

API_KEY = " "
DEVICE_ID = " "

TEXTBEE_URL = f"https://api.textbee.dev/api/v1/gateway/devices/{DEVICE_ID}/send-sms"


def send_sms(phone, message):

    payload = {
        "recipients": [phone],
        "message": message
    }

    headers = {
        "x-api-key": API_KEY,
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(TEXTBEE_URL, json=payload, headers=headers)

        if response.status_code == 200:
            print(f"SMS sent to {phone}")
        else:
            print(f"Error sending to {phone}: {response.text}")

    except Exception as e:
        print(f"Connection error: {e}")


# ---------------------------
# CLEAN PHONE NUMBER
# ---------------------------

def clean_phone(phone):

    phone = str(phone).strip()

    if phone.startswith("0"):
        phone = "20" + phone[1:]

    if phone.startswith("+"):
        phone = phone[1:]

    return phone


# ---------------------------
# MAIN LOOP
# ---------------------------

today = datetime.today().date()

for idx, patient in enumerate(data, start=2):

    try:

        name_ar = patient['First Name (arabic)']
        name_en = patient['First Name (english)']
        phone = clean_phone(patient['WhatsApp_Number'])
        gender = patient['Gender'].upper()

        last_visit = datetime.strptime(
            patient['Last_Visit_Date'], '%d/%m/%Y'
        )

        last_reminder = patient.get('Last_Reminder_Date', '')

        six_months_after = (last_visit + timedelta(days=180)).date()

        if today >= six_months_after:

            if last_reminder:
                continue

            # Arabic greeting
            if gender == 'M':
                arabic_msg = "نأمل أن تكون بخير!"
            elif gender == 'F':
                arabic_msg = "نأمل أن تكوني بخير!"
            else:
                arabic_msg = "نأمل أن تكون/ي بخير!"

            # Build message
            message_text = f"""
مرحباً {name_ar} 
معك د. عاصم مصطفي -أخصائي تجميل الأسنان
{arabic_msg} مرّ حوالي ٦ أشهر منذ آخر زيارة لك، وحان وقت جلسة تنظيف الأسنان والمتابعة.
دعنا نحافظ على ابتسامتك الجميلة 
في انتظار تواصلكم لتحديد موعد مناسب لك. 
"""
            
            # Send SMS
            send_sms(phone, message_text)

            print(f"Reminder sent to {name_en}")

            # Update sheet
            sheet.update_cell(idx, 9, today.strftime('%Y-%m-%d'))

            # Delay between SMS
            time.sleep(5)

    except Exception as e:

        print(f"Error processing row {idx}: {e}")
