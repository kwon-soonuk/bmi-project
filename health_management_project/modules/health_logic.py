# ===========================================================================
# [AI 사용 주석]
#  - AI 종류     : Claude (Anthropic, Claude Opus 5.5)
#  - 사용 목적   : 모듈2 설계 방향(클래스·메소드 이름과 매개변수)과 줄 단위 작성 힌트,
#                  독스트링 초안, 자가 점검용 채점 스크립트, 완성 후 힌트 주석 정리
#                  → 실행 코드는 힌트를 보고 본인이 직접 작성 (힌트 주석은 완성 후 삭제)
#  - 사용 프롬프트 :
#      (1) "현재 지정개인프로젝트를 진행하는 중이야 지난번에 모듈1을 작성했었고 이제 모듈2를
#           작성해야해 관련내용을 첨부파일에 올렸어 코드작성을 완전히 맡기는게 아니야 한줄씩
#           어떤 코드를 작성해야할지 방향을 너가 잡아줬으면 좋겠어 물론 이 프롬프트 내용도
#           모듈2 코드에 주석으로 달아둬야해 그게 규칙이야 내가 스스로 공부할 수 있도록
#           계획을 설정하고 모듈2를 완성하는게 목표야"
#           (첨부: 12주차 과제 공지 PDF, 지정프로젝트 요구서 BMI-2026-v11 PDF)
#      (2) "현재상황 업데이트해" 등 → 진행 상황 점검·코드 검토만 받음
#      (3) "로직에 불필요한 주석이 너무 많아서 읽기 힘들어 ai사용했다는거 맨처음에 밝히고
#           코드 중간중간 미션처럼 만들어둔 주석을 최소화하고싶어"
#  - 사용한 사람 : 권순욱 (202611814)
#  - 날짜        : 2026-11-23
# ===========================================================================
"""모듈2: 건강정보 핵심 로직(CRUD, BMI 재계산, 통계) + 콘솔 테스트 프로그램(TUI).

- HealthManager : 메모리의 HealthRecord 목록만 관리 (input/print/파일 X, 결과는 return)
- TUI 함수들    : 사용자 입력과 출력 담당, HealthManager 와 HealthDB(모듈1)를 호출
"""
import statistics

try:
    from modules.health_db import HealthDB, HealthRecord, dict_to_record
except ModuleNotFoundError:
    from health_db import HealthDB, HealthRecord, dict_to_record


