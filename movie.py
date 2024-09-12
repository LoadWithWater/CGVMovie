import tkinter as tk
from tkinter import ttk
import requests
from bs4 import BeautifulSoup

# 웹 크롤링 함수 정의
def fetch_movie_data():
    url = "http://www.cgv.co.kr/movies/?lt=1&ft=0"
    response = requests.get(url)
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')
    movies = soup.select('.sect-movie-chart ol li')

    movie_data = []
    for movie in movies[:20]:  # 상위 20개 영화만 처리
        try:
            title = movie.find('strong', class_='title').text.strip()
        except AttributeError:
            title = "기본값"
        try:
            percent = float(movie.find('strong', class_='percent').text.strip().replace('예매율', '').replace('%',''))
        except AttributeError:
            percent = 0.0
        try:
            release_date = movie.find('span', class_='txt-info').find('strong').text.strip()
        except AttributeError:
            release_date = "기본값"
        movie_data.append({'title': title, 'percent': percent, 'release_date': release_date})
    
    # 예매율을 기준으로 데이터 정렬
    sorted_movies = sorted(movie_data, key=lambda x: x['percent'], reverse=True)
    return sorted_movies

# Tkinter GUI 초기화
root = tk.Tk()
root.title("CGV 영화 예매율 순위")

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
