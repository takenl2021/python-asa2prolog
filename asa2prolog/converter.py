import io
import sys
import re
from asapy.ASA import ASA
from graphviz import Digraph
import random
import string
from pprint import pprint


class Converter():
    def __init__(self, asa_instance):
        self.__sentences = None
        try:
            if isinstance(asa_instance, ASA):
                self.__asa_instance = asa_instance
            else:
                raise ValueError("Invalid ASA instance.")
        except ValueError as e:
            print(e)

    def set_sentences(self, sentences):
        try:
            self.__sentences = re.split(
                '[\.\!\?\。\！\？\「\」\．]', sentences.replace('\n', ''))
        except:
            print(f"\033[31mError\033[0m: Couldn't set sentences.")

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

    def analyze_sentence(self, sentence):
        self.__asa_instance.parse(sentence)
        with io.StringIO() as f:
            sys.stdout = f
            self.__asa_instance.selectOutput()
            asa_output = f.getvalue()
            sys.stdout = sys.__stdout__
        asa_json = self.__asa_instance.dumpJson()
        shaped_json = self.__shape_json_to_tree(asa_json)
        return {
            'asa_output': asa_output,
            'asa_json': asa_json,
            'shaped_json': shaped_json
        }

    def __shape_json_to_tree(self, json):
        # _____(0)variables_____
        node_id_lv0 = 0  # sentenceレベルのノード番号 実質不要だが好みで配置
        node_id_lv1 = 1  # chunkレベルのノード番号
        node_id_lv2 = len(json["chunks"]) + 1  # morphレベルのノード番号
        sloc_start_lv0 = 0  # sentenceレベルのslocカウンタ 実質不要だが好みで配置
        sloc_start_lv1 = 0  # chunkレベルのslocカウンタ
        sloc_start_lv2 = 0  # morphレベルのslocカウンタ

        # _____START_____(1)sentenceレベル_____
        shaped_json = {
            'node_id': node_id_lv0,
            'children': [{
                'node_id': json["surface"],
                'pred_name': "surf",
            }]
        }
        for chunk in json["chunks"]:
            # _____START_____(2)chunkレベル_____
            shaped_chunk = {
                'node_id': node_id_lv1,
                'pred_name': "chunk",
                'children': [{
                    'node_id': chunk["surface"],
                    'pred_name': "surf"
                }, {
                    'node_id': f"{sloc_start_lv1}_{sloc_start_lv1+len(chunk['surface'])-1}",
                    'pred_name': "sloc"
                }]
            }

            semroles = chunk.get("semrole")  # 意味役割
            if semroles:
                for role in semroles.split("|"):
                    if role != "":
                        shaped_chunk["children"].append({
                            'node_id': role.replace("-","ー").replace("（","「").replace("）","」"),
                            'pred_name': "role"
                        })

            semantics = chunk.get("semantic")  # 概念
            if semantics:
                for semantic in semantics.split("-"):
                    if semantic != "":
                        shaped_chunk["children"].append({
                            'node_id': semantic.replace("-","ー").replace("（","「").replace("）","」"),
                            'pred_name': "semantic"
                        })

            deps = chunk.get("modified")  # 係り関係
            if deps:
                for dep in deps:
                    shaped_chunk["children"].append({
                        'node_id': dep+1,
                        'pred_name': "dep"
                    })

            main = chunk.get("main")  # main部
            if main:
                shaped_chunk["children"].append({
                    'node_id': main,
                    'pred_name': "main"
                })

            part = chunk.get("part")  # part部
            if part:
                shaped_chunk["children"].append({
                    'node_id': part,
                    'pred_name': "part"
                })

            morphs = chunk.get("morphs")  # 形態素
            if morphs:
                # _____START_____(3)morphレベル_____
                for morph in morphs:
                    morph_surface = morph.get("surface")
                    morph_base = morph.get("base")
                    morph_sloc = f"{sloc_start_lv2}_{sloc_start_lv2+len(morph_surface)-1}"
                    morph_poses = morph.get("pos").split(",")
                    shaped_morph = {
                        'node_id': node_id_lv2,
                        'pred_name': "morph",
                        'children': [
                            {
                                'node_id': morph_surface,
                                'pred_name': "surf"
                            },
                            {
                                'node_id': morph_base,
                                'pred_name': "surfBF"
                            },
                            {
                                'node_id': morph_sloc,
                                'pred_name': "sloc"
                            }
                        ]
                    }
                    for pos in morph_poses:
                        shaped_morph["children"].append({
                            'node_id': pos,
                            'pred_name': "pos"
                        })
                    sloc_start_lv2 += len(morph_surface)
                    shaped_chunk["children"].append(shaped_morph)
                    node_id_lv2 += 1
                # ______END______(3)morphレベル_____
            sloc_start_lv1 += len(chunk["surface"])
            shaped_json["children"].append(shaped_chunk)
            node_id_lv1 += 1
            # ______END______(2)chunkレベル_____
        # ______END______(1)sentenceレベル_____
        return shaped_json

    def __gen_prolog_pred(self, pred_name, params):
        params = list(map(str,params))
        if pred_name == "sloc":
            params = [params[0],params[1],f"'{params[2]}'"]
        pred = f'{pred_name}({",".join(params)}).'
        return pred

    def __parse_node(self, sentence_id, current_node, parent_node_id=None):
        pred_list = []
        current_node_id = current_node["node_id"]
        pred_name = current_node.get("pred_name")
        if pred_name and parent_node_id != None:
            pred_list.append(
                self.__gen_prolog_pred(
                    pred_name, [sentence_id, parent_node_id, current_node_id])
            )
        children = current_node.get("children")
        if children:
            for child in children:
                pred_list.extend(
                    self.__parse_node(sentence_id, child, current_node_id)
                )
        return pred_list

    def __parse_node_dot(self, current_node, dg, dg_id="0", start=False):
        current_node_surf = current_node.get('node_id')
        children = current_node.get('children')  # 子ノード
        if start:  # 先頭のみ
            dg.node(f"{current_node_surf}", style="bold", color="blue")
            dg_id = str(current_node_surf)
        if children:
            for child in children:
                child_surf = child.get('node_id')
                edge_label = child.get('pred_name')
                child_dg_id = gen_random_name(16)
                if edge_label == 'sloc':  # slocはひし形ノード
                    dg.node(child_dg_id, str(child_surf),
                            shape='diamond', style='filled', color='yellow')
                elif edge_label == 'surf':  # surfは水色塗りつぶし
                    dg.node(child_dg_id, str(child_surf), shape="box",
                            style='filled', color='lightblue2')
                elif edge_label == 'surfBF':  # surfBFは水色太枠
                    dg.node(child_dg_id, str(child_surf), shape="box",
                            style='bold', color='lightblue2')
                elif edge_label == 'pos':  # posはオレンジ太線
                    dg.node(child_dg_id, str(child_surf),
                            style='bold', color='orange')
                elif edge_label in ['chunk', 'morph']:  # chunk/morphは青太枠
                    dg.node(child_dg_id, str(child_surf),
                            style='bold', color='blue')
                elif edge_label == 'role':
                    dg.node(child_dg_id, str(child_surf), shape="doubleoctagon",
                            style="bold", color="blue", fontcolor="blue", fontstyle="bold")
                elif edge_label == 'semantic':
                    dg.node(child_dg_id, str(child_surf), shape="tripleoctagon",
                            style="filled", color="navy", fontcolor="white", fontstyle="bold")
                elif edge_label == 'main':
                    dg.node(child_dg_id, str(child_surf), style='filled',
                            color="pink", fontstyle='bold')
                elif edge_label == 'part':
                    dg.node(child_dg_id, str(child_surf),
                            style='bold', color="pink")
                else:
                    dg.node(child_dg_id, str(child_surf))
                dg.edge(dg_id, child_dg_id, label=edge_label)
                self.__parse_node_dot(child, dg, child_dg_id)

    def convert(self, sentence, sentence_id=0, graphnize=False):
        sentence_info = self.analyze_sentence(sentence)
        json = sentence_info["asa_json"]
        shaped_json = sentence_info["shaped_json"]
        pred_list = self.__parse_node(
            sentence_id=sentence_id,
            current_node=shaped_json,
            parent_node_id=None
        )
        result = {
            'predicates': "\n".join(pred_list),
            'asa_json': json
        }
        if graphnize: # グラフ化オプションを指定した場合
            dg = Digraph(
                engine='dot',
                format='png',
                name=f"{sentence}",
                node_attr={
                    'height': '1'
                },
                graph_attr={
                    'size': '500, 500',
                    'ranksep': "2.5"
                }
            )
            self.__parse_node_dot(shaped_json, dg, start=True)
            result['dot_string'] = dg.source

        return result

    def convert_all(self, graphnize=False):
        if(self.__sentences == None):
            print(
                f"\033[31mConvert Error\033[0m: Make sure to set some sentences before conversion.")
        else:
            sentence_id = 0
            results = []
            for sentence in self.__sentences:
                if sentence == "" or sentence == " " or sentence == "　":
                    continue
                result = self.convert(sentence, sentence_id, graphnize)
                results.append(result)
                sentence_id += 1
            return results


def gen_random_name(n):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=n))
