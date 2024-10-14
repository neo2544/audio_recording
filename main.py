from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import sounddevice as sd
import numpy as np
import threading
import wave
import os
import datetime
import glob
import re

app = FastAPI()

# 녹음 파일을 저장할 폴더 경로를 지정합니다.
RECORDINGS_FOLDER = 'recordings'
os.makedirs(RECORDINGS_FOLDER, exist_ok=True)

class AudioRecorder:
    def __init__(self):
        self.is_recording = False
        self.frames = []
        self.stream = None
        self.device_index = None
        self.device_name = None  # 디바이스 이름 저장
        self.samplerate = None
        self.channels = None
        self.lock = threading.Lock()
        self.file_path = None  # 파일 경로를 저장하기 위한 변수

    def start_recording(self, device_index):
        with self.lock:
            if self.is_recording:
                raise Exception("이미 녹음이 진행 중입니다.")
            self.device_index = device_index
            device_info = sd.query_devices(device_index, 'input')
            self.device_name = device_info['name']  # 디바이스 이름 저장
            self.samplerate = int(device_info['default_samplerate'])
            self.channels = device_info['max_input_channels']
            self.frames = []
            self.stream = sd.InputStream(device=device_index,
                                         channels=self.channels,
                                         samplerate=self.samplerate,
                                         callback=self.callback,
                                         dtype='int16')
            self.stream.start()
            self.is_recording = True

    def stop_recording(self):
        with self.lock:
            if not self.is_recording:
                raise Exception("녹음이 진행 중이 아닙니다.")
            self.stream.stop()
            self.stream.close()
            self.stream = None
            self.is_recording = False

            # 디바이스 이름을 파일명에 포함시키기 위해 안전한 문자열로 변환합니다.
            sanitized_device_name = self.sanitize_filename(self.device_name)
            if not sanitized_device_name:
                raise Exception("디바이스 이름이 유효하지 않아 파일을 저장할 수 없습니다.")

            # 녹음된 데이터를 지정된 폴더에 저장합니다.
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_filename = f"{sanitized_device_name}_{timestamp}.wav"
            self.file_path = os.path.join(RECORDINGS_FOLDER, unique_filename)
            wf = wave.open(self.file_path, 'wb')
            wf.setnchannels(self.channels)
            wf.setsampwidth(2)  # 'int16'은 2바이트입니다.
            wf.setframerate(self.samplerate)
            wf.writeframes(b''.join(self.frames))
            wf.close()
            return self.file_path

    def callback(self, indata, frames, time, status):
        if status:
            print(status)
        self.frames.append(indata.tobytes())

    def sanitize_filename(self, filename):
        # 파일명에 사용할 수 없는 문자 제거
        sanitized = re.sub(r'[\\/*?:"<>|]', "_", filename)
        sanitized = sanitized.strip()
        # 파일명이 너무 길거나 빈 문자열인 경우 처리
        if len(sanitized) == 0 or len(sanitized) > 255:
            return None
        return sanitized

# 오디오 재생 관리 클래스 추가
class AudioPlayer:
    def __init__(self):
        self.is_playing = False
        self.play_thread = None
        self.lock = threading.Lock()

    def play_audio(self, audio_data, samplerate, device_index):
        with self.lock:
            if self.is_playing:
                raise Exception("이미 오디오가 재생 중입니다.")
            self.is_playing = True

        def playback():
            try:
                sd.play(audio_data, samplerate=samplerate, device=device_index)
                sd.wait()  # 재생이 끝날 때까지 대기
            except Exception as e:
                print(f"오디오 재생 중 오류 발생: {e}")
            finally:
                with self.lock:
                    self.is_playing = False

        self.play_thread = threading.Thread(target=playback)
        self.play_thread.start()

    def stop_audio(self):
        with self.lock:
            if not self.is_playing:
                raise Exception("오디오가 재생 중이 아닙니다.")
            sd.stop()
            self.is_playing = False

recorder = AudioRecorder()
audio_player = AudioPlayer()

@app.post("/start_recording")
def start_recording(device_index: int):
    try:
        recorder.start_recording(device_index)
        return {"message": "녹음을 시작했습니다.", "device_index": device_index, "device_name": recorder.device_name}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/stop_recording")
def stop_recording():
    try:
        audio_file = recorder.stop_recording()
        return FileResponse(audio_file, media_type='audio/wav', filename=os.path.basename(audio_file))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/audio_devices")
def get_audio_devices():
    try:
        # sounddevice 라이브러리를 다시 초기화하여 장치 목록을 최신화합니다.
        sd._terminate()
        sd._initialize()
        devices = sd.query_devices()
        input_devices = []
        output_devices = []
        for idx, device in enumerate(devices):
            device_info = {
                'index': idx,
                'name': device['name'],
                'max_input_channels': device['max_input_channels'],
                'max_output_channels': device['max_output_channels'],
            }
            if device['max_input_channels'] > 0:
                input_devices.append(device_info)
            if device['max_output_channels'] > 0:
                output_devices.append(device_info)
        return {
            'input_devices': input_devices,
            'output_devices': output_devices
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.get("/recordings")
def list_recordings():
    try:
        files = glob.glob(os.path.join(RECORDINGS_FOLDER, '*.wav'))
        # 파일의 수정 시간을 기준으로 내림차순 정렬
        files.sort(key=os.path.getmtime, reverse=True)
        file_list = [os.path.basename(f) for f in files]
        return {"recordings": file_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/delete_recording")
def delete_recording(filename: str):
    try:
        # 파일 이름에서 디렉토리 경로 제거
        safe_filename = os.path.basename(filename)
        file_path = os.path.join(RECORDINGS_FOLDER, safe_filename)

        # 파일이 존재하는지 확인
        if not os.path.isfile(file_path):
            raise HTTPException(status_code=404, detail="파일을 찾을 수 없습니다.")

        # 파일 삭제
        os.remove(file_path)

        return {"message": f"{safe_filename} 파일이 삭제되었습니다."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 오디오 재생 API 수정
@app.post("/play_audio")
def play_audio(filename: str, device_index: int):
    try:
        file_path = os.path.join(RECORDINGS_FOLDER, filename)
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="파일을 찾을 수 없습니다.")

        # 오디오 파일을 읽어옵니다.
        wf = wave.open(file_path, 'rb')
        samplerate = wf.getframerate()
        channels = wf.getnchannels()
        sampwidth = wf.getsampwidth()
        dtype = 'int16' if sampwidth == 2 else 'int32'
        data = wf.readframes(wf.getnframes())
        wf.close()

        # 오디오 데이터를 numpy 배열로 변환합니다.
        audio_data = np.frombuffer(data, dtype=dtype)

        # 다중 채널 오디오의 경우 reshape 필요
        if channels > 1:
            audio_data = audio_data.reshape(-1, channels)

        audio_player.play_audio(audio_data, samplerate, device_index)
        return {"message": f"{filename} 파일을 재생합니다.", "device_index": device_index}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 오디오 재생 중지 API 추가
@app.post("/stop_audio")
def stop_audio():
    try:
        audio_player.stop_audio()
        return {"message": "오디오 재생을 중지했습니다."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))



# **경로 정의 순서 중요**
# 녹음된 파일 서빙을 위한 설정을 먼저 마운트합니다.
app.mount("/recordings", StaticFiles(directory=RECORDINGS_FOLDER), name="recordings")

# 정적 파일 서빙을 위한 설정
app.mount("/", StaticFiles(directory="static", html=True), name="static")