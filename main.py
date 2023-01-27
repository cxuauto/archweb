from shutil import which
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument("enable-automation");
options.add_argument("start-maximized");
options.add_argument("--disable-infobars")
options.add_argument("--disable-browser-side-navigation");
options.add_argument('--disable-dev-shm-usage')
options.add_argument("--disable-extensions");
options.add_argument("--dns-prefetch-disable");
options.add_argument("--disable-gpu");
# options.page_load_strategy='normal';

from data import url_list

CHROMEPATH = which("chromium-browser")
options.binary_location=CHROMEPATH
wd = webdriver.Chrome(options=options)
wd.implicitly_wait(10)

import time, re, os, requests

wd.get("https://archive.org/account/login")
elem = wd.find_element(By.CSS_SELECTOR, ".login-form .input-email")
elem.clear()
elem.send_keys(os.environ.get('EMAIL_ADD'),
               Keys.TAB,
               os.environ.get('PASSD'),
               Keys.RETURN)
print("login")
time.sleep(6)

failed_list = []

def check():
    try:
        track_id = re.findall('watchJob\("(.*?)"', wd.page_source)[0]
        resp = requests.get(f"https://web.archive.org/save/status/{track_id}?_t=" + str(int(time.time()*100)) ).json()
    except:
        return 'No Result'    
    return resp['status']

def wait_check():
        min = 0
        step = 1
        Flag = False
        while min<3:
            time.sleep(step * 60)
            status = check()
            print(f"{status} at {min}")
            if status == 'pending':
                pass
            elif status == 'success':
                Flag = True
            else:
                break
            min += step
        status = check()
        return Flag

for url_save in url_list:
    wd.get("https://web.archive.org/save") 

    wd.find_element(By.ID, "web-save-url-input").send_keys(url_save)
    elem = wd.find_element(By.ID,"capture_outlinks")
    elem.click()
    elem.submit()
    print("Saving: ", url_save)
    
    successful = wait_check()
    if not successful:
        failed_list.append(url_save)

print("Failed Savings:")
for item in failed_list:
    print(item)
