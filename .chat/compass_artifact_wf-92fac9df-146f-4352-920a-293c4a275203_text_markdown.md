# UCB CS61A 외부 학습자를 위한 공개 자료 완전 가이드

UC Berkeley CS61A(Structure and Interpretation of Computer Programs)의 거의 모든 핵심 자료는 **로그인 없이 외부인도 접근 가능하다.** 공식 사이트 cs61a.org는 현재 학기(Spring 2026) 콘텐츠를 공개하고 있으며, 교재·강의영상·과제·시험 아카이브 등 독학에 필요한 자원이 무료로 풍부하게 존재한다. 과거 학기 서브도메인(fa24.cs61a.org 등)은 현재 학기로 리다이렉트되지만, GitHub 미러와 Vercel 백업을 통해 과거 학기 자료에도 완전히 접근할 수 있다. 아래에 카테고리별로 정리한다.

---

## 1. 강의 웹사이트: 현재 학기는 공개, 과거 학기는 미러 활용

**cs61a.org (현재: Spring 2026)** — ✅ **로그인 없이 완전 공개**

현재 학기 사이트에서는 강의 일정 캘린더, 강의 슬라이드(PDF), 모든 Lab·Homework·Project 과제, Discussion 워크시트 및 솔루션, 학습 가이드가 공개되어 있다. 과제 zip 파일도 직접 다운로드 가능하며, 솔루션은 마감일 **약 3일 후** 공개된다(학기 종료 후 비공개 전환).

과거 학기 서브도메인(`fa25.cs61a.org`, `sp25.cs61a.org`, `fa24.cs61a.org` 등)은 모두 **현재 학기로 리다이렉트**되어 직접 접근이 불가능하다. `inst.eecs.berkeley.edu/~cs61a/` 경로도 CalNet 로그인을 요구한다. 하지만 아래 미러 사이트들을 통해 과거 학기 전체 콘텐츠에 접근할 수 있다.

| 사이트 | 학기 | 접근 | URL | 설명 |
|--------|------|------|-----|------|
| cs61a.org | Spring 2026 (현재) | ✅ 공개 | https://cs61a.org/ | 현재 학기 전체 콘텐츠 |
| InsideEmpire 아카이브 | Fall 2024 | ✅ 공개 | https://insideempire.github.io/CS61A-Website-Archive/ | Fall 2024 사이트 완전 오프라인 미러 |
| cs61a.vercel.app | Spring 2022 | ✅ 공개 | https://cs61a.vercel.app/ | Pamela Fox 학기, 솔루션 포함 |
| berkeleycs 웹 아카이브 | 과제별 | ✅ 공개 | https://berkeleycs-web-archive.vercel.app/ | CS61A HW·Lab·Project 아카이브 |
| Wayback Machine | 다수 학기 | ✅ 공개 | https://web.archive.org/ 에서 cs61a.org 검색 | 과거 스냅샷 열람 가능 |
| Brian Harvey 아카이브 | ~2010 (Scheme) | ✅ 공개 | https://people.eecs.berkeley.edu/~bh/61a-pages/ | 구 Scheme 버전 완전 아카이브 |

---

## 2. 강의 영상: DeNero의 YouTube 플레이리스트가 핵심

CS61A 강의 영상의 핵심은 **John DeNero 교수의 사전 녹화(pre-recorded) YouTube 강의**다. 이 영상들은 학기에 무관하게 재사용되는 주제별 짧은 영상(5~15분) 시리즈로, 전체 CS61A 커리큘럼을 완전히 커버한다. cs61a.org의 각 강의 페이지에서 해당 주제의 YouTube 플레이리스트가 직접 링크되어 있다.

**중요**: 교실 라이브 강의 녹화는 bCourses(Berkeley LMS) 로그인이 필요하여 외부인 접근 불가. 오직 DeNero의 사전 녹화본만 YouTube에서 공개된다.

