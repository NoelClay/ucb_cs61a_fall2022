---
layout: default
title: "제3장: 컴퓨터 프로그램 해석"
---

# 제3장: 컴퓨터 프로그램 해석
## Interpreting Computer Programs

> 우리는 이제 프로그래밍의 세 번째 기본 요소인 **프로그램** 자체에 초점을 맞춥니다. 프로그래밍 언어의 인터프리터를 이해하고, 심지어 직접 만들 수 있습니다.

---

## 3.1 소개(Introduction)

### 핵심 질문

**"프로그래밍 언어란 무엇인가?"**

프로그래밍 언어는 단순히 **문법(Syntax)**이 아닙니다. 진정한 언어는 **의미(Semantics)**를 가져야 합니다.

### 인터프리터의 역할

**인터프리터란?**

"프로그래밍 언어에 의미를 부여하는 프로그램"

```
소스 코드 → [인터프리터] → 실행 결과
```

인터프리터는:
- 표현식의 의미를 정의함
- 프로그래밍 언어가 무엇을 하는지 결정함
- 모든 언어 기능의 기초

### 언어 설계자로서의 관점 전환

이 장에서는:
- 사용자 관점: "다른 사람이 설계한 언어를 사용"
- → 설계자 관점: "프로그래밍 언어 자체를 설계"

이를 통해 언어의 본질을 깊이 있게 이해합니다.

### 평가와 적용: 상호 재귀

인터프리터는 두 개의 상호 재귀 함수로 구축됩니다:

**평가(eval):** 특정 환경에서 표현식을 평가
**적용(apply):** 함수를 인자에 적용

```
eval ←→ apply
```

이 두 함수는 서로에 의존하여 언어의 의미를 정의합니다.

---

## 3.2 함수형 프로그래밍 (Functional Programming)

### Scheme 언어: 최소이면서 강력한 언어

**Scheme이란?**

- Lisp 방언
- 최소한의 구문 규칙
- 최대한의 표현력
- 함수형 프로그래밍 전통

### 기본 문법

**표현식의 기본 형식:**

```scheme
(operator operand1 operand2 ...)
```

**전치 표기법(Prefix Notation):**

```scheme
(+ (* 3 5) (- 10 6))  ; 곱하기와 빼기는 각각 평가되고, 덧셈은 그 결과에 적용됨
                       ; = (+ 15 4) = 19
```

### 특수 형식 (Special Forms)

일반 함수와 다르게 모든 피연산자를 즉시 평가하지 않는 표현식:

**조건문 (if):**

```scheme
(if <predicate> <consequent> <alternative>)
```

**논리 연산자:**

```scheme
(and <expression> ...)  ; 모든 식이 참일 때만 참
(or <expression> ...)   ; 하나라도 참이면 참
(not <expression>)      ; 부정
```

### 정의 (Definitions)

**변수 정의:**

```scheme
(define pi 3.14159)
```

**함수 정의:**

```scheme
(define (square x)
  (* x x))

(define (sum-of-squares x y)
  (+ (square x) (square y)))
```

**람다 (Lambda):**

```scheme
(lambda (x) (* x x))  ; 무명 제곱 함수
```

### 데이터 구조

**쌍 (Pairs):**

```scheme
(cons 1 2)           ; [1, 2] 쌍 생성
(car (cons 1 2))     ; 1 (첫 번째 요소)
(cdr (cons 1 2))     ; 2 (두 번째 요소)
```

**리스트 (Lists):**

```scheme
(list 1 2 3 4)       ; (1 2 3 4)
(cons 1 (list 2 3))  ; (1 2 3)
```

**인용 (Quotation):**

```scheme
'x                    ; 평가하지 않고 x라는 기호
'(1 2 3)              ; 기호의 리스트
```

### 고급 예제: 터틀 그래픽

Scheme은 간단한 터틀 그래픽도 지원합니다:

```scheme
(forward 100)         ; 앞으로 100 단위 이동
(right 90)            ; 90도 오른쪽 회전
(penup)               ; 펜 올리기
(pendown)             ; 펜 내리기
```

---

## 3.3 예외 처리 (Exceptions)

### 예외 발생

**언제 예외를 발생시키는가?**

프로그램이 정상적으로 계속할 수 없는 조건에서:

```python
if not isinstance(x, (int, float)):
    raise TypeError(f'{x} must be numeric')
```

**예외는 객체:**

```python
class IterImproveError(Exception):
    """반복 개선 중 수학적 오류 발생"""
    pass

raise IterImproveError('not converging')
```

### 예외 처리

**try-except 블록:**

```python
try:
    result = risky_operation()
except ValueError as e:
    print(f'Error occurred: {e}')
    result = default_value
except ZeroDivisionError:
    print('Cannot divide by zero')
```

### 설계 철학

**다양한 전략:**

- **웹 서버:** 오류 로깅 후 계속 실행
- **계산기:** 사용자 입력 오류 시 다시 시도 요청
- **임베디드 시스템:** 임계값 초과 시 즉시 종료

프로그래머는 특정 맥락에 맞는 적절한 전략을 선택합니다.

### 이점

