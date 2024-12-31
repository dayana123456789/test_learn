import pandas as pd
import numpy as np
from datetime import datetime
import re
###Exclude owners not Lead Sources please note it 

def data_read(file_paths, encodings):
    """
    Reads multiple CSV files, concatenates them into a single DataFrame.
    Args:
        file_paths (list): List of file paths.
        encodings (list): List of encoding formats corresponding to the files.
    Returns:
        pd.DataFrame: Concatenated DataFrame.
    """
    dataframes = [
        pd.read_csv(path, encoding=encoding, low_memory=False)  # Suppress mixed-type warnings
        for path, encoding in zip(file_paths, encodings)
    ]
    return pd.concat(dataframes, ignore_index=True)

def rename_lead_status(df):
    #df=df[~df['Lead Status'].isin(['Appointment Fixed'])]
    df["Lead Status"]=df["Lead Status"].replace(
        {"RNR":"General Enquiry","WIP":"Lost",
       }
    )
    df=df.dropna(subset=["Lead Status"]) 
    return df



def sort_dates(df):
    df['Modified On'] = pd.to_datetime(df['Modified On'])
    start_date = '2023-04-01'
    end_date = '2024-09-30'
    df = df[(df['Modified On'] >= start_date) & (df['Modified On'] < end_date)]
    return df

def clean_phone_numbers(df):
    df.rename(columns={"Created On":"Opportunity Created On"},inplace=True)
    df['Phone Number']=df['Phone Number'].astype(str)

    df['Phone Number']=df['Phone Number'].str.replace(".0","")
    df['Phone Number'] = df['Phone Number'].str.lstrip('91')
    return df


def drop_duplicates(df):
    return df.drop_duplicates(subset=["Phone Number", "Prospect Id", "Opportunity Id"])


def remove_test_leads(df):
    """
    Removes test leads based on certain keywords in specific columns.
    """
    test_lead_identifiers = ["test", "Test", "TEST"]
    columns_to_check = ["Lead Name", "First Name", "Last Name", "Email"]

    columns_to_check = [col for col in columns_to_check if col in df.columns]

    test_leads_mask = df[columns_to_check].apply(
        lambda col: col.astype(str).str.contains('|'.join(test_lead_identifiers), case=False, na=False)
    ).any(axis=1)
    return df[~test_leads_mask]

def remove_lead_sources(df):
    excluded_sources=["Walkin","Campaign-SMS","Webinar","Camp","Signboard","C - ARPD","Ref-MVT","Inbound Email",
             'Center-Appt','Center-Phone','Other']
    df=df[~df["Lead Source"].isin( excluded_sources)]
    return df, excluded_sources

def exclude_crm(df):
    df=df[~df["Owner (User Name)"].isin(["AVH IT2","CRM Team Lead","CRM-3"])]
    return df

def clean_age_column(df):
    def clean_age(age):
        if pd.isna(age) or age in [".", ","]:
            return None
        age = str(age).lower()
        if 'bais' in age:
            return 22
        if 'month' in age:
            months = re.findall(r'(\d+)', age)
            return round(float(months[0]) / 12, 2) if months else None
        age = re.sub(r'[^\d\.]', '', age)
        try:
            return float(age) if age else None
        except ValueError:
            return None

    df['Age'] = df['Age'].apply(clean_age)
    df['Age'] = df['Age'].apply(lambda x: x if x < 120 else None)
    df['Age'] = pd.to_numeric(df['Age'], errors='coerce')
    return df


def cap_outliers_and_group_age(df):
    def cap_outliers(age):
        return None if age > 120 or age < 0.1 else age

    def age_group_function(age):
        if pd.isna(age):
            return "Unknown"
        elif age >= 80:
            return '[80-90]'
        elif age >= 70:
            return '[70-80]'
        elif age >= 60:
            return '[60-70]'
        elif age >= 50:
            return '[50-60]'
        elif age >= 40:
            return '[40-50]'
        elif age >= 30:
            return '[30-40]'
        elif age >= 20:
            return '[20-30]'
        elif age >= 10:
            return '[10-20]'
        else:
            return '[0-10]'

    df['Age'] = df['Age'].apply(cap_outliers)
    df['Age Group'] = df['Age'].apply(age_group_function)
    return df


