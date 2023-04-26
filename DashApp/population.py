from dash import Dash, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
from numerize import numerize 
import plotly
import plotly.express as px
from dash import dcc
import math
import plotly.graph_objects as go
from dotenv import load_dotenv
import os

#Applying Secrets
load_dotenv()
secret_token = os.getenv('secret_token')
#Import style sheet CSS for Basic Dash App
stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = Dash(__name__, external_stylesheets=[dbc.themes.PULSE, dbc.icons.BOOTSTRAP])


# READ EXCEL FILES FOR POPULATION-------------------------------------------------------------------------------------------
pop = pd.ExcelFile("DashApp/population/Total_population.xlsx")
population = pop.parse('Data',skiprows=3)
Male = pd.ExcelFile("DashApp/population/population_male.xlsx") 
Male_population = Male.parse('Data',skiprows=3)
Female = pd.ExcelFile("DashApp/population/population_female.xlsx") 
Female_population = Female.parse('Data',skiprows=3)

Age = pd.ExcelFile("DashApp/population/AgeGroup.xlsx")
Agedf = Age.parse('CLEANDATA')
Total = numerize.numerize(population['2021'].sum())
Male_Total = numerize.numerize(Male_population['2021'].sum())
Female_Total = numerize.numerize(Female_population['2021'].sum())

types= pop.parse('Metadata - Countries')
Country_codes = types.dropna(subset=['Region'])
Country_codes = Country_codes[['Country Code','Region']]
pop_region = population.merge(Country_codes, how='left', on='Country Code')
pop_region.Region = pop_region.Region.fillna('others')

col = pop_region.columns
pop_columns = list(col[56:-1:])

#Join the Country Code to retrieve the Country Latitiudes and Longitudes
country_code = pd.read_excel("DashApp/population/countries_codes.xlsx")
country_code.rename(columns = {'Alpha-3code':'Country Code'}, inplace=True)
population1_latlng = population.merge(country_code, how='left', on='Country Code')
#For testing purpose lets drop the nulls
population1_latlng = population1_latlng.dropna()
population1_latlng.set_index('Country Code')

#Country Columns
Country_Rows = population1_latlng['Country Name']
Country_names = list(Country_Rows[1::])
Country_names.insert(0,'ALL')

line_columns = ['TOTAL','MALE','FEMALE']
app.layout = html.Div(
    [
        html.H1('How Population Grew Over Years?',className='h1'),
#WORLD MAP DCC SCATTERMAPBOX-------------------------------------------------------------                        
        dbc.Row(
            [
                html.Div(
                    [
                        dcc.Graph(id='map_chart', config={'displayModeBar': 'hover',
                                                          'scrollZoom': False},
                        style={'background':'#00FC87','padding-bottom':'0px','padding-left':'0px','height':'70vh'})
                    ],className='create_container1 twelve columns'
                ),
            ]
        ), 
# DROP DOWN MENU-------------------------------------------------------------------------------------------             
        html.Div(
            [
                dbc.Row(
                    [
                        dbc.Col([
                            html.Label(['Select The Year:'],
                                       style={'color':'white','font-weight':'bold','text-align':'center'}),
                            dcc.Dropdown(
                                id='my_dropdown',
                                multi=False,
                                options=[
                                    {"label": x, "value": x}
                                    for x in pop_columns[1:]
                                ],
                                value='2021',
                                clearable = False,
                                placeholder = 'Select The Year:',
                                style={'background':'#1f2c56','margin':'10px',
                                       'font-weight':'bold'}
                            )
                        ],width=4),
                        
                        dbc.Col([
                            html.Label(['Select The Country'],
                                       style={'color':'white','font-weight':'bold','text-align':'center'}),
                            dcc.Dropdown(
                                id='country_dropdown',
                                multi=False,
                                options=[
                                    {"label": x, "value": x}
                                    for x in Country_names
                                ],
                                value=Country_names[0],
                                clearable = False,
                                style={'background':'#1f2c56','margin':'10px',
                                       'font-weight':'bold'}
                            )
                        ],width=8)
                    ]
                ),

            ]
        ),
#CONTAINERS CARDS-------------------------------------------------------------------------
        dbc.Container([
            dbc.Row([
# MINIMAL POPULATION BOOTSTRAP CARD-------------------------------------------------------------------------------------------                
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(
                            html.H2("TOTAL"),id='t-header-color'
                        ),
                        dbc.CardBody(
                            [
                                html.H3(id='Total_Card', className="bi bi-people-fill text-white"),
                                html.Div(id='percentage_tot')
                            ],
                        )
                    ],className="card_container1 text-center")                    
                ],className="four columns"),
                
    # MINIMAL MALE POPULATION BOOTSTRAP CARD-------------------------------------------------------------------------------------------                    
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(
                            html.H2("MALE"),id='m-header-color'
                        ),
                        dbc.CardBody(
                            [
                                html.H3(id='Male_Card', className="bi bi-gender-male text-white"),
                                html.Div(id='percentage_M')
                            ],
                        )
                    ],className="card_container1 text-center") 
                ],className="eight columns"),
    # MINIMAL FEMALE POPULATION BOOTSTRAP CARD-------------------------------------------------------------------------------------------                                        
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(
                            html.H2("FEMALE"),id='f-header-color'
                        ),
                        dbc.CardBody(
                            [
                                html.H3(id='Female_Card', className="bi bi-gender-female text-white"),
                                html.Div(id='percentage_F')
                            ],
                        )
                    ],className="card_container1 text-center") 
                ],className="four columns")
            ])
        ]),
