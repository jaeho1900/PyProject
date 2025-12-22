import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter import ttk
import random
import csv
from datetime import datetime

class IdealWorldCupApp:
    def __init__(self, root, candidates):
        self.root = root
        self.root.title("S&I 미션 키워드 월드컵")

        # 1. 화면 사이즈 설정
        self.root.geometry("1200x900")
        self.root.resizable(False, False)

        # 2. 폰트 및 스타일 설정
        self.font_title = ("Malgun Gothic", 40, "bold")
        self.font_btn = ("Malgun Gothic", 25, "bold")
        self.font_info = ("Malgun Gothic", 18)
        self.bg_color = "#f0f0f0"

        self.color_default = "white"
        self.color_hover = "#FFEB3B"

        self.root.configure(bg=self.bg_color)

        # 데이터 초기화
        self.candidates = candidates
        random.shuffle(self.candidates)
        self.scores = {name: 0 for name in candidates}

        self.current_round_list = self.candidates
        self.next_round_list = []
        self.match_index = 0

        # 결과 데이터 저장 변수
        self.result_data = []

        self.create_widgets()
        self.update_match()

    def create_widgets(self):
        # 상단 라운드 정보
        self.lbl_round = tk.Label(self.root, text="", font=self.font_title, bg=self.bg_color)
        self.lbl_round.pack(pady=40)

        # 대결 버튼 프레임
        self.frame_match = tk.Frame(self.root, bg=self.bg_color)
        self.frame_match.pack(expand=True, fill="both", padx=50, pady=20)

        # --- 왼쪽 버튼 ---
        self.btn_left = tk.Button(self.frame_match, text="", font=self.font_btn,
                                  command=lambda: self.select_winner(0),
                                  bg=self.color_default, relief="groove", bd=5, cursor="hand2")
        self.btn_left.pack(side="left", expand=True, fill="both", padx=20)

        self.btn_left.bind("<Enter>", lambda e: self.on_hover(self.btn_left))
        self.btn_left.bind("<Leave>", lambda e: self.on_leave(self.btn_left))

        # --- VS 라벨 ---
        self.lbl_vs = tk.Label(self.frame_match, text="VS", font=("Impact", 40), bg=self.bg_color, fg="#ff4500")
        self.lbl_vs.pack(side="left", padx=20)

        # --- 오른쪽 버튼 ---
        self.btn_right = tk.Button(self.frame_match, text="", font=self.font_btn,
                                   command=lambda: self.select_winner(1),
                                   bg=self.color_default, relief="groove", bd=5, cursor="hand2")
        self.btn_right.pack(side="right", expand=True, fill="both", padx=20)

        self.btn_right.bind("<Enter>", lambda e: self.on_hover(self.btn_right))
        self.btn_right.bind("<Leave>", lambda e: self.on_leave(self.btn_right))

        # 하단 진행상황 바
        self.lbl_progress = tk.Label(self.root, text="", font=self.font_info, bg=self.bg_color, fg="#666666")
        self.lbl_progress.pack(pady=40)

    def on_hover(self, btn):
        btn['bg'] = self.color_hover

    def on_leave(self, btn):
        btn['bg'] = self.color_default

    def update_match(self):
        if len(self.current_round_list) == 1:
            self.show_result_table(self.current_round_list[0])
            return

        if self.match_index >= len(self.current_round_list):
            self.prepare_next_round()
            return

        if self.match_index == len(self.current_round_list) - 1:
            survivor = self.current_round_list[self.match_index]
            self.next_round_list.append(survivor)
            self.scores[survivor] += 1
            self.prepare_next_round()
            return

        left_name = self.current_round_list[self.match_index]
        right_name = self.current_round_list[self.match_index + 1]

        round_name = f"{len(self.current_round_list)}강" if len(self.current_round_list) > 2 else "👑 결승전 👑"
        self.lbl_round.config(text=f"{round_name}")

        self.btn_left.config(text=left_name)
        self.btn_right.config(text=right_name)

        total_matches = len(self.current_round_list) // 2
        current_match_num = (self.match_index // 2) + 1
        self.lbl_progress.config(text=f"Match {current_match_num} / {total_matches}")

    def select_winner(self, choice):
        if choice == 0:
            winner = self.current_round_list[self.match_index]
        else:
            winner = self.current_round_list[self.match_index + 1]

        self.scores[winner] += 1
        self.next_round_list.append(winner)
        self.match_index += 2
        self.update_match()

    def prepare_next_round(self):
        self.current_round_list = self.next_round_list
        self.next_round_list = []
        self.match_index = 0
        random.shuffle(self.current_round_list)
        self.update_match()

    def show_result_table(self, final_winner):
        for widget in self.root.winfo_children():
            widget.destroy()

        self.root.configure(bg="#fffacd")

        # 최종 우승 텍스트
        lbl_congrats = tk.Label(self.root, text="🎉 최종 우승 🎉", font=("Malgun Gothic", 30, "bold"), bg="#fffacd", fg="red")
        lbl_congrats.pack(pady=(40, 10))

        lbl_winner = tk.Label(self.root, text=final_winner, font=("Malgun Gothic", 50, "bold"), bg="#fffacd", fg="black")
        lbl_winner.pack(pady=(0, 30))

        # 순위표 프레임
        frame_table = tk.Frame(self.root)
        frame_table.pack(pady=20, padx=50, fill="both", expand=True)

        scrollbar = tk.Scrollbar(frame_table)
        scrollbar.pack(side="right", fill="y")

        # Treeview 스타일 설정
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Treeview", font=("Malgun Gothic", 15), rowheight=40)
        style.configure("Treeview.Heading", font=("Malgun Gothic", 18, "bold"))

        columns = ("rank", "name", "score")
        tree = ttk.Treeview(frame_table, columns=columns, show="headings", height=10, yscrollcommand=scrollbar.set)

        tree.heading("rank", text="순위")
        tree.heading("name", text="이름")
        tree.heading("score", text="승리 횟수")

        tree.column("rank", width=100, anchor="center")
        tree.column("name", width=400, anchor="center")
        tree.column("score", width=150, anchor="center")

        tree.pack(fill="both", expand=True)
        scrollbar.config(command=tree.yview)

        # 데이터 정렬 및 저장용 리스트 생성
        sorted_scores = sorted(self.scores.items(), key=lambda x: x[1], reverse=True)
        current_rank = 1
        self.result_data = []

        for i, (name, score) in enumerate(sorted_scores):
            if i > 0 and score < sorted_scores[i-1][1]:
                current_rank = i + 1

            rank_text = "🥇" if name == final_winner else str(current_rank)
            tree.insert("", "end", values=(rank_text, name, score))
            self.result_data.append([rank_text, name, score])

        # 하단 버튼 프레임
        frame_btns = tk.Frame(self.root, bg="#fffacd")
        frame_btns.pack(pady=30)

        # 저장 버튼
        btn_save = tk.Button(frame_btns, text="결과 저장 (CSV)", command=self.save_to_csv,
                             font=("Malgun Gothic", 20, "bold"), bg="#4CAF50", fg="white", cursor="hand2")
        btn_save.pack(side="left", padx=20)

        # 종료 버튼
        btn_exit = tk.Button(frame_btns, text="게임 종료", command=self.root.destroy,
                             font=("Malgun Gothic", 20), bg="white", cursor="hand2")
        btn_exit.pack(side="left", padx=20)

    def save_to_csv(self):
        if not self.result_data:
            messagebox.showwarning("경고", "저장할 데이터가 없습니다.")
            return

        # 1. 오늘 날짜 구하기 (yymmdd 형식)
        today_str = datetime.now().strftime("%y%m%d")

        # 2. 파일명 생성
        default_filename = f"S&I 미션 키워드 월드컵_결과_{today_str}_.csv"

        # 3. 파일 저장 대화상자 (기본 파일명 적용)
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="결과표 저장하기",
            initialfile=default_filename
        )

        if file_path:
            try:
                # utf-8-sig: 엑셀 호환
                with open(file_path, mode='w', newline='', encoding='utf-8-sig') as file:
                    writer = csv.writer(file)
                    writer.writerow(["순위", "이름", "승리 횟수"])
                    writer.writerows(self.result_data)

                messagebox.showinfo("완료", f"파일이 저장되었습니다.\n{file_path}")
            except Exception as e:
                messagebox.showerror("에러", f"파일 저장 중 오류가 발생했습니다.\n{e}")

if __name__ == "__main__":
    data = [
        "지속적인 매출 증대", "차별화 포인트 강화", "고객 이탈 방지", "대외 인지도 향상",
        "수익성 낮은 포트폴리오 탈피", "인당 조직 생산성 향상", "운영비 통제", "핵심 인재 이탈 방지",
        "고객 체감 DX 강화", "비즈니스 모델의 한계 돌파", "고부가가치 신사업 발굴/육성", "Key Account 관계 강화",
        "규제 리스크 대응", "수익성 개선", "우수 협력사 추가 확보", "서비스 투자 확대",
        "조직 사기 향상", "변화 저항 내성 타파", "단기 성과 전략 수립", "중장기 사업 전략 수립"
    ]

    root = tk.Tk()
    app = IdealWorldCupApp(root, data)
    root.mainloop()
