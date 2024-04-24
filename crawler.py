import os
import glob
import re
import pandas as pd
from datetime import datetime
from config import Config



# 최대 메시지 갯수 제한
MAX_COUNT = Config.MAX_COUNT

# 검색 결과에서 제외하기 위한 회사명 리스트
CORP = Config.CORP

def search(strTarget):
    '''주어진 텍스트가 포함된 내용 검색'''    
    today_date = datetime.now().strftime('%Y%m%d')  # 오늘 날짜를 'YYYYMMDD' 형식으로 설정
    df = update(today_date)

    # 'Content' 열에서 'target' 문자열이 포함된 행 찾기
    filtered_df = df[df['Content'].str.contains(strTarget, na=False)]

    # 제외 조건: CORP 뒤에 strTarget이 한 번만 오는 경우, 그리고 strTarget 뒤에 lstExcept가 또 나오지 않는 경우
    def exclude_condition(row):
        if row['Content'].count(strTarget) == 1:
            target_index = row['Content'].find(strTarget)
            substring_before_target = row['Content'][:target_index] # strTarget 바로 앞의 문자열
            substring_after_target = row['Content'][target_index + len(strTarget):] # strTarget 바로 뒤의 문자열
            
            # strTarget 앞의 문자열에서 CORP의 단어가 위치하는지 검사
            for word in CORP:
                if word in substring_before_target:
                    # strTarget 뒤의 문자열에서 CORP의 단어가 나오지 않는 경우만 True
                    for word in CORP:
                        if word in substring_after_target:
                            return True  # CORP가 strTarget 뒤에 존재하므로 제외하지 않음
                    return False  # CORP가 strTarget 뒤에 존재하지 않으므로 제외함
        return True  # strTarget이 두 번 이상 포함되었거나 다른 조건을 만족하지 않는 경우


    filtered_df = filtered_df[filtered_df.apply(exclude_condition, axis=1)]

    return filtered_df.tail(MAX_COUNT)


def update(strToday):
    # 특정 디렉토리 경로 설정
    directory_path = Config.MessengerPath
    
    # 오늘 날짜와 .txt 확장자를 가진 파일들을 찾습니다.
    pattern = f"{directory_path}/*_{strToday}_*.txt"
    files = glob.glob(pattern)

    # 같은 분류와 방 이름의 가장 최신 파일을 찾기 위한 딕셔너리
    latest_files = {}

    # 파일들을 순회하며 가장 최근의 파일을 선택
    for file_path in files:
        # 파일 이름을 분해하여 구성요소를 얻습니다.
        base_name = os.path.basename(file_path).split('.')[0]
        parts = base_name.split('_')
        if len(parts) < 4:  # 유효하지 않은 파일명은 건너뜁니다.
            continue
        
        # 분류와 방 이름을 키로 사용
        category_room = '_'.join(parts[:-2])
        
        # 현재 파일의 시간과 기존에 저장된 파일의 시간을 비교하여 더 최근 것을 저장
        current_time = parts[-1]
        if category_room not in latest_files or latest_files[category_room][0] < current_time:
            latest_files[category_room] = (current_time, file_path)

    # 최종 선택된 파일들의 내용을 읽어 합칩니다.
    exceptStr = Config.exceptStr
    pattern_time = r'\(\d{2}:\d{2}:\d{2}\)'  # 시간을 찾기 위한 정규 표현식 패턴
    # combined_content = {}
    data = []
    for t, file_path in latest_files.values():
        with open(file_path, 'r', encoding='cp949') as file:
            last_name = None
            last_time = None
            last_content = None
            for line in file:   # 파일을 줄 단위로 읽으면서
                if not any(except_word in line for except_word in exceptStr):   # 줄에 제외할 문자열이 없는 경우만 data 추가
                    match = re.search(pattern_time, line)
                    if match:   # 새로운 시간이 발견되면 업데이트
                        last_name = line.split(' (')[0].strip()
                        last_time = match.group(0).strip('()')
                        last_content = line.split(' : ')[1].strip() if ' : ' in line else last_content
                    else:
                        # 시간 정보가 없는 경우 이전 시간과 이름을 그대로 사용하고
                        last_content = line.strip()  # 내용만 업데이트
                    if last_time is not None:
                        data.append([last_name, last_time, last_content, line.strip()])  # 이름, 시간, 내용, 원본을 데이터 리스트에 추가

    # sorted_content = {key: combined_content[key] for key in sorted(combined_content)}
    
    df_raw = pd.DataFrame(data, columns=['Name', 'Time', 'Content', 'Original'])    # 데이터 리스트를 데이터프레임으로 변환
    df_sorted = df_raw.sort_values(by='Time', ascending=True, kind='stable')   # Time 기준 정렬
    df_unique = df_sorted.drop_duplicates(subset='Content', keep='last')    # Content 기준 중복 제거

    # 결과 반환
    return df_unique.reset_index().drop('index', axis=1)