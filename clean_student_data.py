"""
整合版数据清洗脚本
结合了 Data_Cleaning_Teaching_Bilingual.ipynb（原模板）
和同学模板（sklearn 方法 + 箱线图 + 独热编码 + 数值缩放）
对 student_data_messy.csv 进行完整清洗
"""

import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, LabelEncoder

DATA_FILE = Path('/workspace/.uploads/23091186-5ec3-4346-9498-dc542bc22971_student_data_messy.csv')
OUTPUT_CSV = Path('/workspace/student_data_cleaned.csv')
OUTPUT_EXCEL = Path('/workspace/student_data_cleaned.xlsx')


def clean_student_data(raw_df: pd.DataFrame) -> pd.DataFrame:
    data = raw_df.copy()

    # ========== 1. 列名规范化（原模板） ==========
    data.columns = data.columns.str.strip().str.lower().str.replace(' ', '_', regex=False)

    # ========== 2. 缺失值符号统一（原模板） ==========
    missing_markers = ['', ' ', 'NA', 'N/A', 'na', 'n/a', '?', 'missing', 'Missing']
    data = data.replace(missing_markers, np.nan)

    # ========== 3. 文本列去首尾空格（原模板） ==========
    text_cols = data.select_dtypes(include=['object', 'string']).columns
    for col in text_cols:
        data[col] = data[col].astype('string').str.strip()

    # ========== 4. 统一性别类别（原模板 + 同学模板思路） ==========
    gender_map = {'m': 'Male', 'male': 'Male', 'f': 'Female', 'female': 'Female'}
    data['gender'] = data['gender'].str.lower().map(gender_map)

    # ========== 5. 统一专业名称（原模板） ==========
    major_key = data['major'].str.lower().str.replace('.', '', regex=False)
    major_map = {
        'cs': 'Computer Science',
        'computer science': 'Computer Science',
        'ai': 'Artificial Intelligence',
        'artificial intelligence': 'Artificial Intelligence',
        'data science': 'Data Science',
    }
    data['major'] = major_key.map(major_map)

    # ========== 6. 统一城市名称大小写（原模板） ==========
    data['city'] = data['city'].str.title()

    # ========== 7. 数值列转换（原模板 + 同学模板） ==========
    numeric_cols = ['age', 'attendance_pct', 'homework', 'presentation',
                    'project', 'height_cm', 'weight_kg']
    for col in numeric_cols:
        data[col] = pd.to_numeric(data[col], errors='coerce')

    # ========== 8. 数值范围校验，超出范围置为缺失（原模板） ==========
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

    # ========== 9. 解析日期（原模板） ==========
    data['enrollment_date'] = pd.to_datetime(
        data['enrollment_date'], errors='coerce', format='mixed'
    )

    # ========== 10. 删除重复行（两个模板共有） ==========
    data = data.drop_duplicates().reset_index(drop=True)

    # ========== 11. 缺失值处理：使用 sklearn SimpleImputer（同学模板） ==========
    # 数值列用中位数填充
    num_imputer = SimpleImputer(strategy='median')
    data[numeric_cols] = num_imputer.fit_transform(data[numeric_cols])

    # 类别列用众数填充
    cat_cols = ['gender', 'major', 'city']
    for col in cat_cols:
        mode_value = data[col].mode(dropna=True)[0]
        data[col] = data[col].fillna(mode_value)

    # ========== 12. 异常值检测：箱线图 + IQR 方法（同学模板思路） ==========
    def iqr_outlier_mask(series, factor=1.5):
        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1
        lower = q1 - factor * iqr
        upper = q3 + factor * iqr
        return (series < lower) | (series > upper), lower, upper

    # 对 weight_kg 做 IQR 异常值检测（仅记录，不删除，保留原模板"先调查再决定"原则）
    mask, lower, upper = iqr_outlier_mask(data['weight_kg'])
    print(f'[IQR] weight_kg 异常范围: [{lower:.2f}, {upper:.2f}]')
    if mask.any():
        print(f'[IQR] 检测到 {mask.sum()} 个潜在异常值（仅标记，未删除）：')
        print(data.loc[mask, ['student_id', 'name', 'weight_kg']].to_string(index=False))

    # ========== 13. 最终数据类型调整（原模板） ==========
    data['age'] = data['age'].round().astype('Int64')
    for col in cat_cols:
        data[col] = data[col].astype('category')

    # ========== 14. 邮箱清理与有效性校验（原模板） ==========
    data['email'] = data['email'].str.strip().str.lower()
    data['email_valid'] = data['email'].str.contains('@', na=False)

    # ========== 15. 数值缩放：StandardScaler（同学模板） ==========
    scaler = StandardScaler()
    scale_cols = ['attendance_pct', 'homework', 'presentation', 'project', 'height_cm', 'weight_kg']
    data_scaled = pd.DataFrame(
        scaler.fit_transform(data[scale_cols]),
        columns=[f'{c}_scaled' for c in scale_cols],
        index=data.index
    )
    data = pd.concat([data, data_scaled], axis=1)

    # ========== 16. 独热编码：get_dummies（同学模板） ==========
    # 对 city 做独热编码，新增 city_ 前缀列
    data = pd.get_dummies(data, columns=['city'], prefix='city', dtype=int)

    # 对 gender 和 major 做 LabelEncoder（同学模板）
    le_gender = LabelEncoder()
    data['gender_encoded'] = le_gender.fit_transform(data['gender'])
    print(f'[LabelEncoder] gender 映射: {dict(zip(le_gender.classes_, le_gender.transform(le_gender.classes_)))}')

    le_major = LabelEncoder()
    data['major_encoded'] = le_major.fit_transform(data['major'])
    print(f'[LabelEncoder] major 映射: {dict(zip(le_major.classes_, le_major.transform(le_major.classes_)))}')

    return data


def main():
    # 读取原始数据
    df = pd.read_csv(DATA_FILE)
    print('=' * 70)
    print('原始数据 / Raw data')
    print('=' * 70)
    print('形状 / Shape:', df.shape)
    print('重复行 / Duplicate rows:', df.duplicated().sum())
    print('缺失单元格 / Missing cells:', int(df.isna().sum().sum()))
    print()

    # 执行清洗
    clean = clean_student_data(df)

    print()
    print('=' * 70)
    print('清洗后数据 / Cleaned data')
    print('=' * 70)
    print('形状 / Shape:', clean.shape)
    print('重复行 / Duplicate rows:', clean.duplicated().sum())
    print('缺失单元格 / Missing cells:', int(clean.isna().sum().sum()))
    print()

    # 数据类型
    print('数据类型 / Dtypes:')
    print(clean.dtypes.to_string())
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
