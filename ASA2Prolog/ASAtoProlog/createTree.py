class write_tree():
    def __init__(self):
        pass

    def write_sentence(self,sentence):
        return "sentence(" + sentence + ")."

    def write_semantic(self,semantic):
        return "semantic(" + semantic + ")."

    def write_phrase(self,phrase):
        return "phrase(" + phrase + ")."

    def write_main(self,phrase,main):
        return "main(" + phrase + "," + main + ")."

    def write_part(self,phrase,part):
        return "part(" + phrase + "," + part + ")."

    def write_role(self,phrase,role):
        return "role(" + phrase + "," + role + ")."

    def write_morpheme(self,word,morpheme):
        return "morpheme(" + word + "," + morpheme + ")."

    def write_type(self,phrase,type_):
        return "type(" + phrase + "," + type_ + ")."

    def write_class(self,word,class_):
        return "class(" + word + "," + class_ + ")."
