from pydub import AudioSegment
from pydub.silence import split_on_silence
from pathlib import Path
import time

start_time = time.time()
print("1) Starting audio split process...")

print("2) Loading MP3 file...")
audio = AudioSegment.from_mp3("C:\Temp\\rimas-infantis.mp3")

print(f"3) File loaded. Duration: {len(audio) / 1000:.2f} seconds")

print("4) Detecting silence and splitting audio...")
chunks = split_on_silence(
    audio,
    min_silence_len=1200,   # 1.2s of silence
    silence_thresh=audio.dBFS - 14,
    keep_silence=300
)

total_chunks = len(chunks)
print(f"5) Split complete. Total chunks found: {total_chunks}")

output_dir = Path("output")
output_dir.mkdir(exist_ok=True)
print(f"6) Output directory ready: {output_dir.resolve()}")

print("7) Exporting chunks...")

for i, chunk in enumerate(chunks, start=1):
    file_name = output_dir / f"musica_{i}.mp3"
    print(f"   ... Exporting chunk {i} of {total_chunks} -> {file_name.name}")
    chunk.export(file_name, format="mp3")

end_time = time.time()
elapsed = end_time - start_time

print("9) Done!")
print(f"10) Total time: {elapsed:.2f} seconds")
