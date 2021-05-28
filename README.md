# python-asa2prolog

python 3.6.8

## USE IN LOCAL

```
sh setup.sh
python pyswiptest.py test.txt
```

## USE IN DOCKER

```
docker compose up --build
```

## CAUTION
- コマンドライン引数でテキストファイルを指定すればファイルからテキスト読み込み，解析が可能です ．
- あくまでテスト用ということで簡易的に実装しています．
- 改行が入るとうまく動かない場合があるので改良中です．
