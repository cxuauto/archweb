from selenium import webdriver
from selenium.webdriver.common.keys import Keys
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
wd = webdriver.Chrome(options=options)
wd.implicitly_wait(10)

import time, re, os, requests

wd.get("https://archive.org/account/login")
elem = wd.find_element_by_css_selector(".login-form .input-email")
elem.clear()
elem.send_keys(os.environ.get('EMAIL_ADD'),
               Keys.TAB,
               os.environ.get('PASSD'),
               Keys.RETURN)
print("login")
time.sleep(6)

url_list = [
            "https://www.greaterwrong.com/?sort=hot",
            "https://pattern.swarma.org/?page=time",
            "https://forum.obsidian.md/c/knowledge-management/6",
            "https://rizime.substack.com/archive?sort=new",
            "https://www.lesswrong.com/allPosts",
            "https://shimo.im/docs/tjRWrtPYp8JTrpHY/read",
            "https://acacess.substack.com/archive?sort=new",
            "https://swarma.org/",
            "http://headsalon.org/catalog",
            "https://www.foretold.io/c/home/activity",
            "https://www.overcomingbias.com/",
]

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

    wd.find_element_by_id("web-save-url-input").send_keys(url_save)
    elem = wd.find_element_by_id("capture_outlinks")
    elem.click()
    elem.submit()
    print("Saving: ", url_save)
    
    successful = wait_check()
    if not successful:
        failed_list.append(url_save)

print("Failed Savings:")
for item in failed_list:
    print(item)
