---
layout: default
title: "2장: 데이터를 통한 추상화"
---

# 2장: 데이터를 통한 추상화

## 개요

이 장에서는 데이터를 구조화하고 조작하는 방법을 배웁니다. 함수뿐만 아니라 **자료구조(Data Structures)**를 통해 복잡한 문제를 해결할 수 있습니다.

---

## 📌 2.1장: 서열 (Sequences)

### 리스트 (Lists)

가장 기본적인 자료구조입니다.

```python
# 리스트 생성
numbers = [1, 2, 3, 4, 5]
mixed = [1, "hello", 3.14, True]

# 인덱싱
numbers[0]      # 1 (첫 번째 요소)
numbers[-1]     # 5 (마지막 요소)

# 슬라이싱
numbers[1:3]    # [2, 3]
numbers[::2]    # [1, 3, 5] (2칸씩)

# 메서드
numbers.append(6)           # 끝에 추가
numbers.remove(3)           # 값으로 제거
numbers.pop()               # 마지막 요소 제거 및 반환
numbers.sort()              # 정렬
```

### 튜플 (Tuples)

불변 서열입니다.

```python
# 튜플 생성
point = (3, 4)
x, y = point  # 언팩킹

# 활용
coordinates = [(0, 0), (1, 1), (2, 2)]
for x, y in coordinates:
    print(f"({x}, {y})")
```

### 문자열 (Strings)

문자의 서열입니다.

```python
text = "Hello, World!"

# 인덱싱과 슬라이싱
text[0]           # 'H'
text[0:5]         # 'Hello'

# 메서드
text.lower()      # 소문자로 변환
text.replace("World", "Python")
text.split(", ")  # ['Hello', 'World!']
```

---

## 📌 2.2장: 데이터 추상화

### 추상화의 원칙

데이터 추상화는 **인터페이스(Interface)**와 **구현(Implementation)**을 분리합니다.

```python
# 추상 인터페이스 (사용자가 보는 부분)
def make_rational(n, d):
    """유리수 (n/d)를 만든다"""
    pass

def numerator(r):
    """유리수의 분자"""
    pass

def denominator(r):
    """유리수의 분모"""
    pass

# 구현 (내부 구현)
def make_rational(n, d):
    gcd_value = gcd(n, d)
    return [n // gcd_value, d // gcd_value]

def numerator(r):
    return r[0]

def denominator(r):
    return r[1]
```

### 클로저를 이용한 추상화

```python
def make_rational(n, d):
    """클로저를 사용한 유리수 구현"""
    gcd_value = gcd(n, d)
    n = n // gcd_value
    d = d // gcd_value

    def operator(op):
        if op == 'n':
            return n
        elif op == 'd':
            return d

    return operator

r = make_rational(4, 6)  # 2/3
print(r('n'))  # 2
print(r('d'))  # 3
```

---

## 📌 2.3장: 수열의 처리

### 리스트 컴프리헨션

```python
# 제곱수 생성
squares = [x*x for x in range(1, 6)]
# [1, 4, 9, 16, 25]

# 조건 포함
evens = [x for x in range(1, 11) if x % 2 == 0]
# [2, 4, 6, 8, 10]

# 중첩
matrix = [[i*j for j in range(1, 4)] for i in range(1, 4)]
# [[1, 2, 3], [2, 4, 6], [3, 6, 9]]
```

### 고등 함수

```python
# map: 변환
doubled = list(map(lambda x: x*2, [1, 2, 3]))
# [2, 4, 6]

# filter: 필터링
odds = list(filter(lambda x: x % 2 == 1, range(10)))
# [1, 3, 5, 7, 9]

# reduce: 축약
from functools import reduce
product = reduce(lambda x, y: x*y, [1, 2, 3, 4])
# 24
```

---

## 📌 2.4장: 트리 (Trees)

### 트리 구조

```python
# 트리의 표현
def make_tree(root, branches):
    return [root] + branches

def root(tree):
    return tree[0]

def branches(tree):
    return tree[1:]

def is_leaf(tree):
    return len(tree) == 1

# 사용 예
tree = make_tree(1,
    [make_tree(2, [make_tree(4), make_tree(5)]),
     make_tree(3, [make_tree(6)])])

# 구조:
#       1
#      / \
#     2   3
#    / \   \
#   4   5   6
```

### 트리 순회

```python
def tree_sum(tree):
    """트리의 모든 값의 합"""
    total = root(tree)
    for branch in branches(tree):
        total += tree_sum(branch)
    return total

# 트리의 높이
def tree_height(tree):
    if is_leaf(tree):
        return 0
    return 1 + max(tree_height(branch) for branch in branches(tree))
```

