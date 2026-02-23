---
layout: default
title: "제2장: 데이터를 통한 추상화"
---

# 제2장: 데이터를 통한 추상화
## Building Abstractions with Data

> 우리는 단순한 계산 요소뿐만 아니라, 이들을 조합하는 방법을 만들어야 합니다. 가장 강력한 조합 방법 중 하나는 **데이터 객체**입니다.

---

## 2.1 소개: 기본 자료형 소개(Introduction to Native Data Types)

### 핵심 원칙

**"Python의 모든 값은 클래스를 갖습니다."**

클래스는 값이 무엇인지 그리고 어떻게 조작되는지를 결정합니다:

```python
type(2)           # <class 'int'> (정수)
type(1.5)         # <class 'float'> (부동소수점)
type('hello')     # <class 'str'> (문자열)
```

### 정수 vs 부동소수점 (Integers vs Floating Point)

**정수 (Integers):**
- Python에서는 임의의 크기 지원
- 정확한 표현

**부동소수점 (Floating Point):**
- 제한된 정밀도
- 매우 큰 또는 매우 작은 수 표현 가능
- 근사치 기반

```python
# 정수 나눗셈은 부동소수점 반환
7 / 3             # 2.3333333333333335

# 근사 오류의 영향
7 / 3 * 3         # 7.0 (정확함)
1 / 3 * 7 * 3     # 6.999999999999999 (근사 오류!)

# 정수 나눗셈
7 // 3            # 2 (정수 몫)
```

---

## 2.2 데이터 추상화 (Data Abstraction)

### 개념: 추상화 장벽 (Abstraction Barriers)

프로그램을 여러 계층으로 나누고, **각 계층은 하위 계층의 구현 세부사항을 알 필요가 없어야** 합니다:

```
높은 수준: 유리수를 값처럼 사용
   ↕
중간 수준: 생성자/선택자 (rational, numer, denom)
   ↕
낮은 수준: 리스트로 구현
```

### 2.2.1 유리수(Rational Numbers) 예제

**문제:** 정수 나눗셈은 소수로 정보 손실

**해결책:** 분자와 분모의 쌍으로 표현

**인터페이스 정의:**

```python
from math import gcd

def rational(n, d):
    """분자 n과 분모 d로 유리수 생성 (기약분수로 축약)"""
    g = gcd(n, d)
    return [n//g, d//g]

def numer(r):
    """유리수의 분자"""
    return r[0]

def denom(r):
    """유리수의 분모"""
    return r[1]
```

**사용 예제:**

```python
half = rational(1, 2)
numer(half)       # 1
denom(half)       # 2

# 같은 값의 다양한 표현
one_third = rational(1, 3)
also_one_third = rational(2, 6)
# 두 표현 모두 동일하게 동작
```

### 2.2.2 추상화 장벽의 중요성

**올바른 구현 (추상화 유지):**

```python
def add_rationals(x, y):
    nx, dx = numer(x), denom(x)
    ny, dy = numer(y), denom(y)
    return rational(nx * dy + ny * dx, dx * dy)

add_rationals(rational(1, 3), rational(1, 3))
# rational(2, 3)
```

**나쁜 구현 (추상화 위반):**

```python
def add_rationals_bad(x, y):
    return [x[0] * y[1] + y[0] * x[1], x[1] * y[1]]
    # 위: 리스트 구현에 직접 접근
    # 구현 변경 시 모든 코드 수정 필요!
```

**이점:**
- 구현을 독립적으로 수정 가능
- 여러 표현 방식 선택 가능
- 코드 재사용 용이

---

## 2.3 시퀀스 (Sequences)

### 정의와 필수 속성

**시퀀스(Sequence)는 순서가 있는 값의 모음으로, 다음을 만족합니다:**

1. 유한한 길이
2. 0부터 시작하는 정수 인덱스로 원소 선택
3. 순서 유지

### 2.3.1 리스트 (Lists)

**가장 유연한 시퀀스 자료형:**

```python
digits = [1, 8, 2, 8]
digits[0]           # 1 (첫 원소)
digits[-1]          # 8 (마지막 원소)

# 결합
digits + [0, 0]     # [1, 8, 2, 8, 0, 0]

# 반복
[2] * 5             # [2, 2, 2, 2, 2]

# 중첩 리스트
nested = [[1, 2], [3, [4, 5]]]
nested[1]           # [3, [4, 5]]
```

### 2.3.2 시퀀스 반복 (Iteration)

**for 문:**

```python
for <name> in <sequence>:
    <suite>
```