# ---------- HealthManager: 메모리의 건강정보 목록 관리 (입출력 없음, 결과는 return) ----------
class HealthManager:
    """건강정보(HealthRecord) 목록을 메모리에서 관리하는 클래스.

    각 메소드는 한 가지 일만 하고 결과를 반환한다.
    출력은 아래 TUI 함수(나중에는 모듈3 GUI)가 담당한다.
    """

    def __init__(self, records=None):
        """records: 모듈1에서 읽어 온 HealthRecord 리스트. 없으면 빈 목록으로 시작."""
        if records is None:
            records = []

        self.records = list(records)

    def set_records(self, records):
        """관리 목록 전체를 새 리스트로 교체한다. (메뉴 6 '파일에서 가져오기' 용)"""
        self.records = list(records)

    def generate_id(self, year=2026):
        """다음 환자식별번호 문자열을 반환한다. 예: 'P2026-0003'"""
        max_num = 0
        for record in self.records:
            num = int(record.id.split("-")[1])
            if num > max_num:
                max_num = num
        return f"P{year}-{max_num + 1:04d}"

    def is_duplicate(self, name, birth_year, gender):
        """이름·생년·성별이 모두 같은 사람이 이미 있으면 True, 없으면 False."""
        for record in self.records:
            if (record.name == name and
                record.birth_year == int(birth_year) and
                record.gender == gender):
                return True
        return False

    def add_record(self, name, birth_year, gender, height, weight):
        """새 레코드를 만들어 목록에 추가하고 그 레코드를 반환. 중복이면 None."""
        if self.is_duplicate(name, birth_year, gender):
            return None

        new_id = self.generate_id()
        new_record = HealthRecord(new_id, name, birth_year, gender, height, weight)
        self.records.append(new_record)
        return new_record

    def get_all(self):
        """전체 목록을 반환한다 (복사본)."""
        return list(self.records)

    def find_by_id(self, record_id):
        """식별번호가 같은 레코드 1개를 반환, 없으면 None. (상세조회·수정·삭제의 공통 부품)"""
        for record in self.records:
            if record.id == record_id:
                return record
        return None

    def search(self, keyword):
        """이름에 keyword 포함 / 식별번호 일치 / 비만도 일치 인 레코드들의 리스트를 반환."""
        results = []
        for record in self.records:
            if (keyword in record.name or
                keyword == record.id or
                keyword == record.status):
                results.append(record)
        return results

    def update_record(self, record_id, height=None, weight=None):
        """키·몸무게를 수정하고 BMI·비만도를 재계산. 성공 True / 없는 id 면 False."""
        record = self.find_by_id(record_id)
        if record is None:
            return False
        if height is not None:
            record.height = float(height)
        if weight is not None:
            record.weight = float(weight)
        record.calc_bmi()
        return True

    def delete_record(self, record_id):
        """식별번호의 레코드를 목록에서 제거. 성공 True / 없는 id 면 False."""
        record = self.find_by_id(record_id)
        if record is None:
            return False
        self.records.remove(record)
        return True

    def get_statistics(self):
        """통계 딕셔너리를 반환. 레코드가 없으면 None.

        반환 키 (check_module2.py 가 이 이름으로 검사함):
            count, height_mean, height_std, weight_mean, weight_std,
            bmi_mean, bmi_std, status_count   예) status_count = {"정상": 3, "비만": 1}
        """
        if not self.records:
            return None
        list_height = [r.height for r in self.records]
        list_weight = [r.weight for r in self.records]
        list_bmi = [r.bmi for r in self.records]
        status_count = {}
        for r in self.records:
            status_count[r.status] = status_count.get(r.status, 0) + 1

        return {
            "count": len(self.records),
            "height_mean": statistics.mean(list_height),
            "height_std": statistics.pstdev(list_height),
            "weight_mean": statistics.mean(list_weight),
            "weight_std": statistics.pstdev(list_weight),
            "bmi_mean": statistics.mean(list_bmi),
            "bmi_std": statistics.pstdev(list_bmi),
            "status_count": status_count
        }

    def to_dict_list(self):
        """저장용: 모든 레코드를 딕셔너리로 바꾼 리스트를 반환."""
        return [r.to_dict() for r in self.records]


# ---------- 콘솔 인터페이스(TUI): 입력과 출력 담당 ----------
def input_float(prompt):
    """0 보다 큰 실수를 받을 때까지 반복해서 묻고, float 를 반환한다."""
    while True:
        try:
            value = float(input(prompt))
            if value <= 0:
                print("0보다 큰 숫자를 입력하세요.")
                continue
            return value
        except ValueError:
            print("숫자를 입력하세요.")
            continue


def input_int(prompt):
    """정수를 받을 때까지 반복해서 묻고, int 를 반환한다. (생년 입력용)"""
    while True:
        try:
            value = int(input(prompt))
            return value
        except ValueError:
            print("정수를 입력하세요.")
            continue


def print_menu():
    """메인 메뉴를 출력한다."""
    print("1. 등록\n2. 전체 목록\n3. 검색\n4. 수정/삭제\n5. 통계\n6. 불러오기\n7. 저장\n0. 종료")


def print_table(records):
    """레코드 리스트를 표 모양으로 출력한다. (FR-02 '전체 목록 보기')"""
    if not records:
        print("등록된 정보가 없습니다.")
        return
    print(f"{'ID':<12} {'이름':<8} {'생년':<6} {'성별':<4} {'키':>8} {'몸무게':>8} {'BMI':>8} {'상태':<8}")
    for r in records:
        print(f"{r.id:<12} {r.name:<8} {r.birth_year:<6} {r.gender:<4} {r.height:>8.1f} {r.weight:>8.1f} {r.bmi:>8.2f} {r.status:<8}")

