#coding=utf-8
from config import *
from model_mongodb import *
from model_sql import *
from bs4 import BeautifulSoup
import requests
from datetime import datetime, timedelta
import time
import json
import random
import datetime
import sys

gender=sys.argv[1]

def get_non_acc():
    with open('./utils/non_acc_category.json') as f:
        non_acc_category = json.load(f)
    non_acc=[]
    for lst_product in non_acc_category.values():
        non_acc+=lst_product
    return non_acc

def parse_datetime(date_string):
    today=datetime.datetime.now()
    dict_weekday={'昨天':today-timedelta(1),
                '前天':today-timedelta(2),
                '3天前':today-timedelta(3),
                '4天前':today-timedelta(4),
                '5天前':today-timedelta(5),
                '6天前':today-timedelta(6)}
    try:
        outfit_date=datetime.datetime.strptime(date_string,'%Y.%m/%d')
    except:
        if date_string in dict_weekday:
            outfit_date=dict_weekday[date_string]
        else:
            outfit_date=today
    return outfit_date 

def crawl_beautifulsoup(url):
    res = requests.get(url, headers=headers)  
    soup = BeautifulSoup(res.text, 'html.parser')
    return soup

def parse_item_images(tag_images):
    lst_item_images=[image.select_one('a img')['src'].replace('_70','_500') for image in tag_images[1:7]]
    return lst_item_images

def parse_item_match(tag_matches):
    lst_item_match=[]
    for match in tag_matches[1:7]:
        match_url='https://wear.tw'+match.select_one('p.img a')['href']
        match_image_url=match.select_one('p a img')['src'].replace('_276.jpg','_500.jpg')
        lst_item_match.append({'match_url':match_url, 'match_image_url':match_image_url})
    return lst_item_match

def parse_item_data(item_url,shop_url):
    soup_item=crawl_beautifulsoup(item_url)
    subtitle=soup_item.select_one('section#item_info h1').get_text() if shop_url != 'None' else 'None'

    images=soup_item.select('div#thumbnail ul li')
    lst_item_images=parse_item_images(images)
    
    matches=soup_item.select('section#coordinate ul li.like_mark')
    lst_item_match=parse_item_match(matches)
    return subtitle, lst_item_images, lst_item_match

def parse_match_data(items, non_acc):
    lst_match=[]
    for item in items: 
        reference_link=item.select_one('div.main p.btn a').get_text()
        shop_url, search_url, price='None', 'None','None'
        if '購買' in reference_link:
            shop_url=item.select_one('div.main p.btn_buy a')['href'] 
            price=item.select_one('div.sub a p.price').get_text()
        elif '搜尋' in reference_link:
            search_url=item.select_one('div.main p.btn_search a')['href']
        
        item_id=item.select_one('div.sub a')['href'].split('/')[-2]
        item_url='https://wear.tw'+item.select_one('div.sub a')['href']
        item_image=item.select_one('div.sub img')['src'].replace('d_125', 'd_500') 
        brand=item.select_one('div.main p.brand').get_text()
        name=item.select_one('div.main p.txt a').get_text()
        color=name.split('(')[1].split(')')[0].replace('系','')
        title=name.split('(')[0].strip().split('/')[0]
        category=gender if title in non_acc else 'accessories'
        subtitle, lst_item_images, lst_item_match=parse_item_data(item_url, shop_url)

        lst_match.append({'item_id':item_id,'item_url':item_url,'title':title,'subtitle':subtitle,\
                        'item_image_url':item_image,'lst_item_images':lst_item_images, ' lst_item_match': lst_item_match,\
                        'brand':brand, 'color':color,'category':category,'shop_url':shop_url, 'search_url':search_url, \
                        'price':price})
    return lst_match
    
def parse_outfit_data(kol_id, outfit_url, outfit_date,soup_outfit, non_acc):
    try:
        description=soup_outfit.select_one('p.content_txt').get_text()
    except:
        description='None'
    outfit_title=soup_outfit.select_one('section#coordinate_info h1').get_text()
    total_like=soup_outfit.select_one('div.subContainer div.btn_like span').get_text()
    total_comment=soup_outfit.select_one('div.subContainer div.btn_comment a').get_text()
    total_collect=soup_outfit.select_one('p.allBtn span').get_text()
    outfit_image=soup_outfit.select_one('div#coordinate_img img')['src']
    items=soup_outfit.select('section#item li')
    lst_match=parse_match_data(items, non_acc)

    data_outfit={'kol_id':kol_id,'outfit_url':outfit_url,'outfit_date':outfit_date, 'outfit_description':description,'outfit_title':outfit_title,\
        'total_like':total_like,'total_comment':total_comment,'total_collect':total_collect,'outfit_image_url':outfit_image,'lst_match':lst_match}
    return data_outfit

def parse_rating_like(outfit_url):
    like_url=outfit_url+'like/'
    like_soup=crawl_beautifulsoup(like_url)
    
    pages=like_soup.select('div#pager ul li')
    lst_page=[page.get_text() for page in pages]
    last_page=lst_page[-1]

    lst_like=[]
    for page in range(1,int(last_page)+1):
        like_url=outfit_url+'like/?pageno='+str(page)
        like_soup=crawl_beautifulsoup(like_url)
        
        likes=like_soup.select('div#user_list_2column li.list')
        for like in likes:
            uid=like.select_one('div.content li a')['href'].split('/')[-2]        
            lst_like.append(uid)
        time.sleep(2)
    return lst_like

