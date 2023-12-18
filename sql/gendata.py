import psycopg2
import bcrypt
import string
import random
import csv
import numpy as np
import datetime
from faker import Faker
from sqlalchemy import event
import pandas as pd
import sqlalchemy
from sqlalchemy import create_engine
import time

fake = Faker()
USER_STATUS = ['active', 'banned']
USER_STATUS_PROB = [0.95, 0.05]
PASSWORD_LEN = range(8, 16)
PHONENUM_LEN = 10
USER_NAME_DICTIONARY = './csv/baby-names.csv'

ANIMAL_ORG_NAME_DICTIONARY = './csv/animal_org_names.csv'
VET_NAME_DICTIONARY = './csv/vet-names.csv'
FIRE_AGENCY_DICTIONARY = './csv/fireagency_names.csv'
POLICE_STATION_DICTIONARY = './csv/policeagency_names.csv'
SHORT_ADDRESS_DICTIONARY = './csv/short_address.csv'
RESPONDER_ADDRESS_DICTIONARY = './csv/responder_address.csv'
PLACEMENT_NAME_DICTIONARY = './csv/placement_names.csv'
PASSWORD_DICTIONARY_1 = './csv/bcrypt_password.csv'
PASSWORD_DICTIONARY_2 = './csv/bcrypt_password2.csv'
TAIPEI_ADDRESSES_DICTIONARY = './csv/taipei_address.csv'
PLACEMENT_DICTIONARY = './csv/placement.csv'

CITY = ['台北市', '新北市']
DISTRICTS = [
    [
        '松山區', '信義區', '大安區', '中山區', '中正區', '大同區', '萬華區', '文山區', '南港區', '內湖區', '士林區',
        '北投區'
    ],
    [
        '板橋區', '中和區', '新莊區', '土城區', '汐止區', '鶯歌區', '淡水區', '五股區', '林口區', '深坑區', '坪林區',
        '石門區', '萬里區', '雙溪區', '烏來區', '三重區', '永和區', '新店區', '蘆洲區', '樹林區', '三峽區', '瑞芳區',
        '泰山區', '八里區', '石碇區', '三芝區', '金山區', '平溪區', '貢寮區'
    ]
]

DISTRICT_OFFICE_NAMES = [
    'Songshan District Office', 'Xinyi District Office', 'Daan District Office', 'Zhongshan District Office',
    'Zhongzheng District Office', 'Datong District Office', 'Wanhua District Office', 'Wenshan District Office',
    'Nangang District Office', 'Neihu District Office', 'Shilin District Office', 'Beitou District Office',
    'Banqiao District Office', 'Sanchong District Office', 'Zhonghe District Office', 'Yonghe District Office',
    'Xinzhuang District Office', 'Xindian District Office', 'Tucheng District Office', 'Luzhou District Office',
    'Shulin District Office', 'Xizhi District Office', 'Yingge District Office', 'Sanxia District Office',
    'Danshui District Office', 'Ruifang District Office', 'Wugu District Office', 'Taishan District Office',
    'Linkou District Office', 'Shenkeng District Office', 'Shiding District Office', 'Pinglin District Office',
    'Sanzhi District Office', 'Shimen District Office', 'Bali District Office', 'Pingxi District Office',
    'Shuangxi District Office', 'Gongliao District Office', 'Jinshan District Office', 'Wanli District Office',
    'Wulai District Office'
]

ANIMAL_TYPES = [
    'Dog', 'Cat', 'Bird', 'Snake', 'Deer', 'Monkey', 'Fish', 'Bear', 'Other'
]

EVENT_TYPES = [
    'Roadkill',
    'AnimalBlockingTraffic',
    'StrayAnimal',
    'AnimalAttack',
    'AnimalAbuse',
    'DangerousWildlifeSighting',
    'Other'
]

EVENT_STATUS = [
    "Ongoing", "Resolved", "Unresolved", "Deleted", "Failed", "False Alarm"
]

EVENT_STATUS_PROB = [0.1, 0.4, 0.1, 0.2, 0.15, 0.05]

# values generated by psql database after insertions
USER_ID_ARRAY = []
NORMAL_USER_ID_ARRAY = []
RESPONDER_ID_ARRAY = []
NUM_OF_CHANNELS = -1
EVENT_ID_ARRAY = []
PLACEMENT_ID_ARRAY = []
MAX_NUM_ANIMALS_PER_EVENT = 4

