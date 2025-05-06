# Experimenting with lightweight feature extraction front-end for Whisper STT

(this is a quick brain-dump of experimental stuff, excuse the typos etc)

This code is used for experiments in how much abuse can be given to 
the feature-data being fed into the Whisper back-end neural net recognizer,
while still maintaining a low word-error rate (WER).

## How to use:
- The 'radio4sample' script quickly downloads a 6 second buffered snippet of
live talk-radio to use as an infinite stream of test data, which is useful, and
converts it into /tmp/a16.wav file in the regular format that Whisper takes.
(16000 samples/second, 16 bit PCM audio),
and also /tmp/a64.raw (6400 samples/second bit PCM audio) as used by the
alternative feature extraction code.

- The 'doit' script runs the 'go.c' C code which reads /tmp/a64.raw and 
generates alternative log-mel feature
data, puts that into the regular format the the Whisper neural-net  back-end
and does STT on it.
It then runs the full regular Whisper pipeline on the /tmp/a16.wav  16000 samp/sec file for comparison.

- edit the go.py script to choose which Whisper model to use. Smaller models
are faster, but less accurate. the 'medium' 1.5 GB model gives the most
accurate results but the 483 MB 'small' model is generally good enough.
The script should automatically download the required model on first run if
it is now aleady cached, which might take a few minutes but generally the
transcription gets done in a few seconds.

# Things I've discovered:
- The sample rate of the audio can definitely be dropped from 16000samps/sec 
down to 6400 samps/sec without any significant WER rise. This is useful
as it allows a nice power-of-2 FFT in the feature extractor. Surprisingly,
if anything the transcriptions at this sample rate seem _better_ than regular
whisper transcriptions at the regular sample rate! I imagine this is because
irrelivent noise in the audio above the 3200Hz top-end of dominant formant
freqencies is being filtered out. (Nyquist)
- pre-emphasis level doesn't seem to make any difference, allowing for use
of 'heavy' 1.0 pre-emphasis (compared to usual 0.975 or 15/16 traditionally
used) which makes the process much more computationally efficient and elegant, 
it just becomes delta-coding (subtract previous sample from current one).
- 20ms frame width instead of regular 25ms is absolutely fine and has
no significant impact.
- The overall noise-floor for the sample can be much lower than is used
by regular Whisper feature extractor. Instead of 8dB, I go down to 4.5dB.
This might work because the higher pre-emphais is flattening out the
natural spectral tilt of the signsl more completely, but I'm not sure.
(normally the bass has significantly more energy than the mids and highs,
drowning out the signal where the formants live,  pre-emphasis fixes this.)

- FFT is better than LPC - decades of speech recognition research bears
this out but it took me a while to come around to this. LPC is too crude an
initial compression method and does not easily allow noise removal. Pity.
- Windowing the data before the FFT is _essential_, and skipping it gives 
significant rise in WER. This stage simply can't be skipped.
- There are better window functions than Hann. This is especially crucial when
using a narrower-than-normal 20ms frame width. I have adpoted the windowing
function used in the LPCNet audio codec, which has much less cut-off at the
boundaries than Hann, and yeilds improved results.
- Integer processing is fine, no need for floating-point.
- Integer resolution - the bit resolution for:

  a) the sample data

  b) the window data 

  c) The FFT sine/cosin 'twiddle' data

    Can all be dropped to surprisingly low levels. I've been experimenting with
this in the same way the LLM folks are toying with low-bit quantized weights, 
seeing how low they can go while maintaining decent results.
Levels as low as 4 bits (scaled) for the sample data,
2 bits for the window function
and 2 bits for the FFT twiddles seem acceptable, paving the way for potential 8-bit feature extraction!
- Conversion to cepstrum data via DCT is a bad idea - more recent research 
bears this out, Whisper forgoes DCT and works on high-dimensional raw log-mel bin data (80 mel bins), which is computationally more intense but acceptable 
with modern hardware.
- Mel-bins are _not_ needed as a process step. When the number of FFT output bins is relatively near the number of expected mel output bins, it doesn't make
much sense to do a conversion really.
- All you _really_ need to know are where/what the top 5 (bounded) FFT bins are.
This is an interesting discovery, and ties in with the historical use of
10th-order LPC-based voice codecs (e.g. CELP, MELP, Speex etc) which simiarly
code speech frames in the frequency domain as a curve with (up to) 5 peaks 
and 5 troughs. (i.e. the 5 complex-conjugate root-pairs for a order-10 polynomial).
FFT can provide this data in a more computationlly elegant,accurate, efficent 
and noise-tolerant manner than LPC.
The bounding I use is roughly based on mel-scale, with no bounding of lower bin frequencies, scaling up to wide bounds on the higher end high-freqency bins.
