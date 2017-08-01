from main_tetrode import main 
import pickle
import os
import sys

mainPath = sys.stdin.read().splitlines()[0]
dirs = os.listdir(mainPath)

for folder in (folder for folder in dirs if ((folder != 'log.txt') and (folder != 'notes.docx') and (folder != 'analyzed') and (folder != 'other'))):
    print(mainPath + folder)
    p = pickle.load(open(mainPath + folder + '/paramsDict.p', 'rb'))
    main(p)
