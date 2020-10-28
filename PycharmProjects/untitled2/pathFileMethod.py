import os
import hashlib

arg = input("输入文件路径：")
pdfs = []

for root, x, files in os.walk(arg):
    print(root, x, files)
    for fn in files:
        ext = os.path.splitext(fn)[1].lower()
        if ext != '.pdf':
            continue
        fpth = os.path.join(root, fn)
        fpth = os.path.relpath(fpth,root)
        print(f'发现pdf文件: {fpth}')
        pdfs.append(fpth)

for f in pdfs:
    print("++++++++++++++++++++")
    print(f)

    f1 = arg + "\\" + f
    md5_before = hashlib.md5(open(f1).read()).hexdigest()

    mtime_before = os.stat(f1).st_mtime

    os.stat(f1).st_mtime == mtime_before

    hashlib.md5(open(f1).read()).hexdigest() == md5_before


    os.stat(f1).st_mtime == mtime_before
    hashlib.md5(open(f1).read()).hexdigest() == md5_before





