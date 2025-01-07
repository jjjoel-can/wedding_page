import tweepy



# Authenticate to Twitter
auth = tweepy.OAuth1UserHandler(consumer_key=consumer_token, consumer_secret=consumer_token_secret, 
                                access_token=access_token, access_token_secret=access_token_secret)

api = tweepy.API(auth)

print(api)

# Search for tweets with hashtags related to wedding services
hashtag = "weddingphotographer"  # Change to any wedding-related hashtag
tweets = api.search(q=hashtag, lang="en", count=100)

# Extract tweet data
for tweet in tweets:
    print(f"Tweet by @{tweet.user.screen_name}:")
    print(f"Text: {tweet.text}")
    print(f"Date: {tweet.created_at}")
    print(f"Location: {tweet.user.location if tweet.user.location else 'No location'}")
    print(f"Followers: {tweet.user.followers_count}")
    print("-" * 40)