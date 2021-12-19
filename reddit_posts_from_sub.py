import requests
from datetime import datetime, timezone
import pandas as pd
import itertools    # itertools.product()
import json         # json.dumps()

#####################################################################

# NOTE: Reddit has a hard limit on 1000 posts returned,
# so we can't get any more for this listing + timeframe

#!!!!!!!!!!! FILL THIS IN !!!!!!!!!!!#

subreddit = 'python'
limit = 100       # number of posts per request. max: 100
listing = 'top' # controversial, best, hot, new, random, rising, top
timeframe = 'all' # hour, day, week, month, year, all (timeframe doesnt matter for new listing)

stat_type = 'mean' # print statistics with mean or median

#####################################################################

pd.set_option('display.max_columns', None)      # do not hide columns
pd.set_option('max_colwidth', None)             # do not truncate

#####################################################################

number_of_posts = 1000                          # variable only used for progress bar. Not actual limit

# https://stackoverflow.com/a/15860757
def update_progress(progress):
    barLength = 10 # Modify this to change the length of the progress bar
    status = ""
    if isinstance(progress, int):
        progress = float(progress)
    if not isinstance(progress, float):
        progress = 0
        status = "error: progress var must be float\r\n"
    if progress < 0:
        progress = 0
        status = "Halt...\r\n"
    if progress >= 1:
        progress = 1
        status = "Done...\r\n"
    block = int(round(barLength*progress))
    text = "Progress: [{0}] {1}% {2}".format( "#"*block + "-"*(barLength-block), progress*100, status)
    print(text)

#####################################################################

# get posts
after = ''
posts_info = []

posts_found = 0;
try:
    base_url = f'https://www.reddit.com/r/{subreddit}/{listing}.json?limit={limit}&t={timeframe}'
    response = requests.get(base_url, headers = {'User-agent': 'yourbot'}).json()
    after = response['data']['after']
except:
    print('An Error Occured')
for post in response['data']['children']:
    posts_info.append([
        post['data']['ups'],
        datetime.fromtimestamp(post['data']['created_utc'], timezone.utc).astimezone().hour,
        datetime.fromtimestamp(post['data']['created_utc'], timezone.utc).astimezone().weekday(),
        post['data']['url']
    ])
posts_found += limit
update_progress(posts_found / number_of_posts)

while after is not None:
    try:
        base_url = f'https://www.reddit.com/r/{subreddit}/{listing}.json?limit={limit}&t={timeframe}&after={after}'
        response = requests.get(base_url, headers = {'User-agent': 'yourbot'}).json()
        after = response['data']['after']
    except:
        print('An Error Occured')
    for post in response['data']['children']:
        posts_info.append([
            post['data']['ups'],
            datetime.fromtimestamp(post['data']['created_utc'], timezone.utc).astimezone().hour,
            datetime.fromtimestamp(post['data']['created_utc'], timezone.utc).astimezone().weekday(),
            post['data']['url']
        ])
    posts_found += limit
    update_progress(posts_found / number_of_posts)

# create dataframe of average upvotes from rows of same weekday and hour of creation
# then show top 10
df = pd.DataFrame(posts_info, columns = ['Upvotes', 'Hour', 'Weekday', 'Url'])
day_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
avg_upvotes_by_hour_and_weekday = []
for day in range(7):
    for hour in range(24):
        if stat_type == 'mean':
            avg_upvotes_by_hour_and_weekday.append(df[(df['Weekday'] == day) & (df['Hour'] == hour)]['Upvotes'].mean())
        elif stat_type == 'median':
            avg_upvotes_by_hour_and_weekday.append(df[(df['Weekday'] == day) & (df['Hour'] == hour)]['Upvotes'].median())
        else:
            print("Error: unknown stat_type")
            quit()
df_by_weekday = pd.DataFrame(avg_upvotes_by_hour_and_weekday, index = itertools.product(day_of_week, list(range(24))), columns = ['Upvotes'])
print(df_by_weekday.sort_values('Upvotes', ascending = 0).head(10))





# format:
# upvotes
# hour of post
# day of post (0 = Monday)
# URL

#print(json.dumps(posts_info, indent=4))