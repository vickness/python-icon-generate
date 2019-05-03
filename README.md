# python-icon-generate
react-native 自动配置替换图标和启动图，支持iOS和Android

## 使用方法
下载 icon.py 文件，放在项目根目录下

方法一：直接
执行脚本，path 为源文件夹路径，包含 icon 图标 和 启动图
 ```python
python icon.py path
```
方法二：在项目根目录下创建res文件夹，加入 icon 图标 和 启动图，执行脚本
```python
python icon.py
```


文件尺寸列表
```text
icon - 1024x1024

ios-launch - 320x480
ios-launch - 640x960
ios-launch - 640x1136
ios-launch - 750x1334
ios-launch - 828x1792
ios-launch - 1125x2436
ios-launch - 1242x2208
ios-launch - 1242x2688

android-launch - 320x480
android-launch - 480x800
android-launch - 720x1280
android-launch - 960x1600
android-launch - 1280x1920
```
