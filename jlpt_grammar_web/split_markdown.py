import os  

def split_markdown(input_file, output_folder):
    os.makedirs(output_folder, exist_ok=True)  

    with open(input_file, 'r', encoding='utf-8') as f:  
        lines = f.readlines()
        
    info_list = []
    title = ''
    for line in lines[2:]:
        if line.startswith('## '):
            title = line[3:].strip()
            info_list.append([title, []])
        if line.startswith('#'):
            info_list[-1][1].append(line[1:])
        else:
            info_list[-1][1].append(line)
    
    for info in info_list:
        title = info[0]
        content = info[1]
        file_name = os.path.join(output_folder, f"{title}.md")  
        with open(file_name, 'w+', encoding='utf-8') as out_file:  
            out_file.writelines(content)

if __name__ == "__main__":  
    input_file = "vocabulary/index.md"
    output_dir = "output"     # 输出文件夹  
    split_markdown(input_file, output_dir)  