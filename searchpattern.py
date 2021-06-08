from time import time
import os
from pyswip import Prolog

if __name__ == "__main__":
    answers_list = []
    start_time = time()

    # plfiles 以下のファイル内を検索
    path ="plfiles/"
    files = os.listdir(path)
    file_name_list = [f for f in files if os.path.isfile(os.path.join(path, f))]

    prolog = Prolog()  # Prologのインスタンス化
    
    for file_name in file_name_list:
        # pattern = "semantic(生成),type(X0,verb),(main(X0,書く);main(X0,描く)),role(X1,動作主),main(X1,_author),role(X2,対象),main(X2,_work)"
        pattern = "class(X,名詞)"
        lines = open(path+file_name,"r").readlines()
        # prologインスタンスはシングルトンであるため，
        # consultからの静的読み込みだと上書きされましたよっていう警告が出てくる．
        # なので動的読み込みで１文ずつ行う
        for line in lines:
            prolog.assertz(line.replace('\n','').replace('.',''))
        
        answer = list(prolog.query(pattern))
        
        prolog.retractall("sentence(_)")
        prolog.retractall("main(_,_)")
        prolog.retractall("type(_,_)")
        prolog.retractall("class(_,_)")
        prolog.retractall("role(_,_)")
        prolog.retractall("part(_,_)")
        prolog.retractall("semantic(_)")

        answers_list.append(answer)
        
        if len(answer) > 0:
            print("\033[31m", "一致しました", "\033[0m","-",answer,"\n")
        else:
            print("\033[31m", "一致するものはありませんでした", "\033[0m","\n")

    end_time = time()
    
    print(answers_list)
    print("[実行時間]", end_time - start_time, "秒","\n")