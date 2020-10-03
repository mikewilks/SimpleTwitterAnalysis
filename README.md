This is a very simple script that pulls data from the Twitter API to save cutting and pasting manually. Supplied with a list of row separated twitter handles  (without the '@') the output is a CSV file with the relevant columns created.

The keyword can be '' and it will ignore it. If the keyword is populated then the number of followers who have that keyword in their profile will be returned for each user (as well as the percentage of followers). This is useful for finding the percentage of a particular user's followers who have a given interest or maybe work for a particular company.

Authentication is very basic and requires Twitter credentials to be manually obtained and stored in a json file (params.json) loaded from the same location as the script. There is a sample of this file in the repository, edit and rename it.

Credentials are obtained by following the instructions here:

https://developer.twitter.com/en/docs/basics/authentication/guides/access-tokens