# user names
file = open(USER_NAME_DICTIONARY)
name_reader = csv.reader(file)
names = []
prob = []
sum = 0
for row in name_reader:
    if row[0] == 'year' and row[1] == 'name' and row[2] == 'percent' and row[3] == 'sex':
        continue
    names.append(row[1])
    prob.append(float(row[2]))
    sum += float(row[2])
prob = np.divide(prob, np.array(sum))

# responder names
f = open(ANIMAL_ORG_NAME_DICTIONARY)
f.readline()
reader = f.readlines()
ANIMAL_ORG_NAMES = [row.strip() for row in reader]
f.close()

f = open(VET_NAME_DICTIONARY)
f.readline()
reader = f.readlines()
VET_NAMES = [row.strip() for row in reader]
f.close()

f = open(FIRE_AGENCY_DICTIONARY)
f.readline()
reader = f.readlines()
FIRE_AGENCY_NAMES = [row.strip() for row in reader]
f.close()

f = open(POLICE_STATION_DICTIONARY)
f.readline()
reader = f.readlines()
POLICE_STATION_NAMES = [row.strip() for row in reader]
f.close()

f = open(SHORT_ADDRESS_DICTIONARY)
f.readline()
reader = f.readlines()
SHORT_ADDRESSES = [row.strip() for row in reader]
f.close()

f = open(RESPONDER_ADDRESS_DICTIONARY)
f.readline()
reader = f.readlines()
RESPONDER_ADDRESSES = [row.strip() for row in reader]
f.close()

f = open(PASSWORD_DICTIONARY_1)
f.readline()
reader = f.readlines()
BCRYPT_PASSWORDS = [row.strip() for row in reader]
f.close()

f = open(PASSWORD_DICTIONARY_2)
f.readline()
reader = f.readlines()
BCRYPT_PASSWORDS += [row.strip() for row in reader]
f.close()

taipei_address_df = pd.read_csv(TAIPEI_ADDRESSES_DICTIONARY)
TAIPEI_ADDRESSES = taipei_address_df.values.tolist()

place_df = pd.read_csv(PLACEMENT_DICTIONARY, dtype={'phonenumber': str})
place_df = place_df.fillna(np.nan).replace([np.nan], [None])
PLACEMENTS = place_df.values.tolist()

RESPONDER_TYPES = [
    'Vet', 'Police', 'Fire Agency', 'Animal Protection Groups', 'District Office'
]

RESPONDER_NAMES = [
    VET_NAMES, POLICE_STATION_NAMES, FIRE_AGENCY_NAMES, ANIMAL_ORG_NAMES, DISTRICT_OFFICE_NAMES
]

f = open(PLACEMENT_NAME_DICTIONARY)
f.readline()
reader = f.readlines()
PLACEMENT_NAMES = [row.strip() for row in reader]
f.close()


# generate random values
def manual_gen_password():
    global PASSWORD_LEN
    len = random.choice(PASSWORD_LEN)
    letters = string.ascii_letters + string.digits
    passwd = ''.join(random.choice(letters) for _ in range(len))
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(passwd.encode(), salt).decode()
    return hashed


def gen_password():
    global BCRYPT_PASSWORDS
    return random.choice(BCRYPT_PASSWORDS)


def gen_phonenumber():
    global PHONENUM_LEN
    letters = string.digits
    return ''.join(random.choice(letters) for i in range(PHONENUM_LEN))


def gen_user_name():
    global names, prob
    name = np.random.choice(names, p=prob)
    return name


def gen_time_stamp(start=datetime.datetime(2013, 1, 1), end=datetime.datetime(2023, 11, 20)):
    global fake
    timestamp = fake.date_time_between(start_date=start, end_date=end)
    return timestamp


# gen email based on a given organization name
# truncated to 20 characters
def gen_org_email(org_name):
    email = org_name.lower().replace(" ", "_")[:20] + "@gmail.com"
    return email


# gen email based on a given user name
# truncated to 20 characters
def gen_user_email(user_name):
    random_digits = ''.join(random.choice(string.digits) for i in range(4))
    email = (user_name.lower() + random_digits)[:20] + "@gmail.com"
    return email


