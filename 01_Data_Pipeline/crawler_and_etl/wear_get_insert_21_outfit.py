#coding=utf-8
from model_sql import *
from model_mongodb import *
from datetime import datetime
import datetime
from utils.utils import get_season

def check_new_outfit_by_kol_info(collection_new_outfit_by_kol):
    lst_new_outfit_by_kol=[]
    for outfit in collection_new_outfit_by_kol:
        outfit_id=outfit['outfit_url'].split('/')[-2]
        kol_id=outfit['kol_id']
        posted_at=outfit['outfit_date']
        season=get_season(posted_at.date())
        outfit_title=outfit['outfit_title']
        outfit_description=outfit['outfit_description']
        outfit_image='https:'+outfit['outfit_image_url']
        posted_year=posted_at.year
        year_now = datetime.datetime.now().year
        total_likes=int(outfit['total_like']) 
        total_weighted_likes= total_likes  if posted_year >= year_now else total_likes//3
        tuple_outfit=(outfit_id, kol_id, posted_at, season, outfit_title, outfit_description, outfit_image,total_likes,total_weighted_likes)
        lst_new_outfit_by_kol.append(tuple_outfit)  
    return lst_new_outfit_by_kol

if __name__ == "__main__":
    genders=['women','men']
    for gender in genders:
        lst_mongodb_kol=extract_mongodb_kol(gender)
        for kol in lst_mongodb_kol:
            kol_id=kol['kol_id']
            latest_update_at=kol['latest_update_at']
            collection_new_outfit_by_kol=extract_mongodb_new_outfit_by_kol(gender,kol_id, latest_update_at )
        
            lst_new_outfit_by_kol=check_new_outfit_by_kol_info(collection_new_outfit_by_kol)
            insert_sql_new_outfit(gender,kol['kol_id'], lst_new_outfit_by_kol)