def preprocess_text_column(df, column_name):
    def preprocess_text(text):
        if pd.isna(text):
            return ""
        text = re.sub(r'[^\w\s]', '', text)
        return ' '.join(text.split())

    df[column_name] = df[column_name].apply(preprocess_text)
    df["Text Length"] = df[column_name].str.len()
    return df

def rename_lead_sources(df):
    df["Lead Source"] = df["Lead Source"].replace({
        "WHP - Direct Corp": 'WHP - Aggregate Corp', 'Inbound Phone call': "Ph-SEO",
        'Outbound Phone call': "Ph-SEO", 'Referral Sites': 'Ref-Doctor',
        'Ref-Other': 'Ref-Patient', 'Instagram-SEM': 'Social Media',
    })
    return df


def clean_primary_disease(df):
    mapping = {
        "Orthopedics": "Orthopaedics",
        "Male Reproductive Disorders": "Male Reproductive Disorder",
    }
    df["Primary Disease"] = df["Primary Disease"].replace(mapping)
    return df

def clean_crm(df):
    df=df[~df["Owner (User Name)"].isin(["AVH IT2","CRM Team Lead","CRM-3"])]
    return df

def rename_primary_physician(df):
    mapping={
        'Dr Ajithkumar  Vivekanandan(AVHVN)':'Dr Ajithkumar V',
        'Dr Ajithkumar V (AHLL-KP)':'Dr Ajithkumar V',
        'Dr Smitha Jayadev':'Dr Smitha Jayadev',
        'Dr Smitha Jayadev (AHLL-KP)':'Dr Smitha Jayadev',
        'Dr Smitha Jayadev(AHLL-KP)':'Dr Smitha Jayadev',
        'Dr Swetha Suvarna (HRBR)':'Dr Swetha Suvarna',
        'Dr Swetha Suvarna-AVDW':'Dr Swetha Suvarna',
        'Dr Tinkle Rani (AVND)':'Dr Tinkle Rani',
        'Dr Tinkle Rani(AVND)':'Dr Tinkle Rani',
        'Dr Zankhana Buch-BG Road':'Dr Zankhana Buch',
        'Dr. Aishwarya Chand':'Dr. Aishwarya Chand',
        'Dr. Aishwarya Chand (AVHR)':'Dr. Aishwarya Chand',
        'Dr. Aishwarya Chand(HRBR)':'Dr. Aishwarya Chand',
        'Dr. Aishwarya Lakshmi (AVHD)':'Dr. Aishwarya Chand',
        'Dr. Aishwarya Lakshmi (SSAVCIO)':'Dr. Aishwarya Chand',
        'Dr. Anagha J':'Dr. Anagha J',
        'Dr. Anagha J (AVND)':'Dr. Anagha J',
        'Dr. Aswathi (AVM)':'Dr. Aswathi',
        'Dr. Aswathi (AVND)':'Dr. Aswathi',
        'Dr. Aswathi A T':'Dr. Aswathi A T',
        'Dr. Aswathi AT (AVM)':'Dr. Aswathi A T',
        'Dr. Bheema Bhatta':'Dr. Bheema Bhatta',
        'Dr. Bheema Bhatta (AVM)':'Dr. Bheema Bhatta',
        'Dr. Bheema Bhatta (AVND)':'Dr. Bheema Bhatta',
        'Dr. Bheema Bhatta-AVND':'Dr. Bheema Bhatta',
        'Dr. Byresh Appaiah (AVHR)':'Dr. Byresh Appaiah (HRBR)',
        'Dr. Deepika Gunawan':'Dr. Deepika Gunawant',
        'Dr. Jairam Nair (AVK)':'Dr. Jairam Nair',
        'Dr. Jairam Nair (AVND)':'Dr. Jairam Nair',
        'Dr. Kalpita Thakre':'Dr. Kalpita Thakre',
        'Dr. Kalpita Thakre(HRBR)':'Dr. Kalpita Thakre',
        'Dr. Nidhin A M':'Dr. Nidhin A M',
        'Dr. Nidhin A M (AVHD)':'Dr. Nidhin A M',
        'Dr. Nidhin A M (HRBR)':'Dr. Nidhin A M',
        'Dr. Prathyusha  V(AVHVN)':'Dr. Prathyusha',
        'Dr. Prathyusha (AHLL-KP)':'Dr. Prathyusha',
        'Dr. Sandhya Ramesh (AVM)':'Dr. Sandhya Ramesh',
        'Dr. Shashidhara Gopalkrishna (AVHD)':'Dr. Shashidhara Gopalkrishna',
        'Dr. Shashidhara Gopalkrishna (HRBR)':'Dr. Shashidhara Gopalkrishna',
        'Dr. Srinivasa Pandey (AVM)':'Dr. Srinivasa Pandey',
        'Dr. Srinivasa Pandey (AVND)':'Dr. Srinivasa Pandey',
        'Dr. Sushma M (AVHR)':'Dr. Sushma M',
        'Dr. Sushma M (HRBR)':'Dr. Sushma M',
        'Dr. Swathi Bhat': 'Dr. Swathi Bhatt',
        'Dr. Swathi Bhat (AVCMI)': 'Dr. Swathi Bhatt',
        'Dr. Swathi Bhatt': 'Dr. Swathi Bhatt',
        'Dr. Vasantha Lakshmi':'Dr. Vasantha Lakshmi',
        'Dr. Vasantha Lakshmi(HRBR)':'Dr. Vasantha Lakshmi',
        'Dr. Vimarsha S': 'Dr. Vimarsha S',
        'Dr. Vimarsha S (SSAVCIO)': 'Dr. Vimarsha S',
        'Dr. Zankhana Buch (AVCMI)':'Dr. Zankhana Buch',
        "Dr. Zankhana Buch (AVHD)":'Dr. Zankhana Buch',
        'Dr. Zankhana Buch (AVHR)':'Dr. Zankhana Buch',
        'Dr. Zankhana Buch (HRBR)':'Dr. Zankhana Buch',"Dr Ajithkumar  Vivekanandan(AVHVN)":'Dr Ajithkumar V',
    'Dr Ajithkumar V (AHLL-KP)':'Dr Ajithkumar V',
    'Dr Shrinivasa Pandey-AVND':'Dr Shrinivasa Pandey',
    'Dr Nagendra Kumar (HRBR)':'Dr Nagendra',
    'Dr Shrinivasa Pandey-AVND':'Dr Shrinivasa Pandey',
    'Dr Smitha Jayadev (AHLL-KP)':'Dr Smitha Jayadev',
    'Dr Smitha Jayadev (AHLL-KP)':'Dr Smitha Jayadev',
    'Dr Smitha Jayadev(AHLL-KP)':'Dr Smitha Jayadev',
    'Dr Supraja Reddy (AVND)':'Dr Supraja Reddy',
    'Dr Susmitha C (AHLL-KP)':'Dr Susmitha C',
    'Dr Swetha Suvarna (HRBR)':'Dr Swetha Suvarna',
    'Dr Swetha Suvarna-AVDW':'Dr Swetha Suvarna',
    'Dr Tinkle Rani (AVND)':'Dr Tinkle Rani',
    'Dr Tinkle Rani(AVND)':'Dr Tinkle Rani',
    'Dr Vimarsha S(Diva)':'Dr Vimarsha S',
    'Dr Zankhana Buch-BG Road':'Dr. Zankhana Buch',
    'Dr. Aishwarya Chand (AVHR)':'Dr. Aishwarya Chand',
    'Dr. Aishwarya Chand(HRBR)':'Dr. Aishwarya Chand',
    'Dr. Aishwarya Lakshmi (AVHD)':'Dr. Aishwarya Lakshmi',
    'Dr. Aishwarya Lakshmi (SSAVCIO)':'Dr. Aishwarya Lakshmi',
    'Dr. Anagha J (AVND)':'Dr. Anagha J',
    'Dr. Anooj Chakrapani (AVM)':'Dr. Anooj Chakrapani',
    'Dr. Ashima Sardana (AVM)':'Dr. Ashima Sardana',
    'Dr. Aswathi (AVM)':'Dr. Aswathi',
    'Dr. Aswathi (AVND)':'Dr. Aswathi',
    'Dr. Aswathi AT (AVM)':'Dr. Aswathi A T',
    'Dr. Bheema Bhatta (AVM)':'Dr. Bheema Bhatta',
    'Dr. Bheema Bhatta (AVM)':'Dr. Bheema Bhatta',
    'Dr. Bheema Bhatta (AVND)':'Dr. Bheema Bhatta',
    'Dr. Bheema Bhatta-AVND':'Dr. Bheema Bhatta',
    'Dr. Byresh Appaiah (AVHR)':'Dr. Byresh Appaiah',
    'Dr. Byresh Appaiah (HRBR)':'Dr. Byresh Appaiah',
    'Dr. Deepika Gunawan':'Dr. Deepika Gunawan',
    'Dr. Deepika Gunawant':'Dr. Deepika Gunawan',
    'Dr. Girish Varrier (AVHD)':'Dr. Girish Varrier',
    'Dr. Jairam Nair (AVK)':'Dr. Jairam Nair',
    'Dr. Jairam Nair (AVND)':'Dr. Jairam Nair',
    'Dr. Kalpita Thakre(HRBR)':'Dr. Kalpita Thakre',
    'Dr. Nidhin A M (AVHD)':'Dr. Nidhin A M',
    'Dr. Prathyusha  V(AVHVN)':'Dr. Prathyusha  V',
    'Dr. Prathyusha (AHLL-KP)':'Dr. Prathyusha  V',
    'Dr. Sandhya Ramesh (AVM)':'Dr. Sandhya Ramesh',
    'Dr. Shashidhara Gopalkrishna (AVHD)':'Dr. Shashidhara Gopalkrishna',
    'Dr. Shashidhara Gopalkrishna (HRBR)':'Dr. Shashidhara Gopalkrishna',
    'Dr. Smitha  Jaydev(AVHVN)':'Dr. Smitha  Jaydev',
    'Dr. Srinivasa Pandey (AVM)':'Dr. Srinivasa Pandey',
    'Dr. Srinivasa Pandey (AVND)':'Dr. Srinivasa Pandey',
    'Dr. Srinivasa Pandey-AVND':'Dr. Srinivasa Pandey',
    'Dr. Sunil Arya (AVM)':'Dr. Sunil Arya',
    'Dr. Sushma M (AVHR)':'Dr. Sushma M',
    'Dr. Sushma M (HRBR)':'Dr. Sushma M',
    'Dr. Swathi Bhat (AVCMI)':'Dr. Swathi Bhat',
    'Dr. Swathi Bhatt':'Dr. Swathi Bhat',
    'Dr. Swathi Bhatt':'Dr. Swathi Bhat',
    'Dr. Vasantha Lakshmi':'Dr. Vasantha Lakshmi',
    'Dr. Vasantha Lakshmi(HRBR)':'Dr. Vasantha Lakshmi',
    'Dr. Vimarsha S':'Dr. Vimarsha S',
    'Dr. Vimarsha S (SSAVCIO)':'Dr. Vimarsha S',
    'Dr. Zankhana Buch (AVCMI)':'Dr. Zankhana Buch',
    'Dr. Zankhana Buch (AVHD)':'Dr. Zankhana Buch',
    'Dr. Zankhana Buch (AVHR)':'Dr. Zankhana Buch',
    'Dr. Zankhana Buch (HRBR)':'Dr. Zankhana Buch',
    'Dr. Srinivasa Pandey':'Dr. Srinivasa Pandey',
    'Dr Shrinivasa Pandey':'Dr. Srinivasa Pandey'}

    df.loc[:,"Primary Physician"] = df["Primary Physician"].replace(mapping)
    return df


