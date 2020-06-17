# -*- coding: utf-8 -*-
"""
Created on Tue Jun 16 21:50:30 2020

@author: Jean
"""

# The first way to create an Orange palette is sampleing from matplotlib colormap
import numpy as np
import matplotlib.cm as cm

def palette(mapName):
    cmap = cm.get_cmap(mapName)
    colors = []
    for i in range(256):
        colors.append(cmap((i)/256))
    carray = np.array(colors)
    carray = carray[:,0:3]
    carray = np.round(carray*256,0)
    carray = carray.astype(np.ubyte)
    colors = carray.tolist()
    return colors

# 从 matplotlib预定义的连续颜色几生成 Orange 调色板
# matplotlib Reds的颜色要深一点
print(palette("Reds"))
print(palette("gist_heat"))


# The second way to create an Orange palette is color gradient
def hex_to_RGB(hex):
    ''' "#FFFFFF" -> [255,255,255] '''
    # Pass 16 to the integer function for change of base
    return [int(hex[i:i+2], 16) for i in range(1,6,2)]

def linear_gradient(start_hex, finish_hex="#FFFFFF", n=307):
    ''' returns a gradient list of (n) colors between
        two hex colors. start_hex and finish_hex
        should be the full six-digit color string,
        inlcuding the number sign ("#FFFFFF") '''
    # Starting and ending colors in RGB form
    s = hex_to_RGB(start_hex)
    f = hex_to_RGB(finish_hex)
    # Initilize a list of the output colors with the starting color
    RGB_list = [s]
    # Calcuate a color at each evenly spaced value of t from 1 to n
    for t in range(1, n):
        # Interpolate RGB vector for color at the current value of t
        curr_vector = [int(s[j] + (float(t)/(n-1))*(f[j]-s[j])) for j in range(3)]
        # Add it to our list of output colors
        RGB_list.append(curr_vector)
    return RGB_list

# 从白色到正红色生成256个色阶，颜色要淡一点
end = '#FF0000'; start = '#FFFFFF'
colors1 = linear_gradient(start,end,256)
# 从正红色到暗红色生成256个色阶，暗色段只取一半，避免过暗
end = '#800000'; start = '#FF0000'
colors2 = linear_gradient(start,end,256)
# 合并两个色阶，并从第2行开始，隔行采样，生成Orange调色板256个色阶
colors = colors1+colors2; colors = np.array(colors)
rows = [x*2+1 for x in range(256)]
colors = colors[rows,:]; colors = colors.tolist()
print(colors)
