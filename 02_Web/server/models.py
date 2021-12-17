from server import db_connection
import datetime


def get_user_by_id(uid):
    db = db_connection()
    cursor = db.cursor()
    sql = "SELECT * FROM user WHERE uid=%s"
    cursor.execute(sql, uid)
    user = cursor.fetchone()
    return user


def get_user_by_email(email):
    db = db_connection()
    cursor = db.cursor()
    sql = "SELECT * FROM user WHERE email=%s"
    cursor.execute(sql, email)
    user = cursor.fetchone()
    return user


def create_user(uid, gender, email, hashed_password, source, picture, access_token, access_expired, login_at):
    db = db_connection()
    try:
        cursor = db.cursor()
        sql = "INSERT INTO user (uid, gender, email, password, source, picture, access_token, access_expired, login_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(sql, (uid, gender, email, hashed_password, source, picture, access_token, access_expired, login_at))
        db.commit()
        return 'success'
    except Exception as e:
        print(e)
        return None


def save_access_token(access_token, email):
    db = db_connection()
    try:
        cursor = db.cursor()
        sql = "UPDATE user SET access_token=%s WHERE email=%s"
        cursor.execute(sql, (access_token, email))
        db.commit()
        return 'success'
    except Exception as e:
        print(e)
        return None


def get_total_wish_outfit(time_period, uid):
    db = db_connection()
    cursor = db.cursor()
    sql = "SELECT count(*) as total_outfit FROM outfit \
            WHERE posted_at > %s and outfit_id in (SELECT outfit_id FROM event WHERE uid=%s and event_type=4)"
    cursor.execute(sql, (time_period, uid))
    total_outfit = cursor.fetchone()['total_outfit']
    return total_outfit


def get_populer_recomm(season, gender, uid):
    db = db_connection()
    cursor = db.cursor()
    sql = "SELECT outfit.outfit_id as outfit_id, outfit.outfit_image as outfit_image FROM outfit \
            JOIN kol ON outfit.kol_id=kol.kol_id \
            WHERE outfit.season=%s and kol.gender=%s and outfit.outfit_id not in (SELECT outfit_id FROM event WHERE uid=%s) \
            GROUP BY outfit.outfit_id \
            ORDER BY outfit.total_weighted_likes DESC LIMIT 6"
    cursor.execute(sql, (season, gender, uid))
    lst_outfit_recomm = cursor.fetchall()
    return lst_outfit_recomm


def get_explore_recomm(uid, gender, season):
    db = db_connection()
    cursor = db.cursor()
    sql = "SELECT outfit.outfit_id, outfit.outfit_image \
            FROM recommendation_test \
            JOIN outfit ON recommendation_test.outfit2=outfit.outfit_id \
            JOIN kol ON outfit.kol_id=kol.kol_id \
            WHERE recommendation_test.outfit1 in (SELECT outfit_id FROM (SELECT outfit_id FROM event WHERE uid=%s and event_type=%s ORDER BY time DESC LIMIT 6) T) \
                    and recommendation_test.outfit2 not in (SELECT outfit_id FROM event WHERE uid=%s) \
                    and kol.gender=%s and outfit.season=%s \
            GROUP BY recommendation_test.outfit2 \
            ORDER BY recommendation_test.similar_score LIMIT 6"
    cursor.execute(sql, (uid, 4, uid, gender, season))
    lst_explore_recomm = cursor.fetchall()
    return lst_explore_recomm


def tracking_behavior_viewed(lst_outfit, uid):
    db = db_connection()
    # event_type: view=-1, like=1, comment=2, strong_positive_comment=3, collect/wish=4, shop=5
    viewed_at = datetime.datetime.now()
    lst_outfit_viewed = list()
    for outfit in lst_outfit:
        tuple_viewed = (uid, outfit['outfit_id'], -1, viewed_at)
        lst_outfit_viewed.append(tuple_viewed)
    cursor = db.cursor()
    sql = "INSERT INTO event (uid, outfit_id, event_type, time) \
             VALUES (%s, %s, %s, %s)"
    cursor.executemany(sql, (lst_outfit_viewed))
    db.commit()
    print("Tracking View Event for user #{} sucessfully!".format(uid))


def get_trendy_wordcloud(gender):
    db = db_connection()
    cursor = db.cursor()
    sql = "SELECT calculated_at, word_ch, word_jp, frequency FROM wordcloud \
            WHERE gender=%s \
            ORDER BY calculated_at DESC, frequency DESC LIMIT 30"
    cursor.execute(sql, gender)
    words = cursor.fetchall()
    return words


