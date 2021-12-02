from config import *
from model_mongodb import *
from bs4 import BeautifulSoup 
import requests
import datetime
from dateutil.relativedelta import relativedelta
import sys

gender=sys.argv[1]

def crawl_top100_kol(gender):
    rank_url='https://wear.jp/women-ranking/user/' if gender == 'women' else 'https://wear.jp/men-ranking/user/' 
    res = requests.get(rank_url, headers=headers)  
    soup = BeautifulSoup(res.text, 'html.parser')
    lst_top100_kol=soup.select('div#user_ranking li')
    return lst_top100_kol

def check_new_kol(lst_exist_kol,lst_top100_kol):
    datetime_value_1month_ago=datetime.datetime.now() - relativedelta(months=+1)
    lst_new_kol=[]
    for kol in lst_top100_kol:
        if kol.select_one('p'):
            kol_id=kol.select_one('a')['href'].replace('/','')
            if kol_id not in lst_exist_kol:
                lst_new_kol.append({'kol_id':kol_id,'latest_update_at':datetime_value_1month_ago})
        else: 
            continue
    return lst_new_kol

if __name__ == "__main__":  
    lst_exist_kol=extract_mongodb_distinct_kol(gender)
    lst_top100_kol=crawl_top100_kol(gender)
    lst_new_kol=check_new_kol(lst_exist_kol,lst_top100_kol)
    try:
        insert_mongodb_new_kol(gender, lst_new_kol)
    except:
        pass

    

