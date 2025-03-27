import os
import gradio as gr
from scipy.io.wavfile import write


def inference(audio):
  os.makedirs("out", exist_ok=True)
  write('test.wav', audio[0], audio[1])
  os.system("python -m demucs.separate -n htdemucs --two-stems=vocals -d cpu test.wav -o out")
  return "./out/htdemucs/test/vocals.wav","./out/htdemucs/test/no_vocals.wav"
    
title = "语音分类系统的设计与实现项目演示"
description = "功能是基于Demucs将歌曲中的伴奏和人声分离，可以上传歌曲文件，也可以实时播放音乐.\n项目部署在笔记本上，使用的M2 CPU进行实时推理"

examples=[['稻香.mp3']]
gr.Interface(
    inference, 
    gr.Audio(type="numpy", label="Input"),
    [gr.Audio(type="filepath", label="Vocals"),gr.Audio(type="filepath", label="No Vocals / Instrumental")],
    title=title,
    description=description,
    examples=examples
).launch()
#).launch(server_port=6666)
