---
layout: default
title: "제1장: 함수를 통한 추상화"
---

# 제1장: 함수를 통한 추상화
## Building Abstractions with Functions

> 이 장은 프로그래밍의 가장 기본적인 아이디어들을 소개합니다: **표현식(Expressions)**, **선언(Statements)**, **함수(Functions)**, 그리고 **제어(Control)**

---

## 1.1 시작하기(Getting Started)

### Python에서 프로그래밍하기

Python이 이 교과서의 언어로 선택된 이유는 무엇일까요?

- **가독성**: Python은 인간이 읽을 수 있도록 설계되었습니다. Python 커뮤니티는 "아름다움, 단순함, 명시성"이 "복잡성, 복잡함, 암시성"보다 낫다는 **젠(Zen) 원칙**을 따릅니다.

- **유연성**: Python은 절차형, 함수형, 객체지향 프로그래밍 패러다임을 모두 지원합니다.

- **실용성**: Python은 학계와 산업계 모두에서 광범위하게 사용됩니다.

### 대화형 세션(Interactive Sessions)

Python 3 인터프리터는 대화형 셸을 제공합니다:

```python
>>> 2 + 2
4
>>> 2 - 1
1
```

`>>>` 프롬프트는 Python이 당신의 입력을 기다리고 있다는 뜻입니다. 각 표현식을 평가한 후 결과를 출력합니다.

### 첫 번째 예제: Shakespeare 텍스트 분석

다음은 인터넷에서 Shakespeare의 글을 다운로드한 후, 회문(palindrome)인 6자리 단어를 찾는 간단한 프로그램입니다:

```python
from urllib.request import urlopen

shakespeare = urlopen('http://composingprograms.com/shakespeare.txt')
words = set(shakespeare.read().decode().split())

# 6자리이고 회문인 단어 찾기
[w for w in words if len(w) == 6 and w == w[::-1]]
```

이 프로그램은 여러 **프로그래밍의 기초 개념**을 보여줍니다:

1. **함수(Functions)**: `urlopen()`은 URL에서 데이터를 가져오는 복잡한 작업을 단순한 호출로 캡슐화합니다.
2. **객체(Objects)**: `set` 컬렉션과 `decode()` 메서드는 데이터를 조작합니다.
3. **리스트 컴프리헨션**: 필터링 로직을 간결하게 표현합니다.

### 디버깅(Errors and Debugging)

프로그래밍의 현실적 측면 중 하나는 **디버깅**입니다. 좋은 프로그래머들이 따르는 네 가지 전략이 있습니다:

1. **모듈식으로 테스트하기**: 프로그램의 작은 부분을 점진적으로 테스트합니다.
2. **오류 격리하기**: 문제를 특정 코드 조각으로 좁힙니다.
3. **가정 검증하기**: 변수 값과 함수 동작에 대한 기본 가정을 확인합니다.
4. **다른 사람에게 물어보기**: 다른 프로그래머와 협력하면 새로운 관점을 얻을 수 있습니다.

---

## 1.2 프로그래밍의 요소들(Elements of Programming)

모든 강력한 언어는 세 가지 메커니즘을 갖추고 있습니다:

1. **기본 표현식(Primitive Expressions)**: 언어가 제공하는 가장 간단한 개체들
2. **결합 수단(Means of Combination)**: 간단한 것들을 합쳐 더 복잡한 것을 만드는 방법
3. **추상 수단(Means of Abstraction)**: 복합 개체에 이름을 붙여 단위로 다루는 방법

### 표현식(Expressions)

기본 표현식은 숫자입니다:

```python
2
3.0
5 + (3 * 4 + (2 + (1 + 1))))
```

이러한 수치 표현식은 파이썬 인터프리터에 의해 계산되어 숫자 값으로 평가됩니다.

표현식은 **연산자(Operators)**를 통해 결합될 수 있습니다:

```python
2.0 * 3  # 곱셈
3 / 2    # 부동소수점 나눗셈
3 // 2   # 정수 나눗셈
3 ** 2   # 지수
```

### 호출 표현식(Call Expressions)

가장 중요한 복합 표현식 유형은 **호출 표현식(Call Expression)**입니다. 이는 함수를 인수들에 적용하는 방법입니다:

```python
max(7.5, 9.5)        # 9.5
min(1, -2, 3, -5)    # -5
abs(-5)              # 5
```

호출 표현식의 구조는:

```
  max(7.5, 9.5)
     ^     ^    ^
  operator arguments
```

