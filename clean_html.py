import os
# 打开原始文件和一个临时文件
src = input("> ")
b = os.path.join(os.path.dirname(src),'temp.txt')
with open(src, 'r') as infile, open(b, 'w') as outfile:
    for line in infile:
        # 如果不包含指定字符串，就将该行写入临时文件
        if '<img src=\'\' style=\'width: 100%; max-width: 100%; height: auto;\' />' not in line:
            outfile.write(line)

# 关闭文件
infile.close()
outfile.close()

# 用临时文件替换原始文件
import os
os.remove(src)
os.rename(b,src)
