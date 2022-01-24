from model_mongodb import *
from model_sql import *
from datetime import date
from dateutil.relativedelta import relativedelta

if __name__ == "__main__":
    genders = ['women', 'men']
    for gender in genders:
        lst_max_outfit_date = extract_mongodb_kol_latest_update(gender)
        update_mongodb_kol_latest_update(gender, lst_max_outfit_date)
    
    latest_date = date.today()-relativedelta(day=+1)
    insert_marketing_funnel(latest_date)
