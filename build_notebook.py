import nbformat as nbf
from pathlib import Path

OUTPUT = Path('/workspace/student_data_cleaning.ipynb')
nb = nbf.v4.new_notebook()
cells = []

def md(t): cells.append(nbf.v4.new_markdown_cell(t))
def code(t): cells.append(nbf.v4.new_code_cell(t))

md("# Student Data Cleaning / 学生数据清洗")

code("""import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder

data = pd.read_csv('/workspace/.uploads/23091186-5ec3-4346-9498-dc542bc22971_student_data_messy.csv')
data.head()
""")

md("## 1. 列名规范化 / Clean column names")
code("""data.columns = data.columns.str.strip().str.lower().str.replace(' ', '_', regex=False)
data.columns.tolist()
""")

md("## 2. 缺失值符号统一 / Replace missing markers")
code("""data = data.replace(['', 'NA', 'N/A', '?', 'missing'], np.nan)
data.isna().sum()
""")

md("## 3. 数值转换 / Convert numeric columns")
code("""numeric_cols = ['age','attendance_pct','homework','presentation','project','height_cm','weight_kg']
for col in numeric_cols:
    data[col] = pd.to_numeric(data[col], errors='coerce')
data[numeric_cols].dtypes
""")

md("## 4. 范围校验 / Validate ranges")
code("""data.loc[~data['age'].between(16,80), 'age'] = np.nan
data.loc[~data['attendance_pct'].between(0,100), 'attendance_pct'] = np.nan
data.loc[~data['height_cm'].between(130,220), 'height_cm'] = np.nan
data.loc[~data['weight_kg'].between(35,200), 'weight_kg'] = np.nan
""")

md("## 5. 日期解析 / Parse dates")
code("""data['enrollment_date'] = pd.to_datetime(data['enrollment_date'], errors='coerce')
data['enrollment_date'].head()
""")

md("## 6. 处理缺失值 / Fill missing values")
code("""data['age'].fillna(data['age'].median(), inplace=True)
data['height_cm'].fillna(data['height_cm'].median(), inplace=True)
data['weight_kg'].fillna(data['weight_kg'].median(), inplace=True)
data['gender'].fillna(data['gender'].mode()[0], inplace=True)
data['major'].fillna(data['major'].mode()[0], inplace=True)
data['city'].fillna(data['city'].mode()[0], inplace=True)
""")

md("## 7. 删除重复 / Remove duplicates")
code("""data = data.drop_duplicates()
data.shape
""")

md("## 8. 统一格式 / Standardize categories")
code("""data['gender'] = data['gender'].str.lower().map({'m':'Male','male':'Male','f':'Female','female':'Female'})
data['major'] = data['major'].str.lower().str.replace('.','').map({'cs':'Computer Science','computer science':'Computer Science','ai':'Artificial Intelligence','artificial intelligence':'Artificial Intelligence','data science':'Data Science'})
data['city'] = data['city'].str.title()
""")

md("## 9. 邮箱清理 / Clean email")
code("""data['email'] = data['email'].str.strip().str.lower()
data['email_valid'] = data['email'].str.contains('@', na=False)
""")

md("## 10. 编码 / Encoding")
code("""data = pd.get_dummies(data, columns=['city'], prefix='city')
le = LabelEncoder()
data['gender_encoded'] = le.fit_transform(data['gender'])
data['major_encoded'] = le.fit_transform(data['major'])
""")

md("## 11. 数值缩放 / Scale numeric")
code("""scaler = StandardScaler()
data['age_scaled'] = scaler.fit_transform(data[['age']])
""")

md("## 12. 保存 / Save")
code("""data.to_csv('/workspace/student_data_cleaned.csv', index=False)
print("处理后的数据：")
data.head()
""")

nb['cells'] = cells
nb['metadata'] = {
    'kernelspec': {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'},
    'language_info': {'name': 'python', 'version': '3.x'}
}
nbf.write(nb, OUTPUT)
print('Notebook generated:', OUTPUT)
