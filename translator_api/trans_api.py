from bs4 import BeautifulSoup
import re
import ssl
import urllib.request
import urllib.parse
import sys
import os
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
import pandas as pd
from kiwipiepy import Kiwi
import requests
import json
import nltk
from flask import Flask, jsonify


app = Flask(__name__)


@app.route('/translate/<param>')
def translator(param):
    data = pd.read_csv('slang.csv')
    kiwi = Kiwi()
    text: str = param
    text = text.replace('&&123', '?')
    print(text)
    reg = re.compile(r'[a-zA-Z]')

    print()
    if text.upper() != text.lower() and reg.match(text):
        tokens = nltk.word_tokenize(text)
        porter_stemmer = PorterStemmer()
        porter = [porter_stemmer.stem(i) for i in tokens]

        client_id = "mwMbpfnCxxyFJ_CdovDX"
        client_secrect = "sNScXhF7nV"
        url = "https://openapi.naver.com/v1/papago/n2mt"
        headers = {
            'Content-Type': 'application/json',
            'X-Naver-Client-Id': client_id,
            'X-Naver-Client-Secret': client_secrect
        }
        data = {'source': 'en', 'target': 'ko', 'text': text}
        response = requests.post(url, json.dumps(data), headers=headers)
        request = urllib.request.Request(url)

        ko_text = response.json()['message']['result']['translatedText']
        print("파파고번역:", ko_text, end="\n\n")

        list1 = kiwi.tokenize(ko_text)

        for token in list1:
            min_str = 100
            slang = ''

            if ('a' <= token.form[0].lower() <= "z"):
                for c in token.form:
                    if c.isalnum():
                        slang += c
                print("신조어:", slang)
                r = requests.get(
                    "http://www.urbandictionary.com/define.php?term={}".format(slang))
                soup = BeautifulSoup(r.content, "html.parser")

                en_mean = soup.find(
                    'div', attrs={"class": "break-words meaning mb-4"}).text
                print("뜻", end=": ")

                if '"' in en_mean:
                    str_split = re.search('"(.+?)"', en_mean).group(1)
                    print(str_split)
                    text = text.replace(slang, str_split)
                elif "'" in en_mean:
                    str_split = re.search("'(.+?)'", en_mean).group(1)
                    print(str_split)
                    text = text.replace(slang, str_split)
                else:
                    if "." in en_mean:
                        str_list = en_mean.split(".")

                        for i in str_list:
                            if len(i) == 0:
                                str_list.remove(i)

                        min_str = min(str_list, key=len)
                        print(min_str)
                        text = text.replace(slang, min_str)
                    else:
                        print(en_mean)
                        text = text.replace(slang, en_mean)

        print("\n대체한 문장:", text)
        data = {'source': 'en', 'target': 'ko', 'text': text}
        response = requests.post(url, json.dumps(data), headers=headers)
        request = urllib.request.Request(url)

        ko_text = response.json()['message']['result']['translatedText']
        print("출력:", ko_text, end="\n\n")
        return jsonify({"output": ko_text})
    else:
        for i in data['title']:
            kiwi.add_user_word(i.replace(" ", ""), tag='NNG', score=0.0)

        title_list1 = []
        title_list = data['title'].values.tolist()
        for i in title_list:
            i = i.strip()
            title_list1.append(i)

        def extract_noun(text):
            result = kiwi.tokenize(text)
            for token in result:
                if token.tag in ['NNG']:
                    yield token.form

        noun = list(extract_noun(text))

        des_list = []
        des_list1 = []

        des_list = data['description'].values.tolist()
        for i in des_list:
            i = i.strip()
            des_list1.append(i)

        for j in noun:
            if (j in title_list1):
                title_idx = title_list1.index(j)
                word = j
                print("신조어 : " + word)
                print("신조어 뜻 : " + des_list1[title_idx])
                print()
                text = text.replace(j, des_list1[title_idx])
                print("중간 과정 : " + text)

        # 파파고 번역
        def papago(sentence):
            client_id = 'mwMbpfnCxxyFJ_CdovDX'
            client_secrect = 'sNScXhF7nV'

            url = 'https://openapi.naver.com/v1/papago/n2mt'
            headers = {
                'Content-Type': 'application/json',
                'X-Naver-Client-Id': client_id,
                'X-Naver-Client-Secret': client_secrect
            }
            data = {'source': 'ko', 'target': 'en', 'text': sentence}
            response = requests.post(url, json.dumps(data), headers=headers)

            en_text = response.json()['message']['result']['translatedText']
            return en_text

        print()
        print("출력 : " + papago(text))
        return jsonify({"output": papago(text)})


if __name__ == "__main__":
    app.run()