def remove_columns(df):
    ignored=['Email Address', 'Lead Owner Email', 'Lead Number',
       'Opportunity Name', 'Opportunity Event','Owner (User Email)','Modified By (User ID)',
        'Modified By (User Email)',
       'Created By (User ID)', 'Created By (User Name)','Created By (User Email)',
         'ChatLink - ChatLink', 'ChatLink - Status',
       'Corporate Name','Campaign Name', 'Appointment ID', 
       'Documents - Status','Opportunity Event Name', 'Owner (User ID)',
       'INSURANCE COMPANY', 'Insurance UIN', 'Opportunity Status',  
       'Comment', 'HIS ID', 'Source - Campaign',
       'Source - Medium', 'Source - Term', 'Source - Content', 
       'Source - Name', 'Employer Name', 'Employer Other',
       'Phone Number.1', 'Email', 'Date of Birth', 'Referral - Dr', 
       'Referral - Patient', 'Referral - Other',
         'Product', 'Origin', 'Description', 'Expected Deal Size',
       "Payment Status",'Special Requirement', 'Health Status', 
       'Consultation Type','Consultation Charges','NetSuite ID', 'Appt Sys ID', 'IVR Sys ID', 'Patient Date Time',
         'Treatment Date Time','Health Management Date Time',
       'Disease Inquired','Lead Source URL - URL','Lead Source URL - Status','Enquiry Date','RNR Attempts',
         'WhatsApp Number','Appointment Completion Status',
       'NFT Qualification_BG','Country','First Name','Cough', 'Cold', 'Fever','Follow Up Date Time',
       'Pain', 'Other', 'Other Disease Specialties','Integrative Care Offerings', 'Sleep', 'Appetite', 'Digestion',
       'High Stress', 'Bowels', 'Urination', 'Obesity', 'Vitality', 'Hair','Owner (User Name)','Modified By (User Name)',
       'Lead Sub Status','utm_campaign_Campaign_Name',
         'utm_content_Campaign Keywords','utm_medium_Campaign Ad Group','Opportunity Age','City',
       'Skin','Other Disease Conditions', 'Last Name', 'Lead Name','Appointment Message', 'Appointment Status','Locality', 'appt_locationId',
       'appt_practionerId', 'Disease Related Questions','Actual Deal Size', 'Expected Closure Date', 'utm_network','Actual Closure Date',]
    df=df.drop(ignored,axis=1)
    return df

