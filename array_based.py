import itertools
import numpy as np

def create_word_array(word_length, word_list):
  print(word_list[0])

  word_arr = np.zeros((len(word_list), word_length * 26))
  print(word_arr.shape)
  for i, w in enumerate(word_list):
    for j, letter in enumerate(w):
      ind = ord(letter) - 97
      word_arr[i][ind + j*26] = 1

def create_result_array(word_vec, word_length):
  permutations = itertools.product([0,1,2], repeat=word_length)
  permutations = sorted(permutations, key=lambda x: sum(x))

  result_arr = np.zeros((word_length * 26, 3 ** word_length))

  print(result_arr.shape)

  WL * 26, 3^WL = 