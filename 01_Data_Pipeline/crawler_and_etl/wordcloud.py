#coding=utf-8
from model_sql import *
from datetime import datetime, date
from dateutil.relativedelta import relativedelta 
import googletrans  
import MeCab 
from collections import Counter, defaultdict
import re
import json

def get_stop_words():
    with open('./utils/stop_words.json') as f:
         stop_words= json.load(f)
    return stop_words

def get_word_translation():
    with open('./utils/word_translation.json') as f:
         word_translation= json.load(f)
    return word_translation

def strip_emoji(text):
    RE_EMOJI = re.compile('[\U00010000-\U0010ffff]', flags=re.UNICODE)
    return RE_EMOJI.sub(r'', text)

def description_remove_emoji(outfit_descriptions):
    source_text=''
    for outfit in outfit_descriptions:
        source_text += outfit['outfit_description'].replace('╼','').replace('￣','').replace('＿','').replace('･','').replace('_','')\
            .replace('@','').replace('-','').replace('☞','').replace('☺️','').replace('♡','').replace('✨','').replace('❤️‍','').replace('⭕️I','')\
                .replace('✊','').replace('❗️','')

    source_text=strip_emoji(source_text)
    source_text=source_text[:950000]
    return source_text

def wordcloud_analysis(source_text, stop_words):
    tagger  = MeCab.Tagger("-Owakati")
    node = tagger.parseToNode(source_text)
    word_list = []
    while node:
        word_type = node.feature.split(',')[0]
        word=node.surface
        if (word_type == '形容詞' or word_type == '名詞') and (word not in stop_words['stop_words']):
            word_list.append(node.surface)
        node = node.next
    word_counter = Counter(word_list).most_common(30)
    return word_counter

def translate_word_counter(word_counter, word_translation):
    translator = googletrans.Translator()
    word_counter_ch=defaultdict()
    for word in word_counter:
        if word[0] in word_translation:
            if word_translation[word[0]] in word_counter_ch:
                word_counter_ch[word_translation[word[0]]]+=word[1]
            else:
                word_counter_ch[word_translation[word[0]]]=word[1]
        else:
            result = translator.translate(word[0], dest='zh-TW').text
            if result in word_counter_ch:
                word_counter_ch[result]+=word[1]
            else:
                word_counter_ch[result+'/'+word[0]]=word[1] #save japanese for which can't be tanslated!

    lst_words=[]
    calculated_at= datetime.now()
    for key,value in word_counter_ch.items():
        if key in list(word_translation.values()):
            word_jp=list(word_translation.keys())[list(word_translation.values()).index(key)]
            tuple_word=(calculated_at,gender, key,word_jp,value)
            lst_words.append(tuple_word)
        else: 
            word_ch=key.split('/')[0]
            word_jp=key.split('/')[1]
            tuple_word=(calculated_at,gender, word_ch, word_jp,value)
            lst_words.append(tuple_word)
    return lst_words


if __name__ == "__main__":
    genders=['women','men']
    for gender in genders:
        stop_words=get_stop_words()
        word_translation=get_word_translation()
        period_3month_ago=date.today() - relativedelta(months=+3)

        outfit_descriptions=extract_sql_outfit_description(gender,period_3month_ago)
        source_text=description_remove_emoji(outfit_descriptions)
        word_counter=wordcloud_analysis(source_text,stop_words)
        lst_words=translate_word_counter(word_counter, word_translation)
        insert_sql_wordcloud(lst_words)