---

## 📌 2.5장: 객체지향 프로그래밍 (OOP)

### 클래스와 인스턴스

```python
class Dog:
    """개를 나타내는 클래스"""

    def __init__(self, name, age):
        self.name = name
        self.age = age

    def bark(self):
        return f"{self.name}가 멍멍 짖습니다!"

    def get_older(self):
        self.age += 1

# 인스턴스 생성
my_dog = Dog("뽀삐", 3)
print(my_dog.bark())        # "뽀삐가 멍멍 짖습니다!"
print(my_dog.age)           # 3
my_dog.get_older()
print(my_dog.age)           # 4
```

### 상속 (Inheritance)

```python
class Animal:
    def __init__(self, name):
        self.name = name

    def speak(self):
        pass

class Dog(Animal):
    def speak(self):
        return f"{self.name}가 멍멍 짖습니다!"

class Cat(Animal):
    def speak(self):
        return f"{self.name}가 야옹 웁니다!"

# 사용
dog = Dog("뽀삐")
cat = Cat("나비")

print(dog.speak())  # "뽀삐가 멍멍 짖습니다!"
print(cat.speak())  # "나비가 야옹 웁니다!"
```

### 다형성 (Polymorphism)

```python
def animal_sounds(animals):
    for animal in animals:
        print(animal.speak())

animals = [Dog("뽀삐"), Cat("나비")]
animal_sounds(animals)
# 뽀삐가 멍멍 짖습니다!
# 나비가 야옹 웁니다!
```

---

## 📌 2.6장: 딕셔너리와 해시맵

### 딕셔너리

```python
# 생성
person = {"name": "김철수", "age": 30, "city": "서울"}

# 접근
person["name"]              # "김철수"
person.get("age")           # 30
person.get("job", "직업없음")  # "직업없음"

# 수정
person["age"] = 31
person["job"] = "개발자"

# 반복
for key, value in person.items():
    print(f"{key}: {value}")

# 메서드
person.keys()               # ['name', 'age', 'city', 'job']
person.values()             # ['김철수', 31, '서울', '개발자']
```

### 해시 테이블 구현

```python
def make_hash_table(size):
    return [[] for _ in range(size)]

def hash_function(key, size):
    return hash(key) % size

def insert(table, key, value):
    index = hash_function(key, len(table))
    table[index].append((key, value))

def lookup(table, key):
    index = hash_function(key, len(table))
    for k, v in table[index]:
        if k == key:
            return v
    return None
```

---

## 📌 2.7장: 제네릭 연산

### 다중 표현

같은 데이터를 여러 방식으로 표현할 수 있습니다.

```python
# 복소수의 직각 좌표 표현
def make_rect(x, y):
    return {"type": "rect", "x": x, "y": y}

# 복소수의 극 좌표 표현
def make_polar(r, theta):
    return {"type": "polar", "r": r, "theta": theta}

# 일반 인터페이스
def magnitude(c):
    if c["type"] == "rect":
        return (c["x"]**2 + c["y"]**2)**0.5
    elif c["type"] == "polar":
        return c["r"]
```

---

## 📌 2.8장: 메타 언어 추상화

### 언어 설계

새로운 언어나 도메인 특화 언어(DSL)를 만들 수 있습니다.

```python
# 간단한 계산기 언어
def calculate(expr):
    if isinstance(expr, (int, float)):
        return expr
    else:
        op = expr[0]
        a = calculate(expr[1])
        b = calculate(expr[2])

        if op == '+':
            return a + b
        elif op == '*':
            return a * b

# 사용
result = calculate(['+', ['*', 2, 3], 4])
# (* 2 3) = 6, (+ 6 4) = 10
```

---

## 🎯 핵심 요약

| 개념 | 설명 | 예시 |
|------|------|------|
| 서열 | 순서가 있는 데이터 | 리스트, 튜플, 문자열 |
| 데이터 추상화 | 인터페이스와 구현 분리 | 유리수 ADT |
| 트리 | 계층적 데이터 구조 | 파일 시스템 |
| 클래스 | 객체 템플릿 | Dog 클래스 |
| 상속 | 클래스의 계층 | Animal → Dog, Cat |
| 딕셔너리 | 키-값 쌍 | {"name": "철수"} |

---

## 📚 관련 페이지

- [1장: 함수를 통한 추상화](./chapter1.md)
- [3장: 컴퓨터 프로그램 해석](./chapter3.md)

---

**이 페이지는 현재 제작 중이며, 더 자세한 코드 예시와 연습 문제가 추가될 예정입니다.**
