import requests as rq
import requests
import os, time, sys
from data import url_list
import functools
import logging

logger = logging.getLogger(__name__)

headers = {'Accept': 'application/json',
"Authorization": f"LOW {os.environ.get('MYACCESSKEY')}:{os.environ.get('MYSECRET')}", 
}
api_url = 'https://web.archive.org/save'

def retry(try_count=3, retry_interval=2, retry_interval_step=3):
    def _retry(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            _retry_interval = retry_interval

            for i in range(try_count):
                try:
                    _result = func(*args, **kwargs)
                    if i > 0:
                        logger.warning('(Try %d/%d) %r success', i + 1, try_count, func.__name__)

                    return _result
                except Exception as e:
                    if i < try_count - 1:
                        logger.warning('(Try %d/%d) %r got exception %r: %r', i + 1, try_count, func.__name__, type(e), e)

                        if _retry_interval < 0:
                            _retry_interval = 0

                        logger.warning('Wait %.2f s to retry', _retry_interval)
                        time.sleep(_retry_interval)
                        _retry_interval += retry_interval_step

                        logger.warning('(Try %d/%d) retrying ...', i + 2, try_count)
                    else:
                        raise e

        return wrapper

    return _retry

@retry(try_count=10, retry_interval=1, retry_interval_step=5)
def http_post_request(*args, **kwargs):
    # default kwargs
    kwargs_real = {
        'timeout': DEFAULT_TIMEOUT,
    }
    kwargs_real.update(kwargs)

    logger.debug('http_post_request: args=%r, kwargs=%r, cookies=%r', args, kwargs_real, sess.cookies)
    r = sess.post(*args, **kwargs_real)

    return r


DEFAULT_TIMEOUT = 32
sess = requests.Session()

job_query = []
for i, url in enumerate(url_list):
    
    data = {
        'url': url,
        'skip_first_archive': '1',#这个参数，能减少IA那边的数据库查询，加快存档速度
        'js_behavior_timeout': '30',#让js最多运行30s（默认是5s），似乎可以应对一些图片懒加载网速比较慢的网页
        'capture_outlinks': '1',
    }

    r = http_post_request(api_url, headers=headers, data=data)
    if r.status_code != 200:
        print(url, r.text[:256])
    else:
        try:
            job_id = r.json()['job_id']
            job_query += [(url, job_id)]
        except:
            print("Failed to get job_id", r.text[:256])
            continue
#         try:
#             job_query += [(url, job_id)]
# #             job_info = requests.get(f"https://web.archive.org/save/status/{job_id}?_t=" + str(int(time.time()*100)) ).json()
#             print(url, job_info['status'])
#         except:
#             print(url, 'No Result')

    if i!=0 and i%6 == 5 or i == len(url_list)-1:
        time.sleep(12*60)
        for job_url, job_id in job_query:
            try:
                job_info = rq.get(f"https://web.archive.org/save/status/{job_id}?_t=" + str(int(time.time()*100)) ).json()
                print(job_url, job_info['status'])
            except:
                print(job_url, 'No Result')
        job_query = []
#         time.sleep(5*60)
