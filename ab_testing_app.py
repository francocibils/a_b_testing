# Import necessary packages
import pandas as pd
import numpy as np
import statsmodels.stats.api as sms
import streamlit as st

from statsmodels.stats.proportion import proportions_ztest, proportion_confint
from helper_functions import *

# Streamlit app
app_mode = st.sidebar.selectbox('Select Page', ['Home', 'Power Analysis', 'Manual A/B Testing', 'Automatic A/B Testing'])

if app_mode == 'Home':
    st.title('A/B Testing')
    st.markdown('This is a simple app that provides several tools.')
    st.markdown('1. Perform power analysis to determine the appropiate size for the sample to capture an specific effect.')
    st.markdown('2. Perform manual A/B testing by providing number of observations and conversions in control and treatment groups.')
    st.markdown('3. perform automatic A/B testing by providing an Excel o CSV file with the experiment results.')

if app_mode == 'Power Analysis':
    st.title('Power Analysis - Required sample size')
    st.markdown('Perform a power analysis to obtain the required sample size to get a specific effect size. Provide the control conversion rate and the desired effect size. Remember that the sum of both numbers can be at most 100% (since it does not make to think about a conversion rate higher that a 100%).')
    st.markdown('Note: On the left you may set the power of the test and the alpha, set to 80% and 5% by default.')

    power = st.sidebar.slider('Power of the test', min_value = 0., max_value = 1., step = 0.01, value = 0.8)
    alpha = st.sidebar.slider('Alpha', min_value = 0., max_value = 1., step = 0.01, value = 0.05)

    control_rate = st.slider('Control rate', min_value = 0., max_value = 1., step = 0.01)
    effect_size = st.number_input("Desired effect size (in %) over the control rate (control rate + desired effect size)", min_value = 0., value = 2., max_value = 100. - control_rate * 100) / 100

    if st.button('Get required observation size'):
        required_size = get_required_size(control_rate = control_rate, 
                                            desired_effect_size = effect_size, 
                                            power = power, 
                                            alpha = alpha)
        
        st.markdown(f'The required size to obtain an effect size of {effect_size * 100}%, given an {round(power, 2) * 100}% power test and significance level of {(round(alpha, 2)) * 100}% should at least consist of **{required_size}** observations.')

if app_mode == 'Manual A/B Testing':
    st.title('Manual A/B Testing')
    st.markdown('Perform an a two-tailed test by providing the results of the experiment: number of observations and conversions in control and treatments groups.')
    st.markdown('It will test the assumption that both proportions are the same against the possibility that they are different in any direction.')

    control_obs = st.number_input('Number of observations in the control group', min_value = 0, step = 1)
    treatment_obs = st.number_input('Number of observations in the treatment group', min_value = 0, step = 1)

    control_conversions = st.number_input('Number of conversions in the control group', min_value = 0, max_value = control_obs, step = 1)
    treatment_conversions = st.number_input('Number of conversions in the treatment group', min_value = 0, max_value = treatment_obs, step = 1)

    if st.button('Perform test'):
        zstat, pval = proportions_ztest(count = np.array([control_conversions, treatment_conversions]), nobs = np.array([control_obs, treatment_obs]))
        (lower_con, lower_treat), (upper_con, upper_treat) = proportion_confint(count = [control_conversions, treatment_conversions], nobs = [control_obs, treatment_obs], alpha = 0.05)

        if pval <= 0.05:
            st.markdown(f'With a p-value of {round(pval, 3)} we **reject** the null hypothesis and therefore there is a statistically significant difference between both groups.')
            st.markdown(f'The confidence interval for the **control** group is [{round(lower_con, 3)}, {round(upper_con, 3)}].')
            st.markdown(f'The confidence interval for the **treatment** group is [{round(lower_treat, 3)}, {round(upper_treat, 3)}].')
        else:
            st.markdown(f'With a p-value of {round(pval, 3)} we **fail to reject** the null hypothesis and therefore there is not enough evidence to suggest there is a statistically significant difference between both groups.')
            st.markdown(f'The confidence interval for the **control** group is [{round(lower_con, 3)}, {round(upper_con, 3)}].')
            st.markdown(f'The confidence interval for the **treatment** group is [{round(lower_treat, 3)}, {round(upper_treat, 3)}].')

if app_mode == 'Automatic A/B Testing':
    st.title('Automatic A/B Testing')
    st.markdown('Perform an a two-tailed test by providing the results of the experiment: Excel or CSV file.')
    st.markdown('It will test the assumption that both proportions are the same against the possibility that they are different in any direction.')
    st.markdown('Note: The file should have 3 columns in the following order: ID; column that specifies to which group the ID was assigned to; and, a column that tells whether the ID converted or not (1 if there was a conversion, 0 otherwise). The second column should have two values: *control* or *treatment*.')

    file = st.file_uploader("Upload a CSV or Excel file", type = ["csv", "xlsx"])

    if file is not None:
        file_type = get_file_type(file)
        
        if file_type == "csv":
            df = pd.read_csv(file)
        elif file_type == "xlsx":
            df = pd.read_excel(file, engine='openpyxl')

        if df.shape[1] != 3:
            st.warning(f'There are {df.shape[1]} columns. There should be only 3 columns: ID, conversion/treatment, and converted column.')

        # Rename columns
        df.columns = ['ID', 'con_treat', 'converted']

        # Split by control and treatment
        df_control = df[df['con_treat'] == 'control']
        df_treatment = df[df['con_treat'] == 'treatment']
        
        # Get sample size
        obs_control = df_control.shape[0]
        obs_treatment = df_treatment.shape[0]

        # Get amount of conversions in each group
        conv_control = df_control['converted'].sum()
        conv_treatment = df_treatment['converted'].sum()

        st.markdown('Some insights about the file provided:')
        st.markdown(f'1. There are {df.shape[0]} observations: {obs_control} belong to the control group (around {round(obs_control / df.shape[0], 4) * 100}%) and {obs_treatment} to the treatment group (around {round(obs_treatment / df.shape[0], 4) * 100}%).')
        st.markdown(f'2. There are {conv_control} conversions in the control group and {conv_treatment} in the treatment group.')
        st.markdown(f'3. The conversion rate is around {round(conv_control / obs_control, 4) * 100}% in the control group and {round(conv_treatment / obs_treatment, 4) * 100}% in the treatment group.')

    if st.button('Perform test'):
        
        zstat, pval = proportions_ztest(count = np.array([conv_control, conv_treatment]), nobs = np.array([obs_control, obs_treatment]))
        (lower_con, lower_treat), (upper_con, upper_treat) = proportion_confint(count = [conv_control, conv_treatment], nobs = [obs_control, obs_treatment], alpha = 0.05)

        if pval <= 0.05:
            st.markdown(f'With a p-value of {round(pval, 3)} we **reject** the null hypothesis and therefore there is a statistically significant difference between both groups.')
            st.markdown(f'The confidence interval for the **control** group is [{round(lower_con, 3)}, {round(upper_con, 3)}].')
            st.markdown(f'The confidence interval for the **treatment** group is [{round(lower_treat, 3)}, {round(upper_treat, 3)}].')
        else:
            st.markdown(f'With a p-value of {round(pval, 3)} we **fail to reject** the null hypothesis and therefore there is not enough evidence to suggest there is a statistically significant difference between both groups.')
            st.markdown(f'The confidence interval for the **control** group is [{round(lower_con, 3)}, {round(upper_con, 3)}].')
            st.markdown(f'The confidence interval for the **treatment** group is [{round(lower_treat, 3)}, {round(upper_treat, 3)}].')