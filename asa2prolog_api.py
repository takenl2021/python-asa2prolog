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
        sys.stdout = sys.__stdout__
    os.remove("./"+new_file_name)
    return answer
