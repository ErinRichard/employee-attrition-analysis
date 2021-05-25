############################# IMPORT DEPENDENCIES ############################

from os import X_OK
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from numpy.lib.function_base import _diff_dispatcher, select
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objs as go
import seaborn as sns
import plotly.figure_factory as ff

from emp_attrition import app
import dash_bootstrap_components as dbc

# for more complicated dashboard, can define dccs before the layout



############################## READ & CLEAN DATA ############################

# Read in dataset as a dataframe
df = pd.read_csv('ibm_emp_att_dataset.csv')
# print(df.head())

# Make copy of the dataframe - to maintain original
# Because will change Yes/No values in Attrition column to numerical values
ea_rev = df.copy(deep = True)
# ea_rev.head()

# Remove EmployeeCount and StandardHours columns for heatmap
# Otherwise these produce blank spaces within heatmap b/c these columns have the exact same value in each row
ea_rev.drop(['EmployeeCount', 'StandardHours'], axis=1, inplace=True)
# ea_rev.head()

# Change Attrition values from text to numerical
ea_rev["Attrition"]= ea_rev["Attrition"].replace("Yes", 1)
ea_rev["Attrition"]= ea_rev["Attrition"].replace("No", 0)
# ea_rev.head()

# This syntax to change values works in matplotlib, but doesn't work in plotly:
# ea_rev.Attrition.replace({"Yes":1, "No": 0}, inplace=True)

# Export to csv to confirm above changes (drops and value changes)
# Works!!
# ea_rev.to_csv('csv_test.csv')

# Make another copy of data frame to update BusinessTravel values to numeric
df_trvl = ea_rev.copy(deep = True)

# Change BusinessTravel values from text to numerical - for calcs and to get into the Heatmap
df_trvl["BusinessTravel"]= df_trvl["BusinessTravel"].replace("Non-Travel", 1)
df_trvl["BusinessTravel"]= df_trvl["BusinessTravel"].replace("Travel_Frequently", 2)
df_trvl["BusinessTravel"]= df_trvl["BusinessTravel"].replace("Travel_Rarely", 3)

# Confirming Changes - Works!!
# df_trvl.to_csv('df_trvl.csv')

# Copy dataframe to shorten HR & R&D Dept values for charting purposes
dept_shorten = df_trvl.copy(deep = True)


# Shorten HR & R&D Dept values
dept_shorten["Department"]= dept_shorten["Department"].replace("Human Resources", "HR")
dept_shorten["Department"]= dept_shorten["Department"].replace("Research & Development", "R & D")

# Confirm - works!
# dept_shorten.to_csv('dept_shorten.csv')


# Change Overtime values from text to numerical
dept_shorten["OverTime"]= dept_shorten["OverTime"].replace("Yes", 1)
dept_shorten["OverTime"]= dept_shorten["OverTime"].replace("No", 0)
# ea_rev.head()


# Create income groups for monthly income ranges & populate new column with appropriate grouping
def make_monthly_income_groups(monthly_income):
    if 1000 <= monthly_income and 2000 > monthly_income:
        return '$1,000-$1,999'
    elif 2000 <= monthly_income and 3000 > monthly_income:
        return '$2,000-$2,999'
    elif 3000 <= monthly_income and 4000 > monthly_income:
        return '$3,000-$3,999'
    elif 4000 <= monthly_income and 5000 > monthly_income:
        return '$4,000-$4,999'
    elif 5000 <= monthly_income and 6000 > monthly_income:
        return '$5,000-$5,999'
    elif 6000 <= monthly_income and 7000 > monthly_income:
        return '$6,000-$6,999'
    elif 7000 <= monthly_income and 8000 > monthly_income:
        return '$7,000-$7,999'
    elif 8000 <= monthly_income and 9000 > monthly_income:
        return '$8,000-$8,999'
    elif 9000 <= monthly_income and 10000 > monthly_income:
        return '$9,000-$9,999'
    elif 10000 <= monthly_income:
        return '$10,000 or more'

# Create a new column called monthly_income_group
df_trvl['monthly_income_group'] = df_trvl['MonthlyIncome'].apply(make_monthly_income_groups)

# Check new column groupings
# df_trvl.to_csv('checking_inc_groups.csv')



# Make new copy of data frame to create commute groups
commute_df = ea_rev.copy(deep = True)

# Create Commute Groups
def make_commute_groups(distance):
    if 1 <= distance and 5 > distance:
        return '1 to 5 miles'
    elif 5 <= distance and 10 > distance:
        return '6 to 10 miles'
    elif 10 <= distance and 20 > distance:
        return '11 to 20 miles'
    elif 20 <= distance:
        return 'Over 20 miles'

# Create a new column called CommuteGroup
commute_df['CommuteGroup'] = commute_df['DistanceFromHome'].apply(make_commute_groups)

# Confirm change
# commute_df[['Attrition','CommuteGroup']].head()

# Check count of new groupings
# commute_group_count = commute_df.groupby(['CommuteGroup','Attrition']).count()
# commute_df.groupby('CommuteGroup', as_index = False).count()


# Make another copy of data frame to update Education values from # to Text
df_educ = df_trvl.copy(deep = True)

# Change Education values from numerical to text
df_educ["Education"]= df_educ["Education"].replace(1, "Below College")
df_educ["Education"]= df_educ["Education"].replace(2, "College")
df_educ["Education"]= df_educ["Education"].replace(3, "Bachelor")
df_educ["Education"]= df_educ["Education"].replace(4, "Master")
df_educ["Education"]= df_educ["Education"].replace(5, "Doctor")


# Confirm above value changes - Works!!
# df_educ.to_csv('csv_test.csv')


# Make another copy of data frame to Rename Satisfaction Columns
df_satis_rev = df.copy(deep = True)

# Rename Satisfaction Columns-adding a space between words to improve readability in Satisfactoin chart display
df_satis_rev.rename(columns={"EnvironmentSatisfaction": "Environment Satisfaction", "JobInvolvement": "Job Involvement", "JobSatisfaction": "Job Satisfaction", "RelationshipSatisfaction": "Relationship Satisfaction"}, inplace=True)

# Confirm above changes - Works!!
# df_satis_rev.to_csv('df_satis_rev.csv')


# Make a copy of data frame to update PerformanceRating values from # to Text
perf_rating_df = df_trvl.copy(deep = True)

# Change Education values from numerical to text
perf_rating_df["PerformanceRating"]= perf_rating_df["PerformanceRating"].replace(1, "Low")
perf_rating_df["PerformanceRating"]= perf_rating_df["PerformanceRating"].replace(2, "Good")
perf_rating_df["PerformanceRating"]= perf_rating_df["PerformanceRating"].replace(3, "Excellent")
perf_rating_df["PerformanceRating"]= perf_rating_df["PerformanceRating"].replace(4, "Outstanding")


# Make a copy of data frame to update WorkLifeBalance values from # to Text
work_balance_df = df_trvl.copy(deep = True)

# Change Education values from numerical to text
work_balance_df["WorkLifeBalance"]= work_balance_df["WorkLifeBalance"].replace(1, "Bad")
work_balance_df["WorkLifeBalance"]= work_balance_df["WorkLifeBalance"].replace(2, "Good")
work_balance_df["WorkLifeBalance"]= work_balance_df["WorkLifeBalance"].replace(3, "Better")
work_balance_df["WorkLifeBalance"]= work_balance_df["WorkLifeBalance"].replace(4, "Best")


