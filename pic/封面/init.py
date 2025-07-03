import os
import sys


# from xml.etree.ElementTree import tostring  <-- 已移除，这是不正确的引入

def batch_rename_images():
    # 0. 定义常见的图片文件扩展名
    image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp')

    # 1. 获取当前文件夹下的所有文件
    try:
        all_files = os.listdir('.')
    except OSError as e:
        print(f"错误：无法访问当前目录。 {e}")
        return

    # 2. 筛选出所有图片文件
    image_files = [f for f in all_files if os.path.isfile(f) and f.lower().endswith(image_extensions)]

    if not image_files:
        print("在此文件夹中未找到任何图片文件。")
        return

    print(f"找到了 {len(image_files)} 个图片文件。")
    start_index = len(image_files)

    # 3. 开始重命名
    renamed_count = 0
    # enumerate 的起始值设为 1
    for i, old_name in enumerate(image_files, 1): 
        # 分离文件名和扩展名
        file_name, file_ext = os.path.splitext(old_name)
        new_name = str(start_index + i) + file_ext

        # 检查新文件名是否与旧文件名相同
        if file_name.isdigit() and file_ext in image_extensions:
            print(f"跳过： '{old_name}' 已经符合命名规则。")
            continue

        # 检查新文件名是否已存在，避免覆盖
        if os.path.exists(new_name):
            print(f"警告：目标文件名 '{new_name}' 已存在。跳过对 '{old_name}' 的重命名。")
            continue

        try:
            # 执行重命名
            os.rename(old_name, new_name)
            print(f"成功: '{old_name}'  ->  '{new_name}'")
            renamed_count += 1
        except OSError as e:
            print(f"错误：重命名 '{old_name}' 失败。 {e}")

    print(f"\n处理完成！共重命名了 {renamed_count} 个文件。")


if __name__ == "__main__":
    print("本脚本将重命名当前目录下的所有图片文件为 '1.jpg', '2.png' ... 的格式。")

    confirm = input("确定要继续吗？ (输入 'y' 或 'yes' 继续): ").lower()

    if confirm in ['y', 'yes']:
        batch_rename_images()
    else:
        print("操作已取消。")