#coding=utf-8
from config import *

def extract_sql_distinct_kol(gender):
    cursor=mysqldb.cursor() 
    sql="SELECT DISTINCT(kol_id) as kol_id FROM kol WHERE gender=%s"
    cursor.execute(sql,gender)
    lst_sql_kol=[ kol['kol_id'] for kol in cursor.fetchall()]
    return lst_sql_kol

def extract_sql_product_id():
    cursor=mysqldb.cursor() 
    sql="SELECT id, product_id from product WHERE source='wear' "
    cursor.execute(sql)
    lst_product_id_pk=cursor.fetchall()
    return lst_product_id_pk

def extract_sql_exist_match(outfit_id, product_id):
    cursor=mysqldb.cursor() 
    sql_query="SELECT * FROM match_item WHERE outfit_id=%s and product_id=%s"
    cursor.execute(sql_query, (outfit_id,product_id))
    check_match_data=cursor.fetchall()
    return check_match_data 

def extract_sql_exist_uid():
    cursor=mysqldb.cursor() 
    sql="SELECT uid from user"
    cursor.execute(sql)
    lst_exist_uid=[user['uid'] for user in cursor.fetchall()]
    return lst_exist_uid


def extract_sql_max_rating_id():
    cursor=mysqldb.cursor() 
    sql="SELECT MAX(id) as max_id FROM rating"
    cursor.execute(sql)
    max_rating_id=cursor.fetchone()

    last_rating_id=0
    if max_rating_id['max_id'] != None:
        last_rating_id=max_rating_id['max_id']
    return last_rating_id

def extract_sql_max_comment_id():
    cursor=mysqldb.cursor() 
    sql="SELECT MAX(id) as max_id FROM comment"
    cursor.execute(sql)
    max_comment_id=cursor.fetchone()

    last_comment_id=0
    if max_comment_id['max_id'] != None:
        last_comment_id=max_comment_id['max_id']
    return last_comment_id

def extract_sql_max_event_id():
    cursor=mysqldb.cursor() 
    sql="SELECT MAX(id) as max_id FROM event"
    cursor.execute(sql)
    max_event_id=cursor.fetchone()

    last_event_id=0
    if max_event_id['max_id'] != None:
        last_event_id=max_event_id['max_id']
    return last_event_id

def extract_sql_new_event_like(start_id,end_id):
    cursor=mysqldb.cursor()
    sql="SELECT id, uid, outfit_id FROM event WHERE event_type='like' and id between %s and %s"
    cursor.execute(sql,(start_id,end_id))
    lst_new_event_like=cursor.fetchall()
    return lst_new_event_like

def extract_sql_new_comment():
    cursor=mysqldb.cursor() 
    sql="SELECT uid, outfit_id, positive_sentiment_socre \
            FROM comment  \
            WHERE outfit_id not in (SELECT outfit_id  FROM rating GROUP BY outfit_id) \
            GROUP BY uid, outfit_id \
            HAVING MAX(positive_sentiment_socre)"
    
    cursor.execute(sql)
    lst_new_comment=cursor.fetchall()
    return lst_new_comment


def extract_sql_outfit_description(gender,period_3month_ago):
    cursor=mysqldb.cursor()  
    sql="SELECT outfit.outfit_description FROM outfit\
        JOIN kol\
        ON outfit.kol_id=kol.kol_id \
        WHERE kol.gender='{}' AND DATE(outfit.posted_at) > {} \
        and kol.kol_id not like '{}' and  kol.kol_id not like '{}' ".format(gender,period_3month_ago,'hm_official_women','hm_official_men')
    cursor.execute(sql)
    outfit_descriptions = cursor.fetchall()
    return outfit_descriptions

def extract_seasonal_outfit(season_now, year_now, gender):
    sql="SELECT outfit.outfit_id as outfit_id FROM outfit \
                JOIN kol ON outfit.kol_id=kol.kol_id \
                WHERE outfit.season = %s \
                and YEAR(outfit.posted_at)=%s \
                and kol.gender=%s \
                and outfit.total_likes > 280 "
    cursor=mysqldb.cursor() 
    cursor.execute(sql,(season_now, year_now, gender))
    tuple_seasonal_outfit=tuple([outfit['outfit_id'] for outfit in cursor.fetchall()])
    return tuple_seasonal_outfit

def extract_batch_seasonal_rating_data(tuple_seasonal_outfit, start_point, end_point):
    sql="SELECT uid,outfit_id,rating FROM rating \
          WHERE outfit_id in %s \
                and id between %s and %s \
          Group BY 1,2 \
          HAVING MAX(rating)"

    cursor=mysqldb.cursor() 
    cursor.execute(sql,(tuple_seasonal_outfit, start_point, end_point)) 
    batch_rating_dataset=cursor.fetchall()
    print("Number of data added is {}".format(len(batch_rating_dataset)))
    return batch_rating_dataset

