import config
import model_sql 
from bs4 import BeautifulSoup
import requests
from urllib.parse import unquote
import time

def crawl_beautifulsoup(url):
    res = requests.get(url, headers=config.headers)
    soup = BeautifulSoup(res.text, 'html.parser')
    return soup

if __name__ == "__main__":
    shop_urls = model_sql.extract_sql_product_shop_url()
    for shop_url in shop_urls:
        url = shop_url['shop_url']
        id = shop_url['id']
        if 'https://ck.jp.ap.valuecommerce.com/servlet/referral' in url:
            decode_url = unquote(url).split('vc_url=')[1]
            soup = crawl_beautifulsoup(decode_url)
            if soup.select_one('div.p-goods-information__price') or soup.select_one('div.p-goods-information__price--discount'):
                model_sql.update_sql_valid_shop_url(id, decode_url)
                print(id, decode_url, "pass")
            else:
                model_sql.update_sql_valid_shop_url(id, 'None')
                print(id, decode_url, "fail")
            time.sleep(5)