**예제:**

```python
# 리스트 반복
for digit in digits:
    print(digit)

# 범위(Range) - 정수 시퀀스
for i in range(5):      # 0, 1, 2, 3, 4
    print(i)

for i in range(1, 6):   # 1, 2, 3, 4, 5
    print(i)

# 시퀀스 언팩 (Unpacking)
pairs = [[1, 2], [3, 4]]
for x, y in pairs:
    print(f'{x}, {y}')
    # Output: 1, 2 / 3, 4
```

### 2.3.3 시퀀스 처리 패턴

#### 1. 리스트 컴프리헨션 (List Comprehension)

```python
[<expression> for <name> in <sequence> if <condition>]
```

**예제:**

```python
# 변환 (Mapping)
squares = [x*x for x in range(5)]
# [0, 1, 4, 9, 16]

# 필터링 (Filtering)
evens = [x for x in range(10) if x % 2 == 0]
# [0, 2, 4, 6, 8]

# 중첩 컴프리헨션
nested_pairs = [(x, y) for x in range(2) for y in range(3)]
# [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2)]
```

#### 2. 고차 함수 (Higher-Order Functions)

```python
# map: 모든 원소에 함수 적용
list(map(lambda x: x*x, [1, 2, 3, 4]))
# [1, 4, 9, 16]

# filter: 조건에 맞는 원소만
list(filter(lambda x: x % 2 == 0, range(10)))
# [0, 2, 4, 6, 8]

# reduce: 누적 계산
from functools import reduce
reduce(lambda x, y: x + y, [1, 2, 3, 4])
# 10
```

### 2.3.4 시퀀스 추상화

**멤버십 테스트:**

```python
3 in [3, 1, 4]          # True
5 not in [3, 1, 4]      # True
```

**슬라이싱 (Slicing):**

```python
digits = [1, 8, 2, 8]
digits[1:3]             # [8, 2] (인덱스 1부터 3 미만)
digits[:2]              # [1, 8] (처음부터 2 미만)
digits[2:]              # [2, 8] (2부터 끝까지)
digits[-2:]             # [2, 8] (마지막에서 2개)
digits[::2]             # [1, 2] (2칸씩 건너뛰기)
```

### 2.3.5 문자열 (Strings)

**문자의 시퀀스로서 모든 시퀀스 연산 지원:**

```python
s = "Hello"
len(s)                  # 5
s[1]                    # 'e'
s[1:3]                  # 'el'

for char in s:
    print(char)

# 주의: 개별 문자뿐만 아니라 부분문자열도 검색 가능
'e' in s                # True
'ell' in s              # True (부분문자열!)
```

**타입 변환:**

```python
str(2.5)                # '2.5'
str([1, 2, 3])          # '[1, 2, 3]'
```

### 2.3.6 트리 (Trees)

**계층 구조를 나타내는 데이터 구조:**

```python
def tree(label, branches=[]):
    """label과 branches로 트리 노드 생성"""
    for branch in branches:
        assert is_tree(branch), 'branches must be trees'
    return [label] + list(branches)

def label(tree):
    """트리의 레이블"""
    return tree[0]

def branches(tree):
    """트리의 가지들"""
    return tree[1:]

def is_leaf(tree):
    """잎 노드 판정"""
    return not branches(tree)
```

**트리 처리 - 재귀 함수:**

```python
def tree_sum(t):
    """모든 레이블의 합"""
    return label(t) + sum(tree_sum(b) for b in branches(t))

def leaves(t):
    """잎 노드의 개수"""
    if is_leaf(t):
        return 1
    else:
        return sum(leaves(b) for b in branches(t))
```

---

## 2.4 가변 데이터 (Mutable Data)

### 2.4.1 객체의 비유 (Object Metaphor)

**"객체는 상태와 동작을 가진 엔티티입니다."**

파이썬의 날짜 객체:

```python
from datetime import date
today = date(2024, 2, 23)
today.year              # 2024
today.month             # 2
today.strftime('%B %d') # 'February 23'
```

### 2.4.2 시퀀스 객체와 가변성

**불변(Immutable) vs 가변(Mutable):**

- **불변:** 숫자, 문자열, 튜플 (수정 불가)
- **가변:** 리스트 (수정 가능)

**가변 객체의 위험:**

```python
chinese = ['coin', 'string', 'myriad']
suits = chinese  # 같은 객체 참조

suits.pop()      # 'myriad' 제거
print(chinese)   # ['coin', 'string'] - 양쪽 모두 변함!
```

