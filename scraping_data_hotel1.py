from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time
import io
from csv import writer
import pandas as pd
import csv
import mysql.connector

db = mysql.connector.connect(
  host="localhost",
  user="root",
  passwd="",
  database='data_hotel'
)

cursor = db.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS hotel (hotel_id INT PRIMARY KEY, nama_hotel VARCHAR(255), link_halaman VARCHAR(255), market1 VARCHAR(255), harga1 VARCHAR(255), lokasi VARCHAR(255), fasilitas VARCHAR(255), fitur VARCHAR(255), jenis_kamar VARCHAR(255), hotel_rating FLOAT)")
cursor.execute("CREATE TABLE IF NOT EXISTS user (user_id INT AUTO_INCREMENT PRIMARY KEY, nama_user VARCHAR(255), link_halaman VARCHAR(255))")
cursor.execute("CREATE TABLE IF NOT EXISTS review (review_id INT PRIMARY KEY, hotel_id INT, user_id INT, judul VARCHAR(255), isi VARCHAR(255), tanggal_menginap VARCHAR(255), jenis_trip VARCHAR(255), review_rating FLOAT, FOREIGN KEY (hotel_id) REFERENCES hotel(hotel_id), FOREIGN KEY (user_id) REFERENCES user(user_id))")

PATH = "chromedriver_win32\chromedriver.exe"
driver = webdriver.Chrome(PATH)
action = ActionChains(driver)

driver.maximize_window()

driver.get("https://www.tripadvisor.co.id/Hotels-g294230-Yogyakarta_Region_Java-Hotels.html")
driver.implicitly_wait(10)
#link halaman terakhir
#https://www.tripadvisor.co.id/Hotels-g294230-oa2610-Yogyakarta_Region_Java-Hotels.html

page=1
data_hotel=[]
data_user=[]
data_review=[]
#data_duplikat=[]

cursor.execute("SELECT review_id, judul FROM review")
sql_review = cursor.fetchall()
cursor.execute("SELECT hotel_id, nama_hotel FROM hotel")
sql_hotel = cursor.fetchall()
cursor.execute("SELECT user_id, nama_user FROM user")
sql_user = cursor.fetchall()

try:
    user_id = sql_user[len(sql_user)-1][0]+1
    print(user_id)
except:
    user_id=1

