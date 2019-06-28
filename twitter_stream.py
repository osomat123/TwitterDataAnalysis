from twython import TwythonStreamer
import json
import uuid

class DEIStreamer(TwythonStreamer):
    tweets=[]
    no_of_tweets=0
    tweets_per_file=1000
    filename = "tweet_" + str(uuid.uuid4()) + ".json"

    def process_tweets(self,tweet):
        try:
            self.tweets.append(tweet)
            self.no_of_tweets+=1
            print("Tweets in file= ",self.no_of_tweets)

            if self.no_of_tweets == self.tweets_per_file:
                self.save_to_disk(self.tweets,self.filename)
                self.tweets=[]
                self.no_of_tweets=0

        except:
            self.disconnect()

    def init_variables(self,tweets):
        self.tweets_per_file=tweets

    def on_success(self, data):
        try:
            if data['lang'] == 'en':
                self.process_tweets(data)
        except:
            self.disconnect()

    def on_error(self, status_code, data):
        print(status_code,data)
        self.disconnect()

    def on_timeout(self,data):
        pass

    def disconnect(self):
        self.disconnect()

    def save_to_disk(self,tweets,filename):
        with open(filename,"a") as outfile:
            json.dump(tweets,outfile)