### 2.4.3 리스트 변경 메서드

```python
suits = ['diamond', 'club', 'heart', 'spade']

# 제거
suits.pop()              # 'spade' 제거 및 반환
suits.remove('heart')    # 'heart' 제거

# 추가
suits.append('Joker')    # 끝에 추가
suits.extend(['A', 'B']) # 여러 원소 추가

# 삽입
suits.insert(1, 'Extra') # 인덱스 1에 삽입

# 범위 할당 (슬라이스 할당)
suits[0:2] = ['new1', 'new2']  # 처음 2개 교체
```

### 2.4.4 딕셔너리 (Dictionaries)

**키-값 매핑:**

```python
numerals = {'I': 1.0, 'V': 5, 'X': 10}

# 값 추가
numerals['L'] = 50

# 값 접근
numerals['V']            # 5
numerals.get('A', 0)     # 키 없으면 기본값 0 반환

# 반복
for key in numerals:
    print(f'{key}: {numerals[key]}')

# 메서드
numerals.keys()          # dict_keys(['I', 'V', 'X', 'L'])
numerals.values()        # dict_values([1.0, 5, 10, 50])
```

### 2.4.5 국소 상태 (Local State)

**문제:** 함수 호출 간 상태 유지 필요

**해결책: `nonlocal` 키워드**

```python
def make_withdraw(balance):
    """출금 함수를 생성"""
    def withdraw(amount):
        nonlocal balance  # 외부 balance 수정
        if amount > balance:
            return 'Insufficient funds'
        balance = balance - amount
        return balance
    return withdraw

# 사용
withdraw_20 = make_withdraw(100)
withdraw_20(20)          # 80 반환
withdraw_20(30)          # 50 반환
withdraw_20(30)          # 'Insufficient funds'

# 각 함수는 독립적 상태 유지
withdraw_30 = make_withdraw(100)
withdraw_30(30)          # 70 반환
```

---

## 2.5 객체지향 프로그래밍 (Object-Oriented Programming)

### 핵심 개념

**객체지향 프로그래밍은:**
- 데이터와 메서드를 함께 번들링
- 메시지 전송으로 객체 조작
- 상속으로 공통 동작 공유

### 2.5.1 클래스 정의

**기본 은행 계좌 예제:**

```python
class Account:
    def __init__(self, account_holder):
        """생성자 - 초기화"""
        self.balance = 0
        self.holder = account_holder

    def deposit(self, amount):
        """입금"""
        self.balance = self.balance + amount
        return self.balance

    def withdraw(self, amount):
        """출금"""
        if amount > self.balance:
            return 'Insufficient funds'
        self.balance = self.balance - amount
        return self.balance
```

**사용:**

```python
account = Account('Alice')
account.deposit(100)      # 100
account.withdraw(30)      # 70
account.balance           # 70
```

### 2.5.2 점 표기법 (Dot Notation)

```
<object>.<attribute>
```

**메커니즘:**
- `account.balance` → 속성 접근
- `account.deposit(50)` → `Account.deposit(account, 50)`
- `self`는 자동 주입

### 2.5.3 클래스 속성 (Class Attributes)

**인스턴스 속성 vs 클래스 속성:**

```python
class Account:
    interest_rate = 0.02  # 클래스 속성 (모든 인스턴스 공유)

    def __init__(self, account_holder):
        self.balance = 0      # 인스턴스 속성 (개별)
        self.holder = account_holder

    def add_interest(self):
        self.balance = self.balance * (1 + self.interest_rate)

# 사용
account1 = Account('Alice')
account1.balance = 100
account1.add_interest()     # balance = 102.0

Account.interest_rate = 0.03  # 클래스 속성 변경
account1.interest_rate       # 0.03 (변경 반영)
```

### 2.5.4 상속 (Inheritance)

**부모 클래스 확장:**

```python
class CheckingAccount(Account):
    """수표 기능이 있는 계좌"""
    def __init__(self, account_holder):
        Account.__init__(self, account_holder)  # 부모 초기화
        self.checks_remaining = 3

    def withdraw(self, amount):
        """수표를 사용한 출금"""
        if self.checks_remaining == 0:
            return 'No checks remaining'
        self.checks_remaining -= 1
        return Account.withdraw(self, amount)  # 부모 메서드 호출

# 사용
checking = CheckingAccount('Bob')
checking.deposit(100)       # 100
checking.withdraw(20)       # 80, checks_remaining = 2
```

---

## 2.6 클래스와 객체 구현 (Implementing Classes and Objects)

