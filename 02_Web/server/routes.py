from flask import render_template, redirect, url_for, flash, session, request, make_response
from server import app, bcrypt
from server.models import *
from config import *
from server.forms import RegistrationForm, LoginForm
import datetime
from datetime import date, timedelta
import jwt
from dateutil.relativedelta import relativedelta
from flask_restful import Resource
import json
from utils import get_season
import time
import math

# plotly
import pandas as pd
import plotly
import plotly.express as px

access_token_expired_time = 3600


def check_valid_token():
    token = session.get('access_token')
    if not token:
        return {'result': 'fail', 'error_message': 'No Token. Please Login Again!'}
    else:
        try:
            decode_token = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            uid = decode_token['sub']
        except jwt.exceptions.InvalidSignatureError:
            return {'result': 'fail', 'error_message': 'Signature verification failed. Please login again!'}
        except jwt.exceptions.ExpiredSignatureError:
            return {'result': 'fail', 'error_message': 'Signature has expired. Please Login Again!'}
        except:
            return {'result': 'fail', 'error_message': 'Token is Invalid. Please Login Again!'}
        else:
            current_user = get_user_by_id(uid)
            return {'result': 'success', 'current_user': current_user}


def create_access_token(uid, access_expired):
    try:
        payload = {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=access_expired),
            'iat': datetime.datetime.utcnow(),
            'sub': uid
        }
        access_token = jwt.encode(payload, app.config.get('SECRET_KEY'), algorithm='HS256')
        return {'result': 'success', 'access_token': access_token}
    except Exception as e:
        print(e)
        return {'result': 'fail', 'error_message': 'Server Error! Please try again!'}


def create_session(dict_session):
    for key, value in dict_session.items():
        session[key] = value


def _check_login_auth(email, password):
    user = get_user_by_email(email)
    uid = user['uid'] if user else None
    gender = user['gender'] if user else None
    hashed_password = user['password'] if user else None
    valid = bcrypt.check_password_hash(hashed_password, password) if hashed_password != None else False
    return {'uid': uid, 'gender': gender, 'valid': valid}


