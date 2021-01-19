from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pyswip import Prolog
from converter import AsaToPrologConverter
from asapy.ASA import ASA
from time import sleep, time
import os
import io
import sys
import re
import random
import string


def randomname(n):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=n))


def my_split(str_, split_list):
    re_splits = []
    for spl in split_list:
        re_splits.append("({})".format(spl))
    presult = re.split("|".join(re_splits), str_)  # 区切り文字を含めたリストができる。
    result = [pr for pr in presult if pr != None and pr != '']  # None と 空文字を削除
    res_arr = [{'data': r, 'color': "red"} if r in split_list else {
        'data': r, 'color': "black"} for r in result]
    return res_arr


app = FastAPI()

origins = [
    "http://localhost:3000",
    "localhost",
    "http://localhost"
    # "https://demo-sip7map.datacradle.jp/tile/styles/basic/*.png"

]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

asa = ASA()


@app.get('/')
async def main(query, text):
    print(query, text)
    query = query
    a2p_converter = AsaToPrologConverter(asa)
    prolog = Prolog()
    inp = text
    queryy = query.split(":")[0]
    a2p = a2p_converter.convert(inp)
    new_file_name = randomname(10) + ".pl"
    with open(new_file_name, mode="w") as f:
        f.write("\n".join(a2p) + "\n" + query)
    with io.StringIO() as f:
        sys.stdout = f
        consult = prolog.consult(new_file_name)
        answer = list(prolog.query(queryy))
        answer[0]["prolog_tree"] = "\n".join(a2p) + "\n" + query
        sys.stdout = sys.__stdout__
    datas = my_split(text, list(answer[0].values()))
    answer[0]["datas"] = datas
    os.remove("./"+new_file_name)
    return answer[0]