def get_wish_outfit(uid):
    db = db_connection()
    cursor = db.cursor()
    sql = "SELECT outfit_id FROM event \
            WHERE uid=%s and event_type=4"
    cursor.execute(sql, uid)
    lst_wish_outfits = [outfit['outfit_id'] for outfit in cursor.fetchall()]
    return lst_wish_outfits


def get_wordcloud_search_outfit(keyword, season, gender):
    db = db_connection()
    cursor = db.cursor()
    sql = "SELECT outfit.outfit_id as outfit_id, outfit.outfit_image as outfit_image FROM outfit \
            JOIN kol on outfit.kol_id=kol.kol_id \
            WHERE outfit.outfit_description RLIKE %s and outfit.season=%s and kol.gender=%s \
            and outfit.total_weighted_likes > %s \
            GROUP BY kol.kol_id \
            ORDER BY outfit.total_weighted_likes DESC LIMIT 15"
    cursor.execute(sql, (keyword, season, gender, 150))
    lst_wordcloud_search_outfits = cursor.fetchall()
    return lst_wordcloud_search_outfits


def tracking_behavior_addevent(uid, outfit_id, event_type):
    db = db_connection()
    event_at = datetime.datetime.now()
    cursor = db.cursor()
    
    if event_type == 'wish':
        rating = 4
    elif event_type == 'shop':
        rating = 5

    sql = "INSERT INTO event (uid, outfit_id, event_type, time) \
            VALUES (%s, %s, %s, %s)"
    cursor.execute(sql, (uid, outfit_id, rating, event_at))
    db.commit()
    print("Add {} to {}'s event list({})  sucessfully!".format(outfit_id, uid, event_type))


def tracking_behavior_removewish(outfit_id, uid):
    db = db_connection()
    cursor = db.cursor()
    sql_removewish = "UPDATE event \
                    SET event_type=0 \
                    WHERE outfit_id=%s and uid=%s and event_type=4"
    cursor.execute(sql_removewish, (outfit_id, uid))
    db.commit()
    print("Remove {} from {}'s wishlist sucessfully!".format(outfit_id, uid))


def get_outfit_info(outfit_id):
    db = db_connection()
    cursor = db.cursor()
    sql = "SELECT outfit_id, outfit_image \
            FROM outfit \
            WHERE outfit_id=%s"
    cursor.execute(sql, outfit_id)
    outfit = cursor.fetchone()
    return outfit


def get_product_info(outfit_id):
    db = db_connection()
    cursor = db.cursor()
    sql = "SELECT product.product_id as product_id, product.brand as brand, product.category as category, product.price as price, \
            product.shop_url as shop_url, product.product_image_feature_url as product_image \
            FROM product \
            JOIN match_item on product.id=match_item.product_id \
            WHERE match_item.outfit_id={} and product.brand not like '{}' ".format(outfit_id, '%nstagram%')
    cursor.execute(sql)
    products = cursor.fetchall()
    return products


def get_wish_outfit_by_page(uid, per_page, offset):
    db = db_connection()
    cursor = db.cursor()
    sql = "SELECT outfit.outfit_id as outfit_id, outfit.outfit_image as outfit_image FROM outfit \
            JOIN event ON outfit.outfit_id=event.outfit_id \
            WHERE event.uid=%s and event.event_type=%s \
            GROUP BY 1 \
            ORDER BY event.time DESC LIMIT %s OFFSET %s"
    cursor.execute(sql, (uid, 4, per_page, offset))
    outfits = cursor.fetchall()
    return outfits


def get_colors():
    db = db_connection()
    cursor = db.cursor()
    sql = "SELECT name FROM color where name not like '%金%' and  name not like '%銀%' "
    cursor.execute(sql)
    colors = cursor.fetchall()[:-1]
    return colors


def get_categories(gender):
    db = db_connection()
    cursor = db.cursor()
    sql = "SELECT name, name_ch FROM category"
    cursor.execute(sql)

    categories = list()
    if gender == 'women':
        categories = [{'namech': category['name_ch'], 'name':category['name']} for category in cursor.fetchall()[1:]]
    elif gender == 'men':
        categories = [{'namech': category['name_ch'], 'name':category['name']} for category in cursor.fetchall()[1:] if category['name_ch'] not in ['洋裝', '裙子']]
    return categories