예외 처리를 통해:
- 정상 흐름과 오류 처리 분리
- 코드 가독성 향상
- 강건한 프로그램 작성

---

## 3.4 조합을 지원하는 언어의 인터프리터

### 계산기 언어 구현

**메타언어 추상화(Metalinguistic Abstraction):**

새로운 언어를 만들어 특정 도메인의 문제를 우아하게 해결

### 핵심 구성요소

#### 1. 표현식 트리

```python
# (+ (* 3 4) 5)
# 를 다음과 같이 표현
Pair('+', Pair(Pair('*', Pair(3, Pair(4, nil))),
              Pair(5, nil)))
```

#### 2. 파싱 (2단계)

**어휘 분석 (Tokenization):**

```
"(+ (* 3 4) 5)"
↓
['(', '+', '(', '*', 3, 4, ')', 5, ')']
```

**구문 분석 (Syntactic Analysis):**

```
토큰 → 표현식 트리
```

#### 3. 평가 (Evaluation)

```python
def calc_eval(expr):
    if isinstance(expr, (int, float)):
        return expr          # 자기 평가
    elif isinstance(expr, str):
        return expr          # 기호
    else:
        # 호출 표현식
        operator = calc_eval(expr.first)
        args = [calc_eval(arg) for arg in expr.rest]
        return operator(*args)
```

#### 4. REPL (Read-Eval-Print Loop)

```
입력 → 읽기 → 평가 → 출력 → (반복)
```

사용자는 다음과 같이 상호작용합니다:

```
calc> (+ 2 (* 3 4))
14
calc> (* (- 10 5) 2)
10
```

---

## 3.5 추상화를 지원하는 언어의 인터프리터

### Scheme 인터프리터 확장

계산기 인터프리터를 확장하여 다음을 지원합니다:

- 함수 정의 (`define`)
- 변수 바인딩
- 람다 표현식
- 특수 형식 (`if`, `and`, `or`)

### Eval-Apply 사이클

**핵심 원칙:**

```
평가는 적용으로 정의되고
적용은 평가로 정의된다
```

#### 평가 (scheme_eval)

```python
def scheme_eval(expr, env):
    # 원시값 (자기 평가)
    if isinstance(expr, (int, float)):
        return expr

    # 기호 (환경에서 조회)
    if isinstance(expr, str):
        return env.lookup(expr)

    # 특수 형식
    if is_special_form(expr):
        return eval_special_form(expr, env)

    # 호출 표현식
    func = scheme_eval(expr.first, env)
    args = [scheme_eval(arg, env) for arg in expr.rest]
    return scheme_apply(func, args, env)
```

#### 적용 (scheme_apply)

```python
def scheme_apply(func, args, env):
    if is_primitive_procedure(func):
        # 내장 함수
        return apply_primitive(func, args)
    else:
        # 사용자 정의 함수
        # 새 프레임 생성하여 형식 매개변수 바인딩
        new_env = env.extend(func.params, args)
        return scheme_eval(func.body, new_env)
```

### 환경 모델

**프레임 (Frame):**

변수-값 바인딩의 딕셔너리

```python
class Frame:
    def __init__(self, parent=None):
        self.bindings = {}
        self.parent = parent

    def lookup(self, symbol):
        # 현재 프레임에서 검색
        if symbol in self.bindings:
            return self.bindings[symbol]
        # 부모 프레임에서 검색
        elif self.parent:
            return self.parent.lookup(symbol)
        else:
            raise NameError(f'undefined variable: {symbol}')

    def define(self, symbol, value):
        self.bindings[symbol] = value
```

**환경 확장:**

함수 호출 시 새로운 프레임이 부모를 확장합니다:

```
[함수 호출]
  ↓
[새 프레임 생성]
  ↓
[형식 매개변수를 실제 인자로 바인딩]
  ↓
[함수 본체 평가]
```

### 사용자 정의 함수

**정의:**

```scheme
(define (sum-of-squares x y)
  (+ (square x) (square y)))
```

**호출 시:**

```scheme
(sum-of-squares 3 4)

; 평가 과정:
; 1. 환경에서 sum-of-squares 조회
; 2. 인자 3, 4 평가
; 3. 새 프레임: x=3, y=4 바인딩
; 4. 함수 본체 평가
```

---

## 🎯 핵심 개념 요약

| 개념 | 정의 | 예시 |
|------|------|------|
| 인터프리터 | 언어에 의미 부여 | Scheme 인터프리터 |
| 평가 | 환경에서 표현식 계산 | `scheme_eval` |
| 적용 | 함수를 인자에 적용 | `scheme_apply` |
| 환경 | 변수-값 바인딩 | 프레임 체인 |
| 특수 형식 | 모든 인자를 평가하지 않음 | `if`, `define` |
| 메타 추상화 | 언어로 언어 만들기 | 계산기 언어 |

---

## 📚 학습 경로

→ [**제4장: 데이터 처리**](./chapter4.md)

---

**이 페이지는 [Composing Programs - Chapter 3](https://www.composingprograms.com/pages/31-introduction.html)의 한국어 초월번역입니다.**
