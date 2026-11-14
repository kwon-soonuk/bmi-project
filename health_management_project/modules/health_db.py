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
