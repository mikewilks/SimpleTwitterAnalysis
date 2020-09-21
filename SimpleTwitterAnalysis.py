import tweepy
import csv
import datetime
import json


# load parameters from file
paramfile = open("params.json", "r")
params = json.loads(paramfile.read())
paramfile.close()

consumer_key = params['consumer_key']
consumer_secret = params['consumer_secret']
access_token = params['access_token']
access_token_secret = params['access_token_secret']
file_of_ids = params['file_of_ids']
output_file = params['output_file']

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

analysed_data_item = ['Name', 'Twitter ID', 'Followers', 'Tweets', 'Last Tweet', 'Last Checked']
analysed_data = []

# Add the headers
analysed_data.append(analysed_data_item)

api = tweepy.API(auth)

# Load a list of Twitter handles to check from a file
f = open(file_of_ids, "r")
ids_to_check = f.readlines()
f.close()

# Open the file for writing to
csv_output = open(output_file, 'w')

# Loops through and check them
for i in ids_to_check:
    i = i.strip()
    user_to_check = api.get_user(i)
    print(i)

    # Get the results
    analysed_data_item = [user_to_check.name,
                          i,
                          user_to_check.followers_count,
                          user_to_check.statuses_count,
                          user_to_check.status.created_at.strftime('%m/%d/%Y'),
                          datetime.date.today()]
    analysed_data.append(analysed_data_item)

# write the data out to a csv file
with csv_output:
    writer = csv.writer(csv_output)
    writer.writerows(analysed_data)
csv_output.close()
