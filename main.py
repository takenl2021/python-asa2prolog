from asa2prolog_converter import Converter
from python_asa.asapy.ASA import ASA
from prologpy import Solver
import numpy as np


def main():
    # 1. ASAとコンバータのインスタンス化
    '''
    - 初期ロードに時間がかかるためASAはシングルトン
    - Converter内でインスタンス化しないのは、API側での複数リクエストに関してリソースを共有しないため
    '''
    asa = ASA()
    converter = Converter(asa_instance=asa)

    # 2. テキストのロード
    '''
    - string形式のロードとファイルからのロードいずれにも対応
    - 現状ロードは上書き方式にしているが、追加方式(リセットも含め)にするか検討中
    - ロードされたテキストを配列で確認可能
    '''
    converter.set_sentences("有川浩が図書館戦争を書いた。")
    converter.load_sentences("example/sample.txt")
    converter.get_sentences()  # ロードされたテキストを配列で取得

    # 3. コンバート
    '''
    - テキストをコンバートする
    - convert("コンバートしたいテキスト") で一文コンバート
    - convert_all() でロードされた全テキストをコンバート
    '''
    result = converter.convert("有川浩が図書館戦争を書いた。")
    '''
    result => {
      'predicates': prolog述語集合<string>,
      'dot_string': DOT<string>,
      'asa_json': ASAの出力json<dict>
    }
    '''
    results = converter.convert_all()
    '''
    results => {
      'predicates': prolog述語集合<string>,
      'dot_string': DOT<string>,
      'asa_json': ASAの出力json<dict>
    }[]
    '''

    # 4. prolog述語をまとめる
    predicates = "\n".join([result['predicates'] for result in results])

    # 5. prolog定義済みruleをロード
    rule_file_path = "./config/rules.pl"
    with open(rule_file_path, "r") as f:
        rule_txt = f.read()

    # 6. クエリ
    query = "売るのを格sloc(SENTENCE_ID,X,Y)"

    # 7. 述語とルールをprolog処理系にconsult
    prolog = Solver(predicates+"\n"+rule_txt)

    # 8. 解探索
    solutions = dict(prolog.find_solutions(query))

    print(solutions)  # この形式で解が返されるの少し不満

    try:
        # 整形 内包表記で書けそう???
        transposed = np.array([solutions[key] for key in solutions.keys()]).T
        answers = []
        for t in transposed:
            answer = {}
            for key, value in zip(solutions.keys(), t):
                answer[key] = value
            answers.append(answer)
        print(answers)
    except:
        []


if __name__ == "__main__":
    main()
