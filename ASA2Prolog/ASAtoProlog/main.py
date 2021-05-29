from asapy.ASA import ASA

if __name__ == '__main__':
    asa = ASA()
    inp = input()
    asa.parse(inp)
    asa.selectOutput()
