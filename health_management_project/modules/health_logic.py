import json
import csv
import pickle
from health_db import *

class HealthManager:
    def __init__(self):
        self.health_data = {}
        self.health_db = HealthDB()

    def add_record(self, user_name, record):
        if user_name not in self.health_data:
            self.health_data[user_name] = []
        self.health_data[user_name].append(record)

    def list_records(self, user_name):
        return self.health_data.get(user_name, [])
    
    def search_records(self, user_name, search_term):
        records = self.list_records(user_name)
        return [record for record in records if search_term.lower() in record["name"].lower()]

    def edit_delete_record(self, user_name, record_index, new_record=None):
        if user_name in self.health_data and 0 <= record_index < len(self.health_data[user_name]):
            if new_record:
                self.health_data[user_name][record_index] = new_record
                return True
            else:
                del self.health_data[user_name][record_index]
                return True
        return False
    # 건강정보 통계 (레코드 수, 각 필드(몸무게, 키, BMI) 평균, 표준편차 등) 계산
    def statistics(self, user_name):
        records = self.list_records(user_name)
        if not records:
            return None
        total_height = sum(record["height"] for record in records)
        total_weight = sum(record["weight"] for record in records)
        count = len(records)
        return {
            "average_height": total_height / count,
            "average_weight": total_weight / count,
            "average_bmi": sum(record["bmi"] for record in records) / count if "bmi" in records[0] else None,
            "total_records": count
        }

    def import_data(self, jsdata, csvdata, txtdata, pkldata):
        for record in jsdata:
            user_name = record.get("user_name")
            if user_name:
                self.add_record(user_name, record)
        
        for record in csvdata:
            user_name = record.get("user_name")
            if user_name:
                self.add_record(user_name, record)

        for row in txtdata:
            if len(row) >= 4:
                user_name, name, height, weight = row[0], row[1], float(row[2]), float(row[3])
                record = {"user_name": user_name, "name": name, "height": height, "weight": weight}
                self.add_record(user_name, record)

        for record in pkldata:
            user_name = record.get("user_name")
            if user_name:
                self.add_record(user_name, record)

    def save_data(self):
        jsdata = []
        csvdata = []
        txtdata = []
        pkldata = []

        for user_name, records in self.health_data.items():
            for record in records:
                record_with_id = {"user_name": user_name, **record}
                jsdata.append(record_with_id)
                csvdata.append(record_with_id)
                txtdata.append([user_name, record["name"], str(record["height"]), str(record["weight"])])
                pkldata.append(record_with_id)

        self.health_db.save_data(jsdata, csvdata, txtdata, pkldata)


if __name__ == "__main__":
    m = HealthManager()
    choice = input("----- 건강정보 관리 시스템 ------\n1. 추가\n2. 목록 조회\n3. 검색 및 상세조회\n4. 수정 및 삭제\n5. 통계조회\n6. 파일에서 가져오기 (모듈1)\n7. 파일로 저장 (모듈1)\n0. 종료\n")
#while을 빼야할까? 
    while choice != "0":
        if choice == "1":
            name = input("사용자 이름을 입력하세요: ")
            height = float(input("키를 입력하세요 (cm): "))
            weight = float(input("몸무게를 입력하세요 (kg): "))
            record = {"name": name, "height": height, "weight": weight}
            m.add_record(name, record)
            print("기록이 추가되었습니다.")
        elif choice == "2":
            records = m.list_records(name)
            if records:
                for idx, record in enumerate(records):
                    print(f"{idx + 1}. {record}")
            else:
                print("기록이 없습니다.")
        elif choice == "3":
            search_term = input("검색할 이름을 입력하세요: ")
            results = m.search_records(name, search_term)
            if results:
                for record in results:
                    print(record)
            else:
                print("검색 결과가 없습니다.")
        elif choice == "4":
            records = m.list_records(name)
            if records:
                for idx, record in enumerate(records):
                    print(f"{idx + 1}. {record}")
                record_index = int(input("수정/삭제할 기록 번호를 입력하세요: ")) - 1
                action = input("수정하려면 '수정', 삭제하려면 '삭제'를 입력하세요: ")
                if action == "수정":
                    name = input("새 이름을 입력하세요: ")
                    height = float(input("새 키를 입력하세요 (cm): "))
                    weight = float(input("새 몸무게를 입력하세요 (kg): "))
                    new_record = {"name": name, "height": height, "weight": weight}
                    if m.edit_delete_record(name, record_index, new_record):
                        print("기록이 수정되었습니다.")
                    else:
                        print("기록 수정에 실패했습니다.")
                elif action == "삭제":
                    if m.edit_delete_record(name, record_index):
                        print("기록이 삭제되었습니다.")
                    else:
                        print("기록 삭제에 실패했습니다.")
                else:
                    print("잘못된 입력입니다.")
        elif choice == "5":
            people_statistics = {}
            stats = m.statistics(name)
            if stats:
                print(f"평균 키: {stats['average_height']:.2f} cm")
                print(f"평균 몸무게: {stats['average_weight']:.2f} kg")
                print(f"총 기록 수: {stats['total_records']}")
            else:
                print("기록이 없습니다.")
        elif choice == "6":
            db = HealthDB()
            jsdata, csvdata, txtdata, pkldata = db.load_data()
            m.import_data(jsdata, csvdata, txtdata, pkldata)
            print("파일에서 데이터를 가져왔습니다.")
        choice = input("----- 건강정보 관리 시스템 ------\n1. 추가\n2. 목록 조회\n3. 검색 및 상세조회\n4. 수정 및 삭제\n5. 통계조회\n6. 파일에서 가져오기 (모듈1)\n7. 파일로 저장 (모듈1)\n0. 종료\n")


# 수정필요