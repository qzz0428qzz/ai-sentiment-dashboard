"""
数据清洗脚本 —— 基于 Data_Cleaning_Teaching_Bilingual.ipynb 模板
对 student_data_messy.csv 进行完整清洗
"""

import pandas as pd
import numpy as np
from pathlib import Path

DATA_FILE = Path('/workspace/.uploads/23091186-5ec3-4346-9498-dc542bc22971_student_data_messy.csv')
OUTPUT_CSV = Path('/workspace/student_data_cleaned.csv')
OUTPUT_EXCEL = Path('/workspace/student_data_cleaned.xlsx')


def clean_student_data(raw_df: pd.DataFrame) -> pd.DataFrame:
    data = raw_df.copy()

    # 1. 清理列名（去空格、转小写、空格替换为下划线）
    data.columns = data.columns.str.strip().str.lower().str.replace(' ', '_', regex=False)

    # 2. 统一缺失值符号（'', ' ', NA, N/A, na, n/a, ?, missing 等 -> NaN）
    missing_markers = ['', ' ', 'NA', 'N/A', 'na', 'n/a', '?', 'missing', 'Missing']
    data = data.replace(missing_markers, np.nan)

    # 3. 文本列去首尾空格
    text_cols = data.select_dtypes(include=['object', 'string']).columns
    for col in text_cols:
        data[col] = data[col].astype('string').str.strip()

    # 4. 统一性别类别
    gender_map = {'m': 'Male', 'male': 'Male', 'f': 'Female', 'female': 'Female'}
    data['gender'] = data['gender'].str.lower().map(gender_map)

    # 5. 统一专业名称
    major_key = data['major'].str.lower().str.replace('.', '', regex=False)
    major_map = {
        'cs': 'Computer Science',
        'computer science': 'Computer Science',
        'ai': 'Artificial Intelligence',
        'artificial intelligence': 'Artificial Intelligence',
        'data science': 'Data Science',
    }
    data['major'] = major_key.map(major_map)

    # 6. 统一城市名称大小写
    data['city'] = data['city'].str.title()

    # 7. 数值列转换（非法值 -> NaN）
    numeric_cols = ['age', 'attendance_pct', 'homework', 'presentation',
                    'project', 'height_cm', 'weight_kg']
    for col in numeric_cols:
        data[col] = pd.to_numeric(data[col], errors='coerce')

    # 8. 数值范围校验，超出合理范围的视为缺失
    ranges = {
        'age': (16, 80),
        'attendance_pct': (0, 100),
        'homework': (0, 20),
        'presentation': (0, 20),
        'project': (0, 50),
        'height_cm': (130, 220),
        'weight_kg': (35, 200),
    }
    for col, (low, high) in ranges.items():
        data.loc[~data[col].between(low, high), col] = np.nan

    # 9. 解析日期（非法日期 -> NaT）
    data['enrollment_date'] = pd.to_datetime(
        data['enrollment_date'], errors='coerce', format='mixed'
    )

    # 10. 删除重复行
    data = data.drop_duplicates().reset_index(drop=True)

    # 11. 数值缺失值用中位数填补
    for col in numeric_cols:
        data[col] = data[col].fillna(data[col].median())

    # 12. 类别缺失值用众数填补
    for col in ['gender', 'major', 'city']:
        data[col] = data[col].fillna(data[col].mode(dropna=True)[0])

    # 13. 最终数据类型调整
    data['age'] = data['age'].round().astype('Int64')
    for col in ['gender', 'major', 'city']:
        data[col] = data[col].astype('category')

    # 14. 邮箱清理与有效性校验
    data['email'] = data['email'].str.strip().str.lower()
    data['email_valid'] = data['email'].str.contains('@', na=False)

    return data


def main():
    # 读取原始数据
    df = pd.read_csv(DATA_FILE)
    print('=' * 60)
    print('原始数据 / Raw data')
    print('=' * 60)
    print('形状 / Shape:', df.shape)
    print('重复行 / Duplicate rows:', df.duplicated().sum())
    print('缺失单元格 / Missing cells:', int(df.isna().sum().sum()))
    print()

    # 执行清洗
    clean = clean_student_data(df)

    print('=' * 60)
    print('清洗后数据 / Cleaned data')
    print('=' * 60)
    print('形状 / Shape:', clean.shape)
    print('重复行 / Duplicate rows:', clean.duplicated().sum())
    print('缺失单元格 / Missing cells:', int(clean.isna().sum().sum()))
    print()

    # 数据类型
    print('数据类型 / Dtypes:')
    print(clean.dtypes)
    print()

    # 数值范围校验
    checks = {
        'age_valid': clean['age'].between(16, 80).all(),
        'attendance_valid': clean['attendance_pct'].between(0, 100).all(),
        'homework_valid': clean['homework'].between(0, 20).all(),
        'presentation_valid': clean['presentation'].between(0, 20).all(),
        'project_valid': clean['project'].between(0, 50).all(),
        'height_valid': clean['height_cm'].between(130, 220).all(),
        'weight_valid': clean['weight_kg'].between(35, 200).all(),
    }
    print('数值范围校验 / Range checks:')
    for k, v in checks.items():
        print(f'  {k}: {v}')
    print()

    # 缺失值统计
    print('各列缺失值 / Missing values by column:')
    print(clean.isna().sum().sort_values(ascending=False).to_string())
    print()

    # 前 10 行预览
    print('前 10 行预览 / First 10 rows:')
    print(clean.head(10).to_string(index=False))
    print()

    # 保存
    clean.to_csv(OUTPUT_CSV, index=False)
    clean.to_excel(OUTPUT_EXCEL, index=False)
    print(f'已保存 / Saved: {OUTPUT_CSV}')
    print(f'已保存 / Saved: {OUTPUT_EXCEL}')


if __name__ == '__main__':
    main()