| 자료 | 접근 | URL | 설명 |
|------|------|-----|------|
| DeNero YouTube 채널 | ✅ 공개 | https://www.youtube.com/channel/UClPkNCC1Gd_cyI7QTe7lJwA | 주제별 플레이리스트 ~200개 영상 |
| 강의별 플레이리스트 (예: Lec 2) | ✅ 공개 | https://www.youtube.com/playlist?list=PL6BsET-8jgYULSxiV2garZ0FxbnXR08MP | cs61a.org 각 강의에서 링크 |
| Brian Harvey CS61A (Scheme, 2011) | ✅ 공개 | https://www.youtube.com/playlist?list=PLhMnuBfGeCDNgVzLPxF9o5UNKG1b-LFY9 | ~59개 전체 강의, UCBerkeley 채널 |
| Bilibili 미러 (Fall 2021) | ✅ 공개 | https://www.bilibili.com/video/BV1244y1a7Zp/ | DeNero 영상 중국어 자막 포함 |
| Bilibili (Fall 2022 교실 강의) | ✅ 공개 | https://www.bilibili.com/video/BV1GK411Q7qp/ | 49개 실제 교실 강의 영상 |
| Internet Archive 웹캐스트 | ✅ 공개 | https://archive.org/details/ucberkeley-webcast | 2015년 이전 학기 강의 다수 보존 |

cs61a.org 강의 페이지에는 "Please watch the video playlist before attending live lecture"라는 안내가 있으며, 이 영상만으로도 수업 내용 전체를 커버할 수 있도록 설계되어 있다.

---

## 3. 교재: Composing Programs는 완전 무료 공개

| 교재 | 접근 | URL | 설명 |
|------|------|-----|------|
| **Composing Programs** | ✅ 무료 공개 | https://www.composingprograms.com/ | CS61A 공식 교재, John DeNero 저, CC BY-SA 3.0 |
| SICP 원본 (MIT Press) | ✅ 무료 공개 | https://mitp-content-server.mit.edu/books/content/sectbyfn/books_pres_0/6515/sicp.zip/full-text/book/book.html | Scheme 기반 원본, 참고용 |
| SICP 깔끔한 HTML 버전 | ✅ 무료 공개 | https://sarabander.github.io/sicp/html/ | 읽기 편한 형식 |
| Interactive SICP | ✅ 무료 공개 | https://xuanji.appspot.com/isicp/ | 브라우저에서 코드 실행 가능 |
| Composing Programs 중국어 번역 | ✅ 무료 공개 | https://composingprograms.netlify.app/ | 중국어 번역판 |
| sicp-py-zh (GitHub 중국어 번역) | ✅ 무료 공개 | https://github.com/wizardforcel/sicp-py-zh | ★2,300, 가장 인기 있는 번역 |

**Composing Programs**는 총 4개 챕터, 27개 섹션으로 구성된다. Chapter 1은 함수 추상화(고차 함수, 재귀), Chapter 2는 데이터 추상화(OOP, 시퀀스, 트리), Chapter 3은 인터프리터 구현, Chapter 4는 데이터 처리(제너레이터, SQL, 병렬 컴퓨팅)를 다룬다. cs61a.org 캘린더에서 각 강의에 해당하는 교재 섹션이 명시되어 있어 교재와 강의를 병행하기 쉽다.

---

## 4. 과제(Homework/Lab/Project): GitHub 저장소에서 완전 확보 가능

cs61a.org 현재 학기에서 과제 zip 파일을 직접 다운로드할 수 있으며, 과거 학기 과제는 GitHub 저장소를 통해 시작 코드(starter code)와 솔루션 모두 확보 가능하다. 자동 채점기 OKPy는 `python3 ok --local` 플래그로 Berkeley 로그인 없이 **로컬에서 모든 테스트 실행**이 가능하다.

**주요 GitHub 저장소 (최신순)**:

