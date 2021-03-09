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
        upload_time = re.search('\d{4}.\d\d.\d\d',text) #날짜 형식의 데이터 추출

        if not upload_time:
            upload_time = re.search('\d\d.\d\d',text) #날짜 형식의 데이터 추출

        if upload_time:
            now = datetime.now()

            try:
                upload_time = parse(upload_time.group())
            except:
                return
            start_date = now - relativedelta(months =+ 1) #게시글의 최소 날짜
            end_date = now + relativedelta(months =+ 1) #게시글의 최대 날짜
            if  start_date < upload_time < end_date: #가끔 전화번호 잘못 긁어서 범위 설정함
                print(f"결혼 정보 사용가능 사이트 : {self.href}")
                return True #사용 가능한 정보면 파일에 입력
        return

    def crawling_table(self):
        tables = self.site_soup.find_all("table")
        is_useful_href = False
        #결혼이란 키워드를 포함하고 최근 날짜에 올라온 게시글의 링크 모음
        for table in tables:
            rows = table.find_all("tr") #테이블의 가로를 스크래핑
            for r in rows:
                text = r.get_text()
                if re.search("결혼|자혼|혼인",text):
                    print(self.href)
                    is_useful_href = self.time_check(text)
                    if is_useful_href:
                        return self.href
                    # 시간 조건을 확인하고 만족하면 이 사이트에는 적어도 1개의 유용한 결혼정보가 존재하므로 url을 전달

                else:
                    continue
        return 
        
    def print_title(self):
        title = self.site_soup.find('title')
        if title:
            title = title.get_text()
        else:
            title = "None"
        print(f"사이트 제목: {title} \n 사이트 주소: {self.href}")
        return 
class Google_API:
    def __init__(self,query,page):
        self.query = query
        self.page = page
        self.items = self.get_search_data()

    def get_search_data(self):
        API_KEY = "AIzaSyAQuWE-QFadlKJ3BLSM_LeEdqxFXwE7Tn4"
        SEARCH_ENGINE_ID = "e15ba323e66efc543"
        start = (self.page - 1) * 10 + 1
        url =  f"https://www.googleapis.com/customsearch/v1?key={API_KEY}&cx={SEARCH_ENGINE_ID}&q={self.query}&start={start}"
        data = requests.get(url).json()
        hrefs = []
        for item in data.get("items"):
            hrefs.append(item.get("link"))

        return hrefs
        # get the result items    
        # iterate over 10 results found
        
class Naver:
    def __init__(self,query,page):
        self.query = query
        self.page = page
  
    def get_search_data(self): 
        url = f"https://search.naver.com/search.naver?display=15&f=&filetype=0&page={self.page + 1}&query={self.query}&research_url=&sm=tab_pge&start={self.page}&where=web"
        site = Site(url).site_status()
        if site:
            soup = BeautifulSoup(site.text,"lxml")
            links = soup.find_all("a",attrs={"class":"link_tit"})
        
        hrefs = []
        for link in links:  
            hrefs.append(link["href"])

        return hrefs
        
if __name__ == "__main__":

    def use_crawler(hrefs):
        useful_hrefs = []
        for href in hrefs:
            site = Site(href).site_status()
            if site:
                c = Crawler(site,href)
                c.print_title() #사이트 제목 출력
                content = c.crawling_table() #테이블에 있는 데이터 긁어오기
                if content:
                    useful_hrefs.append(content)
                  
        return useful_hrefs

    query = ["경조사 알림,경조사,회원 경조사"]
    page =  int(input("탐색 페이지 수:  "))
    start =  int(input("탐색 페이지 수:  "))
    f = open(f"result.txt","w",encoding="UTF-8")

    for qi in range(len(query)):
        for i in range(start,page):
            naver = Naver(query[qi],i).get_search_data()
            google = Google_API(query[qi],i).get_search_data()
            res = use_crawler(naver)
            res.extend(use_crawler(google))
            if res:
                for r in res:
                    f.write(r + "\n")
    f.close()

    