# gen users
def gen_all_users(cursor, num_of_users):
    global USER_ID_ARRAY
    max_existing_user_id = max(USER_ID_ARRAY)
    global USER_STATUS, USER_STATUS_PROB
    insert_users_query = """INSERT INTO Users(userid, password, email, role) VALUES(%s, %s, %s, %s);"""
    insert_user_info_query = """INSERT INTO UserInfo(userid, name, phonenumber, status) VALUES(%s, %s, %s, %s);"""

    for i in range(num_of_users):
        print(i)
        userid = max_existing_user_id + i + 1
        name = gen_user_name()
        users_record = (userid, gen_password(), gen_user_email(name), 'user')
        cursor.execute(insert_users_query, users_record)
        user_info_record = (userid, name, gen_phonenumber(), np.random.choice(USER_STATUS, p=USER_STATUS_PROB))
        cursor.execute(insert_user_info_query, user_info_record)

    print("Generated all users")


# gen responders
def gen_all_responders(cursor):
    responders_df = pd.read_csv("./csv/responder.csv", dtype={'phonenumber': str})
    max_existing_user_id = max(USER_ID_ARRAY)
    responders_df['userid'] = responders_df.index + max_existing_user_id + 1
    responders_df['email'] = responders_df['email'].apply(lambda x: gen_org_email(gen_user_name()) if x != x else x)
    responders_df['password'] = responders_df['password'].apply(lambda x: gen_password() if x != x else x)
    print(responders_df.to_string())

    insert_users_query = """INSERT INTO Users(userid, password, email, role) VALUES(%s, %s, %s, %s);"""
    insert_responder_info_query = """INSERT INTO ResponderInfo(responderid, respondername, phonenumber, respondertype, address) VALUES(%s, %s, %s, %s, %s);"""
    #
    for i in range(len(responders_df)):
        responder = responders_df.loc[[i]].to_dict('records')[0]
        print(responder)
        userid = responder['userid']
        password = responder['password']
        email = responder['email']
        role = 'responder'
        responderid = userid
        respondername = responder['respondername']
        phonenumber = responder['phonenumber']
        respondertype = responder['respondertype']
        address = responder['address']
        users_record = (userid, password, email, role)
        cursor.execute(insert_users_query, users_record)
        responder_info_record = (responderid, respondername, phonenumber, respondertype, address)
        cursor.execute(insert_responder_info_query, responder_info_record)
    print("Generated all responders")


# user subscription records
def gen_user_sub_records(cursor, num_of_records):
    insert_query = """INSERT INTO subscriptionRecord(channelid, userid) VALUES(%s, %s);"""
    records = [(random.choice(range(NUM_OF_CHANNELS)), random.choice(USER_ID_ARRAY)) for _ in range(num_of_records)]
    records = list(set(records))
    for i in range(len(records)):
        cursor.execute(insert_query, records[i])
    print("Generated user subscription records")


# gen channels
def gen_all_channels(cursor):
    global NUM_OF_CHANNELS
    insert_query = """INSERT INTO Channel(channelid, eventdistrict, eventtype, eventanimal) VALUES(%s, %s, %s, %s);"""
    idx = 0
    for dist in ([None] + DISTRICTS[0] + DISTRICTS[1]):
        for eventtype in ([None] + EVENT_TYPES):
            for animal in ([None] + ANIMAL_TYPES):
                record = (idx, dist, eventtype, animal)
                cursor.execute(insert_query, record)
                idx += 1
    NUM_OF_CHANNELS = idx
    count = cursor.rowcount
    print(count, "Record inserted successfully into channel table")


def gen_all_placements(cursor):
    idx = 0
    insert_query = """INSERT INTO Placement(placementid, name, address, phonenumber) VALUES(%s, %s, %s, %s)"""
    for placement in PLACEMENTS:
        placementid = placement[0]
        name = placement[1]
        address = placement[2]
        phonenumber = placement[3]
        if phonenumber is None and placementid not in (0, 1):
            phonenumber = gen_phonenumber()
        record = (placementid, name, address, phonenumber)
        cursor.execute(insert_query, record)


# gen events
def gen_events(cursor, num_of_events):
    insert_query = """INSERT INTO Event(eventtype, userid, responderid, status, shortdescription, city, district, shortaddress, createdat) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s);"""

    # "Ongoing", "Resolved", "Unresolved", "Deleted", "Failed", "False Alarm"

    for _ in range(num_of_events):
        cityindex = random.choice(range(len(CITY)))
        status = np.random.choice(EVENT_STATUS, p=EVENT_STATUS_PROB)
        address_list = random.choice(TAIPEI_ADDRESSES)

        if (status == EVENT_STATUS[2] or status == EVENT_STATUS[3]):
            responder = None
        else:
            responder = random.choice(RESPONDER_ID_ARRAY)
        record = (
            random.choice(EVENT_TYPES),
            random.choice(NORMAL_USER_ID_ARRAY),
            responder,
            status,
            "this is a short description",
            address_list[0],
            address_list[1],
            address_list[2],
            gen_time_stamp())

        cursor.execute(insert_query, record)