########### CREATE CHART VARIABLES & STATIC (NON-CALLBACK) CHARTS ############

### Start of Calc for Card 2 in Top Row (Overall Percent of Attrition) ###

# Calculate overall attrition percentage rate
agg_att_avg = df_trvl["Attrition"].mean()

# Add formatting as % with 0 decimals
percentage_attrition = "{:.0%}".format(agg_att_avg)

### End of Calc for Card 2 in Top Row (Overall Percent of Attrition) ###


### Start of Calc for Card 3 in Top Row (Avg Length of Service) ###

# Calculate avg length of services in years
avg_yrs_svc = df_trvl["YearsAtCompany"].describe()['mean']

# Format to remove decimal
avg_yrs_format = "{:.0f}".format(avg_yrs_svc)

### End of Calc for Card 3 in Top Row (Avg Length of Service) ###



### Start of Monthly Income vs. Attrition Line Chart ###
# Not using callbacks for this chart

# Count Monthly Income & set to new column
inc_attrition=df.groupby(['MonthlyIncome','Attrition']).apply(lambda x:x['MonthlyIncome'].count()).reset_index(name='MoIncomeCounts')

# Round Monthly Income Rates
inc_attrition['MonthlyIncome']=round(inc_attrition['MonthlyIncome'],-3)

# Count Monthly Income again based on rounding and update MoIncomeCounts
inc_attrition=inc_attrition.groupby(['MonthlyIncome','Attrition']).apply(lambda x:x['MonthlyIncome'].count()).reset_index(name='MoIncomeCounts')

# Populate Line Chart Based on Rounded Income & Counts of those values
fig_income1a=px.line(inc_attrition,x='MonthlyIncome',y='MoIncomeCounts',color='Attrition',title='Monthly Income vs. Attrition')

fig_income1a.update_layout(
transition_duration=500,
# margin=dict(l=20, r=20, t=70, b=90),
paper_bgcolor="LightSteelBlue",
# font=dict(size=12),
font_color="black",
title_font_color="black",
# title_font=dict(size=16),
legend_title_font_color="black",
legend_title_text="Attrition",
title_x=0.5, #centers the chart title
xaxis_title="Monthly Income",
yaxis_title="Count"
)

# Footnote/caption for chart
# fig_income1a_note = 'The highest rate of attrition based on monthly income is<br>among employees earning less than $5k per month.'

# fig_income1a.add_annotation(
#     showarrow=False,
#     text=fig_income1a_note,
#     font=dict(size=9), 
#     xref='paper',
#     x=0.5,
#     yref='paper',
#     y=-0.30,
#     align="center",
#     )

### End of Monthly Income vs. Attrition Line Chart ###


### Start of Salary Increase vs. Attrition Line Chart ###
# Not using callbacks for this chart

# Group by PercentSalaryHike and count the values
df_percent_salary_increase=df.groupby(['PercentSalaryHike','Attrition']).apply(lambda x:x['PercentSalaryHike'].count()).reset_index(name='Count')

# Use the count of PercentSalaryHike & Attrition values to populate the line chart
fig_percent_salary_increase=px.line(df_percent_salary_increase,x='PercentSalaryHike',y='Count',color='Attrition',title='Percent Salary Increase vs. Attrition')

fig_percent_salary_increase.update_layout(
transition_duration=500,
# margin=dict(l=20, r=20, t=70, b=90),
paper_bgcolor="LightSteelBlue",
# font=dict(size=12),
font_color="black",
title_font_color="black",
# title_font=dict(size=16),
legend_title_font_color="black",
legend_title_text="Attrition",
title_x=0.5, #centers the chart title
xaxis_title="Percent Salary Increase",
yaxis_title="Count"
)

# Add footnote/caption to chart
# fig_percent_salary_increase_note = "Higher attrition rates are associated with lower percent salary increases."

# fig_percent_salary_increase.add_annotation(
#     showarrow=False,
#     text=fig_percent_salary_increase_note,
#     font=dict(size=11), 
#     xref='paper',
#     x=0.5,
#     yref='paper',
#     y=-0.30,
#     align="center",
#     )

### End of Percent Salary Increase vs. Attrition Line Chart ###


### Start of Stock Options vs. Attrition Line Chart ###
# Not using callbacks for this chart

# Group by StockOptionLevel and count the values
df_stock_options=df.groupby(['StockOptionLevel','Attrition']).apply(lambda x:x['StockOptionLevel'].count()).reset_index(name='Count')

# Use the count of StockOptionLevel & Attrition values to populate the line chart
fig_stock_options=px.line(df_stock_options,x='StockOptionLevel',y='Count',color='Attrition',title='Stock Option Level vs. Attrition')

fig_stock_options.update_layout(
transition_duration=500,
# margin=dict(l=20, r=20, t=70, b=90),
paper_bgcolor="LightSteelBlue",
# font=dict(size=12),
font_color="black",
title_font_color="black",
# title_font=dict(size=16),
legend_title_font_color="black",
legend_title_text="Attrition",
title_x=0.5, #centers the chart title
xaxis_title="Stock Option Level",
yaxis_title="Count",
# The xaxis = dict below sets the x-axis tick marks to start at 0 and increment by 1 in whole numbers
xaxis = dict(
    tickmode = 'linear',
    tick0 = 0,
    dtick = 1
    )
)

# Add footnote/caption to chart
# fig_stock_options_note = "Higher attrition rates are associated with lower stock option levels."

# fig_stock_options.add_annotation(
#     showarrow=False,
#     text=fig_stock_options_note,
#     font=dict(size=11), 
#     xref='paper',
#     x=0.5,
#     yref='paper',
#     y=-0.30,
#     align="center",
#     )

### End of Stock Options vs. Attrition Line Chart ###


### Years Since Last Promotion vs. Attrition Line Chart Start ###
# Not using callbacks on this chart

# Group by YearsSinceLastPromotion & Attrition and count the values of YearsSinceLastPromotion
df_promotion=df.groupby(['YearsSinceLastPromotion','Attrition']).apply(lambda x:x['YearsSinceLastPromotion'].count()).reset_index(name='Count')

# Use the counts of YearsSinceLastPromotion & Attrition values to populate the line chart
fig_promotion=px.line(df_promotion,x='YearsSinceLastPromotion',y='Count',color='Attrition',title='Years Since Last Promotion vs. Attrition')

fig_promotion.update_layout(
transition_duration=500,
# margin=dict(l=20, r=20, t=70, b=90),
paper_bgcolor="LightSteelBlue",
# font=dict(size=12),
font_color="black",
title_font_color="black",
# title_font=dict(size=16),
legend_title_font_color="black",
legend_title_text="Attrition",
title_x=0.5, #centers the chart title
xaxis_title="Years Since Last Promotion",
yaxis_title="Count"
)

# fig_promotion_note = "There is increased attrition among employees who have<br>not received a promotion in the last 3 to 7 years."

# fig_promotion.add_annotation(
#     showarrow=False,
#     text=fig_promotion_note,
#     font=dict(size=11), 
#     xref='paper',
#     x=0.5,
#     yref='paper',
#     y=-0.30,
#     align="center",
#     )
### Years Since Last Promotion vs. Attrition Line Chart End ###



