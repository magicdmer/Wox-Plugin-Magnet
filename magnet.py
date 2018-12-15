import requests
from lxml import html
import clipboard
import copy

from wox import Wox

import os
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    filename=os.path.join(os.path.abspath(
        os.path.dirname(__file__)), 'CQHanlder.log'),
    filemode='w+'
)

result_template = {
    'Title': '{}',
    'SubTitle': 'Press enter copy magnet url',
    'IcoPath': 'img/app.png',
    'JsonRPCAction': {
        'method': 'copyToClipboard',
        'parameters': ['{}'],
    }
}

class Main(Wox):

    def query(self, param):
        results = []
        q = param.strip()
        if not q:
            results.append({
            "Title": "磁链搜索",
            "SubTitle": "Search on feikebt",
            "IcoPath":"img/app.png",
            "ContextData": "ctxData"
            })
            return results
        
        searchTUrl = "http://feikebt.cc/s/@key/1/0/0.html"
        searchUrl = searchTUrl.replace('@key', q)
        
        response = self.search(searchUrl)
        if not response:
            results.append({
            "Title": "磁链搜索",
            "SubTitle": "have no results",
            "IcoPath":"img/app.png",
            "ContextData": "ctxData"
            })
            return results
            
        return response
        

    def copyToClipboard(self, value):
        clipboard.copy(value)

    @staticmethod
    def search(searchUrl):
        s = requests.session()
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko'}
        res = s.get(searchUrl, headers=headers)
        if res.ok:
            results = []
            tree = html.fromstring(res.content.decode('utf-8'))
            resultList = tree.xpath("//div[@class='ffbox']")
            if len(resultList) == 0:
                return None
                
            for item in resultList:
                result = copy.deepcopy(result_template)
                videoName = item.cssselect("h3 a")
                if not videoName:
                    continue
                videoName = videoName[0].text_content()
                result['Title'] = result['Title'].format('{}'.format(videoName))
                
                magnetUrl = item.cssselect("div.categorybar a")
                if not magnetUrl:
                    continue
                magnetUrl = magnetUrl[0].get('href')
                magnetUrl = magnetUrl[0:magnetUrl.index('&dn')]
                result['JsonRPCAction']['parameters'][0] = result['JsonRPCAction']['parameters'][0].format(magnetUrl)
                
                results.append(result)
                result = None
            return results
        else:
            logging.info('connect url failed')
            return None

    def __get_proxies(self):
        proxies = {}
        if self.proxy and self.proxy.get("enabled") and self.proxy.get("server"):
            proxies["http"] = "http://{}:{}".format(self.proxy.get("server"), self.proxy.get("port"))
            proxies["https"] = "http://{}:{}".format(self.proxy.get("server"), self.proxy.get("port"))
        return proxies


if __name__ == '__main__':
    Main()
