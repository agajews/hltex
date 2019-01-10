from hltex.translator import Translator

t = Translator('\\documentclass{article}\n===\nHey!\n')
# print(t.translate())
print(t.translate_internal())
