from plotly.subplots import make_subplots
import plotly.graph_objs as go
import pandas as pd  

'''Cleaned data is passed for class function to visualization'''

class call_Visualisation:
    def __init__(self, df):
        self.df = df

    def bivariate_call_app_analysis(self, variables):
        self.df = self.df[~self.df["Lead Status"].isin(["General Enquiry", "Duplicate", "Unqualified", "RNR"])]
        total_appointment_fixed = self.df[self.df["Appointment Fixed?"] == "Yes"].shape[0]
        total = self.df.shape[0]
        population_average_percentage = round((total_appointment_fixed / total) * 100, 1)

        fig = make_subplots(vertical_spacing=0.1, shared_xaxes=True, specs=[[{"secondary_y": True}]])

        if variables:
            for variable in variables:
                # Ensure all values including "Missing" are accounted for
                count_of_leads = self.df[variable].value_counts(dropna=False)
                count_appointment_fixed = self.df[self.df["Appointment Fixed?"] == "Yes"][variable].value_counts(dropna=False)

                # Replace NaN with "Missing"
                count_of_leads.index = count_of_leads.index.astype(str).str.replace("nan", "Missing")
                count_appointment_fixed.index = count_appointment_fixed.index.astype(str).str.replace("nan", "Missing")

                aligned_counts = count_of_leads.align(count_appointment_fixed, fill_value=0)
                count_of_leads = aligned_counts[0]
                count_appointment_fixed = aligned_counts[1]

                # Prepare data for plotting
                data = pd.DataFrame({
                    'Lead Source': count_of_leads.index,
                    'Count of Leads': count_of_leads.values,
                    'Appointment Fixed': count_appointment_fixed.values
                })

                # Define custom orders for specific variables
                custom_orders = {
                    'Severity': ['Low', 'Medium', 'High', 'Missing'],
                    'Insured':['Missing','Yes','No',"Don't Know"],
                    'Age Group':['Unknown', '[0-10]', '[10-20]', '[20-30]', '[30-40]', '[40-50]', '[50-60]', '[60-70]', '[70-80]', '[80-90]'],
                    'Time_of_Day':['Morning', 'Afternoon', 'Evening'],
                   'Total_Inbound_Duration': ['0-1 min', '1-5 min', '5-10 min', '10-20 min', '20-40 min'],
                    'Total_Outbound_Duration':['0-1 min', '1-5 min', '5-10 min', '10-20 min', '20-40 min'],
                    'Avg_Inbound_Duration':['0-1 sec', '1-2 sec', '2-3 sec', '3-4 sec', '4-5 sec', '5-6 sec'],
                      'Avg_Outbound_Duration':['0-1 sec', '1-2 sec', '2-3 sec', '3-4 sec', '4-5 sec', '5-6 sec'],
                      'Weekday':['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Missing'],
                        'days_since_last_call':['0-7 days', '8-30 days', '31-90 days', '91-180 days', '181-365 days'],
                        "Text_length" :['Very Short', 'Short', 'Medium', 'Long'],
                        'effective_call_rate' : ['Very Low', 'Low', 'Moderate', 'High']


                }

                if variable in custom_orders:
                    # Apply custom ordering explicitly
                    custom_order = custom_orders[variable]
                    data['Lead Source'] = pd.Categorical(data['Lead Source'], categories=custom_order, ordered=True)
                    data = data.sort_values(by='Lead Source')
                else:
                    # Default: Sort by 'Appointment Fixed' in descending order
                    data = data.sort_values(by='Appointment Fixed', ascending=False)

                data = data.reset_index(drop=True)

                # Ensure 'Missing' row is explicitly included
                if 'Missing' not in data['Lead Source'].values:
                    missing_row = {
                        'Lead Source': 'Missing',
                        'Count of Leads': self.df[variable].isna().sum(),
                        'Appointment Fixed': self.df[self.df["Appointment Fixed?"] == "Yes"][variable].isna().sum()
                    }
                    data = pd.concat([data, pd.DataFrame([missing_row])], ignore_index=True)

                data['AFX Rate (%)'] = round((data['Appointment Fixed'] / data['Count of Leads']) * 100, 0)
                x_values = data['Lead Source']
                y_values = data['Appointment Fixed']
                percentage_values = data['AFX Rate (%)']

                # Add bar and line traces
                fig.add_trace(go.Bar(
                    x=x_values,
                    y=y_values,
                    name="Appointment Fixed",
                    marker=dict(color="blue"),
                    opacity=0.8
                ), secondary_y=False)

                fig.add_trace(go.Scatter(
                    x=x_values,
                    y=percentage_values,
                    mode='lines+markers',
                    name='AFX Rate(%)',
                    line=dict(color='green')
                ), secondary_y=True)

            # Add population average line
            fig.add_shape(type="line", x0=-0.5, x1=len(data) - 0.5, y0=population_average_percentage,
                          y1=population_average_percentage, line=dict(color='firebrick', width=4, dash='dot'), yref='y2')

            fig.add_annotation(x=len(data) - 0.2, y=population_average_percentage, font=dict(size=24, color="red", family="Sans Serif"),
                               text=f"<b>{round(population_average_percentage, 0)}</b>%", showarrow=False, align="left", yref='y2')

            # Update layout
            fig.update_layout(
                title_x=0.45,
                xaxis_title=variable,
                yaxis_title="Count of Leads",
                yaxis2_title="Percentage (%)",
                height=500,
                width=1300,
                barmode='stack',
                template="plotly_white",
                xaxis=dict(
                    type='category',
                    categoryorder='array',
                    categoryarray=data['Lead Source']
                ),
                yaxis2=dict(
                    title="AFX Rate(%)",
                    overlaying="y",
                    side="right",
                    ticksuffix="%",
                    tickmode="sync",
                    automargin=True,
                    range=[0, 100]
                ),
                showlegend=True
            )

            return fig



    def bivariate_call_won_analysis(self, variables):
        self.df = self.df[~self.df["Lead Status"].isin(["General Enquiry", "Duplicate", "Unqualified", "RNR"])]
        total_appointment_fixed = self.df[self.df["Lead Status"] == "Won"].shape[0]
        total = self.df.shape[0]
        population_average_percentage = round((total_appointment_fixed / total) * 100, 1)

        fig = make_subplots(vertical_spacing=0.1, shared_xaxes=True, specs=[[{"secondary_y": True}]])

        if variables:
            for variable in variables:
                ## Ensure all values including "Missing" are accounted for
                count_of_leads = self.df[variable].value_counts(dropna=False)
                count_appointment_fixed = self.df[self.df["Lead Status"] == "Won"][variable].value_counts(dropna=False)

                # Replace NaN with "Missing"
                count_of_leads.index = count_of_leads.index.astype(str).str.replace("nan", "Missing")
                count_appointment_fixed.index = count_appointment_fixed.index.astype(str).str.replace("nan", "Missing")

                aligned_counts = count_of_leads.align(count_appointment_fixed, fill_value=0)
                count_of_leads = aligned_counts[0]
                count_appointment_fixed = aligned_counts[1]

                # Prepare data for plotting
                data = pd.DataFrame({
                    'Lead Source': count_of_leads.index,
                    'Count of Leads': count_of_leads.values,
                    'Won': count_appointment_fixed.values  # Correct column name here
                })

                # Define custom orders for specific variables
                custom_orders = {
                    'Severity': ['Low', 'Medium', 'High', 'Missing'],
                    'Insured': ['Missing', 'Yes', 'No', "Don't Know"],
                    'Age Group': ['Unknown', '[0-10]', '[10-20]', '[20-30]', '[30-40]', '[40-50]', '[50-60]', '[60-70]', '[70-80]', '[80-90]'],
                    'Total_Inbound_Duration': ['0-1 min', '1-5 min', '5-10 min', '10-20 min', '20-40 min'],
                    'Total_Outbound_Duration':['0-1 min', '1-5 min', '5-10 min', '10-20 min', '20-40 min'],
                    'Time_of_Day':['Morning', 'Afternoon', 'Evening'],
                     'Avg_Inbound_Duration':['0-1 sec', '1-2 sec', '2-3 sec', '3-4 sec', '4-5 sec', '5-6 sec'],
                      'Avg_Outbound_Duration':['0-1 sec', '1-2 sec', '2-3 sec', '3-4 sec', '4-5 sec', '5-6 sec'],
                    'Weekday':['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Missing'],
                    'days_since_last_call':['0-7 days', '8-30 days', '31-90 days', '91-180 days', '181-365 days'],
                    'Text_length' :['Very Short', 'Short', 'Medium', 'Long'],
                     'effective_call_rate' : ['Very Low', 'Low', 'Moderate', 'High']



                }

                if variable in custom_orders:
                    custom_order = custom_orders[variable]
                    data['Lead Source'] = pd.Categorical(data['Lead Source'], categories=custom_order, ordered=True)
                    data = data.sort_values(by='Lead Source')
                else:
                    data = data.sort_values(by='Won', ascending=False)

                data = data.reset_index(drop=True)

                # Ensure 'Missing' row is explicitly included
                if 'Missing' not in data['Lead Source'].values:
                    missing_row = {
                        'Lead Source': 'Missing',
                        'Count of Leads': self.df[variable].isna().sum(),
                        'Appointment Fixed': self.df[self.df["Lead Status"] == "Won"][variable].isna().sum()
                    }
                    data = pd.concat([data, pd.DataFrame([missing_row])], ignore_index=True)

                data['Won Rate (%)'] = round((data['Won'] / data['Count of Leads']) * 100, 0)
                x_values = data['Lead Source']
                y_values = data['Won']
                percentage_values = data['Won Rate (%)']

                fig.add_trace(go.Bar(
                    x=x_values,
                    y=y_values,
                    name="Won",
                    marker=dict(color="blue"),
                    opacity=0.8
                ), secondary_y=False)

                fig.add_trace(go.Scatter(
                    x=x_values,
                    y=percentage_values,
                    mode='lines+markers',
                    name='Won Rate(%)',
                    line=dict(color='green')
                ), secondary_y=True)

            # Add population average line
            fig.add_shape(type="line", x0=-0.5, x1=len(data) - 0.5, y0=population_average_percentage,
                          y1=population_average_percentage, line=dict(color='firebrick', width=4, dash='dot'), yref='y2')

            fig.add_annotation(x=len(data) - 0.2, y=population_average_percentage, font=dict(size=24, color="red", family="Sans Serif"),
                               text=f"<b>{round(population_average_percentage, 0)}</b>%", showarrow=False, align="left", yref='y2')

            # Update layout
            fig.update_layout(
                title_x=0.45,
                xaxis_title=variable,
                yaxis_title="Count of Leads",
                yaxis2_title="Percentage (%)",
                height=500,
                width=1300,
                barmode='stack',
                template="plotly_white",
                xaxis=dict(
                    type='category',
                    categoryorder='array',
                    categoryarray=data['Lead Source']
                ),
                yaxis2=dict(
                    title="AFX Rate(%)",
                    overlaying="y",
                    side="right",
                    ticksuffix="%",
                    tickmode="sync",
                    automargin=True,
                    range=[0, 100]
                ),
                showlegend=True
            )

            return fig
        

    def bivariate_call_lost_analysis(self, variables):
        self.df = self.df[~self.df["Lead Status"].isin(["General Enquiry", "Duplicate", "Unqualified", "RNR"])]
        total_appointment_fixed = self.df[self.df["Lead Status"] == "Lost"].shape[0]
        total = self.df.shape[0]
        population_average_percentage = round((total_appointment_fixed / total) * 100, 1)

        fig = make_subplots(vertical_spacing=0.1, shared_xaxes=True, specs=[[{"secondary_y": True}]])

        if variables:
            for variable in variables:
                # Ensure all values including "Missing" are accounted for
                count_of_leads = self.df[variable].value_counts(dropna=False)
                count_lost = self.df[self.df["Lead Status"] == "Lost"][variable].value_counts(dropna=False)

                # Replace NaN with "Missing"
                count_of_leads.index = count_of_leads.index.astype(str).str.replace("nan", "Missing")
                count_lost.index = count_lost.index.astype(str).str.replace("nan", "Missing")

                aligned_counts = count_of_leads.align(count_lost, fill_value=0)
                count_of_leads = aligned_counts[0]
                count_lost = aligned_counts[1]

                # Prepare data for plotting
                data = pd.DataFrame({
                    'Lead Source': count_of_leads.index,
                    'Count of Leads': count_of_leads.values,
                    'Lost': count_lost.values  # Correct column name here
                })

                # Define custom orders for specific variables
                custom_orders = {
                    'Severity': ['Low', 'Medium', 'High', 'Missing'],
                    'Insured': ['Missing', 'Yes', 'No', "Don't Know"],
                    'Age Group': ['Unknown', '[0-10]', '[10-20]', '[20-30]', '[30-40]', '[40-50]', '[50-60]', '[60-70]', '[70-80]', '[80-90]'],
                    'Time_of_Day':['Morning', 'Afternoon', 'Evening'],
                    'Total_Inbound_Duration':['0-1 min', '1-5 min', '5-10 min', '10-20 min', '20-40 min'],
                    'Total_Outbound_Duration':['0-1 min', '1-5 min', '5-10 min', '10-20 min', '20-40 min'],
                     'Avg_Inbound_Duration':['0-1 sec', '1-2 sec', '2-3 sec', '3-4 sec', '4-5 sec', '5-6 sec'],
                      'Avg_Outbound_Duration':['0-1 sec', '1-2 sec', '2-3 sec', '3-4 sec', '4-5 sec', '5-6 sec'],
                    'Weekday':['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Missing'],
                   'days_since_last_call':['0-7 days', '8-30 days', '31-90 days', '91-180 days', '181-365 days'],
                     "Text_length" :['Very Short', 'Short', 'Medium', 'Long'],
                     'effective_call_rate' : ['Very Low', 'Low', 'Moderate', 'High']

      
                }

                if variable in custom_orders:
                    custom_order = custom_orders[variable]
                    data['Lead Source'] = pd.Categorical(data['Lead Source'], categories=custom_order, ordered=True)
                    data = data.sort_values(by='Lead Source')
                else:
                    data = data.sort_values(by='Lost', ascending=False)

                data = data.reset_index(drop=True)

                # Ensure 'Missing' row is explicitly included
                if 'Missing' not in data['Lead Source'].values:
                    missing_row = {
                        'Lead Source': 'Missing',
                        'Count of Leads': self.df[variable].isna().sum(),
                        'Lost': self.df[self.df["Lead Status"] == "Lost"][variable].isna().sum()
                    }
                    data = pd.concat([data, pd.DataFrame([missing_row])], ignore_index=True)

                data['Lost Rate (%)'] = round((data['Lost'] / data['Count of Leads']) * 100, 0)
                x_values = data['Lead Source']
                y_values = data['Lost']
                percentage_values = data['Lost Rate (%)']

                # Add bar and line traces
                fig.add_trace(go.Bar(
                    x=x_values,
                    y=y_values,
                    name="Lost",
                    marker=dict(color="blue"),
                    opacity=0.8
                ), secondary_y=False)

                fig.add_trace(go.Scatter(
                    x=x_values,
                    y=percentage_values,
                    mode='lines+markers',
                    name='Lost Rate(%)',
                    line=dict(color='green')
                ), secondary_y=True)

                # Add population average line
                fig.add_shape(type="line", x0=-0.5, x1=len(data) - 0.5, y0=population_average_percentage,
                            y1=population_average_percentage, line=dict(color='firebrick', width=4, dash='dot'), yref='y2')

                fig.add_annotation(x=len(data) - 0.2, y=population_average_percentage, font=dict(size=24, color="red", family="Sans Serif"),
                                text=f"<b>{round(population_average_percentage, 0)}</b>%", showarrow=False, align="left", yref='y2')

                # Update layout
                fig.update_layout(
                    title_x=0.45,
                    xaxis_title=variable,
                    yaxis_title="Count of Leads",
                    yaxis2_title="Lost Rate (%)",
                    height=500,
                    width=1300,
                    barmode='stack',
                    template="plotly_white",
                    xaxis=dict(
                        type='category',
                        categoryorder='array',
                        categoryarray=data['Lead Source']
                    ),
                    yaxis2=dict(
                        title="Lost Rate(%)",
                        overlaying="y",
                        side="right",
                        ticksuffix="%",
                        tickmode="sync",
                        automargin=True,
                        range=[0, 100]
                    ),
                    showlegend=True
                )

                return fig

        
