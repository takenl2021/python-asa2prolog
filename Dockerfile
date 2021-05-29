FROM python:3.6.8
WORKDIR /usr/app

RUN wget http://www.swi-prolog.org/download/devel/src/swipl-7.5.11.tar.gz \
    && tar -xzf swipl-7.5.11.tar.gz \
    && cd swipl-7.5.11 && ./configure && make && make install \
    && cd packages && ./configure && make && make install \
    && cd ../.. && rm -rf swipl-7.5.11.tar.gz swipl-7.5.11

RUN apt update && apt-get install -y mecab libmecab-dev mecab-ipadic mecab-ipadic-utf8
RUN pip install mecab-python3 pyswip fastapi uvicorn

COPY CRF++-0.58.tar.gz /usr/app/CRF++-0.58.tar.gz
RUN tar zxvf CRF++-0.58.tar.gz \
    && cd CRF++-0.58 \
    && ./configure \
    && make \
    && make install

RUN DOWNLOAD_URL="https://drive.google.com`curl -c cookies.txt \
       'https://drive.google.com/uc?export=download&id=0B4y35FiV1wh7SDd1Q1dUQkZQaUU' \
       | sed -r 's/"/\n/g' |grep id=0B4y35FiV1wh7SDd1Q1dUQkZQaUU |grep confirm |sed 's/&amp;/\&/g'`" \
    && curl -L -b cookies.txt -o cabocha-0.69.tar.bz2 "$DOWNLOAD_URL" \
    && tar jxf cabocha-0.69.tar.bz2 \
    && cd cabocha-0.69 \
    && ./configure --with-mecab-config=`which mecab-config` --with-charset=utf8 \
    && make \
    && make install \
    && cd python \
    && python setup.py build \
    && python setup.py install
RUN echo "/usr/local/lib" >> /etc/ld.so.conf && /sbin/ldconfig
ADD setup.sh ./setup.sh
RUN sh setup.sh
