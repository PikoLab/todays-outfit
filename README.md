# [Today's Outfit](https://todaysoutfit.online/)

A Fashion Guide Website that aims to equip users with outfit trends and fashion tips by providing “Trendy Fashion Word Cloud” and “Fashion Exploration Recommendation Engine.”


![](https://github.com/PikoLab/todays-outfit/blob/main/03_Charts/00_cover_page.png)

#### Website : https://todaysoutfit.online/
```txt
👉Test Account
E-mail: demowomen@gmail.com
Password: demowomen
```


## Table of Contents
* [Server Structure & Data Pipeline](#Server-Structure-&-Data-Pipeline)
* [Airflow Dag](#Airflow-Dag)
* [Technologies](#Technologies)
* [MySQL Schema](#MySQL-Schema)
* [Features](#Features)


## Server Structure & Data Pipeline
![](https://github.com/PikoLab/todays-outfit/blob/main/03_Charts/07_server_structure_and_data_pipeline.png)

## Airflow Dag
![](https://github.com/PikoLab/todays-outfit/blob/develop-dashboard/03_Charts/05_airflow_dag.png)


## Technologies
1. Data Pipeline: `Airflow`
2. Database: `MongoDB`, `MySQL`
3. Cloud Service(AWS): `EC2`, `RDS`, `S3`
4. Recommendation Model:`Collaborative Filtering Approach`(`cosine similarity` for distance metric)
5. NLP: Word Cloud, `Mecab`(Japanese Word Segmentation), `asari`(Japanese Sentiment Analysis)
6. Designed API for Event Tracking (viewed, collected)
7. Backend: `Flask`
8. Frontend: `HTML`, `CSS`, `JavaScript`
9. Networking: `Nginx`, `SSL Certificate`

 

## MySQL Schema
![](https://github.com/PikoLab/todays-outfit/blob/main/03_Charts/08_mysql_schema.png)

## Features
### 1. Trendy Fashion Word Cloud
Generated Word Cloud of trendy fashion keywords by word segmentation and word frequency calculation
![](https://github.com/PikoLab/todays-outfit/blob/main/03_Charts/01_wordcloud.gif)
### 2. Fashion Exploration Recommendation Engine
* Constructed Fashion Exploration Recommendation Engine in `collaborative filtering` approach to make personalized recommendations according to `tracked user preference(events) on outfit posts`. 
* The way of `Explore`: Recommend user the outfits which are similar with the outfits on user's wishlist. And filter out the outfits which user have viewed. 
* Here is the evaluatoin table of event and user rating:  

| Event  | User Rating | Description |
| --- |  :---:  | --- |
| view     | 0     |     |
| like     | 1     |     |
| commentA | 2     | More than `70% Positive Score` evaluated by "asari" Sentiment Analysis |
| commentB | 3     | More than `90% Positive Score` evaluated by "asari" Sentiment Analysis |
| collect  | 4     | user add the outfit to `wishlist` |
| shop     | 5     | user click `go shopping`  |

![](https://github.com/PikoLab/todays-outfit/blob/main/03_Charts/02_explore_recommendation.gif)
### 3. Product Search
User can search outfits by color or product category. Only show the most popular outfit results. 
![](https://github.com/PikoLab/todays-outfit/blob/main/03_Charts/03_product_search.gif)
### 4. Wishlist 
List the outfits on user's wishlist and sort by time in descending order.
![](https://github.com/PikoLab/todays-outfit/blob/main/03_Charts/04_wishlist.gif)

## Contact Me
Piko Chen(Chen Ku-Nung) nonie.115@gmail.com

