from model_sql import *
from model_mongodb import *
import datetime
from asari.api import Sonar  

def analysis_sentiment_positive_power(data):
    sonar = Sonar()
    info = sonar.ping(data)
    positive_vector = info["classes"][1]["confidence"]
    return positive_vector

def check_new_user_event_comment(gender,lst_exist_uid, collection_new_outfit_rating_by_kol):
    lst_new_user=[]
    lst_new_event=[]
    lst_new_comment=[]
    for rating in collection_new_outfit_rating_by_kol: 
        outfit_id=rating['outfit_url'].split('/')[-2]
   
        for like in rating['lst_like_uid']:
            rating_time=datetime.datetime.strptime('2000.1/1', '%Y.%m/%d')
            tuple_event=(like, outfit_id, 'like',rating_time)
            lst_new_event.append(tuple_event)
            if like not in lst_exist_uid:
                lst_exist_uid.append(like)
                email='wear_{}@gmail.com'.format(like)
                password='wear'
                source='wear'
                picture=''
                access_token=''
                access_expired=3600
                login_at=datetime.datetime.strptime('20000101', '%Y%m%d')
                tuple_user=(like, gender, email,password,source,picture, access_token, access_expired,login_at)
                lst_new_user.append(tuple_user)

        for comment in rating['lst_comment']:
            try:
                comment_time=comment['date']
            except:
                try:
                    comment_time=datetime.datetime.strptime(comment['date'], '%Y/%m/%d')
                except:
                    comment_time=datetime.datetime.strptime(comment['date'], '%Y%m%d')
            finally:
                tuple_event=(comment['uid'], outfit_id, 'comment',comment_time)
                lst_new_event.append(tuple_event)
            
            positive_score=analysis_sentiment_positive_power(comment['comment'])
            tuple_comment=(comment['uid'], outfit_id,comment['comment'],positive_score, comment_time)
            lst_new_comment.append(tuple_comment)
            if comment['uid'] not in lst_exist_uid:
                lst_exist_uid.append(comment['uid'])
                email='wear_{}@gmail.com'.format(comment['uid'])
                password='wear'
                source='wear'
                picture=''
                access_token=''
                access_expired=3600
                login_at=datetime.datetime.strptime('20000101', '%Y%m%d')
                tuple_user=(comment['uid'], gender, email,password,source,picture, access_token, access_expired,login_at)
                lst_new_user.append(tuple_user)
    return lst_new_user, lst_new_event, lst_new_comment

if __name__ == "__main__":
    genders=['women','men']
    for gender in genders:
        lst_mongodb_kol=extract_mongodb_kol(gender)
        for kol in lst_mongodb_kol:
            kol_id=kol['kol_id']
            latest_update_at=kol['latest_update_at']
            collection_new_outfit_rating_by_kol=extract_mongodb_new_outfit_rating_by_kol(gender,kol_id,latest_update_at)

            lst_exist_uid=extract_sql_exist_uid()
            lst_new_user, lst_new_event, lst_new_comment=check_new_user_event_comment(gender,lst_exist_uid, collection_new_outfit_rating_by_kol)

            insert_sql_new_user(lst_new_user)
            insert_sql_new_event(lst_new_event)
            insert_sql_new_comment(lst_new_comment)
        
