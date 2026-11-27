# ===========================================================================
# [AI 사용 주석]
#  - AI 종류     : Claude (Anthropic, Claude Opus 5.5)
#  - 사용 목적   : load_data / save_data 에 파일 부재·손상 예외 처리(try-except) 추가
#                  → 이 두 메소드는 AI가 작성 (요구서 모듈1 "파일 부재나 손상 시 예외 처리",
#                    비기능 "try-except 로 안전하게 처리하고 기본값(빈 리스트 등)을 반환")
#                  → HealthRecord, dict_to_record, 파일 경로는 본인이 작성한 그대로
#  - 사용 프롬프트 : "확인 필요한 1번 파일 없거나 손상시 예외처리 그냥 추가하는건 어때?"
#                    "진행방식 1번으로해 작성, 테스트, 적용까지하면 내가 main에병합할게"
#  - 사용한 사람 : 권순욱 (202611814)
#  - 날짜        : 2026-11-26
# ===========================================================================
import json
import csv
import pickle

class HealthRecord:
    def __init__(self, record_id, name, birth_year, gender, height, weight):
        self.id = record_id
        self.name = name
        self.birth_year = int(birth_year)
        self.gender = gender
        self.height = float(height)
        self.weight = float(weight)
        self.bmi = 0.0
        self.status = ""
        self.calc_bmi()

    def calc_bmi(self):
        heightM = self.height / 100
        self.bmi = round(self.weight / (heightM ** 2), 2)
        self.status = self.judge_status()

    def judge_status(self):
        if self.bmi < 18.5:
            return "저체중"
        elif self.bmi < 23.0:
            return "정상"
        elif self.bmi < 25.0:
            return "과체중"
        else:
            return "비만"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "birth_year": self.birth_year,
            "gender": self.gender,
            "height": self.height,
            "weight": self.weight,
            "bmi": self.bmi,
            "status": self.status
        }

    def __str__(self):
        return f"HealthRecord(id={self.id}, name={self.name}, bmi={self.bmi}, status={self.status})"

def dict_to_record(data):
    return HealthRecord(
        record_id=data["id"],
        name=data["name"],
        birth_year=data["birth_year"],
        gender=data["gender"],
        height=data["height"],
        weight=data["weight"]
    )

class HealthDB:
    def __init__(self):
        self.json_file = "health_management_project\\data\\health_data.json"
        self.csv_file = "health_management_project\\data\\health_data.csv"
        self.txt_file = "health_management_project\\data\\health_data.txt"
        self.pkl_file = "health_management_project\\data\\health_data.pkl"
        
    def load_data(self):
        """4가지 파일을 읽어 (json, csv, txt, pkl) 데이터 4개를 돌려준다.
        파일마다 따로 try-except 로 감싸서, 없거나 손상되어 읽지 못한 파일은 빈 리스트로 돌려준다.
        그래서 파일 하나가 없어도 나머지 형식은 불러올 수 있다."""
        try:
            with open(self.json_file, "r", encoding="utf-8") as jf:
                jsdata = json.load(jf)
        except Exception:       # 파일 없음(FileNotFoundError), 권한 문제, 내용 손상(JSONDecodeError) 등
            jsdata = []

        try:
            with open(self.csv_file, "r", encoding="utf-8") as cf:
                csvdata = list(csv.DictReader(cf))
        except Exception:       # 파일 없음, 권한 문제, UTF-8 이 아닌 파일(UnicodeDecodeError) 등
            csvdata = []

        try:
            with open(self.txt_file, "r", encoding="utf-8") as tf:
                txtdata = [line.strip().split(",") for line in tf.readlines()]
        except Exception:       # 파일 없음, 권한 문제, UTF-8 이 아닌 파일 등
            txtdata = []

        try:
            with open(self.pkl_file, "rb") as pf:
                pkldata = pickle.load(pf)
        except Exception:       # 파일 없음, 빈 파일(EOFError), 내용 손상(UnpicklingError) 등
            pkldata = []

        return jsdata, csvdata, txtdata, pkldata

    def save_data(self, jsdata, csvdata, txtdata, pkldata):
        """4가지 파일로 저장한다. 모두 저장하면 True, 하나라도 실패하면 False 를 돌려준다.
        실패 예: 파일이 다른 프로그램(엑셀 등)에서 열려 있음, 권한 문제, 디스크 용량 부족, 저장할 목록이 비어 있음.
        중간에 실패하면 그 앞에서 저장한 파일은 이미 바뀌어 있을 수 있다."""
        try:
            with open(self.json_file, "w", encoding="utf-8") as jf:
                json.dump(jsdata, jf, ensure_ascii=False, indent=4)

            with open(self.csv_file, "w", encoding="utf-8", newline="") as cf:
                writer = csv.DictWriter(cf, fieldnames=csvdata[0].keys())
                writer.writeheader()
                writer.writerows(csvdata)

            with open(self.txt_file, "w", encoding="utf-8") as tf:
                for row in txtdata:
                    tf.write(",".join(row) + "\n")

            with open(self.pkl_file, "wb") as pf:
                pickle.dump(pkldata, pf)
        except Exception:
            return False
        return True