def generate_cross_table_call_app(df, primary_variable1):
    df = df[~df["Lead Status"].isin(["General Enquiry", "Duplicate", "Unqualified", 'RNR'])]
    
    if primary_variable1 == 'Severity':
        severity_order = ['Low', 'Medium', 'High', 'Missing']
        df[primary_variable1] = pd.Categorical(df[primary_variable1], categories=severity_order, ordered=True)
    
    if primary_variable1 == 'Insured':
        Insured_order=['Missing','Yes','No',"Don't Know"]
        df[primary_variable1] = pd.Categorical(df[primary_variable1], categories=Insured_order, ordered=True)

    if primary_variable1 == 'Lead Age':
        severity_order = ['0-30', '31-60', '61-90', '91-120', '121-150', '151-200', '201-300', '301-500', '501+']
        df[primary_variable1] = pd.Categorical(df[primary_variable1], categories=severity_order, ordered=True)

    if primary_variable1 == 'Age Group':
        age_order = ['Unknown', '[0-10]', '[10-20]', '[20-30]', '[30-40]', '[40-50]', '[50-60]', '[60-70]', '[70-80]', '[80-90]']
        df[primary_variable1] = pd.Categorical(df[primary_variable1], categories=age_order, ordered=True)

    if primary_variable1 == 'Time_of_Day':
        time_of_day = ['Morning', 'Afternoon', 'Evening']
        df[primary_variable1] = pd.Categorical(df[primary_variable1], categories=time_of_day, ordered=True)

    if primary_variable1 == 'Call_Weekday':
        call_week = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Missing']
        df[primary_variable1] = pd.Categorical(df[primary_variable1], categories=call_week, ordered=True)

    if primary_variable1 == 'Total_Inbound_Duration':
        Total_Inbound_Duration= ['0-1 min', '1-5 min', '5-10 min', '10-20 min', '20-40 min']
        df[primary_variable1] = pd.Categorical(df[primary_variable1], categories=Total_Inbound_Duration, ordered=True)

    if primary_variable1 == 'Total_Outbound_Duration':
        Total_Outbound_Duration= ['0-1 min', '1-5 min', '5-10 min', '10-20 min', '20-40 min']
        df[primary_variable1] = pd.Categorical(df[primary_variable1], categories=Total_Outbound_Duration, ordered=True)
    
    if primary_variable1 == 'Avg_Inbound_Duration':
        Total_Inbound_Duration= ['0-1 sec', '1-2 sec', '2-3 sec', '3-4 sec', '4-5 sec', '5-6 sec']
        df[primary_variable1] = pd.Categorical(df[primary_variable1], categories=Total_Inbound_Duration, ordered=True)

    if primary_variable1 == 'Avg_Outbound_Duration':
        Total_Outbound_Duration= ['0-1 sec', '1-2 sec', '2-3 sec', '3-4 sec', '4-5 sec', '5-6 sec']
        df[primary_variable1] = pd.Categorical(df[primary_variable1], categories=Total_Outbound_Duration, ordered=True)

    
    if primary_variable1 == 'days_since_last_call':
        days_since_last_call= ['0-7 days', '8-30 days', '31-90 days', '91-180 days', '181-365 days']
        df[primary_variable1] = pd.Categorical(df[primary_variable1], categories=days_since_last_call, ordered=True)

    if primary_variable1=='Text_length':
       Time_of_Day=  ['Very Short', 'Short', 'Medium', 'Long']
       df[primary_variable1] = pd.Categorical(df[primary_variable1], categories=Time_of_Day, ordered=True) 
    if primary_variable1=='effective_call_rate' :
       effective_call_rate=  ['Very Low', 'Low', 'Moderate', 'High']
       df[primary_variable1] = pd.Categorical(df[primary_variable1], categories=effective_call_rate, ordered=True) 


    # Ensure 'Missing' is not added if it already exists
    if pd.api.types.is_categorical_dtype(df[primary_variable1]):
        if 'Missing' not in df[primary_variable1].cat.categories:
            df[primary_variable1] = df[primary_variable1].cat.add_categories('Missing')

    df[primary_variable1] = df[primary_variable1].fillna('Missing')

    cross_table = pd.crosstab(index=df[primary_variable1], columns=df['Appointment Fixed?'], margins=True, margins_name="Grand Total")
    cross_table = cross_table.reset_index()
    cross_table['Sl No.'] = cross_table.index + 1

    cross_table['AFX Rate(%)'] = (
        (cross_table['Yes'] / cross_table['Grand Total']) * 100
    ).round(0).astype(str) + "%"

    cross_table.at[cross_table.index[-1], primary_variable1] = 'Population Average Percentage (%)'

    population_avg_row = cross_table[cross_table[primary_variable1] == 'Population Average Percentage (%)']
    cross_table = cross_table[cross_table[primary_variable1] != 'Population Average Percentage (%)']

    if 'Missing' in cross_table[primary_variable1].values:
        missing_row = cross_table[cross_table[primary_variable1] == 'Missing']
        cross_table = cross_table[cross_table[primary_variable1] != 'Missing']
        cross_table = pd.concat([cross_table, missing_row, population_avg_row], ignore_index=True)
    else:
        cross_table = pd.concat([cross_table, population_avg_row], ignore_index=True)

    cross_table['Sl No.'] = cross_table.index + 1

    cols = ['Sl No.'] + [col for col in cross_table.columns if col != 'Sl No.']
    cross_table = cross_table[cols]
    return cross_table


