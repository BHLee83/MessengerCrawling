import os
import glob
import re
from datetime import datetime



def search(strTarget):
    '''주어진 텍스트가 포함된 내용 검색'''    
    today_date = datetime.now().strftime('%Y%m%d')  # 오늘 날짜를 'YYYYMMDD' 형식으로 설정
    ret = update(today_date)

    result = []
    for i in ret:
        for j in i:
            if strTarget in j:
                result.append(j)
    return result


def update(strToday):
    # 특정 디렉토리 경로 설정
    directory_path = 'C:/Users/infomax/Documents/K-Bond Messenger Chat'
    
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
    exceptStr = ['자동 대화 저장 시작', '입장', '퇴장', '감사' '있나', '잇나', '있으', '잇으', '있을', '잇을', '확정', 'ㅎㅈ', '앗', '넵']
    pattern_time = r'\(\d{2}:\d{2}:\d{2}\)'  # 시간을 찾기 위한 정규 표현식 패턴
    combined_content = {}
    for t, file_path in latest_files.values():
        with open(file_path, 'r', encoding='cp949') as file:
            for line in file:   # 파일을 줄 단위로 읽으면서
                if not any(except_word in line for except_word in exceptStr):   # 줄에 제외할 문자열이 없는 경우만 combined_content에 추가
                    match = re.search(pattern_time, line)
                    time = match.group(0) if match else list(combined_content.keys())[-1]
                    time = time.strip('()')
                    if time not in combined_content:
                        combined_content[time] = []
                    combined_content[time].append(line)

    sorted_content = {key: combined_content[key] for key in sorted(combined_content)}

    # 결과 반환
    return sorted_content.values()