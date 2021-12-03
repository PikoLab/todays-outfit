from flask import Flask
from config import *
import pymysql.cursors  
from flask_bcrypt import Bcrypt
from flask_restful import Api  


app=Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY

db = pymysql.connect(host=MYSQL_HOST,
                    user=MYSQL_USER,
                    password=MYSQL_PASSWORD,
                    db=MYSQL_DB_TODAYSOUTFIT,
                    charset='utf8mb4',
                    cursorclass=pymysql.cursors.DictCursor)

bcrypt=Bcrypt(app)
api=Api(app)


from server.routes import *
api.add_resource(Home, '/')
api.add_resource(Register, '/register')
api.add_resource(Login, '/login')
api.add_resource(Wordcloud, '/wordcloud')
api.add_resource(Explore, '/explore')
api.add_resource(Search, '/product/search')
api.add_resource(Wishlist, '/wishlist')
api.add_resource(Logout,'/login')
api.add_resource(Datapipeline,'/datapiline')
api.add_resource(WordcloudSearch,'/wordcloud/search')
api.add_resource(Shopping,'/shopping')
api.add_resource(AddWish,'/addwish')
api.add_resource(RemoveWish,'/removewish')