def get_all_userids(cursor):
    global USER_ID_ARRAY
    select_query = "SELECT userid FROM Users;"
    cursor.execute(select_query)
    userids = cursor.fetchall()
    USER_ID_ARRAY = [row[0] for row in userids]


def get_normal_userids(cursor):
    global NORMAL_USER_ID_ARRAY
    select_query = "SELECT userid FROM UserInfo;"
    cursor.execute(select_query)
    userids = cursor.fetchall()
    NORMAL_USER_ID_ARRAY = [row[0] for row in userids]


def get_all_responderids(cursor):
    global RESPONDER_ID_ARRAY
    select_query = "SELECT responderid FROM ResponderInfo;"
    cursor.execute(select_query)
    responderids = cursor.fetchall()
    RESPONDER_ID_ARRAY = [row[0] for row in responderids]


def get_num_of_channels(cursor):
    global NUM_OF_CHANNELS
    select_query = "SELECT COUNT(*) FROM Channel;"
    cursor.execute(select_query)
    NUM_OF_CHANNELS = cursor.fetchone()[0]


def get_event_ids(cursor):
    global EVENT_ID_ARRAY
    select_query = "SELECT eventid FROM Event;"
    cursor.execute(select_query)
    eventids = cursor.fetchall()
    EVENT_ID_ARRAY = [row[0] for row in eventids]


def get_placement_ids(cursor):
    global PLACEMENT_ID_ARRAY
    select_query = "SELECT placementid FROM placement;"
    cursor.execute(select_query)
    placementids = cursor.fetchall()
    PLACEMENT_ID_ARRAY = [row[0] for row in placementids]


def gen_event_animals(cursor):
    global MAX_NUM_ANIMALS_PER_EVENT
    insert_query = """INSERT INTO Animal(EventId, Type, Description, PlacementId) VALUES(%s, %s, %s, %s);"""
    for eid in EVENT_ID_ARRAY:
        num_animals = random.randint(1, MAX_NUM_ANIMALS_PER_EVENT)
        for _ in range(num_animals):
            record = (eid, random.choice(ANIMAL_TYPES), "This is a description", random.choice(PLACEMENT_ID_ARRAY))
            cursor.execute(insert_query, record)


conn = psycopg2.connect(
    host="127.0.0.1",
    port="5432",
    user="postgres",
    password="postgres",
    database="testcreate"
)

cursor = conn.cursor()
# # generate all channels
# gen_all_channels(cursor)
# get_num_of_channels(cursor)
# conn.commit()
#
# generate users
# get_all_userids(cursor)
# gen_all_users(cursor, 20000)
# conn.commit()
#
# # generate responders
# get_all_userids(cursor)
# gen_all_responders(cursor)
# get_all_responderids(cursor)
# conn.commit()

# # generate events
# get_normal_userids(cursor)
# get_all_responderids(cursor)
# gen_events(cursor, 100000)
# # get_event_ids(cursor)
# conn.commit()

# # generate user subscription records
# get_num_of_channels(cursor)
# get_all_userids(cursor)
# print(NUM_OF_CHANNELS)
# gen_user_sub_records(cursor, 5000)
# conn.commit()


# # generate placements
# gen_all_placements(cursor)
# get_placement_ids(cursor)
# conn.commit()
#
# # generate event animals
get_event_ids(cursor)
get_placement_ids(cursor)
gen_event_animals(cursor)
conn.commit()

# conn.close()


# engine = create_engine('postgresql://postgres:postgres@127.0.0.1:5432/furalert')
#
# # temp_df = pd.DataFrame(columns=['password', 'name', 'email', 'phonenumber', 'status'])
# # print(temp_df)
# temp_list = []
# start_time = time.time()
# for i in range(100000):
#     name = gen_user_name()
#     record = [gen_password(), name, gen_user_email(name), gen_phonenumber(), np.random.choice(USER_STATUS, p=USER_STATUS_PROB)]
#     temp_list.append(record)
# # print(temp_list)
# df = pd.DataFrame(temp_list,
#                   columns=['password', 'name', 'email', 'phonenumber', 'status'])
# print("--- %s seconds ---" % (time.time() - start_time))
#
# df.to_sql("users", engine.connect(), index=False, if_exists="append")
