import telebot
from threading import Thread
from time import sleep
import parse_and_dbadd as parse
import pymysql
from config import *

bot=telebot.TeleBot(token)

try:
    connection = pymysql.connect(host=host,
                                 port=3306,
                                 user=user,
                                 password=password,
                                 database=db_name,

                                 )
    print('succesful')

    try:
        with connection.cursor() as cursor1:

            create_table_users = 'CREATE TABLE users(user_id int,group_number int);'
            create_table_raspes = 'CREATE TABLE raspes(group_number int, raspisaniye varchar(500),group_name varchar(50));'
            create_table_current_raspes = 'CREATE TABLE current_raspes(id int, curent varchar(10000));'
            create_current_raspes_row = 'INSERT INTO current_raspes (id, curent) VALUES(1,"Привет");'
            # cursor1.execute('drop table current_raspes')
            # cursor1.execute(create_table_users)
            # print('users')
            # cursor1.execute(create_table_raspes)
            # print('raspes')
            # cursor1.execute(create_table_current_raspes)
            # print('current_rapses')
            # cursor1.execute(create_current_raspes_row)
            # print('row')

    except Exception as ex1:
        print(ex1)
        print('bebra')



except Exception as ex:
    print("Error")
    print(ex)
cursor1 = connection.cursor()




def check_userid_in_database(id):
    cursor1.execute("SELECT user_id FROM users WHERE user_id=%s", (id,))
    data = cursor1.fetchall()
    if len(data) == 0:
        return True
    else:
        return False


def check_group_id_in_database(id):
    cursor1.execute("SELECT group_number FROM users WHERE user_id =%s", (id,))
    data = cursor1.fetchall()
    if len(data) == 0:
        return False
    else:
        return True


def message_from_db(id):

    def select_group_id(id):
        cursor1.execute("SELECT group_number FROM users WHERE user_id =%s", (id,))
        data = cursor1.fetchall()
        return data[0]['group_number']

    cursor1.execute("SELECT raspisaniye FROM raspes WHERE group_number =%s", (select_group_id(id),))
    data = cursor1.fetchall()[0]['raspisaniye']
    return data


def db_table_val(user_id: int, group_number: int):
    if check_userid_in_database(user_id):
        cursor1.execute('INSERT INTO users (user_id, group_number) VALUES (%s, %s)', (user_id, group_number))
        connection.commit()
    else:
        cursor1.execute('UPDATE users SET group_number =%s WHERE user_id=%s',(group_number,user_id))
        connection.commit()

def mailing_raspes(mailflag):
    if mailflag=='raspes':
        cursor1.execute('SELECT user_id FROM users;')
        data = cursor1.fetchall()
        for user_dict in data:
            try:
                bot.send_message(user_dict['user_id'], 'НОВОЕ РАСПИСАНИЕ!!!!')
                bot.send_message(user_dict['user_id'], message_from_db(user_dict['user_id']))
            except Exception:
                print('юзер с айди', user_dict['user_id'], 'забанил бота')
                continue


def admin_message(message):
    admins_ids=[761983343,460206879]
    if message.from_user.id in admins_ids:
        cursor1.execute('SELECT user_id FROM users;')
        message_to_users=message.text[6:]
        data = cursor1.fetchall()
        for user_dict in data:
            try:
                if user_dict['user_id']==message.from_user.id:
                    bot.send_message(user_dict['user_id'], 'Рассылка отправлена')
                    continue
                bot.send_message(user_dict['user_id'], 'СООБЩЕНИЕ ОТ АДМИНА!!!')
                bot.send_message(user_dict['user_id'],message_to_users)
            except Exception:
                print('юзер с айди', user_dict['user_id'], 'забанил бота')
                continue


START_MESSAGE='Привет, я легенда МГАКА. Тупа ботяра созданная легендами для легенд. В общем, я занимаюсь рассылкой распи'\
              'сания. Чтобы увидеть мой функционал напиши "/help"'

HELP_MESSAGE='Итак, для того, чтобы я мог корректно спамить тебе расписанием, выбери свою группу командой "/setgroup".\n'\
    'Как только выберешь группу, можешь ввести команду "/now", чтобы глянуть текущее расписание для твоей группы.\nТакже'\
    ' я буду присылать тебе расписание, как только оно появится на сайте.'

