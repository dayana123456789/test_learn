import pandas as pd
import numpy as np
import plotly.graph_objs as go
from plotly.subplots import make_subplots

class PredictedBivariateAnalysis:
        def __init__(self, df):
            self.df = df

        def bivariate_closed_opportunity_analysis_predicted(self, variables):
            """
            Analyze Closed Opportunity (Won/Lost) leads based on Prediction (Yes/No) across selected variables.
            """
            # Filter only "Won" and "Lost" leads
            self.df = self.df[self.df["Lead Status"].isin(["Won", "Lost"])]

            # Total "Yes" Predictions
            closed_opportunity_predictions = self.df[self.df["Prediction"] == "Yes"]

            # Overall population average percentage
            total_closed_opportunity_predictions = closed_opportunity_predictions.shape[0]
            total_predictions = self.df.shape[0]

            population_average_percentage = (
                round((total_closed_opportunity_predictions / total_predictions) * 100, 1)
                if total_predictions > 0 else 0
            )

            # Initialize Plotly Subplot
            fig = make_subplots(
                rows=len(variables),
                cols=1,
                subplot_titles=[f"{var}" for var in variables],
                shared_xaxes=False,
                vertical_spacing=0.15,
                specs=[[{"secondary_y": True}] for _ in variables]
            )

            for i, variable in enumerate(variables):
                # Count total leads and "Yes" predictions per category
                count_of_leads = self.df[variable].value_counts(dropna=False)
                count_closed_opportunity_predictions = closed_opportunity_predictions[variable].value_counts(dropna=False)

                # Replace NaN with "Missing"
                count_of_leads.index = count_of_leads.index.astype(str).str.replace("nan", "Missing")
                count_closed_opportunity_predictions.index = count_closed_opportunity_predictions.index.astype(str).str.replace("nan", "Missing")

                # Align counts
                aligned_leads, aligned_yes = count_of_leads.align(count_closed_opportunity_predictions, fill_value=0)

                # Create DataFrame for plotting
                data = pd.DataFrame({
                    'Category': aligned_leads.index,
                    'Total Count': aligned_leads.values,
                    'Closed Opportunity Predictions': aligned_yes.values
                })

                # Correct AFX Rate Calculation
                data['AFX Rate (%)'] = (
                    (data['Closed Opportunity Predictions'] / data['Total Count'].replace(0, np.nan)) * 100
                ).round(0).fillna(0)

                # Sort categories if custom order exists
                custom_orders = {
                    'Severity': ['Low', 'Medium', 'High', 'Missing'],
                    'Insured': ['Missing', 'Yes', 'No', "Don't Know"],
                    'days_since_last_call':['0-7 days', '8-30 days', '31-90 days', '91-180 days', '181-365 days'],
                    'time_of_day':["Morning","Afternoon","Evening"],
                    'Age Group': ['Unknown', '[0-10]', '[10-20]', '[20-30]', '[30-40]', '[40-50]', '[50-60]', '[60-70]', '[70-80]', '[80-90]'],
                    'total_inbound_duration':['0-1 min', '1-5 min', '5-10 min', '10-20 min', '20-40 min'],
                    'total_outbound_duration':['0-1 min', '1-5 min', '5-10 min', '10-20 min', '20-40 min'],
                    "Text Length" :['Very Short', 'Short', 'Medium', 'Long'],


                }

                if variable in custom_orders:
                    custom_order = custom_orders[variable]
                    data['Category'] = pd.Categorical(data['Category'], categories=custom_order, ordered=True)
                    data = data.sort_values(by='Category')
                else:
                    data = data.sort_values(by='Closed Opportunity Predictions', ascending=False)

                data = data.reset_index(drop=True)

                # Explicitly add a "Missing" row if not already present
                if 'Missing' not in data['Category'].values:
                    missing_row = {
                        'Category': 'Missing',
                        'Total Count': self.df[variable].isna().sum(),
                        'Closed Opportunity Predictions': closed_opportunity_predictions[variable].isna().sum()
                    }
                    data = pd.concat([data, pd.DataFrame([missing_row])], ignore_index=True)

                # Plot Data
                fig.add_trace(
                    go.Bar(
                        x=data['Category'],
                        y=data['Closed Opportunity Predictions'],
                        name=f"{variable} - Closed Opportunity Predictions",
                        marker=dict(color="blue"),
                        opacity=0.8
                    ),
                    row=i + 1, col=1, secondary_y=False
                )

                fig.add_trace(
                    go.Scatter(
                        x=data['Category'],
                        y=data['AFX Rate (%)'],
                        mode='lines+markers',
                        name=f"{variable} - AFX Rate (%)",
                        line=dict(color='green')
                    ),
                    row=i + 1, col=1, secondary_y=True
                )

                # Add Population Average Line
                fig.add_shape(
                    type="line",
                    x0=-0.5,
                    x1=len(data) - 0.5,
                    y0=population_average_percentage,
                    y1=population_average_percentage,
                    line=dict(color='firebrick', width=4, dash='dot'),
                    row=i + 1, col=1, yref='y2'
                )

                fig.add_annotation(
                    x=len(data) - 0.2,
                    y=population_average_percentage,
                    font=dict(size=14, color="red"),
                    text=f"<b>{round(population_average_percentage, 0)}</b>%",
                    showarrow=False,
                    align="left",
                    row=i + 1, col=1, yref='y2'
                )

            # Update Layout
            fig.update_layout(
                height=400 * len(variables),
                width=1300,
                barmode='stack',
                template="plotly_white",
                showlegend=True
            )

            for i in range(1, len(variables) + 1):
                fig.update_yaxes(title_text="Total Count", secondary_y=False, row=i, col=1)
                fig.update_yaxes(title_text="AFX Rate (%)", secondary_y=True, ticksuffix="%", range=[0, 100], row=i, col=1)

            return fig