def insert_sql_new_kol(gender,lst_new_kol): 
    cursor=mysqldb.cursor()    
    count_new_kol=len(lst_new_kol)
    if len(lst_new_kol)==0:
        print("NO updated kol data for ({}) commited to SQL!".format(gender))
    else:
        try:
            sql="INSERT INTO kol(kol_id,gender) \
                VALUES (%s, %s)"
            cursor.executemany(sql, lst_new_kol)
            mysqldb.commit()
            print("Dataset (#1:{})commited to SQL/kol!".format(lst_new_kol[0]))
            print("Wear New Kols commited to SQL for {}/{} kols".format(gender,count_new_kol))
        except: #in case duplicate primary key error: "insert_one" (insert one by one)
            for tuple_kol in lst_new_kol:
                try:
                    sql="INSERT INTO kol(kol_id,gender) \
                        VALUES (%s, %s)"
                    cursor.execute(sql, tuple_kol)
                    mysqldb.commit()
                    print("Dataset (#1:{})commited to SQL/kol!".format(tuple_kol))
                except:
                    print("Duplicate Primary Key Error for ({}) commited to SQL/kol!".format(tuple_kol))

def insert_sql_new_outfit(gender,kol_id, lst_new_outfit_by_kol):
    cursor=mysqldb.cursor()
    if len(lst_new_outfit_by_kol)==0: 
        print("NO updated outfit data for ({}/{}) commited to SQL!".format(gender,kol_id))
    else:
        try: 
            sql="INSERT INTO outfit(outfit_id, kol_id, posted_at, season, outfit_title, outfit_description, outfit_image,total_likes,total_weighted_likes) \
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
            cursor.executemany(sql, lst_new_outfit_by_kol)
            mysqldb.commit()
            print("Dataset (#1:{})commited to SQL/outfit!".format(lst_new_outfit_by_kol[0]))
            print("Wear New Outfits commited to SQL for {}/{}/{}".format(gender,kol_id,len(lst_new_outfit_by_kol)))

        except: #in case duplicate primary key error: "insert_one" (insert one by one)
            for tuple_outfit in lst_new_outfit_by_kol: 
                try:
                    sql="INSERT INTO outfit(outfit_id, kol_id, posted_at, season, outfit_title, outfit_description, outfit_image,total_likes,total_weighted_likes)\
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
                    cursor.execute(sql, tuple_outfit)
                    mysqldb.commit()
                    print("Dataset (#1:{})commited to SQL/outfit!".format(tuple_outfit[0]))
                except:
                    print("Duplicate Primary Key Error for ({}/{}/{}) commited to SQL/outfit!".format(gender,kol_id,tuple_outfit[0]))


def insert_sql_new_product(gender,kol_id,lst_new_product_by_kol):
    cursor=mysqldb.cursor()
    if len(lst_new_product_by_kol)==0:
        print("NO updated product data for ({}/{}) commited to SQL!".format(gender,kol_id))
    else:
        try:
            sql="INSERT INTO product(source,product_id, category, brand, product_title, color_id, price, shop_url, product_image_feature_url, product_image_match_url) \
                VALUES (%s,%s, %s, %s, %s, %s, %s, %s, %s, %s)"
            cursor.executemany(sql, lst_new_product_by_kol)
            mysqldb.commit()
            print("Dataset (#1:{})commited to SQL/product!".format(lst_new_product_by_kol[0]))
            print("Wear New Products commited to SQL for {}/{}/{}".format(gender,kol_id,len(lst_new_product_by_kol)))
        except: #in case duplicate primary key error: "insert_one" (insert one by one)
            for tuple_product in lst_new_product_by_kol:
                try:
                    sql="INSERT INTO product(source,product_id, category, brand, product_title, color_id, price, shop_url, product_image_feature_url, product_image_match_url) \
                        VALUES (%s,%s, %s, %s, %s, %s, %s, %s, %s, %s)"
                    cursor.execute(sql, tuple_product)
                    mysqldb.commit()
                    print("Dataset (#1:{})commited to SQL/product!".format(tuple_product[1]))
                except:
                    print("Duplicate Primary Key Error for ({}/{}/{}) commited to SQL/product!".format(gender,kol_id,tuple_product[1]))