#WORLD MAP DCC SCATTERMAPBOX-------------------------------------------------------------                        
        dbc.Row(
            [
                html.Div(
                    [
                        dcc.Graph(id='line_chart', config={'displayModeBar': 'hover',
                                                          'scrollZoom': False},
                        style={'background':'#00FC87','padding-bottom':'0px','padding-left':'0px','height':'60vh'})
                    ],className='create_container1 twelve columns'
                ),
            ],className='twelve columns'
        ), 
#BAR CHART-------------------------------------------------------------------------------             
        dbc.Row(
            [
                html.Div(
                    [
                        dcc.Graph(id='pie_chart', config={'displayModeBar': 'hover',
                                                          'scrollZoom': False},
                        style={'background':'#00FC87','padding-bottom':'0px','padding-left':'0px','height':'60vh'})
                    ],className='create_container1 twelve columns'
                ),
            ],className='twelve columns'
        ), 
    ]
)

@app.callback(Output('pie_chart', 'figure'),
              [Input('my_dropdown','value'),
               Input('country_dropdown','value')])
def updatecard(my_dropdown,country_dropdown):
    if country_dropdown == 'ALL':
        year = int(my_dropdown)
        Male = Agedf[(Agedf['Country Code'] == 'WLD') & (Agedf['Gender'] == 'male')][[year,'Age Group']]
        Male = Male.sort_values(by='Age Group', ascending= False)
        Female = Agedf[(Agedf['Country Code'] == 'WLD') & (Agedf['Gender'] == 'female')][[year,'Age Group']]
        Female = Female.sort_values(by='Age Group', ascending= False)
        
        Male_age = [float("{:.2f}".format(x)) for x in Male[year]]
        Male_group = [x for x in Male['Age Group']]
        Female_age = [float("{:.2f}".format(x)) for x in Female[year]]
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            y=Male_group,
            x=Male_age,
            name='Male',
            orientation='h',
            marker=dict(
                color='rgba(246, 78, 139, 0.6)'
            )
        ))
        fig.add_trace(go.Bar(
            y=Male_group,
            x=Female_age,
            name='FEMALE',
            orientation='h',
            marker=dict(
                color='rgba(58, 71, 80, 0.6)'
            )
        ))

        fig.update_layout(barmode='stack',font=dict(family="Courier New, monospace",
                                                    size=12,color="white"))
        fig.update_layout(plot_bgcolor='black',paper_bgcolor='black')
        fig.update_layout(title_text='Percentage Of Population by Gender/Age Group ' + ' for '+
                          country_dropdown + ' Countries',  
                          title_x=0.5,  
                          title_font_color= 'white')
        return fig 
    else:
        year = int(my_dropdown)
        Male = Agedf[(Agedf['Country Name'] == country_dropdown) & (Agedf['Gender'] == 'male')][[year,'Age Group']]
        Male = Male.sort_values(by='Age Group', ascending= False)
        Female = Agedf[(Agedf['Country Name'] == country_dropdown) & (Agedf['Gender'] == 'female')][[year,'Age Group']]
        Female = Female.sort_values(by='Age Group', ascending= False)
        
        Male_age = [float("{:.2f}".format(x)) for x in Male[year]]
        Male_group = [x for x in Male['Age Group']]
        Female_age = [float("{:.2f}".format(x)) for x in Female[year]]
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            y=Male_group,
            x=Male_age,
            name='Male',
            orientation='h',
            marker=dict(
                color='rgba(246, 78, 139, 0.6)'
            )
        ))
        fig.add_trace(go.Bar(
            y=Male_group,
            x=Female_age,
            name='FEMALE',
            orientation='h',
            marker=dict(
                color='rgba(58, 71, 80, 0.6)'
            )
        ))

        fig.update_layout(barmode='stack',font=dict(family="Courier New, monospace",
                                                    size=12,color="white"))
        fig.update_layout(plot_bgcolor='black',paper_bgcolor='black')
        fig.update_layout(title_text='Percentage Of Population by Gender/Age Group ' + ' for '+
                          country_dropdown,  
                          title_x=0.5,  
                          title_font_color= 'white')
        return fig 
    
