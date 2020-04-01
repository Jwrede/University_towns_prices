import pandas as pd
from scipy.stats import ttest_ind
import numpy as np

np.dot()

#maps state names to two letter acronyms
states = {'OH': 'Ohio', 'KY': 'Kentucky', 'AS': 'American Samoa', 'NV': 'Nevada', 'WY': 'Wyoming', 'NA': 'National', 'AL': 'Alabama', 'MD': 'Maryland', 'AK': 'Alaska', 'UT': 'Utah', 'OR': 'Oregon', 'MT': 'Montana', 'IL': 'Illinois', 'TN': 'Tennessee', 'DC': 'District of Columbia', 'VT': 'Vermont', 'ID': 'Idaho', 'AR': 'Arkansas', 'ME': 'Maine', 'WA': 'Washington', 'HI': 'Hawaii', 'WI': 'Wisconsin', 'MI': 'Michigan', 'IN': 'Indiana', 'NJ': 'New Jersey', 'AZ': 'Arizona', 'GU': 'Guam', 'MS': 'Mississippi', 'PR': 'Puerto Rico', 'NC': 'North Carolina', 'TX': 'Texas', 'SD': 'South Dakota', 'MP': 'Northern Mariana Islands', 'IA': 'Iowa', 'MO': 'Missouri', 'CT': 'Connecticut', 'WV': 'West Virginia', 'SC': 'South Carolina', 'LA': 'Louisiana', 'KS': 'Kansas', 'NY': 'New York', 'NE': 'Nebraska', 'OK': 'Oklahoma', 'FL': 'Florida', 'CA': 'California', 'CO': 'Colorado', 'PA': 'Pennsylvania', 'DE': 'Delaware', 'NM': 'New Mexico', 'RI': 'Rhode Island', 'MN': 'Minnesota', 'VI': 'Virgin Islands', 'NH': 'New Hampshire', 'MA': 'Massachusetts', 'GA': 'Georgia', 'ND': 'North Dakota', 'VA': 'Virginia'}

def get_list_of_university_towns():
    '''
    ____________________________________________________________________________
    
    returns a list of the university cities, where a university town is a city that 
    has a high percentage of university students compared to the total population
    ____________________________________________________________________________'''
    
    states = []
    df_data = []
    with open(r"C:\Users\Jonathan\Desktop\coursera\Data science\testing\university_towns.txt") as data:
        for line in data:
            if "edit" in line:
                states.append(line[:-7])
            else:
                df_data.append([line[:line.find("(")],states[len(states)-2]])
    #cleans data
    university_towns = pd.DataFrame(data = df_data, columns = ["State", "RegionName"])
    university_towns.drop([179,184], inplace = True)
    university_towns = university_towns["State"].to_list()
    return [i[:-1] for i in university_towns] 
                

def clean_gdp_data():
    '''
    ____________________________________________________________________________
    
    cleans the dataset that gives the gdp over time in years and in quartals
    only returns the quartals from 2000Q1 onwards as a dataframe
    ____________________________________________________________________________'''
    
    data = pd.read_excel(r"C:\Users\Jonathan\Desktop\coursera\Data science\testing\gdplev.xlsx")
    data = data.iloc[:,4:7]
    data.columns = ["Quarterly", "GDP in billions of current dollars", "GDP in billions of chained 2012 dollars"]
    data = data[218:]
    data.reset_index(inplace = True)
    data = data.iloc[:,1:]
    return data

def get_recession_start():
    '''
    ____________________________________________________________________________
    
    a recession start is defined as two consecutive quarters of GDP decline,
    returns the starting quartal as a string
    ____________________________________________________________________________'''
    data = clean_gdp_data()
    for i in range(0, data.iloc[:,0].size):
        if data.iloc[i, 2] > data.iloc[i+1, 2] and data.iloc[i+1, 2] > data.iloc[i+2, 2]:
            return data.iloc[i].Quarterly
        
def get_recession_end():
    '''
    ____________________________________________________________________________
    
    a recession start is defined as two consecutive quarters of GDP increase after a recession start,
    returns the ending quartal as a string
    ____________________________________________________________________________'''
    
    data = clean_gdp_data()
    recession_start_index = data[data.iloc[:,0] == get_recession_start()].index[0]
    for i in range(recession_start_index, data.iloc[:,0].size):
        if data.iloc[i, 2] > data.iloc[i-1, 2] and data.iloc[i-1, 2] > data.iloc[i-2, 2]:
            return data.iloc[i].Quarterly


def get_recession_bottom():
    '''
    ____________________________________________________________________________
    
    returns the quarter with the lowest GDP in a recession as a string
    ____________________________________________________________________________'''
    
    data = clean_gdp_data()
    recession_start = data[data.iloc[:,0] == get_recession_start()].index[0]
    recession_end = data[data.iloc[:,0] == get_recession_end()].index[0]
    return data[data["GDP in billions of chained 2012 dollars"] == data.iloc[recession_start:recession_end,2].min()].Quarterly.values[0]
    
def convert_housing_data_to_quarters():
    '''
    ____________________________________________________________________________
    
    loads a dataset that shows the housing prices in different cities over time
    and converts the columns that show the prices monthly to quartals,
    returns a dataframe
    ____________________________________________________________________________'''


    data = pd.read_csv(r"C:\Users\Jonathan\Desktop\coursera\Data science\testing\City_Zhvi_AllHomes.csv")
    data.State = data.State.map(states)
    data.set_index(["State", "RegionName"], inplace = True)
    data = data.loc[:,"2000-01":"2019-12"]
    return data.groupby(pd.PeriodIndex(data = data.columns, freq = "Q"), axis = 1).mean()

def run_ttest():
    '''
    ____________________________________________________________________________
    
    creates two dataframes that show the absolute change in university towns and 
    non university towns during the recession and tests whether they differ in
    their change.
    
    returns a tuple where:
    
    returns whether the hypothesis is true
         ⭣
        (a, b, c)
           ⭡   ⮡ the dataframe with the favorable prices
        p_value           
    ____________________________________________________________________________'''
    
    data = convert_housing_data_to_quarters()
    data = data.loc[:,get_recession_start():get_recession_bottom()]
    university_towns = get_list_of_university_towns()
    data = data.dropna()
    data_absolute_change = data["2008Q2"] - data["2009Q2"]
    university_towns_data = data_absolute_change.loc[university_towns]
    non_university_towns_data = data_absolute_change.drop(index = university_towns, level = 0)
    ttest = ttest_ind(university_towns_data, non_university_towns_data)
    _ = "university_towns_data" if ttest[0] < 0 else "non_university_towns_data"
    return (ttest[1] < 0.01, ttest[1], _)


ye = run_ttest()