### Start of Years at Company vs. Attrition Line Chart ###
# Not using callbacks with this chart

# Group by YearsAtCompany and count the values
df_yrs_at_co=df.groupby(['YearsAtCompany','Attrition']).apply(lambda x:x['YearsAtCompany'].count()).reset_index(name='Count')

# Use the count of YearsAtCompany & Attrition values to populate the line chart
fig_yrs_at_co=px.line(df_yrs_at_co,x='YearsAtCompany',y='Count',color='Attrition',title='Years at Company vs. Attrition')

fig_yrs_at_co.update_layout(
transition_duration=500,
# margin=dict(l=20, r=20, t=70, b=90),
paper_bgcolor="LightSteelBlue",
# font=dict(size=12),
font_color="black",
title_font_color="black",
# title_font=dict(size=16),
legend_title_font_color="black",
legend_title_text="Attrition",
title_x=0.5, #centers the chart title
xaxis_title="Years at Company",
yaxis_title="Count"
)

# Add footnote/caption to chart
# fig_yrs_at_co_note = "Evaluating attrition against years at the company, the highest rate<br>of attrition occurs within the first four years of employment."

# fig_yrs_at_co.add_annotation(
#     showarrow=False,
#     text=fig_yrs_at_co_note,
#     font=dict(size=11), 
#     xref='paper',
#     x=0.5,
#     yref='paper',
#     y=-0.30,
#     align="center",
#     )

### Years at Company vs. Attrition Line Chart End ###


### Years in Current Role vs. Attrition Line Chart Start ###
# Not using callbacks with this chart

# Group by YearsInCurrentRole and count the values
df_current_role=df.groupby(['YearsInCurrentRole','Attrition']).apply(lambda x:x['YearsInCurrentRole'].count()).reset_index(name='Count')

# Use the count of YearsInCurrentRole & Attrition values to populate the line chart
fig_current_role=px.line(df_current_role,x='YearsInCurrentRole',y='Count',color='Attrition',title='Years in Current Role vs. Attrition')

fig_current_role.update_layout(
transition_duration=500,
# margin=dict(l=20, r=20, t=70, b=90),
paper_bgcolor="LightSteelBlue",
# font=dict(size=12),
font_color="black",
title_font_color="black",
# title_font=dict(size=16),
legend_title_font_color="black",
legend_title_text="Attrition",
title_x=0.5, #centers the chart title
xaxis_title="Years in Current Role",
yaxis_title="Count"
)

# fig_current_role_note = f'Evaluating attrition against years in current role, the highest rate of attrition occurs<br>among employees working for the company for less than 1 year or around 2 years.'

# fig_current_role.add_annotation(
#     showarrow=False,
#     text=fig_current_role_note,
#     font=dict(size=11), 
#     xref='paper',
#     x=0.5,
#     yref='paper',
#     y=-0.30,
#     align="center",
#     )
### Years in Current Role vs. Attrition Line Chart End ###


### Start of Stacked Bar - Gender & Education Level ###
# Not using callbacks on this chart

fig_gender_ed_level=px.histogram(df_educ,x='Education',y='Attrition',color='Gender',histfunc="avg", title='Average Rate of Attrition by Gender and Education Level',category_orders={"Education": ["Below College", "College", "Bachelor", "Master", "Doctor"]})

fig_gender_ed_level.update_layout(
transition_duration=500,
# margin=dict(l=20, r=20, t=70, b=90),
paper_bgcolor="LightSteelBlue",
# font=dict(size=12),
font_color="black",
title_font_color="black",
# title_font=dict(size=16),
legend_title_font_color="black",
title_x=0.5, #centers the chart title
xaxis_title="Education Level",
yaxis_title="Avg Rate of Attrition",
yaxis_tickformat = '%',
)


# fig_gender_ed_level_note = "Comparing rate of attrition against gender and level of education, the highest rate of attrition among women are those with an education level below college (18%). The highest rate of attrition among men are those with education levels below college and bachelor (both 18%)."

# fig_gender_ed_level.add_annotation(
#     showarrow=False,
#     text=fig_gender_ed_level_note,
#     font=dict(size=11), 
#     xref='paper',
#     x=0.5,
#     yref='paper',
#     y=-0.30,
#     align="center",
#     )

### End of Stacked Bar - Gender & Education Level ###


### Start of Stacked Bar - Gender & Education Field ###
fig_gender_ed_field=px.histogram(df_trvl,x='EducationField',y='Attrition',color='Gender',histfunc="avg", title='Average Rate of Attrition by Gender and Field of Education')

fig_gender_ed_field.update_layout(
transition_duration=500,
# margin=dict(l=20, r=20, t=70, b=90),
paper_bgcolor="LightSteelBlue",
# font=dict(size=12),
font_color="black",
title_font_color="black",
# title_font=dict(size=16),
legend_title_font_color="black",
title_x=0.5, #centers the chart title
xaxis_title="Field of Education",
yaxis_title="Avg Rate of Attrition",
yaxis_tickformat = '%',
)


# fig_gender_ed_field_note = "Comparing rate of attrition against gender and field of education, the highest rate of attrition among women are those with education in HR (38%). The highest rate of attrition among men are those with a Technical Degree (28%)."

# fig_gender_ed_field.add_annotation(
#     showarrow=False,
#     text=fig_gender_ed_field_note,
#     font=dict(size=11), 
#     xref='paper',
#     x=0.5,
#     yref='paper',
#     y=-0.30,
#     align="center",
#     )

### End of Stacked Bar - Gender & Education Level ###


### Start of Contents for Card 1 in Row 1 ###
# Total number of employees
card_text_1 = df["EmployeeCount"].sum()



# Heatmap to show correlation between all features in the dataset
# Useful to determine which features to focus on in model/analysis
# As the color becomes darker in either direction, that means that those variables are more highly correlated and should not be paired together in the same model
# https://medium.com/@connor.anderson_42477/hot-or-not-heatmaps-and-correlation-matrix-plots-940088fa2806
# fig4 = px.imshow(ea_rev.corr(),width=1000, height=1000)
fig4 = px.imshow(df_trvl.corr(),width=1000, height=1000)
# fig4 = ff.create_annotated_heatmap(ea_rev)

# fig4 = px.imshow(df.corr())


############################## START PAGE LAYOUT ##############################

# style arguments for the sidebar (chart parameters/selections)
SIDEBAR_STYLE = {
    'position': 'fixed',
    'top': 0,
    'left': 0,
    'bottom': 0,
    'width': '20%',
    'padding': '20px 10px',
    'background-color': '#f8f9fa'
}


# style arguments for main page contents
CONTENT_STYLE = {
    'margin-left': '25%',
    'margin-right': '5%',
    'top': 0,
    'padding': '20px 10px'
}

TEXT_STYLE = {
    'textAlign': 'center',
    'color': '#191970'
}

CARD_TEXT_STYLE = {
    'textAlign': 'center',
    'color': '#0074D9',
    # 'fontSize': 25
}


CARD_INFO_STYLE = {
    'textAlign': 'center',
    'color': '#0074D9',
    # 'fontSize': 20
}

SUMMARY_STYLE = {
    # 'fontSize': 14
}

