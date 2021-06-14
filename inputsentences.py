from converter import AsaToPrologConverter, genRandomName
from python_asa.asapy.ASA import ASA
from time import time
import sys
import re
import datetime

def genpl(filename):
        start_time = time()
        asa = ASA()  # ASAのインスタンス化
        asa_2_prolog_converter = AsaToPrologConverter(asa) # ASAtoPrologコンバータのコンストラクタにASAのインスタンスを渡す

        # CL引数から日本語テキストのfilename取得 
        # e.g.) python inputsentences.py test.txt => text.txt
    
        with open(filename, "r") as f:
            raw_text = f.read().replace('\n','')
    
        inputs = re.split('[\.\!\?\。\！\？\「\」\．]', raw_text)  # 句読点等でsplit

        # inputs to file
        for i in range(len(inputs)-1):
            sentence = inputs[i]
            # print("<文章{}>".format(str(i)), "\033[31m", sentence, "\033[0m")
        
            new_file_name = "plfiles/"+ datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S_%f') + ".pl"

            # ファイルへ保存
            with open(new_file_name, mode="w") as f:
                converted_list = asa_2_prolog_converter.convert(re.sub('[\，\、]','',sentence))
                # https://www.swi-prolog.org/pldoc/man?predicate=style_check/1
                f.write("style_check(-discontiguous).\n") # dicontiguous warningの無視
                f.write("\n".join(converted_list) + "\n")

        end_time = time()
        return {"files":i+1, "time":end_time - start_time}
    
if __name__ == "__main__":
    filename = str(sys.argv[1])
    value = genpl(filename)
    print("[生成ファイル数]", value["files"],"\n")
    print("[実行時間]", value["time"],"秒","\n")

# semantics(生成（物理）)　の　（）がエラー