**중요한 개념**: "연산자"는 호출할 함수입니다. "인수(Arguments)"는 함수에 전달되는 값들입니다.

호출 표현식은 **중첩될 수 있습니다**:

```python
max(3, min(5, 7))         # 5를 반환
abs(max(-1, -2))          # 1을 반환
```

### 라이브러리 함수 임포트(Importing Library Functions)

Python의 광범위한 기능은 여러 모듈로 조직화되어 있습니다. 표준 라이브러리의 함수를 사용하려면 `import` 문을 사용합니다:

```python
from math import sqrt
sqrt(256)              # 16.0

from operator import add
add(1, 2)              # 3
```

### 이름과 환경(Names and the Environment)

프로그래밍 언어의 관리 가능한 특징은 **변수를 사용하여 계산 결과에 이름을 붙이는 능력**입니다:

```python
radius = 10
2 * 3.14159 * radius   # 반지름이 10인 원의 둘레
```

할당 문(Assignment Statement)에 의해 이름(변수명)이 값과 연결됩니다. 이렇게 저장된 이름-값 쌍들의 메모리를 **환경(Environment)**이라고 합니다.

**다중 할당(Multiple Assignment)**:

```python
area, circumference = 3.14159 * radius ** 2, 2 * 3.14159 * radius
```

### 표현식 평가(Evaluating Nested Expressions)

표현식을 평가할 때 Python은 다음 규칙을 따릅니다:

1. **재귀적 평가**: 복합 표현식을 평가하려면 먼저 부분식들을 평가합니다.
2. **함수 적용**: 연산자 함수를 인수 값들에 적용합니다.

예시:

```python
2 + 3 * 4 + 5    # 다음과 같이 평가됨:
# = 2 + (3 * 4) + 5     (곱셈 우선)
# = 2 + 12 + 5
# = 19
```

### 순수 함수 vs 비순수 함수(Pure Functions vs Non-Pure Functions)

**순수 함수(Pure Functions)**:
- 부작용(side effects)이 없습니다
- 동일한 입력에 대해 항상 동일한 출력을 반환합니다
- 예: `abs()`, `max()`, `sqrt()`

```python
abs(-5)    # 항상 5를 반환
```

**비순수 함수(Non-Pure Functions)**:
- 반환값 외에 추가 효과를 가집니다
- 예: `print()` 함수는 값을 표시하면서 `None`을 반환합니다

```python
print(1)     # None을 반환하면서 "1"을 화면에 출력
```

**중요**: 비순수 함수의 반환값을 할당하면 안 됩니다:

```python
x = print(3)  # x는 None이 됩니다!
```

---

## 1.3 새로운 함수 정의하기(Defining New Functions)

**함수 정의**를 통해 새로운 계산 단위를 만들 수 있습니다:

```python
def square(x):
    return x * x
```

함수 정의 문법:

```
def <name>(<formal parameters>):
    return <return expression>
```

함수를 정의한 후 호출할 수 있습니다:

```python
square(3)      # 9
square(4)      # 16
```

### 환경 모델(Environment Model)

함수 호출 시 새로운 **프레임(Frame)**이 생성됩니다:

```python
def square(x):
    return x * x

def sum_of_squares(x, y):
    return square(x) + square(y)

sum_of_squares(3, 4)  # 25를 반환
```

평가 과정:
1. `sum_of_squares` 호출 → 로컬 프레임 생성, `x=3, y=4`
2. `square(3)` 호출 → 새 로컬 프레임 생성, `x=3`
3. `x * x` 반환 → 9
4. `square(4)` 호출 → 새 로컬 프레임 생성, `x=4`
5. `x * x` 반환 → 16
6. `9 + 16` 반환 → 25

### 함수 추상화(Function Abstraction)

함수는 **계산을 추상화**합니다. 함수 사용자는 구현 세부사항을 알 필요가 없습니다:

```python
def improve(update, close, guess=1):
    while not close(guess):
        guess = update(guess)
    return guess
```

이 함수는:
- **정의역**: 세 개의 함수 인자
- **치역**: 개선된 추정값
- **의도**: 반복적으로 추정값을 개선

---

## 1.4 함수 설계(Designing Functions)

좋은 함수를 작성하기 위한 세 가지 원칙이 있습니다:

### 원칙 1: 단일 책임(Single Responsibility)

**"각 함수는 정확히 한 가지 작업을 가져야 하며, 이는 짧은 이름으로 식별되고 한 문장으로 설명될 수 있어야 합니다."**