def bivariate_wip_predicted(df, variables):
    """
    Analyze WIP leads based on Prediction (Yes/No) across selected variables.
    """
    # Filter only "WIP" leads
    wip_df = df[df["Lead Status"] == "WIP"]

    # Total "Yes" Predictions
    wip_predictions = wip_df[wip_df["Prediction"] == "Yes"]

    # Overall population average percentage
    total_wip_predictions = wip_predictions.shape[0]
    total_predictions = wip_df.shape[0]

    population_average_percentage = (
        round((total_wip_predictions / total_predictions) * 100, 1)
        if total_predictions > 0 else 0
    )

    # Initialize Plotly Subplot
    fig = make_subplots(
        rows=len(variables),
        cols=1,
        subplot_titles=[f"{var}" for var in variables],
        shared_xaxes=False,
        vertical_spacing=0.15,
        specs=[[{"secondary_y": True}] for _ in variables]
    )

    for i, variable in enumerate(variables):
        # Count total leads and "Yes" predictions per category
        count_of_leads = wip_df[variable].value_counts(dropna=False)
        count_wip_predictions = wip_predictions[variable].value_counts(dropna=False)

        # Replace NaN with "Missing"
        count_of_leads.index = count_of_leads.index.astype(str).str.replace("nan", "Missing")
        count_wip_predictions.index = count_wip_predictions.index.astype(str).str.replace("nan", "Missing")

        # Align counts
        aligned_leads, aligned_yes = count_of_leads.align(count_wip_predictions, fill_value=0)

        # Create DataFrame for plotting
        data = pd.DataFrame({
            'Category': aligned_leads.index,
            'Total Count': aligned_leads.values,
            'WIP Predictions': aligned_yes.values
        })

        # Correct AFX Rate Calculation
        data['AFX Rate (%)'] = (
            (data['WIP Predictions'] / data['Total Count'].replace(0, np.nan)) * 100
        ).round(0).fillna(0)

        # Sort categories if custom order exists
        custom_orders = {
            'Severity': ['Low', 'Medium', 'High', 'Missing'],
            'Insured': ['Missing', 'Yes', 'No', "Don't Know"],
            'time_of_day':["Morning","Afternoon","Evening"],
            'total_inbound_duration':['0-1 min', '1-5 min', '5-10 min', '10-20 min', '20-40 min'],
            'total_outbound_duration':['0-1 min', '1-5 min', '5-10 min', '10-20 min', '20-40 min'],
            "Text Length" :['Very Short', 'Short', 'Medium', 'Long'],
            'Age Group': ['Unknown', '[0-10]', '[10-20]', '[20-30]', '[30-40]', '[40-50]', '[50-60]', '[60-70]', '[70-80]', '[80-90]'],
            'days_since_last_call':['0-7 days', '8-30 days', '31-90 days', '91-180 days', '181-365 days'],

        }

        if variable in custom_orders:
            custom_order = custom_orders[variable]
            data['Category'] = pd.Categorical(data['Category'], categories=custom_order, ordered=True)
            data = data.sort_values(by='Category')
        else:
            data = data.sort_values(by='WIP Predictions', ascending=False)

        data = data.reset_index(drop=True)

        # Explicitly add a "Missing" row if not already present
        if 'Missing' not in data['Category'].values:
            missing_row = {
                'Category': 'Missing',
                'Total Count': wip_df[variable].isna().sum(),
                'WIP Predictions': wip_predictions[variable].isna().sum()
            }
            data = pd.concat([data, pd.DataFrame([missing_row])], ignore_index=True)

        # Plot Data
        fig.add_trace(
            go.Bar(
                x=data['Category'],
                y=data['WIP Predictions'],
                name=f"{variable} - WIP Predictions",
                marker=dict(color="blue"),
                opacity=0.8
            ),
            row=i + 1, col=1, secondary_y=False
        )

        fig.add_trace(
            go.Scatter(
                x=data['Category'],
                y=data['AFX Rate (%)'],
                mode='lines+markers',
                name=f"{variable} - AFX Rate (%)",
                line=dict(color='green')
            ),
            row=i + 1, col=1, secondary_y=True
        )

        # Add Population Average Line
        fig.add_shape(
            type="line",
            x0=-0.5,
            x1=len(data) - 0.5,
            y0=population_average_percentage,
            y1=population_average_percentage,
            line=dict(color='firebrick', width=4, dash='dot'),
            row=i + 1, col=1, yref='y2'
        )

        fig.add_annotation(
            x=len(data) - 0.2,
            y=population_average_percentage,
            font=dict(size=14, color="red"),
            text=f"<b>{round(population_average_percentage, 0)}</b>%",
            showarrow=False,
            align="left",
            row=i + 1, col=1, yref='y2'
        )

    # Update Layout
    fig.update_layout(
        height=400 * len(variables),
        width=1300,
        barmode='stack',
        template="plotly_white",
        showlegend=True
    )

    for i in range(1, len(variables) + 1):
        fig.update_yaxes(title_text="Total Count", secondary_y=False, row=i, col=1)
        fig.update_yaxes(title_text="AFX Rate (%)", secondary_y=True, ticksuffix="%", range=[0, 100], row=i, col=1)

    return fig

