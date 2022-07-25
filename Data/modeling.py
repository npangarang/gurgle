# Processing
import numpy as np
import pandas as pd
import datetime
import warnings

from datetime import datetime
from datetime import timedelta
from plotly.offline import init_notebook_mode

from prophet.diagnostics import cross_validation
from prophet.diagnostics import performance_metrics
from prophet import Prophet
import tqdm
import itertools

init_notebook_mode(connected=True)
warnings.filterwarnings("ignore")

def outlier_replacement(serie):
    # outliers correction
    serie_centered=serie-serie.mean()
    sd=serie.std()
    outliers=np.abs(serie_centered)>3*sd
    serie_centered_fixed=serie.copy()
    serie_centered_fixed[outliers]=np.nanmedian(serie_centered_fixed)
    return serie_centered_fixed

def get_parameters(**kwargs):
    """
    Takes dictionary input of model parameters to create a list for iterations
    Returns:
    params: list of parameters
    modellist: list to initialize top 5 models
    bestlist: list to initializr top models
    """
    grid = {**kwargs}
    params = [dict(zip(grid.keys(), v)) for v in itertools.product(*grid.values())]

    #Adding model numbers
    modellist = list()
    for i in range(len(params)):
        modellist.append("Model_" + str(i))
    #Best model number
    bestlist = list()
    for j in range(5):
        bestlist.append("Rank_" + str(j+1))
    return params, modellist, bestlist

def parameter_tuner(data_dict, modelgrowth='logistic', growth_cap=None, growth_floor=None):
    """
    Improved to take dynamic input for growth, cap, floor, asu_bool
    Recommends a cutoff date if not passed, but by default would take input from website

    Update 09/30 -- removed covid filter, Added growth as an input
    Update 03/23 -- Yearly seasonality tuning
    ASU sigma filter
    Volume bins
    Using asu from Modeltraining-1 run
    variable flagDict is used to alert for volume change in queue

    """

    avg_error = list()
    best_results = dict()

    for key, value in tqdm.tqdm_notebook(data_dict.items(), total=len(data_dict)):
        if len(value) < 52:
            print("Length too short hence skiping code ", key)
            continue

        else:
            try:

                method = 'prophet'
                last_actual = value['Week_Ending_Date'].max()

                errorlist1 = list()

                buildmodel = value.copy()

                # Outliers
                buildmodel['CPASU'] = outlier_replacement(buildmodel['CPASU'])

                buildmodel = buildmodel.rename(columns={'Week_Ending_Date': 'ds', 'CPASU': 'y'})

                if modelgrowth == 'logistic':
                    upper_df = buildmodel[:52]
                    limit_df = buildmodel[-18:]

                    #                     avg = upper_df['y'].mean()
                    #                     stnd = upper_df['y'].std()
                    cap = upper_df['y'].sort_values(ascending=False).iloc[1]
                    floor = limit_df['y'].sort_values().iloc[1]

                    buildmodel['cap'] = cap
                    buildmodel['floor'] = floor

                # Validation part
                valid_time = last_actual - timedelta(weeks=26)

                kwargs = {'changepoint_prior_scale': [0.02, 0.1, 0.5],
                          'seasonality_prior_scale': [0.02, 0.05, 0.1]}

                all_params, modelnames, bestmodel = get_parameters(**kwargs)

                for params in all_params:

                    tm1 = Prophet(weekly_seasonality=False, daily_seasonality=False, yearly_seasonality=10,
                                  growth=modelgrowth, seasonality_mode='additive', **params,
                                  uncertainty_samples=False)  # Fit model with given params

                    #             with suppress_stdout_stderr():
                    tm1.fit(buildmodel)

                    my_time = datetime.min.time()
                    valid_time = datetime.combine(valid_time, my_time)
                    valid_time = pd.Timestamp(valid_time)

                    df_cv1 = cross_validation(tm1, cutoffs=[valid_time], horizon='8 W', parallel="threads")
                    df_p1 = performance_metrics(df_cv1)

                    if len(buildmodel[buildmodel['y'] == 0]) > 0:  # Using MAE for queues where values are zeros
                        errorlist1.append(df_p1['mae'].values[0])
                    else:
                        errorlist1.append(df_p1['mape'].values[0])

                # Find the best parameters

                tuning_results = pd.DataFrame(all_params)
                tuning_results['mape'] = errorlist1
                tuning_results = tuning_results.sort_values('mape')[:5]
                tuning_results['Key'] = key
                tuning_results['Method'] = method
                best_results[key] = tuning_results[:1]

            except Exception as e:
                print(f"Error occured while working with {key}")
                print(e)

    return best_results

