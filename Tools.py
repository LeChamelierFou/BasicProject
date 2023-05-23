import numpy as np

# The function to add a number of columns inside an array
def adder(Data, times):
    for i in range(1, times + 1):
        new_col = np.zeros((len(Data), 1), dtype=float)
        Data = np.append(Data, new_col, axis=1)

    return Data


# The function to delete a number of columns starting from an index
def deleter(Data, index, times):
    for i in range(1, times + 1):
        Data = np.delete(Data, index, axis=1)

    return Data


# The function to delete a number of rows from the beginning
def jump(Data, jump):
    Data = Data[jump:, ]

    return Data