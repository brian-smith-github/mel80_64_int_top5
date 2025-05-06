# Standard Whisper run, no injection
import whisper
import torch
import numpy as np

#model = whisper.load_model("tiny")   # 75 Mb, fast, low accuracy
model = whisper.load_model("base")   # 145 Mb, fast
#model = whisper.load_model("small")  # 483 Mb,  bearable
#model = whisper.load_model("medium") # 1.5 Gb, slooow

# load audio and pad/trim it to fit 30 seconds

audio = whisper.load_audio("/tmp/a16.wav")
audio = whisper.pad_or_trim(audio)

mel = whisper.log_mel_spectrogram(audio)
print(mel.size())
torch.save(mel, 'file.pt')


#mel=torch.load('file2.pt')   # load the alternative version!


# detect the spoken language
#_, probs = model.detect_language(mel)
#print(f"Detected language: {max(probs, key=probs.get)}")



# decode the audio
options = whisper.DecodingOptions(fp16=False,language="en")
result = whisper.decode(model, mel, options)

# print the recognized text
print(result.text)
