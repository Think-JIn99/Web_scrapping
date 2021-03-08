from typing import Text
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
from dateutil.relativedelta import *
from dateutil.parser import *

class Site:
    def __init__(self,href):
        self.href = href
        self.headers = {"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.192 Safari/537.36"}

    def site_status(self):
        try:
            res = requests.get(self.href,headers = self.headers)
            res.raise_for_status()
            
        except requests.exceptions.RequestException as e:
            print(f"error page: {self.href}")
            print(f"error: {e}")
            return False
        
        return res
class Crawler:
    def __init__(self,res,href):
        self.site_soup = BeautifulSoup(res.text,"lxml")
        self.href = href

    def time_check(self,text):
        upload_time = re.search('\d{4}.\d\d.\d\d', text) #데이터 형식이 숫자 4 2 2 인 것 모두
        if upload_time:
            now = datetime.now()
            try:
                upload_time = parse(upload_time.group())
            except:
                return
            start_date = now - relativedelta(months =+ 1) #게시글의 최소 날짜
            end_date = now + relativedelta(months =+ 1) #게시글의 최대 날짜
            if  start_date < upload_time < end_date: #가끔 전화번호 잘못 긁어서 범위 설정함
                print(f"내용: {text} 시간:{upload_time} \nsite_href:{self.href}")
                return self.href


    def crawling_nontable(self):
        selcet_tag = []
        for tag in self.site_soup.find_all("a"):
            try:
                parent = tag.parent
                selcet_tag.append(parent)

            except AttributeError:
                print(f"No parent on {tag}\n")

        for tag in selcet_tag:
            text = tag.get_text()
            if "결혼" in text:
                return self.time_check(text)
            else:
                continue


    def crawling_table(self,tables):
        #결혼이란 키워드를 포함하고 최근 날짜에 올라온 게시글의 링크 모음
        for table in tables:
            rows = table.find_all("tr") #테이블의 가로를 스크래핑
            for r in rows:
                text = r.get_text()
                if "결혼" in text:
                    return self.time_check(text)
                else:
                    continue
        

    def get_content(self):
        tables = self.site_soup.find_all("table")
        content = ""
        if tables:
            print(f"사이트 제목: {self.site_soup.find('title').get_text()} \n 테이블 확인: {self.href} ")
            content = self.crawling_table(tables)
        else:
            print(f"사이트 제목: {self.site_soup.find('title').get_text()} \n 테이블 미확인: {self.href} ")
            content = self.crawling_nontable()

        return content
class Google_API:
    def __init__(self,query,page):
        self.query = query
        self.page = page
        self.items = self.get_search_data()

    def get_search_data(self):
        API_KEY = "AIzaSyCoOjeELwfwkaSy_rIqYMyJf8fIbPNai8I"
        SEARCH_ENGINE_ID = "93d897fa50c427465"
        start = (self.page - 1) * 10 + 1
        url =  f"https://www.googleapis.com/customsearch/v1?key={API_KEY}&cx={SEARCH_ENGINE_ID}&q={self.query}&start={start}"
        data = requests.get(url).json()
        # get the result items
        items = data.get("items")
        return items
        # iterate over 10 results found

class Naver_API:
    def __init__(self,query,page):
        self.query = query
        self.page = page
        self.items = self.get_search_data()

    def get_search_data(self):
        Client_ID = "AUocdELFYLK2MNZYTtpj"
        Client_Secret = "GiYlez4DCe"
        start = (self.page - 1) * 10 + 1
        url = f"https://openapi.naver.com/v1/search/webkr?query={query}&start={start}"
        header = {
        "X-Naver-Client-Id": Client_ID,
        "X-Naver-Client-Secret":Client_Secret
    }
        data = requests.get(url,headers = header).json()
        items = data.get("items")
        return items
    
def use_api(items,f):
    for item in items:
        href = item.get("link")
        site = Site(href).site_status()
        if site:
            c = Crawler(site,href)
            content = c.get_content()
            if content:
                f.write(content + "\n")

if __name__ == "__main__":
    query = ["경조사","회원 동정","회원 경조사"]
    page = range(1,20)
    for qi in range(len(query)):
        f = open(f"google_{query[qi]}.txt","w",encoding="UTF-8")
        nf = open(f"naver_{query[qi]}.txt","w",encoding="UTF-8")
        for i in page:
            # google = Google_API(query[qi],i).get_search_data()
            naver = Naver_API(query[qi],i).get_search_data()
            # use_api(google,f)
            use_api(naver,f)

    f.close()
    nf.close()

    
