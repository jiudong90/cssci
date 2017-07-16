#-*-conding:utf-8-*-

import sqlite3
import traceback
from bs4 import BeautifulSoup
import urllib.request
import time


def create_table(database='cssci.db', table='CSSCI'):
    global conn, cursor
    if table == 'CSSCI':
        table_columns = '''CREATE TABLE IF NOT EXISTS CSSCI(
                        RID INT PRIMARY KEY  NOT NULL,
                        篇名 TEXT  NOT NULL,
                        英文篇名 TEXT  NOT NULL,
                        作者及机构 TEXT  NOT NULL,
                        文献类型 TEXT,
                        学科类别 TEXT,
                        中图类号 TEXT,
                        基金项目 TEXT,
                        来源期刊 TEXT,
                        年代卷期 TEXT,
                        关键词 TEXT,
                        参考文献 TEXT);'''

    # establish connection
    # if the database provided is not exist, sqlite will create a new one.
    conn = sqlite3.connect(database)
    # create a cursor
    cursor = conn.cursor()
    try:
        cursor.execute(table_columns)
        print('Table created successfully')
    except:
        print("Create table failed")
        traceback.print_exc()
        return False
    return True


def open_database(database='cssci.db'):
    # establish connection
    # if the database provided is not exist, sqlite will create a new one.
    conn = sqlite3.connect(database)
    return conn


def close_database():
    global conn, cursor
    # commit
    conn.commit()
    # close cursor
    cursor.close()
    # close connection
    conn.close()


def insert_record(table, data):
    global conn, cursor
    # make sure the cursor is valid

    # check table here

    # get next RID
    values = select_query('SELECT * FROM CSSCI')
    rid = len(values)+1
    rid_tuple = (rid,)

    sql = 'INSERT INTO {} VALUES{}'.format(table, rid_tuple+data)
    # print("SQL: %s" % sql)
    cursor.execute(sql)
    print('Records {} inserted successfully'.format(rid))
    return rid


# rid: record id
def delete_record(table, record_id):
    global conn, cursor
    # make sure the cursor is valid

    # check table here

    sql = 'DELETE FROM {} WHERE RID={}'.format(table, record_id)
    cursor.execute(sql)
    print('Records {} deleted successfully'.format(record_id))


# begin: start from which record id
# end: end with which record id
def delete_records(table, begin, end):
    global conn, cursor
    # make sure the cursor is valid

    # check table here

    for offset in range(end - begin + 1):
        rid = begin + offset
        sql = 'DELETE FROM {} WHERE RID={}'.format(table, rid)
        cursor.execute(sql)
        print('Records {} deleted successfully'.format(rid))


def select_query(sql):
    global conn, cursor
    # issue SQL command
    cursor.execute(sql)
    # fetch the result
    values = cursor.fetchall()
    # print(values)
    return values


def get_record(page_source, parser='lxml'):
    # print('get_record')
    soup = BeautifulSoup(page_source, parser)
    time.sleep(5)
    # print(soup.prettify())
    record = ''
    flag = False
    for sub_tr in soup.find_all("tr", style=None):
        key = sub_tr.find_all("td")[0].string
        sub_td = sub_tr.find_all("td")[1]
        # print(sub_td.string)
        if key == "参考文献":
            # print(sub_td.string, end='')
            # record += sub_td.string.strip()
            flag = True
        if flag:
            for sub_div in sub_td.find_all("div"):
                for sub_div_str in sub_div.strings:
                    print(sub_div_str, end='')
                    record += sub_div_str.strip()
                print('\t', end='')
                record += '\t'
        else:
            for sub_str in sub_td.strings:
                print(sub_str.string, end='')
                record += sub_str.string.strip()
        # print("\t", end='')
        print("|", end='')
        record += '|'
    print()
    columns_list = record.strip('|').split(sep='|')
    columns_tuple = tuple(columns_list)
    # return record
    # return columns_list
    return columns_tuple


def save_to_db(page_source, database='cssci.db', table='CSSCI'):
    global conn, cursor
    print('save_to_db')
    conn = open_database(database=database)
    cursor = conn.cursor()
    create_table(database='cssci.db', table=table)
    # html = open(page_source, encoding='utf-8')
    record = get_record(page_source)
    print(record)
    rid = insert_record('CSSCI', record)
    close_database()


if __name__ == '__main__':
    global conn, cursor
    # conn = open_database('cssci.db')
    # cursor = conn.cursor()

    # create_table('cssci.db')
    # local html page
    source = 'testdata/test.html'
    html = open(source, encoding='utf-8')
    # web page
    # url = r'http://cssci.nju.edu.cn/ly_search_list.html?id=11G0422011010001'
    # html = urllib.request.urlopen(url, timeout=5000).read()
    record = get_record(html)
    print(record)
    # rid = insert_record('CSSCI', record)
    # sql = 'SELECT * FROM CSSCI WHERE RID={}'.format(rid)
    # print(select_query(sql))

    # delete_records('CSSCI', 1, rid)

    # close_database()