| 저장소 | 학기 | ★ | 내용 | URL |
|--------|------|---|------|-----|
| YiWang24/CS61A-25SP | Spring 2025 | - | HW·Lab·Project 솔루션 | https://github.com/YiWang24/CS61A-25SP |
| InsideEmpire/CS61A-PathwayToSuccess | Fall 2024 | 63 | 전체 솔루션 + 이중언어 주석 | https://github.com/InsideEmpire/CS61A-PathwayToSuccess |
| InsideEmpire/CS61A-Assignments | Fall 2024 | - | **시작 코드(starter code) 전용** | https://github.com/InsideEmpire/CS61A-Assignments |
| xianzhe233/UCB-CS61A-Summer-2024 | Summer 2024 | - | 자료 + 비공식 솔루션 | https://github.com/xianzhe233/UCB-CS61A-Summer-2024-Resources-and-Unofficial-Solutions |
| shuo-liu16/CS61A | Spring 2024 | 278 | 전체 솔루션 + 상세 주석 | https://github.com/shuo-liu16/CS61A |
| yitai-cheng/CS61A-2024-Spring | Spring 2024 | - | 전체 과제 + --local 가이드 | https://github.com/yitai-cheng/CS61A-2024-Spring |
| cy-Yin/UCBerkeley-CS61A-Fall2023 | Fall 2023 | 33 | 전체 솔루션 + **Fall 2022 강의 슬라이드** | https://github.com/cy-Yin/UCBerkeley-CS61A-Fall2023 |
| PKUFlyingPig/CS61A | Summer 2020 | 331 | 전체 솔루션, csdiy.wiki 추천 | https://github.com/PKUFlyingPig/CS61A |

CS61A의 대표 프로젝트는 **Hog**(주사위 게임), **Cats**(타이핑 테스트), **Ants**(타워 디펜스, Plants vs. Zombies 유사), **Scheme**(Scheme 인터프리터 구현) 4개다. 모두 위 저장소들에서 시작 코드와 솔루션을 확인할 수 있다.

---

## 5. 시험(Exams): 1992년부터 2025년까지 방대한 공개 아카이브

CS61A 시험 자료는 세 곳의 공개 아카이브에서 **수십 년치**를 무료로 열람할 수 있다. 이는 CS61A 독학 시 가장 강력한 자원 중 하나다.