def utm_campaign_source(df):
    df['utm_source_Campaign Source']=df['utm_source_Campaign Source'].fillna("Unknown")
    df["utm_source_Campaign Source"]=df['utm_source_Campaign Source'].replace(
        {"google":"Google","fb":"Social Media","Na":"Unknown",'Web-SEO':"Google",
        "ig":"Social Media",'facebook':"Social Media",'Instagram':"Social Media"})
    return df

def process_appointment_fixed(df):
    """
    Processes the Appointment Fixed column based on the following rules:
    1. If 'Appointment Date' is present, set 'Appointment Fixed' to 'Yes'.
    2. If 'Appointment Date' is missing for 'Won' leads, fill with 'Lead Created On' and set 'Appointment Fixed' to 'Yes'.
    3. Otherwise, set 'Appointment Fixed' to 'No'.

    Args:
        df (pd.DataFrame): The DataFrame containing lead data.

    Returns:
        pd.DataFrame: Updated DataFrame with 'Appointment Fixed' and updated 'Appointment Date'.
    """
    # Fill missing 'Appointment Date' for 'Won' leads with 'Lead Created On'
    df['Appointment Date Time'] = df['Appointment Date Time'].fillna(
        df.loc[df['Lead Status'] == 'Won', 'Lead Created On']
    )
    
    
    # Create 'Appointment Fixed' column
    df['Appointment Fixed?'] = df['Appointment Date Time'].apply(
        lambda x: 'Yes' if pd.notna(x) else 'No'
    )

    return df


