#coding=utf-8
from config import *

def extract_mongodb_distinct_kol(gender):
    collection_kol=collection_wearwomen if gender=='women' else collection_wearmen
    non_duplicate_kol=collection_kol.find().distinct('kol_id')
    lst_kol=[kol for kol in non_duplicate_kol]
    return lst_kol

def extract_mongodb_kol(gender):
    collection_kol=collection_wearwomen if gender=='women' else  collection_wearmen
    lst_kol=[kol for kol in collection_kol.find({})]
    return lst_kol

def extract_mongodb_new_outfit_by_kol(gender,kol_id,latest_update_at): 
    collection_outfit= collection_wearwomen_outfit if gender == 'women' else collection_wearmen_outfit
    collection_new_outfit_by_kol=collection_outfit.find({"kol_id":kol_id,'outfit_date': {"$gt":latest_update_at}})
    return collection_new_outfit_by_kol

def extract_mongodb_new_outfit_rating_by_kol(gender,kol_id,latest_update_at):
    collection_rating=collection_wearwomen_rating if gender == 'women' else collection_wearmen_rating
    collection_new_outfit_rating_by_kol=collection_rating.find({"outfit_url":{"$regex":kol_id},'outfit_date': {"$gt":latest_update_at}})
    return collection_new_outfit_rating_by_kol

def extract_mongodb_kol_latest_update(gender):
    collection_outfit= collection_wearwomen_outfit if gender == 'women' else collection_wearmen_outfit
    result=collection_outfit.aggregate([{"$group":{"_id":"$kol_id", "maxValue": {"$max":"$outfit_date"}}}])
    lst_max_outfit_date=[ max_outfit_date for max_outfit_date in result]
    return lst_max_outfit_date

def insert_mongodb_new_kol(gender, lst_new_kol):
    kol_collection=collection_wearwomen if gender=='women' else collection_wearmen
    kol_collection.insert_many(lst_new_kol)
    print("New Kols commited to MongoDB for {}/{} kols".format(gender,len(lst_new_kol)))

def insert_mongodb_one_new_outfit(gender,outfit_url,data_outfit):    
    outfit_collection=collection_wearwomen_outfit if gender=='women' else collection_wearmen_outfit
    outfit_collection.insert_one(data_outfit)
    print("New Outfit Data {} Commited to MongoDB".format(outfit_url))

def insert_mongodb_one_new_rating(gender,outfit_url,lst_like, lst_comment,outfit_date):
    data_rating={"outfit_url":outfit_url, "lst_like_uid":lst_like, "lst_comment":lst_comment, "outfit_date":outfit_date}
    rating_collection=collection_wearwomen_rating if gender=='women' else collection_wearmen_rating
    rating_collection.insert_one(data_rating)
    print("New Rating Data {} commited to MongoDB".format(outfit_url))
        
def update_mongodb_kol_latest_update(gender,lst_max_outfit_date): 
    collection_kol=collection_wearwomen if gender=='women' else collection_wearmen  
    for kol_data in lst_max_outfit_date:
        collection_kol.update_one({'kol_id': kol_data['_id']},{'$set': {'latest_update_at':kol_data['maxValue']}}, upsert=False)
        print("Update MongoDB Collection, {}".format(kol_data))
