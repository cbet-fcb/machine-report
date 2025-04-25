from objects import *

class ServerRequests:
    def __init__(self):
        pass
    
    def testModel(self, a, b, c, d, e, f) -> None:
        TestModel(a=a,b=b,c=c,d=d,e=e,f=f).print_all()
        pass

    # def ocr(self, image_path) -> None:

    pass

if __name__ == "__main__":
    from utils import generateRandomString
    sr = ServerRequests()

    def stripBeforeSubstring(text: str, substring: str):
        return text[i := text.find(substring) if i != -1 else 0 : ]

    text = "abcdef" 
    sr.testModel(a=stripBeforeSubstring(text,"a") + "\n", 
                 b=stripBeforeSubstring(text,"b") + "\n", 
                 c=stripBeforeSubstring(text,"c") + "\n",
                 d=stripBeforeSubstring(text,"d") + "\n",
                 e=stripBeforeSubstring(text,"e") + "\n",
                 f=stripBeforeSubstring(text,"f"))