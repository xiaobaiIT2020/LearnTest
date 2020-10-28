import cmd
import sys
import json
import pdfplumber
import os
import pprint


class FapiaoShell(cmd.Cmd):
    """ 发票 """

    intro = '欢迎使用发票提取工具，输入?(help)获取帮助消息和命令列表，CTRL+C退出程序。\n'
    prompt = '\n输入命令: '
    doc_header = "详细文档 (输入 help <命令>):"
    misc_header = "友情提示:"
    undoc_header = "没有帮助文档:"
    nohelp = "*** 没有命令(%s)的帮助信息 "

    def __init__(self):
        print("---- SELF ----")
        super().__init__()

    def do_load(self, arg):
        """ 加载发票 例如：load D:\ """
        if not os.path.isdir(arg):           ##-- 支持文件夹，文件夹下全为发票文件
        ## if not os.path.isfile(arg):
            print('参数必须是发票文件/目录!')
            return
        os.chdir(os.path.dirname(arg))


        pdfs = []
        for root, _, files in os.walk(arg):
            for fn in files:
                ext = os.path.splitext(fn)[1].lower()
                if ext != '.pdf':
                    continue
                fpth = os.path.join(root, fn)
                ## 返回fpath从某个位置开始的相对路径
                fpth = os.path.relpath(fpth, root)
                print(f'发现pdf文件: {fpth}')
                pdfs.append(fpth)

        pdf_ctxs = self._parse_pdfs(pdfs)       ## ？？？？？？
        total = {
            '内容': pdf_ctxs,
            '发票数': len(pdf_ctxs),
            '总计': 0,
        }
        for fpth, info in pdf_ctxs:
            total['总计'] += float(info['总计'])

        print('\n保存到 结果.json...')

        with open("结果.json", 'w', encoding='utf-8') as json_file:
            json.dump(total,
                      json_file,
                      ensure_ascii=False,
                      sort_keys=True,
                      indent=4,
                      separators=(', ', ': '))

        print('完成!')

    def _parse_pdfs(self, pdfs):
        """ 分析 """
        result = []
        for fpth in pdfs:
            info = {}
            with pdfplumber.open(fpth) as pdf:
                page = pdf.pages[0]

                print(page.extract_text())

                if '增值税电子普通发票' not in ''.join(page.extract_text()):
                    result.append((fpth, {}))

                inf = self._extrace_from_words(page.extract_words())
                info.update(inf)

                inf = self._extrace_from_table(page.extract_tables())
                info.update(inf)

            result.append((fpth, info))
        return result

    def _extrace_from_words(self, words):
        """ 从单词中提取 """
        info = {}

        lines = {}
        for word in words:
            top = int(word['top'])
            bottom = int(word['bottom'])
            pos = (top + bottom) // 2
            text = word['text']
            if pos not in lines:
                lines[pos] = [text]
            else:
                lines[pos].append(text)

        lines_pack = []
        last_pos = None
        for pos in sorted(lines):
            arr = lines[pos]

            if len(lines_pack) > 0 and pos - last_pos <= 10:
                lines_pack[-1] += arr
                continue

            lines_pack.append(arr)
            last_pos = pos
            continue

        for pack in lines_pack:
            for idx, line in enumerate(pack):
                if '电子普通发票' in line:
                    info['标题'] = line
                    continue

                if '发票代码:' in line:
                    info['发票代码'] = line.split(':')[1]
                    continue

                if '发票号码:' in line:
                    info['发票号码'] = line.split(':')[1]
                    continue

                if '开票日期:' in line:
                    year = line.split(':')[1]
                    month = [ln for ln in pack if ln.isdigit()][0]
                    day = [ln[:2] for ln in pack if '日' in ln][0]
                    info['开票日期'] = f'{year}-{month}-{day}'
                    continue

                if '机器编号:' in line:
                    info['机器编号'] = [ln for ln in pack if ln.isdigit()
                                    and len(ln) > 10][0]
                    continue

                if '码:' in line:
                    c1 = pack[idx].split(':')[1]
                    c2 = pack[idx+1]
                    c3 = pack[idx+2]
                    c4 = pack[idx+3]
                    info['校验码'] = f'{c1} {c2} {c3} {c4}'
                    continue

                if '收款人:' in line:
                    info['收款人'] = line.split(':')[1]
                    continue

                if '开票人:' in line:
                    info['开票人'] = line.split(':')[1]
                    continue

        return info

    def _extrace_from_table(self, table):
        """ 从表中提取 """
        info = {}
        if len(table) != 4:
            return None

        # 购买方
        for cell in table[0]:
            if not cell:
                continue

            lines = cell.splitlines()
            for line in lines:
                if '名        称:' in line:
                    info['购买方名称'] = line.split(':')[1]
                    continue

                if len(line) == 18 and line.isalnum():
                    info['购买方税号'] = line
                    continue

                if len(line) == 27:
                    if '密码' not in info:
                        info['密码'] = []
                    info['密码'].append(line)
                    continue

        # 详细
        for cell in table[1]:
            if not cell:
                continue

            lines = cell.splitlines()
            for line in lines:
                if '货物或应税劳务、服务名称' in line:
                    info['商品'] = lines[1:-1]
                    break

                if '金  额' in line:
                    info['总金额'] = lines[-1][1:]
                    break

                if '税  额' in line:
                    info['总税额'] = lines[-1][1:]
                    break

        # 合计
        for cell in table[2]:
            if not cell:
                continue

            lines = cell.splitlines()
            for line in lines:
                if '¥' in line:
                    info['总计'] = line[1:]

        # 销售方
        for cell in table[3]:
            if not cell:
                continue

            lines = cell.splitlines()
            for line in lines:
                if '名        称:' in line:
                    info['销售方名称'] = line.split(':')[1]
                    continue

                if len(line) == 18 and line.isalnum():
                    info['销售方税号'] = line
                    continue

        return info


if __name__ == '__main__':
    try:
        FapiaoShell().cmdloop()
    except KeyboardInterrupt:
        print('\n\n再见！')