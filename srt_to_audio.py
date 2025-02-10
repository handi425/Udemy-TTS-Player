import asyncio
import edge_tts
import pysrt
import os
from pathlib import Path
import time
from pydub import AudioSegment

VOICE_LIST = {
    "pria": "id-ID-ArdiNeural",
}

async def text_to_speech(text, output_file, voice_type="pria", rate="+0%", volume="+0%"):
    """Mengkonversi teks ke audio menggunakan Edge TTS"""
    communicate = edge_tts.Communicate(text, VOICE_LIST[voice_type], rate=rate, volume=volume)
    await communicate.save(output_file)

def calculate_speech_rate(text_length, duration_ms, global_speed=1):
    """Menghitung rate berdasarkan panjang teks dan durasi yang diinginkan"""
    # Pastikan durasi valid
    duration_ms = max(duration_ms, 1000)  # Minimal 1 detik
    
    # Base rate yang lebih rendah (100 wpm) untuk kontrol lebih baik
    base_words_per_minute = 100
    # Estimasi jumlah kata (dengan asumsi rata-rata 5 karakter per kata)
    estimated_words = text_length / 5
    # Durasi dalam menit
    duration_minutes = duration_ms / (1000 * 60)
    # Hitung target words per minute dengan faktor kecepatan global
    target_wpm = (estimated_words / duration_minutes) * global_speed
    # Hitung persentase perubahan
    rate_change = int((target_wpm / base_words_per_minute - 1) * 100)
    # Batasi perubahan rate maksimum
    rate_change = min(max(rate_change, -30), 150)  # Batasi antara -30% sampai +150%
    return f"{rate_change:+d}%"

async def convert_srt_to_audio(srt_file, output_dir="output", voice_type="pria", global_speed=1):
    """Mengkonversi file SRT ke audio menggunakan TTS"""
    
    # Buat direktori output jika belum ada
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Baca file SRT
    subs = pysrt.open(srt_file)
    
    print("Memulai konversi teks ke audio...")
    
    # Proses setiap subtitle
    for i, sub in enumerate(subs):
        output_file = os.path.join(output_dir, f"segment_{i+1}.mp3")
        duration = (sub.end.seconds - sub.start.seconds) * 1000  # Konversi ke milidetik
        
        print(f"Memproses segment {i+1}: {sub.text}")
        
        # Hitung rate berdasarkan panjang teks dan durasi dengan faktor kecepatan global
        rate = calculate_speech_rate(len(sub.text), duration, global_speed)
        
        # Konversi teks ke audio dengan penyesuaian kecepatan
        await text_to_speech(sub.text, output_file, voice_type, rate=rate)
        print(f"Durasi target: {duration}ms, Rate: {rate}")

    # Buat file tunggal
    print("\nMembuat file audio tunggal...")
    combined_file = os.path.join(output_dir, "combined_output.mp3")
    
    # Gabungkan semua teks dengan timing yang sesuai
    combined_text = " ".join([sub.text for sub in subs])
    await text_to_speech(combined_text, combined_file, voice_type)
    print(f"File audio tunggal telah dibuat: {combined_file}")

if __name__ == "__main__":
    # Konversi SRT ke audio dengan pilihan suara dan kecepatan global
    output_dirs = {
        "pria": "output_pria_faster",
    }
    
    # Gunakan kecepatan global 1.2x untuk mempercepat output
    global_speed = 1  # Sedikit lebih lambat untuk hasil yang lebih natural
    
    # Buat konversi dengan dua jenis suara
    for voice_type, output_dir in output_dirs.items():
        print(f"\nMemulai konversi dengan suara {voice_type} (kecepatan {global_speed}x)...")
        asyncio.run(convert_srt_to_audio(
            "1. Introduction.srt",
            output_dir=output_dir,
            voice_type=voice_type,
            global_speed=global_speed
        ))
        
    print("\nKonversi selesai! Cek folder output_pria_faster dan output_wanita_faster untuk hasil konversi.")
