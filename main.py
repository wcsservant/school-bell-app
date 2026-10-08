import tkinter as tk
from tkinter import ttk, messagebox
import json
import time
from datetime import datetime
import os
import winsound

class SchoolBellApp:
    def __init__(self, root):
        self.root = root
        self.root.title("WCS 종소리 프로그램")
        self.root.geometry("450x650")
        
        # 설정 저장 파일
        self.settings_file = "bell_settings.json"
        self.days = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"]
        self.current_day_var = tk.StringVar(value=self.days[0])
        self.schedule_data = self.load_settings()
        
        self.entries = []
        
        self.build_ui()
        self.update_ui_for_day()
        self.check_time()

    def load_settings(self):
        # 기존 설정 파일이 있으면 불러오고, 없으면 기본값 생성
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                pass
        return {day: [{"start": "", "end": ""} for _ in range(11)] for day in self.days}

    def save_settings(self):
        # 현재 화면에 입력된 값을 데이터에 먼저 업데이트
        day = self.current_day_var.get()
        for i in range(11):
            self.schedule_data[day][i]["start"] = self.entries[i][0].get()
            self.schedule_data[day][i]["end"] = self.entries[i][1].get()
            
        # 파일로 저장
        with open(self.settings_file, "w", encoding="utf-8") as f:
            json.dump(self.schedule_data, f, ensure_ascii=False, indent=4)
        messagebox.showinfo("저장 완료", "시간 설정이 저장되었습니다.\n(bell_settings.json 파일에 저장됨)")

    def on_day_change(self, event=None):
        # 요일이 바뀔 때 이전 요일의 데이터를 임시 저장하고 새 요일 데이터를 화면에 표시
        self.update_ui_for_day()

    def update_ui_for_day(self):
        day = self.current_day_var.get()
        day_data = self.schedule_data[day]
        for i in range(11):
            self.entries[i][0].delete(0, tk.END)
            self.entries[i][0].insert(0, day_data[i]["start"])
            self.entries[i][1].delete(0, tk.END)
            self.entries[i][1].insert(0, day_data[i]["end"])

    def build_ui(self):
        # 상단: 요일 선택 및 현재 시간
        top_frame = tk.Frame(self.root)
        top_frame.pack(pady=10)
        
        tk.Label(top_frame, text="요일 선택:").grid(row=0, column=0, padx=5)
        day_combo = ttk.Combobox(top_frame, textvariable=self.current_day_var, values=self.days, state="readonly")
        day_combo.grid(row=0, column=1, padx=5)
        day_combo.bind("<<ComboboxSelected>>", self.on_day_change)
        
        self.clock_label = tk.Label(self.root, text="현재 시간: 00:00:00", font=("Helvetica", 16, "bold"))
        self.clock_label.pack(pady=5)
        
        # 중단: 1~8교시 입력칸
        mid_frame = tk.Frame(self.root)
        mid_frame.pack(pady=10)
        
        tk.Label(mid_frame, text="교시").grid(row=0, column=0, padx=10)
        tk.Label(mid_frame, text="시작벨 (HH:MM)").grid(row=0, column=1, padx=10)
        tk.Label(mid_frame, text="종료벨 (HH:MM)").grid(row=0, column=2, padx=10)
        
        for i in range(11):
            tk.Label(mid_frame, text=f"{i+1}교시").grid(row=i+1, column=0, pady=5)
            start_entry = tk.Entry(mid_frame, width=10, justify="center")
            start_entry.grid(row=i+1, column=1, pady=5)
            end_entry = tk.Entry(mid_frame, width=10, justify="center")
            end_entry.grid(row=i+1, column=2, pady=5)
            self.entries.append((start_entry, end_entry))
            
        # 하단: 안내 문구 및 저장 버튼
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="설정 저장", command=self.save_settings, width=20, bg="#d0e8f2").pack(pady=5)
        
        info_text = "시간 입력 예시: 09:00 (24시간제)\n프로그램과 같은 폴더에 start.wav, end.wav 파일을\n넣어두면 해당 음악이 재생됩니다. (없으면 기본 비프음)"
        tk.Label(self.root, text=info_text, fg="#555555", justify="center").pack(pady=10)

    def check_time(self):
        now = datetime.now()
        current_time_str = now.strftime("%H:%M:%S")
        self.clock_label.config(text=f"현재 시간: {current_time_str}")
        
        # 매 분 00초 정각에만 알람 확인
        if now.second == 0:
            weekday_idx = now.weekday()
            today_str = self.days[weekday_idx]
            today_schedule = self.schedule_data.get(today_str, [])
            
            current_hm = now.strftime("%H:%M")
            
            for period in today_schedule:
                if period["start"] == current_hm:
                    self.play_bell("start")
                elif period["end"] == current_hm:
                    self.play_bell("end")
                    
        # 1초(1000ms)마다 시계 갱신
        self.root.after(1000, self.check_time)

    def play_bell(self, type):
        filename = "start.wav" if type == "start" else "end.wav"
        if os.path.exists(filename):
            # 외부 wav 파일이 있으면 비동기로 재생 (프로그램 멈춤 방지)
            winsound.PlaySound(filename, winsound.SND_FILENAME | winsound.SND_ASYNC)
        else:
            # 파일이 없으면 기본 비프음 발생 (시작벨은 높은음, 종료벨은 낮은음)
            freq = 1000 if type == "start" else 600
            winsound.Beep(freq, 2000)

if __name__ == "__main__":
    root = tk.Tk()
    app = SchoolBellApp(root)
    root.mainloop()