while True:
    count_hotel=0
    review_page=1
    count_sponsor=0

    time.sleep(10)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    wait = WebDriverWait(driver, 25)
    wait.until(EC.element_to_be_clickable((By.XPATH, '//a[@class="nav next ui_button primary"]')))
    items = soup.findAll('div', 'prw_rup prw_meta_hsx_responsive_listing ui_section listItem')

    for it in items:
        check = True
        check_hotel = 0
        try: 
            refresh_harga = driver.find_elements_by_xpath('//div[@class="refreshPricesButton change_dates_button ui_button primary"]')
            time.sleep(3)
            action.move_to_element(refresh_harga[0])
            time.sleep(3)
            refresh_harga[0].click()
            time.sleep(13)
            soup = BeautifulSoup(driver.page_source, 'html.parser')
        except:
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            pass
        hotel = driver.find_elements_by_xpath('//div[@class="prw_rup prw_meta_hsx_listing_name listing-title"]//a')
        try: hotel_id = hotel[count_hotel].get_attribute("id").replace('property_','')
        except: hotel_id = ""
        try: nama_hotel = hotel[count_hotel].text
        except: nama_hotel = ""
        try: link_hotel = hotel[count_hotel].get_attribute("href")
        except: link_hotel = ""
        try: 
            market = it.find("div","unavailableText").text
            harga = ""
        except:
            try: 
                market = it.find('span', 'provider_text').text
            except: 
                market = ""
            try: 
                harga = driver.find_elements_by_xpath('//div[@class="price-wrap "]/div[@class="price __resizeWatch"]')
                harga = str(harga[count_hotel].text)
            except: 
                harga = ""

        while True:
            try: 
                #print(check_hotel)
                if nama_hotel in data_hotel[check_hotel]:
                    print("Data Hotel Duplikat_1")
                    print(hotel_id, nama_hotel)
                    check = False
                    break
                elif nama_hotel in sql_hotel[check_hotel]: 
                    print("Data Hotel Duplikat_2")
                    print(hotel_id, nama_hotel)
                    check = False
                    break
                else:
                    check_hotel+=1
            except (AttributeError, IndexError): 
                try:
                    if nama_hotel in sql_hotel[check_hotel]:
                        print("Data Hotel Duplikat_2")
                        print(hotel_id, nama_hotel)
                        check = False
                        break
                    else:
                        check_hotel+=1
                except (AttributeError, IndexError):
                    break
        if check:
            try:
                print(hotel_id, nama_hotel, link_hotel, market, harga)
                time.sleep(3)
                action.move_to_element(hotel[count_hotel])
                time.sleep(3)
                hotel[count_hotel].click()
                time.sleep(3)
                driver.switch_to.window(driver.window_handles[1])
            except IndexError:
                print("Gagal Membuka Page Hotel")
            


            while True:
                time.sleep(12)
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                #Ambil Data di Halaman Hotel
                try: 
                    review_lengkap = driver.find_elements_by_xpath('//div[@class="XUVJZtom"]')
                    action.move_to_element(review_lengkap[0])
                    time.sleep(2)
                    review_lengkap[0].click()
                    soup = BeautifulSoup(driver.page_source, 'html.parser')
                except:
                    pass
                lokasi = soup.find('span', '_3ErVArsu jke2_wbp').text
                hotel_rating = soup.find('span', '_3cjYfwwQ').text.replace('0,5', '0.5').replace('1,0', '1.0').replace('1,5', '1.5').replace('2,0', '2.0').replace('2,5', '2.5').replace('3,0', '3.0').replace('3,5', '3.5').replace('4,0', '4.0').replace('4,5', '4.5').replace('5,0', '5.0')
                hotel_rating = float(hotel_rating)
                fasilitas = driver.find_elements_by_xpath('//div[@class="ssr-init-26f"]/div[2]')
                fasilitas = fasilitas[1].text.replace('\n', ',')
                fitur = driver.find_elements_by_xpath('//div[@class="ssr-init-26f"]/div[5]')
                fitur = fitur[0].text.replace('\n', ',')
                jenis_kamar = driver.find_elements_by_xpath('//div[@class="ssr-init-26f"]/div[8]')
                jenis_kamar = jenis_kamar[0].text.replace('\n', ',')
                #bahasa = driver.find_elements_by_xpath('//div[@class="ui_column is-6 "]/div[@class="ssr-init-26f"]/div[@class="_2dtF3ueh"]')
                review = soup.findAll('div', '_2wrUUKlw _3hFEdNs8')
                for it in review:
                    check_user=0
                    check_review=0
                    review_id = it.find('div', 'oETBfkHU')
                    review_id = review_id['data-reviewid']
                    nama_user = it.find('a', 'ui_header_link _1r_My98y').text
                    link_halaman = it.find('a', 'ui_header_link _1r_My98y')['href']
                    link_halaman = "https://www.tripadvisor.co.id" + link_halaman
                    judul = it.find('div', 'glasR4aX').text
                    isi = str(it.find('q', 'IRsGHoPm').text)
                    try: 
                        jenis_trip = it.find('span', '_2bVY3aT5').text.replace('Jenis Trip: ','')
                    except: 
                        jenis_trip = ""
                    try : tanggal_menginap = it.find('span', '_34Xs-BQm').text.replace('Tanggal menginap: ', '')
                    except : tanggal_menginap = ''
                    review_rating = str(it.find('div', 'nf9vGX55')).replace('<div class="nf9vGX55" data-test-target="review-rating"><span class="ui_bubble_rating bubble_50"></span></div>', '5').replace('<div class="nf9vGX55" data-test-target="review-rating"><span class="ui_bubble_rating bubble_40"></span></div>', '4').replace('<div class="nf9vGX55" data-test-target="review-rating"><span class="ui_bubble_rating bubble_30"></span></div>', '3').replace('<div class="nf9vGX55" data-test-target="review-rating"><span class="ui_bubble_rating bubble_20"></span></div>', '2').replace('<div class="nf9vGX55" data-test-target="review-rating"><span class="ui_bubble_rating bubble_10"></span></div>', '1')
                    review_rating=int(review_rating)
                    #print(len(data_review))

                    check = True
                    while True:
                        try:
                            if review_id in sql_review[check_review]:
                                check = False
                                print("Data Review Duplikat_2")
                                print(review_id, judul)
                                break
                            else:
                                check_review+=1
                            #print("2Check review"+str(check_review))
                        except (AttributeError, IndexError):
                            break
                    if check:
                        data_review.append([int(review_id), int(hotel_id), user_id, judul, isi, tanggal_menginap, jenis_trip, review_rating])

                    check = True
                    while True:
                        try: 
                            if user_id in data_user[check_user] or nama_user in data_user[check_user]:
                                check = False
                                print("Data User Duplikat_1")
                                print(user_id, nama_user)
                                break
                            elif user_id in sql_user[check_user] or nama_user in sql_user[check_user]:
                                check = False
                                print("Data User Duplikat_2")
                                print(user_id, nama_user)
                                break
                            else:
                                check_user+=1
                            #print("1Check User"+str(check_user))
                        except (AttributeError, IndexError):
                            try:
                                if user_id in sql_user[check_user] or nama_user in sql_user[check_user]:
                                    check = False
                                    print("Data User Duplikat_2")
                                    print(user_id, nama_user)
                                    break
                                else:
                                    check_user+=1
                                #print("2Check User"+str(check_user))
                            except (AttributeError, IndexError):
                                break
                    if check:
                        data_user.append([user_id, nama_user, link_halaman])
                        user_id+=1
                
                try : 
                    halaman_terakhir = soup.find("span", "ui_button nav next primary disabled").text
                    print("Halaman Terakhir")
                    break
                except : 
                    print("Scraping Selesai, Halaman Review " + str(review_page))

                change_review_page = driver.find_elements_by_xpath('//a[@class="ui_button nav next primary "]')
                action.move_to_element(change_review_page[0])
                change_review_page[0].click()
                #Batasan page review, biar ngga kebanyakan
                """ if review_page==2:
                    break """
                review_page+=1
            try: 
                print(count_hotel)
                data_hotel.append([int(hotel_id), nama_hotel, link_hotel, market, harga, lokasi, fasilitas, fitur, jenis_kamar, hotel_rating])
            except (AttributeError, IndexError): 
                print("Error")

            check_review1=0
            check_review2=0
            while True:
                if check_review1==len(data_review):
                    break
                elif check_review1==check_review2:
                    check_review2+=1
                else:
                    try:
                        if data_review[check_review1][0] in data_review[check_review2]:
                            print("Data Review Duplikat_2")
                            print(data_review[check_review1][0])
                            data_review.pop(check_review1)
                        else:
                            pass
                        check_review2+=1
                    except:
                        check_review1+=1
                        check_review2=0
                        
            cursor.executemany("INSERT INTO hotel (hotel_id, nama_hotel, link_halaman, market1, harga1, lokasi, fasilitas, fitur, jenis_kamar, hotel_rating) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",data_hotel)
            cursor.executemany("INSERT INTO user (user_id, nama_user, link_halaman) VALUES (%s, %s, %s)",data_user)
            cursor.executemany("INSERT INTO review (review_id, hotel_id, user_id, judul, isi, tanggal_menginap, jenis_trip, review_rating) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",data_review)

            db.commit()

            data_review = []
            data_hotel = []
            data_user = []

            #driver.switch_to.window(driver.window_handles[1])
            time.sleep(2)
            driver.close()
            time.sleep(2)
            driver.switch_to.window(driver.window_handles[0])
        #Banyaknya hotel yang di scraping
        if count_hotel==14:
            break
        count_hotel+=1
    #Banyaknya page hotel yang di scraping
    if page==1:
        break
    page+=1
    next_page = driver.find_elements_by_xpath('//a[@class="nav next ui_button primary"]')
    time.sleep(3)
    action.move_to_element(next_page[0])
    time.sleep(3)
    next_page[0].click()
    time.sleep(3)
    driver.switch_to.window(driver.window_handles[0])
    print("Next Page")
        
