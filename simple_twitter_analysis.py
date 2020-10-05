"""Simple Twitter Analysis of followers, tweets, how many of their
followers have a particular keyword in their profiles and last tweeted. Written to a CSV file."""
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
            # of the keyword in each followers profile / description
            followers = get_followers(tweepy_api, i)
            keyword_followers = count_keywords_in_profile(tweepy_api, followers,
                                                          keyword_to_check)

            print(f"{i} has {keyword_followers} "
                  "followers with the keyword in their profile")

            # Protect against div by 0, could have caught
            # the exception but this seems tidier
            follower_count = user_to_check.followers_count
            if follower_count == 0 or keyword_followers == 0:
                percentage_of_followers = 0
            else:
                percentage_of_followers = (keyword_followers / follower_count) * 100

            # Build the data object to return
            analysed_data_item = [user_to_check.name,
                                  i,
                                  follower_count,
                                  keyword_followers,
                                  percentage_of_followers,
                                  user_to_check.statuses_count,
                                  user_to_check.status.created_at.strftime('%d/%m/%Y'),
                                  datetime.date.today()]

        analysed_data.append(analysed_data_item)
    return analysed_data


def get_users(input_list, tweepy_api):
    """Returns the user objects from the given ids."""
    users = []
    length = len(input_list)
    if length in range(1, 100):
        print("length is less than 100 so just using the supplied list")
        users = tweepy_api.lookup_users(input_list)
    elif length > 100:
        for i in range(0, len(input_list), 100):
            print(i)
            sublist = input_list[i:i + 100]
            temp_results = tweepy_api.lookup_users(sublist)
            for entry in temp_results:
                users.append(entry)
    return users


def count_keywords_in_profile(tweepy_api, list_of_users, keyword_to_check):
    """Returns the number profiles containing the keyword in
    the list_of_users and returns it."""
    # Get the actual user objects
    users = get_users(list_of_users, tweepy_api)
    count = 0
    # Check the profiles (descriptions) for
    # the keyword
    for user in users:
        if keyword_to_check in user.description:
            count += 1
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
# api = tweepy.API(auth_token)
api = tweepy.API(auth_token, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

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
