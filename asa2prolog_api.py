from fastapi import FastAPI, Request, File, UploadFile, Form
from starlette.middleware.cors import CORSMiddleware
from pyswip import Prolog
from converter import AsaToPrologConverter, mySplit, genRandomName
from python_asa.asapy.ASA import ASA
from inputsentences import genpl
import io
import sys


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

asa = ASA()

@app.post('/post/sentencesFile/save')
async def setencesFileSave(file: UploadFile = File(...)):
    path = "./uploads/"+file.filename
    with open(path, "wb+") as file_object:
        file_object.write(file.file.read())
    pl = genpl(path)
    return {"status":path, "result":pl}

@app.get('/')
async def main(query, text):

    print(query, text)

    input_query = query
    input_text = text

    asa_2_prolog_converter = AsaToPrologConverter(asa)
    prolog = Prolog()

    object_query = input_query.split(":")[0]
    a2p = asa_2_prolog_converter.convert(input_text)
    new_file_name = genRandomName(10) + ".pl"

    with open(new_file_name, mode="w") as f:
        f.write("\n".join(a2p) + "\n" + query)

    with io.StringIO() as f:
        sys.stdout = f
        consult = prolog.consult(new_file_name)
        answer = list(prolog.query(object_query))
        sys.stdout = sys.__stdout__

    try:
        datas = mySplit(text, list(answer[0].values()))
        res_data = answer[0]
        res_data["datas"] = datas
        res_data["prolog_tree"] = "\n".join(a2p) + "\n" + query

    except:
        datas = [{'data': text, 'color': "black"}]
        res_data = {'datas': datas}
        res_data["prolog_tree"] = ""

    return res_data
