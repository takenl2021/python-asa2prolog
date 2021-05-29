from pyswip import Prolog
from converter import AsaToPrologConverter
from python_asa.asapy.ASA import ASA
from time import sleep, time
import os
import io
import sys
import re
import random
import string


def randomname(n):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=n))


if __name__ == "__main__":
    asa = ASA()  # ASAのインスタンス化
    # ASAtoPrologコンバータのコンストラクタにASAのインスタンスを渡す
    a2p_converter = AsaToPrologConverter(asa)
    prolog = Prolog()  # Prologのインスタンス化
    filename = str(sys.argv[1])  # CL引数から日本語テキストのfilename取得 e.g.) test.txt
    with open(filename, "r") as f:
        raw_text = f.read()
    inp = re.split('[\.\!\?\。\！\？\n]', raw_text)  # 句読点等でsplit
    query = 'author(_author,_work):-semantic(生成),type(X0,verb),(main(X0,書く);main(X0,描く)),role(X1,動作主),main(X1,_author),role(X2,対象),main(X2,_work).'
    queryy = "author(X,Y)"

    start = time()

    for i in range(len(inp)-1):
        a2p = a2p_converter.convert(inp[i])

        new_file_name = randomname(10) + ".pl"
        with open(new_file_name, mode="w") as f:
            f.write("\n".join(a2p) + "\n" + query)

        anslist = []
        with io.StringIO() as f:
            sys.stdout = f
            consult = prolog.consult(new_file_name)
            answer = list(prolog.query(queryy))
            sys.stdout = sys.__stdout__
            anslist.append(answer)
        if len(answer) != 0:
            print("<文章{}>".format(str(i)), "\033[31m", inp[i], "\033[0m")
            print("-[結果] パタンに一致しました")
            print(answer[0]["X"]+" , "+answer[0]["Y"])
            print("")
        # os.remove("./"+new_file_name)
    end = time()
    print(anslist)
    print("-[実行時間]", end - start, "秒")