@bot.message_handler(commands=['start'])
def handle_start(message):
    start_keyboard = telebot.types.ReplyKeyboardMarkup(True)
    start_keyboard.row('/start','/stop')
    start_keyboard.row('/help','/setgroup')
    start_keyboard.row('/now')
    start_keyboard.row('Информация/связь с разработчиком')
    bot.send_message(message.from_user.id, START_MESSAGE,reply_markup=start_keyboard)


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    #commands
    start_keyboard = telebot.types.ReplyKeyboardMarkup(True)

    if message.text == "/help":
        bot.send_message(message.from_user.id, HELP_MESSAGE, reply_markup=start_keyboard)

    elif message.text == "/setgroup":
        bot.send_message(message.from_user.id, 'Напиши мне свою группу. Формат:40АС(без пробелов, дефисов и т.д.)',
                         reply_markup=start_keyboard)

    elif message.text == "Информация/связь с разработчиком":
        bot.send_message(message.from_user.id, 'Пиши @legendaryoper', reply_markup=start_keyboard)



    elif message.text == "/stop":
        hide_keyboard = telebot.types.ReplyKeyboardRemove()
        bot.send_message(message.from_user.id, 'Блин, за что?((( Ладно, я заткнусь', reply_markup=hide_keyboard)
        sleep(5)
        bot.send_message(message.from_user.id, 'Ахах нюхай бебру, эта адская машина никогда не прекращает спамить',
                         reply_markup=start_keyboard)

    elif message.text == "/now":
        if check_group_id_in_database(message.from_user.id):
            bot.send_message(message.from_user.id, 'Держи текущее расписание:\n', )
            bot.send_message(message.from_user.id, message_from_db(message.from_user.id),reply_markup=start_keyboard)

        else:
            bot.send_message(message.from_user.id, 'Сначала скажи свою группу', reply_markup=start_keyboard)







    elif message.text.upper() in GROUP_LIST_FOR_MESSAGES[0]:
        bot.send_message(message.from_user.id, 'Хорошо, буду знать.',reply_markup=start_keyboard)
        us_id = message.from_user.id
        group_number = 1

        db_table_val(user_id=us_id,group_number=group_number )
        bot.send_message(us_id, 'Держи текущее расписание:\n', )
        bot.send_message(us_id, message_from_db(us_id), reply_markup=start_keyboard)

    elif message.text.upper() in GROUP_LIST_FOR_MESSAGES[1]:
        bot.send_message(message.from_user.id,  'Хорошо, буду знать.',reply_markup=start_keyboard)
        us_id = message.from_user.id
        group_number = 2

        db_table_val(user_id=us_id,group_number=group_number )
        bot.send_message(us_id, 'Держи текущее расписание:\n', )
        bot.send_message(us_id, message_from_db(us_id), reply_markup=start_keyboard)

    elif message.text.upper() in GROUP_LIST_FOR_MESSAGES[2]:
        bot.send_message(message.from_user.id,  'Хорошо, буду знать.',reply_markup=start_keyboard)
        us_id = message.from_user.id
        group_number = 3

        db_table_val(user_id=us_id,group_number=group_number)
        bot.send_message(us_id, 'Держи текущее расписание:\n', )
        bot.send_message(us_id, message_from_db(us_id), reply_markup=start_keyboard)

    elif message.text.upper() in GROUP_LIST_FOR_MESSAGES[3]:
        bot.send_message(message.from_user.id,  'Хорошо, буду знать.',reply_markup=start_keyboard)
        us_id = message.from_user.id
        group_number = 4

        db_table_val(user_id=us_id,group_number=group_number )
        bot.send_message(us_id, 'Держи текущее расписание:\n', )
        bot.send_message(us_id, message_from_db(us_id), reply_markup=start_keyboard)

    elif message.text.upper() in GROUP_LIST_FOR_MESSAGES[4]:
        bot.send_message(message.from_user.id,  'Хорошо, буду знать.',reply_markup=start_keyboard)
        us_id = message.from_user.id
        group_number = 5

        db_table_val(user_id=us_id,group_number=group_number )
        bot.send_message(us_id, 'Держи текущее расписание:\n', )
        bot.send_message(us_id, message_from_db(us_id), reply_markup=start_keyboard)

    elif message.text.upper() in GROUP_LIST_FOR_MESSAGES[5]:
        bot.send_message(message.from_user.id,  'Хорошо, буду знать.',reply_markup=start_keyboard)
        us_id = message.from_user.id
        group_number = 6

        db_table_val(user_id=us_id,group_number=group_number )
        bot.send_message(us_id, 'Держи текущее расписание:\n', )
        bot.send_message(us_id, message_from_db(us_id), reply_markup=start_keyboard)

    elif message.text.upper() in GROUP_LIST_FOR_MESSAGES[6]:
        bot.send_message(message.from_user.id,  'О, та самая группа где чел обосрался? Хорош мужик!',reply_markup=start_keyboard)
        us_id = message.from_user.id
        group_number = 7

        db_table_val(user_id=us_id,group_number=group_number )
        bot.send_message(us_id, 'Держи текущее расписание:\n', )
        bot.send_message(us_id, message_from_db(us_id), reply_markup=start_keyboard)

    elif message.text.upper() in GROUP_LIST_FOR_MESSAGES[7]:
        bot.send_message(message.from_user.id,  'Хорошо, буду знать.',reply_markup=start_keyboard)
        us_id = message.from_user.id
        group_number = 8

        db_table_val(user_id=us_id,group_number=group_number )
        bot.send_message(us_id, 'Держи текущее расписание:\n', )
        bot.send_message(us_id, message_from_db(us_id), reply_markup=start_keyboard)

    elif message.text.upper() in GROUP_LIST_FOR_MESSAGES[8]:
        bot.send_message(message.from_user.id, 'Ого, вижу ты из самой легендарной группы. Хорошо, буду знать.',reply_markup=start_keyboard)
        us_id = message.from_user.id
        group_number = 9

        db_table_val(user_id=us_id,group_number=group_number )
        bot.send_message(us_id, 'Держи текущее расписание:\n', )
        bot.send_message(us_id, message_from_db(us_id), reply_markup=start_keyboard)

    elif message.text.upper() in GROUP_LIST_FOR_MESSAGES[9]:
        bot.send_message(message.from_user.id,  'Чел ты...кринж, даже расписание тебе кидать не хочу.',reply_markup=start_keyboard)
        us_id = message.from_user.id
        group_number = 10

        db_table_val(user_id=us_id,group_number=group_number )
        bot.send_message(us_id, 'Держи текущее расписание:\n', )
        bot.send_message(us_id, message_from_db(us_id), reply_markup=start_keyboard)

    elif message.text.upper() in GROUP_LIST_FOR_MESSAGES[10]:
        bot.send_message(message.from_user.id,  'Хорошо, буду знать.',reply_markup=start_keyboard)
        us_id = message.from_user.id
        group_number = 11

        db_table_val(user_id=us_id,group_number=group_number )
        bot.send_message(us_id, 'Держи текущее расписание:\n', )
        bot.send_message(us_id, message_from_db(us_id), reply_markup=start_keyboard)

    elif message.text.upper() in GROUP_LIST_FOR_MESSAGES[11]:
        bot.send_message(message.from_user.id,  'Хорошо, буду знать.',reply_markup=start_keyboard)
        us_id = message.from_user.id
        group_number = 12

        db_table_val(user_id=us_id,group_number=group_number )
        bot.send_message(us_id, 'Держи текущее расписание:\n', )
        bot.send_message(us_id, message_from_db(us_id), reply_markup=start_keyboard)

    elif message.text.upper() in GROUP_LIST_FOR_MESSAGES[12]:
        bot.send_message(message.from_user.id,  'Хорошо, буду знать.',reply_markup=start_keyboard)
        us_id = message.from_user.id
        group_number = 13

        db_table_val(user_id=us_id,group_number=group_number )
        bot.send_message(us_id, 'Держи текущее расписание:\n', )
        bot.send_message(us_id, message_from_db(us_id), reply_markup=start_keyboard)

    elif message.text.upper() in GROUP_LIST_FOR_MESSAGES[13]:
        bot.send_message(message.from_user.id,  'Хорошо, буду знать.',reply_markup=start_keyboard)
        us_id = message.from_user.id
        group_number = 14

        db_table_val(user_id=us_id,group_number=group_number )
        bot.send_message(us_id, 'Держи текущее расписание:\n', )
        bot.send_message(us_id, message_from_db(us_id), reply_markup=start_keyboard)

    elif message.text.upper() in GROUP_LIST_FOR_MESSAGES[14]:
        bot.send_message(message.from_user.id,  'Хорошо, буду знать.',reply_markup=start_keyboard)
        us_id = message.from_user.id
        group_number = 15

        db_table_val(user_id=us_id,group_number=group_number )
        bot.send_message(us_id, 'Держи текущее расписание:\n', )
        bot.send_message(us_id, message_from_db(us_id), reply_markup=start_keyboard)

    elif message.text.upper() in GROUP_LIST_FOR_MESSAGES[15]:
        bot.send_message(message.from_user.id,  'Хорошо, буду знать.',reply_markup=start_keyboard)
        us_id = message.from_user.id
        group_number = 16

        db_table_val(user_id=us_id,group_number=group_number )
        bot.send_message(us_id, 'Держи текущее расписание:\n', )
        bot.send_message(us_id, message_from_db(us_id), reply_markup=start_keyboard)

    elif message.text.upper() in GROUP_LIST_FOR_MESSAGES[16]:
        bot.send_message(message.from_user.id,  'Хорошо, буду знать.',reply_markup=start_keyboard)
        us_id = message.from_user.id
        group_number = 17

        db_table_val(user_id=us_id,group_number=group_number )
        bot.send_message(us_id, 'Держи текущее расписание:\n', )
        bot.send_message(us_id, message_from_db(us_id), reply_markup=start_keyboard)

    elif message.text.upper() in GROUP_LIST_FOR_MESSAGES[17]:
        bot.send_message(message.from_user.id,  'Хорошо, буду знать.',reply_markup=start_keyboard)
        us_id = message.from_user.id
        group_number = 18

        db_table_val(user_id=us_id,group_number=group_number )
        bot.send_message(us_id, 'Держи текущее расписание:\n', )
        bot.send_message(us_id, message_from_db(us_id), reply_markup=start_keyboard)

    elif message.text.upper() in GROUP_LIST_FOR_MESSAGES[18]:
        bot.send_message(message.from_user.id,  'Хорошо, буду знать.',reply_markup=start_keyboard)
        us_id = message.from_user.id
        group_number = 19

        db_table_val(user_id=us_id,group_number=group_number )
        bot.send_message(us_id, 'Держи текущее расписание:\n', )
        bot.send_message(us_id, message_from_db(us_id), reply_markup=start_keyboard)

    elif message.text.upper() in GROUP_LIST_FOR_MESSAGES[19]:
        bot.send_message(message.from_user.id,  'Хорошо, буду знать.',reply_markup=start_keyboard)
        us_id = message.from_user.id
        group_number = 20

        db_table_val(user_id=us_id,group_number=group_number )
        bot.send_message(us_id, 'Держи текущее расписание:\n', )
        bot.send_message(us_id, message_from_db(us_id), reply_markup=start_keyboard)

    elif message.text.upper() in GROUP_LIST_FOR_MESSAGES[20]:
        bot.send_message(message.from_user.id,  'Хорошо, буду знать.',reply_markup=start_keyboard)
        us_id = message.from_user.id
        group_number = 21

        db_table_val(user_id=us_id,group_number=group_number )
        bot.send_message(us_id, 'Держи текущее расписание:\n', )
        bot.send_message(us_id, message_from_db(us_id), reply_markup=start_keyboard)

    elif message.text.upper() in GROUP_LIST_FOR_MESSAGES[21]:
        bot.send_message(message.from_user.id, 'Хорошо, буду знать.',reply_markup=start_keyboard)
        us_id = message.from_user.id
        group_number = 22

        db_table_val(user_id=us_id,group_number=group_number )
        bot.send_message(us_id, 'Держи текущее расписание:\n', )
        bot.send_message(us_id, message_from_db(us_id), reply_markup=start_keyboard)

    elif message.text.upper() in GROUP_LIST_FOR_MESSAGES[22]:
        bot.send_message(message.from_user.id,  'Хорошо, буду знать.',reply_markup=start_keyboard)
        us_id = message.from_user.id
        group_number = 23

        db_table_val(user_id=us_id,group_number=group_number )
        bot.send_message(us_id, 'Держи текущее расписание:\n', )
        bot.send_message(us_id, message_from_db(us_id), reply_markup=start_keyboard)

    elif message.text.upper() in GROUP_LIST_FOR_MESSAGES[23]:
        bot.send_message(message.from_user.id,  'Хорошо, буду знать.',reply_markup=start_keyboard)
        us_id = message.from_user.id
        group_number = 24

        db_table_val(user_id=us_id,group_number=group_number )
        bot.send_message(us_id, 'Держи текущее расписание:\n', )
        bot.send_message(us_id, message_from_db(us_id), reply_markup=start_keyboard)

    elif message.text.upper() in GROUP_LIST_FOR_MESSAGES[24]:
        bot.send_message(message.from_user.id,  'Хорошо, буду знать.',reply_markup=start_keyboard)
        us_id = message.from_user.id
        group_number = 25

        db_table_val(user_id=us_id,group_number=group_number )
        bot.send_message(us_id, 'Держи текущее расписание:\n', )
        bot.send_message(us_id, message_from_db(us_id), reply_markup=start_keyboard)

    elif message.text.upper() in GROUP_LIST_FOR_MESSAGES[25]:
        bot.send_message(message.from_user.id,  'Хорошо, буду знать.',reply_markup=start_keyboard)
        us_id = message.from_user.id
        group_number = 26

        db_table_val(user_id=us_id,group_number=group_number )
        bot.send_message(us_id, 'Держи текущее расписание:\n', )
        bot.send_message(us_id, message_from_db(us_id), reply_markup=start_keyboard)

    elif message.text.upper() in GROUP_LIST_FOR_MESSAGES[26]:
        bot.send_message(message.from_user.id,  'Хорошо, буду знать.',reply_markup=start_keyboard)
        us_id = message.from_user.id
        group_number = 27

        db_table_val(user_id=us_id,group_number=group_number )
        bot.send_message(us_id, 'Держи текущее расписание:\n', )
        bot.send_message(us_id, message_from_db(us_id), reply_markup=start_keyboard)

    elif message.text.upper() in GROUP_LIST_FOR_MESSAGES[27]:
        bot.send_message(message.from_user.id,  'Хорошо, буду знать.',reply_markup=start_keyboard)
        us_id = message.from_user.id
        group_number = 28

        db_table_val(user_id=us_id,group_number=group_number )
        bot.send_message(us_id, 'Держи текущее расписание:\n', )
        bot.send_message(us_id, message_from_db(us_id), reply_markup=start_keyboard)

    elif message.text.upper() in GROUP_LIST_FOR_MESSAGES[28]:
        bot.send_message(message.from_user.id,  'Хорошо, буду знать.',reply_markup=start_keyboard)
        us_id = message.from_user.id
        group_number = 29

        db_table_val(user_id=us_id,group_number=group_number )
        bot.send_message(us_id, 'Держи текущее расписание:\n', )
        bot.send_message(us_id, message_from_db(us_id), reply_markup=start_keyboard)

    elif message.text.upper() in GROUP_LIST_FOR_MESSAGES[29]:
        bot.send_message(message.from_user.id,  'Хорошо, буду знать.',reply_markup=start_keyboard)
        us_id = message.from_user.id
        group_number = 30

        db_table_val(user_id=us_id,group_number=group_number )
        bot.send_message(us_id, 'Держи текущее расписание:\n', )
        bot.send_message(us_id, message_from_db(us_id), reply_markup=start_keyboard)

    elif message.text.upper() in GROUP_LIST_FOR_MESSAGES[30]:
        bot.send_message(message.from_user.id,  'Хорошо, буду знать.',reply_markup=start_keyboard)
        us_id = message.from_user.id
        group_number = 31

        db_table_val(user_id=us_id,group_number=group_number )
        bot.send_message(us_id, 'Держи текущее расписание:\n', )
        bot.send_message(us_id, message_from_db(us_id), reply_markup=start_keyboard)

    elif message.text.upper() in GROUP_LIST_FOR_MESSAGES[31]:
        bot.send_message(message.from_user.id,  'Хорошо, буду знать.',reply_markup=start_keyboard)
        us_id = message.from_user.id
        group_number = 32

        db_table_val(user_id=us_id,group_number=group_number )
        bot.send_message(us_id, 'Держи текущее расписание:\n', )
        bot.send_message(us_id, message_from_db(us_id), reply_markup=start_keyboard)

    elif message.text.upper() in GROUP_LIST_FOR_MESSAGES[32]:
        bot.send_message(message.from_user.id,  'Хорошо, буду знать.',reply_markup=start_keyboard)
        us_id = message.from_user.id
        group_number = 33

        db_table_val(user_id=us_id,group_number=group_number )
        bot.send_message(us_id, 'Держи текущее расписание:\n', )
        bot.send_message(us_id, message_from_db(us_id), reply_markup=start_keyboard)

    elif message.text.upper() in GROUP_LIST_FOR_MESSAGES[33]:
        bot.send_message(message.from_user.id,  'Хорошо, буду знать.',reply_markup=start_keyboard)
        us_id = message.from_user.id
        group_number = 34

        db_table_val(user_id=us_id,group_number=group_number )
        bot.send_message(us_id, 'Держи текущее расписание:\n', )
        bot.send_message(us_id, message_from_db(us_id), reply_markup=start_keyboard)

    elif message.text.upper() in GROUP_LIST_FOR_MESSAGES[34]:
        bot.send_message(message.from_user.id,  'Хорошо, буду знать.',reply_markup=start_keyboard)
        us_id = message.from_user.id
        group_number = 35

        db_table_val(user_id=us_id,group_number=group_number )
        bot.send_message(us_id, 'Держи текущее расписание:\n', )
        bot.send_message(us_id, message_from_db(us_id), reply_markup=start_keyboard)

    elif message.text.upper() in GROUP_LIST_FOR_MESSAGES[35]:
        bot.send_message(message.from_user.id,  'Хорошо, буду знать.',reply_markup=start_keyboard)
        us_id = message.from_user.id
        group_number = 36

        db_table_val(user_id=us_id,group_number=group_number )
        bot.send_message(us_id, 'Держи текущее расписание:\n', )
        bot.send_message(us_id, message_from_db(us_id), reply_markup=start_keyboard)

    elif message.text.upper() in GROUP_LIST_FOR_MESSAGES[36]:
        bot.send_message(message.from_user.id,  'Хорошо, буду знать.',reply_markup=start_keyboard)
        us_id = message.from_user.id
        group_number = 37

        db_table_val(user_id=us_id,group_number=group_number )
        bot.send_message(us_id, 'Держи текущее расписание:\n', )
        bot.send_message(us_id, message_from_db(us_id), reply_markup=start_keyboard)

    elif message.text.upper() in GROUP_LIST_FOR_MESSAGES[37]:
        bot.send_message(message.from_user.id,  'Хорошо, буду знать.',reply_markup=start_keyboard)
        us_id = message.from_user.id
        group_number = 38

        db_table_val(user_id=us_id,group_number=group_number )
        bot.send_message(us_id, 'Держи текущее расписание:\n', )
        bot.send_message(us_id, message_from_db(us_id), reply_markup=start_keyboard)

    elif message.text.upper() in GROUP_LIST_FOR_MESSAGES[38]:
        bot.send_message(message.from_user.id,  'Хорошо, буду знать.',reply_markup=start_keyboard)
        us_id = message.from_user.id
        group_number = 39

        db_table_val(user_id=us_id,group_number=group_number )
        bot.send_message(us_id, 'Держи текущее расписание:\n', )
        bot.send_message(us_id, message_from_db(us_id), reply_markup=start_keyboard)

    elif message.text.upper() in GROUP_LIST_FOR_MESSAGES[39]:
        bot.send_message(message.from_user.id,  'Хорошо, буду знать.',reply_markup=start_keyboard)
        us_id = message.from_user.id
        group_number = 40

        db_table_val(user_id=us_id,group_number=group_number )
        bot.send_message(us_id, 'Держи текущее расписание:\n', )
        bot.send_message(us_id, message_from_db(us_id), reply_markup=start_keyboard)

    elif message.text.upper() in GROUP_LIST_FOR_MESSAGES[40]:
        bot.send_message(message.from_user.id,  'Хорошо, буду знать.',reply_markup=start_keyboard)
        us_id = message.from_user.id
        group_number = 41

        db_table_val(user_id=us_id,group_number=group_number )
        bot.send_message(us_id, 'Держи текущее расписание:\n', )
        bot.send_message(us_id, message_from_db(us_id), reply_markup=start_keyboard)

    elif message.text.upper() in GROUP_LIST_FOR_MESSAGES[41]:
        bot.send_message(message.from_user.id,  'Хорошо, буду знать.',reply_markup=start_keyboard)
        us_id = message.from_user.id
        group_number = 42

        db_table_val(user_id=us_id,group_number=group_number )
        bot.send_message(us_id, 'Держи текущее расписание:\n', )
        bot.send_message(us_id, message_from_db(us_id), reply_markup=start_keyboard)

    elif message.text.upper() in GROUP_LIST_FOR_MESSAGES[42]:
        bot.send_message(message.from_user.id,  'Хорошо, буду знать.',reply_markup=start_keyboard)
        us_id = message.from_user.id
        group_number = 43

        db_table_val(user_id=us_id,group_number=group_number )
        bot.send_message(us_id, 'Держи текущее расписание:\n', )
        bot.send_message(us_id, message_from_db(us_id), reply_markup=start_keyboard)

    elif message.text.upper() in GROUP_LIST_FOR_MESSAGES[43]:
        bot.send_message(message.from_user.id,  'Хорошо, буду знать.',reply_markup=start_keyboard)
        us_id = message.from_user.id
        group_number = 44

        db_table_val(user_id=us_id,group_number=group_number )
        bot.send_message(us_id, 'Держи текущее расписание:\n', )
        bot.send_message(us_id, message_from_db(us_id), reply_markup=start_keyboard)

    elif message.text.upper() in GROUP_LIST_FOR_MESSAGES[44]:
        bot.send_message(message.from_user.id,  'Хорошо, буду знать.',reply_markup=start_keyboard)
        us_id = message.from_user.id
        group_number = 45

        db_table_val(user_id=us_id,group_number=group_number )
        bot.send_message(us_id, 'Держи текущее расписание:\n', )
        bot.send_message(us_id, message_from_db(us_id), reply_markup=start_keyboard)

    elif message.text.upper() in GROUP_LIST_FOR_MESSAGES[45]:
        bot.send_message(message.from_user.id,  'Хорошо, буду знать.',reply_markup=start_keyboard)
        us_id = message.from_user.id
        group_number = 46

        db_table_val(user_id=us_id,group_number=group_number )
        bot.send_message(us_id, 'Держи текущее расписание:\n', )
        bot.send_message(us_id, message_from_db(us_id), reply_markup=start_keyboard)

    elif message.text.startswith('/admin'):
        admin_message(message)

    else:
        bot.send_message(message.from_user.id, "Я тебя не понимаю. Напиши /start или /help.",reply_markup=start_keyboard)


def polling():
    while True:
        bot.polling(none_stop=False,interval=1)


print('привет')


parsing_thread = Thread(target=parse.parse_and_update_db,args=(HEADERS,GROUP_LIST,PARSE_URL,connection))
polling_thread = Thread(target=polling,)
parsing_thread.start()
polling_thread.start()

while True:
    if parse.NEW_RASPES:
        mailing_raspes('raspes')
        sleep(60*20)
    else:
        sleep(60*20)






