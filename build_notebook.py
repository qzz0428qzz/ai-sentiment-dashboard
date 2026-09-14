"""
生成 student_data 数据清洗 Notebook（.ipynb）
使用 nbformat 库确保输出合法的 Notebook JSON
"""

import nbformat as nbf
from pathlib import Path

OUTPUT = Path('/workspace/student_data_cleaning.ipynb')

nb = nbf.v4.new_notebook()
cells = []


def md(text):
    cells.append(nbf.v4.new_markdown_cell(text))


def code(text):
    cells.append(nbf.v4.new_code_cell(text))


# ========== 标题 ==========
md("""# Student Data Cleaning / 学生数据清洗

整合了两个模板的清洗流程：
- 原教学模板（Data_Cleaning_Teaching_Bilingual.ipynb）
- 同学模板（sklearn 方法 + 箱线图 + 独热编码 + 数值缩放）
""")

# ========== 1. 导入库 ==========
md("""## 1. Import libraries / 导入库""")
code("""import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, LabelEncoder

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 160)
print('pandas:', pd.__version__)
""")

# ========== 2. 读取数据 ==========
md("""## 2. Read the data / 读取数据""")
code("""DATA_FILE = Path('/workspace/.uploads/23091186-5ec3-4346-9498-dc542bc22971_student_data_messy.csv')

df = pd.read_csv(DATA_FILE)
print('Shape / 形状:', df.shape)
print('Duplicate rows / 重复行:', df.duplicated().sum())
print('Missing cells / 缺失单元格:', int(df.isna().sum().sum()))
df.head()
""")

# ========== 3. 初步检查 ==========
md("""## 3. Inspect the data / 初步检查""")
code("""df.info()""")
code("""df.describe(include='all').T""")

# ========== 4. 开始清洗 ==========
md("""# Part A — Cleaning / 第一部分：数据清洗""")

code("""clean = df.copy()
print('Raw shape / 原始形状:', df.shape)
""")

# 4.1 列名规范化
md("""### 4.1 Clean column names / 清理列名""")
code("""clean.columns = (
    clean.columns
         .str.strip()
         .str.lower()
         .str.replace(' ', '_', regex=False)
)
clean.columns.tolist()
""")

# 4.2 缺失值符号统一
md("""### 4.2 Replace missing-value markers / 统一缺失值符号""")
code("""missing_markers = ['', ' ', 'NA', 'N/A', 'na', 'n/a', '?', 'missing', 'Missing']
clean = clean.replace(missing_markers, np.nan)
clean.isna().sum().sort_values(ascending=False)
""")

# 4.3 文本去空格
md("""### 4.3 Trim text / 去除文本多余空格""")
code("""text_cols = clean.select_dtypes(include=['object', 'string']).columns
for col in text_cols:
    clean[col] = clean[col].astype('string').str.strip()
clean[['name', 'gender', 'major', 'email', 'city']].head(8)
""")

# 4.4 统一性别
md("""### 4.4 Standardize gender / 统一性别类别""")
code("""gender_map = {'m': 'Male', 'male': 'Male', 'f': 'Female', 'female': 'Female'}
clean['gender'] = clean['gender'].str.lower().map(gender_map)
clean['gender'].value_counts(dropna=False)
""")

# 4.5 统一专业
md("""### 4.5 Standardize major / 统一专业名称""")
code("""major_key = clean['major'].str.lower().str.replace('.', '', regex=False)
major_map = {
    'cs': 'Computer Science',
    'computer science': 'Computer Science',
    'ai': 'Artificial Intelligence',
    'artificial intelligence': 'Artificial Intelligence',
    'data science': 'Data Science',
}
clean['major'] = major_key.map(major_map)
clean['major'].value_counts(dropna=False)
""")

# 4.6 统一城市
md("""### 4.6 Standardize city / 统一城市大小写""")
code("""clean['city'] = clean['city'].str.title()
clean['city'].value_counts(dropna=False)
""")

# 4.7 数值转换
md("""### 4.7 Convert numeric columns / 转换数值列""")
code("""numeric_cols = ['age', 'attendance_pct', 'homework', 'presentation',
                'project', 'height_cm', 'weight_kg']
for col in numeric_cols:
    clean[col] = pd.to_numeric(clean[col], errors='coerce')
clean[numeric_cols].dtypes
""")

# 4.8 范围校验
md("""### 4.8 Validate ranges / 检查数值范围""")
code("""rules = {
    'age': (16, 80),
    'attendance_pct': (0, 100),
    'homework': (0, 20),
    'presentation': (0, 20),
    'project': (0, 50),
    'height_cm': (130, 220),
    'weight_kg': (35, 200),
}
for col, (low, high) in rules.items():
    invalid = ~clean[col].between(low, high) & clean[col].notna()
    if invalid.any():
        print(f'{col}: invalid values / 无效值 ->', clean.loc[invalid, col].tolist())
""")

# 4.9 超出范围置为缺失
md("""### 4.9 Replace impossible values with missing / 将不合理值设为缺失""")
code("""for col, (low, high) in rules.items():
    clean.loc[~clean[col].between(low, high), col] = np.nan
clean[numeric_cols].isna().sum()
""")

# 4.10 日期解析
md("""### 4.10 Parse dates / 解析日期""")
code("""clean['enrollment_date'] = pd.to_datetime(
    clean['enrollment_date'], errors='coerce', format='mixed'
)
print('Invalid/missing dates / 无效或缺失日期:')
clean.loc[clean['enrollment_date'].isna(), ['student_id', 'name', 'enrollment_date']]
""")

