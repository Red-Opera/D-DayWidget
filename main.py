import tkinter as tk
import json, os, uuid, sys, winreg
from datetime import datetime
from pathlib import Path
from event_frame import EventFrame

# --- 자동 실행 등록 (Windows 레지스트리) ---
def add_to_startup():
    """
    컴퓨터 부팅 시 자동으로 실행되도록 레지스트리에 등록.
    콘솔창이 뜨지 않도록 pythonw.exe 사용.
    """
    try:
        script_path = os.path.abspath(sys.argv[0])
        # 만약 sys.executable이 "python.exe"라면 "pythonw.exe"로 변경
        executable = sys.executable
        
        if "python.exe" in executable.lower():
            executable = executable.replace("python.exe", "pythonw.exe")

        reg_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        key_name = "MyTkinterApp"
        
        reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_SET_VALUE)
        command = f'"{executable}" "{script_path}"'
        
        winreg.SetValueEx(reg_key, key_name, 0, winreg.REG_SZ, command)
        winreg.CloseKey(reg_key)
        
        print("자동 실행 등록 성공!")
        
    except Exception as e:
        print("자동 실행 등록 실패:", e)

# 필요하다면 주석 해제하여 부팅 시 자동 실행 등록
# add_to_startup()

# 사용자 홈 디렉터리 내 .my_d_day_widget 폴더 생성
user_data_dir = Path(os.path.expanduser('~')) / ".my_d_day_widget"
user_data_dir.mkdir(parents=True, exist_ok=True)

# JSON 파일을 홈 디렉터리 하위 폴더에 저장
EVENTS_FILE = user_data_dir / "events.json"

def load_events():
    """JSON 파일에서 일정 정보를 불러옴 (없으면 기본 일정 생성)"""
    if EVENTS_FILE.exists():
        with open(EVENTS_FILE, "r", encoding="utf-8") as f:
            events = json.load(f)
            
            # target_date 문자열 -> datetime 변환
            for event in events:
                event["target_date"] = datetime.strptime(event["target_date"], "%Y-%m-%d %H:%M")
                
            return events
    else:
        # 기본 일정 데이터
        return [
            {"id": str(uuid.uuid4()), "title": "일정 1", "target_date": datetime(2000, 1, 1, 0, 0)},
            {"id": str(uuid.uuid4()), "title": "일정 2", "target_date": datetime(2025, 2, 25, 0, 0)},
            {"id": str(uuid.uuid4()), "title": "일정 3", "target_date": datetime(2030, 1, 1, 0, 0)},
        ]

def save_events():
    """event_data를 JSON 파일에 저장"""
    to_save = []
    
    for event in event_data:
        to_save.append({
            "id": event["id"],
            "title": event["title"],
            "target_date": event["target_date"].strftime("%Y-%m-%d %H:%M")
        })
        
    with open(EVENTS_FILE, "w", encoding="utf-8") as f:
        json.dump(to_save, f, ensure_ascii=False, indent=4)

def update_all():
    """전체 일정 UI 갱신 및 재배치"""
    for widget in container_frame.winfo_children():
        widget.destroy()
        
    event_frames.clear()

    # 날짜 순으로 정렬하여 EventFrame 생성
    sorted_data = sorted(event_data, key=lambda d: d["target_date"])
    
    for data in sorted_data:
        ef = EventFrame(
            container_frame,
            data["title"],
            data["target_date"],
            update_callback=update_all,
            add_event_callback=add_event,
            update_event_callback=update_event,
            delete_event_callback=delete_event,
            event_id=data["id"],
            width=220,
            height=120,
            bg="gray"
        )
        
        ef.pack(side="left", padx=10)
        event_frames.append(ef)

    # 메인 창 크기 재설정
    root.update_idletasks()
    win_width = container_frame.winfo_reqwidth() + 20
    win_height = container_frame.winfo_reqheight() + 20
    screen_width = root.winfo_screenwidth()
    x_pos = screen_width - win_width - 10
    y_pos = 50
    root.geometry(f"{win_width}x{win_height}+{x_pos}+{y_pos}")

    # 1분마다 갱신
    root.after(60000, update_all)

def add_event(new_title, new_target_date):
    """새 일정 추가"""
    new_event = {
        "id": str(uuid.uuid4()),
        "title": new_title,
        "target_date": new_target_date,
    }
    
    event_data.append(new_event)
    save_events()
    update_all()

def update_event(event_id, new_title, new_target_date):
    """기존 일정 수정"""
    for event in event_data:
        if event["id"] == event_id:
            event["title"] = new_title
            event["target_date"] = new_target_date
            break
        
    save_events()
    update_all()

def delete_event(event_id):
    """일정 삭제"""
    global event_data
    event_data = [ev for ev in event_data if ev["id"] != event_id]
    save_events()
    update_all()

# Tkinter 메인 윈도우 생성
root = tk.Tk()
root.overrideredirect(True)  # 기본 창 테두리 제거
root.attributes("-alpha", 0.7)  # 투명도
root.configure(bg="gray")
root.attributes("-transparentcolor", "gray")

container_frame = tk.Frame(root, bg="gray")
container_frame.pack(padx=10, pady=10, anchor="center")

# JSON 파일 로드
event_data = load_events()
event_frames = []

# 최초 UI 초기화
update_all()

# 창 위치 지정
root.update_idletasks()
win_width = container_frame.winfo_reqwidth() + 20
win_height = container_frame.winfo_reqheight() + 20
screen_width = root.winfo_screenwidth()
x_pos = screen_width - win_width - 10
y_pos = 50
root.geometry(f"{win_width}x{win_height}+{x_pos}+{y_pos}")

root.mainloop()
