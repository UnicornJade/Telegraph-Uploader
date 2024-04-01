import re
import os

def split(file,max=200):
    # 读取包含多个img标签的txt文件
    input_file = file
    root = os.path.dirname(input_file)
    with open(input_file, 'r') as f:
        content = f.read()

    # 使用正则表达式找到所有的img标签
    img_tags = re.findall(r'<img\s+[^>]*/>', content)
    htmls =[]
    # 分割img标签为多个txt文件
    batch_size = max
    for i in range(0, len(img_tags), batch_size):
        batch = img_tags[i:i + batch_size]

        # 获取源文件的名称（不包含路径和扩展名）
        base_filename = os.path.splitext(os.path.basename(input_file))[0]

        # 创建一个新txt文件并写入img标签，文件名包含编号
        output_file_name = f'{base_filename}(Page{i//batch_size}).txt'
        splited_path = os.path.join(root,output_file_name)
        htmls.append(splited_path)

        with open(splited_path, 'w') as output_file:
            for img_tag in batch:
                output_file.write(img_tag)

    print("[ * ] Splited...")
    return htmls
