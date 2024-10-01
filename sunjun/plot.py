import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# 각 지역의 상관계수를 시각화하는 함수 (영어로 제목 설정)
def plot_correlation_heatmap(corr_matrix, region_name):
    plt.figure(figsize=(10, 8))
    sns.heatmap(corr_matrix, annot=True, fmt=".2f", cmap='coolwarm', vmin=-1, vmax=1)
    plt.title(f"Correlation between climate factors and electricity usage in {region_name}", fontsize=15)
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    plt.tight_layout()
    plt.show()

# 각 지역의 날씨 데이터와 전력 데이터를 읽어올다.
regions = ['gyeonggi', 'jeju', 'jeonnam', 'seoul', 'ulsan']
correlation_matrices = {}

# 데이터 경로 설정
base_weather_path = './weather data/'
base_power_path = './power data/'

# 지점 코드와 지역명 매핑 테이블
station_to_region = {
    'gyeonggi': ['98', '99', '119', '202', '203'],
    'jeju': ['184', '185', '188', '189'],
    'jeonnam': ['168'],
    'seoul': ['108'],
    'ulsan': ['152']
}

# 전국 데이터를 담을 리스트
national_data_list = []

# 각 지역의 데이터를 분석하고 시각화
for region in regions:
    print(f"\n==== {region.upper()} analysis ====")

    # 날씨 데이터와 전력 데이터를 읽어옴
    weather_data = pd.read_csv(f'{base_weather_path}{region}_weather.csv', encoding='cp949')
    power_data = pd.read_csv(f'{base_power_path}{region}_power.csv', encoding='cp949')

    # 각 열을 문자열로 변환 및 공백 제거
    weather_data['지점'] = weather_data['지점'].astype(str).str.strip()
    power_data['지역'] = power_data['지역'].astype(str).str.strip()

    # 지점 코드와 지역명 매핑 (전력 데이터의 지역명을 지점 코드로 변환)
    weather_data = weather_data[weather_data['지점'].isin(station_to_region[region])]
    power_data['지점'] = station_to_region[region][0]

    # 날짜에서 시간 단위를 제외하고 일 단위로 통일 (날짜 형식 통일)
    weather_data['일시'] = pd.to_datetime(weather_data['일시']).dt.date
    power_data['거래일자'] = pd.to_datetime(power_data['거래일자']).dt.date

    # 두 데이터를 병합
    merged_data = pd.merge(weather_data, power_data, left_on=['일시', '지점'], right_on=['거래일자', '지점'], how='inner')

    # 병합된 데이터 상태 확인
    if merged_data.shape[0] > 0:
        # 열 이름 공백 제거
        merged_data.columns = merged_data.columns.str.strip()

        # 열 이름을 영어로 변환
        merged_data = merged_data.rename(columns={
            '기온(°C)': 'Temperature(°C)',
            '강수량(mm)': 'Precipitation(mm)',
            '풍속(m/s)': 'Wind Speed(m/s)',
            '풍향(16방위)': 'Wind Direction(16 points)',
            '습도(%)': 'Humidity(%)',
            '현지기압(hPa)': 'Local Pressure(hPa)',
            '일조(hr)': 'Sunshine(hr)',
            '일사(MJ/m2)': 'Solar Radiation(MJ/m2)',
            '적설(cm)': 'Snowfall(cm)',
            '전운량(10분위)': 'Cloudiness(10 scale)',
            '지면온도(°C)': 'Ground Temperature(°C)',
            '전력거래량(MWh)': 'Power Usage(MWh)'
        })

        # 실제 열 이름 확인
        print(f"Columns after merge: {merged_data.columns.tolist()}")

        # 상수 값(모든 값이 동일한 열) 제거
        non_constant_columns = merged_data.loc[:, (merged_data != merged_data.iloc[0]).any()]

        # 분석에 사용할 열 정의 (영문명으로 변경)
        selected_columns = ['Temperature(°C)', 'Precipitation(mm)', 'Wind Speed(m/s)', 'Wind Direction(16 points)',
                            'Humidity(%)', 'Local Pressure(hPa)', 'Sunshine(hr)', 'Solar Radiation(MJ/m2)',
                            'Snowfall(cm)', 'Cloudiness(10 scale)', 'Ground Temperature(°C)', 'Power Usage(MWh)']

        # 숫자형 열만 선택하여 결측값을 평균값으로 채움
        numeric_columns = non_constant_columns[selected_columns].select_dtypes(include=['float64', 'int64'])
        merge_data_clean = numeric_columns.fillna(numeric_columns.mean())

        # 상관계수 계산
        correlation_matrix = merge_data_clean.corr()

        # 상관계수 시각화
        plot_correlation_heatmap(correlation_matrix, region.upper())

        # 상관계수를 저장
        correlation_matrices[region] = correlation_matrix

        # 전국 데이터를 위해 추가
        national_data_list.append(merge_data_clean)

# 전국 데이터를 합쳐서 분석
national_data = pd.concat(national_data_list)

# 전국 상관계수 계산
national_corr_matrix = national_data.corr()

# 전국 상관계수 시각화
plot_correlation_heatmap(national_corr_matrix, "National")
