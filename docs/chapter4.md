---
layout: default
title: "4장: 데이터 처리"
---

# 4장: 데이터 처리

## 개요

이 장에서는 대규모 데이터를 효율적으로 처리하는 방법을 배웁니다. **선언형 프로그래밍**, **논리 프로그래밍**, **SQL**, 그리고 **분산 컴퓨팅** 기초를 다룹니다.

---

## 📌 4.1장: 선언형 프로그래밍 (Declarative Programming)

### 명령형 vs 선언형

**명령형 (Imperative)**: 어떻게 하는가를 명시

```python
# 명령형: 단계별 지시
total = 0
for x in numbers:
    if x > 5:
        total += x * 2
print(total)
```

**선언형 (Declarative)**: 무엇을 원하는가를 명시

```python
# 선언형: 결과 정의
total = sum(x * 2 for x in numbers if x > 5)
```

### 함수형 스타일

```python
# 파이프라인 구성
def pipeline(data, *functions):
    result = data
    for f in functions:
        result = f(result)
    return result

# 각 단계 정의
filter_large = lambda nums: [x for x in nums if x > 5]
double = lambda nums: [x * 2 for x in nums]
sum_all = lambda nums: sum(nums)

# 사용
result = pipeline(numbers, filter_large, double, sum_all)
```

---

## 📌 4.2장: 논리 프로그래밍 (Logic Programming)

### 논리 프로그래밍 개념

논리 프로그래밍은 **사실(Facts)**과 **규칙(Rules)**로 프로그램을 작성합니다.

```
# 사실 (Facts)
parent(tom, bob)
parent(bob, alice)

# 규칙 (Rules)
grandparent(X, Z) :- parent(X, Y), parent(Y, Z)

# 쿼리 (Query)
?- grandparent(tom, alice)
```

### Python에서의 간단한 구현

```python
# 데이터베이스
facts = [
    ("parent", ("tom", "bob")),
    ("parent", ("bob", "alice")),
]

# 규칙
rules = {
    "grandparent": lambda x, z: any(
        ("parent", (x, y)) in facts and
        ("parent", (y, z)) in facts
        for y in range(100)
    )
}

# 쿼리
def query(relation, args):
    if relation == "parent":
        return ("parent", args) in facts
    elif relation == "grandparent":
        return rules["grandparent"](*args)

# 사용
print(query("parent", ("tom", "bob")))        # True
print(query("grandparent", ("tom", "alice"))) # True
```

---

## 📌 4.3장: SQL을 통한 데이터 조회

### SQL 기초

**SELECT**: 데이터 조회

```sql
-- 모든 학생의 이름과 학번
SELECT name, student_id FROM students;

-- 조건부 조회
SELECT name, grade FROM students WHERE grade >= 80;

-- 정렬
SELECT name, grade FROM students ORDER BY grade DESC;
```

### Python에서 SQL 사용

```python
import sqlite3

# 데이터베이스 연결
conn = sqlite3.connect(':memory:')
cursor = conn.cursor()

# 테이블 생성
cursor.execute('''
    CREATE TABLE students (
        id INTEGER PRIMARY KEY,
        name TEXT,
        grade INTEGER
    )
''')

# 데이터 삽입
cursor.execute("INSERT INTO students VALUES (1, '철수', 85)")
cursor.execute("INSERT INTO students VALUES (2, '영희', 92)")

# 데이터 조회
cursor.execute("SELECT * FROM students WHERE grade >= 90")
for row in cursor.fetchall():
    print(row)

conn.close()
```

### JOIN 연산

```sql
-- 내부 조인
SELECT students.name, courses.title
FROM students
INNER JOIN enrollments ON students.id = enrollments.student_id
INNER JOIN courses ON enrollments.course_id = courses.id;

-- 왼쪽 외부 조인
SELECT students.name, courses.title
FROM students
LEFT JOIN enrollments ON students.id = enrollments.student_id
LEFT JOIN courses ON enrollments.course_id = courses.id;
```

### 집계 함수

```sql
-- 학생 수
SELECT COUNT(*) FROM students;

-- 평균 성적
SELECT AVG(grade) FROM students;

-- 그룹별 집계
SELECT course_id, COUNT(*) as count
FROM enrollments
GROUP BY course_id
HAVING COUNT(*) > 5;
```

---

## 📌 4.4장: 데이터 프레임 (DataFrames)

### Pandas 소개

```python
import pandas as pd

# 데이터프레임 생성
df = pd.DataFrame({
    'name': ['철수', '영희', '민준'],
    'age': [30, 28, 35],
    'city': ['서울', '부산', '서울']
})

# 데이터 조회
print(df.head())              # 처음 5행
print(df[df['age'] > 30])     # 30살 이상

# 통계
print(df['age'].mean())       # 평균 나이
print(df.groupby('city').size())  # 도시별 인구
```

### 데이터 변환

```python
# 필터링
young = df[df['age'] < 30]

# 정렬
sorted_df = df.sort_values('age', ascending=False)

# 새 열 추가
df['age_group'] = df['age'].apply(
    lambda x: '젊음' if x < 30 else '성인'
)

# 행 결합 (UNION)
combined = pd.concat([df1, df2])

# 열 합치기 (JOIN)
merged = pd.merge(df1, df2, on='id')
```

---

## 📌 4.5장: 분산 컴퓨팅 기초

### Map-Reduce 패턴

**Map**: 데이터를 변환

```python
# 각 단어의 길이를 매핑
words = ['hello', 'world', 'python']
word_lengths = list(map(len, words))
# [5, 5, 6]
```

**Reduce**: 데이터를 축약