# Add shadow effect to the card placeholders for charts & info cards at top
CARD_STYLE = {
    'box-shadow': '8px 8px 8px grey',
}


### Chart controls in the sidebar - Start ###
controls = dbc.FormGroup(
    [
        html.P('Select to update Avg Attrition vs. Commute chart:', style={
            'font-size': '11px',
        }),
        dbc.Card([dbc.Checklist(
            id='commute_group_selections',
            style={'font-size': '11px'},
            options=[{
            'label': '1 to 5 miles',
            'value': '1 to 5 miles'
        },
            {
                'label': '6 to 10 miles',
                'value': '6 to 10 miles'
            },
            {
                'label': '11 to 20 miles',
                'value': '11 to 20 miles'
            },
                        {
                'label': 'Over 20 miles',
                'value': 'Over 20 miles'
            }
        ],
            value=['1 to 5 miles', '6 to 10 miles', '11 to 20 miles', 'Over 20 miles'],
            inline=True,
        )]),

        html.Br(),
        html.P('Select to update Breakout by Travel Freq chart:', style={
            'font-size': '11px',
        }),
        dbc.Card([dbc.Checklist(
            id='emp-attributes-checkbox-1',
            style={'font-size': '11px'},
            options=[{
            'label': 'No Travel',
            'value': 'Non-Travel'
        },
            {
                'label': 'Travel Rarely',
                'value': 'Travel_Rarely'
            },
            {
                'label': 'Travel Frequently',
                'value': 'Travel_Frequently'
            }
            ],
            value=['Non-Travel', 'Travel_Rarely', 'Travel_Frequently'],
            inline=True
        )]),

        
        html.Br(),
        html.P('Select to update Avg Rate of Attrition vs. Overtime chart:' , style={
            'font-size': '11px',
        }),
        
        dbc.Card([dbc.Checklist(
            id='ot-checkbox-1',
            style={'font-size': '11px'},
            options=[{
            'label': 'Yes',
            'value': 'Yes'
        },
            {
                'label': 'No',
                'value': 'No'
            },

            ],
            value=['Yes', 'No'],
            inline=True
        )]),

 
        html.Br(),
        html.P('Select to update Rate of Attrition by Job Role chart:', style={
            'font-size': '11px',
        }),
        dbc.Card([dbc.Checklist(
            id='jobrole-checkboxes',
            style={'font-size': '11px'},
            options=[{
                'label': 'Healthcare Rep',
                'value': 'Healthcare Representative'
            },
                {
                    'label': 'HR',
                    'value': 'Human Resources'
                },
                {
                    'label': 'Lab Tech',
                    'value': 'Laboratory Technician'
                },
                {
                    'label': 'Manager',
                    'value': 'Manager'
                },
                {
                    'label': 'Mfg Dir',
                    'value': 'Manufacturing Director'
                },
                {
                    'label': 'Research Dir',
                    'value': 'Research Director'
                },
                {
                    'label': 'Research Scientist',
                    'value': 'Research Scientist'
                },                                                
                {
                    'label': 'Sales Exec',
                    'value': 'Sales Executive'
                },
                {
                    'label': 'Sales Rep',
                    'value': 'Sales Representative'
                }
            ],
            value=['Healthcare Representative', 'Human Resources', 'Laboratory Technician', 'Manager', 'Manufacturing Director', 'Research Director', 'Research Scientist', 'Sales Executive', 'Sales Representative'],
            inline=True,
        )]),
        
        
            html.Br(),
            html.P('Select to update Percent Breakout by Dept chart:', style={
                'font-size': '11px',
        }),
        dbc.Card([dbc.Checklist(
            id='dept-pie-checkbox',
            style={'font-size': '11px'},
            options=[{
                'label': 'HR',
                'value': 'Human Resources'
            },
                {
                    'label': 'R&D',
                    'value': 'Research & Development'
                },
                {
                    'label': 'Sales',
                    'value': 'Sales'
                }
            ],
            value=['Human Resources', 'Research & Development', 'Sales'],
            inline=True
        )]),
            html.Br(),
            html.P('Select to update Avg Rate of Attrition by Dept chart: ', style={
             'font-size': '11px',
        }),
            dbc.Card([dbc.Checklist(
            id='dept-dropdown',
            style={'font-size': '11px'},
            options=[{
                'label': 'HR',
                'value': 'Human Resources'
            },
                {
                    'label': 'R&D',
                    'value': 'Research & Development'
                },
                {
                    'label': 'Sales',
                    'value': 'Sales'
                }
            ],
            value=['Human Resources', 'Research & Development', 'Sales'],
            inline=True
        )]),
           
            html.Br(),
            html.P('Select to update Avg Rate of Attrition vs. Work Life Balance chart: ', style={
            'font-size': '11px',
        }),
            dbc.Card([dbc.Checklist(
            id='work-balance-checklist',
            style={'font-size': '11px'},
            options=[{
                    'label': 'Bad (1)',
                    'value': 'Bad'
                },
                {
                    'label': 'Good (2)',
                    'value': 'Good'
                },
                {
                    'label': 'Better (3)',
                    'value': 'Better'
                },
                {
                    'label': 'Best (4)',
                    'value': 'Best'
                }
            ],
            value=['Bad', 'Good', 'Better', 'Best'],
            inline=True
        )]),

            html.Br(),
            html.P('Select to update Avg Rate of Attrition vs. Performance Rating chart: ', style={
            'font-size': '11px',
        }),
            dbc.Card([dbc.Checklist(
            id='perf-rating-checkbox',
            style={'font-size': '11px'},
            options=[{
                    'label': 'Excellent (3)',
                    'value': 'Excellent'
                },
                {
                    'label': 'Outstanding (4)',
                    'value': 'Outstanding'
                }
            ],
            value=['Excellent', 'Outstanding'],
            inline=True
        )]),
            
            html.Br(),
            html.P('Select to update Attrition vs. Satisfaction chart: ', style={
            'font-size': '11px'
        }),
            dbc.Card([dcc.Dropdown(
            id="satisfaction-x-axis",
            style={'font-size': '11px'},
            options=[{
                'label': 'Environment Satisfaction',
                'value': 'Environment Satisfaction'
            },
                {
                    'label': 'Job Involvement',
                    'value': 'Job Involvement'
                },
                {
                    'label': 'Job Satisfaction',
                    'value': 'Job Satisfaction'
                },
                {
                    'label': 'Relationship Satisfaction',
                    'value': 'Relationship Satisfaction'
                }
            ],
            value='Environment Satisfaction'
        )]),  
    ]
)

### Chart controls in the sidebar - End ###


### Sidebar Layout - Start ###
sidebar = html.Div(
    [
        html.H2('Chart Selections', style=TEXT_STYLE),
        html.Hr(),
        controls
    ],
    style=SIDEBAR_STYLE,
)

### Sidebar Layout - End ###


