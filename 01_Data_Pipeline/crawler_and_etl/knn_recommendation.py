# coding=utf-8
from model_sql import *
import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors
from datetime import date
from scipy.sparse import csr_matrix
import datetime
from dateutil.relativedelta import relativedelta
import time


def get_outfit_user_matrix(lst_seasonal_rating):
    df_ratings = pd.DataFrame(lst_seasonal_rating)
    df_ratings = df_ratings.drop_duplicates(subset=['uid', 'outfit_id'], keep='first')
    print("df:{}".format(df_ratings))

    shape = df_ratings.shape
    quantity_rating = shape[0]  # Number of rows/ratings

    outfit_user_matrix = df_ratings.pivot(index='outfit_id', columns='uid', values='rating').fillna(0)
    return outfit_user_matrix, quantity_rating


def build_knn_model(outfit_user_matrix, calculated_at):
    outfit_user_matrix_sparse = csr_matrix(outfit_user_matrix.values)
    num_total_outfits = outfit_user_matrix_sparse.shape[0]
    print("num_total_outfits:{}".format(num_total_outfits))

    model_knn = NearestNeighbors(n_neighbors=20, algorithm='brute', metric='cosine', n_jobs=-1)
    model_knn.fit(outfit_user_matrix_sparse)

    per_query = 50
    iters = num_total_outfits // per_query
    for iter in range(iters+1):
        start = iter*per_query
        n_neighbors = 201 if num_total_outfits > 201 else num_total_outfits
        print("max iter number is {}".format(start+per_query))
        lst_seasonal_recomm = []
        for num in range(start, start+per_query):
            if num < num_total_outfits:
                _, indices = model_knn.kneighbors(outfit_user_matrix_sparse[num], n_neighbors=n_neighbors)
                outfit_item1 = outfit_user_matrix.index[indices.tolist()[0][0]]
                for rank, idx in enumerate(indices.tolist()[0][1:]):
                    outfit_item2 = outfit_user_matrix.index[idx]
                    tuple_data = (outfit_item1, outfit_item2, rank+1, calculated_at)
                    lst_seasonal_recomm.append(tuple_data)
        insert_sql_knn_recommendation(lst_seasonal_recomm)


if __name__ == "__main__":
    genders = ['women', 'men']
    for gender in genders:
        t1 = time.time()
        calculated_at = datetime.datetime.now()

        period_month_ago = date.today() - relativedelta(months=+2)
        tuple_seasonal_outfit = extract_month_outfit(gender, period_month_ago)
        quantity_outfit = len(tuple_seasonal_outfit)

        per_query = 300000  # RDS memory limitation
        start = 1
        max_rating_id = extract_sql_max_rating_id()
        total_iters = max_rating_id//per_query

        lst_seasonal_rating = []
        for iter in range(0, total_iters+1):
            start_point = start+iter*per_query
            end_point = start_point+per_query-1
            batch_seasonal_rating = extract_batch_seasonal_rating_data(tuple_seasonal_outfit, start_point, end_point)
            lst_seasonal_rating += batch_seasonal_rating

        outfit_user_matrix, quantity_rating = get_outfit_user_matrix(lst_seasonal_rating)
        build_knn_model(outfit_user_matrix, calculated_at)
        t2 = time.time()
        knn_time_consumption = t2-t1
        insert_sql_etl_time_consumption(calculated_at, 'Build Recommendation Model', gender, knn_time_consumption)
        insert_sql_etl_quantity(calculated_at, 'knn_ratings', gender, quantity_rating)
        insert_sql_etl_quantity(calculated_at, 'knn_outfits', gender, quantity_outfit)
