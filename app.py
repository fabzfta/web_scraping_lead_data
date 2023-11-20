
from importlib.abc import Loader
import pickle
import googlemaps
import pandas as pd
import geocoder
import time
import requests
import json
import streamlit as st
from pathlib import Path
import streamlit_authenticator as stauth
import yaml



def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def remote_css(url):
    st.markdown(f'<link href="{url}" rel="stylesheet">', unsafe_allow_html=True)    


def convert_df(df):

    return df.to_csv().encode('utf-8')

local_css("style.css")
remote_css('https://fonts.googleapis.com/icon?family=Material+Icons')


st.title('Lead Contact Search 🔎')
selected = st.text_input(label='Search places nearby...')
distance = st.slider(
    label='Radius search',
    min_value=50000, max_value=313800, 
    step=10000)

distance = str(distance)
st.write(f'{distance} m.')
button_clicked = st.button("OK")

API_KEY = 'AIzaSyAOJXTdwy4hJTae2_tsmcQ28kvEnSJ3iwQ'
map_client = googlemaps.Client(API_KEY)


g = geocoder.ipinfo('100.127.255.208')

lat_lon = g.latlng
lat_lon_tuple = (lat_lon[0], lat_lon[1])
# Tornar latitude e longitude dinamico

st.write(lat_lon_tuple)
st.write(selected)
st.write(distance)

business_list = []


if button_clicked:
    response = map_client.places_nearby(
        location=lat_lon_tuple,
        keyword=selected,
        name='search',
        radius = distance
    )

    

    business_list.extend(response.get('results'))
    next_page_token = response.get('next_page_token')

    while next_page_token:
        time.sleep(2)
        response = map_client.places_nearby(
        location=lat_lon_tuple,
        keyword=selected,
        name='search',
        radius = distance,
        page_token=next_page_token
            )

        business_list.extend(response.get('results'))   
        next_page_token = response.get('next_page_token')

    df = pd.DataFrame(business_list)
    


    json_list = []
    for place_id in df['place_id']:

        url = 'https://maps.googleapis.com/maps/api/place/details/json?place_id=' + place_id + '&fields=formatted_phone_number&key=' + API_KEY

        payload = {}
        headers= {}
        
        response = requests.request("GET", url, headers=headers, data=payload)
        
        data = response.json()
        json_list.append(data['result'])

    json_values_list = []
    for values in json_list:
        values = list(values.values())
        if values:
            print(values[0])
            json_values_list.append(values[0])
        else:
            json_values_list.append(values)

    df_tel = pd.DataFrame({'phone_number':json_values_list}) 

    json_site_list = []
    for place_id in df['place_id']:

        url = 'https://maps.googleapis.com/maps/api/place/details/json?place_id=' + place_id + '&fields=website&key=' + API_KEY

        payload = {}
        headers= {}
        
        response = requests.request("GET", url, headers=headers, data=payload)
        
        data = response.json()
        json_site_list.append(data['result'])

    json_site_values_list = []
    for values in json_site_list:
        values = list(values.values())
        if values:
            json_site_values_list.append(values[0])
        else:
            json_site_values_list.append(values)

    df_site = pd.DataFrame({'website':json_site_values_list}) 

    df = pd.concat([df, df_tel, df_site], axis=1)

    df = df[['name','phone_number','website','vicinity','plus_code','rating','types','user_ratings_total']]
    



    st.dataframe(df)
    csv = convert_df(df)

    st.download_button(
        label="Download CSV",
        data= csv,
        file_name='lead_data.csv',
        mime='text/csv'
    )


