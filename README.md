# python-asa2prolog

python 3.6.8

## USE IN LOCAL

```
sh setup.sh
python pyswiptest.py test.txt
python asa2prolog_api.py
```

## USE IN DOCKER

```
docker compose up --build
docker exec -i -t python3.6.8-ASA bash
```

### システム立ち上げ時

```
$ uvicorn asa2prolog_api:app --port 5000
```

### pyswiptest.py 使用時

```
$ python pyswiptest.py test.txt
```

### python_asa使用時

```
$ cd python_asa/asapy
$ python main.py
```

## CAUTION
- コマンドライン引数でテキストファイルを指定すればファイルからテキスト読み込み，解析が可能です．
- あくまでテスト用ということで簡易的に実装しています．
- 改行が入るとうまく動かない場合があるので改良中です．
