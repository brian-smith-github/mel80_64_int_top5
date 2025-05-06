# Injection-attack version

import whisper
import torch
import numpy as np

#model = whisper.load_model("tiny")   # 75 Mb, fast, low accuracy
#model = whisper.load_model("base")   # 145 Mb, fast
model = whisper.load_model("small")  # 483 Mb,  bearable
#model = whisper.load_model("medium") # 1.5 Gb, slooow, but most accurate

mel=torch.load('file2.pt')   # load the alternative version!

# decode the audio
options = whisper.DecodingOptions(fp16=False,language="en")
result = whisper.decode(model, mel, options)

# print the recognized text
print(result.text)
