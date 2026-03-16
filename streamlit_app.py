# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests  

# Write directly to the app
st.title(f":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write(
  """Choose the fruits you want in your cusom Smoothie! """
)

name_on_order = st.text_input('Name on Smoothie:')
st.write("The name on our smoothie will be", name_on_order)

cnx=st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))

# convert the snowpark datafrme tp a pandas df so we can use the LOC fn
pd_df = my_dataframe.to_pandas()
st.dataframe(pd_df)



ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:", 
    my_dataframe,
    max_selections =5
)

if ingredients_list:
    ingredients_string = ''
    for x in ingredients_list:
        ingredients_string += x + ' '
        search_on=pd_df.loc[pd_df['FRUIT_NAME'] == x, 'SEARCH_ON'].iloc[0]
        st.write('The search value for ', x,' is ', search_on, '.')
        st.header(x + 'Nutrition Information')
        smoothiefroot_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on}")  
        sf_df = st.dataframe(st.text(smoothiefroot_response.json()), use_container_width=True)

    my_insert_stmt = """ insert into smoothies.public.orders(ingredients, name_on_order)
                    values ('""" + ingredients_string + """', '""" + name_on_order + """')"""
    trim_to_insert = st.button('Submit Order')

    #st.write(my_insert_stmt)
    if trim_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success(f'Your Smoothie is ordered, {name_on_order}!', icon="✅")

# new section to display the nutrient information


    
    