```python
def square(x):
    """Return the square of x."""
    return x * x
```

### 원칙 2: DRY (Don't Repeat Yourself)

코드 로직을 복제하지 마세요:

```python
# 나쁜 예 (코드 중복):
def sum_naturals(n):
    total = 0
    k = 1
    while k <= n:
        total = total + k
        k = k + 1
    return total

def sum_cubes(n):
    total = 0
    k = 1
    while k <= n:
        total = total + k**3
        k = k + 1
    return total

# 좋은 예 (일반화):
def summation(n, term):
    total, k = 0, 1
    while k <= n:
        total = total + term(k)
        k = k + 1
    return total

def identity(x):
    return x

def cube(x):
    return x ** 3

summation(5, identity)  # 1+2+3+4+5
summation(5, cube)      # 1³+2³+3³+4³+5³
```

### 원칙 3: 일반성(Generality)

특정 시나리오보다는 더 광범위한 경우를 처리하세요.

### 문서화(Documentation)

#### Docstrings

함수 정의 직후의 문자열을 **docstring**이라고 합니다. 이는 함수의 목적을 설명합니다:

```python
def ideal_gas_law(n, t, v):
    """Return the pressure of an ideal gas.

    n: number of moles (몰의 수)
    t: absolute temperature in Kelvin (절대 온도)
    v: volume in liters (부피)
    """
    return n * 8.3144621 * t / v
```

Docstring은 `help()` 함수로 확인할 수 있습니다:

```python
help(ideal_gas_law)
```

#### 주석(Comments)

특정 줄에 대한 추가 설명은 `#`으로 시작합니다:

```python
# 황금비 계산
phi = (1 + 5**0.5) / 2
```

### 기본 인자값(Default Argument Values)

함수 정의에서 기본값을 지정할 수 있습니다:

```python
def pressure(n=6.022e23, t, v):
    return n * 8.3144621 * t / v

# 호출:
pressure(6.022e23, 373, 0.5)  # 모든 인자 지정
pressure(t=373, v=0.5)         # n은 기본값 사용
```

---

## 1.5 제어(Control)

### 문(Statements) vs 표현식(Expressions)

- **표현식**: 값으로 평가됩니다. 예: `2 + 3`, `square(5)`
- **문**: 실행되며 인터프리터 상태를 변경합니다. 예: 할당, 함수 정의, 반환

### 복합 문(Compound Statements)

복합 문은 **헤더(header)**와 **스위트(suite)**로 구성됩니다:

```
if <expression>:
    <suite>
```

### 조건 문(Conditional Statements)

```python
def abs_value(x):
    if x >= 0:
        return x
    else:
        return -x
```

조건 문은 `if`, `elif`, `else`를 포함할 수 있습니다:

```python
def sign(x):
    if x > 0:
        return 1
    elif x < 0:
        return -1
    else:
        return 0
```

### 부울 컨텍스트(Boolean Contexts)

비교 연산자: `>`, `<`, `==`, `!=`, `>=`, `<=`

논리 연산자: `and`, `or`, `not`

**단락 평가(Short-circuit evaluation)**:

```python
True or <error>   # True (오른쪽 평가 안함)
False and <error> # False (오른쪽 평가 안함)
```

### 반복(Iteration)

#### While 루프

```python
def fibonacci(n):
    """Print Fibonacci numbers up to n."""
    a, b = 0, 1
    while a < n:
        print(a)
        a, b = b, a + b

fibonacci(10)  # 0, 1, 1, 2, 3, 5, 8 출력
```

### 테스팅(Testing)

#### Assert 문

```python
assert square(3) == 9, "square(3) should return 9"
```

#### Doctests

함수의 docstring 안에 테스트를 작성할 수 있습니다:

```python
def sum_squares(x, y):
    """Compute x*x + y*y.

    >>> sum_squares(3, 4)
    25
    """
    return x*x + y*y
```

---

## 1.6 고차 함수(Higher-Order Functions)

**고차 함수**는:
- 다른 함수를 인자로 받거나
- 함수를 값으로 반환하는 함수입니다

이를 통해 프로그래머는 **공통 패턴을 추상화**할 수 있습니다.

### 함수를 인자로(Functions as Arguments)

세 개의 유사한 합계 함수를 생각해봅시다:

```python
def sum_naturals(n):
    total, k = 0, 1
    while k <= n:
        total, k = total + k, k + 1
    return total

def sum_cubes(n):
    total, k = 0, 1
    while k <= n:
        total, k = total + k**3, k + 1
    return total
```