@app.callback(Output('map_chart', 'figure'),
              [Input('my_dropdown','value'),
               Input('country_dropdown','value')])
def updatecard(my_dropdown,country_dropdown):
    if country_dropdown == 'ALL':
        year = ''.join(my_dropdown)
        population1_latlng_diffq = (population1_latlng[year].max()-population1_latlng[year].min()) / 16
        population1_latlng["scale"] = (population1_latlng[year]-population1_latlng[year].min()) / population1_latlng_diffq + 1
        
        locations = [go.Scattermapbox(    
                lon = population1_latlng['Longitude'],
                lat = population1_latlng['Latitude'],
                mode='markers',
                marker=go.scattermapbox.Marker(size=population1_latlng['scale']*4,
                                               color=population1_latlng['scale']),
                hoverinfo='text',
                hovertext=
                '<b>Country Name</b>:' + population1_latlng['Country Name'].astype(str) + '<br>' +
                '<b>Total Popultation:' + population1_latlng[year].astype(str)   
                
            )]
        
        layout = go.Layout(
                hovermode='x',
                paper_bgcolor='#1f2c56',
                plot_bgcolor='#1f2c56',
               margin=dict(r=10, l =10, b = 0, t = 0),
                mapbox=dict(
                    accesstoken=secret_token,
                    style='dark',
                ),
                autosize=True
                
            )
        
        fig = go.Figure(data=locations, layout=layout)
        return fig
        
    else:
        year = ''.join(my_dropdown)
        population1_latlng_diffq = (population1_latlng[year].max()-population1_latlng[year].min()) / 16
        population1_latlng["scale"] = (population1_latlng[year]-population1_latlng[year].min()) / population1_latlng_diffq + 1
        
        Country_latitude = population1_latlng[population1_latlng['Country Name'] == country_dropdown]['Latitude']
        Country_latitude = float(Country_latitude.to_string(index=False))
        #Country_latitude = float(Country_latitude)
        
        Country_longitude = population1_latlng[population1_latlng['Country Name'] == country_dropdown]['Longitude']
        Country_longitude = float(Country_longitude.to_string(index=False))
        
        
        locations = [go.Scattermapbox(    
                lon = population1_latlng['Longitude'],
                lat = population1_latlng['Latitude'],
                mode='markers',
                marker=go.scattermapbox.Marker(size=population1_latlng['scale']*5,
                                               color=population1_latlng['scale']),
                hoverinfo='text',
                hovertext=
                '<b>Country Name</b>:' + population1_latlng['Country Name'].astype(str) + '<br>' +
                '<b>Total Popultation:' + population1_latlng[year].astype(str)   
                
            )]
        
        layout = go.Layout(
                hovermode='x',
                paper_bgcolor='#1f2c56',
                plot_bgcolor='#1f2c56',
               margin=dict(r=10, l =10, b = 0, t = 0),
                mapbox=dict(
                    accesstoken=secret_token,
                    center=dict(
                        lat=Country_latitude,
                        lon=Country_longitude
                    ),
                    zoom=11.5,
                    bearing=0,
                    pitch=0,
                    style='dark'
                ),
                autosize=True
            )
        
        fig = go.Figure(data=locations, layout=layout)
        return fig

@app.callback(Output('line_chart', 'figure'),
              [Input('country_dropdown','value')])
