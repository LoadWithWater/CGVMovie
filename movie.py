import time
import tkinter as tk
from tkinter import ttk
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import re  # 정규식을 사용해 개봉일 포맷을 맞춤

# Selenium으로 페이지 로드 및 '더보기' 버튼 클릭
def fetch_movie_data():
    # ChromeOptions 설정 (헤드리스 모드)
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # 헤드리스 모드 활성화
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Chrome 웹드라이버 설정
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    # CGV 영화 페이지 열기
    url = "http://www.cgv.co.kr/movies/?lt=1&ft=0"
    driver.get(url)
    
    # '더 보기' 버튼이 로드될 때까지 기다린 후 클릭
    time.sleep(3)  # 페이지가 로드될 시간을 확보
    try:
        more_button = driver.find_element(By.CLASS_NAME, 'btn-more-fontbold')
        more_button.click()
        time.sleep(3)  # 데이터 로드 시간 확보
    except Exception as e:
        print(f"'더 보기' 버튼을 클릭할 수 없습니다: {e}")
    
    # 페이지 소스 가져오기
    html = driver.page_source
    driver.quit()

    # BeautifulSoup로 크롤링
    soup = BeautifulSoup(html, 'html.parser')
    movies = soup.select('.sect-movie-chart ol li')

    movie_data = []
    for idx, movie in enumerate(movies[:20]):  # 상위 20개 영화만 처리
        try:
            title = movie.find('strong', class_='title').text.strip()
        except AttributeError:
            title = "기본값"
        
        try:
            percent = float(movie.find('strong', class_='percent').text.strip().replace('예매율', '').replace('%', ''))
        except (AttributeError, ValueError):
            percent = 0.0
        
        try:
            release_date = movie.find('span', class_='txt-info').find('strong').text.strip()
            # 정규식을 사용해 '년, 월, 일'만 추출
            release_date = re.search(r'\d{4}\.\d{2}\.\d{2}', release_date).group(0)
        except (AttributeError, ValueError):
            release_date = "기본값"
        
        movie_data.append({'title': title, 'percent': percent, 'release_date': release_date})

    # 예매율을 기준으로 데이터 정렬
    sorted_movies = sorted(movie_data, key=lambda x: x['percent'], reverse=True)
    return sorted_movies

# Tkinter GUI 초기화
root = tk.Tk()
root.title("CGV 영화 예매율 순위")

# 창 크기 설정
root.geometry('600x450')  # 창 크기를 600x450으로 설정
root.resizable(True, True)  # 사용자가 창 크기 조정을 할 수 있도록 설정

# 표(treeview) 생성
columns = ('rank', 'title', 'percent', 'release_date')
treeview = ttk.Treeview(root, columns=columns, show='headings')
treeview.pack(expand=True, fill='both')

# 컬럼 설정
treeview.heading('rank', text='순위')
treeview.heading('title', text='제목')
treeview.heading('percent', text='예매율(%)')
treeview.heading('release_date', text='개봉일')

# 컬럼 너비 설정
treeview.column('rank', width=50, anchor='center')
treeview.column('title', width=200, anchor='center')
treeview.column('percent', width=100, anchor='center')
treeview.column('release_date', width=100, anchor='center')

# 웹 크롤링을 실행하고 결과를 표에 표시
movie_data = fetch_movie_data()
for idx, movie in enumerate(movie_data, start=1):
    treeview.insert('', tk.END, values=(idx, movie['title'], movie['percent'], movie['release_date']))

# GUI 실행
root.mainloop()
