import io
import sys
import re
from python_asa.asapy.ASA import ASA
from prologpy import Solver

asa = ASA()


def gen_pred(pred_name, params):
    """
    Prolog述語を生成する。

    Params
    ------
    pred_name : str
        述語名
    params : any[]
        述語引数のリスト。
        *params: tuple としないのは単純に可読性の好み。

    Returns
    -------
    pred : str
        Prolog述語。
    """

    # str型にmapしてからjoin
    pred = f'{pred_name}({",".join(list(map(str, params)))}).'
    return pred


class Converter():
    def __init__(self, asa_instance):
        self.__sentences = None
        try:
            if(isinstance(asa_instance, ASA)):
                self.__asa_instance = asa_instance
            else:
                raise ValueError("Invalid ASA instance.")
        except ValueError as e:
            print(e)
            sys.exit()

    def set_sentences(self, sentences):
        self.__sentences = re.split(
            '[\.\!\?\。\！\？\「\」\．]', sentences.replace('\n', ''))

    def load_sentences(self, file_path):
        try:
            with open(file_path, "r") as f:
                raw_text = f.read()
            self.set_sentences(raw_text)
        except:
            print(
                f"\033[31mResolve Error\033[0m: Couldn't resolve '{file_path}' in load_sentences().")

    def get_sentences(self):
        return self.__sentences

    def get_sentence_info(self, sentence):
        self.__asa_instance.parse(sentence)
        with io.StringIO() as f:
            sys.stdout = f
            self.__asa_instance.selectOutput()
            asa_output = f.getvalue()
            sys.stdout = sys.__stdout__
        asa_json = json = self.__asa_instance.dumpJson()
        return {
            'surface': sentence,
            'asa_output': asa_output,
            'asa_json': asa_json
        }

    def convert(self, sentence, sentence_id):
        sentence_info = self.get_sentence_info(sentence)
        json = sentence_info["asa_json"]
        pred_list = []

        # ①ノード番号を0として一文全体のsurface述語生成
        pred_list.append(
            gen_pred("surf", [sentence_id, 0, json["surface"]]))

        # var: ノード番号1~len(json["chunks"])まで、深さ1(chunkレベル)のid
        node_id_depth1 = 1

        # var: ノード番号len(json["chunks"]) + 1 ~、深さ2(main, partレベル)のid
        node_id_depth2 = len(json["chunks"]) + 1

        # var: ノード番号3 * len(json["chunks"]) + 1 ~、深さ3(morphレベル)のid
        # node_id_depth3 = 3 * len(json["chunks"]) + 1
        node_id_depth3 = 0

        chunk_sloc_start = 0
        morph_sloc_start = 0
        for chunk in json["chunks"]:
            # ②ノード番号0(文ノード)から派生するchunk述語、surface述語生成
            pred_list.append(
                gen_pred("chunk", [sentence_id, 0, node_id_depth1])
            )
            pred_list.append(
                gen_pred("surf", [sentence_id,
                         node_id_depth1, chunk["surface"]])
            )
            pred_list.append(gen_pred("sloc", [sentence_id, node_id_depth1,
                             f"{chunk_sloc_start}_{chunk_sloc_start + len(chunk['surface'])-1}"]))
            chunk_sloc_start += len(chunk["surface"])
            # ③各chunkのroleもしくはsemantic述語生成
            if 'semrole' in chunk:
                for role in chunk['semrole'].split("|"):
                    if role != "":
                        pred_list.append(
                            gen_pred("role", [sentence_id, node_id_depth1, role]))
            elif 'semantic' in chunk:
                # semanticは複数分類が「-」で連結されている場合があるため分割
                for semantic in chunk['semantic'].split("-"):
                    if semantic != "":
                        pred_list.append(
                            gen_pred("semantic", [sentence_id, node_id_depth1, semantic]))

            if 'modified' in chunk:
                for dep in chunk["modified"]:
                    pred_list.append(
                        gen_pred("dep", [sentence_id, node_id_depth1, dep+1]))

            node_type = str(chunk.get('type'))  # main/partのタイプ
            for node_depth3_pred_name in ["main", "part"]:
                node_surface = str(
                    chunk.get(node_depth3_pred_name))  # main/partの表層
                if node_surface == "" or node_surface == 'None':  # 表層が空もしくはNoneの場合スキップ
                    continue
                if node_type == 'verb':  # 動詞の場合は形態素のsurfaceをmain/partのsurfaceに
                    for morph in chunk["morphs"]:
                        if morph["base"] == node_surface:
                            pred_list.append(gen_pred(node_depth3_pred_name,
                                                      [sentence_id, node_id_depth1, node_id_depth2]))
                            pred_list.append(gen_pred("surf",
                                                      [sentence_id, node_id_depth2, morph["surface"]]))
                elif node_type == 'adjective':
                    node_adjective_surface = ""
                    for idx, morph in enumerate(chunk["morphs"]):
                        if node_depth3_pred_name == "main" and idx == 0:
                            node_adjective_surface += morph["surface"]
                        elif node_depth3_pred_name == "part" and idx > 0:
                            node_adjective_surface += morph["surface"]
                    pred_list.append(gen_pred(node_depth3_pred_name, [
                                     sentence_id, node_id_depth1, node_id_depth2]))
                    pred_list.append(
                        gen_pred("surf", [sentence_id, node_id_depth2, node_adjective_surface]))
                    for morph in chunk["morphs"]:
                        if morph["surface"] in node_adjective_surface:
                            pred_list.append(
                                gen_pred("morph", [sentence_id, node_id_depth2, f"m{node_id_depth3}"]))
                            pred_list.append(
                                gen_pred("surf", [sentence_id, f"m{node_id_depth3}", morph["surface"]]))
                            pred_list.append(
                                gen_pred("surfBF", [sentence_id, f"m{node_id_depth3}", morph["base"]]))
                            pred_list.append(gen_pred("sloc", [
                                sentence_id, f"m{node_id_depth3}", f"{morph_sloc_start}_{morph_sloc_start + len(morph['surface'])-1}"]))
                            morph_sloc_start += len(morph["surface"])
                            for pos in morph["pos"].split(","):
                                pred_list.append(
                                    gen_pred("pos", [sentence_id, f"m{node_id_depth3}", pos]))
                            node_id_depth3 += 1
                else:  # それ以外はそのまま
                    pred_list.append(gen_pred(node_depth3_pred_name, [
                                     sentence_id, node_id_depth1, node_id_depth2]))
                    pred_list.append(
                        gen_pred("surf", [sentence_id, node_id_depth2, node_surface]))

                if(node_type != "adjective"):
                    for morph in chunk["morphs"]:
                        if morph["base"] in node_surface:
                            pred_list.append(
                                gen_pred("morph", [sentence_id, node_id_depth2, f"m{node_id_depth3}"]))
                            pred_list.append(
                                gen_pred("surf", [sentence_id, f"m{node_id_depth3}", morph["surface"]]))
                            pred_list.append(
                                gen_pred("surfBF", [sentence_id, f"m{node_id_depth3}", morph["base"]]))
                            pred_list.append(gen_pred("sloc", [
                                sentence_id, f"m{node_id_depth3}", f"{morph_sloc_start}_{morph_sloc_start + len(morph['surface'])-1}"]))
                            morph_sloc_start += len(morph["surface"])
                            for pos in morph["pos"].split(","):
                                pred_list.append(
                                    gen_pred("pos", [sentence_id, f"m{node_id_depth3}", pos]))
                            node_id_depth3 += 1
                node_id_depth2 += 1
            for morph in chunk["morphs"]:
                # 一度のみのはず
                if (morph["base"] not in str(chunk.get("main"))) and (morph["base"] not in str(chunk.get("part"))):
                    pred_list.append(
                        gen_pred("else", [sentence_id, node_id_depth1, node_id_depth2]))
                    pred_list.append(
                        gen_pred("surf", [sentence_id, node_id_depth2, morph["surface"]]))
                    pred_list.append(
                        gen_pred("morph", [sentence_id, node_id_depth2, f"m{node_id_depth3}"]))
                    pred_list.append(
                        gen_pred("surf", [sentence_id, f"m{node_id_depth3}", morph["surface"]]))
                    pred_list.append(
                        gen_pred("surfBF", [sentence_id, f"m{node_id_depth3}", morph["base"]]))
                    pred_list.append(gen_pred("sloc", [
                                     sentence_id, f"m{node_id_depth3}", f"{morph_sloc_start}_{morph_sloc_start + len(morph['surface'])-1}"]))
                    morph_sloc_start += len(morph["surface"])
                    for pos in morph["pos"].split(","):
                        pred_list.append(
                            gen_pred("pos", [sentence_id, f"m{node_id_depth3}", pos]))
                    node_id_depth3 += 1
                    node_id_depth2 += 1
            node_id_depth1 += 1
        self.__pred_list = pred_list
        return pred_list

    def convert_all(self):
        if(self.__sentences == None):
            print(
                f"\033[31mConvert Error\033[0m: Make sure to set some sentences before conversion.")
        else:
            sentence_id = 0
            pred_list = []
            for sentence in self.__sentences:
                if sentence == "":
                    continue
                pred_list.extend(self.convert(sentence, sentence_id))
                sentence_id += 1
            return pred_list


