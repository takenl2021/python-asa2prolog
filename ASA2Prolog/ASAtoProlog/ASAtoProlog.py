from . import ASA_assembler,createTree

def ASAtoProlog(input_string):
    result = ASA_assembler.Analyze_sentence(input_string).analyze()
    dc = ASA_assembler.Get_element(result).get_dictionary()
    buf = []
    ids = []
    ct = createTree.write_tree()
    buf.append(ct.write_sentence(dc["sentence"]))

    for idcount in range(len(dc)-1):
        ids.append(dc["ID{}".format(str(idcount))])
    
    for i in range(len(ids)):
        # buf.append(ct.write_phrase(ids[i]["phrase"]))
        buf.append(ct.write_type(ids[i]["phrase"],ids[i]["type"]))
        if "semantic" in ids[i]:
            for sems in ids[i]["semantic"].split("-"):
                buf.append(ct.write_semantic(sems.replace("・","or")))
        
        if "semrole" in ids[i]:
            buf.append(ct.write_role(ids[i]["phrase"],ids[i]["semrole"].split("（")[0]))

        for ii in range(2):
            if ii == 0 and ("main" in ids[i]):
                buf.append(ct.write_main(ids[i]["phrase"],ids[i]["main"]))
                for iii in range(len(ids[i]["morphemes"])):
                    if ids[i]["morphemes"][iii][3] in ids[i]["main"]:
                        buf.append(ct.write_class(ids[i]["main"],ids[i]["morphemes"][iii][4]))

            if ii == 1 and ("part" in ids[i]):
                buf.append(ct.write_part(ids[i]["phrase"],ids[i]["part"]))
                for iii in range(len(ids[i]["morphemes"])):
                    if ids[i]["morphemes"][iii][3] in ids[i]["part"]:
                        buf.append(ct.write_class(ids[i]["part"],ids[i]["morphemes"][iii][4]))

    return buf