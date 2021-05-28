import os
import sys
import io
import re


def mystrip(str):
    return str.strip()


def write_sentence(sentence):
    return "sentence(" + sentence + ")."


def write_semantic(semantic):
    return "semantic(" + semantic + ")."


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
        sentence = re.split("ID: \d ", analyze_result)[
            0].split("sentence: ")[1].strip()
        IDlist = re.split("ID: \d ", analyze_result)[1:]
        result_dict = {}
        result_dict["sentence"] = sentence
        for i in range(len(IDlist)):
            semantic_dict = {}
            phrase = IDlist[i].split("\n\t\t")[0].split("\n\t")[0]
            semantics = IDlist[i].split("\n\t\t")[0].split("\n\t")[1:]
            semantic_key = [semantics[sc].split(
                ": ")[0] for sc in range(len(semantics))]
            semantic_value = [semantics[sc].split(
                ": ")[1] for sc in range(len(semantics))]
            morphemes = IDlist[i].split("\n\t\t")[1:]
            semantic_dict = {key: value for (key, value) in zip(
                semantic_key, semantic_value)}
            semantic_dict["phrase"] = phrase
            semantic_dict["morphemes"] = [list(map(mystrip, re.split(
                '\t+|,', morphemes[mc]))) for mc in range(len(morphemes))]
            result_dict["ID{}".format(str(i))] = semantic_dict
        return result_dict

    def convert(self, input_string):
        analyze_result = self.analyze(input_string)
        dc = self.get_dictionary(analyze_result)
        buf = []
        ids = []
        buf.append(write_sentence(dc["sentence"]))

        for idcount in range(len(dc)-1):
            ids.append(dc["ID{}".format(str(idcount))])

        for i in range(len(ids)):
            buf.append(write_type(ids[i]["phrase"], ids[i]["type"]))
            if "semantic" in ids[i]:
                for sems in ids[i]["semantic"].split("-"):
                    buf.append(write_semantic(sems.replace("・", "or")))

            if "semrole" in ids[i]:
                buf.append(write_role(
                    ids[i]["phrase"], ids[i]["semrole"].split("（")[0]))

            for ii in range(2):
                if ii == 0 and ("main" in ids[i]):
                    buf.append(write_main(ids[i]["phrase"], ids[i]["main"]))
                    for iii in range(len(ids[i]["morphemes"])):
                        if ids[i]["morphemes"][iii][3] in ids[i]["main"]:
                            buf.append(write_class(
                                ids[i]["main"], ids[i]["morphemes"][iii][4]))

                if ii == 1 and ("part" in ids[i]):
                    buf.append(write_part(ids[i]["phrase"], ids[i]["part"]))
                    for iii in range(len(ids[i]["morphemes"])):
                        if ids[i]["morphemes"][iii][3] in ids[i]["part"]:
                            buf.append(write_class(
                                ids[i]["part"], ids[i]["morphemes"][iii][4]))

        return buf
