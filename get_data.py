from matplotlib.colors import ListedColormap
import matplotlib.pyplot as plt
import seaborn as sns
import requests
import tweepy
import sys
import os


# Secrets
GH_TOKEN = os.getenv('GH_TOKEN')
CONSUMER_KEY = os.getenv('CONSUMER_KEY')
CONSUMER_SECRET = os.getenv('CONSUMER_SECRET')
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
ACCESS_TOKEN_SECRET = os.getenv('ACCESS_TOKEN_SECRET')

# Config
GITHUB_USERNAME = 'GonzaloLardies'
BACKGROUND_COLOR = '#191724'
SPACE_BETWEEN_CELLS = 1
DPI = 300
COLOR_MAP = {
  0: '#26233a',
  4: '#9be9a8',
  3: '#40c463',
  2: '#30a14e',
  1: '#216e39'
}
WIDTH = 1500
HEIGHT = 500


# Get contributions
contributions_query = '''
query($userName:String!) { 
    user(login: $userName) {
        contributionsCollection {
            contributionCalendar {
                totalContributions
                weeks {
                    contributionDays {
                        contributionCount
                        date
                    }
                }
            }
        }
    }
}
'''

variables, headers = { 'userName' : GITHUB_USERNAME }, {'Authorization': 'Bearer ' + GH_TOKEN}
response = requests.post( 'https://api.github.com/graphql', json={'query': contributions_query, 'variables': variables}, headers=headers)

if response.status_code == 200:
  contributions = response.json()
else:
  print('Error: No se han podido recuperar las contribuciones')
  sys.exit()


# Plot data
weeks = contributions['data']['user']['contributionsCollection']['contributionCalendar']['weeks']
days_per_week = [week['contributionDays'] for week in weeks][:-1]
days_per_weekday = [list(day) for day in zip(*days_per_week)]

def value_to_color(val):
  if val == 0:
      return 0
  elif val < 10:
      return 1
  elif val < 15:
      return 2
  elif val < 25:
      return 3
  else: # val == 4
      return 4

heatmap_data = [[value_to_color(d['contributionCount']) for d in wd] for wd in days_per_weekday]


# Plot style
palette = sns.color_palette("coolwarm", as_cmap=True)
custom_cmap = ListedColormap([COLOR_MAP[i] for i in range(5)])
sns.set_theme(rc={ 'axes.facecolor' : BACKGROUND_COLOR, 'figure.facecolor' : BACKGROUND_COLOR})
plt.figure(figsize=(WIDTH / DPI, HEIGHT / DPI))
ax = sns.heatmap(heatmap_data, cmap=custom_cmap, linewidths=SPACE_BETWEEN_CELLS, linecolor=BACKGROUND_COLOR, cbar=False, square=True)
ax.axis('off')


# Save fig
plt.savefig('output.jpg', dpi=DPI)


# X upload
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)
upload_result = api.media_upload('output.jpg')
api.update_profile_banner('output.jpg')
print('Done!')

