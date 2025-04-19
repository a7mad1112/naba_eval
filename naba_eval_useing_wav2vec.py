!pip install noisereduce transformers librosa soundfile torchaudio jiwer
!pip install pydub
!apt install ffmpeg

import os
import librosa
import numpy as np
import re
import torch
import noisereduce as nr
from transformers import pipeline
from jiwer import wer
from pydub import AudioSegment
from tqdm import tqdm

# 🧠 Load ASR model
device = 0 if torch.cuda.is_available() else -1
asr_pipeline = pipeline(
    "automatic-speech-recognition",
    model="elgeish/wav2vec2-large-xlsr-53-arabic",
    device=device
)

# 🌍 Buckwalter to Arabic map
def buckwalter_to_arabic(text):
    buck2arab = {
        "A": "ا", "b": "ب", "t": "ت", "v": "ث", "j": "ج", "H": "ح", "x": "خ",
        "d": "د", "r": "ر", "z": "ز", "s": "س", "E": "ع", "g": "غ", "f": "ف",
        "q": "ق", "k": "ك", "l": "ل", "m": "م", "n": "ن", "h": "ه", "w": "و",
        "y": "ي", "T": "ط", "Z": "ظ", "S": "ص", "D": "ض", "Y": "ى", "e": "ة",
        "a": "َ", "u": "ُ", "i": "ِ", "o": "ٌ", "~": "ّ", "’": "ء", "'": "أ",
        ">": "إ", "<": "ا", "|": "آ", "}": "ئ", "&": "ؤ", "$": "ش", "`": "ً",
        "{": "ئ", ":": ":", "\"": "\"", " ": " ", "\n": "\n"
    }
    return ''.join([buck2arab.get(c, '') for c in text])

# 🧹 Clean Buckwalter text
def clean_buckwalter(text):
    return re.sub(r"[^A-Za-z\$\>\<\{\}\&\~\|\'\: ]", "", text)

# 🎵 Process single file
def transcribe_audio(file_path):
    audio = AudioSegment.from_mp3(file_path).set_channels(1).set_frame_rate(16000)
    samples = np.array(audio.get_array_of_samples()).astype(np.float32) / (2**15)
    trimmed, _ = librosa.effects.trim(samples)
    denoised = nr.reduce_noise(y=trimmed, sr=16000)
    normalized = librosa.util.normalize(denoised)
    result = asr_pipeline(normalized)
    text = result['text']
    return buckwalter_to_arabic(clean_buckwalter(text))

# 📖 سورة النبأ كاملة (منقحة بدقة عالية حسب المصحف)
an_naba_verses = [
    "عَمَّ يَتَسَاءَلُونَ", "عَنِ النَّبَإِ الْعَظِيمِ", "الَّذِي هُمْ فِيهِ مُخْتَلِفُونَ",
    "كَلَّا سَيَعْلَمُونَ", "ثُمَّ كَلَّا سَيَعْلَمُونَ", "أَلَمْ نَجْعَلِ الْأَرْضَ مِهَادًا",
    "وَالْجِبَالَ أَوْتَادًا", "وَخَلَقْنَاكُمْ أَزْوَاجًا", "وَجَعَلْنَا نَوْمَكُمْ سُبَاتًا",
    "وَجَعَلْنَا اللَّيْلَ لِبَاسًا", "وَجَعَلْنَا النَّهَارَ مَعَاشًا", "وَبَنَيْنَا فَوْقَكُمْ سَبْعًا شِدَادًا",
    "وَجَعَلْنَا سِرَاجًا وَهَّاجًا", "وَأَنْزَلْنَا مِنَ الْمُعْصِرَاتِ مَاءً ثَجَّاجًا",
    "لِنُخْرِجَ بِهِ حَبًّا وَنَبَاتًا", "وَجَنَّاتٍ أَلْفَافًا", "إِنَّ يَوْمَ الْفَصْلِ كَانَ مِيقَاتًا",
    "يَوْمَ يُنفَخُ فِي الصُّورِ فَتَأْتُونَ أَفْوَاجًا", "وَفُتِحَتِ السَّمَاءُ فَكَانَتْ أَبْوَابًا",
    "وَسُيِّرَتِ الْجِبَالُ فَكَانَتْ سَرَابًا", "إِنَّ جَهَنَّمَ كَانَتْ مِرْصَادًا",
    "لِلطَّاغِينَ مَآبًا", "لَابِثِينَ فِيهَا أَحْقَابًا", "لَا يَذُوقُونَ فِيهَا بَرْدًا وَلَا شَرَابًا",
    "إِلَّا حَمِيمًا وَغَسَّاقًا", "جَزَاءً وِفَاقًا", "إِنَّهُمْ كَانُوا لَا يَرْجُونَ حِسَابًا",
    "وَكَذَّبُوا بِآيَاتِنَا كِذَّابًا", "وَكُلَّ شَيْءٍ أَحْصَيْنَاهُ كِتَابًا",
    "فَذُوقُوا فَلَنْ نَزِيدَكُمْ إِلَّا عَذَابًا", "إِنَّ لِلْمُتَّقِينَ مَفَازًا", "حَدَائِقَ وَأَعْنَابًا",
    "وَكَوَاعِبَ أَتْرَابًا", "وَكَأْسًا دِهَاقًا", "لَا يَسْمَعُونَ فِيهَا لَغْوًا وَلَا كِذَّابًا",
    "جَزَاءً مِّن رَّبِّكَ عَطَاءً حِسَابًا", "رَّبِّ السَّمَاوَاتِ وَالْأَرْضِ وَمَا بَيْنَهُمَا الرَّحْمَٰنِ لَا يَمْلِكُونَ مِنْهُ خِطَابًا",
    "يَوْمَ يَقُومُ الرُّوحُ وَالْمَلَائِكَةُ صَفًّا لَّا يَتَكَلَّمُونَ إِلَّا مَنْ أَذِنَ لَهُ الرَّحْمَٰنُ وَقَالَ صَوَابًا",
    "ذَٰلِكَ الْيَوْمُ الْحَقُّ ۖ فَمَن شَاءَ اتَّخَذَ إِلَىٰ رَبِّهِ مَآبًا",
    "إِنَّا أَنذَرْنَاكُمْ عَذَابًا قَرِيبًا يَوْمَ يَنظُرُ الْمَرْءُ مَا قَدَّمَتْ يَدَاهُ وَيَقُولُ الْكَافِرُ يَا لَيْتَنِي كُنتُ تُرَابًا"
]

# 🧪 Main Evaluation
root_dir = "./an-naba"
reciters = [d for d in os.listdir(root_dir) if os.path.isdir(os.path.join(root_dir, d)) and not d.startswith('.')]

for reciter in reciters:
    print(f"\n🎙️ Reciter: {reciter}")
    reciter_path = os.path.join(root_dir, reciter)
    total_wer = 0

    for i in tqdm(range(1, 41)):
        print(f"Current working directory: {os.getcwd()}")
        file_path = os.path.join(reciter_path, f"{i}.mp3")
        print(f"Accessing file: {file_path}")
        pred = transcribe_audio(file_path)
        ref = an_naba_verses[i - 1]
        score = wer(ref, pred)
        total_wer += score

        print(f"\n📌 Ayah {i}")
        print(f"✅ Reference : {ref}")
        print(f"🧠 Predicted : {pred}")
        print(f"📉 WER       : {score:.2%}")

    avg_wer = total_wer / 40
    print(f"\n📊 Average WER for {reciter}: {avg_wer:.2%}")

