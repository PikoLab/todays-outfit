# coding=utf-8
from model_sql import *
from model_mongodb import *


def check_new_kol(gender, lst_mongo_kol, lst_sql_kol):
    lst_new_kol = list()
    for kol_id in lst_mongo_kol:
        if kol_id not in lst_sql_kol:
            lst_new_kol.append((kol_id, gender))
    return lst_new_kol


if __name__ == "__main__":
    genders = ['women', 'men']
    for gender in genders:
        lst_mongo_kol = extract_mongodb_distinct_kol(gender)
        lst_sql_kol = extract_sql_distinct_kol(gender)
        lst_new_kol = check_new_kol(gender, lst_mongo_kol, lst_sql_kol)
        insert_sql_new_kol(gender, lst_new_kol)