# First row start - contains four cards
content_first_row = dbc.Row([
    dbc.Col(
        dbc.Card(
            [
                dbc.CardBody(
                    [
                        html.H4(id='card_title_1', children=['Total Number of Employees:'], className='card-title',
                                style=CARD_TEXT_STYLE),
                        html.P(id='card_text_1', children=[df["EmployeeCount"].sum()], style=CARD_INFO_STYLE),
                    ]
                )
            ],
            style = CARD_STYLE,
        ),
        md=4, style={
            'paddingBottom': '3%'
        }
    ),
    dbc.Col(
        dbc.Card(
            [

                dbc.CardBody(
                    [
                        html.H4('Overall Percent of Attrition:', className='card-title', style=CARD_TEXT_STYLE),
                        html.P(percentage_attrition, style=CARD_INFO_STYLE),
                    ]
                ),
            ],
            style = CARD_STYLE,

        ),
        md=4, style={
            'paddingBottom': '3%'
        }
    ),
    # dbc.Col(
    #     dbc.Card(
    #         [
    #             dbc.CardBody(
    #                 [
    #                     html.H4('Attrition Within First 2 Years:', className='card-title', style=CARD_TEXT_STYLE),
    #                     html.P(test_calc, style=CARD_INFO_STYLE),
    #                 ]
    #             ),
    #         ],
    #         style = CARD_STYLE,

    #     ),
    #     md=3, style={
    #         'paddingBottom': '3%'
    #     }
    # ),
    dbc.Col(
        dbc.Card(
            [
                dbc.CardBody(
                    [
                        html.H4('Average Employee Yrs at Company:', className='card-title', style=CARD_TEXT_STYLE),
                        html.P(avg_yrs_format, style=CARD_INFO_STYLE),
                    ]
                ),
            ],
            style = CARD_STYLE,
        ),
        md=4
    )
])

### First Row End ###


### Second Row Start - contains three charts ###
content_second_row = dbc.Row(
    [
        # Line Chart - Monthly Income vs. Attrition
        dbc.Col(
            dcc.Graph(id='fig_income1a', figure=fig_income1a, style = CARD_STYLE), md=4, style={
            'paddingBottom': '3%'
        }
        ),

        # Line Chart - Percent of Salary Increase vs. Attrition
        dbc.Col(
            dcc.Graph(id='fig_percent_salary_increase', figure=fig_percent_salary_increase, style = CARD_STYLE), md=4, style={
            'paddingBottom': '3%'
        }
        ),

        # Line Chart - Stock Options vs. Attrition
        dbc.Col(
            dcc.Graph(id='fig_stock_options', figure=fig_stock_options, style = CARD_STYLE), md=4, style={
            'paddingBottom': '3%'
        }
        )
    ]
)

### Second Row End ###


### Row 2b Start - contains three charts ###
content_row_2b = dbc.Row(
    [
        # Line Chart of Years in Current Role vs. Attrition
        dbc.Col(
            dcc.Graph(id='fig_current_role', figure=fig_current_role, style = CARD_STYLE), md=4, style={
            'paddingBottom': '3%'
        }
        ),

        # Line Chart - Years with Current Manager vs. Attrition
        dbc.Col(
            dcc.Graph(id='fig_promotion', figure=fig_promotion, style = CARD_STYLE), md=4, style={
            'paddingBottom': '3%'
        }
        ),

        # Line Chart - Years at Company vs. Attrition
        dbc.Col(
            dcc.Graph(id='fig_yrs_at_co', figure=fig_yrs_at_co, style = CARD_STYLE), md=4, style={
            'paddingBottom': '3%'
        }
        )
    ]
)

### Row 2b End ###


### Third Row Start - contains three charts ###
content_third_row = dbc.Row(
    [
        # Horizontal histogram - Avg Rate of Attrition vs. Commute Distance
        dbc.Col(
            dcc.Graph(id='commute-chart', style = CARD_STYLE), md=4, style={
            'paddingBottom': '3%'
        }
        ),

        # Pie chart - Attrition Percent Breakout by Job Travel 
        dbc.Col(
            dcc.Graph(id='employee-attributes-1', style = CARD_STYLE), md=4, style={
            'paddingBottom': '3%'
        }
        ),

        # Bar chart of avg rate of attrition vs. Overtime status
        dbc.Col(
            dcc.Graph(id='ot-percent', style = CARD_STYLE), md=4, style={
            'paddingBottom': '3%'
        }
        )
    ]
)

### Third Row End ###


### Fourth Row Start - Contains 1 Chart ###
content_fourth_row = dbc.Row(
    [
        # Stacked Bar Chart - Avg Rate of Attrition by Gender & Educ Level
        dbc.Col(
            dcc.Graph(id='fig_gender_ed_level', figure=fig_gender_ed_level, style=CARD_STYLE), md=12, style={
            'paddingBottom': '3%'
        }
        )
        
    ]
)

### Fourth Row End ###


### Row 4a Start - Contains 1 Chart ###
content_row_4a = dbc.Row(
    [
        # Stacked Bar Chart - Avg Rate of Attrition by Gender & Educ Field
        dbc.Col(
            dcc.Graph(id='fig_gender_ed_field', figure=fig_gender_ed_field, style=CARD_STYLE), md=12, style={
            'paddingBottom': '3%'
        }
        )
        
    ]
)

### Row 4a End ###


### Fifth Row Start - Contains 1 Chart ###
content_fifth_row = dbc.Row(
    [
        # Horiz. bar chart of Avg Rate of Attrition by Job Role
        dbc.Col(
            dcc.Graph(id='chart-jobrole-checkbox', style=CARD_STYLE), md=12, style={
            'paddingBottom': '3%'
        }
        )
        
    ]
)

### Fifth Row End ###


### Sixth Row Start - contains 2 Charts ###
content_sixth_row = dbc.Row(
    [
        # Pie Chart of Attrition percentage breakout by Dept
        dbc.Col(
            dcc.Graph(id='dept_pct_pie', style = CARD_STYLE), md=6, style={
            'paddingBottom': '3%'
        }
        ),
        
        # Horiz. bar chart of avg rate of attrition by Dept
        dbc.Col(
            dcc.Graph(id='chart-with-dropdown', style = CARD_STYLE), md=6, style={
            'paddingBottom': '3%'
        }
        
        )
    ]
)

### Sixth Row End ###


### Seventh Row Start - contains 2 Charts ###
content_seventh_row = dbc.Row(
    [
        # Pie Chart of Attrition breakout based on WorkLifeBalance
        dbc.Col(
            dcc.Graph(id='work_balance_pie', style = CARD_STYLE), md=6, style={
            'paddingBottom': '3%'
        }
        ),
        
        # Pie Chart of Attrition breakout based on Performance Rating
        dbc.Col(
            dcc.Graph(id='perf_rating_pie', style = CARD_STYLE), md=6, style={
            'paddingBottom': '3%'
        }
        
        )
    ]
)

### Seventh Row End ###


### Bottom Row Start - Contains 1 Chart ###
content_bottom_row = dbc.Row(
    [
        # Horiz. bar chart of Avg Rate of Attrition by Job Role
        dbc.Col(
            dcc.Graph(id='satisfaction_area_chart', style=CARD_STYLE), md=12, style={
            'paddingBottom': '3%'
        }
        )
        
    ]
)

### Bottom Row End ###


