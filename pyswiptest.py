from pyswip import Prolog
from ASAtoProlog import ASAtoProlog, ASA_assembler
from time import sleep, time
import os
import io
import sys
import re


if __name__ == "__main__":
    filename = str(sys.argv[1])
    with open(filename, "r") as f:
        raw_text = f.read()
    inp = re.split('[\.\!\?\。\！\？\n]', raw_text)
    print(inp)
    query = 'author(_author,_work):-semantic(生成),type(X0,verb),(main(X0,書く);main(X0,描く)),role(X1,動作主),main(X1,_author),role(X2,対象),main(X2,_work).'
    queryy = "author(X,Y)"

    match = 0
    prolog = Prolog()

    print("以下の条件でパタンマッチを開始します")
    print("-[条件1]", query)
    print("")
    print("")

    start = time()

    for i in range(len(inp)-1):
        # for i in range(len(inp)-1):
        a2p = ASAtoProlog.ASAtoProlog(inp[i])

        with open("testfile.pl", mode="w") as f:
            f.write("\n".join(a2p) + "\n" + query)

        with io.StringIO() as f:
            sys.stdout = f
            consult = prolog.consult("testfile.pl")
            sys.stdout = sys.__stdout__

        answer = list(prolog.query(queryy))
        # if answer.strip().split(",\n")[0] != "false.":
        if len(answer) != 0:
            print("<文章{}>".format(str(i)), "\033[31m", inp[i], "\033[0m")
            print("-[結果] パタンに一致しました")
            print(answer[0]["X"]+" , "+answer[0]["Y"])
            print("")
            match += 1
        if len(answer) == 0:
            print("<文章{}>".format(str(i)), inp[i])
            print("-[結果] パタンに一致しませんでした")
            print("")

    end = time()
    print("")

    print("パタンマッチが終了しました")
    print("-[マッチ数]", match)
    print("-[実行時間]", end - start, "秒")
