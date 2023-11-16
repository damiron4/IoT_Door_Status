import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import numpy as np
from datetime import datetime, timedelta
import random

def calculate_weights(timestamps):
    weights = []
    now = datetime.now()
    s = len(timestamps)
    for i in range(s):
        if i == 0:
            w = (timestamps[i+1] - (now - timedelta(days=1))).seconds / 3600
        elif i == s-1:
            w = (now - timestamps[i]).seconds / 3600
        else:
            w = (timestamps[i+1] - timestamps[i]).seconds / 3600
        weights.append(w)
    return weights
    
def calculate_starts(timestamps):
    starts = [0]
    now = datetime.now()
    for i in range(1, len(timestamps)):
        if i == 1:
            s = (timestamps[i] - (now - timedelta(days=1))).seconds / 3600
        else:
            s = starts[i-1] + (timestamps[i] - timestamps[i-1]).seconds / 3600
        starts.append(s)
    return starts

def generate_timestamps(n):
    current_time = datetime.now()
    timestamps = [current_time - timedelta(hours=random.randint(1, 23), minutes=random.randint(0, 59)) for _ in range(n-1)]
    timestamps.append(current_time - timedelta(days=1, minutes=59))
    timestamps.sort()
    door_status = np.tile([0,1],24//2)
    return timestamps, door_status

def get_plot(weights, starts, colors):
    plt.figure(figsize=(7, 2.43))
    plt.barh(0, weights, color=colors, height=1, left=starts)

    # Customize the plot
    plt.yticks([])
    plt.xticks(np.arange(7.5, 31.5, 8), [(datetime.now() - timedelta(hours=i)).strftime('%H:%M') for i in range(0, 24, 8)][::-1])
    # plt.rcParams['font.sans-serif'] = "Roboto"
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    plt.gca().spines['bottom'].set_visible(False)
    plt.gca().spines['left'].set_visible(False)
    plt.tick_params(axis="x", bottom=False)
    plt.tight_layout()
    plt.margins(x=0, y=0)
    legend_elements = [Patch(facecolor='#F84F31', label='Closed'),
                       Patch(facecolor='#23C552', label='Open')]
    plt.legend(handles=legend_elements, loc='lower left', bbox_to_anchor=(-0.01, -0.18), prop={'size': 9}, ncols=2)
    
    # Save the plot
    filename = f'charts/door_status {datetime.now().strftime("%Y-%m-%d %H-%M-%S-%f")}.png'
    plt.savefig(filename)
    # plt.show()
    return filename

def get_daily_status(data):
    data = np.array(data)
    t1, t2 = np.split(data, 2, axis = 1)
    timestamps = t1.flatten().tolist()
    door_status = t2.flatten().tolist()
    # timestamps, door_status = generate_timestamps(24)
    weights = calculate_weights(timestamps)
    starts = calculate_starts(timestamps)
    colors = ['#F84F31' if status == 0 else '#23C552' for status in door_status]
    return get_plot(weights, starts, colors)