# Summary row start
content_summary_row = dbc.Row([
    dbc.Col(
        dbc.Card(
            [
                dbc.CardBody(
                    [
                        html.H4(id='summary', children=['Summary:'], className='card-title',
                                style=CARD_TEXT_STYLE),
                        html.P(id='summary_text_1', children="Evaluting against pay and benefits, the highest rates of attrition are seen with the lowest monthly income, lowest percent salary increase, and lowest stock option level.", style=SUMMARY_STYLE),

                        html.P(id='summary_text_2', children="Evaluating against employee length of service and promotion status, the highest rates of attrition occur among employees working at the company for 4 years or less or have not received a promotion within the last 3 to 7 years.", style=SUMMARY_STYLE),

                        html.P(id='summary_text_3', children="Longer commute distances are related to higher levels of attrition.", style=SUMMARY_STYLE),
                        
                        html.P(id='summary_text_4', children="Roles that require rare travel make up a higher rate of overall attrition than frequent or no travel. Consideration: Is rare travel too much or not enough?", style=SUMMARY_STYLE),

                        html.P(id='summary_text_5', children="There is a 31% attrition rate among employees who worked ovetime, compared to 10% attrition for those who did not work overtime.", style=SUMMARY_STYLE),

                        html.P(id='summary_text_6', children="Job role seems to be a factor in attrition, with Sales Representative having the highest rate of attrition at 40%, followed by Laboratory Technician at 24% and HR at 23%.", style=SUMMARY_STYLE),
                    ]
                )
            ],
            style = CARD_STYLE,
        ),
        md=12, style={
            'paddingBottom': '3%'
        }
    ),

])

### Summary Row End ###

# Specify page content to include in app.layout
content = html.Div(
    [
        ### Navbar Start ###
        dbc.NavbarSimple(
        children=[
            dbc.NavItem(dbc.NavLink("Home", href="/", external_link=True)),
            dbc.NavItem(dbc.NavLink("Dashboard", href="/dashboard", external_link=True)),
        ],
        brand="Erin Richard - Employee Attrition Analysis Project",
        color="light",
        dark=False,
        ),

        ### Navbar End ###

        html.Br(),
        html.H2('Employee Attrition Analysis', style=TEXT_STYLE),
        html.Hr(),
        content_first_row,
        content_second_row,
        content_row_2b,
        content_third_row,
        content_fourth_row,
        content_row_4a,
        content_fifth_row,
        content_sixth_row,
        content_seventh_row,
        content_bottom_row,
        content_summary_row,
    ],
    style=CONTENT_STYLE
)


# specifying layout is required in order for Dash to work
app.layout = html.Div([sidebar, content])



################################## CALLBACKS ##################################

### Businesss Travel Pie Chart Start ###
@app.callback(
    Output('employee-attributes-1', 'figure'),
    [Input('emp-attributes-checkbox-1', 'value')])
def update_ee_fig(selected_ee_attribute):

    if selected_ee_attribute == []:
        return {}  # Returning this empty {} resolves a callback error that was occurring when all checklist items were unselected
    
    else:
        attribute1_df = ea_rev[ea_rev["BusinessTravel"].isin(selected_ee_attribute)]

        # Set variable to Total Count of Attrition = "Yes" (or 1)
        attrition_yes_count = sum(ea_rev["Attrition"]==1)

    # This pie chart shows percentage of attrition for each travel category as a percentage of the whole 237 employees who have left the company
    fig_ee_attributes1 = px.pie(attribute1_df, values='Attrition', names='BusinessTravel',color="BusinessTravel", title=f"Total Attrition - Percent Breakout by Job Travel (n={attrition_yes_count})")


    # This chart shows percentage of attrition within each travel category, not as a percentage of the whole -- pie chart above shows it as percentage of whole
    # fig_ee_attributes1 = px.histogram(attribute1_df, x="BusinessTravel", y="Attrition", color="BusinessTravel", title="Avg Rate of Attrition by Job Travel")

    fig_ee_attributes1.update_layout(
    transition_duration=500,
    # margin=dict(l=20, r=20, t=70, b=90),
    paper_bgcolor="LightSteelBlue",
    # font=dict(size=12),
    font_color="black",
    title_font_color="black",
    # title_font=dict(size=16),
    legend_title_font_color="black",
    legend_title_text="Travel Frequency",
    title_x=0.5, #centers the chart title
    )

    # figJobTravel_note = 'Job Roles with Rare Travel make up a higher rate of overall attrition<br>(66%) than roles with Frequent Travel (29%) or No Travel (5%).<br>Consideration: Is rare travel too much travel or not enough?'

    # fig_ee_attributes1.add_annotation(
    #     showarrow=False,
    #     text=figJobTravel_note,
    #     font=dict(size=11), 
    #     xref='paper',
    #     x=0.6,
    #     yref='paper',
    #     y=-0.30,
    #     align="center"
    #     )

    return fig_ee_attributes1

### Business Travel Pie Chart End ###


### Overtime Chart Start ###
@app.callback(
    Output('ot-percent', 'figure'),
    [Input('ot-checkbox-1', 'value')])
def update_ot_fig(selected_ot_attribute):
    if selected_ot_attribute == []:
        return {}  # Returning this empty {} resolves a callback error that was occurring when all checklist items were unselected

    else:
        ot_df = ea_rev[ea_rev["OverTime"].isin(selected_ot_attribute)]

    # Set variable to Total Count of OverTime == "Yes"
    ot_yes_count = sum(dept_shorten["OverTime"])

    # This pie chart shows percentage of attrition for each travel category as a percentage of the whole 237 employees who have left the company
    # ot_fig = px.pie(ot_df, values='Attrition', names='OverTime',color="OverTime", title=f"Total Attrition - Percent Breakout by Overtime (n={ot_yes_count})")


    # This chart shows percentage of attrition within each OverTime category, not as a percentage of the whole -- pie chart above shows it as percentage of whole
    ot_fig = px.histogram(ot_df, x="OverTime", y="Attrition", histfunc='avg', color="OverTime", title="Avg Rate of Attrition vs. Overtime Status")

    ot_fig.update_layout(
    transition_duration=500,
    # margin=dict(l=20, r=20, t=70, b=90),
    paper_bgcolor="LightSteelBlue",
    # font=dict(size=12),
    font_color="black",
    title_font_color="black",
    # title_font=dict(size=16),
    legend_title_font_color="black",
    legend_title_text="Overtime Required",
    title_x=0.5, #centers the chart title
    xaxis_title="Overtime Required",
    yaxis_tickformat = '%',
    )

    # fig_ot_note = 'There is a 31% average attrition rate among employees who worked overtime,<br>while there is a 10% average attrition rate among employees who did not work overtime.'

    # ot_fig.add_annotation(
    #     showarrow=False,
    #     text=fig_ot_note,
    #     font=dict(size=11), 
    #     xref='paper',
    #     x=0.6,
    #     yref='paper',
    #     y=-0.30,
    #     align="center",
    #     )

    return ot_fig

### Overtime Chart End ###


### Years at Company Line Chart Start ###
@app.callback(
    Output("last-promotion-chart", "figure"), 
    [Input("last-promotion-checklist", "value")])