### 원칙

**"클래스와 객체는 함수와 딕셔너리로 구현될 수 있습니다."**

Python 언어의 특정 특징에 의존하지 않고, 기본 메커니즘을 이해할 수 있습니다.

### 2.6.1 인스턴스 구현

**핵심 아이디어:**

```python
def make_instance(cls):
    """인스턴스 생성"""
    def get_value(name):
        """속성 조회"""
        if name in attributes:
            return attributes[name]
        else:
            # 인스턴스 속성 없으면 클래스에서 검색
            value = cls('get', name)
            return bind_method(value, instance)

    def set_value(name, value):
        """속성 설정"""
        attributes[name] = value

    attributes = {}
    instance = {'get': get_value, 'set': set_value}
    return instance

def bind_method(value, instance):
    """메서드 바인딩"""
    if callable(value):
        def method(*args):
            return value(instance, *args)
        return method
    else:
        return value
```

### 2.6.2 클래스 구현

```python
def make_class(attributes, base_class=None):
    """클래스 생성"""
    def get_value(name):
        if name in attributes:
            return attributes[name]
        elif base_class is not None:
            return base_class('get', name)
        else:
            raise AttributeError(name)

    def new(*args):
        """새 인스턴스 생성"""
        instance = make_instance(cls)
        init = get_value('__init__')
        if init is not None:
            init(instance, *args)
        return instance

    cls = {'get': get_value, 'new': new}
    return cls
```

---

## 2.7 객체 추상화 (Object Abstraction)

### 2.7.1 특수 메서드 (Special Methods)

파이썬의 특정 연산에 응답하는 메서드들:

```python
class Rational:
    def __init__(self, numer, denom):
        from math import gcd
        g = gcd(numer, denom)
        self.numer = numer // g
        self.denom = denom // g

    # 문자열 표현
    def __str__(self):
        """사람 읽기 가능한 형식"""
        return f'{self.numer}/{self.denom}'

    def __repr__(self):
        """Python 평가 가능한 형식"""
        return f'Rational({self.numer}, {self.denom})'

    # 산술 연산
    def __add__(self, other):
        """덧셈"""
        if isinstance(other, Rational):
            n = self.numer * other.denom + self.denom * other.numer
            d = self.denom * other.denom
            return Rational(n, d)
        else:
            return NotImplemented

    def __mul__(self, other):
        """곱셈"""
        if isinstance(other, Rational):
            return Rational(self.numer * other.numer,
                          self.denom * other.denom)
        else:
            return NotImplemented
```

**사용:**

```python
r = Rational(1, 3)
str(r)              # '1/3'
repr(r)             # 'Rational(1, 3)'

r1 = Rational(1, 3)
r2 = Rational(1, 2)
r1 + r2             # Rational(5, 6)
```

### 2.7.2 다중 표현 (Multiple Representations)

**복소수의 두 가지 표현:**

#### 직각좌표계 (Rectangular)

```python
from math import cos, sin, atan2

class ComplexRI:
    def __init__(self, real, imag):
        self.real = real
        self.imag = imag

    @property
    def magnitude(self):
        return (self.real**2 + self.imag**2) ** 0.5

    @property
    def angle(self):
        return atan2(self.imag, self.real)
```

#### 극좌표계 (Polar)

```python
class ComplexMA:
    def __init__(self, magnitude, angle):
        self.magnitude = magnitude
        self.angle = angle

    @property
    def real(self):
        return self.magnitude * cos(self.angle)

    @property
    def imag(self):
        return self.magnitude * sin(self.angle)
```

**@property 데코레이터:**

```python
@property
def magnitude(self):
    """속성처럼 접근 가능한 메서드"""
    return (self.real**2 + self.imag**2) ** 0.5

# 메서드처럼 호출하지 않음
z = ComplexRI(3, 4)
z.magnitude         # 5.0
```

---

## 2.8 효율성 (Efficiency)

### 2.8.1 효율성 측정

**문제:** Fibonacci 계산의 중복

```python
def fib(n):
    if n == 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fib(n-1) + fib(n-2)

# fib(5) = 15번 함수 호출
# fib(19) = 13,529번 함수 호출!
```

**호출 횟수 세기:**

```python
def count_calls(f):
    """함수 호출 횟수 측정"""
    def counted(n):
        counted.call_count += 1
        return f(n)
    counted.call_count = 0
    return counted

fib_counted = count_calls(fib)
result = fib_counted(30)
print(fib_counted.call_count)  # 매우 큰 수
```