def generate_cross_table_closed(df, primary_variable):
    """
    Generate a cross-table showing the appointment fixed rate (AFX Rate) for a given primary variable.
    """
    # Filter out WIP leads
    df = df[~df["Lead Status"].isin(["WIP"])]
    
    # Ensure categorical order for specific variables
    category_orders = {
        'Severity': ['Low', 'Medium', 'High'],
        'Insured': ['Yes', 'No', "Don't Know"],
        'Lead Age': ['0-30', '31-60', '61-90', '91-120', '121-150', '151-200', '201-300', '301-500', '501+'],
        'Age Group': ['Unknown', '[0-10]', '[10-20]', '[20-30]', '[30-40]', '[40-50]', '[50-60]', '[60-70]', '[70-80]', '[80-90]'],
        'time_of_day': ['Morning', 'Afternoon', 'Evening', "Night"],
        'Call_Weekday': ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'],
        'Text length': ['Very Short', 'Short', 'Medium', 'Long']
    }
    
    if primary_variable in category_orders:
        df[primary_variable] = pd.Categorical(df[primary_variable], categories=category_orders[primary_variable], ordered=True)
    
    # *Ensure 'Missing' is part of categories*
    if pd.api.types.is_categorical_dtype(df[primary_variable]):
        if 'Missing' not in df[primary_variable].cat.categories:
            df[primary_variable] = df[primary_variable].cat.add_categories('Missing')
    
    # Replace NaN with 'Missing'
    df[primary_variable] = df[primary_variable].fillna('Missing')

    # Step 1: Calculate Global Population Average Including Missing
    global_yes_count = df[df['Prediction'] == 'Yes'].shape[0]
    global_total_count = df.shape[0]
    
    global_population_avg = (
        (global_yes_count / global_total_count) * 100 if global_total_count > 0 else 0
    )

    # Step 2: Create Main Crosstab
    cross_table = pd.crosstab(
        index=df[primary_variable],
        columns=df['Prediction'],
        margins=False
    ).reset_index()

    # Step 3: Add Serial Numbers
    cross_table['Sl No.'] = cross_table.index + 1

    # Step 4: Calculate AFX Rate (%) for each row
    cross_table['AFX Rate(%)'] = (
        (cross_table['Yes'] / cross_table[['Yes', 'No']].sum(axis=1).replace(0, np.nan)) * 100
    ).round(0).fillna(0).astype(str) + "%"

    # Step 5: Add Population Average Row at the Bottom
    population_avg_row = {
        'Sl No.': len(cross_table) + 1,
        primary_variable: 'Population Average Percentage (%)',
        'Yes': global_yes_count,
        'No': global_total_count - global_yes_count,
        'AFX Rate(%)': f"{round(global_population_avg, 1)}%"
    }
    
    cross_table = pd.concat([cross_table, pd.DataFrame([population_avg_row])], ignore_index=True)

    # Step 6: Recalculate Serial Numbers
    cross_table['Sl No.'] = cross_table.index + 1

    # Step 7: Reorder Columns
    cols = ['Sl No.'] + [col for col in cross_table.columns if col != 'Sl No.']
    cross_table = cross_table[cols]

    return cross_table

