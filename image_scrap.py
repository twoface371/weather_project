import os
import csv
import time
import random
import urllib.request
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def web_scraping_final():
    # 환경 설정 (폴더 생성, 파일 열기, 차단 방지)
    
    # 이미지 저장 폴더
    img_folder = 'musinsa_images'
    if not os.path.exists(img_folder):
        os.makedirs(img_folder)

    # 403 Forbidden 차단 방지용 헤더 설정
    opener = urllib.request.build_opener()
    opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')]
    urllib.request.install_opener(opener)

    # CSV 파일 준비 
    f = open('train_data.csv', 'w', newline='', encoding='utf-8-sig')
    writer = csv.writer(f)
    writer.writerow(['file_name', 'style_tags'])

    # 크롬 드라이버 설정
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless") # 동작 확인 후, 창 없이 하고 싶으면 주석 뺴셈
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    collected_links = set() # 링크 중복 방지용

    try:
        #목록 페이지에서 게시물 링크 수집
        print("게시물 링크 수집 시작")
        driver.get('https://www.musinsa.com/snap/main/recommend?gf=A')
        driver.implicitly_wait(10)
        time.sleep(3) # 초기 로딩 대기

        # 스크롤 횟수
        SCROLL_COUNT = 5 
        
        for i in range(SCROLL_COUNT):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2) # 스크롤 후 로딩 대기
            
            # '/snap/'이 들어간 링크(a 태그)만 찾기
            links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/snap/']")
            for link in links:
                url = link.get_attribute('href')
                if url:
                    collected_links.add(url)
        
        print(f"{len(collected_links)}개의 게시물 수집 시작")

        # 각 링크로 들어가서 '이미지','태그' 수집하기
        count = 0
        for url in collected_links:
            try:
                driver.get(url)
                # 차단 방지를 위해 텀 설정함
                time.sleep(random.uniform(1.5, 2.5)) 

                #메인 이미지 찾기 (크기 필터링)
                real_img_url = ""

                #모든 이미지 태그 검사
                images = driver.find_elements(By.TAG_NAME, "img")
                
                for img in images:
                    src = img.get_attribute('src')
                    if not src: continue
                    
                    # '가짜 이미지' 제외 (프로필, 아이콘, 로고 등)
                    # 주소에 이런 단어가 들어가면 메인 사진이 아님
                    if any(bad_word in src for bad_word in ['_simbols', 'basic.png', 'profile', 'icon', 'logo']):
                        continue
                    
                    # 크기 필터링 
                    # 너비가 300px 이상인 이미지만 진짜 스냅 사진으로 인정
                    if img.size['width'] > 300:
                        real_img_url = src
                        break # 큰 이미지를 찾았으면 종료 후 태그 찾기로 넘어감
                
                if not real_img_url:
                    continue

                # 태그 찾기 (학습 시키는 데 활용할 거임)
                # 본문 전체 텍스트를 가져와서 #으로 시작하는 단어만 추출
                body_text = driver.find_element(By.TAG_NAME, "body").text.replace('\n', ' ')
                tags = [word for word in body_text.split() if word.startswith('#')]
                
                # 태그 정제 (중복 제거, 1글자짜리 제외, 20글자 넘는 이상한 것 제외)
                clean_tags = list(set([t for t in tags if 1 < len(t) < 20]))

                # 저장

                if clean_tags: # 태그가 있는 경우에만 저장
                    file_name = f"snap_{count:05d}.jpg"
                    file_path = os.path.join(img_folder, file_name)

                    # 이미지 다운로드
                    urllib.request.urlretrieve(real_img_url, file_path)
                    
                    # CSV에 기록
                    writer.writerow([file_name, ", ".join(clean_tags)])
                    
                    count += 1
                    print(f"[{count}번째] 저장완료 | 태그: {clean_tags}")
                else:
                    pass
                   

            except Exception as e:
                print(f"{e}")
                continue

    except Exception as e:
        print(f"전체 프로세스 에러: {e}")

    finally:
        f.close()
        driver.quit()
        print("\n모든 작업 종료")

# 함수 실행
if __name__ == "__main__":
    web_scraping_final()