def parse_rating_comment_latest(kol_id,soup_outfit):
    year_now=datetime.datetime.now().strftime('%Y')
    lst_latest_comment=soup_outfit.select('div.comment_container div.date_container')
    lst_comment=[]
    for daily_comment in lst_latest_comment:
        tag_comment_date=daily_comment.select_one('p.date').get_text().split('（')[0]
        comment_date=datetime.datetime.strptime(tag_comment_date,'%Y/%m/%d') if len(tag_comment_date)>5 else datetime.datetime.strptime(year_now+'/'+tag_comment_date,'%Y/%m/%d')
        comments=daily_comment.select('ul.reply_container li')
        for comment in comments:
            comment_uid=comment.select_one('span.userid a')['href'].split('/')[-2]
            if comment_uid!=kol_id:
                comment_text=comment.select_one('p.txt').get_text()
                lst_comment.append({"date":comment_date,"uid":comment_uid,"comment":comment_text})
    return lst_comment

def parse_rating_comment_history(outfit_url):
    outfit_id=outfit_url.split('/')[-2]
    url = "https://wear.tw/username/comment_list.json?id={}&comment_cnt=8&type=coordinate".format(outfit_id)
    headers_comment = {
        'User-Agent': MY_USER_AGENT4,
        'X-Requested-With': 'XMLHttpRequest',
        'Cookie': COOKIE
    }
    res = requests.get(url, headers=headers_comment)
    json_file=json.loads(res.text)
    
    lst_comment=[]
    for data in json_file[0]['comments']:
        comment_date=data['regist_date']
        for message in data['list']:
            if message['mycoordinate_flag'] == False:
                comment_uid=message['user_url'].split('/')[-2]
                comment_text=message['message']
                lst_comment.append({"date":comment_date,"uid":comment_uid,"comment":comment_text})
    return lst_comment

def check_new_outfit(kol_id,kol_latest_update_at):        
    kol_url='https://wear.tw/'+kol_id+'/'
    soup_kol=crawl_beautifulsoup(kol_url)
    
    #if outfit list page is not empty(get number of total pages)
    if soup_kol.select('div#pager ul li'):
        pages=int(soup_kol.select('div#pager ul li')[-1].get_text())

        lst_new_outfit=[]
        for page_num in range(1,pages+1):
            lst_outfit_url='https://wear.tw/'+kol['kol_id']+'/?pageno='+str(page_num)
            soup_kol_paging=crawl_beautifulsoup(lst_outfit_url)

            lst_outfit=soup_kol_paging.select('div#main_list ul li div.image')
            for outfit in lst_outfit:
                outfit_url='https://wear.tw'+outfit.select_one('div.image a.over')['href']
                date_string=outfit.select_one('p.show_dt').get_text()
                outfit_date=parse_datetime(date_string)
                
                # if outfit_date > latest_outfit_date for the kol (record in mongodb collection)
                if outfit_date> kol_latest_update_at:
                    lst_new_outfit.append({'outfit_url':outfit_url,'outfit_date':outfit_date})
        return lst_new_outfit


if __name__ == "__main__":
    t1=time.time()
    calculated_at=datetime.datetime.now()

    quantity_outfit=0
    quantity_like=0
    quantity_comment=0

    lst_kol=extract_mongodb_kol(gender)
    non_acc=get_non_acc()
    for kol in lst_kol: 
        kol_id=kol['kol_id']
        kol_latest_update_at= kol['latest_update_at']
        
        lst_new_outfit=check_new_outfit(kol_id, kol_latest_update_at)
        quantity_outfit += len(lst_new_outfit)
        try:
            for new_outfit in lst_new_outfit:
                outfit_url=new_outfit['outfit_url']
                outfit_date=new_outfit['outfit_date']
                soup_outfit = crawl_beautifulsoup(outfit_url)
                
                data_outfit=parse_outfit_data(kol_id, outfit_url, outfit_date,soup_outfit, non_acc)
                insert_mongodb_one_new_outfit(gender,outfit_url,data_outfit)
                time.sleep(random.randint(1,5))
                
                lst_like=parse_rating_like(outfit_url)
                lst_comment=parse_rating_comment_latest(kol_id,soup_outfit)                      
                if soup_outfit.select_one('p#history_comment'):
                    time.sleep(5)
                    lst_comment+=parse_rating_comment_history(outfit_url)
                insert_mongodb_one_new_rating(gender,outfit_url,lst_like, lst_comment,outfit_date)
                quantity_like += len(lst_like)
                quantity_comment += len(lst_comment)
                time.sleep(1)
            time.sleep(3)
        except:
            pass
    
    t2=time.time()
    time_consumption=t2-t1  
    insert_sql_etl_time_consumption(calculated_at, 'crawl_outfit', gender, time_consumption)
    insert_sql_etl_quantity(calculated_at, 'new_outfit', gender, quantity_outfit)
    insert_sql_etl_quantity(calculated_at, 'new_like', gender, quantity_like)
    insert_sql_etl_quantity(calculated_at, 'new_comment', gender, quantity_comment)