이들은 같은 패턴을 따릅니다. 이를 **고차 함수**로 추상화할 수 있습니다:

```python
def summation(n, term):
    """Compute sum of term(k) for k=1 to n."""
    total, k = 0, 1
    while k <= n:
        total, k = total + term(k), k + 1
    return total

def cube(x):
    return x ** 3

def identity(x):
    return x

summation(5, cube)      # 1³+2³+3³+4³+5³ = 225
summation(5, identity)  # 1+2+3+4+5 = 15
```

### 함수를 일반 메서드로(Functions as General Methods)

고차 함수는 특정 함수와 무관한 **일반적인 계산 방법**을 표현합니다:

```python
def improve(update, close, guess=1):
    """Improve guess until it satisfies close."""
    while not close(guess):
        guess = update(guess)
    return guess

def golden_ratio():
    def golden_update(guess):
        return 1/guess + 1

    def square_close_to_successor(guess):
        return abs(guess*guess - guess - 1) < 1e-11

    return improve(golden_update, square_close_to_successor)

golden_ratio()  # 약 1.618 (황금비)
```

---

## 1.7 재귀 함수(Recursive Functions)

**재귀 함수**는 자신을 호출하는 함수입니다.

### 기본 예제: 자릿수 합(Sum of Digits)

```python
def sum_digits(n):
    """Return the sum of the digits of positive integer n."""
    if n < 10:
        return n          # 기저 사례
    else:
        # 마지막 자릿수와 나머지로 분리
        all_but_last = n // 10
        last = n % 10
        return sum_digits(all_but_last) + last

sum_digits(9)       # 9
sum_digits(18117)   # 1+8+1+1+7 = 18
```

### 재귀 함수의 구조

모든 재귀 함수는 두 가지를 포함해야 합니다:

1. **기저 사례(Base Case)**: 가장 간단한 입력 - 재귀 없이 직접 계산
2. **재귀 사례(Recursive Case)**: 더 간단한 문제로 축약한 후 자신 호출

### 팩토리얼(Factorial)

```python
def factorial(n):
    if n == 1:
        return 1          # 기저 사례
    else:
        return n * factorial(n - 1)  # 재귀 사례

factorial(5)  # 5 * 4 * 3 * 2 * 1 = 120
```

### 상호 재귀(Mutual Recursion)

두 함수가 서로를 호출할 수 있습니다:

```python
def is_even(n):
    if n == 0:
        return True
    else:
        return is_odd(n - 1)

def is_odd(n):
    if n == 0:
        return False
    else:
        return is_even(n - 1)
```

### 트리 재귀(Tree Recursion)

함수가 자신을 여러 번 호출합니다:

```python
def fib(n):
    """Return the nth Fibonacci number."""
    if n == 1:
        return 0
    if n == 2:
        return 1
    return fib(n - 2) + fib(n - 1)

fib(5)  # 3
```

**주의**: 트리 재귀는 많은 중복 계산을 생성합니다. 이를 최적화하려면 **메모이제이션(memoization)**을 사용합니다.

### 재귀의 신념의 도약(Recursive Leap of Faith)

재귀를 이해하는 열쇠는:

> "재귀 호출이 더 간단한 문제를 올바르게 해결한다고 믿으세요."

전체 계산을 정신적으로 풀어헤치려고 하지 마세요. 각 단계가 올바른지만 확인하세요.

---

## 🎯 핵심 개념 요약

| 개념 | 의미 | 예시 |
|------|------|------|
| 표현식 | 값으로 평가되는 코드 | `2 + 3`, `square(5)` |
| 호출 표현식 | 함수를 인자에 적용 | `max(7.5, 9.5)` |
| 함수 정의 | 새로운 함수 생성 | `def square(x): return x * x` |
| 환경 모델 | 이름-값 바인딩 | 전역/로컬 프레임 |
| 조건문 | 조건에 따른 실행 | `if`, `elif`, `else` |
| 반복문 | 반복 실행 | `while` 루프 |
| 고차 함수 | 함수를 인자/반환값으로 | `summation(n, term)` |
| 재귀 | 자신을 호출하는 함수 | `factorial(n)` |

---

## 📚 다음 단계

[**제2장: 데이터를 통한 추상화**](./chapter2.md)로 이동하여 데이터 구조와 객체지향 프로그래밍을 배웁니다.

---

**이 페이지는 [Composing Programs](https://www.composingprograms.com/pages/11-getting-started.html)의 한국어 초월번역입니다.**
