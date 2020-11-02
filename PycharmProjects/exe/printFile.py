import win32api
import win32print
import os

## 自带功能
def printer_loading(filename):
    win32api.ShellExecute (
    0,
    "print",
    filename,
    '/d:"%s"' % win32print.GetDefaultPrinter (),
    ".",
    0
    )

## 统一修改，新建窗体录入功能
arg = input("输入文件路径：")
pdfs = []

for root, x, files in os.walk(arg):
    print(root, "\t", x, "\t", files, "\n")
    for fn in files:
        ext = os.path.splitext(fn)[1].lower()
        if ext != '.pdf':
            continue
        fpth = os.path.join(root, fn)
        ## fpth = os.path.relpath(fpth,root)
        print(f'发现pdf文件: {fpth}')
        pdfs.append(fpth)

for pdf in pdfs:
    ## print(pdf)
    printer_loading(pdf)