def update_promotion_chart(last_promotion_selected):

    df_yrs_at_co=df.groupby(['YearsAtCompany','Attrition']).apply(lambda x:x['YearsAtCompany'].count()).reset_index(name='Count')

    fig_promotion=px.line(df_yrs_at_co,x='YearsAtCompany',y='Count',color='Attrition',title='Years at Company vs. Attrition')

    fig_promotion.update_layout(
    transition_duration=500,
    margin=dict(l=20, r=20, t=70, b=90),
    paper_bgcolor="LightSteelBlue",
    font=dict(size=12),
    font_color="black",
    title_font_color="black",
    title_font=dict(size=16),
    legend_title_font_color="black",
    legend_title_text="Attrition",
    title_x=0.5, #centers the chart title
    xaxis_title="Years at Company",
    yaxis_title="Count"
    )

    # Set variable to Total Count of 2 years in current role
    # two_yr_role = df[df['YearsInCurrentRole'] == 2].count()
    # two = df.groupby("Attrition").count()[["YearsInCurrentRole"]]==2
    # two_yr_role = df.groupby["YearsInCurrentRole"].count()["YearsInCurrentRole"]==2

    fig_promotion_note = f'Evaluating attrition against years in current role, the highest rate of attrition occurs<br>among employees working for the company for less than 1 year or around 2 years.'

    fig_promotion.add_annotation(
        showarrow=False,
        text=fig_promotion_note,
        font=dict(size=11), 
        xref='paper',
        x=0.5,
        yref='paper',
        y=-0.30,
        align="center",
        )

    return fig_promotion

### Years at Company Line Chart End ###


### Start of Attrition vs. Commute Chart ###
@app.callback(
    Output("commute-chart", "figure"), 
    [Input("commute_group_selections", "value")])

def update_commute_chart(commute_group_selected):
    if commute_group_selected == []:
        return {}  # Returning this empty {} resolves a callback error that was occurring when all checklist items were unselected
    
    else:
        commute_group_df = commute_df[commute_df["CommuteGroup"].isin(commute_group_selected)]
    
    
    # Create Commute vs. Attrition Chart
    # category_orders sets the display order of the bars in the chart
    fig_commute=px.histogram(commute_group_df,x='Attrition',y='CommuteGroup',color='CommuteGroup',histfunc='avg', title='Avg Rate of Attrition vs. Commute Distance', category_orders={"CommuteGroup": ["1 to 5 miles", "6 to 10 miles", "11 to 20 miles", "Over 20 miles"]})

    fig_commute.update_layout(
    transition_duration=500,
    # margin=dict(l=20, r=20, t=70, b=90),
    paper_bgcolor="LightSteelBlue",
    # font=dict(size=12),
    font_color="black",
    title_font_color="black",
    # title_font=dict(size=16),
    legend_title_font_color="black",
    legend_title_text="Commute Distance",
    title_x=0.5, #centers the chart title
    xaxis_title="Rate of Attrition",
    yaxis_title="Commute Distance",
    xaxis_tickformat = '%', #Adds % sign to xaxis ticks
    )

    # fig_commute_note = 'Based on commute distance, the highest rate of attrition is 21% for commutes over 20<br>miles, while commutes between 1 to 5 miles have the lowest average attrition rate at 14%.'

    # fig_commute.add_annotation(
    #     showarrow=False,
    #     text=fig_commute_note,
    #     font=dict(size=11), 
    #     xref='paper',
    #     x=0.55,
    #     yref='paper',
    #     y=-0.30,
    #     align="center",
    #     )

    return fig_commute

### End of Commute vs. Attrition Chart ###






### Satisfaction Bar Chart Start ###
@app.callback(
    Output("satisfaction_area_chart", "figure"), 
    [Input("satisfaction-x-axis", "value")])

def display_area(x):
    df_satisfaction=df_satis_rev.groupby(['Environment Satisfaction', 'Job Involvement', 'Job Satisfaction','Relationship Satisfaction','Attrition']).apply(lambda x:x['EmployeeCount'].count()).reset_index(name='Count')
    
    
    fig_satisfaction_area_chart = px.bar(df_satisfaction, x=x, y="Count",
        color="Attrition", barmode="stack", title=f"Attrition vs. Satisfaction Ratings")
    
    fig_satisfaction_area_chart.update_layout(
    transition={
        'duration': 500,
        'easing': 'cubic-in-out',
    },
    # margin=dict(l=20, r=20, t=70, b=90),
    paper_bgcolor="LightSteelBlue",
    # font=dict(size=12),
    font_color="black",
    title_font_color="black",
    # title_font=dict(size=16),
    legend_title_font_color="black",
    legend_title_text="Attrition",
    title_x=0.5, #centers the chart title
    xaxis_title="Satisfaction Rating",
    # yaxis_title="Count",
    # The xaxis = dict below sets the x-axis tick marks to start at 0 and increment by 1 in whole numbers
    xaxis = dict(
        tickmode = 'array', # Set to array in order to rename tick labels
        tick0 = 0,
        dtick = 1,
        tickvals = [1,2,3,4], # Position of tick labels to rename
        ticktext = ['1: Low', "2: Medium", "3: High", "4: Very High"] # rename tick labels at positions [1,2,3,4]
        )
    )
    
    return fig_satisfaction_area_chart

### Satisfaction Bar Chart End ###



### Avg Rate of Attrition by Dept horiz. bar chart Start ###
@app.callback(
    Output('chart-with-dropdown', 'figure'),
    [Input('dept-dropdown', 'value')])
def update_figure(selected_dept):

    if selected_dept == []:
        return {}  # Returning this empty {} resolves a callback error that was occurring when all checklist items were unselected
        
    # dept_df = dept_shorten[dept_shorten["Department"].isin(selected_dept)]
    else:
        dept_df = df_trvl[df_trvl["Department"].isin(selected_dept)]
    # fig100 = px.histogram(dept_df, x="Attrition", histfunc='avg', barmode="group", color="Department", title="Average Rate of Attrition by Department")

    # This chart displays horizontally - one Attrition measure for each dept
    # fig100 = px.histogram(dept_df, x="Attrition", y="Department", histfunc='avg', barmode="group", color="Department", title="Average Rate of Attrition by Department")

    fig100 = px.histogram(dept_df, x="Attrition", y="Department", histfunc='avg', barmode="group", color="Department", 
    color_discrete_map={
        "Human Resources": "red",
        "Research & Development": "green",
        "Sales": "blue"}, 
        title="Average Rate of Attrition by Department")


    fig100.update_layout(
    transition_duration=500,
    # margin=dict(l=20, r=20, t=70, b=90),
    paper_bgcolor="LightSteelBlue",
    # font=dict(size=12),
    # font_family="Courier New",
    font_color="black",
    # title_font_family="Times New Roman",
    title_font_color="black",
    # title_font=dict(size=16),
    legend_title_font_color="black",
    title_x=0.5,
    xaxis_tickformat = '%',
    )

    # fig100_note = 'Although Percent Breakout by Department indicates that R&D makes up the highest percentage of all employees who have<br>left the company, the average rate of attrition within R&D independently is 14%, compared to 21% for Sales and 19% for HR.'

    # fig100.add_annotation(
    #     showarrow=False,
    #     text=fig100_note,
    #     font=dict(size=11), 
    #     xref='paper',
    #     x=0.5,
    #     yref='paper',
    #     y=-0.30,
    #     align="center"
    #     )

    return fig100

### Avg Rate of Attrition by Dept horiz. bar chart End ###


### Avg Rate of Attrition percent by Dept Pie Chart Start ###
@app.callback(
    Output('dept_pct_pie', 'figure'),
    [Input('dept-pie-checkbox', 'value')])
