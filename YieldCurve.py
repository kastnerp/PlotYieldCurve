import traceback
import urllib3

urllib3.disable_warnings()
import xmltodict

# get_ipython().run_line_magic('matplotlib', 'inline')
import matplotlib.pyplot as plt

plt.style.use('seaborn-whitegrid')
import numpy as np
import matplotlib.animation as animation
import imageio
from pygifsicle import optimize
import numpy as np


year = 2020
number_days = 110


def getxml():
    url = "http://www.treasury.gov/resource-center/data-chart-center/interest-rates/pages/XmlView.aspx?data=yieldyear&year=" + str(
        year)
    http = urllib3.PoolManager()
    response = http.request('GET', url)

    try:
        data = xmltodict.parse(response.data)
    except:
        print("Failed to parse xml from response (%s)" %
              traceback.format_exc())
    return data


yieldcurve = getxml()

months_string = [
    'd:BC_1MONTH', 'd:BC_2MONTH', 'd:BC_3MONTH', 'd:BC_6MONTH', 'd:BC_1YEAR',
    'd:BC_2YEAR', 'd:BC_3YEAR', 'd:BC_5YEAR', 'd:BC_7YEAR', 'd:BC_10YEAR',
    'd:BC_20YEAR', 'd:BC_30YEAR'
]

months = [
    1, 2, 3, 6, 12, 12 * 2, 12 * 3, 12 * 5, 7 * 12, 10 * 12, 20 * 12, 30 * 12
]

months_in_years = ['', '', '', '', 1, 2, 3, 5, 7, 10, 20, 30]


def get_data(day, months):
    vals = []
    time = "0"

    for i in months_string:
        try:
            string = yieldcurve['pre']['entry'][day]['content'][
                'm:properties'][i]['#text']
            time = yieldcurve['pre']['entry'][day]['content']['m:properties'][
                       'd:NEW_DATE']['#text'][:10]
            vals.append(float(string))


        except:
            print("The day", day, "doesn't exist in the data.")
    image = plot_image(months, vals, time)
    return image


def plot_image(months, vals, time):
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(months, vals, '-', color='black')
    ax.set_ylim(-0.5, 4)
    ax.set_xlim(0, 360)
    ax.set_title("U.S. Treasury Yield Curve on: " + time)
    ax.set_xlabel("Years")
    ax.set_ylabel("ROI [%]")
    ax.set_xticks(months)
    ax.set_xticklabels(months_in_years)

    # Used to return the plot as an image array
    fig.canvas.draw()  # draw the canvas, cache the renderer
    image = np.frombuffer(fig.canvas.tostring_rgb(), dtype='uint8')
    image = image.reshape(fig.canvas.get_width_height()[::-1] + (3,))
    return image


kwargs_write = {'fps': 1.0, 'quantizer': 'nq'}
filename = './yield_curve_' + str(year) + '.gif'
imageio.mimsave(filename,
                [get_data(i, months) for i in range(number_days)],
                fps=10)

# Optimize GIF

optimize(filename)
