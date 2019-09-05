import csv
import numpy as np
# import panda as pd
import time

bg_data_list = []

with open("grid_eye/background_data.csv", "r") as readfile:
    bg_data = csv.reader(readfile)
    # print(bg_data)
    for row in bg_data:
        # print(row[1])
        bg_data_list.append(row[1])

# for row in bg_data_list:
#     print(row)

frames = []

for bg_frame in bg_data_list:
    frame = []
    for pixel in bg_frame:
        decoded_pixel = ord(pixel)
        frame.append(decoded_pixel)
    frame = np.array(frame)
    frame = frame.reshape(8, 8)
    frames.append(frame.T.tolist())

def list_sum(test_list):
    sum = 0
    for rows in range(len(test_list)):
        # print(len(test_list[rows]))
        for cols in range(len(test_list[rows])):
            sum = sum + test_list[rows][cols]

    return sum

# Sum of first element of all frames
def sum_element():
    sum = 0
    # print(frames[0][0][0])

    rows = 8
    cols = 8
    index = 0
    sum_list = []
    sum_array = np.zeros([8,8])

    for row in range(0, rows):
        for col in range(0, cols):
            for frame in frames:
                sum += frame[row][col]
            sum_array[row][col] = sum
            sum = 0
    sum_array =  sum_array / len(frames)
    print(np.around(sum_array, 2))

sum_element()
# print("Frame is ",frames[0], " \nand sum is ", list_sum(frames[0]))