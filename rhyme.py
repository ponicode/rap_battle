import random
import re
import operator
import functools
from nltk.corpus import cmudict

e = cmudict.entries()
d = cmudict.dict()

def make_word_list(tokenized_text):
    word_list = []
    for i in tokenized_text:
        try:
            d[i.lower()]
        except KeyError:
            pass
        else:
            if i.lower() == "'s":
                pass
            elif i[-1] == ".":
                pass
            else:
                word_list.append((i.lower(), d[i.lower()][0]))
    return word_list

def unique(s):
    u = []
    for x in s:
        if x not in u:
            u.append(x)
        else:
            pass
    return u

def meter(word):
    pron = d[word]
    m1 = []
    m2 = []
    mx = []
    if len(pron) == 1:
        for i in pron[0]:
            if '0' in i:
                m1.append(0)
            elif '1' in i:
                m1.append(1)
            elif '2' in i:
                m1.append(2)
            else:
                pass
        mx = [m1]
    elif len(pron) >= 2:
        for i in pron[0]:
            if '0' in i:
                m1.append(0)
            elif '1' in i:
                m1.append(1)
            elif '2' in i:
                m1.append(2)
            else:
                pass
        for i in pron[1]:
            if '0' in i:
                m2.append(0)
            elif '1' in i:
                m2.append(1)
            elif '2' in i:
                m2.append(2)
            else:
                pass
        mx = [m1, m2]
    m = []
    if len(mx) == 1:
        w0 = functools.reduce(operator.mul, mx[0], 1)
        if w0 >= 2:
            for i in mx[0]:
                if i == 1:
                    m.append('u')
                elif i == 2:
                    m.append('s')
        elif w0 == 1:
            for i in mx[0]:
                m.append('s')
        elif w0 == 0:
            for i in mx[0]:
                if i == 0:
                    m.append('u')
                elif i == 1 or i == 2:
                    m.append('s')
    elif len(mx) == 2:
        w0 = functools.reduce(operator.mul, mx[0], 1)
        w1 = functools.reduce(operator.mul, mx[1], 1)
        if w0 >= 2 and w1 >= 2:
            for (i, j) in zip(mx[0], mx[1]):
                if i * j == 1:
                    m.append('u')
                elif i * j == 4:
                    m.append('s')
                elif i * j == 2:
                    m.append('x')
        elif w0 == 1 and w1 == 1:
            for (i, j) in zip(mx[0], mx[1]):
                m.append('s')
       	elif w0 == 0 and w1 == 0:
            for (i, j) in zip(mx[0], mx[1]):
                if i == j and i * j >= 1:
                    m.append('s')
                elif i != j and i * j == 0:
                    m.append('x')
                elif i == j and i * j == 0:
                    m.append('u')
        elif w0 >= 2 and w1 == 0:
            for (i, j) in zip(mx[0], mx[1]):
                if i == 1 and j == 0:
                    m.append('u')
                elif i == 2 and j == 0:
                    m.append('x')
                elif i == 1 and j == 1:
                    m.append('x')
                elif i == 1 and j == 2:
                    m.append('x')
                elif i == 2 and j == 1:
                    m.append('s')
                elif i == 2 and j == 2:
                    m.append('s')
        elif w0 == 0 and w1 >= 2:
            for (i, j) in zip(mx[0], mx[1]):
                if i == 0 and j == 1:
                    m.append('u')
                elif i == 0 and j == 2:
                    m.append('x')
                elif i == 1 and j == 1:
                    m.append('x')
                elif i == 2 and j == 1:
                    m.append('x')
                elif i == 1 and j == 2:
                    m.append('s')
                elif i == 2 and j == 2:
                    m.append('s')
        elif w0 == 1 and w1 >= 2:
            for (i, j) in zip(mx[0], mx[1]):
                if j == 1:
                    m.append('x')
                elif j == 2:
                    m.append('s')
        elif w0 >= 2 and w1 == 1:
            for (i, j) in zip(mx[0], mx[1]):
                if i == 1:
                    m.append('x')
                elif i == 2:
                    m.append('s')
        elif w0 == 1 and w1 == 0:
            for (i, j) in zip(mx[0], mx[1]):
                if j == 0:
                    m.append('x')
                elif j == 1:
                    m.append('s')
                elif j == 2:
                    m.append('s')
        elif w0 == 0 and w1 == 1:
            for (i, j) in zip(mx[0], mx[1]):
                if i == 0:
                    m.append('x')
                if i == 1:
                    m.append('s')
                if i == 2:
                    m.append('s')
    return m

def strip_numbers(x):
    xj = '.'.join(x)
    xl = re.split('0|1|2', xj)
    xjx = ''.join(xl)
    xlx = xjx.split('.')
    return xlx

def last_stressed_vowel(word):
    if len(d[word]) <= 1:
        pron = d[word][0]
    else:
        p0 = d[word][0]
        p1 = d[word][1]
        sj0 = ''.join(p0)
        sl0 = re.split('0|1|2', sj0)
        sj1 = ''.join(p1)
        sl1 = re.split('0|1|2', sj1)
        if len(sl1) < len(sl0):
            pron = p1
        else:
            pron = p0
    mtr = meter(word)
    vowel_index = []
    if len(mtr) == 1:
        lsv = -1
    elif mtr[-1] == 's' or mtr[-1] == 'x':
        lsv = -1
    elif mtr[-2] == 's' or mtr[-3] == 'x':
        lsv = -2
    elif mtr[-3] == 's' or mtr[-3] == 'x':
        lsv = -3
    elif mtr[-4] == 's' or mtr[-4] == 'x':
        lsv = -4
    elif mtr[-5] == 's' or mtr[-5] == 'x':
        lsv = -5
    elif mtr[-6] == 's' or mtr[-6] == 'x':
        lsv = -6
    elif mtr[-7] == 's' or mtr[-7] == 'x':
        lsv = -7
    elif mtr[-8] == 's' or mtr[-8] == 'x':
        lsv = -8
    elif mtr[-9] == 's' or mtr[-9] == 'x':
        lsv = -9
    elif mtr[-10] == 's' or mtr[-10] == 'x':
        lsv = -10
    else:
        lsv = -1
    for i in pron:
        if '0' in i or '1' in i or '2' in i:
            vowel_index.append(pron.index(i))
        else:
            continue
    return vowel_index[lsv]

def rhyme_finder(word, tokenized_text):
    word_list = make_word_list(tokenized_text)
    word_list_u = unique(word_list)
    rhyming_words = []
    if len(d[word]) <= 1:
        pron = d[word][0]
    else:
        p0 = d[word][0]
        p1 = d[word][1]
        sj0 = ''.join(p0)
        sl0 = re.split('0|1|2', sj0)
        sj1 = ''.join(p1)
        sl1 = re.split('0|1|2', sj1)
        if len(sl1) < len(sl0):
            pron = p1
        else:
            pron = p0
    pron = strip_numbers(pron)
    lsv = last_stressed_vowel(word)
    rhyme_part = pron[lsv:]
    lrp = len(rhyme_part) * -1
    for (x, y) in word_list_u:
        ps = strip_numbers(y)
        if ps[lrp:] == rhyme_part and ps[lrp-1:] != pron[lsv-1:]:
            rhyming_words.append(x)
        else:
            pass
    rw = [i for i in rhyming_words if not i == word]
    return rw