### 2.8.2 메모이제이션 (Memoization)

**이전 결과를 저장하여 중복 계산 제거:**

```python
def memo(f):
    """메모이제이션 데코레이터"""
    cache = {}

    def memoized(n):
        if n not in cache:
            cache[n] = f(n)
        return cache[n]

    return memoized

# 사용
fib_memo = memo(fib)
result = fib_memo(30)  # 31번의 함수 호출로 단축!
```

**극적인 개선:**
- 원래: `fib(34)` → 약 5,702,887회 호출
- 메모이제이션: `fib(34)` → 35회 호출

### 2.8.3 성장 차수 (Orders of Growth)

**Theta 표기법 Θ(f(n)):**

n이 충분히 클 때, 어떤 상수 k₁, k₂에 대해
```
k₁ · f(n) ≤ R(n) ≤ k₂ · f(n)
```

**일반적 성장 차수:**

| 차수 | 명칭 | 특성 |
|------|------|------|
| Θ(1) | 상수 | 가장 빠름 |
| Θ(log n) | 로그 | 매우 빠름 |
| Θ(n) | 선형 | 빠름 |
| Θ(n log n) | 선형로그 | 중간 |
| Θ(n²) | 이차 | 느림 |
| Θ(n³) | 삼차 | 매우 느림 |
| Θ(2ⁿ) | 지수 | 극히 느림 |

### 2.8.4 거듭제곱 최적화 (Successive Squaring)

**문제:** b^n을 계산하는 효율적 방법

```python
# 기본 O(n) 알고리즘
def exp(b, n):
    if n == 0:
        return 1
    return b * exp(b, n-1)

# 최적화 O(log n) 알고리즘
def fast_exp(b, n):
    """Successive Squaring"""
    if n == 0:
        return 1
    elif n % 2 == 0:
        return fast_exp(b*b, n//2)
    else:
        return b * fast_exp(b, n-1)

# 예: 2^100
# 기본: 100번 곱셈
# 최적화: 약 14번 곱셈
```

---

## 2.9 재귀적 객체 (Recursive Objects)

### 2.9.1 연결 리스트 클래스 (Linked List)

**함수형 연결 리스트:**

```python
class Link:
    """연결 리스트"""
    empty = ()  # 빈 리스트 표시

    def __init__(self, first, rest=empty):
        assert rest is Link.empty or isinstance(rest, Link)
        self.first = first
        self.rest = rest

    def __len__(self):
        """리스트 길이 - Θ(n)"""
        if self.rest is Link.empty:
            return 1
        else:
            return 1 + len(self.rest)

    def __getitem__(self, i):
        """인덱싱 - Θ(n)"""
        if i == 0:
            return self.first
        else:
            return self.rest[i-1]

    def __repr__(self):
        if self.rest is Link.empty:
            return f'Link({self.first})'
        else:
            return f'Link({self.first}, {self.rest})'
```

**사용:**

```python
s = Link(3, Link(4, Link(5)))
len(s)              # 3
s[1]                # 4
```

### 2.9.2 트리 클래스 (Tree Class)

**계층 구조 표현:**

```python
class Tree:
    def __init__(self, label, branches=[]):
        self.label = label
        self.branches = [b for b in branches]

    def is_leaf(self):
        return not self.branches

    def __repr__(self):
        if self.is_leaf():
            return f'Tree({self.label})'
        return f'Tree({self.label}, {self.branches})'

# 사용
t = Tree(1, [
    Tree(2, [Tree(4), Tree(5)]),
    Tree(3, [Tree(6)])
])
```

---

## 🎯 핵심 개념 요약

| 개념 | 정의 | 예시 |
|------|------|------|
| 데이터 추상화 | 표현과 인터페이스 분리 | 유리수 추상화 |
| 시퀀스 | 순서 있는 값의 모음 | 리스트, 문자열 |
| 가변성 | 수정 가능한 객체 | 리스트, 딕셔너리 |
| 객체 | 상태와 메서드 | 클래스 인스턴스 |
| 상속 | 부모 클래스 확장 | CheckingAccount(Account) |
| 메모이제이션 | 결과 캐싱 | 중복 계산 제거 |
| 성장 차수 | 성능 분석 | Big-O 표기 |

---

## 📚 학습 경로

→ [**제3장: 컴퓨터 프로그램 해석**](./chapter3.md)

---

**이 페이지는 [Composing Programs - Chapter 2](https://www.composingprograms.com/pages/21-introduction.html)의 한국어 초월번역입니다.**
