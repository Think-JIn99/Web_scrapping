from os import PRIO_PGRP
import requests
import re
from bs4 import BeautifulSoup
from datetime import datetime
from dateutil.relativedelta import *
from dateutil.parser import *

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
            start_date = now - relativedelta(days =+ 5) #게시글의 최소 날짜
            end_date = now + relativedelta(months =+ 1) #게시글의 최대 날짜
            if  start_date < upload_time < end_date: #가끔 전화번호 잘못 긁어서 범위 설정함
                print(f"결혼 정보 사용가능 사이트 : {self.href}")
                return True #사용 가능한 정보면 파일에 입력
        return

    def crawling_table(self):
        tables = self.site_soup.select("table > tbody")
        is_useful_href = False
        #결혼이란 키워드를 포함하고 최근 날짜에 올라온 게시글의 링크 모음
        for table in tables:
            row = table.select_one("tr")
            while row:
                #테이블의 가로를 스크래핑
                row = row.find_next_sibling('tr')
                if row:
                    for td in row.find_all("td",recursive = False):
                        text = td.get_text().strip()
                        if not re.search("[^0-9]",text):
                            continue
                        print(text)
                        if re.search("결혼|자혼|혼인",text):
                            is_useful_href = self.time_check(text)
                            if is_useful_href:
                                return self.href
                        # 시간 조건을 확인하고 만족하면 이 사이트에는 적어도 1개의 유용한 결혼정보가 존재하므로 url을 전달

                        else:
                            continue
        return 

headers = {"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.192 Safari/537.36"}
# url = "http://sgno.or.kr/notice/event.htm"
url = ["http://cw.kugeu.org/notice/news_event.php",
"http://gpgeu.or.kr/?page_id=3311",
"http://www.gbnojo.or.kr/pages/sub/page.html?mc=0022",
"http://www.cabo.busan.kr/Board.asp?menucode=0402030000",
"http://www.penlu.or.kr/news/familyEvent.php",
"http://imsil.gnch.or.kr/bbs/board.php?bo_table=unit_uon_notify",
"http://www.gjhma.org/bbs/board.php?bo_table=affairs",
"http://www.jou.or.kr/jou/welfare/familyevent.do",
"http://www.phdsteel.com/bbs/board5_2",
"http://www.obnhic.co.kr/2012/bbs/board.php?bo_table=memkojo"]
for u in url:
    res = requests.get(u,headers = headers)
    c = Crawler(res,u)
    c.crawling_table()

   