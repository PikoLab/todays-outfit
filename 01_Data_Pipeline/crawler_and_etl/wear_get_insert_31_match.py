# coding=utf-8
from model_sql import *
from model_mongodb import *
from collections import defaultdict


def check_dictionary_product_id(lst_product_id_pk):
    dict_id = defaultdict()
    for pair_id in lst_product_id_pk:
        dict_id[pair_id['product_id']] = pair_id['id']
    return dict_id


def check_new_match_by_kol(collection_new_outfit_by_kol, dict_id):
    lst_new_match = []
    for outfit in collection_new_outfit_by_kol:
        for item in outfit['lst_match']:
            try:
                outfit_id = outfit['outfit_url'].split('/')[-2]
                product_id = dict_id[int(item['item_id'])]
                tuple_match = (outfit_id, product_id)
                lst_new_match.append(tuple_match)
            except:
                continue
    return lst_new_match


if __name__ == "__main__":
    genders = ['women', 'men']
    for gender in genders:
        lst_mongo_kol = extract_mongodb_kol(gender)
        for kol in lst_mongo_kol:
            kol_id = kol['kol_id']
            latest_update_at = kol['latest_update_at']
            collection_new_outfit_by_kol = extract_mongodb_new_outfit_by_kol(gender, kol_id, latest_update_at)

            lst_product_id_pk = extract_sql_product_id()
            dict_id = check_dictionary_product_id(lst_product_id_pk)
            lst_new_match = check_new_match_by_kol(collection_new_outfit_by_kol, dict_id)
            insert_sql_new_match(gender, kol['kol_id'], lst_new_match)
