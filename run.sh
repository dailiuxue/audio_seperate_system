#!/bin/sh
#1.安装环境以来
pip install -r requirement.txt -i https://mirrors.aliyun.com/pypi/simple/

#2.启动模型推理演示服务
python gradio_demucs.py > gradio_demucs.log 2>&1 &

#2.启动用户注册登录服务
python app.py > app.log 2>&1 &

#  * Running on http://127.0.0.1:5000
echo '服务地址：http://127.0.0.1:5000'