def parse_date(date_str):
    """
    Parses a date string with multiple possible formats.

    Args:
        date_str (str): The date string to parse.

    Returns:
        datetime or None: The parsed datetime object or None if parsing fails.
    """
    if pd.isna(date_str) or not isinstance(date_str, str):
        return None
    formats = ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d %I:%M:%S %p', '%d-%m-%Y %H:%M']
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    return None


# Extract date range from a column
def get_date_range(df, date_column):
    if date_column in df.columns:
        parsed_dates = df[date_column].apply(parse_date)
        valid_dates = parsed_dates.dropna()
        if not valid_dates.empty:
            min_date = valid_dates.min().strftime("%d %B %Y")
            max_date = valid_dates.max().strftime("%d %B %Y")
            return min_date, max_date
    return "Unknown", "Unknown"

# Read data with mixed types handling
def data_read(file_paths, encodings):
    dataframes = [
        pd.read_csv(path, encoding=encoding, low_memory=False)
        for path, encoding in zip(file_paths, encodings)
    ]
    return pd.concat(dataframes, ignore_index=True)

def parse_date(date_val):
    formats = ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d %I:%M:%S %p', '%d-%m-%Y %H:%M']
    if isinstance(date_val, pd.Timestamp):  # If already a datetime object, return it
        return date_val
    if isinstance(date_val, str):  # Process only strings
        for fmt in formats:
            try:
                return datetime.strptime(date_val, fmt)
            except ValueError:
                continue
    return None  # Return None if no format matches

