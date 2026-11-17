import json
import csv
import pickle

class HealthDB:
    def __init__(self):
        self.json_file = "health_management_project\\data\\health_data.json"
        self.csv_file = "health_management_project\\data\\health_data.csv"
        self.txt_file = "health_management_project\\data\\health_data.txt"
        self.pkl_file = "health_management_project\\data\\health_data.pkl"
        
    def load_data(self):
        with open(self.json_file, "r", encoding="utf-8") as jf:
            jsdata = json.load(jf)
        
        with open(self.csv_file, "r", encoding="utf-8") as cf:
            csvdata = list(csv.DictReader(cf))

        with open(self.txt_file, "r", encoding="utf-8") as tf:
            txtdata = [line.strip().split(",") for line in tf.readlines()]

        with open(self.pkl_file, "rb") as pf:
            pkldata = pickle.load(pf)

        return jsdata, csvdata, txtdata, pkldata

    def save_data(self, jsdata, csvdata, txtdata, pkldata):
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


# AI 사용
# 프롬프트: 지금 네가지 타입의 파일 쓰기와 읽기기능을 만들고있어 리스트나 딕셔너리로 읽고 출력하여 검증하는 예제 코드를 작성해줘
if __name__ == "__main__":
    # 리스트에 딕셔너리 형태로 사람 구별 
    records = [
        #P2026-0001,홍길동,1995,남,175.0,72.5,23.67,과체중
        #P2026-0002,김영희,1998,여,162.0,52.0,19.81,정상
        {"id": "P2026-0001", "name": "홍길동", "birth_year": 1995, "gender": "남", "height": 175.0, "weight": 72.5, "bmi": 23.67, "status": "과체중"},
        {"id": "P2026-0002", "name": "김영희", "birth_year": 1998, "gender": "여", "height": 162.0, "weight": 52.0, "bmi": 19.81, "status": "정상"}
    ]

    print("원본 데이터:", records)
    db = HealthDB()

    # 현재 TXT 저장 메소드에 맞춰 문자열 리스트로 변환+ for 축약문법
    txt_rows = [
        # 문자열로 바꾸는 이유: TXT 저장 메소드의 ",".join(row)에서 join()은 문자열만 연결가능
        [row["name"], str(row["height"]), str(row["weight"])]
        for row in records
    ]

    db.save_data(records, records, txt_rows, records)
    # 저장 후, 로드 검증
    jsdata, csvdata, txtdata, pkldata = db.load_data()

    # CSV에서 문자열로 읽은 숫자를 복원
    for row in csvdata:
        row["height"] = float(row["height"])
        row["weight"] = float(row["weight"])

    # TXT에서 읽은 리스트를 원본과 같은 딕셔너리로 복원
    txtdata = [
        {"name": row[0], "height": float(row[1]), "weight": float(row[2])}
        for row in txtdata
    ]

    results = {
        "JSON": jsdata,
        "CSV": csvdata,
        "TXT": txtdata,
        "PKL": pkldata
    }

    for file_type, loaded in results.items():
        print(f"\n{file_type}에서 읽은 데이터:", loaded)
        print("원본과 일치:", records == loaded)



# 코드 매일 보완 및 수정 필요