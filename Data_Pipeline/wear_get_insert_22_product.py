#coding=utf-8
import json
from model_sql import *
from model_mongodb import *

def get_wear_color(color):
    with open('./utils/colors.json') as f:
         dict_color= json.load(f)
    color_id=dict_color[color]
    return color_id

def get_wear_category(product):
    with open('./utils/non_acc_category.json') as f:
        non_acc_category = json.load(f)
    for key, lst_product in non_acc_category.items():
        if product in lst_product:
            category=key 
            return category
    category='accessories'
    return category

def check_new_product_by_kol(lst_exist_pid,collection_new_outfit_by_kol):
    lst_new_product_by_kol=[]
    for outfit in collection_new_outfit_by_kol:
        for item in outfit['lst_match']:
            if item['item_id'] not in lst_exist_pid:
                source='wear'
                product_id=item['item_id']
                category=get_wear_category(item['title'])
                brand=item['brand']
                product_title=item['subtitle']
                color_id=get_wear_color(item['color'])
                price=int(int(item['price'].replace('JP¥','').replace('$','').replace(',',''))/4//100*100) if (item['price']!='None') and (item['price']!='') and ('SGD' not in item['price']) else 0  
                shop_url=item['shop_url'] if item['shop_url'] !='None' else item['search_url']
                product_image_feature_url='https:'+item['item_image_url']
                if item[' lst_item_match']:
                    product_image_match_url= ['https:'+detail['match_image_url'] for detail in item[' lst_item_match']][0]
                else: 
                    product_image_match_url='None'
                tuple_item=(source,product_id, category, brand, product_title, color_id, price, shop_url, product_image_feature_url,product_image_match_url)
                lst_exist_pid.append(product_id)
                lst_new_product_by_kol.append(tuple_item)
            else:
                continue
    return lst_new_product_by_kol


if __name__ == "__main__":
    genders=['women','men']
    for gender in genders:
        lst_mongo_kol=extract_mongodb_kol(gender)
        for kol in lst_mongo_kol:
            kol_id=kol['kol_id']
            latest_update_at=kol['latest_update_at']
            collection_new_outfit_by_kol=extract_mongodb_new_outfit_by_kol(gender,kol_id, latest_update_at)
                        
            lst_exist_pid=[product['product_id'] for product in extract_sql_product_id()]
            lst_new_product_by_kol=check_new_product_by_kol(lst_exist_pid,collection_new_outfit_by_kol)
            insert_sql_new_product(gender,kol['kol_id'],lst_new_product_by_kol)