```python
from functools import reduce

# 모든 길이의 합
total_length = reduce(lambda a, b: a + b, word_lengths)
# 16
```

### Word Count 예제

```python
from functools import reduce
from collections import defaultdict

text = """
python is great
python is powerful
python is elegant
"""

# Map: 각 단어를 (word, 1)로 변환
words_with_count = [
    (word.strip(), 1)
    for word in text.lower().split()
    if word.strip()
]

# Shuffle: 같은 단어끼리 그룹화
word_groups = defaultdict(list)
for word, count in words_with_count:
    word_groups[word].append(count)

# Reduce: 각 그룹의 개수 합산
word_counts = {
    word: sum(counts)
    for word, counts in word_groups.items()
}

print(word_counts)
# {'python': 3, 'is': 3, 'great': 1, 'powerful': 1, 'elegant': 1}
```

### 실시간 데이터 처리

```python
# 스트림 처리 시뮬레이션
def process_stream(data_stream):
    """스트림 데이터 처리"""
    accumulator = 0
    for data in data_stream:
        accumulator += data
        yield {
            'value': data,
            'cumulative': accumulator
        }

# 사용
stream = range(1, 6)
results = list(process_stream(stream))
for result in results:
    print(result)
```

---

## 📌 4.6장: 병렬 처리

### 멀티프로세싱

```python
from multiprocessing import Pool

def square(x):
    return x * x

# 병렬 처리
with Pool(4) as p:
    results = p.map(square, range(10))

print(results)  # [0, 1, 4, 9, 16, ...]
```

### 멀티스레딩

```python
import threading
import time

def worker(name):
    for i in range(3):
        print(f"{name}이 작업 중... {i}")
        time.sleep(1)

threads = []
for i in range(3):
    t = threading.Thread(target=worker, args=(f"스레드 {i}",))
    threads.append(t)
    t.start()

for t in threads:
    t.join()  # 모든 스레드 대기
```

---

## 📌 4.7장: 최적화 (Optimization)

### 시간 복잡도 분석

```python
# O(n) - 선형
def find_max(numbers):
    return max(numbers)

# O(n²) - 이차
def bubble_sort(numbers):
    n = len(numbers)
    for i in range(n):
        for j in range(n - i - 1):
            if numbers[j] > numbers[j + 1]:
                numbers[j], numbers[j + 1] = numbers[j + 1], numbers[j]

# O(log n) - 로그
def binary_search(sorted_list, target):
    left, right = 0, len(sorted_list) - 1
    while left <= right:
        mid = (left + right) // 2
        if sorted_list[mid] == target:
            return mid
        elif sorted_list[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1
```

### 캐싱 (Memoization)

```python
from functools import lru_cache

# 최적화 전 (느림)
def fib_slow(n):
    if n <= 1:
        return n
    return fib_slow(n - 1) + fib_slow(n - 2)

# 최적화 후 (빠름)
@lru_cache(maxsize=None)
def fib_fast(n):
    if n <= 1:
        return n
    return fib_fast(n - 1) + fib_fast(n - 2)

# 성능 비교
import time

start = time.time()
result = fib_slow(35)
print(f"느린 버전: {time.time() - start:.2f}초")

start = time.time()
result = fib_fast(35)
print(f"빠른 버전: {time.time() - start:.4f}초")
```

---

## 📌 4.8장: 사례 연구

### 추천 시스템

```python
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

# 사용자-영화 평점 행렬
ratings = pd.DataFrame({
    '유저1': [5, 3, 0, 1],
    '유저2': [4, 0, 0, 1],
    '유저3': [1, 1, 0, 5],
    '유저4': [1, 0, 0, 4]
}, index=['영화A', '영화B', '영화C', '영화D'])

# 유사도 계산
similarity = cosine_similarity(ratings.T)

# 유저1과 유사한 유저 찾기
similar_users = pd.Series(similarity[0]).nlargest(2).index
print(f"유저1과 유사한 유저: {similar_users}")
```

### 데이터 시각화

```python
import matplotlib.pyplot as plt

# 데이터 준비
categories = ['A', 'B', 'C', 'D']
values = [23, 45, 56, 78]

# 막대 그래프
plt.bar(categories, values)
plt.title('카테고리별 값')
plt.xlabel('카테고리')
plt.ylabel('값')
plt.show()

# 선 그래프
time_series = [1, 4, 9, 16, 25]
plt.plot(time_series)
plt.title('시간 경과에 따른 변화')
plt.show()
```

---

## 🎯 핵심 요약

| 주제 | 설명 | 기술 |
|------|------|------|
| 선언형 프로그래밍 | 무엇을 원하는가 표현 | 함수형 파이프라인 |
| 논리 프로그래밍 | 사실과 규칙으로 표현 | Prolog, 논리 규칙 |
| SQL | 데이터 조회 언어 | SELECT, JOIN, GROUP BY |
| 데이터프레임 | 테이블 형태 데이터 | Pandas |
| Map-Reduce | 분산 데이터 처리 | 병렬 계산 |
| 최적화 | 성능 개선 | 시간 복잡도, 캐싱 |

---

## 📚 관련 페이지

- [3장: 컴퓨터 프로그램 해석](./chapter3.md)
- [메인 페이지](./index.md)

---

## 🚀 다음 단계

이 교과서를 완료하면:
- Python을 능숙하게 다룰 수 있습니다
- 프로그래밍의 본질적인 개념을 이해합니다
- 복잡한 문제를 체계적으로 해결할 수 있습니다

**UC Berkeley CS61A 과정에 도전해보세요!**

---

**이 페이지는 현재 제작 중이며, 더 자세한 코드 예시와 연습 문제가 추가될 예정입니다.**