def print_detail(record):
    """레코드 1개의 모든 항목을 세로로 출력한다. (상세조회)"""
    for key, value in record.to_dict().items():
        print(f"{key}: {value}")


def print_statistics(stats):
    """get_statistics() 의 결과를 보기 좋게 출력한다."""
    if stats is None:
        print("통계를 낼 데이터가 없습니다.")
        return

    print(f"인원수: {stats['count']}")
    print(f"키 평균: {stats['height_mean']:.2f}, 표준편차: {stats['height_std']:.2f}")
    print(f"몸무게 평균: {stats['weight_mean']:.2f}, 표준편차: {stats['weight_std']:.2f}")
    print(f"BMI 평균: {stats['bmi_mean']:.2f}, 표준편차: {stats['bmi_std']:.2f}")
    for status, count in stats['status_count'].items():
        print(f"{status}: {count}명")

def menu_add(manager):
    """메뉴 1: 값 입력 → manager.add_record → 결과 출력"""
    name = input("이름: ")
    gender = input("성별(남/여): ")
    birth_year = input_int("생년: ")
    height = input_float("키: ")
    weight = input_float("몸무게: ")
    record = manager.add_record(name, birth_year, gender, height, weight)

    if record is None:
        print("이미 등록된 사람입니다.")
    else:
        print(f"등록 완료: {record.id}")

def menu_search(manager):
    """메뉴 3: 검색어 입력 → 결과 표 출력 → 1건이면 상세 출력"""
    keyword = input("검색어: ")
    results = manager.search(keyword)
    print_table(results)
    if len(results) == 1:
        print_detail(results[0])

def menu_edit_delete(manager):
    """메뉴 4: 식별번호 입력 → 상세 출력 → 수정 또는 삭제"""
    record_id = input("식별번호: ")
    record = manager.find_by_id(record_id)

    if record is None:
        print("없는 식별번호입니다.")
        return

    print_detail(record)
    choice = input("1.수정  2.삭제: ")
    if choice == "1":
        new_height = input_float("새 키: ")
        new_weight = input_float("새 몸무게: ")
        manager.update_record(record_id, height=new_height, weight=new_weight)
        print_detail(manager.find_by_id(record_id))

    elif choice == "2":
        confirm = input("정말 삭제할까요? (y/n): ")
        if confirm.lower() == "y":
            manager.delete_record(record_id)
            print("삭제 완료.")

    else:
        print("잘못된 선택입니다.")

def menu_load(manager, db):
    """메뉴 6: 모듈1(HealthDB)로 파일을 읽어 HealthRecord 목록으로 바꿔 manager 에 넘긴다."""
    try:
        json_data, csv_data, txt_data, pkl_data = db.load_data()
        records = [dict_to_record(d) for d in json_data]
        manager.set_records(records)
        print(f"{len(records)}건 불러왔습니다.")
    except Exception as e:
        print(f"불러오기 실패: {e}")

def menu_save(manager, db):
    """메뉴 7: manager 의 데이터를 모듈1(HealthDB)로 4가지 파일에 저장한다."""
    if not manager.get_all():
        print("저장할 데이터가 없습니다.")
        return
    dict_list = manager.to_dict_list()
    txt_rows = [list(map(str, d.values())) for d in dict_list]
    try:
        db.save_data(dict_list, dict_list, txt_rows, dict_list)
        print("저장 완료.")
    except Exception as e:
        print(f"저장 실패: {e}")

def main():
    """콘솔 프로그램 시작점: 파일 읽기 → 메뉴 반복."""
    db = HealthDB()
    manager = HealthManager()
    menu_load(manager, db)
    while True:
        print_menu()
        choice = input("선택: ")
        if choice == "1":
            menu_add(manager)
        elif choice == "2":
            print_table(manager.get_all())
        elif choice == "3":
            menu_search(manager)
        elif choice == "4":
            menu_edit_delete(manager)
        elif choice == "5":
            print_statistics(manager.get_statistics())
        elif choice == "6":
            menu_load(manager, db)
        elif choice == "7":
            menu_save(manager, db)
        elif choice == "0":
            print("프로그램을 종료합니다.")
            break
        else:
            print("잘못된 선택입니다.")

