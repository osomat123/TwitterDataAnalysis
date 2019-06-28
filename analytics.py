import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import datetime as dt
import pytz

sns.set()

class Tweet_Analyser:

    def __init__(self):

        self.search_terms = []
        self.df = pd.DataFrame()
        self.tweets = []

    def get_from_files(self, filepath):
        with open(filepath, "r") as read:
            data = json.load(read)

        with open("search_terms.json","r") as read:
            words = json.load(read)

        for word in words:
            self.search_terms.append(word['keyword'].upper())

        for tweet in data:
            for word in self.search_terms:
                text = tweet["text"]
                if word in text.upper():
                    self.tweets.append(tweet)
                    break


    def make_dataframe(self):

        df1 = pd.DataFrame()
        df2 = pd.DataFrame()

        # Making dataframe from tweets in files
        df1['TweetID'] = np.array([tweet["id_str"] for tweet in self.tweets])
        df1['Text'] = np.array([tweet["text"] for tweet in self.tweets])
        df1['TimeUTC'] = np.array([dt.datetime.strptime(tweet["created_at"], "%a %b %d %H:%M:%S %z %Y") for tweet in self.tweets])
        df1['TimeIST'] = np.array([time.astimezone("Asia/Kolkata") for time in df1.TimeUTC])
        df1['Likes'] = np.array([tweet["favorite_count"] for tweet in self.tweets])
        df1['Retweets'] = np.array([tweet["retweet_count"] for tweet in self.tweets])

        # Making dataframe from the original tweets of the retweeted tweets
        df2['TweetID'] = np.array([tweet["retweeted_status"]["id_str"] for tweet in self.tweets if "RT @" in tweet["text"]])
        df2['Text'] = np.array([tweet["retweeted_status"]["text"] for tweet in self.tweets if "RT @" in tweet["text"]])
        df2['TimeUTC'] = np.array([dt.datetime.strptime(tweet["retweeted_status"]["created_at"], "%a %b %d %H:%M:%S %z %Y") for tweet in self.tweets if "RT @" in tweet["text"]])
        df2['TimeIST'] = np.array([time.astimezone("Asia/Kolkata") for time in df2.TimeUTC])
        df2['Likes'] = np.array([tweet["retweeted_status"]["favorite_count"] for tweet in self.tweets if "RT @" in tweet["text"]])
        df2['Retweets'] = np.array([tweet["retweeted_status"]["retweet_count"] for tweet in self.tweets if "RT @" in tweet["text"]])

        self.df = pd.concat([df1, df2])
        self.df.drop_duplicates(subset="TweetID",keep="first",inplace=True) # Removing duplicate tweets
        self.df.reset_index(inplace=True)

        keywords = []
        remove_tweets = []

        for i in range(len(self.df)):
            j = 0
            for word in self.search_terms:
                text=self.df["Text"][i]
                if word in text.upper():
                    keywords.append(word)
                    j = 1
                    break
            if j == 0: # Removing unwanted tweets
                np.array(remove_tweets.append(i))

        self.df.drop(remove_tweets,inplace=True)

        self.df["Keyword"]=keywords

        self.df.reset_index(inplace=True)
        self.df["Keyword"]=keywords

    def getStats(self):
        print(self.df.describe())

    # Histogram of number of tweets at various hours of day
    def plot_time_hist(self):
        plt.hist([time.hour for time in self.df["TimeIST"]], bins=24, edgecolor="black", linewidth=1.2)

        font_labels = {'family': 'serif', 'color': 'darkred', 'weight': 'bold', 'size': 18}
        font_title = {'family': 'serif', 'color': 'darkred', 'weight': 'bold', 'size': 20}

        plt.xticks(np.arange(2, 24, step=2),fontweight="bold")
        plt.yticks(np.arange(500, 4500, step=500),fontweight="bold")

        plt.xlabel("Hour of Day",fontdict=font_labels)
        plt.ylabel("Number of tweets",fontdict=font_labels)

        plt.title("Variation in number of tweets at various hours of the day",fontdict=font_title)
        plt.show()

    # Bar plot of number of tweets containing each of the provided keywords
    def plot_keyword_bar(self):

        num_of_tweets = [len([key for key in self.df["Keyword"] if key == keyword]) for keyword in self.search_terms]
        arr = np.arange(len(self.search_terms))

        plt.bar(arr,num_of_tweets,edgecolor="black",linewidth=1.2)

        font_labels = {'family': 'serif', 'color': 'darkred', 'weight': 'bold', 'size': 18}
        font_data = {'family': 'serif', 'color': 'darkred', 'weight': 'bold'}
        font_title = {'family': 'serif', 'color': 'darkred', 'weight': 'bold', 'size': 20}

        plt.xticks(arr,self.search_terms,fontweight="bold")
        plt.yticks(np.arange(0, 6000, step=1000),fontweight="bold")

        plt.xlabel("Keywords Given",fontdict=font_labels)
        plt.ylabel("Number of tweets",fontdict=font_labels)

        for i in arr:
            plt.text(i,num_of_tweets[i]+35,str(num_of_tweets[i]),horizontalalignment='center',fontdict=font_data)

        plt.title("Variation in number of tweets containing each of the provided keywords",fontdict=font_title)
        plt.show()

    # Bar plot of maximum number of likes for each of the provided keywords
    def plot_maxLikes_bar(self):

        max_likes=[]

        for keyword in self.search_terms:
            max_likes.append(self.df[self.df["Keyword"] == keyword]["Likes"].max())

        arr = np.arange(len(self.search_terms))

        plt.bar(arr, max_likes, edgecolor="black",linewidth=1.2)

        font_labels={'family': 'serif','color':  'darkred','weight': 'bold','size': 18}
        font_data = {'family': 'serif', 'color': 'darkred', 'weight': 'bold'}
        font_title = {'family': 'serif', 'color': 'darkred', 'weight': 'bold', 'size': 20}

        plt.xticks(arr,self.search_terms,fontweight="bold")
        plt.yticks(np.arange(0, 400000, step=50000),fontweight="bold")

        plt.xlabel("Keywords Given",fontdict=font_labels)
        plt.ylabel("Maximum Likes", fontdict=font_labels)

        for i in arr:
            plt.text(i,max_likes[i]+45,str(max_likes[i]),horizontalalignment='center',fontdict=font_data)

        plt.title("Variation in number of likes for each of the provided keywords",fontdict=font_title)

        plt.show()

    # Bar plot of mean and standard deviation of likes for each of the provided keywords
    def plot_likesMeanStd_bar(self):

        mean_likes = []
        std_likes =[]

        for keyword in self.search_terms:
            std_likes.append(int(self.df[self.df["Keyword"] == keyword]["Likes"].std()))
            mean_likes.append(int(self.df[self.df["Keyword"] == keyword]["Likes"].mean()))

        arr = np.arange(len(self.search_terms))

        plt.bar(arr+0.2, std_likes, edgecolor="black", linewidth=1.2, label="Standard deviation of likes",width=0.4)
        plt.bar(arr-0.2, mean_likes, edgecolor="black", linewidth=1.2, label="Mean number of likes",width=0.4)

        font_labels = {'family': 'serif', 'color': 'darkred', 'weight': 'bold', 'size': 18}
        font_data = {'family': 'serif', 'color': 'darkred', 'weight': 'bold'}
        font_title = {'family': 'serif', 'color': 'darkred', 'weight': 'bold', 'size': 20}

        plt.xticks(arr, self.search_terms, fontweight="bold")
        plt.yticks(np.arange(0, 14000, step=2000), fontweight="bold")

        plt.xlabel("Keywords Given", fontdict=font_labels)
        plt.ylabel("Mean/Standard Deviation of Likes", fontdict=font_labels)

        for i in arr:
            plt.text(i-0.2, mean_likes[i] + 45, str(mean_likes[i]), horizontalalignment='center', fontdict=font_data)
            plt.text(i+0.2, std_likes[i] + 45, str(std_likes[i]), horizontalalignment='center', fontdict=font_data)

        plt.legend()
        plt.title("Variation in number of likes for each of the provided keywords", fontdict=font_title)

        plt.show()

    # Bar plot of maximum number of likes for each of the provided keywords
    def plot_maxRetweets_bar(self):

        max_likes = []

        for keyword in self.search_terms:
            max_likes.append(self.df[self.df["Keyword"] == keyword]["Retweets"].max())

        arr = np.arange(len(self.search_terms))

        plt.bar(arr, max_likes, edgecolor="black", linewidth=1.2)

        font_labels = {'family': 'serif', 'color': 'darkred', 'weight': 'bold', 'size': 18}
        font_data = {'family': 'serif', 'color': 'darkred', 'weight': 'bold'}
        font_title = {'family': 'serif', 'color': 'darkred', 'weight': 'bold', 'size': 20}

        plt.xticks(arr, self.search_terms, fontweight="bold")
        plt.yticks(np.arange(0, 100000, step=10000), fontweight="bold")

        plt.xlabel("Keywords Given", fontdict=font_labels)
        plt.ylabel("Maximum Retweets", fontdict=font_labels)

        for i in arr:
            plt.text(i, max_likes[i] + 45, str(max_likes[i]), horizontalalignment='center', fontdict=font_data)

        plt.title("Variation in number of retweets for each of the provided keywords", fontdict=font_title)

        plt.show()

    # Bar plot of mean and standard deviation of likes for each of the provided keywords
    def plot_retweetsMeanStd_bar(self):

        mean_likes = []
        std_likes = []

        for keyword in self.search_terms:
            std_likes.append(int(self.df[self.df["Keyword"] == keyword]["Likes"].std()))
            mean_likes.append(int(self.df[self.df["Keyword"] == keyword]["Likes"].mean()))

        arr = np.arange(len(self.search_terms))

        plt.bar(arr + 0.2, std_likes, edgecolor="black", linewidth=1.2, label="Standard deviation of likes",width=0.4)
        plt.bar(arr - 0.2, mean_likes, edgecolor="black", linewidth=1.2, label="Mean number of likes", width=0.4)

        font_labels = {'family': 'serif', 'color': 'darkred', 'weight': 'bold', 'size': 18}
        font_data = {'family': 'serif', 'color': 'darkred', 'weight': 'bold'}
        font_title = {'family': 'serif', 'color': 'darkred', 'weight': 'bold', 'size': 20}

        plt.xticks(arr, self.search_terms, fontweight="bold")
        plt.yticks(np.arange(0, 14000, step=2000), fontweight="bold")

        plt.xlabel("Keywords Given", fontdict=font_labels)
        plt.ylabel("Mean/Standard Deviation of Retweets", fontdict=font_labels)

        for i in arr:
            plt.text(i - 0.2, mean_likes[i] + 45, str(mean_likes[i]), horizontalalignment='center',fontdict=font_data)
            plt.text(i + 0.2, std_likes[i] + 45, str(std_likes[i]), horizontalalignment='center',fontdict=font_data)

        plt.legend()
        plt.title("Variation in number of retweets for each of the provided keywords", fontdict=font_title)

        plt.show()


if __name__ == "__main__":

    analyser = Tweet_Analyser()
    analyser.get_from_files("tweet_d1fdaab1-b8c1-4f6b-b7e9-17844d8d6186.json")
    analyser.make_dataframe()
    analyser.plot_keyword_bar()
    analyser.plot_time_hist()
    analyser.plot_maxLikes_bar()
    analyser.plot_likesMeanStd_bar()
    analyser.plot_maxRetweets_bar()
    analyser.plot_retweetsMeanStd_bar()







