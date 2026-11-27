# ===========================================================================
# [AI 사용 주석]
#  - AI 종류     : Claude (Anthropic, Claude Opus 5.5 / Claude Fable 5.2)
#  - 사용 목적   : 모듈3 GUI 기획(구상안 피드백 반영한 단일 창 설계), 클래스·메소드·위젯 이름 설계,
#                  줄 단위 작성 힌트, 자가 점검용 채점 스크립트(check_module3.py), 완성 후 힌트 주석 정리
#                  → 기능 코드는 힌트를 보고 본인이 작성
#                  → 프롬프트 (4)에서는 AI가 코드를 직접 고침:
#                     · 화면 꾸미기(색·글꼴 상수, make_button / make_entry / make_stat_card,
#                       표 스타일, 통계 카드, 차트 색)
#                     · 어려운 코드를 수업에서 배운 수준의 쉬운 코드로 바꿔 쓰기
#                  → 프롬프트 (5)에서는 AI가 화면을 평가하고 사용성 보완 코드를 직접 작성:
#                     · 화면 전환 탭(기록/통계), 상태 표시줄(건수·저장 여부), 폼의 모드 표시,
#                       선택한 행 강조, 통계의 표준편차·비율 표시, 엔터 키 처리
#  - 사용 프롬프트 :
#      (1) "개인프로젝트 모듈3 작성을할거야 구상안에서 피드백 받은 내용은 조회하면서 수정과 삭제를
#           할 수 있도록, 지금은 스마트폰 화면처럼 창을 메뉴마다 바뀌는걸 최소화할거야 우리가 하던
#           방식처럼 기획부터 해줘"  (첨부: 개인프로젝트 gui 구상안.pptx)
#      (2) "마감일은 그대로지만 내일까지 완성하고싶어 1.수정범위 추천해준대로 할게 2.저장버튼 누르지
#           않고 종료하면 저장되지 않도록 할게 구상안대로야 파일 열어서 health_gui 코드 작성할 수
#           있도록 힌트를 통해 도와봐(코드 온전히 넣진말고)"
#      (3) "확인해봐", "다시 확인하고 문제 없으면 마무리" → 채점 결과 확인과 힌트 주석 정리만 받음
#      (4) "figma와 디자인 관련 스킬 활용해서 프로그램 조금 꾸며봐 코드들중에 시니어 이상의 수준인
#           코드가 있다면 대학생 입장에서 작성한 수준으로 낮춰줘"
#      (5) "지금 gui어떤지 평가하고 보완하자 물론 과제 조건은 지켜야해 작업은 바로 적용하지말고
#           임시폴더 하나 만들어서 거기서 작업해"
#      (6) "확인 필요한 1번 파일 없거나 손상시 예외처리 그냥 추가하는건 어때?"
#          "진행방식 1번으로해 작성, 테스트, 적용까지하면 내가 main에병합할게"
#          → AI가 on_load / on_save 를 모듈1의 새 예외 처리 방식(빈 리스트, True/False)에 맞춰 수정 (2026-11-26)
#  - AI 추가 사용 기록 : OpenAI Codex로 GUI 색상·배치 적용 및 통계 화면 전환 구현
#    요청: "지금 gui파일 수정해야해 ... 통계부분을 다른창에 볼 수 있으면 좋겠어 버튼누르면 창 바뀌게"
#  - 사용한 사람 : 권순욱 (202611814)
#  - 날짜        : 2026-11-25
# ===========================================================================
"""모듈3: 한 창에서 기록 화면과 전체 통계 화면을 전환하는 Tkinter GUI.

- 기록 화면: 입력 폼과 조회 표를 나란히 두어 선택한 기록을 바로 수정·삭제한다.
- 통계 화면: 총 인원, 평균·표준편차(키·몸무게·BMI), BMI 상태별 인원을 보여 준다.
- 맨 위 [기록] [통계] 탭으로 화면을 바꾸고, 맨 아래 상태 표시줄에 건수와 저장 여부를 보여 준다.
- 데이터 처리는 모듈2 HealthManager, 파일은 모듈1 HealthDB 의 메소드를 부른다.
- 수정은 키·몸무게만 가능하며 파일 저장은 [저장] 버튼으로 한다.
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import datetime
import csv

try:
    from modules.health_db import HealthDB, HealthRecord, dict_to_record
    from modules.health_logic import HealthManager
except ModuleNotFoundError:
    from health_db import HealthDB, HealthRecord, dict_to_record
    from health_logic import HealthManager


# ---------- 화면에 쓰는 상수 ----------
COLUMNS = ("id", "name", "age", "gender", "height", "weight", "bmi", "status")   # 표 열 이름
HEADINGS = ("식별번호", "이름", "나이", "성별", "키(cm)", "몸무게(kg)", "BMI", "상태")   # 표 제목(같은 순서)
STATUS_ORDER = ("저체중", "정상", "과체중", "비만")                              # 차트 막대 순서
FORMATS = ("JSON", "CSV", "TXT", "PKL")                                         # 파일 형식 Combobox

# ---------- 디자인 상수: 색과 글꼴을 한곳에 모아 두고 이름으로 쓴다 ----------
BG = "#F2F6F3"          # 창 바탕
CARD = "#FFFFFF"        # 구역 바탕
TEXT = "#172C27"        # 기본 글자
SUBTEXT = "#536863"     # 보조 글자
LINE = "#D6E2DA"        # 테두리
GRAY = "#EAF0EB"        # 보조 버튼, 잠긴 입력칸
STRIPE = "#F4F8F5"      # 표의 줄무늬, 통계 카드
ACCENT = "#176455"      # 기본 동작
SELECTED = "#E6F2EB"    # BMI 결과, 모드 표시 바탕
SELECTED_ROW = "#BFDDCD"  # 표에서 선택한 행 (줄무늬와 헷갈리지 않게 더 진한 색)
DANGER = "#9E4037"      # 삭제 글자
STATUS_COLORS = {"저체중": "#355F73", "정상": "#176455", "과체중": "#7B5719", "비만": "#9E4037"}

FONT = ("맑은 고딕", 10)
FONT_BOLD = ("맑은 고딕", 10, "bold")
FONT_TITLE = ("맑은 고딕", 15, "bold")
FONT_BIG = ("맑은 고딕", 16, "bold")


class HealthGUI:
    """BMI 건강관리 프로그램의 기록 화면과 통계 화면."""

    # ---------- 화면 구성 ----------
    def __init__(self, root):
        """창을 설정하고 두 화면을 만든 뒤 처음 기록을 불러온다."""
        self.root = root
        self.root.title("BMI 건강관리 프로그램")
        self.root.geometry("1060x700")
        self.root.minsize(940, 680)
        self.root.configure(bg=BG)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)

        self.db = HealthDB()
        self.manager = HealthManager()
        self.selected_id = None     # 지금 폼에 띄운 사람의 식별번호 (None 이면 신규 모드)
        self.changed = False        # 저장하지 않은 변경이 있으면 True

        self.build_file_bar()
        self.records_page = tk.Frame(self.root, bg=BG)
        self.records_page.grid(row=1, column=0, sticky="nsew")
        self.records_page.grid_columnconfigure(1, weight=1)
        self.records_page.grid_rowconfigure(0, weight=1)
        self.build_form()
        self.build_table()
        self.build_stats()
        self.build_status_bar()

        self.clear_form()
        self.refresh()
        self.set_changed(False)
        self.on_load(quiet=True)

    def make_button(self, parent, text, color, command):
        """배경색이 color 인 평평한 버튼을 만들어 반환한다. 배치(pack/grid)는 부른 쪽에서 한다."""
        if color == GRAY:
            text_color = TEXT
        else:
            text_color = "white"
        button = tk.Button(parent, text=text, command=command, font=FONT_BOLD,
                           bg=color, fg=text_color, activebackground=color, activeforeground=text_color,
                           disabledforeground="#71817A", relief="flat", bd=0,
                           highlightthickness=1, highlightbackground=CARD, highlightcolor=TEXT,
                           padx=12, pady=5, cursor="hand2")
        return button

    def paint_button(self, button, color):
        """버튼 배경색을 color 로 바꾸고 글자색을 거기에 맞춘다. (회색이면 어두운 글자, 아니면 흰 글자)"""
        if color == GRAY:
            text_color = TEXT
        else:
            text_color = "white"
        button.config(bg=color, fg=text_color, activebackground=color, activeforeground=text_color)

    def make_entry(self, parent, width):
        """입력칸을 만들고 포커스가 있을 때 강조색 테두리를 표시한다."""
        entry = tk.Entry(parent, width=width, font=FONT, relief="flat", bg=CARD, fg=TEXT,
                         readonlybackground=GRAY, highlightthickness=1,
                         highlightbackground=LINE, highlightcolor=ACCENT)
        return entry

    def build_file_bar(self):
        """두 화면에서 공통으로 쓰는 제목, 화면 전환 탭, 파일 작업 버튼."""
        bar = tk.Frame(self.root, bg=CARD, padx=24, pady=14)
        bar.grid(row=0, column=0, sticky="we")
        tk.Label(bar, text="BMI 건강관리 프로그램", bg=CARD, fg=TEXT, font=FONT_TITLE).pack(side="left")

        # 화면 전환 탭: 지금 보고 있는 화면의 탭만 강조색이다 (show_records / show_stats 가 색을 바꾼다)
        self.btn_records = self.make_button(bar, "기록", ACCENT, self.show_records)
        self.btn_records.pack(side="left", padx=(24, 0))
        self.btn_stats = self.make_button(bar, "통계", GRAY, self.show_stats)
        self.btn_stats.pack(side="left", padx=(4, 0))

        # side="right" 는 먼저 pack 한 것이 가장 오른쪽에 간다
        self.btn_import = self.make_button(bar, "CSV 일괄 등록", GRAY, self.on_import_csv)
        self.btn_import.pack(side="right", padx=(6, 0))
        self.btn_save = self.make_button(bar, "저장", GRAY, self.on_save)
        self.btn_save.pack(side="right", padx=(6, 0))
        self.btn_load = self.make_button(bar, "불러오기", GRAY, self.on_load)
        self.btn_load.pack(side="right", padx=(6, 0))

        self.format_var = tk.StringVar(value="JSON")
        self.combo_format = ttk.Combobox(bar, textvariable=self.format_var, values=FORMATS,
                                         state="readonly", width=6, font=FONT)
        self.combo_format.pack(side="right", padx=(6, 6))
        tk.Label(bar, text="파일 형식", bg=CARD, fg=SUBTEXT, font=FONT).pack(side="right")

    def build_form(self):
        """① 왼쪽 입력 폼: 모드 표시 / 식별번호(표시만) / 이름 / 생년 / 성별 / 키 / 몸무게 / BMI 결과 / 버튼 4개."""
        form = tk.LabelFrame(self.records_page, text=" 기록 입력 ", bg=CARD, fg=TEXT, font=FONT_TITLE,
                             bd=0, highlightthickness=1, highlightbackground=LINE, highlightcolor=LINE,
                            padx=16, pady=16)
        form.grid(row=0, column=0, sticky="nsew", padx=(24, 8), pady=16)

        # 0행: 지금 폼이 어떤 모드인지 보여 준다 (set_mode 가 글자를 바꾼다)
        self.lbl_mode = tk.Label(form, text="신규 등록", bg=SELECTED, fg=ACCENT, font=FONT_BOLD, padx=8, pady=2)
        self.lbl_mode.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 6))

        # 0열: 항목 이름 (1행부터)
        row = 1
        for text in ("식별번호", "이름", "생년", "성별", "키(cm)", "몸무게(kg)"):
            tk.Label(form, text=text, bg=CARD, fg=SUBTEXT, font=FONT).grid(row=row, column=0, sticky="w", pady=7)
            row += 1

        # 1열: 값 (식별번호는 입력칸이 아니라 보여 주기만 한다)
        self.lbl_id = tk.Label(form, text="(자동 발급)", bg=CARD, fg=ACCENT, font=FONT_BOLD)
        self.lbl_id.grid(row=1, column=1, sticky="w", padx=(12, 0))

        self.entry_name = self.make_entry(form, 16)
        self.entry_name.grid(row=2, column=1, sticky="w", padx=(12, 0), ipady=3)
        self.entry_birth = self.make_entry(form, 16)
        self.entry_birth.grid(row=3, column=1, sticky="w", padx=(12, 0), ipady=3)

        self.gender_var = tk.StringVar(value="남")
        gender_frame = tk.Frame(form, bg=CARD)
        gender_frame.grid(row=4, column=1, sticky="w", padx=(8, 0))
        self.radio_male = tk.Radiobutton(gender_frame, text="남", value="남", variable=self.gender_var,
                                         bg=CARD, activebackground=CARD, font=FONT)
        self.radio_male.pack(side="left")
        self.radio_female = tk.Radiobutton(gender_frame, text="여", value="여", variable=self.gender_var,
                                           bg=CARD, activebackground=CARD, font=FONT)
        self.radio_female.pack(side="left")

        self.entry_height = self.make_entry(form, 16)
        self.entry_height.grid(row=5, column=1, sticky="w", padx=(12, 0), ipady=3)
        self.entry_weight = self.make_entry(form, 16)
        self.entry_weight.grid(row=6, column=1, sticky="w", padx=(12, 0), ipady=3)

        # BMI 결과: 선택한 사람의 BMI 와 상태를 상태 색으로 보여 준다
        self.lbl_result = tk.Label(form, text="BMI -", bg=SELECTED, fg=SUBTEXT, font=FONT_BIG, pady=8)
        self.lbl_result.grid(row=7, column=0, columnspan=2, sticky="we", pady=(16, 8))

        # 버튼 2 x 2
        buttons = tk.Frame(form, bg=CARD)
        buttons.grid(row=8, column=0, columnspan=2)
        self.btn_add = self.make_button(buttons, "등록", ACCENT, self.on_add)
        self.btn_add.grid(row=0, column=0, padx=3, pady=3, sticky="we")
        self.btn_update = self.make_button(buttons, "수정", ACCENT, self.on_update)
        self.btn_update.grid(row=0, column=1, padx=3, pady=3, sticky="we")
        self.btn_delete = self.make_button(buttons, "삭제", GRAY, self.on_delete)
        self.btn_delete.config(fg=DANGER, activeforeground=DANGER)
        self.btn_delete.grid(row=1, column=0, padx=3, pady=3, sticky="we")
        self.btn_new = self.make_button(buttons, "새로 입력", GRAY, self.clear_form)
        self.btn_new.grid(row=1, column=1, padx=3, pady=3, sticky="we")
        for button in (self.btn_add, self.btn_update, self.btn_delete, self.btn_new):
            button.config(width=9)      # 네 버튼의 폭을 같게

        # 모드에 따라 바뀌는 안내 문장 (set_mode 가 글자를 바꾼다)
        self.lbl_hint = tk.Label(form, text="", bg=CARD, fg=SUBTEXT, font=("맑은 고딕", 9), justify="center")
        self.lbl_hint.grid(row=9, column=0, columnspan=2, pady=(8, 0))

        # 입력칸에서 엔터를 누르면 등록(신규 모드) 또는 수정(선택 모드)
        for entry in (self.entry_name, self.entry_birth, self.entry_height, self.entry_weight):
            entry.bind("<Return>", self.on_form_enter)

    def build_table(self):
        """② 오른쪽 조회 구역: 검색 줄 + Treeview 표 + 세로 스크롤바 + 행 선택 이벤트."""
        box = tk.LabelFrame(self.records_page, text=" 기록 조회 ", bg=CARD, fg=TEXT, font=FONT_TITLE,
                            bd=0, highlightthickness=1, highlightbackground=LINE, highlightcolor=LINE,
                            padx=16, pady=16)
        box.grid(row=0, column=1, sticky="nsew", padx=(8, 24), pady=16)

        # 검색 줄
        search_frame = tk.Frame(box, bg=CARD)
        search_frame.pack(fill="x", pady=(0, 4))
        self.entry_search = self.make_entry(search_frame, 20)
        self.entry_search.pack(side="left", fill="x", expand=True, ipady=4)
        self.entry_search.bind("<Return>", self.on_search)      # 엔터로도 검색
        self.make_button(search_frame, "검색", GRAY, self.on_search).pack(side="left", padx=(8, 0))
        self.make_button(search_frame, "전체", GRAY, self.on_show_all).pack(side="left", padx=(8, 0))
        tk.Label(box, text="이름 · 식별번호 · 상태로 검색", bg=CARD, fg=SUBTEXT,
                 font=("맑은 고딕", 9)).pack(anchor="w", pady=(0, 12))

        # 표 모양 (ttk 위젯은 색·글꼴을 Style 로 정한다)
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", font=FONT, rowheight=34, background=CARD, fieldbackground=CARD,
                        foreground=TEXT, borderwidth=0)
        style.configure("Treeview.Heading", font=FONT_BOLD, background=GRAY, foreground=TEXT,
                        relief="flat", padding=(0, 8))
        style.map("Treeview", background=[("selected", SELECTED_ROW)], foreground=[("selected", TEXT)])

        table_frame = tk.Frame(box, bg=CARD)
        table_frame.pack(fill="both", expand=True)
        self.tree = ttk.Treeview(table_frame, columns=COLUMNS, show="headings", height=12)
        for column, heading in zip(COLUMNS, HEADINGS):
            self.tree.heading(column, text=heading)
            self.tree.column(column, width=80, anchor="center")
        self.tree.column("id", width=110)
        self.tree.tag_configure("odd", background=STRIPE)       # 홀수 번째 줄만 옅은 색 (줄무늬)

        scrollbar = tk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 행을 클릭(선택)할 때마다 on_select 가 불린다
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

    def make_stat_card(self, parent, caption):
        """통계 카드 1개(작은 제목 + 큰 숫자 + 작은 설명)를 만든다.
        반환: (큰 숫자 Label, 작은 설명 Label) — 작은 설명에는 표준편차를 보여 준다."""
        card = tk.Frame(parent, bg=STRIPE, padx=16, pady=12)
        card.pack(side="left", fill="both", expand=True, padx=4)
        tk.Label(card, text=caption, bg=STRIPE, fg=SUBTEXT, font=FONT).pack(anchor="w")
        value_label = tk.Label(card, text="-", bg=STRIPE, fg=TEXT, font=FONT_BIG, width=8, anchor="w")
        value_label.pack(anchor="w")
        sub_label = tk.Label(card, text="", bg=STRIPE, fg=SUBTEXT, font=("맑은 고딕", 9))
        sub_label.pack(anchor="w")
        return value_label, sub_label

    def build_stats(self):
        """통계 화면을 준비한다. 맨 위 [통계] 탭을 누르면 기록 화면 대신 표시한다."""
        self.stats_page = tk.Frame(self.root, bg=CARD, highlightthickness=1,
                                   highlightbackground=LINE, highlightcolor=LINE,
                                   padx=20, pady=16)

        heading = tk.Frame(self.stats_page, bg=CARD)
        heading.pack(fill="x", pady=(0, 16))
        tk.Label(heading, text="전체 기록 통계", bg=CARD, fg=TEXT, font=FONT_TITLE).pack(side="left")
        tk.Label(heading, text="검색과 관계없이 등록된 전체 기록으로 계산합니다.", bg=CARD, fg=SUBTEXT,
                 font=("맑은 고딕", 9)).pack(side="left", padx=(12, 0))

        cards = tk.Frame(self.stats_page, bg=CARD)
        cards.pack(fill="x", pady=(0, 20))
        self.lbl_count, self.lbl_count_sub = self.make_stat_card(cards, "총 인원")
        self.lbl_height, self.lbl_height_std = self.make_stat_card(cards, "평균 키")
        self.lbl_weight, self.lbl_weight_std = self.make_stat_card(cards, "평균 몸무게")
        self.lbl_bmi, self.lbl_bmi_std = self.make_stat_card(cards, "평균 BMI")

        tk.Label(self.stats_page, text="BMI 상태별 인원", bg=CARD, fg=TEXT,
                 font=FONT_BOLD).pack(anchor="w", padx=4)
        self.canvas = tk.Canvas(self.stats_page, width=720, height=272, bg=CARD, highlightthickness=0)
        self.canvas.pack(expand=True)

    def show_stats(self):
        """[통계] 탭: 통계 화면으로 전환하고 탭 색을 바꾼다."""
        self.records_page.grid_remove()
        self.stats_page.grid(row=1, column=0, sticky="nsew", padx=24, pady=16)
        self.paint_button(self.btn_records, GRAY)
        self.paint_button(self.btn_stats, ACCENT)

    def show_records(self):
        """[기록] 탭: 검색과 입력 상태를 그대로 둔 채 기록 화면으로 돌아간다."""
        self.stats_page.grid_remove()
        self.records_page.grid()
        self.paint_button(self.btn_records, ACCENT)
        self.paint_button(self.btn_stats, GRAY)

    def build_status_bar(self):
        """맨 아래 상태 표시줄: 왼쪽에는 기록 건수(검색 결과), 오른쪽에는 저장 여부를 보여 준다."""
        bar = tk.Frame(self.root, bg=CARD, padx=24, pady=6)
        bar.grid(row=2, column=0, sticky="we")
        self.lbl_status = tk.Label(bar, text="", bg=CARD, fg=SUBTEXT, font=FONT)
        self.lbl_status.pack(side="left")
        self.lbl_saved = tk.Label(bar, text="", bg=CARD, fg=SUBTEXT, font=FONT_BOLD)
        self.lbl_saved.pack(side="right")

    def set_changed(self, changed):
        """저장하지 않은 변경이 있는지 기억하고, 상태 표시줄과 [저장] 버튼 색으로 알려 준다.
        등록·수정·삭제·일괄 등록 뒤에는 True, 불러오기·저장 뒤에는 False 로 부른다."""
        self.changed = changed
        if changed:
            self.lbl_saved.config(text="저장하지 않은 변경이 있습니다 → [저장]", fg=DANGER)
            self.paint_button(self.btn_save, ACCENT)
        else:
            self.lbl_saved.config(text="변경 사항 없음", fg=SUBTEXT)
            self.paint_button(self.btn_save, GRAY)

    # ---------- 표 갱신 ----------
    def refresh(self, records=None):
        """표를 records 로 다시 채우고 통계를 갱신한다. records 가 None 이면 전체 목록.
        등록·수정·삭제·불러오기 후에는 항상 이 메소드 하나만 부른다."""
        searching = True            # records 를 넘겨받았으면 검색 결과를 보여 주는 중
        if records is None:
            records = self.manager.get_all()
            searching = False

        # 기존 행을 모두 지운다 (안 지우면 같은 사람이 계속 쌓인다)
        for row_id in self.tree.get_children():
            self.tree.delete(row_id)

        current_year = datetime.date.today().year
        index = 0
        for record in records:
            age = current_year - record.birth_year
            values = (record.id, record.name, age, record.gender,
                      f"{record.height:.1f}", f"{record.weight:.1f}", f"{record.bmi:.2f}", record.status)
            if index % 2 == 0:
                tag = "even"
            else:
                tag = "odd"
            # iid 에 식별번호를 넣어 두면 tree.selection()[0] 이 바로 식별번호가 된다
            self.tree.insert("", "end", iid=record.id, values=values, tags=(tag,))
            index += 1

        # 상태 표시줄에 건수를 보여 준다 (표가 비어 있을 때는 무엇을 하면 되는지도 알려 준다)
        total = len(self.manager.get_all())
        if total == 0:
            self.lbl_status.config(text="등록된 기록이 없습니다. 왼쪽에서 등록하거나 [불러오기]를 누르세요.")
        elif searching == False:
            self.lbl_status.config(text=f"전체 {total}건")
        elif len(records) == 0:
            self.lbl_status.config(text=f"검색 결과가 없습니다. [전체]를 누르면 {total}건이 모두 보입니다.")
        else:
            self.lbl_status.config(text=f"검색 결과 {len(records)}건 / 전체 {total}건")

        self.update_stats()

    # ---------- 입력 검증 · 등록 ----------
    def read_positive(self, entry, label):
        """entry 의 글자를 0보다 큰 float 로 바꿔 반환. 잘못되면 경고창 띄우고 None.
        label: 경고 문장에 넣을 이름("키", "몸무게"). 모듈2 input_float 의 GUI 버전."""
        try:
            value = float(entry.get())
        except ValueError:
            messagebox.showwarning("입력 오류", f"{label}에 숫자를 입력하세요.")
            return None

        if not 0 < value <= 500:
            messagebox.showwarning("입력 오류", f"{label}에는 0보다 크고 500 이하인 숫자를 입력하세요.")
            return None
        return value

    def read_form(self):
        """폼 전체를 검사해 (name, birth_year, gender, height, weight) 튜플 반환. 하나라도 틀리면 None."""
        name = self.entry_name.get().strip()
        if name == "":
            messagebox.showwarning("입력 오류", "이름을 입력하세요.")
            return None

        try:
            birth_year = int(self.entry_birth.get())
        except ValueError:
            messagebox.showwarning("입력 오류", "생년을 정수로 입력하세요. 예) 1995")
            return None

        current_year = datetime.date.today().year
        if not 1900 <= birth_year <= current_year:
            messagebox.showwarning("입력 오류", f"생년은 1900년부터 {current_year}년까지 입력하세요.")
            return None

        gender = self.gender_var.get()

        height = self.read_positive(self.entry_height, "키")
        if height is None:
            return None
        weight = self.read_positive(self.entry_weight, "몸무게")
        if weight is None:
            return None

        return name, birth_year, gender, height, weight

    def on_add(self):
        """[등록] 버튼: 검사 → 모듈2 add_record → 결과 알림 → 폼 비우기 → 표 갱신."""
        values = self.read_form()
        if values is None:
            return      # 경고창은 read_form 이 이미 띄웠다

        name, birth_year, gender, height, weight = values
        record = self.manager.add_record(name, birth_year, gender, height, weight)
        if record is None:
            messagebox.showwarning("등록 실패", "이미 등록된 사람입니다.")
            return

        messagebox.showinfo("등록 완료", f"{record.name} 님을 등록했습니다. (식별번호: {record.id})")
        self.set_changed(True)
        self.clear_form()
        self.refresh()

    def on_form_enter(self, event=None):
        """폼의 입력칸에서 엔터: 신규 모드면 등록, 선택 모드면 수정."""
        if self.selected_id is None:
            self.on_add()
        else:
            self.on_update()

    def set_entry(self, entry, value):
        """입력칸 entry 의 글자를 지우고 value 로 바꾼다."""
        entry.delete(0, "end")
        entry.insert(0, value)

    def clear_form(self):
        """[새로 입력] 버튼 / 등록·삭제 후: 폼을 비우고 신규 모드로 돌아간다."""
        self.selected_id = None
        self.set_mode("new")        # 먼저 잠금을 푼다 (잠긴 칸은 지워지지 않는다)

        self.set_entry(self.entry_name, "")
        self.set_entry(self.entry_birth, "")
        self.set_entry(self.entry_height, "")
        self.set_entry(self.entry_weight, "")
        self.gender_var.set("남")
        self.lbl_id.config(text="(자동 발급)")
        self.lbl_result.config(text="BMI -", fg=SUBTEXT)

        # 표의 선택 표시도 푼다
        self.tree.selection_remove(self.tree.selection())
        self.entry_name.focus_set()     # 바로 이름부터 입력할 수 있게 커서를 옮긴다

    # ---------- 행 선택 → 폼 (신규/선택 모드) ----------
    def set_mode(self, mode):
        """mode == "new": 모두 입력 가능, [등록]만 켬 / 그 외("selected"): 이름·생년·성별 잠금, [수정][삭제]만 켬.
        키·몸무게 칸은 수정해야 하므로 항상 입력 가능하다. 꺼진 버튼은 회색으로 바꾼다.
        폼 위의 모드 표시와 아래 안내 문장도 함께 바꾼다."""
        if mode == "new":
            self.entry_name.config(state="normal")
            self.entry_birth.config(state="normal")
            self.radio_male.config(state="normal")
            self.radio_female.config(state="normal")
            self.btn_add.config(state="normal", bg=ACCENT)
            self.btn_update.config(state="disabled", bg=LINE)
            self.btn_delete.config(state="disabled", bg=LINE)
            self.lbl_mode.config(text="신규 등록")
            self.lbl_hint.config(text="표에서 행을 클릭하면\n수정·삭제할 수 있습니다.")
        else:
            self.entry_name.config(state="readonly")
            self.entry_birth.config(state="readonly")
            self.radio_male.config(state="disabled")
            self.radio_female.config(state="disabled")
            self.btn_add.config(state="disabled", bg=LINE)
            self.btn_update.config(state="normal", bg=ACCENT)
            self.btn_delete.config(state="normal", bg=GRAY)
            self.lbl_mode.config(text="수정 모드")
            self.lbl_hint.config(text="키·몸무게만 수정할 수 있습니다.\n[새로 입력]을 누르면 등록으로 돌아갑니다.")

    def fill_form(self, record):
        """record(HealthRecord) 의 값을 폼에 채운다. on_select 와 on_update 가 부른다."""
        self.set_mode("new")        # 다른 사람을 보던 중이면 칸이 잠겨 있어서 먼저 푼다

        self.set_entry(self.entry_name, record.name)
        self.set_entry(self.entry_birth, record.birth_year)
        self.set_entry(self.entry_height, record.height)
        self.set_entry(self.entry_weight, record.weight)
        self.gender_var.set(record.gender)
        self.lbl_id.config(text=record.id)
        self.lbl_result.config(text=f"BMI {record.bmi:.2f} · {record.status}",
                               fg=STATUS_COLORS[record.status])

    def on_select(self, event=None):
        """표에서 행을 클릭하면(<<TreeviewSelect>>) 그 사람을 폼에 띄우고 선택 모드로."""
        selected = self.tree.selection()
        if len(selected) == 0:
            return      # 선택이 풀릴 때도 이 이벤트가 오기 때문에 필요

        record = self.manager.find_by_id(selected[0])
        if record is None:
            return

        self.selected_id = record.id
        self.fill_form(record)
        self.set_mode("selected")

    # ---------- 수정 · 삭제 ----------
    def on_update(self):
        """[수정] 버튼: 선택한 사람의 키·몸무게만 수정 → BMI 재계산(모듈2) → 화면 갱신."""
        if self.selected_id is None:
            messagebox.showwarning("수정 실패", "표에서 수정할 대상을 먼저 선택하세요.")
            return

        height = self.read_positive(self.entry_height, "키")
        if height is None:
            return
        weight = self.read_positive(self.entry_weight, "몸무게")
        if weight is None:
            return

        # BMI 재계산(calc_bmi)은 모듈2 update_record 안에서 한다
        self.manager.update_record(self.selected_id, height=height, weight=weight)
        record = self.manager.find_by_id(self.selected_id)

        self.refresh()
        self.tree.selection_set(self.selected_id)   # 표를 새로 그리면 선택 표시가 풀려서 다시 선택
        self.fill_form(record)
        self.set_mode("selected")
        self.set_changed(True)
        messagebox.showinfo("수정 완료", f"BMI {record.bmi:.2f} · {record.status} 로 다시 계산했습니다.")

    def on_delete(self):
        """[삭제] 버튼: 확인 창(askyesno) → 모듈2 delete_record → 폼 비우기 → 표 갱신."""
        if self.selected_id is None:
            messagebox.showwarning("삭제 실패", "표에서 삭제할 대상을 먼저 선택하세요.")
            return

        record = self.manager.find_by_id(self.selected_id)
        answer = messagebox.askyesno("삭제 확인", f"{record.name}({record.id}) 정보를 삭제할까요?")
        if answer == False:
            return

        self.manager.delete_record(self.selected_id)
        messagebox.showinfo("삭제 완료", "삭제되었습니다.")
        self.set_changed(True)
        self.clear_form()
        self.refresh()

    # ---------- 검색 ----------
    def on_search(self, event=None):
        """[검색] 버튼 / 엔터: 이름 일부 / 식별번호 / 상태(정상·비만…)로 표를 거른다. 데이터는 바꾸지 않음."""
        keyword = self.entry_search.get().strip()
        if keyword == "":
            self.refresh()
            return
        self.refresh(self.manager.search(keyword))

    def on_show_all(self):
        """[전체] 버튼: 검색칸을 비우고 전체 목록."""
        self.entry_search.delete(0, "end")
        self.refresh()

    # ---------- 통계 · 차트 ----------
    def update_stats(self):
        """모듈2 get_statistics() 결과(인원·평균·표준편차·상태별 인원)로 통계 카드와 차트를 갱신.
        검색 중이어도 항상 전체 기준이다."""
        stats = self.manager.get_statistics()
        if stats is None:       # 0명일 때
            self.lbl_count.config(text="0명")
            self.lbl_height.config(text="-")
            self.lbl_weight.config(text="-")
            self.lbl_bmi.config(text="-")
            self.lbl_height_std.config(text="")
            self.lbl_weight_std.config(text="")
            self.lbl_bmi_std.config(text="")
            self.draw_chart({})
            return

        self.lbl_count.config(text=f"{stats['count']}명")
        self.lbl_height.config(text=f"{stats['height_mean']:.1f} cm")
        self.lbl_weight.config(text=f"{stats['weight_mean']:.1f} kg")
        self.lbl_bmi.config(text=f"{stats['bmi_mean']:.2f}")
        self.lbl_height_std.config(text=f"표준편차 {stats['height_std']:.1f}")
        self.lbl_weight_std.config(text=f"표준편차 {stats['weight_std']:.1f}")
        self.lbl_bmi_std.config(text=f"표준편차 {stats['bmi_std']:.2f}")
        self.draw_chart(stats["status_count"])

    def draw_chart(self, status_count):
        """Canvas 에 비만도별 인원 막대 4개 (막대 위에 인원수와 비율). status_count 예: {"정상": 3, "비만": 1}"""
        self.canvas.delete("all")       # 안 지우면 막대가 겹겹이 쌓인다

        # 가장 많은 인원수 (막대 높이의 기준, 0 으로 나누지 않도록 최소 1) 와 전체 인원수 (비율 계산용)
        max_count = 1
        total = 0
        for count in status_count.values():
            if count > max_count:
                max_count = count
            total += count

        bottom = 224                    # 막대 바닥의 y 좌표 (Canvas 는 아래로 갈수록 y 가 커진다)
        self.canvas.create_line(48, bottom, 672, bottom, fill=LINE)

        index = 0
        for status in STATUS_ORDER:
            count = status_count.get(status, 0)         # 없는 상태는 0명
            center = 126 + index * 156
            top = bottom - count / max_count * 180
            self.canvas.create_rectangle(center - 34, top, center + 34, bottom,
                                         fill=STATUS_COLORS[status], outline="")
            if total == 0:
                percent = 0
            else:
                percent = count / total * 100
            self.canvas.create_text(center, top - 16, text=f"{count}명 ({percent:.0f}%)",
                                    font=FONT_BOLD, fill=TEXT)
            self.canvas.create_text(center, bottom + 20, text=status, font=FONT, fill=SUBTEXT)
            index += 1

    # ---------- 파일 불러오기 · 저장 ----------
    def on_load(self, quiet=False):
        """[불러오기] 버튼 / 프로그램 시작: 고른 형식의 파일을 HealthRecord 목록으로 바꿔 manager 에 넘긴다.
        quiet=True 면 성공 알림을 띄우지 않는다 (시작할 때용). 실패해도 기존 목록은 그대로 둔다.
        저장하지 않은 변경이 있으면 지금 목록이 사라지므로 먼저 물어본다."""
        if self.changed:
            answer = messagebox.askyesno("불러오기", "저장하지 않은 변경이 있습니다.\n"
                                         "불러오면 지금 목록이 파일 내용으로 바뀝니다. 계속할까요?")
            if answer == False:
                return

        fmt = self.format_var.get()
        records = []
        json_data, csv_data, txt_data, pkl_data = self.db.load_data()    # 모듈1: 읽지 못한 파일은 빈 리스트
        try:
            if fmt == "JSON":
                for data in json_data:
                    records.append(dict_to_record(data))
            elif fmt == "CSV":
                for data in csv_data:       # 값이 문자열이지만 HealthRecord 가 int/float 로 바꿔 준다
                    records.append(dict_to_record(data))
            elif fmt == "TXT":
                for row in txt_data:        # row: [id, name, birth_year, gender, height, weight, bmi, status]
                    records.append(HealthRecord(row[0], row[1], row[2], row[3], row[4], row[5]))
            else:
                for data in pkl_data:
                    records.append(dict_to_record(data))
        except Exception as e:      # 파일은 읽었지만 기록 모양이 맞지 않을 때 (예: TXT 한 줄의 값 개수가 다름)
            messagebox.showwarning("불러오기 실패", f"{fmt} 파일의 내용이 올바른 형식이 아닙니다.\n{e}")
            return

        if len(records) == 0:       # 파일이 없거나, 손상되었거나, 비어 있음 → 지금 목록은 그대로 둔다
            messagebox.showwarning("불러오기 실패", f"{fmt} 파일이 없거나, 손상되었거나, 비어 있어서\n"
                                   "불러올 기록이 없습니다. 지금 목록은 그대로 둡니다.")
            return

        self.manager.set_records(records)
        self.set_changed(False)     # 방금 파일에서 읽었으므로 파일과 같은 상태
        self.clear_form()
        self.refresh()
        if quiet == False:
            messagebox.showinfo("불러오기 완료", f"{fmt} 파일에서 {len(records)}건 불러왔습니다.")

    def on_save(self):
        """[저장] 버튼: '파일 저장하시겠습니까?' → 예면 모듈1 save_data 로 4가지 형식 모두 저장.
        저장 버튼을 누르지 않고 창을 닫으면 저장되지 않는다 (설계 결정)."""
        if len(self.manager.get_all()) == 0:
            messagebox.showwarning("파일 저장 실패", "저장할 데이터가 없습니다.")
            return

        answer = messagebox.askyesno("파일 저장", "파일 저장하시겠습니까?")
        if answer == False:
            return

        dict_list = self.manager.to_dict_list()
        txt_rows = [list(map(str, d.values())) for d in dict_list]     # 모듈2 menu_save 와 같은 방식
        saved = self.db.save_data(dict_list, dict_list, txt_rows, dict_list)   # 모듈1: 성공 True / 실패 False
        if saved == False:
            messagebox.showerror("파일 저장 실패", "파일을 저장하지 못했습니다.\n"
                                 "파일이 엑셀 같은 다른 프로그램에서 열려 있거나 쓰기 권한이 없는지 확인하세요.")
            return

        self.set_changed(False)
        messagebox.showinfo("파일 저장 성공", "JSON, CSV, TXT, PKL 4가지 형식으로 저장했습니다.")

    # ---------- CSV 일괄 등록 ----------
    def on_import_csv(self):
        """[CSV 일괄 등록] 버튼: 고른 CSV 의 사람들을 add_record 로 하나씩 추가 (중복·잘못된 줄은 건너뜀).
        CSV 첫 줄에 name, birth_year, gender, height, weight 열 이름이 있어야 한다."""
        path = filedialog.askopenfilename(title="CSV 파일 선택", filetypes=[("CSV 파일", "*.csv")])
        if not path:        # 취소하면 빈 값이 온다
            return

        try:
            with open(path, "r", encoding="utf-8") as file:
                rows = list(csv.DictReader(file))
        except Exception as e:
            messagebox.showwarning("CSV 일괄 등록 실패", f"CSV 파일을 읽지 못했습니다.\n{e}")
            return

        added = 0
        skipped = 0
        for row in rows:
            try:
                name = row["name"]
                birth_year = int(row["birth_year"])
                gender = row["gender"]
                height = float(row["height"])
                weight = float(row["weight"])
            except (KeyError, ValueError, TypeError):
                skipped += 1        # 열이 없거나 숫자가 아닌 줄
                continue

            if not name or gender not in ("남", "여") or height <= 0 or weight <= 0:
                skipped += 1
                continue

            record = self.manager.add_record(name, birth_year, gender, height, weight)
            if record is None:
                skipped += 1        # 이미 등록된 사람
            else:
                added += 1

        if added > 0:
            self.set_changed(True)
        self.refresh()
        messagebox.showinfo("CSV 일괄 등록 완료", f"{added}건 추가, {skipped}건 제외")


if __name__ == "__main__":
    root = tk.Tk()
    HealthGUI(root)
    root.mainloop()
