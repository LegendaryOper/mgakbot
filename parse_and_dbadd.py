import requests
from bs4 import BeautifulSoup
from urllib import parse
from time import sleep
from datetime import datetime
import pymysql
from config import *





NEW_RASPES=False


class Parser:

    def __init__(self,HEADERS,GROUP_LIST,PARSE_URL,connection):
        self.HEADERS = HEADERS
        self.GROUP_LIST = GROUP_LIST
        self.PARSE_URL = PARSE_URL
        self.connection = connection
        self.cursor = self.connection.cursor()

    def parse_and_check(self):
        cursor = self.connection.cursor()
        connection = self.connection
        response = requests.get(self.PARSE_URL, headers=self.HEADERS)
        soup = BeautifulSoup(response.text, 'lxml')
        quotes = soup.find_all('a', class_='sm1')
        if str(quotes[3])[21:-14] == 'assets/site/raspisanie/1.htm' and datetime.today().isoweekday() in [7,1]:
            url = 'https://mgak1.by/' + str(quotes[4])[21:-14]
        else:
            url = 'https://mgak1.by/' + str(quotes[3])[21:-14]
        url = parse.quote(f'{url}', safe='')
        url = 'https://www.w3.org/services/html2txt?url=' + url
        response = requests.get(url, headers=self.HEADERS)
        soup = BeautifulSoup(response.text, 'lxml')
        raspes = soup.text
        cursor.execute("SELECT curent FROM current_raspes")
        data = cursor.fetchall()
        if data[0]['curent']==raspes:
            cursor.close()
            return False
        else:
            cursor.execute('UPDATE current_raspes SET curent=%s where id=1;', [raspes])
            connection.commit()
            cursor.close()
            return raspes

    def find_quote_in_raspes(self,group,raspes):
        quote=raspes[raspes.find(group):raspes.find(group)+raspes[raspes.find(group):].find('─')][:-1]
        if quote=='':
            quote='На сегодняшний день расписание для вашей группы не найдено!(ВЫХОДНОЙ ИЛИ КАНИКУЛЫ!!!)....Ну или практика('
        else:
            quote = '   │'+quote
        return quote

    def update_db(self,group_list,raspes):
        connection = self.connection
        cursor = self.connection.cursor()
        if raspes==False:
            return False

        def check_group_number(group_number):
            cursor.execute("SELECT group_number FROM raspes WHERE group_number=%s", [group_number])
            data = cursor.fetchall()
            if len(data) == 0:
                return False
            else:
                return True

        for i in range(1,len(group_list)+1):
            if check_group_number(i):
                cursor.execute('UPDATE raspes SET raspisaniye = %s, group_name = %s WHERE group_number=%s', [self.find_quote_in_raspes(group_list[i-1],
                raspes),group_list[i-1], i])
                connection.commit()
            else:
                cursor.execute('INSERT INTO raspes (group_number,raspisaniye,group_name) VALUES (%s, %s, %s)', (i,
                self.find_quote_in_raspes(group_list[i-1],raspes),group_list[i-1]))
                connection.commit()
        cursor.close()




def parse_and_update_db(HEADERS,GROUP_LIST,PARSE_URL,connection):

    while True:

        try:
            connection = pymysql.connect(host=host,
                                         port=3306,
                                         user=user,
                                         password=password,
                                         database=db_name,
                                         cursorclass=pymysql.cursors.DictCursor
                                         )

            db_setting1 = 'SET net_read_timeout = 180000;'
            db_setting2 = 'SET net_write_timeout = 180000;'

            connection.cursor().execute(db_setting1)
            connection.cursor().execute(db_setting2)
            connection.cursor().close()
            global NEW_RASPES
            parser = Parser(HEADERS, GROUP_LIST, PARSE_URL,connection)
            parse = parser.parse_and_check()
            if parser.update_db(GROUP_LIST,parse)==False:
                NEW_RASPES=False
                sleep(50)
                continue
            parser.update_db(GROUP_LIST, parse)
            NEW_RASPES=True
            sleep(50)
        except Exception as ex:
            print('ошибка в парсинге')
            print(ex)
            sleep(50)
            continue



