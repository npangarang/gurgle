# Libraries
import plotly.graph_objs as go
import warnings
from plotly.offline import init_notebook_mode, iplot

init_notebook_mode(connected=True)
warnings.filterwarnings("ignore")

def plot_fbpred(train_dict, pred_dict):
    pr_buttons = []
    pr_plotdata = []
    j = 0
    length = 2*len(train_dict)

    for key in sorted(train_dict):
        if key in list(pred_dict.keys()):
            #Actuals
            pr_plotdata.append(go.Scatter(
            x = train_dict[key]['Week_Ending_Date'],
            y = train_dict[key]['CPASU'].values,
            mode = 'lines',
            name = 'Actuals',
            line =  {'color' : '#77acf1'},
            connectgaps=False
        #         text=
            ))

            #Scorecarrd
            pr_plotdata.append(go.Scatter(
            x = pred_dict[key]['ds'],
            y = pred_dict[key]['yhat'].values,
            mode = 'lines',
            name = 'Prediction',
            line =  {'color' : '#f18973'},
            connectgaps=False
        #         text=
            ))


            x = [False]*(length+1)                                      # Sets the visibility of all plots to False
            x[j] = True
            x[j+1] = True
    #         x[j+2] = True

            j=j+2

            pr_buttons.append (dict(label = key,                              # All the plots together
                                        method = 'update',                      # Update the graph with current button values
                                        args = [{'visible': x},                 # Assigning the visibility of all the traces in the Reset State
                                        {'title' : ('Offered for ' + key )}],
                                        ))
        else:
            continue

    updatemenus = list([
        dict(type = "dropdown",
             active = -1,
             showactive = True,
             buttons = pr_buttons,
             font = dict(color = 'green',    # Setting the font of the Button
                         size = 10,
                        ),
             bgcolor = '#E2E2E2',            # Button Settings
             borderwidth = 2,
             bordercolor = '#FFFFFF',
             x = -.1,
             y = 0.8
             )])
        #Layout
    layout = go.Layout(updatemenus = updatemenus,
                       title='Offered Forecast',
                       title_x = 0.5,
                       yaxis=dict(title='Offered'))

    fig = dict(data=pr_plotdata, layout= layout)

    iplot(fig, filename = "SR_Forecast.html")

def plot_predictions(train_dict, pred_dict):
    pr_buttons = []
    pr_plotdata = []
    j = 0
    length = 4 * len(train_dict)

    for key in sorted(train_dict):
        if key in list(pred_dict.keys()):
            # Actuals
            pr_plotdata.append(go.Scatter(
                x=train_dict[key]['Week_Ending_Date'],
                y=train_dict[key]['CPASU'].values,
                mode='lines',
                name='Actuals',
                line={'color': '#77acf1'},
                connectgaps=False
                #         text=
            ))

            # Scorecarrd
            pr_plotdata.append(go.Scatter(
                x=pred_dict[key]['ds'],
                y=pred_dict[key]['yhat'].values,
                mode='lines',
                name='Prediction',
                line={'color': '#f18973'},
                connectgaps=False
                #         text=
            ))

            # AVG
            pr_plotdata.append(go.Scatter(
                x=pred_dict[key]['ds'],
                y=pred_dict[key]['Average'].values,
                mode='lines',
                name='Average',
                connectgaps=False
                #         text=
            ))

            # Holts_AVG
            pr_plotdata.append(go.Scatter(
                x=pred_dict[key]['ds'],
                y=pred_dict[key]['Average_AVG'].values,
                mode='lines',
                name='Average_AVG',
                connectgaps=False
                #         text=
            ))

            x = [False] * (length + 1)  # Sets the visibility of all plots to False
            x[j] = True
            x[j + 1] = True
            x[j + 2] = True
            x[j + 3] = True

            j = j + 4

            pr_buttons.append(dict(label=key,  # All the plots together
                                   method='update',  # Update the graph with current button values
                                   args=[{'visible': x},
                                         # Assigning the visibility of all the traces in the Reset State
                                         {'title': ('Offered for ' + key)}],
                                   ))
        else:
            continue

    updatemenus = list([
        dict(type="dropdown",
             active=-1,
             showactive=True,
             buttons=pr_buttons,
             font=dict(color='green',  # Setting the font of the Button
                       size=10,
                       ),
             bgcolor='#E2E2E2',  # Button Settings
             borderwidth=2,
             bordercolor='#FFFFFF',
             x=-.1,
             y=0.8
             )])
    # Layout
    layout = go.Layout(updatemenus=updatemenus,
                       title='Offered Forecast',
                       title_x=0.5,
                       yaxis=dict(title='Offered'))

    fig = dict(data=pr_plotdata, layout=layout)

    iplot(fig, filename="SR_Forecast.html")
