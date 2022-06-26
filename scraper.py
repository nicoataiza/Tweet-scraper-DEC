from datetime import datetime, timedelta
import snscrape.modules.twitter as sntwitter
import pandas as pd
import os
import boto3
from io import StringIO, BytesIO
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import dotenv

BUCKET_NAME = "output-dec1"
MY_FOLDER_PREFIX = "Bitcoin-Tweets/"
DATA_PATH = '/opt/airflow/data/'
dotenv.load_dotenv("dev.env")

def scrape_tweets(keyword,start_date=datetime(2017,12,30),end_date=datetime(2018,12,30)):
    """
    Scrapes twitter based on specified keyword

    Args:
        keyword (string): keyword to be used for the search query.

    Returns:
        DataFrame: returns a DataFrame with the following columns regarding the tweet -
                   Datetime, Tweet Id, Text, and Username
    """
    # start_date = 
    # end_date =  #datetime.today()
    tweets_list = []
    for i,tweet in enumerate(sntwitter.TwitterSearchScraper(f'{keyword} since:{start_date.strftime("%Y-%m-%d")} until:{end_date.strftime("%Y-%m-%d")}').get_items()):
        tweets_list.append([tweet.date, tweet.id, tweet.content, tweet.user.username])
    tweets_df = pd.DataFrame(tweets_list, columns=['Datetime', 'Tweet Id', 'Text', 'Username'])
    return tweets_df

def upload_string_to_gcs(csv_body, uploaded_filename, service_secret=os.environ.get('SERVICE_SECRET')):
    gcs_resource = boto3.resource(
        "s3",
        region_name="auto",
        endpoint_url="https://storage.googleapis.com",
        aws_access_key_id=os.environ.get("SERVICE_ACCESS_KEY"),
        aws_secret_access_key=os.environ.get("SERVICE_SECRET"),
    )
    gcs_resource.Object(BUCKET_NAME, MY_FOLDER_PREFIX + "/" + uploaded_filename).put(Body=csv_body.getvalue())

start_date = datetime(2017,12,30)
end_date = datetime.today()
while start_date <= end_date:
    # VADER - Sentiment analysis
    print("VADER - Sentiment analysis")
    sid = SentimentIntensityAnalyzer()
    df = scrape_tweets("bitcoin",start_date=start_date,end_date=start_date)
    df['scores'] = df['Text'].apply(lambda tweets: sid.polarity_scores(tweets))
    df['compound']  = df['scores'].apply(lambda score_dict: score_dict['compound'])
    print("df_ready")
    # Validate
    pass 

    # Save as csv and then upload  
    csv_buffer = StringIO()

    df.to_csv(csv_buffer)
    print("csv_ready")
    upload_string_to_gcs(csv_body=csv_buffer, uploaded_filename=f"bitcoin_tweets_{start_date.strftime('%Y-%m-%d')}.csv")
    print(f"done uploading bitcoin_tweets.csv_{start_date}")
    start_date += timedelta(days=1)