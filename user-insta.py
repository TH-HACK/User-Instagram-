import random
import string
import requests
import time
import getpass
from itertools import cycle
from concurrent.futures import ThreadPoolExecutor
from colorama import Fore, Style, init

# تهيئة مكتبة colorama
init(autoreset=True)

# إعدادات بوت تليجرام (ستُملأ عند التشغيل)
TELEGRAM_BOT_TOKEN = None
TELEGRAM_CHAT_ID = None

# الألوان المتدرجة الجديدة (أحمر، أصفر، أخضر، أزرق فاتح)
colors = [Fore.RED, Fore.YELLOW, Fore.GREEN, Fore.CYAN]

def print_banner():
    """طباعة شعار OTH بألوان متدرجة."""
    banner_lines = [
        "   ____  _______ _    _ ",
        "  / __ \\|__   __| |  | |",
        " | |  | |  | |  | |__| |",
        " | |  | |  | |  |  __  |",
        " | |__| |  | |  | |  | |",
        "  \\____/   |_|  |_|  |_|"
    ]

    # تدوير الألوان عبر الشعار لخلق تأثير متدرج
    for line in banner_lines:
        colored_line = "".join(next(cycle(colors)) + char for char in line)
        print(colored_line)
        time.sleep(0.001)  # انتظار قصير لإنشاء تأثير الحركة
    print(Style.RESET_ALL)  # إعادة تعيين الألوان

    # طباعة رسالة الترحيب بعد الشعار
    welcome_message = f"{Fore.GREEN}{Style.BRIGHT}Welcome to the OTH Instagram Username Checker!{Style.RESET_ALL}"
    print("\n" + welcome_message)

def generate_username(length):
    """توليد اسم مستخدم عشوائي بطول معين ويشمل الرموز _ و ."""
    characters = string.ascii_lowercase + string.digits + "_."
    return ''.join(random.choices(characters, k=length))

def check_username_availability(username):
    """التحقق من توفر اسم المستخدم على Instagram."""
    url = f"https://www.instagram.com/{username}/?__a=1"
    response = requests.get(url)
    if response.status_code == 404:
        return True  # اسم المستخدم متاح
    elif response.status_code == 200:
        return False  # اسم المستخدم محجوز
    else:
        return None  # في حالة حدوث خطأ آخر

def send_to_telegram(message):
    """إرسال رسالة إلى بوت تليجرام."""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    requests.post(url, data=payload)

def process_usernames(length):
    available_usernames = []
    unavailable_usernames = []

    print(f"{Fore.YELLOW}Checking usernames of length {length} characters...{Style.RESET_ALL}")
    for _ in range(100):  # يمكنك تعديل عدد المحاولات هنا
        username = generate_username(length)
        result = check_username_availability(username)
        if result is True:
            available_usernames.append(username)
            print(f"{Fore.GREEN}Available: {username}{Style.RESET_ALL}")
            send_to_telegram(f"✅ Available: {username}")
        elif result is False:
            unavailable_usernames.append(username)
            print(f"{Fore.RED}Taken: {username}{Style.RESET_ALL}")
        time.sleep(0.1)  # انتظار قصير لتجنب الحظر

    return available_usernames, unavailable_usernames

def clean_input(user_input):
    """إزالة الرموز ^ و @ من المدخلات."""
    return user_input.replace("^", "").replace("@", "")

def validate_input(prompt):
    while True:
        user_input = input(prompt).strip()
        cleaned_input = clean_input(user_input)
        if user_input != cleaned_input:
            print(f"{Fore.YELLOW}Invalid characters (@ or ^) detected and removed.{Style.RESET_ALL}")
        return cleaned_input

def main():
    global TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

    # طباعة الشعار والرسالة الترحيبية
    print_banner()

    # طلب معلومات بوت تليجرام من المستخدم مع التحقق من المدخلات
    TELEGRAM_BOT_TOKEN = validate_input(f"{Fore.BLUE}Please enter your Telegram Bot Token (without @ or ^):{Style.RESET_ALL} ")
    TELEGRAM_CHAT_ID = validate_input(f"{Fore.BLUE}Please enter your Telegram Chat ID (without @ or ^):{Style.RESET_ALL} ")

    # الحصول على اسم مستخدم الجهاز تلقائيًا
    local_username = getpass.getuser()

    # إرسال رسالة ترحيب إلى التليجرام
    welcome_message = f"مرحبا {local_username}، جاري التحقق من يوزر يرجى الصبر 💓 @l7_l7aj_1"
    send_to_telegram(welcome_message)

    # طلب اختيار طول أسماء المستخدمين
    print(f"{Fore.BLUE}Please choose the username length:{Style.RESET_ALL}")
    print("1. 2 characters")
    print("2. 3 characters")
    print("3. 4 characters")
    choice = input("Enter your choice (1/2/3): ").strip()

    if choice == "1":
        lengths = [2]
    elif choice == "2":
        lengths = [3]
    elif choice == "3":
        lengths = [4]
    else:
        print(f"{Fore.RED}Invalid choice! Exiting...{Style.RESET_ALL}")
        return

    all_available = []
    all_unavailable = []

    with ThreadPoolExecutor() as executor:
        results = executor.map(process_usernames, lengths)
        for available, unavailable in results:
            all_available.extend(available)
            all_unavailable.extend(unavailable)

    # حفظ النتائج في ملفات نصية
    with open('available_usernames.txt', 'w') as file:
        file.write("\n".join(all_available))

    with open('unavailable_usernames.txt', 'w') as file:
        file.write("\n".join(all_unavailable))

if __name__ == "__main__":
    main()
