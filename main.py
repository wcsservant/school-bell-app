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
        self.root.geometry("450x730") # 컴포넌트 추가를 위해 세로 길이 확장
        
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

    def import_day_settings(self):
        target_day = self.copy_day_var.get()
        
        if target_day == "선택안함":
            # 1. 선택안함일 경우: 현재 화면의 1~11교시 값을 모두 빈칸으로 삭제
            for i in range(11):
                self.entries[i][0].delete(0, tk.END)
                self.entries[i][1].delete(0, tk.END)
            messagebox.showinfo("초기화 완료", "현재 요일의 시간 값이 모두 삭제되었습니다.\n\n※ 아래 '설정 저장' 버튼을 눌러야 완전히 적용됩니다.")
            
        else:
            # 2. 특정 요일일 경우: 해당 요일에 저장되어 있는 값을 현재 화면으로 복사
            target_data = self.schedule_data[target_day]
            for i in range(11):
                self.entries[i][0].delete(0, tk.END)
                self.entries[i][0].insert(0, target_data[i]["start"])
                
                self.entries[i][1].delete(0, tk.END)
                self.entries[i][1].insert(0, target_data[i]["end"])
            messagebox.showinfo("가져오기 완료", f"'{target_day}'의 설정값을 화면에 불러왔습니다.\n\n※ 아래 '설정 저장' 버튼을 눌러야 완전히 적용됩니다.")

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
        
        # 중단: 1~11교시 입력칸
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
        
        #가져오기 그룹
        copy_frame = tk.LabelFrame(self.root, text="다른 요일 값 가져오기", padx=10, pady=10)
        copy_frame.pack(pady=10, fill="x", padx=30)
        
        # 콤보박스에 들어갈 항목 설정
        self.copy_day_var = tk.StringVar(value="선택안함")
        copy_options = ["선택안함"] + self.days
        
        # 왼쪽: 레이블과 콤보박스
        left_subframe = tk.Frame(copy_frame)
        left_subframe.pack(side=tk.LEFT)
        tk.Label(left_subframe, text="가져올 요일:").pack(side=tk.LEFT, padx=(0, 5))
        copy_combo = ttk.Combobox(left_subframe, textvariable=self.copy_day_var, values=copy_options, state="readonly", width=10)
        copy_combo.pack(side=tk.LEFT)
        
        # 오른쪽: 가져오기 버튼
        tk.Button(copy_frame, text="가져오기", command=self.import_day_settings, bg="#f0f0f0").pack(side=tk.RIGHT)

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
                start_val = period["start"].strip()
                end_val = period["end"].strip()
                
                # "9:00", "9:0" 등의 입력을 "09:00" 포맷으로 자동 변환
                try:
                    if start_val and ":" in start_val:
                        h, m = start_val.split(":")
                        start_val = f"{int(h):02d}:{int(m):02d}"
                except:
                    pass
                
                try:
                    if end_val and ":" in end_val:
                        h, m = end_val.split(":")
                        end_val = f"{int(h):02d}:{int(m):02d}"
                except:
                    pass
                
                if start_val == current_hm:
                    self.play_bell("start")
                elif end_val == current_hm:
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