print(data_hotel)
print(data_review)
print(data_user)
#print(data_duplikat)

""" cursor.execute("CREATE DATABASE data_hotel")

cursor.execute("DROP TABLE IF EXISTS review")
cursor.execute("DROP TABLE IF EXISTS user")
cursor.execute("DROP TABLE IF EXISTS hotel") """

cursor.execute("SHOW TABLES")
for x in cursor:
  print(x)

""" check_review1=0
check_review2=0
while True:
    if check_review1==len(data_review):
        break
    elif check_review1==check_review2:
        check_review2+=1
    else:
        try:
            if data_review[check_review1][0] in data_review[check_review2]:
                print("Data Review Duplikat_2")
                print(data_review[check_review1][0])
                data_review.pop(check_review1)
            else:
                pass
            check_review2+=1
        except:
            check_review1+=1
            check_review2=0
            
cursor.executemany("INSERT INTO hotel (hotel_id, nama_hotel, link_halaman, market1, harga1, lokasi, fasilitas, fitur, jenis_kamar, hotel_rating) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",data_hotel)
cursor.executemany("INSERT INTO user (user_id, nama_user, link_halaman) VALUES (%s, %s, %s)",data_user)
cursor.executemany("INSERT INTO review (review_id, hotel_id, user_id, judul, isi, tanggal_menginap, jenis_trip, review_rating) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",data_review)

db.commit() """