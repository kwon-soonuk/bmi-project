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
        self.json_file = "health_management_project\\data.health_data.json"
        self.csv_file = "health_management_project\\data.health_data.csv"
        self.txt_file = "health_management_project\\data.health_data.txt"
        self.pkl_file = "health_management_project\\data.health_data.pkl"
        
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