| 아카이브 | 커버 범위 | 접근 | URL |
|----------|-----------|------|-----|
| **cs61a.org/resources/** | Fall 2014 ~ Fall 2025 (~35학기) | ✅ 공개 | https://cs61a.org/resources/ |
| **TBP (Tau Beta Pi)** | Spring 1992 ~ Fall 2024 (~70+) | ✅ 공개 | https://tbp.berkeley.edu/courses/cs/61A/ |
| **HKN (Eta Kappa Nu)** | Spring 1994 ~ Spring 2018 | ✅ 공개 | https://hkn.eecs.berkeley.edu/exams/course/cs/61a |

**cs61a.org/resources/** 가 가장 추천할 만한 아카이브다. 각 학기의 Midterm 1, Midterm 2, Final 시험지 PDF와 솔루션 PDF를 직접 다운로드할 수 있다. 일부 문제에는 YouTube 풀이 워크스루 영상도 포함되어 있다. **주제별 문제 정리**(Environment Diagrams, Recursion, Tree Recursion, Higher-Order Functions 등)도 제공되어, 약점 분야를 집중 연습할 수 있다.

또한 cs61a.org에서는 시험 대비 학습 가이드 PDF도 공개한다:
- MT1 학습 가이드: `cs61a.org/assets/pdfs/61a-mt1-study-guide.pdf`
- MT2 학습 가이드: `cs61a.org/assets/pdfs/61a-mt2-study-guide.pdf`
- Final 학습 가이드: `cs61a.org/assets/pdfs/61a-final-study-guide.pdf`

---

## 6. 코드 실행 환경: 브라우저 IDE와 시각화 도구 모두 공개

CS61A는 자체적으로 강력한 브라우저 기반 개발 환경을 운영하며, 모두 **로그인 없이** 사용 가능하다.

| 도구 | 접근 | URL | 설명 |
|------|------|-----|------|
| **61A Code (Python)** | ✅ 공개 | https://code.cs61a.org/ | Python 3.9 인터프리터, 코드 에디터 |
| **61A Code (Scheme)** | ✅ 공개 | https://code.cs61a.org/scheme | 61A Scheme 인터프리터 |
| **61A Code (SQL)** | ✅ 공개 | https://code.cs61a.org/sql | SQLite, 강의 테이블 사전 로드 |
| **Python Tutor** | ✅ 공개 | https://pythontutor.com/cp/composingprograms.html | 환경 다이어그램 시각화 (CS61A 핵심 도구) |
| **OKPy (로컬 실행)** | ✅ 공개 | 과제 zip에 포함 | `python3 ok --local`로 로그인 없이 테스트 |

**61A Code**는 특히 주목할 만하다. Python·Scheme·SQL 세 언어의 인터프리터가 브라우저에서 완전히 실행되며, 한 번 로드 후에는 **오프라인에서도 작동**한다. `draw()` 함수로 연결 리스트와 트리의 박스-포인터 다이어그램을 시각화할 수 있고, Debug 버튼으로 Python Tutor 환경 다이어그램을 바로 생성할 수 있다. Scheme 모드에서는 트리 재귀 실행 과정과 환경 다이어그램을 시각화한다.

**OKPy 사용법**: 각 과제 zip 파일에 `ok` 바이너리와 `.ok` 설정 파일이 포함되어 있다. 기본 명령 `python3 ok`은 Berkeley 서버 연결을 시도하지만, `python3 ok --local` 옵션을 추가하면 **모든 서버 통신을 차단**하고 로컬에서만 테스트를 실행한다. 특정 문제만 테스트하려면 `python3 ok -q <question_name> --local`, 상세 출력은 `python3 ok -v --local`을 사용한다.

---

## 7. 추천 학습 경로: 외부 학습자를 위한 최적 조합

다양한 자료를 어떻게 조합해야 하는지 정리한다. 전 CS61A TA인 Pamela Fox의 가이드와 csdiy.wiki의 추천을 종합했다.

**교재 + 영상 병행**: cs61a.org 캘린더에서 각 강의 주제와 대응하는 Composing Programs 섹션을 확인하고, YouTube 플레이리스트를 시청한 후 해당 교재 섹션을 읽는다. 영상과 교재는 비슷한 내용을 다루므로 둘 다 사용하거나 하나만 선택해도 된다.

**과제 실습**: InsideEmpire의 Fall 2024 시작 코드 저장소에서 과제를 다운로드하고, `python3 ok --local`로 채점하면서 풀어본다. 막히면 같은 학기의 솔루션 저장소를 참고한다.

**시험 대비**: cs61a.org/resources/에서 최근 3~4학기 시험을 시간 제한을 두고 풀어본다. 주제별 약점은 "Exam Questions by Topic" 섹션을 활용한다.

| 추가 참고 자료 | URL |
|----------------|-----|
| Pamela Fox "How to Audit CS61A" | http://blog.pamelafox.org/2022/07/how-to-audit-cs61a.html |
| csdiy.wiki CS61A 가이드 | https://csdiy.wiki/en/%E7%BC%96%E7%A8%8B%E5%85%A5%E9%97%A8/Python/CS61A/ |
| Albert Wu 연습문제 | https://albertwu.org/cs61a/ |
| Ben Cuan 노트 | https://notes.bencuan.me/cs61a/ |
| Alvin Wan abcSICP 보충교재 | https://alvinwan.com/publications/abcSICP.pdf |
| CS61A 인프라 문서 | https://docs.cs61a.org/ |
| Scheme 명세 | https://cs61a.org/articles/scheme-spec/ |

---

## 결론: 로그인 벽은 사실상 우회 가능하다

CS61A는 세계에서 가장 접근성 높은 대학 CS 강의 중 하나다. **교재(Composing Programs)**, **DeNero의 YouTube 강의 ~200개**, **브라우저 IDE(code.cs61a.org)**, **30년치 시험 아카이브**, **GitHub의 수십 개 과제 저장소**가 모두 무료 공개되어 있다. 유일하게 접근 불가능한 것은 교실 라이브 녹화(bCourses), Ed 토론 포럼, Gradescope 성적 시스템 정도다. 핵심 학습 콘텐츠는 **100% 외부 접근 가능**하며, OKPy `--local` 플래그 덕분에 자동 채점까지 로컬에서 할 수 있다. 과거 학기 사이트 리다이렉트 문제는 InsideEmpire(Fall 2024)와 cs61a.vercel.app(Spring 2022) 미러가 완전히 해결해준다. 가장 최신이며 완전한 자료 세트를 원한다면 **cs61a.org(현재 학기) + InsideEmpire Fall 2024 아카이브 + GitHub 과제 저장소** 조합이 최적이다.