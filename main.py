import tkinter as tk
import json, os, uuid, sys, winreg
from datetime import datetime
from event_frame import EventFrame

# --- 자동 실행 등록 (Windows 레지스트리 사용, 콘솔창 제거를 위해 pythonw.exe 사용) ---
def add_to_startup():
    """
    현재 프로그램을 Windows 레지스트리의 Run 키에 등록하여
    컴퓨터 부팅 시 자동으로 실행되도록 함.
    콘솔창이 뜨지 않도록 pythonw.exe를 사용합니다.
    """
    try:
        script_path = os.path.abspath(sys.argv[0])
        # sys.executable가 "python.exe"이면 "pythonw.exe"로 변경
        executable = sys.executable
        
        if "python.exe" in executable.lower():
            executable = executable.replace("python.exe", "pythonw.exe")
            
        reg_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        key_name = "MyTkinterApp"  # 원하는 이름으로 변경 가능
        reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_SET_VALUE)
        
        # 실행 명령어 예시: "C:\Path\to\pythonw.exe" "C:\path\to\script.py"
        command = f'"{executable}" "{script_path}"'
        
        winreg.SetValueEx(reg_key, key_name, 0, winreg.REG_SZ, command)
        winreg.CloseKey(reg_key)
        
        print("자동 실행 등록 성공!")
        
    except Exception as e:
        print("자동 실행 등록 실패:", e)

# 프로그램 시작 시 자동 실행 등록 (한번만 등록)
add_to_startup()
# --- 끝 ---

# JSON 파일 경로
EVENTS_FILE = "events.json"

def load_events():
    """JSON 파일에서 일정 데이터를 읽어오며, 파일이 없으면 기본 데이터를 반환"""
    if os.path.exists(EVENTS_FILE):
        with open(EVENTS_FILE, "r", encoding="utf-8") as f:
            events = json.load(f)
            # target_date 문자열을 datetime 객체로 변환
            
            for event in events:
                event["target_date"] = datetime.strptime(event["target_date"], "%Y-%m-%d %H:%M")
                
            return events
    else:
        # 기본 일정 데이터 (id는 uuid로 생성)
        return [
            {"id": str(uuid.uuid4()), "title": "일정 1", "target_date": datetime(2000, 1, 1, 0, 0)},
            {"id": str(uuid.uuid4()), "title": "일정 2", "target_date": datetime(2025, 2, 25, 0, 0)},
            {"id": str(uuid.uuid4()), "title": "일정 3", "target_date": datetime(2030, 1, 1, 0, 0)},
        ]

def save_events():
    """event_data를 JSON 파일에 저장 (target_date는 문자열로 변환)"""
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
    """모든 EventFrame의 D-Day를 갱신하고, 일정들을 목표 일시 기준 오름차순으로 재배치"""
    # container_frame 내 기존 위젯 삭제
    for widget in container_frame.winfo_children():
        widget.destroy()
        
    event_frames.clear()

    # event_data를 날짜 기준 오름차순 정렬
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

    # 새로 생성된 일정 프레임에 맞게 메인 창의 크기 재설정
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
    """새로운 일정을 추가한 후 JSON 저장 및 UI 갱신"""
    new_event = {
        "id": str(uuid.uuid4()),
        "title": new_title,
        "target_date": new_target_date,
    }
    
    event_data.append(new_event)
    save_events()
    update_all()

def update_event(event_id, new_title, new_target_date):
    """수정된 일정 정보를 반영하여 JSON 저장 및 UI 갱신"""
    for event in event_data:
        if event["id"] == event_id:
            event["title"] = new_title
            event["target_date"] = new_target_date
            break
        
    save_events()
    update_all()

def delete_event(event_id):
    """해당 일정을 삭제한 후 JSON 저장 및 UI 갱신"""
    global event_data
    event_data = [event for event in event_data if event["id"] != event_id]
    
    save_events()
    update_all()

# 메인 윈도우 생성 및 설정
root = tk.Tk()
root.overrideredirect(True)  # 기본 창 테두리 제거
root.attributes("-alpha", 0.7)  # 전체 창 투명도 70%
root.configure(bg="gray")
root.attributes("-transparentcolor", "gray")  # 회색 배경을 투명하게

# 일정 프레임들을 담을 컨테이너 프레임
container_frame = tk.Frame(root, bg="gray")
container_frame.pack(padx=10, pady=10, anchor="center")

# 전역 일정 데이터 및 EventFrame 리스트 (JSON에서 불러옴)
event_data = load_events()
event_frames = []

# 최초 UI 배치 및 주기적 갱신 시작
update_all()

# 화면 오른쪽 상단에 창 배치
root.update_idletasks()
win_width = container_frame.winfo_reqwidth() + 20
win_height = container_frame.winfo_reqheight() + 20
screen_width = root.winfo_screenwidth()
x_pos = screen_width - win_width - 10
y_pos = 50
root.geometry(f"{win_width}x{win_height}+{x_pos}+{y_pos}")

root.mainloop()