def updatecard(country_dropdown):
    if country_dropdown != 'ALL':        
        years = [str(x) for x in range(1961, 2022)]
        pop = population[population['Country Name']==country_dropdown]
        Total = []
        Gender = []
        Y = []
        for year in years:
            total_pop = pop[year].to_string(index=False)
            Total.append(total_pop)
            Gender.append('ALL')
            Y.append(year)
        
        pop_mal = Male_population[Male_population['Country Name']==country_dropdown]
        for year in years:
            male_pop = pop_mal[year].to_string(index=False)
            Total.append(male_pop)
            Gender.append('MALE')
            Y.append(year)
                    
        pop_fem = Female_population[Female_population['Country Name']==country_dropdown]
        for year in years:
            female_pop = pop_fem[year].to_string(index=False)
            Total.append(female_pop)
            Gender.append('FEMALE')
            Y.append(year)
        years = [int(y) for y in years]
        Total = [float(t) for t in Total]  
        df_total = pd.DataFrame({'Year':Y,'Population':Total,'Gender':Gender})
        fig = px.line(df_total, x="Year", y="Population", 
#                        facet_col="Gender", 
                        color='Gender', symbol="Gender",
                        template='plotly_dark')
        fig.update_layout(title_text='Population Trend for '+
                          country_dropdown + 
                          '(1961-2021)', 
                          title_x=0.5,  
                          title_font_color= 'white')
        return fig
    else:
        years = [str(x) for x in range(1961, 2022)]
        Total = []
        Gender = []
        Y = []
        for year in years:
            total_pop = population[population['Country Code']=='WLD'][year]
            #total_pop = population[yea].sum()
            Total.append(total_pop)
            Gender.append('ALL')
            Y.append(year)

        for year in years:
            #male_pop = Male_population[year].sum()
            male_pop = Male_population[Male_population['Country Code']=='WLD'][year]
            Total.append(male_pop)
            Gender.append('MALE')
            Y.append(year)
                    
        for year in years:
            #female_pop = Female_population[year].sum()
            female_pop = Female_population[Female_population['Country Code']=='WLD'][year]
            Total.append(female_pop)
            Gender.append('FEMALE')
            Y.append(year)
        years = [int(y) for y in years]
        Total = [float(t) for t in Total]  
        df_total = pd.DataFrame({'Year':Y,'Population':Total,'Gender':Gender})
        fig = px.line(df_total, x="Year", y="Population", 
#                        facet_col="Gender", 
                        color='Gender', symbol="Gender",
                        template='plotly_dark')
        fig.update_layout(title_text='Population Trend for ALL Countries(1961-2021)', 
                          title_x=0.5,  
                          title_font_color= 'white')

        return fig

@app.callback([Output('Total_Card', 'children'),
               Output('percentage_tot', 'children')],
              [Input('my_dropdown','value'),
               Input('country_dropdown','value')])
def updatecard(my_dropdown,country_dropdown):
    if country_dropdown == 'ALL':
        year = ''.join(my_dropdown)
        previous_year = int(year) - 1
        previous_year = str(previous_year)
        Total = numerize.numerize(float(population[population['Country Code']=='WLD'][year].to_string(index=False)))
        #Total = numerize.numerize(population[year].sum())
        #Total_Current = population[year].sum()
        #Total_previous =  population[previous_year].sum()
        
        Total_Current = float(population[population['Country Code']=='WLD'][year].to_string(index=False))
        Total_previous =  float(population[population['Country Code']=='WLD'][previous_year].to_string(index=False))
        
        percentage_Change = ((Total_Current-Total_previous)/Total_previous) * 100.0
        
        if percentage_Change > 0:
            percentage_Change = "{:.2f}".format(percentage_Change)
            return Total,html.H4(percentage_Change + "% vs PY",className="bi bi-caret-up-fill text-success")
        else:
            percentage_Change = "{:.2f}".format(percentage_Change)
            return Total,html.H4(percentage_Change + "% vs PY",className="bi bi-caret-down-fill text-danger")
    else:
        year = ''.join(my_dropdown)
        previous_year = int(year) - 1
        previous_year = str(previous_year)
        strr = country_dropdown
        
        Country_Total = population[population['Country Name'] == country_dropdown][year]
        Country_Year = Country_Total.to_string(index=False)
        Country_Year =  float(Country_Year)
        Total = numerize.numerize(Country_Year)
  
        Total_Current = population[population['Country Name'] == country_dropdown][year]        
        Total_previous = population[population['Country Name'] == country_dropdown][previous_year]
        percentage_Change = ((Total_Current-Total_previous)/Total_previous) * 100.0
        percentage_Change = float(percentage_Change)
        
        if percentage_Change > 0:
            percentage_Change = "{:.2f}".format(percentage_Change)
            return Total,html.H4(percentage_Change + "% vs PY",className="bi bi-caret-up-fill text-success")
        else:
            percentage_Change = "{:.2f}".format(percentage_Change)
            return Total,html.H4(percentage_Change + "% vs PY",className="bi bi-caret-down-fill text-danger")


@app.callback([Output('Male_Card', 'children'),
               Output('percentage_M', 'children')],
              [Input('my_dropdown','value'),
               Input('country_dropdown','value')])
