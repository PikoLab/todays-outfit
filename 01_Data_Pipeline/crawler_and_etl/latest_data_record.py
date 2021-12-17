from model_mongodb import *


if __name__ == "__main__":
    genders = ['women', 'men']
    for gender in genders:
        lst_max_outfit_date = extract_mongodb_kol_latest_update(gender)
        update_mongodb_kol_latest_update(gender, lst_max_outfit_date)