def generate_cross_table_call_won(df, primary_variable1):
    df = df[~df["Lead Status"].isin(["General Enquiry", "Duplicate", "Unqualified", 'RNR'])]
    
    if primary_variable1 == 'Severity':
        severity_order = ['Low', 'Medium', 'High', 'Missing']
        df[primary_variable1] = pd.Categorical(df[primary_variable1], categories=severity_order, ordered=True)
    
    if primary_variable1 == 'Insured':
        Insured_order=['Missing','Yes','No',"Don't Know"]
        df[primary_variable1] = pd.Categorical(df[primary_variable1], categories=Insured_order, ordered=True)

    if primary_variable1 == 'Lead Age':
        severity_order = ['0-30', '31-60', '61-90', '91-120', '121-150', '151-200', '201-300', '301-500', '501+']
        df[primary_variable1] = pd.Categorical(df[primary_variable1], categories=severity_order, ordered=True)

    if primary_variable1 == 'Age Group':
        age_order = ['Unknown', '[0-10]', '[10-20]', '[20-30]', '[30-40]', '[40-50]', '[50-60]', '[60-70]', '[70-80]', '[80-90]']
        df[primary_variable1] = pd.Categorical(df[primary_variable1], categories=age_order, ordered=True)

    if primary_variable1 == 'Time_of_Day':
        time_of_day = ['Morning', 'Afternoon', 'Evening']
        df[primary_variable1] = pd.Categorical(df[primary_variable1], categories=time_of_day, ordered=True)

    if primary_variable1 == 'Weekday':
        call_week = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Missing']
        df[primary_variable1] = pd.Categorical(df[primary_variable1], categories=call_week, ordered=True)

    if primary_variable1 == 'Total_Inbound_Duration': 
        Total_Inbound_Duration=  ['0-1 min', '1-5 min', '5-10 min', '10-20 min', '20-40 min']
        df[primary_variable1] = pd.Categorical(df[primary_variable1], categories=Total_Inbound_Duration, ordered=True)

    if primary_variable1 == 'Total_Outbound_Duration':
        Total_Outbound_Duration= ['0-1 min', '1-5 min', '5-10 min', '10-20 min', '20-40 min']
        df[primary_variable1] = pd.Categorical(df[primary_variable1], categories=Total_Outbound_Duration, ordered=True)


    if primary_variable1 == 'Avg_Inbound_Duration':
        Total_Inbound_Duration= ['0-1 sec', '1-2 sec', '2-3 sec', '3-4 sec', '4-5 sec', '5-6 sec']
        df[primary_variable1] = pd.Categorical(df[primary_variable1], categories=Total_Inbound_Duration, ordered=True)

    if primary_variable1 == 'Avg_Outbound_Duration':
        Total_Outbound_Duration= ['0-1 sec', '1-2 sec', '2-3 sec', '3-4 sec', '4-5 sec', '5-6 sec']
        df[primary_variable1] = pd.Categorical(df[primary_variable1], categories=Total_Outbound_Duration, ordered=True)

    
    if primary_variable1 == 'days_since_last_call':
        days_since_last_call= ['0-7 days', '8-30 days', '31-90 days', '91-180 days', '181-365 days']
        df[primary_variable1] = pd.Categorical(df[primary_variable1], categories=days_since_last_call, ordered=True)

    if primary_variable1=='Text_length':
       Time_of_Day=  ['Very Short', 'Short', 'Medium', 'Long']
       df[primary_variable1] = pd.Categorical(df[primary_variable1], categories=Time_of_Day, ordered=True) 

    if primary_variable1=='effective_call_rate' :
       effective_call_rate=  ['Very Low', 'Low', 'Moderate', 'High']
       df[primary_variable1] = pd.Categorical(df[primary_variable1], categories=effective_call_rate, ordered=True) 

    # Ensure 'Missing' is not added if it already exists
    if pd.api.types.is_categorical_dtype(df[primary_variable1]):
        if 'Missing' not in df[primary_variable1].cat.categories:
            df[primary_variable1] = df[primary_variable1].cat.add_categories('Missing')

    df[primary_variable1] = df[primary_variable1].fillna('Missing')

    cross_table = pd.crosstab(index=df[primary_variable1], columns=df['Lead Status'], margins=True, margins_name="Grand Total")
    cross_table = cross_table.reset_index()
    cross_table['Sl No.'] = cross_table.index + 1

    cross_table['Won Rate(%)'] = (
        (cross_table['Won'] / cross_table['Grand Total']) * 100
    ).round(0).astype(str) + "%"

    cross_table.at[cross_table.index[-1], primary_variable1] = 'Population Average Percentage (%)'

    population_avg_row = cross_table[cross_table[primary_variable1] == 'Population Average Percentage (%)']
    cross_table = cross_table[cross_table[primary_variable1] != 'Population Average Percentage (%)']

    if 'Missing' in cross_table[primary_variable1].values:
        missing_row = cross_table[cross_table[primary_variable1] == 'Missing']
        cross_table = cross_table[cross_table[primary_variable1] != 'Missing']
        cross_table = pd.concat([cross_table, missing_row, population_avg_row], ignore_index=True)
    else:
        cross_table = pd.concat([cross_table, population_avg_row], ignore_index=True)

    cross_table['Sl No.'] = cross_table.index + 1

    cols = ['Sl No.'] + [col for col in cross_table.columns if col != 'Sl No.']
    cross_table = cross_table[cols]
    return cross_table