def generate_cross_table_wip(df, primary_variable):
    df = df[~df["Lead Status"].isin(["Won","Lost"])]

    # Ensure categorical order for specific variables
    category_orders = {
        'Severity': ['Low', 'Medium', 'High'],
        'Insured': ['Yes', 'No', "Don't Know"],
        'Lead Age': ['0-30', '31-60', '61-90', '91-120', '121-150', '151-200', '201-300', '301-500', '501+'],
        'Age Group': ['Unknown', '[0-10]', '[10-20]', '[20-30]', '[30-40]', '[40-50]', '[50-60]', '[60-70]', '[70-80]', '[80-90]'],
        'time_of_day': ['Morning', 'Afternoon', 'Evening', "Night"],
        'Call_Weekday': ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'],
        'Text length': ['Very Short', 'Short', 'Medium', 'Long']
    }
    
    if primary_variable in category_orders:
        df[primary_variable] = pd.Categorical(df[primary_variable], categories=category_orders[primary_variable], ordered=True)
    
    # *Ensure 'Missing' is part of categories*
    if pd.api.types.is_categorical_dtype(df[primary_variable]):
        if 'Missing' not in df[primary_variable].cat.categories:
            df[primary_variable] = df[primary_variable].cat.add_categories('Missing')
    
    # Replace NaN with 'Missing'
    df[primary_variable] = df[primary_variable].fillna('Missing')

    # Step 1: Calculate Global Population Average Including Missing
    global_yes_count = df[df['Prediction'] == 'Yes'].shape[0]
    global_total_count = df.shape[0]
    
    global_population_avg = (
        (global_yes_count / global_total_count) * 100 if global_total_count > 0 else 0
    )

    # Step 2: Create Main Crosstab
    cross_table = pd.crosstab(
        index=df[primary_variable],
        columns=df['Prediction'],
        margins=False
    ).reset_index()

    # Step 3: Add Serial Numbers
    cross_table['Sl No.'] = cross_table.index + 1

    # Step 4: Calculate AFX Rate (%) for each row
    cross_table['AFX Rate(%)'] = (
        (cross_table['Yes'] / cross_table[['Yes', 'No']].sum(axis=1).replace(0, np.nan)) * 100
    ).round(0).fillna(0).astype(str) + "%"

    # Step 5: Add Population Average Row at the Bottom
    population_avg_row = {
        'Sl No.': len(cross_table) + 1,
        primary_variable: 'Population Average Percentage (%)',
        'Yes': global_yes_count,
        'No': global_total_count - global_yes_count,
        'AFX Rate(%)': f"{round(global_population_avg, 1)}%"
    }
    
    cross_table = pd.concat([cross_table, pd.DataFrame([population_avg_row])], ignore_index=True)

    # Step 6: Recalculate Serial Numbers
    cross_table['Sl No.'] = cross_table.index + 1

    # Step 7: Reorder Columns
    cols = ['Sl No.'] + [col for col in cross_table.columns if col != 'Sl No.']
    cross_table = cross_table[cols]

    return cross_table