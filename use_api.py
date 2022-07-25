import requests as rq
import os, time
from data import url_list

headers = {'Accept': 'application/json',
"Authorization": f"LOW {os.environ.get('MYACCESSKEY')}:{os.environ.get('MYSECRET')}", 
}
api_url = 'https://web.archive.org/save'

api_url = 'https://web.archive.org/save'
job_query = []
for i, url in enumerate(url_list):
    
    data = {
        'url': url,
        'skip_first_archive': '1',#这个参数，能减少IA那边的数据库查询，加快存档速度
        'js_behavior_timeout': '30',#让js最多运行30s（默认是5s），似乎可以应对一些图片懒加载网速比较慢的网页
        'capture_outlinks': '1',
    }

    r = rq.post(api_url, headers=headers, data=data)
    if r.status_code != 200:
        print(url, r.text[:256])
    else:
        try:
            job_id = r.json()['job_id']
        except:
            print("Failed to get job_id", r.text[:256])
            continue
#         try:
#             job_query += [(url, job_id)]
# #             job_info = requests.get(f"https://web.archive.org/save/status/{job_id}?_t=" + str(int(time.time()*100)) ).json()
#             print(url, job_info['status'])
#         except:
#             print(url, 'No Result')

    if i!=0 and i%8 == 0:
        time.sleep(3*60)
        for job_url, job_id in job_query:
            try:
                job_info = requests.get(f"https://web.archive.org/save/status/{job_id}?_t=" + str(int(time.time()*100)) ).json()
                print(job_url, job_info['status'])
            except:
                print(url, 'No Result')
        job_query = []
        time.sleep(3*60)
