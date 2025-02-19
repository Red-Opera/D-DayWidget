import tkinter as tk
from tkinter import simpledialog, messagebox
from datetime import datetime

class EventFrame(tk.Frame):
    def __init__(self, master, title, target_date, update_callback,
                 add_event_callback=None, update_event_callback=None,
                 delete_event_callback=None, event_id=None,
                 width=220, height=120, **kwargs):
        super().__init__(master, **kwargs)
        
        self.title = title
        self.target_date = target_date
        self.width = width
        self.height = height
        self.update_callback = update_callback
        self.add_event_callback = add_event_callback
        self.update_event_callback = update_event_callback
        self.delete_event_callback = delete_event_callback
        self.event_id = event_id  # 고유 식별자

        # 배경색을 부모 위젯(bg="gray")과 동일하게 설정
        self.configure(bg=master["bg"])

        # 테두리 없는 캔버스 생성
        self.canvas = tk.Canvas(self, width=self.width, height=self.height,
                                highlightthickness=0, bg=self["bg"])
        self.canvas.pack()

        self.create_widgets()
        self.update_dday()

        # 더블 클릭: 일정 수정(제목/날짜)
        self.canvas.bind("<Double-1>", self.modify)
        
        # 오른쪽 클릭: 컨텍스트 메뉴(추가/삭제)
        self.canvas.bind("<Button-3>", self.show_context_menu)

    def create_widgets(self):
        # 둥근 모서리 흰색 카드 배경
        self.create_rounded_rectangle(0, 0, self.width, self.height, radius=20, fill="white", outline="")

        # 제목 텍스트
        self.title_text_id = self.canvas.create_text(
            10, 25, text=self.title, anchor='w',
            font=("맑은 고딕", 12, "bold"), fill="black"
        )

        # 날짜 및 시간 텍스트
        self.date_text_id = self.canvas.create_text(
            10, 50, text=get_date_string(self.target_date), anchor='w',
            font=("맑은 고딕", 10), fill="black"
        )

        # D-Day 텍스트
        self.dday_text_id = self.canvas.create_text(
            self.width / 2, 80, text="",
            anchor='center', font=("CascadiaCode", 14, "bold"), fill="black"
        )

    def create_rounded_rectangle(self, x1, y1, x2, y2, radius=25, **kwargs):
        """둥근 사각형을 그리는 헬퍼 함수"""
        points = [
            x1 + radius, y1,
            x1 + radius, y1,
            x2 - radius, y1,
            x2 - radius, y1,
            x2, y1,
            x2, y1 + radius,
            x2, y1 + radius,
            x2, y2 - radius,
            x2, y2 - radius,
            x2, y2,
            x2 - radius, y2,
            x2 - radius, y2,
            x1 + radius, y2,
            x1 + radius, y2,
            x1, y2,
            x1, y2 - radius,
            x1, y2 - radius,
            x1, y1 + radius,
            x1, y1 + radius,
            x1, y1
        ]
        
        return self.canvas.create_polygon(points, **kwargs, smooth=True)

    def update_dday(self):
        """D-Day 업데이트"""
        now = datetime.now()
        diff = self.target_date - now
        days = diff.days
        
        if diff.total_seconds() < 0:
            dday_str = f"D + {-days}"
            
        else:
            dday_str = f"D - {days}"
            
        self.canvas.itemconfig(self.dday_text_id, text=dday_str)
        self.remaining_seconds = diff.total_seconds()

    def modify(self, event):
        """더블 클릭으로 제목/날짜 수정"""
        new_title = simpledialog.askstring("제목 수정", "새로운 제목:", initialvalue=self.title)
        
        if new_title:
            self.title = new_title
            self.canvas.itemconfig(self.title_text_id, text=self.title)

        default_date_str = self.target_date.strftime("%Y-%m-%d %H:%M")
        new_date_str = simpledialog.askstring("날짜 수정", "새로운 날짜 (YYYY-MM-DD HH:MM):", initialvalue=default_date_str)
        
        if new_date_str:
            try:
                new_target_date = datetime.strptime(new_date_str, "%Y-%m-%d %H:%M")
                self.target_date = new_target_date
                self.update_dday()
                self.canvas.itemconfig(self.date_text_id, text=get_date_string(self.target_date))
                
                if self.update_event_callback and self.event_id is not None:
                    self.update_event_callback(self.event_id, self.title, self.target_date)
                    
                self.update_callback()
                
            except ValueError:
                print("잘못된 날짜 형식입니다. 예시: 2025-02-25 08:00")

    def show_context_menu(self, event):
        """오른쪽 클릭 메뉴 (추가/삭제)"""
        menu = tk.Menu(self, tearoff=0)
        
        menu.add_command(label="추가", command=lambda: self.open_add_event_popup(None))
        menu.add_command(label="삭제", command=self.delete_event)
        
        menu.tk_popup(event.x_root, event.y_root)

    def open_add_event_popup(self, event):
        """새 일정 추가 팝업"""
        self.add_popup = tk.Toplevel(self)
        self.add_popup.title("새로운 일정 추가")
        self.add_popup.geometry("300x200")

        tk.Label(self.add_popup, text="일정 제목:").pack(pady=5)
        self.title_entry = tk.Entry(self.add_popup, width=30)
        self.title_entry.pack(pady=5)

        tk.Label(self.add_popup, text="일정 날짜 (YYYY-MM-DD HH:MM):").pack(pady=5)
        self.date_entry = tk.Entry(self.add_popup, width=30)
        self.date_entry.pack(pady=5)

        tk.Button(self.add_popup, text="추가", command=self.handle_add_event).pack(pady=5)

    def handle_add_event(self):
        """새 일정 추가"""
        new_title = self.title_entry.get()
        new_date_str = self.date_entry.get()
        
        if new_title and new_date_str:
            try:
                new_target_date = datetime.strptime(new_date_str, "%Y-%m-%d %H:%M")
                if self.add_event_callback:
                    self.add_event_callback(new_title, new_target_date)
                    
                self.add_popup.destroy()
                
            except ValueError:
                print("잘못된 날짜 형식입니다. 예시: 2025-02-25 08:00")

    def delete_event(self):
        """현재 일정 삭제"""
        if messagebox.askyesno("삭제", "정말 이 일정을 삭제하시겠습니까?"):
            if self.delete_event_callback and self.event_id is not None:
                self.delete_event_callback(self.event_id)


def get_date_string(target):
    """
    target datetime -> "YYYY-MM-DD (요일) 오전/오후 HH:MM" 형태
    """
    WEEKDAYS_KOR = ["월", "화", "수", "목", "금", "토", "일"]
    wday = WEEKDAYS_KOR[target.weekday()]
    ampm = target.strftime("%p")
    ampm_kor = "오전" if ampm == "AM" else "오후"
    hour_12 = target.strftime("%I")
    minute = target.strftime("%M")
    date_str = target.strftime(f"%Y-%m-%d ({wday})")
    time_str = f"{ampm_kor} {int(hour_12)}:{minute}"
    
    return f"{date_str} {time_str}"