def convert_to_dict(data, list_learn, last_actual=None, history_check=6):
    """
    Modified march cycle - to filter for active queues
    Checks data in past 6 weeks

    """
    if not last_actual:
        last_actual = data['Week_Ending_Date'].max()

    date_to_check = last_actual - timedelta(weeks=history_check)

    raw_dict = dict()
    dead = list()

    for i in list_learn:
        df = data[data['object_code'] == i][['Week_Ending_Date', 'CPASU']].sort_values('Week_Ending_Date')
        check_valid = df[df['Week_Ending_Date'] > date_to_check]

        if (len(check_valid) == history_check) & (check_valid['CPASU'].sum() > 0):
            raw_dict[i] = df
        else:
            dead.append(i)
            continue

    print(f"Total active queues: {len(raw_dict)}")
    print(f"Total dead queues: {len(dead)}")

    return raw_dict, dead

def create_forward_weeks(start_date, future_weeks=64):
    """
    Creates Future time frame for predictions from given start date. Output is a list
    """
    dates = list()
    for i in range(future_weeks +1):
        dates.append(start_date + timedelta(weeks = i))
    return dates

def queue_details(td):
    short = 0
    short_ls = list()
    medium = 0
    medium_ls = list()
    workable = 0
    workable_ls = list()
    long = 0
    avg_length = list()
    for k, v in td.items():
        if len(v) < 8:
            short += 1
            short_ls.append(k)
        elif len(v) < 26:
            medium += 1
            medium_ls.append(k)
        elif len(v) < 52:
            workable += 1
            workable_ls.append(k)
        else:
            long += 1
            avg_length.append(len(v))

    print("Following queue history observed \n", 'Long queue >52: ', long, ' \n workable (26-52): ', workable,
          ' \n medium (<26): ', medium, '\n short(8 weeks): ', short, '\n Average length of long queue',
          sum(avg_length) / len(avg_length))
    return short_ls, medium_ls, workable_ls

def convert_dict_to_df(combine_dict):
    i=0
    for key, value in combine_dict.items():
        if i == 0:
            df = value
            i+=1
        else:
            df = pd.concat([df,value])
#     assert df['Current_FC_Code'].nunique() == len(combine_dict)
    print(f"Total {len(combine_dict)} forecast codes converted to table")
    return df

def predict_wroklable_queues(list_workable, train_dict, future_weeks=77, last_actuals=None):
    output = dict()
    for k, v in tqdm.tqdm_notebook(train_dict.items()):
        if k in list_workable:
            train_sample = v.copy()
            train_sample['CPASU'] = train_sample['CPASU'].replace({np.inf: 0})
            r = pd.date_range(start=train_sample['Week_Ending_Date'].min(), end=train_sample['Week_Ending_Date'].max(),
                              freq='W-FRI')
            train_sample = train_sample.set_index('Week_Ending_Date').reindex(r).fillna(0.0)
            train_sample.index = train_sample.index.rename('ds')

            try:
                if len(train_sample) > 35:
                    model = ExponentialSmoothing(train_sample['CPASU'], trend=None,
                                                 seasonal='add', seasonal_periods=30).fit(optimized=True)
                else:
                    model = ExponentialSmoothing(train_sample['CPASU'], trend=None, seasonal='add',
                                                 seasonal_periods=12).fit(optimized=True)
            except Exception as e:
                print(e)
                continue

            average = train_sample['CPASU'][-16:].mean()

            prediction = pd.DataFrame(
                model.forecast(steps=future_weeks).reset_index().rename(columns={'index': 'ds', 0: 'yhat'}))
            prediction['yhat'] = prediction['yhat'].clip(lower=0)
            prediction['Average'] = average

            prediction['Average_AVG'] = 0.5 * prediction['yhat'] + 0.5 * average
            # pay attention to seasonality and tweak above
            # 0.5 works last 4 cycles

            prediction = pd.concat([train_sample.reset_index(), prediction])
            output[k] = prediction

    return output

