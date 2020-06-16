import subprocess,re
from time import sleep
import os,sys,io
from asapy.ASA import ASA

def mystrip(str):
    return str.strip()

class Analyze_sentence():
    def __init__(self,input_string):
        self.input_string = input_string

    def analyze(self) -> str:
        # abspath = os.path.abspath(__file__).rstrip("ASA_assembler.py") + "main.py"
        # command = ["python", abspath]
        # devnull = open('/dev/null', 'w')
        # python_asa = subprocess.Popen(command,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=devnull)
        # analyzed_result = python_asa.communicate(self.input_string.encode())[0].decode()
        # return analyzed_result
        with io.StringIO() as f:
            sys.stdout = f
            asa = ASA()
            asa.parse(self.input_string)
            asa.selectOutput()
            result = f.getvalue()
            sys.stdout = sys.__stdout__
        return result

class Get_element():
    def __init__(self,shaped_result):
        self.shaped_result = shaped_result

    def get_dictionary(self) -> dict:
        sentence = re.split("ID: \d ", self.shaped_result)[0].split("sentence: ")[1].strip()
        IDlist = re.split("ID: \d ", self.shaped_result)[1:]
        result_dict = {}
        result_dict["sentence"] = sentence
        for i in range(len(IDlist)):
            semantic_dict = {}
            phrase = IDlist[i].split("\n\t\t")[0].split("\n\t")[0]
            semantics = IDlist[i].split("\n\t\t")[0].split("\n\t")[1:]
            semantic_key = [semantics[sc].split(": ")[0] for sc in range(len(semantics))]
            semantic_value = [semantics[sc].split(": ")[1] for sc in range(len(semantics))]
            morphemes = IDlist[i].split("\n\t\t")[1:]
            semantic_dict = {key:value for (key,value) in zip(semantic_key,semantic_value)}
            semantic_dict["phrase"] = phrase
            semantic_dict["morphemes"] = [list(map(mystrip,re.split('\t+|,',morphemes[mc]))) for mc in range(len(morphemes))]
            result_dict["ID{}".format(str(i))] = semantic_dict
        return result_dict