def create_graph(data_source, title):
    gender = ['women', 'men']
    y_axis = [data_source['women'], data_source['men']]
    data = dict(gender=gender, quantity=y_axis)
    figure_name = px.bar(data, x='gender', y='quantity', title=title)
    graphJSON = json.dumps(figure_name, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON


class Home(Resource):
    def get(self):
        return redirect(url_for('wordcloud'))


class Register(Resource):
    def get(self):
        form = RegistrationForm()
        return make_response(render_template("register.html", form=form), 200)

    def post(self):
        form = RegistrationForm()
        if form.validate_on_submit():
            gender = form.gender.data
            uid = form.uid.data
            email = form.email.data
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            picture = "default.png"
            source = 'native'
            login_at = datetime.datetime.now()

            result_new_token = create_access_token(uid, access_token_expired_time)
            if result_new_token['result'] == 'fail':
                error_message = result_new_token['error_message']
                flash(error_message, 'danger')
                return make_response(render_template("register.html", form=form), 200)

            access_token = result_new_token['access_token']
            result_new_user = create_user(uid, gender, email, hashed_password,source, picture, access_token, access_token_expired_time, login_at)
            if result_new_user == 'success':
                season = get_season(date.today())
                create_session({'access_token': access_token, 'gender': gender, 'season': season})
                return redirect(url_for("wordcloud"))
        else:
            return make_response(render_template("register.html", form=form), 200)


class Login(Resource):
    def get(self):
        form = LoginForm()
        return make_response(render_template("login.html", form=form), 200)

    def post(self):
        form = LoginForm()
        if form.validate_on_submit():
            email = form.email.data
            password = form.password.data
            user = _check_login_auth(email, password)
            if user['uid'] and user['valid']:
                result_new_token = create_access_token(user['uid'], access_token_expired_time)
                if result_new_token['result'] == 'fail':
                    error_message = result_new_token['error_message']
                    flash(error_message, 'danger')
                    return make_response(render_template("login.html", form=form), 200)

                new_token = result_new_token['access_token']
                if save_access_token(new_token, email) == 'success':
                    season = get_season(date.today())
                    create_session({'access_token': new_token, 'gender': user['gender'], 'season': season})
                    return redirect(url_for("wordcloud"))
            else:
                flash(f'Fail to login! Please check your email address and password.', 'danger')
                return make_response(render_template("login.html", form=form), 200)
        else:
            flash(f'Fail to login! Please check your email address and password.', 'danger')
            return make_response(render_template("login.html", form=form), 200)


class Wordcloud(Resource):
    def get(self):
        check_token = check_valid_token()
        if check_token['result'] == 'fail':
            gender = 'women'
            words = get_trendy_wordcloud(gender)
            words_json = [{'text': word['word_ch'], 'weight': word['frequency'], 'link': OFFICIAL_URL +
                           '/wordcloud/search?keyword='+word['word_jp']+'&keywordch='+word['word_ch']} for word in words]
            return make_response(render_template('wordcloud.html', words_json=words_json), 200)

        gender = check_token['current_user']['gender']
        words = get_trendy_wordcloud(gender)
        words_json = [{'text': word['word_ch'], 'weight': word['frequency'], 'link': OFFICIAL_URL +
                       '/wordcloud/search?keyword='+word['word_jp']+'&keywordch='+word['word_ch']} for word in words]
        return make_response(render_template('wordcloud.html', words_json=words_json), 200)


class Explore(Resource):
    def get(self):
        t1 = time.time()
        check_token = check_valid_token()
        if check_token['result'] == 'fail':
            season = get_season(date.today())
            lst_outfits = get_populer_recomm(season, 'women', 'demowomen')
            return make_response(render_template('recommendation.html', outfits=lst_outfits), 200)

        uid = check_token['current_user']['uid']
        gender = check_token['current_user']['gender']
        season = session.get('season')
        period_3month_ago = date.today() - relativedelta(months=+ 3)
        total_wish_outfit = get_total_wish_outfit(period_3month_ago, uid)

        lst_outfits = list()
        if total_wish_outfit == 0:
            lst_outfits = get_populer_recomm(season, gender, uid)
        else:
            lst_explore_recomm = get_explore_recomm(uid, gender, season)
            lst_outfits = lst_explore_recomm if len(lst_explore_recomm) != 0 else get_populer_recomm(season, gender, uid)

        tracking_behavior_viewed(lst_outfits, uid)
        t2 = time.time()
        print("Explore Time Consumption:{}".format(t2-t1))
        return make_response(render_template('recommendation.html', outfits=lst_outfits), 200)


class Search(Resource):
    def get(self):
        check_token = check_valid_token()
        if check_token['result'] == 'fail':
            gender = 'women'
            colors = get_colors()
            categories = get_categories(gender)
            return make_response(render_template('search_product.html', colors=colors, categories=categories, title="???????????????????????? ??????????????????!"), 200)

        gender = check_token['current_user']['gender']
        colors = get_colors()
        categories = get_categories(gender)
        return make_response(render_template('search_product.html', colors=colors, categories=categories, title="???????????????????????? Let's Go!"), 200)

    def post(self):
        check_token = check_valid_token()
        gender = 'women' if check_token['result'] == 'fail' else check_token['current_user']['gender']
        hm_kol_id = 'hm_official_women' if gender == 'women' else 'hm_official_men'
        colors = get_colors()
        categories = get_categories(gender)
        season = session.get('season') if session.get('season') != None else get_season(date.today())
        color = request.form.get('choose_color')
        category = request.form.get('choose_category')

        choosen_color = color if color != 'Choose Color' else ''
        choosen_category = category if category != 'Choose Product Category' else ''
        if not choosen_color and not choosen_category:
            title = 'Oops!????????????????????????????????????'
            return make_response(render_template('search_product.html', colors=colors, categories=categories, title=title, type='result'), 200)

        lst_wear_outfits = search_product_wear(season, gender, choosen_category, choosen_color)
        lst_hm_outfits = search_product_hm(hm_kol_id, choosen_category, choosen_color, len(lst_wear_outfits))
        category_ch = get_category_ch_name(choosen_category) if choosen_category else ''
        title = f'"{choosen_color} {category_ch}" ???????????????'
        return make_response(render_template('search_product.html', colors=colors, categories=categories, lst_wear_outfits=lst_wear_outfits, lst_hm_outfits=lst_hm_outfits, title=title, type='search'), 200)


class Wishlist(Resource):
    def get(self):
        check_token = check_valid_token()
        if check_token['result'] == 'fail':
            return make_response(render_template('wishlist.html'), 200)

        uid = check_token['current_user']['uid']
        period_2year_ago = date.today() - relativedelta(years=+ 2)
        total_outfit = get_total_wish_outfit(period_2year_ago, uid)
        per_page = 6
        pages = total_outfit // per_page
        paging = int(request.args.get('paging', 0, type=int))
        offset = paging*per_page
        if paging <= pages:
            create_session({'paging': paging, 'pages': pages, 'total_outfit': total_outfit})
            outfits = get_wish_outfit_by_page(uid, per_page, offset)
            return make_response(render_template('wishlist.html', outfits=outfits, total_outfit=total_outfit, pages=pages, paging=paging), 200)
        else:
            return make_response(render_template('404.html'), 404)

    def post(self):
        check_token = check_valid_token()
        if check_token['result'] == 'success':
            uid = check_token['current_user']['uid']
            outfit_id = json.loads(list(request.form)[0])['outfit_id']
            tracking_behavior_addevent(uid, outfit_id, 'wish')

    def delete(self):
        check_token = check_valid_token()
        if check_token['result'] == 'success':
            uid = check_token['current_user']['uid']
            outfit_id = json.loads(list(request.form)[0])['outfit_id']
            tracking_behavior_removewish(outfit_id, uid)


class Logout(Resource):
    def get(self):
        session.clear()
        return redirect(url_for('home'))


class WordcloudSearch(Resource):
    def get(self):
        if request.args.get('keyword'):
            keyword = request.args.get('keyword')
            keywordch = request.args.get('keywordch')
            season = session.get('season')
            create_session({'category_jp': keyword, 'category_ch': keywordch})

            check_token = check_valid_token()
            if check_token['result'] == 'fail':
                gender = 'women'
                season = get_season(date.today())
                lst_wordcloud_search_outfits = get_wordcloud_search_outfit(keyword, season, gender)
                outfits = list()
                for idx, outfit in enumerate(lst_wordcloud_search_outfits):
                    outfit_info = dict(outfit, index=str(idx + 1), style="color:#B6AD90;")
                    outfits.append(outfit_info)
                return make_response(render_template('wordcloud_search.html', keywordch=keywordch, outfits=outfits), 200)

            uid = check_token['current_user']['uid']
            gender = check_token['current_user']['gender']
            lst_wordcloud_search_outfits = get_wordcloud_search_outfit(keyword, season, gender)
            lst_wish_outfits = get_wish_outfit(uid)

            outfits = list()
            for idx, outfit in enumerate(lst_wordcloud_search_outfits):
                if outfit['outfit_id'] in lst_wish_outfits:
                    outfit_info = dict(outfit, index=str(idx + 1), style="color:#E76F51;")
                    outfits.append(outfit_info)
                else:
                    outfit_info = dict(outfit, index=str(idx + 1), style="color:#B6AD90;")
                    outfits.append(outfit_info)
            tracking_behavior_viewed(lst_wordcloud_search_outfits, uid)
            return make_response(render_template('wordcloud_search.html', keywordch=keywordch, outfits=outfits), 200)
        return redirect(url_for('wordcloud'))


class Shopping(Resource):
    def get(self):
        outfit_id = request.args.get('outfitid')
        shop_outfit = get_outfit_info(outfit_id)
        shop_products = get_product_info(outfit_id)

        check_token = check_valid_token()
        if check_token['result'] == 'success':
            uid = check_token['current_user']['uid']
            tracking_behavior_addevent(uid, outfit_id, 'shop')

        type = request.args.get('type')
        if type == 'wish':
            return make_response(render_template('shopping.html', type=type, products=shop_products, outfit_image=shop_outfit['outfit_image'], outfitid=outfit_id), 200)
        else:
            keyword = session.get('category_jp')
            keywordch = session.get('category_ch')
            keyword_link = OFFICIAL_URL + '/wordcloud/search?keyword=' + keyword + '&keywordch=' + keywordch
            return make_response(render_template('shopping.html', keyword_link=keyword_link, products=shop_products, outfit_image=shop_outfit['outfit_image'], outfitid=outfit_id), 200)


class Datapipeline(Resource):
    def get(self):
        return make_response(render_template('datapipeline.html'), 200)


class RecommendationDashboard(Resource):
    def get(self):
        latest_date = date.today()-timedelta(1)
        knn_time_consumption = get_etl_latest_time(latest_date, 'Build Recommendation Model')
        knn_outfit_quantity = get_etl_quantity(latest_date, 'knn_outfits')
        knn_rating_quantity = get_etl_quantity(latest_date, 'knn_ratings')
        marketing_funnel = get_marketing_funnel(latest_date)
        if not knn_time_consumption['women'] or not knn_outfit_quantity['women'] or not knn_rating_quantity['women'] or not marketing_funnel:
            return make_response(render_template('dashboard.html', latest_date=latest_date,  show_data='no'), 200)
        
        graph1JSON = create_graph(knn_time_consumption, 'Time Consumption(Seconds)')
        graph2JSON = create_graph(knn_outfit_quantity, 'Outfit Quantity')
        graph3JSON = create_graph(knn_rating_quantity, 'Rating Quantity')
   
        stages = ['view', 'wish', 'shop']
        number = [marketing_funnel['view'], marketing_funnel['wish'], marketing_funnel['shop']]
        event_data = dict(number=number, stages=stages)
        fig4 = px.funnel(event_data, x='number', y='stages', title="Marketing Funnel")
        graph4JSON = json.dumps(fig4, cls=plotly.utils.PlotlyJSONEncoder)
        conversion_rate = math.floor(marketing_funnel['shop'] / (marketing_funnel['view']) * 100) if marketing_funnel['view']!=0 else 0
        return make_response(render_template('dashboard.html', latest_date=latest_date,  graph1JSON=graph1JSON, graph2JSON=graph2JSON, graph3JSON=graph3JSON, graph4JSON=graph4JSON, show_data='yes', conversion_rate=conversion_rate), 200)

    def post(self):
        latest_date = request.form['date']
        knn_time_consumption = get_etl_latest_time(latest_date, 'Build Recommendation Model')
        knn_outfit_quantity = get_etl_quantity(latest_date, 'knn_outfits')
        knn_rating_quantity = get_etl_quantity(latest_date, 'knn_ratings')
        marketing_funnel = get_marketing_funnel(latest_date)
        if not knn_time_consumption['women'] or not knn_outfit_quantity['women'] or not knn_rating_quantity['women'] or not marketing_funnel:
            return make_response(render_template('dashboard.html', latest_date=latest_date,  show_data='no'), 200) 
        
        graph1JSON = create_graph(knn_time_consumption, 'Time Consumption(Seconds)')
        graph2JSON = create_graph(knn_outfit_quantity, 'Outfit Quantity')
        graph3JSON = create_graph(knn_rating_quantity, 'Rating Quantity')

        stages = ['view', 'wish', 'shop']
        number = [marketing_funnel['view'], marketing_funnel['wish'], marketing_funnel['shop']]
        event_data = dict(number=number, stages=stages)
        fig4 = px.funnel(event_data, x='number', y='stages', title="Marketing Funnel")
        graph4JSON = json.dumps(fig4, cls=plotly.utils.PlotlyJSONEncoder)
        conversion_rate = math.floor(marketing_funnel['shop'] / (marketing_funnel['view']) * 100) if marketing_funnel['view']!=0 else 0
        return make_response(render_template('dashboard.html', latest_date=latest_date,  graph1JSON=graph1JSON, graph2JSON=graph2JSON, graph3JSON=graph3JSON, graph4JSON=graph4JSON, show_data='yes', conversion_rate=conversion_rate), 200)


class CrawlerDashboard(Resource):
    def get(self):
        latest_date = date.today()-timedelta(1)
        kol_time_consumption = get_etl_latest_time(latest_date, 'crawl_kol')
        outfit_time_consumption = get_etl_latest_time(latest_date, 'crawl_outfit')
        new_kol_quantity = get_etl_quantity(latest_date, 'new_kol')
        new_outfit_quantity = get_etl_quantity(latest_date, 'new_outfit')    
        new_like_quantity = get_etl_quantity(latest_date, 'new_like')    
        new_comment_quantity = get_etl_quantity(latest_date, 'new_comment') 
        if kol_time_consumption['women'] is None or outfit_time_consumption['women'] is None or new_kol_quantity['women'] is None or new_outfit_quantity['women'] is None or new_like_quantity['women'] is None or new_comment_quantity['women'] is None:
            return make_response(render_template('crawler.html', latest_date=latest_date,  show_data='no'), 200)
        
        graph1JSON = create_graph(kol_time_consumption, 'Crawl New KOLs (Seconds)')
        graph2JSON = create_graph(outfit_time_consumption, 'Crawl New Outfits (Hours)')
        graph3JSON = create_graph(new_kol_quantity, 'New KOL Quantity')
        graph4JSON = create_graph(new_outfit_quantity, 'New Outfit Quantity')
        graph5JSON = create_graph(new_like_quantity, 'New Rating Quantity(Like)')
        graph6JSON = create_graph(new_comment_quantity, 'New Rating Quantity(comment)')
        return make_response(render_template('crawler.html', latest_date=latest_date,  graph1JSON=graph1JSON, graph2JSON=graph2JSON, graph3JSON=graph3JSON, graph4JSON=graph4JSON, graph5JSON=graph5JSON, graph6JSON=graph6JSON, show_data='yes'), 200)

    def post(self):
        latest_date = request.form['date']
        kol_time_consumption = get_etl_latest_time(latest_date, 'crawl_kol')
        outfit_time_consumption = get_etl_latest_time(latest_date, 'crawl_outfit')
        new_kol_quantity = get_etl_quantity(latest_date, 'new_kol')
        new_outfit_quantity = get_etl_quantity(latest_date, 'new_outfit') 
        new_like_quantity = get_etl_quantity(latest_date, 'new_like')    
        new_comment_quantity = get_etl_quantity(latest_date, 'new_comment')   
        if not kol_time_consumption['women'] or not outfit_time_consumption['women'] or not new_kol_quantity['women'] or not new_outfit_quantity['women'] or not new_like_quantity['women'] or not new_comment_quantity['women']:
            return make_response(render_template('crawler.html', latest_date=latest_date,  show_data='no'), 200)
        
        graph1JSON = create_graph(kol_time_consumption, 'Crawl New KOLs (Seconds)')
        graph2JSON = create_graph(outfit_time_consumption, 'Crawl New Outfits (Hours)')
        graph3JSON = create_graph(new_kol_quantity, 'New KOL Quantity')
        graph4JSON = create_graph(new_outfit_quantity, 'New Outfit Quantity')
        graph5JSON = create_graph(new_like_quantity, 'New Rating Quantity(Like)')
        graph6JSON = create_graph(new_comment_quantity, 'New Rating Quantity(Comment)')
        return make_response(render_template('crawler.html', latest_date=latest_date,  graph1JSON=graph1JSON, graph2JSON=graph2JSON, graph3JSON=graph3JSON, graph4JSON=graph4JSON, graph5JSON=graph5JSON, graph6JSON=graph6JSON, show_data='yes'), 200)


@app.errorhandler(404)
def page_not_found(e):
    return make_response(render_template('404.html'), 404)


app.register_error_handler(404, page_not_found)
