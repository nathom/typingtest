from requests import get
import threading
from random import choice
import json
from time import sleep, time
from datetime import datetime
from os import system
from pynput.keyboard import Key, Listener
from sys import argv
import csv

HIDE_CURSOR = '\x1b[?25l'
SHOW_CURSOR = '\x1b[?25h'

WORDS_PER_SET = 10
if len(argv) > 1:
    TEST_LEN = int(argv[1])
else:
    TEST_LEN = 60

f = open('/users/nathan/general/fingers.txt', 'r').read()
words = f.split('|')
curr_words = [choice(words) for _ in range(WORDS_PER_SET)]
word_buffer = [choice(words) for _ in range(WORDS_PER_SET)]
cumulative_keylist = []
cumulative_words = ''
keylist = []

capital = False
t1 = 10**10
first = True

print(HIDE_CURSOR)
system('clear')
print(' '.join(curr_words))
print(' '.join(word_buffer))

def check_correct():
    global curr_words
    global words
    global WORDS_PER_SET
    global keylist
    global word_buffer
    global cumulative_words

    if keylist == [' ']:
        keylist.pop()

    system('clear')

    word_str = ' '.join(curr_words)
    for i in range(len(keylist)):
        if keylist[i] == word_str[i]:
            print(colorize(word_str[i], 1), end='')
        elif word_str[i] == ' ':
            print(colorize('▉', 0), end='')
        else:
            print(colorize(word_str[i], 0), end='')
    print(word_str[len(keylist):])
    print(' '.join(word_buffer))

    if len(keylist) == len(word_str):
        cumulative_keylist.extend(keylist)
        cumulative_keylist.append(' ')
        cumulative_words += ' ' + word_str
        keylist = []
        curr_words = word_buffer
        word_buffer = [choice(words) for _ in range(WORDS_PER_SET)]

def on_press(key):
    global capital
    global curr_word
    global keylist
    global first
    global t1
    if len(str(key)) != 3:
        if first:
            t1 = time()
            first = False

        if key == Key.esc or key == Key.enter:
            k = ''
        elif key == Key.space:
            k = ' '
        elif key == Key.shift:
            capital = True
            k = ''
        elif key == Key.backspace and len(keylist) > 0:
            keylist.pop()
            k = ''
        else:
            k = ''
    else:
        k = (not capital) * str(key)[1:-1] + capital * str(key)[1:-1].upper()
        capital = False

    if k != '':
        keylist.append(k)

    check_correct()

def on_release(key):
    global t1
    global keylist
    global cumulative_keylist
    global cumulative_words
    global TEST_LEN

    t2 = time()
    if t2 - t1 > TEST_LEN:
        # Stop listener
        cumulative_keylist.extend(keylist)
        cumulative_words += ' ' + ' '.join(curr_words)[:len(keylist) + 1]

        num_words = len(cumulative_words.split(' '))
        wpm = 60 * num_words/TEST_LEN
        test = ''.join(cumulative_keylist)
        score = get_score(test, cumulative_words[1:])
        accuracy = round(score/(len(cumulative_words)), 2)
        char_per_min = round(60 * len(test)/(t2 - t1), 2)
        stand_wpm = round(char_per_min / 5 )

        with open('/users/nathan/general/typing_speed.csv', 'a') as sheet:
            t = datetime.now()
            date = t.strftime('%Y%m%d%H%M%S')
            writer = csv.writer(sheet)
            writer.writerow([date, stand_wpm, wpm, accuracy, char_per_min, TEST_LEN])

        print(SHOW_CURSOR)
        print(f'\nStandardized WPM: {boldify(stand_wpm)}\nWPM: {boldify(round(wpm, 2))}\nAccuracy: {boldify(100 * round(accuracy, 2))}%\nAdjusted WPM: {boldify(round(60 * (score)/(t2 - t1), 2))}\nCharacters per minute: {boldify(char_per_min)}')
        return False

    if key == Key.esc:
        print(SHOW_CURSOR)
        return False

    if key == Key.cmd:
        print(SHOW_CURSOR)
        print(keylist)
        return False



def colorize(text, color):
    if color != '':
        COLOR = {
        "GREEN": "\033[92m",
        "RED": "\033[91m",
        "ENDC": "\033[0m",
        }
        return color * COLOR['GREEN'] + (1 - color) * COLOR['RED'] + text + COLOR['ENDC']
    else:
        return text



def get_score(i, word_string):
    test_split = list(i)
    word_split = list(word_string)
    score = 0
    for i in range(len(test_split)):
        if test_split[i] == word_split[i]:
            score += 1
        else:
            pass
    return score

def boldify(s):
    s = str(s)
    return f"\033[1m{s}\033[0m"


# Collect events until released
with Listener(
        on_press=on_press,
        on_release=on_release) as listener:
    listener.join()