if __name__ == "__main__":
    converter = Converter(asa)
    converter.set_sentences("彼は本を買って、彼女はあの有名だった本を売った")
    # converter.load_sentences("./example/test.txt")

    pred_txt = "\n".join(converter.convert_all())
    # ①名詞の表層と元の文を抽出するルール
    # rule_txt = "名詞(_元の文,_名詞の表層):- pos(SENTENCE_ID,NODE_ID,名詞),surf(SENTENCE_ID,NODE_ID,_名詞の表層),surf(SENTENCE_ID,0,_元の文)."
    # query = "名詞(X,Y)"

    # ②チャンクの表層を抽出するルール
    # rule_txt = "文節(_文節の表層):- chunk(SENTENCE_ID,0,CHUNK_ID),surf(SENTENCE_ID,CHUNK_ID,_文節の表層)."
    # query = "文節(X)"

    # ③動作主文節のmainのmorphのslocを抽出するルール
    # rule_txt = "動作主形態素sloc(_表層,_sloc):-chunk(SENTENCE_ID,0,CHUNK_ID),role(SENTENCE_ID,CHUNK_ID,動作主),main(SENTENCE_ID,CHUNK_ID,MAIN_ID),morph(SENTENCE_ID,MAIN_ID,MORPH_ID),surf(SENTENCE_ID,MORPH_ID,_表層),sloc(SENTENCE_ID,MORPH_ID,_sloc)."
    # query = "動作主形態素sloc(X,Y)"

    # ④売るの「を」格を抽出するルール
    rule_txt = "売るのを格sloc(_surf,_sloc):-surfBF(SENTENCE_ID,MORPH_ID,売る),morph(SENTENCE_ID,PARENT_ID,MORPH_ID),main(SENTENCE_ID,CHUNK_ID,PARENT_ID),dep(SENTENCE_ID,CHUNK_ID,DEP_ID),surf(SENTENCE_ID,DEP_ID,_surf),sloc(SENTENCE_ID,DEP_ID,_sloc),part(SENTENCE_ID,DEP_ID,WO_ID),surf(SENTENCE_ID,WO_ID,を)."
    query = "売るのを格sloc(X,Y)"

    prolog = Solver(pred_txt+"\n"+rule_txt)
    solutions = prolog.find_solutions(query)

    print(solutions)
