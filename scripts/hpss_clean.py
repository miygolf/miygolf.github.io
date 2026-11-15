"""Keep only the percussive part (zips, fabric) of a clip's audio; drop harmonic content (crying, hum)."""
import sys, numpy as np, librosa, soundfile as sf
src, dst = sys.argv[1], sys.argv[2]
margin = float(sys.argv[3]) if len(sys.argv) > 3 else 3.0
y, sr = librosa.load(src, sr=48000, mono=False)
y = np.atleast_2d(y)
out = []
for ch in y:
    D = librosa.stft(ch, n_fft=4096, hop_length=512)
    H, P = librosa.decompose.hpss(D, kernel_size=(31, 31), margin=(1.0, margin))
    p = librosa.istft(P, hop_length=512, length=len(ch))
    out.append(p)
out = np.stack(out, 0).T
# high-pass below 150 Hz rumble is handled later in ffmpeg
sf.write(dst, out, sr, subtype='PCM_24')
print('ok', out.shape, float(np.abs(out).max()))