def search_product_wear(season, gender, category, color):
    db = db_connection()
    search_category = "and product.category='{}'".format(category) if category else ''
    search_color = "and product.color_id in (SELECT id FROM color WHERE name='{}')".format(color) if color else ''

    cursor = db.cursor()
    sql = "SELECT outfit.outfit_id as outfit_id, outfit.outfit_image as outfit_image, \
            product.brand as brand, product.price as price, product.shop_url as shop_url \
            FROM outfit \
            JOIN kol on outfit.kol_id=kol.kol_id \
            JOIN match_item on outfit.outfit_id=match_item.outfit_id \
            JOIN product on match_item.product_id=product.id \
            WHERE outfit.season='{}' \
                and kol.gender='{}' \
                {} {} \
                and product.source='wear' \
            GROUP BY kol.kol_id \
            ORDER BY outfit.total_weighted_likes DESC LIMIT 8".format(season, gender, search_category, search_color)
    cursor.execute(sql)
    outfits = cursor.fetchall()
    lst_wear_outfits = list()
    for idx, outfit in enumerate(outfits):
        outfit_info = dict(outfit, index=str(idx+1))
        lst_wear_outfits.append(outfit_info)
    return lst_wear_outfits


def search_product_hm(hm_kol_id, category, color, count_wear_outfits):
    db = db_connection()
    search_category = "and product.category='{}'".format(category) if category else ''
    search_color = "and product.color_id in (SELECT id FROM color WHERE name='{}')".format(color) if color else ''

    cursor = db.cursor()
    sql = "SELECT outfit.outfit_id as outfit_id, outfit.outfit_image as outfit_image, outfit.outfit_description, outfit.outfit_title, \
            product.brand as brand, product.price as price, product.shop_url as shop_url \
            FROM outfit \
            JOIN match_item on outfit.outfit_id=match_item.outfit_id \
            JOIN product on product.id=match_item.product_id \
            WHERE outfit.kol_id='{}' \
                {} {} \
                and outfit.outfit_description not like '%四角褲%' \
                and outfit.outfit_title not like '%內褲%' \
                LIMIT 12".format(hm_kol_id, search_category, search_color)

    cursor.execute(sql)
    outfits = cursor.fetchall()
    lst_hm_outfits = list()
    for idx, outfit in enumerate(outfits):
        outfit_info = dict(outfit, index=str(idx+1+count_wear_outfits))
        lst_hm_outfits.append(outfit_info)
    return lst_hm_outfits


def get_category_ch_name(category):
    db = db_connection()
    cursor = db.cursor()
    sql = "SELECT name_ch FROM category WHERE name=%s"
    cursor.execute(sql, category)
    category_ch = cursor.fetchone()['name_ch']
    return category_ch


def get_etl_latest_time(date, etl_job):
    db = db_connection()
    cursor = db.cursor()
    if etl_job =='crawl_outfit':
        sql = "SELECT SUM(CASE WHEN gender='women' THEN time_consumption/3600 END) AS women, \
                SUM(CASE WHEN gender='men' THEN time_consumption/3600 END) AS men \
                FROM etl_time_consumption \
                WHERE etl_job=%s and DATE(calculated_at)=%s"  
    else: 
        sql = "SELECT SUM(CASE WHEN gender='women' THEN time_consumption END) AS women, \
                SUM(CASE WHEN gender='men' THEN time_consumption END) AS men \
                FROM etl_time_consumption \
                WHERE etl_job=%s and DATE(calculated_at)=%s"
    cursor.execute(sql, (etl_job, date))
    time_consumption = cursor.fetchone()
    return time_consumption


def get_etl_quantity(date, item):
    db = db_connection()
    cursor = db.cursor()
    sql = "SELECT SUM(CASE WHEN gender='women' THEN new_quantity END) AS women, \
            SUM(CASE WHEN gender='men' THEN new_quantity END) AS men \
            FROM etl_quantity \
            WHERE item=%s and DATE(calculated_at)=%s"
    cursor.execute(sql, (item, date))
    quantity = cursor.fetchone()
    return quantity


def get_marketing_funnel(date):
    db = db_connection()
    cursor = db.cursor()
    sql = "SELECT * FROM marketing_funnel WHERE date=%s"
    cursor.execute(sql, date)
    marketing_funnel = cursor.fetchone()
    return marketing_funnel