def generate_cross_table_call_lost(df, primary_variable1):
    df = df[~df["Lead Status"].isin(["General Enquiry", "Duplicate", "Unqualified", 'RNR'])]
    
    if primary_variable1 == 'Severity':
        severity_order = ['Low', 'Medium', 'High', 'Missing']
        df[primary_variable1] = pd.Categorical(df[primary_variable1], categories=severity_order, ordered=True)
    
    if primary_variable1 == 'Insured':
        Insured_order=['Missing','Yes','No',"Don't Know"]
        df[primary_variable1] = pd.Categorical(df[primary_variable1], categories=Insured_order, ordered=True)

    if primary_variable1 == 'Lead Age':
        severity_order = ['0-30', '31-60', '61-90', '91-120', '121-150', '151-200', '201-300', '301-500', '501+']
        df[primary_variable1] = pd.Categorical(df[primary_variable1], categories=severity_order, ordered=True)

    if primary_variable1 == 'Age Group':
        age_order = ['Unknown', '[0-10]', '[10-20]', '[20-30]', '[30-40]', '[40-50]', '[50-60]', '[60-70]', '[70-80]', '[80-90]']
        df[primary_variable1] = pd.Categorical(df[primary_variable1], categories=age_order, ordered=True)

    if primary_variable1 == 'Time_of_Day':
        time_of_day = ['Morning', 'Afternoon', 'Evening']
        df[primary_variable1] = pd.Categorical(df[primary_variable1], categories=time_of_day, ordered=True)

    if primary_variable1 == 'Weekday':
        call_week = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Missing']
        df[primary_variable1] = pd.Categorical(df[primary_variable1], categories=call_week, ordered=True)

    if primary_variable1 == 'Total_Inbound_Duration':
        Total_Inbound_Duration= ['0-1 min', '1-5 min', '5-10 min', '10-20 min', '20-40 min']
        df[primary_variable1] = pd.Categorical(df[primary_variable1], categories=Total_Inbound_Duration, ordered=True)

    if primary_variable1 == 'Total_Outbound_Duration':
        Total_Outbound_Duration= ['0-1 min', '1-5 min', '5-10 min', '10-20 min', '20-40 min']
        df[primary_variable1] = pd.Categorical(df[primary_variable1], categories=Total_Outbound_Duration, ordered=True)
    
    if primary_variable1 == 'days_since_last_call':
        days_since_last_call= ['0-7 days', '8-30 days', '31-90 days', '91-180 days', '181-365 days']
        df[primary_variable1] = pd.Categorical(df[primary_variable1], categories=days_since_last_call, ordered=True)

    if primary_variable1=='Text_length' :
       Time_of_Day=  ['Very Short', 'Short', 'Medium', 'Long']
       df[primary_variable1] = pd.Categorical(df[primary_variable1], categories=Time_of_Day, ordered=True) 
    
    if primary_variable1=='effective_call_rate' :
       effective_call_rate=  ['Very Low', 'Low', 'Moderate', 'High']
       df[primary_variable1] = pd.Categorical(df[primary_variable1], categories=effective_call_rate, ordered=True) 

    # Ensure 'Missing' is not added if it already exists
    if pd.api.types.is_categorical_dtype(df[primary_variable1]):
        if 'Missing' not in df[primary_variable1].cat.categories:
            df[primary_variable1] = df[primary_variable1].cat.add_categories('Missing')

    df[primary_variable1] = df[primary_variable1].fillna('Missing')

    cross_table = pd.crosstab(index=df[primary_variable1], columns=df['Lead Status'], margins=True, margins_name="Grand Total")
    cross_table = cross_table.reset_index()
    cross_table['Sl No.'] = cross_table.index + 1

    cross_table['Lost Rate(%)'] = (
        (cross_table['Lost'] / cross_table['Grand Total']) * 100
    ).round(0).astype(str) + "%"

    cross_table.at[cross_table.index[-1], primary_variable1] = 'Population Average Percentage (%)'

    population_avg_row = cross_table[cross_table[primary_variable1] == 'Population Average Percentage (%)']
    cross_table = cross_table[cross_table[primary_variable1] != 'Population Average Percentage (%)']

    if 'Missing' in cross_table[primary_variable1].values:
        missing_row = cross_table[cross_table[primary_variable1] == 'Missing']
        cross_table = cross_table[cross_table[primary_variable1] != 'Missing']
        cross_table = pd.concat([cross_table, missing_row, population_avg_row], ignore_index=True)
    else:
        cross_table = pd.concat([cross_table, population_avg_row], ignore_index=True)

    cross_table['Sl No.'] = cross_table.index + 1

    cols = ['Sl No.'] + [col for col in cross_table.columns if col != 'Sl No.']
    cross_table = cross_table[cols]
    return cross_table
