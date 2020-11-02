import win32api
import win32print
import os

def printer_loading(filename):
    ## win32print.SetDefaultPrinter("Kyocera KM-2540 KX")
    win32api.ShellExecute (
    0,
    "print",
    filename,
    '/d:"%s"' % win32print.GetDefaultPrinter (),

    ".",
    0
    )
    print(win32print.GetDefaultPrinter())

arg = input("输入文件路径：")
pdfs = []

for root, x, files in os.walk(arg):
    print(root, "\t", x, "\t", files, "\n")
    win32print.SetDefaultPrinter("Kyocera KM-2540 KX")
    for fn in files:
        ext = os.path.splitext(fn)[1].lower()
        if ext != '.pdf':
            continue
        fpth = os.path.join(root, fn)
        ## fpth = os.path.relpath(fpth,root)
        print(f'发现pdf文件: {fpth}')
        pdfs.append(fpth)

if len(pdfs) == 0:
    print("目录下无可用pdf文件！")

for pdf in pdfs:
    ## print(pdf)
    printer_loading(pdf)
