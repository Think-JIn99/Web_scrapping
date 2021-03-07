import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
from dateutil.relativedelta import *
from dateutil.parser import *
class Parsing:
    def __init__(self,href):
        self.href = href
        self.headers = {"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.192 Safari/537.36"}

    def site_status(self,res):
        can_connect = True
        try:
            res.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print(f"error page: {self.href}")
            print(f"error: {e}")
            can_connect = False
        
        return can_connect
    
    def get_table(self):
        res = requests.get(self.href,headers = self.headers)
        if self.site_status(res):
            soup = BeautifulSoup(res.text,"lxml")
            tables = soup.find_all("table")

            if tables:
                #tbody태그도 찾아야 함
                title = soup.find('title').get_text()
                print(f"테이블 확인 페이지: {title} \t주소:{self.href}")
                self.extract_raw(tables)

            else:
                print(f"테이블 미확인 페이지: {self.href}")
        else:
            return


    def extract_raw(self,tables):
        articles = []
        for table in tables:
            tr = table.find_all("tr")
            for t in tr:
                text = t.get_text()
                if "결혼" in text:
                    upload_time = re.search('(\d{4}).(\d\d).(\d\d)',text)
                    if upload_time:
                        now = datetime.now()
                        upload_time = parse(upload_time.group())
                        start_date = now - relativedelta(months =+ 1)
                        end_date = now + relativedelta(months =+ 1)
                        if  start_date < upload_time < end_date:
                            article_href = t.find("a")['href'] 
                            articles.append(article_href)
                            print(f"내용: {text} 시간:{upload_time} href:{article_href}") 
                    else:
                        continue
      

class Google_Api:
    def __init__(self,query,page):
        self.query = query
        self.page = page
        self.items = self.get_search_data()

    def get_search_data(self):
        API_KEY = "AIzaSyCA9MhMaovo9IE6C1G2jnEHnp1P-oxNvkk"
        SEARCH_ENGINE_ID = "ec418eeb750683779"
        start = (self.page - 1) * 10 + 1
        url =  f"https://www.googleapis.com/customsearch/v1?key={API_KEY}&cx={SEARCH_ENGINE_ID}&q={self.query}&start={start}"
        data = requests.get(url).json()
        # get the result items
        items = data.get("items")
        return items
        # iterate over 10 results found
    def parse_data(self):
        parse_hrefs = []
        for item in self.items:
            p = Parsing(item.get("link"))
            p.get_table()
            parse_hrefs.append(p)
         
       
    def print_data(self):
        for i, search_item in enumerate(self.items, start=1):
            # get the page title
            title = search_item.get("title")
            # extract the page url
            link = search_item.get("link")
            # print the results
            print("="*10, f"Result #{i+page-1}", "="*10)
            print("Title:", title)
            print("URL:", link, "\n")

if __name__ == "__main__":
    query = "회원 경조사"
    page = 1
    google = Google_Api(query,page)
    google.parse_data()
    print("*"  * 20)
