from converter import AsaToPrologConverter, genRandomName
from python_asa.asapy.ASA import ASA
from time import time
import sys
import re


if __name__ == "__main__":
    asa = ASA()  # ASAのインスタンス化
    asa_2_prolog_converter = AsaToPrologConverter(asa) # ASAtoPrologコンバータのコンストラクタにASAのインスタンスを渡す

    # CL引数から日本語テキストのfilename取得 
    # e.g.) python pyswiptest.py test.txt => text.txt
    filename = str(sys.argv[1])
    
    with open(filename, "r") as f:
        raw_text = f.read().replace('\n','')
    
    inputs = re.split('[\.\!\?\。\！\？\「\」]', raw_text)  # 句読点等でsplit
    generate_query = 'author(_author,_work):-semantic(生成),type(X0,verb),(main(X0,書く);main(X0,描く)),role(X1,動作主),main(X1,_author),role(X2,対象),main(X2,_work).'
    start_time = time()

    # inputs to file
    for i in range(len(inputs)-1):
        sentence = inputs[i]
        print("<文章{}>".format(str(i)), "\033[31m", sentence, "\033[0m")
        
        new_file_name = "plfiles/"+genRandomName(10) + ".pl"

        # ファイルへ保存
        with open(new_file_name, mode="w") as f:
            converted_list = asa_2_prolog_converter.convert(sentence)
            f.write("\n".join(converted_list) + "\n")
    print("Saved. Total ",i+1,"files")

    end_time = time()
    print("-[実行時間]", end_time - start_time, "秒","\n")

# semantics(生成（物理）)　の　（）がエラー