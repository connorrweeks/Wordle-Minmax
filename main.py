import itertools
import time

word_length = 5

cache = None
use_cache = True
cached_first = {4: 'aero', 5: 'serai', 6: 'radios'}
#cached_first = {}
if (word_length in [4, 5] and use_cache):
    cache = open(f"cache_{word_length}.txt").read().strip().split('\n')
    cache = {
        tuple([int(x2) for x2 in x.split(' ')[0].split(',')]): x.split(' ')[1]
        for x in cache
    }
    #print(cache)
    #exit()

permutations = itertools.product([0, 1, 2], repeat=word_length)
permutations = sorted(permutations, key=lambda x: sum(x))

lang = "english"

if (lang == "english"):
    words = open('scrabble.txt').read().strip().split('\n')
    words = [x for x in words if len(x) == word_length]
    words = words
    print(f"Total Words {len(words)}")
else:
    import urllib.request
    url = "https://raw.githubusercontent.com/lorenbrichter/Words/master/Words/es.txt"
    file = urllib.request.urlopen(url)
    words = file.text.strip().split('\n')
    #import requests
    #response = requests.get(url)
    #data = response.text

print("Welcome the the Wordle solver!")
print("Language =", lang)
print()
print("Enter the results as a string of numbers i.e. '01201' or '2,1,0,0,1'")
print("  '0' for no match")
print("  '1' for right letter, wrong place")
print("  '2' for exact match")
print()


def apply_prev(remaining, prev):
    new_remaining = []
    for w in remaining:
        match = True
        for p_word, result in prev:
            for i in range(word_length):
                if (result[i] == 0):
                    if p_word[i] in w: match = False
                if (result[i] == 1):
                    if p_word[i] not in w or w[i] == p_word[i]: match = False
                if (result[i] == 2):
                    if w[i] != p_word[i]: match = False
        if (match):
            new_remaining.append(w)
    return new_remaining


def try_options(remaining, prev=None):

    if (prev != None):
        remaining = apply_prev(remaining, prev)

    if (word_length in cached_first and cache != None):
        if (len(prev) == 1 and prev[0][0] == cached_first[word_length]):
            if (tuple(prev[0][1]) in cache):
                return cache[tuple(prev[0][1])]

    print(f"\nPossible words left = {len(remaining)}")

    if (len(remaining) == 1):
        return remaining[0]
    elif (len(remaining) < 10):
        print(remaining)

    min_max = len(words)
    best_word = ''
    word_scores = []
    t0 = time.perf_counter()
    for i, w in enumerate(words):
        t1 = time.perf_counter()
        print(
            f"{i+1}/{len(words)} - ETA:{(len(words) - i)*(t1-t0)/(i+1):.2f}   \r",
            end="")
        biggest_path = try_word(remaining, w, alpha=min_max)
        if (min_max > biggest_path):
            best_word = w
            min_max = biggest_path
        word_scores.append(biggest_path)
    print()
    ranked = sorted(zip(words, word_scores), key=lambda x: x[1])
    print(f"Top Choices: {ranked[0:3]}")
    print(f"Min-max: {min_max}")

    #try_word(remaining, best_word, p=True)
    print()
    return best_word


#0 - wrong
#1 - wrong position
#2 - correct position


def try_word(remaining, word, alpha=1000000, p=False):
    results = permutations

    max_size = 0
    if (p): worst_result = (0, 0, 0, 0, 0)
    if (p): new_remaining = []
    if (p): worst_remaining = ['ERROR']
    for result in results:
        remaining_num = 0
        for w in remaining:
            match = True
            for i in range(word_length):
                if (result[i] == 0):
                    if word[i] in w:
                        match = False
                        break
                if (result[i] == 1):
                    if word[i] not in w or w[i] == word[i]:
                        match = False
                        break
                if (result[i] == 2):
                    if w[i] != word[i]:
                        match = False
                        break
            if (match):
                remaining_num += 1
                if (p): new_remaining.append(w)
        if (remaining_num > max_size):
            max_size = remaining_num
            if (p): worst_result = result
            if (p): worst_remaining = new_remaining[:]
            if (max_size > alpha):
                return max_size
    if (p):
        print(f"Worst Result {worst_result}")
        if (len(worst_remaining) < 10): print(worst_remaining)
        print(f"Max size {max_size}")
    return max_size


def make_cache(starter):
    new_cache = {}
    results = list(permutations)

    t0 = time.perf_counter()
    for i, r in enumerate(results):
        remaining = apply_prev(words, [(starter, r)])

        min_max = len(words)
        best_word = ''
        for j, w in enumerate(words):
            biggest_path = try_word(remaining, w, alpha=min_max)

            t1 = time.perf_counter()
            n_rem = (len(words) * (len(results) - i)) + (len(words) - j)
            n_com = j + (i * len(words)) + 1
            print(
                f"{i+1}/{len(results)} - {j+1}/{len(words)} - ETA:{n_rem * (t1-t0) / n_com:.2f}\r   ",
                end="")

            if (min_max > biggest_path):
                best_word = w
                min_max = biggest_path
        new_cache[r] = (best_word, min_max)

    f = open(f'cache_{word_length}.txt', 'w+')
    for k in new_cache:
        f.write(
            f"{','.join([str(x) for x in k])} {new_cache[k][0]} {new_cache[k][1]}\n"
        )


def main():
    prev = []
    while (True):
        #Get suggestion
        if (len(prev) == 0):
            if (word_length in cached_first):
                best = cached_first[word_length]
                print(f"Recommended Strategy = '{best}'")
            else:
                best = try_options(words, prev)
                print(f"Recommended Strategy = '{best}'")
        else:
            #t_0 = time.perf_counter()
            best = try_options(words, prev)
            #t_1 = time.perf_counter()
            #print(f"{t_1 - t_0:.2f}")
            print(f"Recommended Strategy = '{best}'")

        #Request results
        exit_flag = True
        while (True):
            in_str = input("Enter Word Used: ").strip().lower()
            if (in_str.lower() == 'exit'): break
            last_word = in_str
            if (len(in_str) == 0):
                last_word = best
                print(f"Using '{best}'")

            if (len(last_word)) != word_length:
                print("Incorrect Formatting!!")
                continue

            in_str = input("Enter Results: ").strip()
            if (in_str.lower() in ['exit', 'q']): break
            if (len(in_str) == word_length):
                last_result = [x for x in in_str]
            elif (len(in_str) == (word_length * 2) - 1):
                sep = in_str[1]
                last_result = in_str.split(sep)
            else:
                print("Incorrect Formatting!")
                continue
            exit_flag = False
            break

        if (exit_flag):
            print("Exiting Program")
            break
        #Process results
        prev.append([last_word, [int(x) for x in last_result]])


main()
#from array_based import create_word_array, create_result_array
#import
#make_cache('radios')
#create_word_array(word_length, words)
#create_result_array(None, word_length)
