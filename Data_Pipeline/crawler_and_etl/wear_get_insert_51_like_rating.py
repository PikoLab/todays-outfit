from model_sql import *

def check_new_like_rating(last_rating_id,last_comment_id, last_event_id):    
    query_offset=last_rating_id-last_comment_id
    per_page=100000
    total_pages=(last_event_id-query_offset)//per_page
    for iter in range(0,total_pages+1):
        start_id=iter*per_page+query_offset
        end_id=start_id+per_page
        lst_new_event_like=extract_sql_new_event_like(start_id,end_id)
    
        lst_new_rating_like = [tuple(dict_.values())[1:]+(1,) for dict_ in lst_new_event_like]
        insert_sql_new_rating_like(lst_new_rating_like)

if __name__ == "__main__":
    last_rating_id = extract_sql_max_rating_id()
    last_comment_id = extract_sql_max_comment_id()
    last_event_id = extract_sql_max_event_id()
    check_new_like_rating(last_rating_id,last_comment_id, last_event_id)