# 4.11 删除重复
md("""### 4.11 Remove duplicates / 删除重复行""")
code("""print('Duplicates before / 删除前重复行:', clean.duplicated().sum())
clean = clean.drop_duplicates().reset_index(drop=True)
print('Shape after / 删除后形状:', clean.shape)
""")

# 4.12 sklearn 缺失值填充
md("""### 4.12 Fill missing values with sklearn SimpleImputer / 用 sklearn 填充缺失值""")
code("""# 数值列用中位数填充
num_imputer = SimpleImputer(strategy='median')
clean[numeric_cols] = num_imputer.fit_transform(clean[numeric_cols])

# 类别列用众数填充
for col in ['gender', 'major', 'city']:
    mode_value = clean[col].mode(dropna=True)[0]
    clean[col] = clean[col].fillna(mode_value)
    print(f'{col}: mode / 众数 = {mode_value}')

clean.isna().sum().sort_values(ascending=False)
""")

# 4.13 异常值检测
md("""### 4.13 Outlier detection (IQR / boxplot) / 异常值检测""")
code("""def iqr_outlier_mask(series, factor=1.5):
    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)
    iqr = q3 - q1
    lower = q1 - factor * iqr
    upper = q3 + factor * iqr
    mask = (series < lower) | (series > upper)
    return mask, lower, upper

mask, lower, upper = iqr_outlier_mask(clean['weight_kg'])
print(f'Weight IQR limits / 体重 IQR 范围: [{lower:.2f}, {upper:.2f}]')
if mask.any():
    print(f'Detected {mask.sum()} potential outliers / 检测到潜在异常值:')
    print(clean.loc[mask, ['student_id', 'name', 'weight_kg']])
else:
    print('No outliers detected / 未检测到异常值')
""")

# 4.14 邮箱清理
md("""### 4.14 Clean email / 清理邮箱""")
code("""clean['email'] = clean['email'].str.strip().str.lower()
clean['email_valid'] = clean['email'].str.contains('@', na=False)
clean[['email', 'email_valid']].head(10)
""")

# 4.15 最终类型调整
md("""### 4.15 Final dtypes / 最终数据类型""")
code("""clean['age'] = clean['age'].round().astype('Int64')
for col in ['gender', 'major', 'city']:
    clean[col] = clean[col].astype('category')
clean.dtypes
""")

# ========== 5. 特征工程 ==========
md("""# Part B — Feature Engineering / 第二部分：特征工程""")

# 5.1 StandardScaler
md("""### 5.1 StandardScaler / 数值标准化""")
code("""scaler = StandardScaler()
scale_cols = ['attendance_pct', 'homework', 'presentation',
              'project', 'height_cm', 'weight_kg']
scaled = pd.DataFrame(
    scaler.fit_transform(clean[scale_cols]),
    columns=[f'{c}_scaled' for c in scale_cols],
    index=clean.index
)
clean = pd.concat([clean, scaled], axis=1)
clean[[f'{c}_scaled' for c in scale_cols]].head()
""")

# 5.2 独热编码
md("""### 5.2 One-hot encoding (get_dummies) / 独热编码""")
code("""clean = pd.get_dummies(clean, columns=['city'], prefix='city', dtype=int)
clean.filter(like='city_').head()
""")

# 5.3 LabelEncoder
md("""### 5.3 LabelEncoder / 标签编码""")
code("""le_gender = LabelEncoder()
clean['gender_encoded'] = le_gender.fit_transform(clean['gender'])
print('gender mapping / 性别映射:', dict(zip(le_gender.classes_, range(len(le_gender.classes_)))))

le_major = LabelEncoder()
clean['major_encoded'] = le_major.fit_transform(clean['major'])
print('major mapping / 专业映射:', dict(zip(le_major.classes_, range(len(le_major.classes_)))))
""")

# ========== 6. 验证 ==========
md("""# Part C — Validation / 第三部分：清洗后验证""")

code("""print('Final shape / 最终形状:', clean.shape)
print('Duplicates / 重复行:', clean.duplicated().sum())
print('Missing cells / 缺失单元格:', int(clean.isna().sum().sum()))
""")

code("""checks = {
    'age_valid': clean['age'].between(16, 80).all(),
    'attendance_valid': clean['attendance_pct'].between(0, 100).all(),
    'homework_valid': clean['homework'].between(0, 20).all(),
    'presentation_valid': clean['presentation'].between(0, 20).all(),
    'project_valid': clean['project'].between(0, 50).all(),
    'height_valid': clean['height_cm'].between(130, 220).all(),
    'weight_valid': clean['weight_kg'].between(35, 200).all(),
}
checks
""")

code("""clean.head(10)""")

# ========== 7. 保存 ==========
md("""# Part D — Save / 第四部分：保存清洗结果""")
code("""OUTPUT_CSV = Path('/workspace/student_data_cleaned.csv')
OUTPUT_EXCEL = Path('/workspace/student_data_cleaned.xlsx')

clean.to_csv(OUTPUT_CSV, index=False)
clean.to_excel(OUTPUT_EXCEL, index=False)

print('Saved / 已保存:', OUTPUT_CSV.resolve())
print('Saved / 已保存:', OUTPUT_EXCEL.resolve())
""")

# 组装
nb['cells'] = cells
nb['metadata'] = {
    'kernelspec': {
        'display_name': 'Python 3',
        'language': 'python',
        'name': 'python3'
    },
    'language_info': {
        'name': 'python',
        'version': '3.x'
    }
}

nbf.write(nb, OUTPUT)
print(f'Notebook generated: {OUTPUT}')