def updatecard(my_dropdown,country_dropdown):
    if country_dropdown == 'ALL':
        year = ''.join(my_dropdown)
        previous_year = int(year) - 1
        previous_year = str(previous_year)

        Male_Total = numerize.numerize(float(Male_population[Male_population['Country Code']=='WLD'][year].to_string(index=False)))
        Male_Current = float(Male_population[Male_population['Country Code']=='WLD'][year].to_string(index=False))
        Male_previous =  float(Male_population[Male_population['Country Code']=='WLD'][previous_year].to_string(index=False))
        percentage_Change = ((Male_Current-Male_previous)/Male_previous) * 100.0

        if percentage_Change > 0:
            percentage_Change = "{:.2f}".format(percentage_Change)
            return Male_Total,html.H4(percentage_Change + "% vs PY",className="bi bi-caret-up-fill text-success")
        else:
            percentage_Change = "{:.2f}".format(percentage_Change)
            return Male_Total,html.H4(percentage_Change + "% vs PY",className="bi bi-caret-down-fill text-danger")
    else:
        year = ''.join(my_dropdown)
        previous_year = int(year) - 1
        previous_year = str(previous_year)
        #strr = country_dropdown
        
        Country_Total = Male_population[Male_population['Country Name'] == country_dropdown][year]
        Country_Year = Country_Total.to_string(index=False)
        Country_Year =  float(Country_Year)
        Total = numerize.numerize(Country_Year)

  
        Total_Current = Male_population[Male_population['Country Name'] == country_dropdown][year]        
        Total_previous = Male_population[Male_population['Country Name'] == country_dropdown][previous_year]
        percentage_Change = ((Total_Current-Total_previous)/Total_previous) * 100.0
        percentage_Change = float(percentage_Change)
        
        if percentage_Change > 0:
            percentage_Change = "{:.2f}".format(percentage_Change)
            return Total,html.H4(percentage_Change + "% vs PY",className="bi bi-caret-up-fill text-success")
        else:
            percentage_Change = "{:.2f}".format(percentage_Change)
            return Total,html.H4(percentage_Change + "% vs PY",className="bi bi-caret-down-fill text-danger")        
                
@app.callback([Output('Female_Card', 'children'),
               Output('percentage_F', 'children')],
              [Input('my_dropdown','value'),
               Input('country_dropdown','value')])
def updatecard(my_dropdown,country_dropdown):
    if country_dropdown == 'ALL':
        year = ''.join(my_dropdown)
        previous_year = int(year) - 1
        previous_year = str(previous_year)

        Female_Total = numerize.numerize(float(Female_population[Female_population['Country Code']=='WLD'][year].to_string(index=False)))
        Female_Current = float(Female_population[Female_population['Country Code']=='WLD'][year].to_string(index=False))
        Female_previous =  float(Female_population[Female_population['Country Code']=='WLD'][previous_year].to_string(index=False))
        
        percentage_Change = ((Female_Current-Female_previous)/Female_previous) * 100.0

        if percentage_Change > 0:
            percentage_Change = "{:.2f}".format(percentage_Change)
            return Female_Total,html.H4(percentage_Change + "% vs PY",className="bi bi-caret-up-fill text-success")
        else:
            percentage_Change = "{:.2f}".format(percentage_Change)
            return Female_Total,html.H4(percentage_Change + "% vs PY",className="bi bi-caret-down-fill text-danger")
    else:
        year = ''.join(my_dropdown)
        previous_year = int(year) - 1
        previous_year = str(previous_year)
        #strr = country_dropdown
        
        Country_Total = Female_population[Female_population['Country Name'] == country_dropdown][year]
        Country_Year = Country_Total.to_string(index=False)
        Country_Year =  float(Country_Year)
        Total = numerize.numerize(Country_Year)

  
        Total_Current = Female_population[Female_population['Country Name'] == country_dropdown][year]        
        Total_previous = Female_population[Female_population['Country Name'] == country_dropdown][previous_year]
        percentage_Change = ((Total_Current-Total_previous)/Total_previous) * 100.0
        percentage_Change = float(percentage_Change)
        
        if percentage_Change > 0:
            percentage_Change = "{:.2f}".format(percentage_Change)
            return Total,html.H4(percentage_Change + "% vs PY",className="bi bi-caret-up-fill text-success")
        else:
            percentage_Change = "{:.2f}".format(percentage_Change)
            return Total,html.H4(percentage_Change + "% vs PY",className="bi bi-caret-down-fill text-danger")        
                
if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=8050)