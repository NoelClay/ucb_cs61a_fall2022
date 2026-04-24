# UCB CS61A Fall 2022 - 학습 자료 모음

UC Berkeley의 CS61A (Structure and Interpretation of Computer Programs) 과목에 대한 학습 자료를 체계적으로 정리한 레퍼지토리입니다.

## 📁 폴더 구조 안내

### 📚 학습 자료 — `materials/` 서브모듈 (private)

UC Berkeley CS 61A 강의 자료(슬라이드·시험·디스커션·스터디가이드 등)는
저작권 보호를 위해 **별도의 private 서브모듈**에 보관합니다:

- 위치: `./materials/`
- 서브모듈 리포: [`NoelClay/ucb_cs61a_fall2022-archive`](https://github.com/NoelClay/ucb_cs61a_fall2022-archive) (private)
- 접근 권한이 있는 사용자만 다음 명령으로 내용을 받습니다:

```bash
git clone --recurse-submodules https://github.com/NoelClay/ucb_cs61a_fall2022.git
# 또는 이미 클론했다면:
git submodule update --init
```

접근 권한이 없는 사용자는 `materials/` 폴더가 비어 있고, 본 리포의
공개 콘텐츠(번역본·파이프라인 코드·개인 학습 기록)만 볼 수 있습니다.

**서브모듈 내부 구조** (접근 권한 있을 때):
```
materials/
├── lecture-notes/         강의 슬라이드 PDF + 데모 노트북
├── exams/                 fa22 시험 + 역대 시험 아카이브
├── exam-solutions/        시험 해답 (placeholder)
├── supplementary-lectures/articles/ & study-guides/
├── assignments/           hw, labs, proj 스타터 + pdf-specs
├── assignment-solutions/  jianweiye 솔루션 미러
└── courses/               강의 메타데이터 (캘린더 등)
```

### 📖 Textbooks (공개) — `./textbooks/`

본인이 한국어로 번역한 *Composing Programs* 및 관련 자료.
원본이 **CC BY-SA 3.0**으로 공개되어 있어 자유롭게 배포 가능합니다.

- 원문: https://www.composingprograms.com/
- 한국어 번역본: https://noelclay.github.io/ucb_cs61a_fall2022/

### 🎙️ Pipeline & Scripts (공개) — `./pipeline/`, `./scripts/`

본인 제작 한국어 더빙 파이프라인 및 아카이브 수확 스크립트.
MIT 라이선스.

### 🔗 On-Site Lectures (공개) — `./on-site-lectures/`

라이브 강의·실시간 세션 메타데이터.

---

### 🎓 개인 학습 기록

#### **My Assignments** (`./my-assignments/`)
개인이 직접 작성한 과제 제출물
- 나의 구현 및 풀이
- 코드 작성 과정
- 학습 진행도 기록

#### **My Exams** (`./my-exams/`)
개인의 시험 준비 및 시험 결과 정리
- 시험 준비 노트
- 자신의 답안
- 시험 결과 분석

---

## 🚀 사용 방법

서브모듈 접근 권한이 있다면:

1. **학습 순서**: `textbooks/` → `materials/lecture-notes/` → `materials/supplementary-lectures/` → `on-site-lectures/` 순으로 학습하며 이해도를 높입니다.
2. **과제 풀이**: `materials/assignments/` 문제를 읽고 `my-assignments/`에 코드를 작성한 후, `materials/assignment-solutions/`와 비교합니다.
3. **시험 대비**: `materials/exams/` 문제를 풀고 `my-exams/`에 답안 정리, 해설을 검토하며 취약점을 파악합니다.

## 📖 Textbooks: Composing Programs (한국어)

이 프로젝트의 **Textbooks** 섹션은 다음 사이트를 한국어로 초월번역한 버전을 제공합니다:
- **원문**: https://www.composingprograms.com/
- **한국어 번역**: https://noelclay.github.io/ucb_cs61a_fall2022/

---

## 📄 라이선스 및 저작권 고지

루트의 `LICENSE`(MIT)는 **리포지토리 소유자가 직접 작성한 콘텐츠**에만 적용됩니다
— 구체적으로는 `pipeline/`·`scripts/` 자동화 코드, `my-assignments/`·`my-exams/`의
개인 학습 기록, 그리고 리포 소유자가 작성한 문서입니다.

Private 서브모듈(`materials/`) 내부의 모든 CS 61A 강의 자료는 **UC Berkeley 및
CS 61A 강의진**(주로 John DeNero)의 저작물이며, 접근 권한이 있는 본인만을 위한
비상업적 개인 학습용 아카이브입니다.

- 서브모듈 리포: [`NoelClay/ucb_cs61a_fall2022-archive`](https://github.com/NoelClay/ucb_cs61a_fall2022-archive) (private)
- 전체 제3자 자료 목록·출처·저작권자: [`NOTICE.md`](./NOTICE.md)
- `textbooks/composing-programs-original/`(공개)은 원본이 **CC BY-SA 3.0** 하에 제공됩니다.
- 저작권자의 삭제 요청은 [issues](https://github.com/NoelClay/ucb_cs61a_fall2022/issues)를
  통해 신속하게 처리합니다.

이 리포는 공식 CS 61A 수강을 대체하지 않으며, 현재 수강생은 본인 학기의 공식 정책과
학문적 진실성 규정을 따라야 합니다.