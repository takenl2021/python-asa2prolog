import sys
import io
import re
import random
import string

def mySplit(str_, split_list):
    re_splits = []
    for spl in split_list:
        re_splits.append("({})".format(spl))
    presult = re.split("|".join(re_splits), str_)  # 区切り文字を含めたリストができる。
    result = [pr for pr in presult if pr != None and pr != '']  # None と 空文字を削除
    
    res_arr = [{'data': r, 'color': "red"} 
    if r in split_list 
    else {'data': r, 'color': "black"} 
    for r in result]

    return res_arr

def genRandomName(n):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=n))

def mystrip(str):
    return str.strip()


def write_sentence(sentence):
    return "sentence(" + sentence + ")."


def write_semantic(semantic):
    return "semantic(" + semantic.replace("・", "or").replace("（","_").replace("）","_").replace("／","/") + ")."


def write_phrase(phrase):
    return "phrase(" + phrase + ")."


def write_main(phrase, main):
    return "main(" + phrase + "," + main + ")."


def write_part(phrase, part):
    return "part(" + phrase + "," + part + ")."


def write_role(phrase, role):
    return "role(" + phrase + "," + role + ")."


def write_morpheme(word, morpheme):
    return "morpheme(" + word + "," + morpheme + ")."


def write_type(phrase, type_):
    return "type(" + phrase + "," + type_ + ")."


def write_class(word, class_):
    return "class(" + word + "," + class_ + ")."

# コンストラクタ引数: ASAのインスタンス
# フロー:
# 1) analyze(input_string)でテキストに対するASA意味役割解析
# 2) get_dictionary(analyze_result)で解析結果をpython連想配列形式に
# 3) convert(input_string)で連想配列をProlog形式stringに
# 戻り値: Prolog形式string


class AsaToPrologConverter():
    def __init__(self, asa_instance):
        self.asa_instance = asa_instance

    def analyze(self, input_string):
        with io.StringIO() as f:
            sys.stdout = f
            self.asa_instance.parse(input_string)
            self.asa_instance.selectOutput()
            result = f.getvalue()
            sys.stdout = sys.__stdout__
        return result

    def get_dictionary(self, analyze_result):
        sentence = re.split("ID: \d ", analyze_result)[0].split("sentence: ")[1].strip()
        IDlist = re.split("ID: \d ", analyze_result)[1:]
        result_dict = {}
        result_dict["sentence"] = sentence
        for i in range(len(IDlist)):
            semantic_dict = {}
            phrase = IDlist[i].split("\n\t\t")[0].split("\n\t")[0]
            semantics = IDlist[i].split("\n\t\t")[0].split("\n\t")[1:]
            semantic_key = [semantics[sc].split(": ")[0] for sc in range(len(semantics))]
            semantic_value = [semantics[sc].split(": ")[1] for sc in range(len(semantics))]
            morphemes = IDlist[i].split("\n\t\t")[1:]
            semantic_dict = {key: value for (key, value) in zip(semantic_key, semantic_value)}
            semantic_dict["phrase"] = phrase
            semantic_dict["morphemes"] = [list(map(mystrip, re.split('\t+|,', morphemes[mc]))) for mc in range(len(morphemes))]
            result_dict["ID{}".format(str(i))] = semantic_dict
        return result_dict

    def convert(self, input_string):
        analyze_result = self.analyze(input_string)
        dictionary = self.get_dictionary(analyze_result)
        buf = []
        ids = []

        buf.append(write_sentence(dictionary["sentence"]))

        for idcount in range(len(dictionary)-1):
            ids.append(dictionary["ID{}".format(str(idcount))])


        for id in range(len(ids)):
            buf.append(write_type(ids[id]["phrase"], ids[id]["type"]))
            if "semantic" in ids[id]:
                for sems in ids[id]["semantic"].split("-"):
                    if len(sems) > 0:
                        buf.append(write_semantic(sems))

            if "semrole" in ids[id]:
                buf.append(write_role(ids[id]["phrase"], ids[id]["semrole"].split("（")[0]))

            for separate in ["main","part"]:
                if separate == "main" and ("main" in ids[id]):
                    buf.append(write_main(ids[id]["phrase"], ids[id]["main"]))
                    for morpheme in ids[id]["morphemes"]:
                        if morpheme[3] in ids[id]["main"]:
                            buf.append(write_class(morpheme[3], morpheme[4]))

                if separate == "part" and ("part" in ids[id]):
                    buf.append(write_part(ids[id]["phrase"], ids[id]["part"]))
                    for morpheme in ids[id]["morphemes"]:
                        if morpheme[3] in ids[id]["part"]:
                            buf.append(write_class(morpheme[3], morpheme[4]))

        return buf