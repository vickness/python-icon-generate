# !/usr/bin/python
# -*- coding: UTF-8 -*-

import sys
import os
import json


# icon图片尺寸
iosIconSize = ['20@2x', '20@3x', '29@2x', '29@3x', '40@2x', '40@3x', '60@2x', '60@3x', '1024@1x']
androidIconSize = [48, 72, 96, 144, 192]
androidNames = ['mdpi', 'hdpi', 'xhdpi', 'xxhdpi', 'xxxhdpi']

# 启动图尺寸
iosSplashSize = [(320, 480), (640, 960), (640, 1136), (750, 1334), (828, 1792), (1125, 2436), (1242, 2208), (1242, 2688)]
androidSplashSize = [(320, 480), (480, 800), (720, 1280), (960, 1600), (1280, 1920)]

# icon输出路径
iosIconOutPutPath = ""
androidIconOutPutPath = "./android/app/src/main/res/"

# 启动图输出路径
iosSplashOutPutPath = ""
androidSplashOutPutPath = "./android/app/src/main/res/"

# 图片默认输入路径
inputPath = "./res"


# 输出函数
def log(text):
    print '\033[31m' + text + '\033[0m'


# 检查路径是否有效
if len(sys.argv) <= 1 and os.path.exists('./res') is False:
    log('图片路径无效，请输入文件目录或在工程根目录创建res文件夹')
    quit()


# 使用输入的图片路径
if len(sys.argv) > 1:
    inputPath = sys.argv[1]


# 遍历iOS工程路径，找到输出路径
for root, dirs, files in os.walk("./ios", topdown=False):
    for name in dirs:
        if name.endswith("Images.xcassets"):
            iosIconOutPutPath = os.path.join(root, name, "AppIcon.appiconset/")
            iosSplashOutPutPath = os.path.join(root, name, "LaunchImage.launchimage/")
            print(iosIconOutPutPath)
            print(iosSplashOutPutPath)


# 检测 Image 是否安装
try:
    from PIL import Image, ImageDraw
except ImportError:
    log('缺少Image模块，正在安装Image模块，请等待...')
    success = os.system('python -m pip install Image')
    if success == 0:
        log('Image模块安装成功.')
        from PIL import Image, ImageDraw
    else:
        log('Image安装失败，请手动在终端执行：\'python -m pip install Image\'重新安装.')
        quit()


# 检查icon是否存在，存在则返回地址
def check_icon():
    files = os.listdir(inputPath)
    image_path = ""
    for file_name in files:
        # 读取图片
        file_path = os.path.join(inputPath, file_name)
        image = Image.open(file_path)
        # 检测是否存在1024图片
        if image.size[0] == image.size[1] == 1024:
            image_path = file_path

    if len(image_path) <= 0:
        log('未找到尺寸 1024x1024 的图片')
        quit()

    return image_path


# 检查splash图片尺寸是否完整
def check_splash():
    files = os.listdir(inputPath)
    sizes = iosSplashSize + androidSplashSize
    for (w, h) in sizes:
        is_exist = False
        for file_name in files:
            # 获取文件，和目标尺寸对比
            file_path = os.path.join(inputPath, file_name)
            image = Image.open(file_path)
            if image.size[0] == w and image.size[1] == h:
                is_exist = True
                break

        if is_exist is False:
            log('尺寸 %dx%d 的启动图不存在' % (w, h))
            quit()


# 处理图片圆角
def circle_corner(image, radii):

    # 画圆（用于分离4个角）
    circle = Image.new('L', (radii * 2, radii * 2), 0)  # 创建一个黑色背景的画布
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, radii * 2, radii * 2), fill=255)  # 画白色圆形

    (w, h) = image.size

    # 画4个角（将整圆分离为4个部分）
    alpha = Image.new('L', image.size, 255)
    alpha.paste(circle.crop((0, 0, radii, radii)), (0, 0))  # 左上角
    alpha.paste(circle.crop((radii, 0, radii * 2, radii)), (w - radii, 0))  # 右上角
    alpha.paste(circle.crop((radii, radii, radii * 2, radii * 2)), (w - radii, h - radii))  # 右下角
    alpha.paste(circle.crop((0, radii, radii, radii * 2)), (0, h - radii))  # 左下角
    # alpha.show()

    image.putalpha(alpha)  # 白色区域透明可见，黑色区域不可见
    return image


# 生成iOS的icon
def create_ios_icon(image_path):

    print '开始配置 iOS icon'

    # 创建icon文件夹
    if os.path.exists(iosIconOutPutPath) is False:
        os.makedirs(iosIconOutPutPath)
        print '创建 ios AppIcon.appiconset 文件夹'

    # 获取图片
    icon = Image.open(image_path).convert("RGBA")

    # 保存图片信息的列表
    image_list = []

    # 生成iOS图片，并保存到指定路径
    for size in iosIconSize:
        # 原始尺寸
        original_size = int(size.split('@')[0])
        # 图片倍数
        multiply = int(size.split('@')[1][0:1])
        # 生成图片
        im = icon.resize((original_size * multiply, original_size * multiply), Image.BILINEAR)
        # 图片完整名称
        name = "icon%s.png" % size
        # 保存到路径
        im.save(iosIconOutPutPath + name, "png")
        # 加入JSON文件
        image_list.append({
            "idiom": ("ios-marketing" if original_size == 1024 else "iphone"),
            "size": "%dx%d" % (original_size, original_size),
            "filename": name,
            "scale": "%dx" % multiply
        })

    # 创建 content 文件
    content = {
        "images": image_list,
        "info": {
            "version": 1,
            "author": "xcode"
        }
    }

    # 打开文件，写入json数据
    f = open(iosIconOutPutPath + 'Contents.json', 'w')
    f.write(json.dumps(content))

    print 'iOS icon 配置完成'