def insert_sql_new_match(gender,kol_id,lst_new_match):
    cursor=mysqldb.cursor()
    if len(lst_new_match)==0 or lst_new_match==None:
        print("NO updated match data for ({}/{}) commited to SQL!".format(gender,kol_id))

    else: # avoid duplicate
        for tuple_match in lst_new_match:
            check_match_data=extract_sql_exist_match(tuple_match[0],tuple_match[1])
            if len(check_match_data) ==0:
                try: 
                    sql_insert="INSERT INTO match_item(outfit_id,product_id) \
                                 VALUES (%s, %s)"
                        
                    cursor.execute(sql_insert, tuple_match)
                    mysqldb.commit()
                    print("Dataset (#1:{})commited to SQL/match_item!".format(tuple_match))
                except: 
                    print("Error: NO updated match data for ({}/{}/{}) commited to SQL!".format(gender,kol_id,tuple_match))
            else:
                print("NO updated match data for ({}/{}/{}) commited to SQL!".format(gender,kol_id,tuple_match)) 


def insert_sql_new_user(lst_new_user):
    cursor=mysqldb.cursor() 
    sql="INSERT INTO user(uid, gender, email,password,source,picture, access_token, access_expired,login_at) \
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
    cursor.executemany(sql, lst_new_user)
    mysqldb.commit()
    print("Dataset (#1:{})commited to SQL/user!".format(lst_new_user[:2]))

def insert_sql_new_event(lst_new_event):
    try: 
        cursor=mysqldb.cursor() 
        sql="INSERT INTO event(uid, outfit_id, event_type,time) \
            VALUES (%s, %s, %s, %s)"
        cursor.executemany(sql, lst_new_event)
        mysqldb.commit()
        print("Dataset (#1:{})commited to SQL/event!".format(lst_new_event[:2]))
    except:
        for tuple_event in lst_new_event:
            try:
                cursor=mysqldb.cursor() 
                sql="INSERT INTO events(uid, outfit_id, event_type,time) \
                    VALUES (%s, %s, %s, %s)"
                cursor.execute(sql, tuple_event)
                mysqldb.commit()
                print("Dataset ({})commited to SQL/event!".format(tuple_event))
            except:
                print("Error: new event data for ({}) did not commit to SQL!".format(tuple_event)) 


def insert_sql_new_comment(lst_new_comment):
    try:
        cursor=mysqldb.cursor() 
        sql="INSERT INTO comment(uid, outfit_id, comment, positive_sentiment_socre, commented_at) \
            VALUES (%s, %s, %s, %s, %s)"
        cursor.executemany(sql, lst_new_comment)
        mysqldb.commit()
        print("Dataset (#1:{})commited to SQL/comment!".format(lst_new_comment[:2]))
    except:
        for tuple_comment in lst_new_comment:
            try: 
                cursor=mysqldb.cursor() 
                sql="INSERT INTO comment(uid, outfit_id, comment, positive_sentiment_socre, commented_at) \
                    VALUES (%s, %s, %s, %s, %s)"
                cursor.execute(sql, tuple_comment)
                mysqldb.commit()
                print("Dataset (#1:{})commited to SQL/comment!".format(tuple_comment))
            except:
                print("Error: new comment data for ({}) did not commit to SQL!".format(tuple_comment)) 



def insert_sql_new_rating_like(lst_new_rating_like):
    cursor=mysqldb.cursor()
    sql="INSERT INTO rating (uid, outfit_id, rating) \
        VALUES(%s, %s, %s)" 
    cursor.executemany(sql, lst_new_rating_like)
    mysqldb.commit()
    print("Dataset (from#{})commited to SQL rating/like!".format(lst_new_rating_like[:1]))


def insert_sql_new_rating_comment(lst_new_rating_comment):
    cursor=mysqldb.cursor() 
    sql="INSERT INTO rating (uid, outfit_id, rating)\
            VALUES (%s, %s, %s);"
    cursor.executemany(sql,lst_new_rating_comment)
    mysqldb.commit()
    print("Dataset (#1:{})commited to SQL rating/comment!".format(lst_new_rating_comment[:5]))


def insert_sql_wordcloud(lst_words):
    cursor=mysqldb.cursor()  
    sql="INSERT INTO wordcloud(calculated_at,gender, word_ch, word_jp, frequency) \
        VALUES (%s, %s, %s, %s, %s)"
    cursor=mysqldb.cursor() 
    cursor.executemany(sql, lst_words)
    mysqldb.commit()
    print("Dataset (#1:{}/{})commited to SQL/wordcloud!".format(lst_words[0][0],lst_words[0]))

def insert_sql_knn_recommendation(lst_seasonal_recomm):
    sql="INSERT INTO recommendation(outfit1,outfit2, similar_score, calculated_at)\
        VALUES (%s,%s,%s, %s) "
    cursor=mysqldb.cursor() 
    cursor.executemany(sql, lst_seasonal_recomm)
    mysqldb.commit()
    print("Recommendation Dataset (data1#{})commited to SQL/recomm!".format(lst_seasonal_recomm[0]))