def update_pie(dept_selection):

    if dept_selection == []:
        return {}  # Returning this empty {} resolves a callback error that was occurring when all checklist items were unselected
    
    else:
        dept_pct_df = df_trvl[df_trvl["Department"].isin(dept_selection)]

        # Set variable to Total Count of Attrition = "Yes" (or 1)
        attrition_yes_count = sum(dept_pct_df["Attrition"]==1)
  

    # This pie chart shows percent of total attrition by department
    # i.e. Sales has 38.8% of total attrition (92 of the 237 empls that left were from the sales department)
    fig200 = px.pie(dept_pct_df, values='Attrition', names='Department',color="Department", color_discrete_map={
        "Human Resources": "red",
        "Research & Development": "green",
        "Sales": "blue"},
        title=f"Total Attrition - Percent Breakout by Department (n={attrition_yes_count})")
   
    fig200.update_layout(
        # margin=dict(l=70, r=70, t=70, b=90),
        paper_bgcolor="LightSteelBlue",
        # font=dict(size=12),
        # font_family="Courier New",
        font_color="black",
        # title_font_family="Times New Roman",
        title_font_color="black",
        # title_font=dict(size=16),
        legend_title_font_color="black",
        legend_title_text="Department",
        title_x=0.5
    )

    # This adds annotation/caption to the chart
    # fig200_note = 'R&D is the largest department, with 65% of all employees, so it stands to reason<br>that the highest percentage of employees leaving would come from the largest department.'

    # fig200.add_annotation(
    #     showarrow=False,
    #     text=fig200_note,
    #     font=dict(size=11), 
    #     xref='paper',
    #     x=0.5,
    #     yref='paper',
    #     y=-0.30,
    #     align = "center",
    #     )

    return fig200

### Avg Rate of Attrition percent by Dept Pie Chart End ###


### Start Avg Rate of Attrition Percent vs WorkLifeBalance Pie Chart ###
@app.callback(
    Output('work_balance_pie', 'figure'),
    [Input('work-balance-checklist', 'value')])
def update_pie(work_balance_selection):

    if work_balance_selection == []:
        return {}  # Returning this empty {} resolves a callback error that was occurring when all checklist items were unselected
    
    else:
        work_life_bal_df = work_balance_df[work_balance_df["WorkLifeBalance"].isin(work_balance_selection)]

        # Set variable to Total Count of Attrition = "Yes" (or 1)
        attrition_yes_count = sum(work_life_bal_df["Attrition"]==1)
  

    # This pie chart shows percent of total attrition based on performance rating
    fig_work_bal = px.pie(work_life_bal_df, values='Attrition', names='WorkLifeBalance',color="WorkLifeBalance", title=f"Total Attrition - Percent Breakout by Work Life Balance Rating (n={attrition_yes_count})")
   
    fig_work_bal.update_layout(
        # margin=dict(l=70, r=70, t=70, b=90),
        paper_bgcolor="LightSteelBlue",
        # font=dict(size=12),
        # font_family="Courier New",
        font_color="black",
        # title_font_family="Times New Roman",
        title_font_color="black",
        # title_font=dict(size=16),
        legend_title_font_color="black",
        legend_title_text="Work Life Balance Rating",
        title_x=0.5
    )

    # This adds annotation/caption to the chart
    # fig_work_bal_note = 'The highest rate of attrition comes from people who rated the work life balance as "Good" (3) out of a 4-point scale.'

    # fig_work_bal.add_annotation(
    #     showarrow=False,
    #     text=fig_work_bal_note,
    #     font=dict(size=11), 
    #     xref='paper',
    #     x=0.5,
    #     yref='paper',
    #     y=-0.30,
    #     align = "center",
    #     )

    return fig_work_bal

### Avg Rate of Attrition Percent vs WorkLifeBalance Pie Chart End ###


### Start Avg Rate of Attrition Percent vs Performance Rating Pie Chart ###
@app.callback(
    Output('perf_rating_pie', 'figure'),
    [Input('perf-rating-checkbox', 'value')])
def update_pie(perf_rating_selection):

    if perf_rating_selection == []:
        return {}  # Returning this empty {} resolves a callback error that was occurring when all checklist items were unselected
    
    else:
        performance_df = perf_rating_df[perf_rating_df["PerformanceRating"].isin(perf_rating_selection)]

        # Set variable to Total Count of Attrition = "Yes" (or 1)
        attrition_yes_count = sum(performance_df["Attrition"]==1)
  

    # This pie chart shows percent of total attrition based on performance rating
    fig_perf_rating = px.pie(performance_df, values='Attrition', names='PerformanceRating',color="PerformanceRating", title=f"Total Attrition - Percent Breakout by Performance Rating (n={attrition_yes_count})")
   
    fig_perf_rating.update_layout(
        # margin=dict(l=70, r=70, t=70, b=90),
        paper_bgcolor="LightSteelBlue",
        # font=dict(size=12),
        # font_family="Courier New",
        font_color="black",
        # title_font_family="Times New Roman",
        title_font_color="black",
        # title_font=dict(size=16),
        legend_title_font_color="black",
        legend_title_text="Performance Rating",
        title_x=0.5
    )

    # This adds annotation/caption to the chart
    # fig_perf_rating_note = 'All employees received performance ratings of Excellent (3) or Outstanding (4)<br>out of a 4-point scale. Of employees who left the company, 84% received an "Excellent" rating.'

    # fig_perf_rating.add_annotation(
    #     showarrow=False,
    #     text=fig_perf_rating_note,
    #     font=dict(size=11), 
    #     xref='paper',
    #     x=0.5,
    #     yref='paper',
    #     y=-0.30,
    #     align = "center",
    #     )

    return fig_perf_rating

### Avg Rate of Attrition Percent vs Performance Rating Pie Chart End ###


### Avg Rate of Attrition by Job Role Chart Start ###
@app.callback(
    Output('chart-jobrole-checkbox', 'figure'),
    [Input('jobrole-checkboxes', 'value')])
def update_figure(selected_role):

    if selected_role == []:
        return {}  # Returning this empty {} resolves a callback error that was occurring when all checklist items were unselected
    # role_df = df_trvl.groupby("JobRole").mean()["Attrition"].multiply(100)
    
    else:
        role_df_rev = df_trvl[df_trvl["JobRole"].isin(selected_role)]


    figJobRole = px.histogram(role_df_rev, x="Attrition", y="JobRole", histfunc='avg',title="Average Rate of Attrition by Job Role")


    figJobRole.update_layout(
    transition_duration=500,
    # margin=dict(l=20, r=20, t=70, b=90),
    paper_bgcolor="LightSteelBlue",
    # font=dict(size=12),
    font_color="black",
    title_font_color="black",
    # title_font=dict(size=16),
    legend_title_font_color="black",
    title_x=0.5, #centers the chart title
    yaxis_title="Job Role",
    xaxis_tickformat = '%',    
    )

    # figJobRole_note = 'The Sales Representative Role has the highest rate of attrition at 40%, followed by Laboratory Technician at 24% and Human Resources at 23%.'

    # figJobRole.add_annotation(
    #     showarrow=False,
    #     text=figJobRole_note,
    #     font=dict(size=12), 
    #     xref='paper',
    #     x=0.5,
    #     yref='paper',
    #     y=-0.30,
    #     align="center"
    #     )

    return figJobRole

### Avg Rate of Attrition by Job Role Chart End ###