def lead_sources(df):
    df["Lead Source_Renamed"]=df["Lead Source"].replace({
    "WHP - Direct Corp":'WHP - Aggregate Corp','Inbound Phone call':"Ph-SEO",
    'Outbound Phone call':"Ph-SEO",'Referral Sites':'Ref-Doctor',
    'Ref-Other':'Ref-Patient','Instagram-SEM':'Social Media','Health Checkup':'Ref-Doctor',
    'Web-Chat':'Web-Chat-SEO','FB-SEM':'Social Media','FB-SEO':'Social Media',
    'REG-SEO':'Ref-Doctor' ,'Social Media':'Social Media','Ref-Partner':'Ref-Patient',
    'Ph-Appt':"Ph-SEO"
})
    return df

def remove_quality(df):
    df=df[df["Lead Quality"]!='4223']
    return df

from dateutil import parser

def parse_date_app(date_str):
    if pd.isna(date_str): 
        return None
    try:
        return parser.parse(str(date_str).strip())
    except Exception:
        return None  

def clean_leadsquared_data(df):
    """
    Cleans the leadsquared data and returns a tuple of cleaned data and metadata.
    """
    df = clean_phone_numbers(df)
    df['Modified On'] = df['Modified On'].apply(parse_date)  
    df['Modified On'] = pd.to_datetime(df['Modified On'], errors='coerce')  # Ensure all values are datetime
    df =rename_lead_status(df)
    df=exclude_crm(df)
    df= remove_quality(df)
    # df = drop_duplicates(df)
    df =rename_primary_physician(df)
    df = remove_test_leads(df)
    df = rename_lead_sources(df)
    df = clean_age_column(df)
    df = cap_outliers_and_group_age(df)
    df = preprocess_text_column(df, "Presenting Complaint - Presenting Complaint")
    df = clean_primary_disease(df)
    df=lead_sources(df)
    df=utm_campaign_source(df)
    # Add 'Appointment Fixed?' column
    df = process_appointment_fixed(df)
    df, excluded_sources = remove_lead_sources(df)
    df=remove_columns(df)
    df['Parsed Appointment DateTime'] = df['Appointment Date Time'].apply(parse_date_app)
    df =sort_dates(df)
    print(df["Lead Status"].value_counts())
    # Get date range using get_date_range
    date_column = "Modified On"  
    min_date, max_date = get_date_range(df, date_column)
    return df, {
        "excluded_sources": excluded_sources,
        "date_range": (min_date, max_date)
    }


