"""Simple Twitter Analysis of followers, tweets and last tweeted written to a CSV file."""
import csv
import datetime
import json

import tweepy


def load_parameters():
    """ Load parameters from file."""
    param_file = open("params.json", "r")
    params_read = json.loads(param_file.read())
    param_file.close()

    return params_read


def authorise(consumer_key, consumer_secret, access_token, access_token_secret):
    """Authorise with Twitter via Tweepy and return the auth token."""
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    return auth


def load_ids_to_analyse(filename):
    """Load a list of Twitter handles to check from a file"""
    file_handle = open(filename, "r")
    ids_list = file_handle.readlines()
    file_handle.close()
    return ids_list


def analyse(tweepy_api, ids, keyword_to_check):
    """Do the analysis and return. """
    if keyword_to_check == '':
        analysed_data_item = ['Name',
                              'Twitter ID',
                              'Followers',
                              'Tweets',
                              'Last Tweet',
                              'Last Checked']
    else:
        analysed_data_item = ['Name',
                              'Twitter ID',
                              'Followers',
                              'Keyword Followers',
                              'Keyword % of followers',
                              'Tweets',
                              'Last Tweet',
                              'Last Checked']

    analysed_data = list()

    # Add the headers
    analysed_data.append(analysed_data_item)

    # Loops through and check them
    for i in ids:
        i = i.strip()
        user_to_check = tweepy_api.get_user(i)
        print(i)

        # Get the results
        if keyword_to_check == '':
            analysed_data_item = [user_to_check.name,
                                  i,
                                  user_to_check.followers_count,
                                  user_to_check.statuses_count,
                                  user_to_check.status.created_at.strftime('%d/%m/%Y'),
                                  datetime.date.today()]
        else:
            # Get their followers and check for the presence
            # of the keyword in it
            followers = get_followers(tweepy_api, user_to_check)
            instances_of_keyword = count_keywords_in_profile(tweepy_api,
                                                             followers,
                                                             keyword_to_check)

            # Build the data object to return
            analysed_data_item = [user_to_check.name,
                                  i,
                                  user_to_check.followers_count,

                                  instances_of_keyword,
                                  user_to_check.followers_count / instances_of_keyword,
                                  user_to_check.statuses_count,
                                  user_to_check.status.created_at.strftime('%d/%m/%Y'),
                                  datetime.date.today()]

        analysed_data.append(analysed_data_item)
    return analysed_data


def count_keywords_in_profile(tweepy_api, list_of_users, keyword_to_check):
    """Returns the number profiles containing the keyword in
    the list_of_users and returns it."""
    count = 0
    # Iterating one at a time over the list of users will
    # get rate-limited by the API very quickly better to
    # use lookup_users not get_user
    for user_id in list_of_users:
        user_object = tweepy_api.get_user(user_id)
        if keyword_to_check in user_object.description:
            count += 1
    print(f"{user_object.name} has {count} keyword followers")
    return count


def get_followers(tweepy_api, twitter_handle):
    """Returns a list of followers."""
    followers_list = []
    for follower in tweepy.Cursor(tweepy_api.followers_ids, id=twitter_handle).items():
        followers_list.append(follower)
    return followers_list

# Load the parameters from the json file
params = load_parameters()

# Authorise with Twitter via Tweepy and get the token
auth_token = authorise(params['consumer_key'], params['consumer_secret'], params['access_token'],
                       params['access_token_secret'])

# Get the API object
api = tweepy.API(auth_token)

# Get the list of ids to analyse
ids_to_check = load_ids_to_analyse(params['file_of_ids'])

# Do the analysis
results = analyse(api, ids_to_check, params['profile_keyword'])

# Open the file for writing to
# and write the data out to a csv file
csv_output = open(params['output_file'], 'w')
with csv_output:
    writer = csv.writer(csv_output)
    writer.writerows(results)
csv_output.close()
