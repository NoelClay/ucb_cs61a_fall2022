---
layout: default
title: "3장: 컴퓨터 프로그램 해석"
---

# 3장: 컴퓨터 프로그램 해석

## 개요

이 장에서는 **프로그래밍 언어**가 어떻게 작동하는지 배웁니다. 언어의 문법(Syntax)과 의미(Semantics)를 이해하고, 간단한 인터프리터를 직접 구현해봅니다.

---

## 📌 3.1장: 소개 및 기본 개념

### 프로그래밍 언어의 3요소

1. **문법 (Syntax)**: 언어의 형식 규칙
2. **의미론 (Semantics)**: 프로그램의 의미
3. **구현 (Implementation)**: 인터프리터/컴파일러

### 평가 프로세스

```
소스 코드 → 파싱 (Parsing) → 추상구문트리 (AST) → 평가 (Evaluation) → 결과
```

### 표현식 평가

```python
# 원시 표현식
5                   # → 5
"hello"            # → "hello"

# 조합 표현식
3 + 4              # → 7
max(5, 3)          # → 5

# 중첩 표현식
f(g(h(x)))         # 안에서부터 바깥쪽으로
```

---

## 📌 3.2장: 함수형 프로그래밍

### 순수 함수 (Pure Functions)

**순수 함수**는:
- 같은 입력에 대해 항상 같은 출력을 반환
- 부작용(Side Effect)이 없음

```python
# 순수 함수 ✓
def add(a, b):
    return a + b

# 비순수 함수 ✗
counter = 0
def increment():
    global counter
    counter += 1  # 외부 상태 변경 (부작용)
    return counter
```

### 불변성 (Immutability)

데이터 구조를 변경하지 않고 새로운 구조를 만듭니다.

```python
# 가변 (Mutable)
numbers = [1, 2, 3]
numbers.append(4)  # 기존 리스트 수정

# 불변 (Immutable)
numbers = (1, 2, 3)  # 튜플
new_numbers = numbers + (4,)  # 새로운 튜플 생성
```

### 고차 함수와 함수 조합

```python
# 함수 조합
def compose(f, g):
    def composed(x):
        return f(g(x))
    return composed

# 함수 적용
def apply_to_all(f, seq):
    return [f(x) for x in seq]

# 함수 축약
def reduce_by(f, initial, seq):
    result = initial
    for x in seq:
        result = f(result, x)
    return result
```

---

## 📌 3.3장: 예외 처리

### try-except 블록

```python
try:
    result = 10 / 0  # 에러 발생
except ZeroDivisionError:
    print("0으로 나눌 수 없습니다!")
    result = None
```

### 여러 예외 처리

```python
try:
    file = open("data.txt")
    data = int(file.read())
except FileNotFoundError:
    print("파일이 없습니다")
except ValueError:
    print("숫자로 변환할 수 없습니다")
except Exception as e:
    print(f"예상하지 못한 오류: {e}")
finally:
    print("정리 작업")
```

### 예외 발생

```python
def validate_age(age):
    if age < 0:
        raise ValueError("나이는 음수일 수 없습니다")
    if age > 150:
        raise ValueError("나이가 너무 많습니다")
    return age

try:
    validate_age(-5)
except ValueError as e:
    print(f"오류: {e}")
```

---

## 📌 3.4장: 계산 모델 (Computation Models)

### 순서 모델 (Iterative Process)

```python
# 반복 계산
def factorial_iter(n):
    result = 1
    for i in range(1, n + 1):
        result *= i
    return result

# 메모리 사용: O(1)
```

### 재귀 모델 (Recursive Process)

```python
# 재귀 계산
def factorial_rec(n):
    if n == 0:
        return 1
    return n * factorial_rec(n - 1)

# 메모리 사용: O(n)
```

### 꼬리 재귀 최적화 (Tail Recursion Optimization)

```python
def factorial_tail(n, acc=1):
    """꼬리 재귀 형태"""
    if n == 0:
        return acc
    return factorial_tail(n - 1, n * acc)

# 일부 언어에서 메모리: O(1)로 최적화됨
```

---

## 📌 3.5장: Scheme 인터프리터 작성

### 간단한 계산기

