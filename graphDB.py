from py2neo import Graph,Node,Relationship
import json

from analytics import Tweet_Analyser

uri="http://localhost:7474"
user="neo4j"
password="password"

remove_tweets=[]

Twitter_graph = Graph(uri=uri,user=user,password=password)

def getData(filename):

    grapher = Tweet_Analyser()
    grapher.get_from_files(filename)
    grapher.make_dataframe()

    with open(filename,"r") as read:
        file_data=json.load(read)

    tweets = []

    for id in grapher.df["TweetID"]:
        i = 0
        for tweet in file_data:

            if id == tweet["id_str"]:
                tweets.append(tweet)
                i = 1

            elif "RT @" in tweet["text"] and id == tweet["retweeted_status"]["id_str"]:
                tweets.append(tweet)
                i = 1

            if i == 1:
                break

    return tweets


def Add_to_Database(tweet):

    if "RT @" not in tweet["text"]:

        u = Node("User",UserID=tweet['user']["id"],ScreenName=tweet["user"]["screen_name"])

        t = Node("Tweet",TweetID=tweet["id"],Text=tweet['text'],Likes=tweet['favorite_count'],Retweets=tweet["retweet_count"])

        rel = Relationship(u,"Tweets",t)

        tx.merge(u,"User","UserID")
        tx.merge(t,"Tweet","TweetID")
        tx.create(rel)

    else:

        u1 = Node("User", UserID=tweet['user']['id'], ScreenName=tweet["user"]["screen_name"]) # User who retweeted

        u2 = Node("User", UserID=tweet["retweeted_status"]['user']['id'], ScreenName=tweet["retweeted_status"]["user"]["screen_name"])  # Original author of tweet

        t = Node("Tweet", TweetID=tweet["retweeted_status"]["id"], Text=tweet["retweeted_status"]['text'], Likes=tweet["retweeted_status"]['favorite_count'],Retweets=tweet["retweeted_status"]["retweet_count"])

        rel1 = Relationship(u2,"Tweets", t)

        rel2 = Relationship(u1,"Retweets",t,TweetID=tweet["id"],Text=tweet['text'],Likes=tweet['favorite_count'],Retweets=tweet["retweet_count"])

        tx.merge(u1,"User","UserID")
        tx.merge(u2,"User","UserID")
        tx.merge(t,"Tweet","TweetID")
        tx.create(rel1)
        tx.create(rel2)

if __name__ == "__main__":

    tweets=getData("tweet_d1fdaab1-b8c1-4f6b-b7e9-17844d8d6186.json")
    i = 0
    for tweet in tweets:
        tx=Twitter_graph.begin()
        Add_to_Database(tweet)
        i += 1
        tx.commit()
        print("Tweets Processed: ",i)