from model_sql import *


def check_new_comment_rating(lst_new_comment):
    lst_new_rating_comment = list()
    for comment in lst_new_comment:
        if comment['positive_sentiment_socre'] >= 0.9:
            tuple_rating = (comment['uid'], comment['outfit_id'], 3)
            lst_new_rating_comment.append(tuple_rating)
        elif comment['positive_sentiment_socre'] >= 0.7 and comment['positive_sentiment_socre'] < 0.9:
            tuple_rating = (comment['uid'], comment['outfit_id'], 2)
            lst_new_rating_comment.append(tuple_rating)
        elif comment['positive_sentiment_socre'] >= 0.6 and comment['positive_sentiment_socre'] < 0.7:
            tuple_rating = (comment['uid'], comment['outfit_id'], 1)
            lst_new_rating_comment.append(tuple_rating)
    return lst_new_rating_comment


if __name__ == "__main__":
    lst_new_comment = extract_sql_new_comment()
    lst_new_rating_comment = check_new_comment_rating(lst_new_comment)
    insert_sql_new_rating_comment(lst_new_rating_comment)
