from pyswip import Prolog
from time import time
import os


if __name__ == "__main__":
    answers_list = []

    # pattern = "semantic(生成),type(X0,verb),(main(X0,書く);main(X0,描く)),role(X1,動作主),main(X1,_author),role(X2,対象),main(X2,_work)"
    pattern = "type(X,elem)"
    start_time = time()

    # plfiles 以下のファイル内を検索
    path ="plfiles/"
    files = os.listdir(path)
    file_name_list = [f for f in files if os.path.isfile(os.path.join(path, f))]
    for file_name in file_name_list:
        prolog = Prolog()  # Prologのインスタンス化
        prolog.consult(path+file_name)
        answer = list(prolog.query(pattern))
        answers_list.append(answer)

        print("[結果]")
        if len(answer) > 0:
            print("一致しました\n",answer)
        else:
            print("一致するものはありませんでした")


    end_time = time()
    print(answers_list)
    print("[実行時間]", end_time - start_time, "秒","\n")