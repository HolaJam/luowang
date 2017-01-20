import queue
import requests
import threading
from bs4 import BeautifulSoup

download_queue = queue.Queue()
download_lock = threading.Lock()

class spider4id(object):

    def __init__(self, page_id):
        self.headers = {
            'Host':
                'www.luoo.net',
            'Referer':
                'http://www.luoo.net/music/',
            'User-Agent':
                'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'

        }
        self.page_id = page_id
        self.url = 'http://www.luoo.net/music/%s' % page_id

    def spider(self):
        r = requests.get(url=self.url, headers=self.headers)
        res = (r.text.encode(r.encoding).decode('utf8'))
        soup = BeautifulSoup(res, 'html.parser')
        if soup.find('div', {'class': 'error-msg'}):
            return False
        else:
            pass

        music_player_node = soup.find(
            'div', {'id': 'luooPlayerPlaylist'}).find('ul').find_all('li')
        return len(music_player_node) + 1


def mp3url(page_id):
    # 落网匹配规则
    base_url = 'http://mp3-cdn.luoo.net/low'

    if page_id == 497:
        return '%s/luoo/s1/' % (base_url)

    elif page_id >= 498 and page_id <= 521:
        return '%s/luoo/S%s/' % (base_url, str(page_id - 496))

    elif page_id == 522:
        return '%s/luoo/s26/'

    elif page_id >= 523 and page_id <= 539:
        return '%s/anbai/radio%s/' % (base_url, str(page_id - 522))

    elif page_id >= 540 and page_id <= 543:
        return '%s/china/radio%s/' % (base_url, str(page_id - 539))

    elif page_id == 545:
        return '%s/china/radio5/' % (base_url)

    elif page_id >= 546 and page_id <= 557:
        return '%s/world/radio%s/' % (base_url, str(page_id - 545))

    elif page_id == 558 or page_id == 559:
        return '%s/electric/radio%s/' % (base_url, str(page_id - 557))

    elif page_id == 560 or page_id == 561:
        return '%s/classical/radio%s/' % (base_url, str(page_id - 559))

    elif page_id >= 562 and page_id <= 565:
        return '%s/jazz/radio%s/' % (base_url, str(page_id - 561))

    elif page_id == 569:
        return '%s/electric/radio3/' % (base_url)

    elif page_id == 573:
        return '%s/luoo/radio499/' % (base_url)

    elif page_id == 576:
        return '%s/jazz/radio5/' % (base_url)

    elif page_id == 581:
        return '%s/luoo/radio500/' % (base_url)

    elif page_id == 582:
        return '%s/luoo/radio581/' % (base_url)

    elif page_id == 583:
        return '%s/anbai/radio18/' % (base_url)

    elif page_id == 594:
        return '%s/anbai/radio19/' % (base_url)

    else:
        return '%s/luoo/radio%s/' % (base_url, page_id)


class download_producer(threading.Thread):
    '''
    下载的生产者，根据匹配规则和统计共有多少歌曲生成队列
    '''
    def __init__(self, page_id):
        threading.Thread.__init__(self)
        threading.Thread.name = 'download_producer'
        self.page_id = page_id

    def run(self):
        download_lock.acquire()
        tmp = spider4id(page_id=self.page_id)
        song_list = tmp.spider()

        if song_list:
            for i in range(1, song_list):
                if len(str(i)) == 1:
                    i = '0%s' % i
                base_url = mp3url(page_id=self.page_id)
                download_url = '%s%s.mp3' % (base_url, i)
                download_queue.put(download_url)


class download_consumer(threading.Thread):
    '''
    下载的消费者，从队列中取出相应的url下载
    '''
    def __init__(self):
        threading.Thread.__init__(self)
        threading.Thread.name = 'download_consumer'

    def run(self):
        download_lock.release()
        while True:
            try:
                song_url = download_queue.get()
                print(song_url)
                r = requests.get(url=song_url, stream=True)
                print(r.status_code)
                if r.status_code != 200:
                    with open('error.txt', 'w') as error:
                        error.write('download_file %s' % song_url + '\n')
                    error.close()
                    continue
                with open(song_url.split('/')[-1],'wb') as song:
                    song.write(r.content)

            except Exception as e:
                break


def main(page_id):

    test = download_producer(page_id=page_id)
    test.start()
    test_ = download_consumer()
    test_.start()

if __name__ == '__main__':
    main(page_id=886)