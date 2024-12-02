from flask import Flask, request, render_template, send_file, jsonify
from moviepy.editor import VideoFileClip, AudioFileClip
import speech_recognition as sr
from googletrans import Translator
from gtts import gTTS
from pydub import AudioSegment
import os

app = Flask(__name__)

@app.route('/')
def upload_form():
    return render_template('upload.html')

@app.route('/process_video', methods=['POST'])
def process_video():
    if 'video' not in request.files:
        return jsonify({'error': 'No video file provided'}), 400

    video_file = request.files['video']
    video_path = 'original_video.mp4'
    video_file.save(video_path)

    # Step 2: Extract the audio from the video
    video_clip = VideoFileClip(video_path)
    audio_path = 'extracted_audio.wav'
    video_clip.audio.write_audiofile(audio_path)

    # Step 3: Transcribe the audio
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio_data = recognizer.record(source)
        text = recognizer.recognize_google(audio_data)

    # Step 4: Translate the transcription to the target language (e.g., Tamil)
    translator = Translator()
    translated_text = translator.translate(text, src='en', dest='ta').text

    # Step 5: Convert the translated text to speech
    tts = gTTS(translated_text, lang='ta')
    translated_audio_path = 'translated_audio.mp3'
    tts.save(translated_audio_path)

    audio = AudioSegment.from_mp3(translated_audio_path)
    translated_audio_wav_path = 'translated_audio.wav'
    audio.export(translated_audio_wav_path, format='wav')

    translated_audio_clip = AudioFileClip(translated_audio_wav_path)
    final_video = video_clip.set_audio(translated_audio_clip)
    final_output_path = 'final_output.mp4'
    final_video.write_videofile(final_output_path, codec='libx264', audio_codec='aac')

    # Cleanup temporary files
    video_clip.close()
    os.remove(audio_path)
    os.remove(translated_audio_path)
    os.remove(translated_audio_wav_path)

    return send_file(final_output_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
