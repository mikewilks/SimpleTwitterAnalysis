import tweepy, csv, datetime, requests,json


#load parameters from file
paramfile = open("params.json","r")
params = json.loads(paramfile.read())
paramfile.close()

consumer_key = params['consumer_key']
consumer_secret = params['consumer_secret']
access_token = params['access_token']
access_token_secret = params['access_token_secret']
klout_key = params['klout_key']
file_of_ids = params['file_of_ids']
output_file = params['output_file']

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
ids_to_check = ['']

analysed_data_item = ['Name','Twitter ID','Followers','Tweets', 'Last Tweet', 'Klout Score','Last Checked']
analysed_data = []

# Add the headers
analysed_data.append(analysed_data_item)


api = tweepy.API(auth)

# Load a list of Twitter handles to check from a file
f= open(file_of_ids,"r")
ids_to_check = f.readlines()
f.close()

# Open the file for writing to
csv_output = open(output_file, 'w')

# Loops through and check them

for i in ids_to_check :
    i=i.strip() #removes the sprurious newline after the IDs, might be able to swap readlines for something to do this in one go
    if i[0] == '@' : # also remove the initial @ if there is one as it upsets Klout
        i=i[1:]
    user_to_check = api.get_user(i)

    print (i)

    #Klout
    klout_score = 'NA'
    resp_url = 'http://api.klout.com/v2/identity.json/twitter?screenName={}&key={}'.format(i,klout_key)

    resp = requests.get(resp_url)
    if resp.status_code != 200:
    # This means something went wrong.
        print ("Klout Error - likely user not found")
    else :
        klout_id = resp.json()['id']
        # Now get the actual klout score
        resp_url = 'http://api.klout.com/v2/user.json/{}/score?key={}'.format(klout_id,klout_key)
        resp = requests.get(resp_url)
        if resp.status_code != 200:
            # This means something went wrong.
            print("This didn't work")
        else :
            klout_score = str(round(resp.json()['score']))

    # Get the results
    analysed_data_item = [user_to_check.name,i,user_to_check.followers_count,user_to_check.statuses_count,user_to_check.status.created_at.strftime('%m/%d/%Y'),klout_score,datetime.date.today()]
    analysed_data.append(analysed_data_item)

#write the data out to a csv file
with csv_output:
    writer = csv.writer(csv_output)
    writer.writerows(analysed_data)
csv_output.close()