# 生成Android的icon
def create_android_icon(image_path):

    print '开始配置 Android icon'

    # 获取图片
    icon = Image.open(image_path).convert("RGBA")

    # 生成Android圆形icon
    circle_icon = circle_corner(icon, radii=1024/2)
    index = 0
    for size in androidIconSize:
        # 压缩图片
        circle_im = circle_icon.resize((size, size), Image.BILINEAR)
        # 图片完整名称
        name = "mipmap-%s/ic_launcher_round.png" % androidNames[index]
        # 保存到路径
        circle_im.save(androidIconOutPutPath + name, "png")
        index = index + 1

    # 生成Android圆角矩形icon
    round_icon = circle_corner(icon, radii=180)
    index = 0
    for size in androidIconSize:
        # 压缩图片
        round_im = round_icon.resize((size, size), Image.BILINEAR)
        # 图片完整名称
        name = "mipmap-%s/ic_launcher.png" % androidNames[index]
        # 保存到路径
        round_im.save(androidIconOutPutPath + name, "png")
        index = index + 1

    print 'Android icon 配置完成'


# ios 启动图配置文件
splash_content = {
    "images": [
        {
            "extent": "full-screen",
            "idiom": "iphone",
            "subtype": "2688h",
            "filename": "launch1242x2688.png",
            "minimum-system-version": "12.0",
            "orientation": "portrait",
            "scale": "3x"
        },
        {
            "extent": "full-screen",
            "idiom": "iphone",
            "subtype": "1792h",
            "filename": "launch828x1792.png",
            "minimum-system-version": "12.0",
            "orientation": "portrait",
            "scale": "2x"
        },
        {
            "extent": "full-screen",
            "idiom": "iphone",
            "subtype": "2436h",
            "filename": "launch1125x2436.png",
            "minimum-system-version": "11.0",
            "orientation": "portrait",
            "scale": "3x"
        },
        {
            "extent": "full-screen",
            "idiom": "iphone",
            "subtype": "736h",
            "filename": "launch1242x2208.png",
            "minimum-system-version": "8.0",
            "orientation": "portrait",
            "scale": "3x"
        },
        {
            "extent": "full-screen",
            "idiom": "iphone",
            "subtype": "667h",
            "filename": "launch750x1334.png",
            "minimum-system-version": "8.0",
            "orientation": "portrait",
            "scale": "2x"
        },
        {
            "orientation": "portrait",
            "idiom": "iphone",
            "filename": "launch640x960.png",
            "extent": "full-screen",
            "minimum-system-version": "7.0",
            "scale": "2x"
        },
        {
            "extent": "full-screen",
            "idiom": "iphone",
            "subtype": "retina4",
            "filename": "launch640x1136.png",
            "minimum-system-version": "7.0",
            "orientation": "portrait",
            "scale": "2x"
        },
        {
            "orientation": "portrait",
            "idiom": "iphone",
            "filename": "launch320x480.png",
            "extent": "full-screen",
            "scale": "1x"
        },
        {
            "orientation": "portrait",
            "idiom": "iphone",
            "filename": "launch640x960.png",
            "extent": "full-screen",
            "scale": "2x"
        },
        {
            "orientation": "portrait",
            "idiom": "iphone",
            "filename": "launch640x1136.png",
            "extent": "full-screen",
            "subtype": "retina4",
            "scale": "2x"
        }
    ],
    "info": {
        "version": 1,
        "author": "xcode"
    }
}


# 生成iOS的启动图
def create_ios_splash():

    print '开始配置 ios splash'

    # 创建启动图文件夹
    if os.path.exists(iosSplashOutPutPath) is False:
        os.makedirs(iosSplashOutPutPath)
        print '创建 ios LaunchImage.launchimage 文件夹'

    # 获取所有文件
    files = os.listdir(inputPath)

    # 遍历保存图片
    for file_name in files:
        file_path = os.path.join(inputPath, file_name)
        image = Image.open(file_path)

        if image.size in iosSplashSize:
            # 图片完整名称
            name = "launch%dx%d.png" % (image.size[0], image.size[1])
            # 保存到路径
            image.save(iosSplashOutPutPath + name, "png")

    # 打开文件，写入json数据
    f = open(iosSplashOutPutPath + 'Contents.json', 'w')
    f.write(json.dumps(splash_content))

    print 'iOS splash 配置完成'


# 生成Android的启动图
def create_android_splash():

    print '开始配置 Android splash'

    # 获取文件夹下所有图片
    files = os.listdir(inputPath)

    # 遍历文件图片
    for file_name in files:

        file_path = os.path.join(inputPath, file_name)
        image = Image.open(file_path)

        # 找出指定文件的位置
        if image.size in androidSplashSize:
            index = androidSplashSize.index(image.size)
            # 创建不同分辨率文件夹
            dir_path = "%sdrawable-%s" % (androidSplashOutPutPath, androidNames[index])
            if os.path.exists(dir_path) is False:
                os.makedirs(dir_path)
                print '创建 %s' % dir_path

            # 保存图片到路径
            file_path = "%s/ic_launcher.png" % dir_path
            image.save(file_path, "png")

    print 'Android splash 配置完成'


# 开始检查icon
icon_path = check_icon()

# 开始检查启动图
check_splash()

# 生成 iOS icon
create_ios_icon(icon_path)

# 生成 Android icon
create_android_icon(icon_path)

# 生成 iOS Splash
create_ios_splash()

# 生成 Android Splash
create_android_splash()