```python
def evaluate(expr):
    """간단한 식을 평가"""
    if isinstance(expr, (int, float)):
        return expr
    elif isinstance(expr, str):
        # 변수 조회
        return variables[expr]
    elif isinstance(expr, list):
        if expr[0] == '+':
            return evaluate(expr[1]) + evaluate(expr[2])
        elif expr[0] == '*':
            return evaluate(expr[1]) * evaluate(expr[2])
        elif expr[0] == 'define':
            # 변수 정의
            variables[expr[1]] = evaluate(expr[2])
        elif expr[0] == 'lambda':
            # 함수 정의
            return create_function(expr)

variables = {}

# 사용
evaluate(['define', 'x', 5])
evaluate(['+', 'x', 3])  # 8
```

### 파싱 (Parsing)

```python
def parse(tokens):
    """토큰 리스트를 구문트리로 변환"""
    token = tokens[0]

    if token != '(':
        return token

    # 괄호 처리
    expr = []
    tokens.pop(0)  # '(' 제거
    while tokens[0] != ')':
        expr.append(parse(tokens))
    tokens.pop(0)  # ')' 제거

    return expr

# 사용
tokens = ['(', '+', '1', '2', ')']
ast = parse(tokens)  # ['+', '1', '2']
```

### 환경 관리

```python
class Environment:
    def __init__(self, parent=None):
        self.vars = {}
        self.parent = parent

    def get(self, var):
        if var in self.vars:
            return self.vars[var]
        elif self.parent:
            return self.parent.get(var)
        else:
            raise NameError(f"변수 '{var}'이 정의되지 않음")

    def set(self, var, value):
        self.vars[var] = value

# 사용
global_env = Environment()
global_env.set('x', 5)

local_env = Environment(parent=global_env)
print(local_env.get('x'))  # 5
```

---

## 📌 3.6장: 메타 순환 평가기 (Meta-Circular Evaluator)

### 기본 구조

```python
def mc_eval(expr, env):
    """메타 순환 평가기"""

    # 자기 평가 표현식
    if is_self_evaluating(expr):
        return expr

    # 변수
    if is_variable(expr):
        return lookup_variable_value(expr, env)

    # 따옴표
    if is_quoted(expr):
        return text_of_quotation(expr)

    # 할당
    if is_assignment(expr):
        return eval_assignment(expr, env)

    # 정의
    if is_definition(expr):
        return eval_definition(expr, env)

    # 표현식
    if is_if(expr):
        return eval_if(expr, env)

    # 절차 응용
    if is_application(expr):
        procedure = mc_eval(car(expr), env)
        args = list_of_arg_values(cdr(expr), env)
        return apply_procedure(procedure, args)

def mc_apply(procedure, args):
    """프로시저 적용"""
    if is_primitive_procedure(procedure):
        return apply_primitive_procedure(procedure, args)
    elif is_compound_procedure(procedure):
        new_env = extend_environment(
            parameters(procedure),
            args,
            environment(procedure)
        )
        return mc_eval(body(procedure), new_env)
```

---

## 🎯 핵심 개념 요약

| 개념 | 설명 | 예시 |
|------|------|------|
| 순수 함수 | 부작용 없음 | `add(a, b)` |
| 불변성 | 데이터 변경 없음 | 튜플 사용 |
| 고차 함수 | 함수를 다루는 함수 | `compose(f, g)` |
| 예외 처리 | 에러 관리 | try-except |
| 인터프리터 | 코드 실행 엔진 | 평가기 |

---

## 💡 응용

### DSL (Domain-Specific Language) 작성

```python
# 간단한 쿼리 언어
def query_all(table):
    return table

def query_where(table, condition):
    return [row for row in table if condition(row)]

def query_select(table, fields):
    return [[row[f] for f in fields] for row in table]

# 사용
data = [
    {"name": "철수", "age": 30},
    {"name": "영희", "age": 28}
]

result = query_where(data, lambda x: x["age"] > 29)
```

---

## 📚 관련 페이지

- [2장: 데이터를 통한 추상화](./chapter2.md)
- [4장: 데이터 처리](./chapter4.md)

---

**이 페이지는 현재 제작 중이며, 더 자세한 코드 예시와 연습 문제가 추가될 예정입니다.**
