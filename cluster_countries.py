import os
import numpy as np
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

os.chdir('/home/nikolay/Documents/Medium/COVID19/')

# The data used as JHU CSSE downloaded from here https://data.humdata.org/dataset/novel-coronavirus-2019-ncov-cases

# Reading cases from CSSE
cases = pd.read_csv('time_series_covid19_confirmed_global.csv')
cases = cases[cases['Province/State'].isna()==True]
cases.index = list(cases['Country/Region'])
cases = cases.drop(['Province/State', 'Lat', 'Long', 'Country/Region'], axis = 1)
#cases = cases.drop(list(cases.columns[0:30]), axis = 1)
print(cases.head())

# Reading deaths from CSSE
deaths = pd.read_csv('time_series_covid19_deaths_global.csv')
deaths = deaths[deaths['Province/State'].isna()==True]
deaths.index = list(deaths['Country/Region'])
deaths = deaths.drop(['Province/State', 'Lat', 'Long', 'Country/Region'], axis = 1)
#deaths = deaths.drop(list(deaths.columns[0:30]), axis = 1)
print(deaths.head())

# Reading population sizes
pop_size_europe_df = pd.read_csv('pops_sizes.csv')
print(pop_size_europe_df)
pop_size_europe_dict = pop_size_europe_df.set_index('Country').T.to_dict('records')[0]
print(pop_size_europe_dict)

public_event_ban = pd.read_csv('PublicEventsBan.csv')

my_countries = ['Austria', 'Belgium', 'Denmark', 'France', 'Germany', 'Greece', 'Italy', 'Netherlands', 
                'Norway', 'Portugal', 'Spain', 'Sweden', 'Switzerland', 'United Kingdom', 'Czechia', 
                'Israel', 'Hungary', 'Serbia', 'Finland', 'Ireland', 'Slovenia', 'Romania', 'Turkey', 'Poland', 
                'Russia', 'Slovakia', 'Estonia', 'Latvia', 'Lithuania', 'Bulgaria', 'Cyprus', 'US', 'Brazil', 
                'Croatia']

DateFirstDeath_list = []
DateFirstCase_list = []
DatePublicEventsBan_list = []
n_tol_cases = 0
n_tol_deaths = 0
for i, country_of_choice in enumerate(my_countries):
	
	datetime_death_str = deaths.loc[country_of_choice][deaths.loc[country_of_choice] > n_tol_deaths].index[0]
	datetime_death_object = datetime.strptime(datetime_death_str, '%m/%d/%y')
	DateFirstDeath_list.append(datetime_death_object.date())
	
	datetime_case_str = cases.loc[country_of_choice][cases.loc[country_of_choice] > n_tol_cases].index[0]
	datetime_case_object = datetime.strptime(datetime_case_str, '%m/%d/%y')
	DateFirstCase_list.append(datetime_case_object.date())
	
	datetime_peb_str = public_event_ban['DatePublicEventsBan'][i]
	datetime_peb_object = datetime.strptime(datetime_peb_str, '%m/%d/%y')
	DatePublicEventsBan_list.append(datetime_peb_object.date())

public_event_ban['DateFirstDeath'] = DateFirstDeath_list
public_event_ban['DateFirstCase'] = DateFirstCase_list
public_event_ban['DatePublicEventsBan'] = DatePublicEventsBan_list
public_event_ban['DaysSinceFirstDeath'] = (public_event_ban['DatePublicEventsBan'] - public_event_ban['DateFirstDeath']).dt.days
public_event_ban['DaysSinceFirstCase'] = (public_event_ban['DatePublicEventsBan'] - public_event_ban['DateFirstCase']).dt.days
print(public_event_ban)


delay = public_event_ban[['DaysSinceFirstDeath','DaysSinceFirstCase']]
delay.index = my_countries
print(delay)

per_capita_deaths = []
per_capita_deaths_binary = []
for i in my_countries:
    print('Per capita deaths for {0}: {1}'.format(i, (deaths.loc[i][-1] / pop_size_europe_dict[i])*1e+6))
    per_capita_deaths.append((deaths.loc[i][-1] / pop_size_europe_dict[i])*1e+6)
    if (deaths.loc[i][-1] / pop_size_europe_dict[i])*1e+6 >= 200:
        per_capita_deaths_binary.append(1)
    else:
        per_capita_deaths_binary.append(0)
        

fig, ax = plt.subplots(figsize=(10, 8))
my_ax = ax.scatter(delay.DaysSinceFirstDeath, delay.DaysSinceFirstCase)

for i, txt in enumerate(list(delay.index)):
    if per_capita_deaths_binary[i] == 1:
        my_color_country = 'red'
    else:
        my_color_country = 'darkgreen'
    if txt == 'Austria' or txt == 'Poland' or txt == 'Estonia' or txt == 'Greece' or txt == 'Brazil':
        ax.annotate(txt, (delay.DaysSinceFirstDeath[i], delay.DaysSinceFirstCase[i]), horizontalalignment='right', 
                   color = my_color_country)
        continue
    if txt == 'Lithuania':
        ax.annotate(txt, (delay.DaysSinceFirstDeath[i], delay.DaysSinceFirstCase[i]), horizontalalignment='right', 
                   color = my_color_country)
        continue
    else:
        ax.annotate(txt, (delay.DaysSinceFirstDeath[i], delay.DaysSinceFirstCase[i]), horizontalalignment='left', 
                    color = my_color_country)

plt.xlabel('Days From First Death to Public Events Banned', fontsize = 13)
plt.ylabel('Days From First Case to Public Events Banned', fontsize = 13)
plt.title('Speed of COVID19 Caused Interventions Across (Mostly) European Countries', fontsize = 15)
red_patch = mpatches.Patch(color='red', label='Deaths Per Million > 200')
blue_patch = mpatches.Patch(color='darkgreen', label='Deaths Per Million < 200')
plt.legend(handles=[blue_patch, red_patch])
plt.show()        
