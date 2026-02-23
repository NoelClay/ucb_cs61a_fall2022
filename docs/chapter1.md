---
layout: default
title: "1장: 함수를 통한 추상화"
---

# 1장: 함수를 통한 추상화

## 개요

프로그래밍의 기초는 **추상화(Abstraction)**입니다. 복잡한 계산 과정을 작은 단위로 나누고, 각 단위에 이름을 붙여 재사용함으로써 복잡한 문제를 해결할 수 있습니다.

이 장에서는 **함수(Function)**라는 도구를 사용하여 계산을 어떻게 조직화하는지 배웁니다.

---

## 📌 1.1장: 프로그래밍의 요소들

### 핵심 개념

프로그래밍 언어는 세 가지 메커니즘을 제공합니다:

1. **원시적 표현식(Primitive Expressions)**
   - 언어가 제공하는 가장 간단한 개체들
   - 예: 숫자 `2`, 문자 `"hello"`

2. **조합 수단(Means of Combination)**
   - 간단한 개체들을 합쳐서 복잡한 개체를 만드는 방법
   - 예: 산술 연산 `2 + 3`, 함수 호출

3. **추상 수단(Means of Abstraction)**
   - 복잡한 개체에 이름을 붙여 단순한 단위로 다루는 방법
   - 예: 함수 정의

### 함수 호출

```python
# 함수 호출의 기본 형태
max(5, 3)  # 5를 반환

# 중첩된 함수 호출
max(3, min(5, 7))  # 5를 반환
```

---

## 📌 1.2장: 데이터 정의하기

### 함수 정의

함수를 정의하면 계산을 추상화할 수 있습니다.

```python
# 함수 정의
def square(x):
    return x * x

# 함수 사용
square(5)  # 25를 반환
```

### 매개변수와 인자

- **매개변수(Parameter)**: 함수 정의에서 사용되는 이름
- **인자(Argument)**: 함수 호출할 때 전달하는 실제 값

```python
def sum_of_squares(x, y):
    return square(x) + square(y)

sum_of_squares(3, 4)  # 9 + 16 = 25를 반환
```

---

## 📌 1.3장: 평가 모델

### 치환 모델 (Substitution Model)

함수 호출의 의미를 이해하기 위해 치환 모델을 사용합니다.

**예시:**
```
sum_of_squares(3, 4)
= square(3) + square(4)
= 3*3 + 4*4
= 9 + 16
= 25
```

### 평가 순서

1. **응용 순서(Applicative Order)**
   - 인자를 먼저 평가한 후 함수를 호출
   - Python의 기본 평가 방식

2. **정상 순서(Normal Order)**
   - 필요할 때까지 계산을 미루기
   - 게으른 평가(Lazy Evaluation)

---

## 📌 1.4장: 환경 모델 (Environment Model)

### 프레임 (Frame)

함수가 호출될 때마다 새로운 **프레임(Frame)**이 생성됩니다.
프레임은 매개변수와 지역 변수의 바인딩(이름과 값의 연결)을 저장합니다.

```python
def f(x):
    def g(y):
        return x + y
    return g

add_5 = f(5)
add_5(3)  # 8을 반환
```

이 예시에서:
- `f` 호출 시 프레임 1 생성: `x = 5`
- `g` 호출 시 프레임 2 생성: `y = 3`, `x`는 외부 프레임에서 참조

---

## 📌 1.5장: 람다 표현식 (Lambda Expressions)

익명 함수를 정의하는 방법입니다.

### 기본 문법

```python
# 일반 함수
def square(x):
    return x * x

# 람다 표현식으로 동일하게 표현
square = lambda x: x * x

# 직접 사용
map(lambda x: x * x, [1, 2, 3, 4])  # [1, 4, 9, 16]
```

### 사용 사례

람다는 간단한 계산을 일회용으로 사용할 때 유용합니다.

```python
sorted([3, 1, 4, 1, 5], key=lambda x: -x)  # 역순 정렬
```

---

## 📌 1.6장: 고등 함수 (Higher-Order Functions)

**고등 함수**는 함수를 인자로 받거나 함수를 반환하는 함수입니다.

### 함수를 인자로 받기

```python
def apply_twice(f, x):
    return f(f(x))

apply_twice(square, 3)  # square(square(3)) = square(9) = 81
```

### 함수를 반환하기

```python
def make_multiplier(n):
    def multiplier(x):
        return x * n
    return multiplier

double = make_multiplier(2)
triple = make_multiplier(3)

double(5)  # 10
triple(5)  # 15
```

### 유용한 고등 함수들

```python
# map: 함수를 각 요소에 적용
list(map(square, [1, 2, 3, 4]))  # [1, 4, 9, 16]

# filter: 조건에 맞는 요소만 선택
list(filter(lambda x: x % 2 == 0, [1, 2, 3, 4]))  # [2, 4]

# reduce: 누적 계산
from functools import reduce
reduce(lambda x, y: x + y, [1, 2, 3, 4])  # 10
```

---

## 📌 1.7장: 재귀 (Recursion)

함수가 자기 자신을 호출하는 방식입니다.

### 재귀의 구조

모든 재귀 함수는 두 부분으로 구성됩니다:

1. **기저 사례 (Base Case)**: 재귀를 멈추는 조건
2. **재귀 사례 (Recursive Case)**: 자기 자신을 호출하는 부분

### 예시 1: 팩토리얼

```python
def factorial(n):
    if n == 0:
        return 1  # 기저 사례
    else:
        return n * factorial(n - 1)  # 재귀 사례

factorial(5)  # 5 * 4 * 3 * 2 * 1 = 120
```

### 예시 2: 피보나치 수열

```python
def fib(n):
    if n == 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fib(n - 1) + fib(n - 2)

fib(6)  # 8
```

### 재귀 vs 반복

```python
# 재귀 버전
def sum_recursive(n):
    if n == 0:
        return 0
    return n + sum_recursive(n - 1)

# 반복 버전
def sum_iterative(n):
    total = 0
    for i in range(n + 1):
        total += i
    return total
```

---

## 📌 1.8장: 함수 합성과 분해

### 함수 분해

큰 문제를 작은 함수로 나누어 해결합니다.

```python
def is_even(n):
    return n % 2 == 0

def is_odd(n):
    return not is_even(n)

def count_evens(numbers):
    count = 0
    for n in numbers:
        if is_even(n):
            count += 1
    return count
```

### 함수 합성

작은 함수들을 조합하여 복잡한 함수를 만듭니다.

```python
def compose(f, g):
    def composed(x):
        return f(g(x))
    return composed

double_then_square = compose(square, lambda x: x * 2)
double_then_square(5)  # square(5*2) = square(10) = 100
```

---

## 🎯 핵심 요약

| 개념 | 설명 | 예시 |
|------|------|------|
| 함수 정의 | 계산을 추상화 | `def square(x): return x * x` |
| 환경 모델 | 함수 호출 시 변수 바인딩 | 프레임과 스코프 |
| 람다 표현식 | 익명 함수 | `lambda x: x * x` |
| 고등 함수 | 함수를 다루는 함수 | `map()`, `filter()` |
| 재귀 | 자기 자신을 호출 | `factorial()`, `fib()` |

---

## 📚 다음 장

[**2장: 데이터를 통한 추상화**](./chapter2.md)로 이동하여 객체지향 프로그래밍과 데이터 구조를 배웁니다.

---

**이 페이지는 현재 제작 중이며, 더 자세한 코드 예시와 연습 문제가 추가될 예정입니다.**
