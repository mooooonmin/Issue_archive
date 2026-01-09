# 📜 Project Standard Conventions

이 문서는 프로젝트의 코드 품질 유지와 원활한 협업을 위한 표준 가이드라인을 정의합니다. 모든 팀원은 코드 작성 시 본 가이드를 준수해야 합니다.

---

## 1. 공통 기본 원칙 (Core Principles)

* **Clean Code**: 의미 있는 변수명 사용, 함수의 단일 책임 원칙(SRP)을 준수합니다.
* **Don't Repeat Yourself (DRY)**: 중복되는 로직은 공통 모듈이나 유틸리티로 분리합니다.
* **Separation of Concerns (SoC)**: UI, 비즈니스 로직, 데이터 접근 계층을 명확히 분리합니다.
* **YAGNI (You Ain't Gonna Need It)**: 실제로 필요하기 전까지는 미리 복잡한 기능을 구현하지 않습니다.

---

## 2. 명명 규칙 (Naming Conventions)

### 🔤 언어별 표준

| 대상 | React (TS) | Java (Spring) | Python (FastAPI) |
| :--- | :--- | :--- | :--- |
| **폴더 (Directory)** | `kebab-case` | `lowercase` | `snake_case` |
| **파일 (File)** | `PascalCase` (Comp) | `PascalCase` | `snake_case` |
| **클래스 (Class)** | `PascalCase` | `PascalCase` | `PascalCase` |
| **함수/변수** | `camelCase` | `camelCase` | `snake_case` |
| **상수 (Constant)** | `UPPER_SNAKE` | `UPPER_SNAKE` | `UPPER_SNAKE` |
| **DB 테이블/컬럼** | - | `snake_case` | `snake_case` |

---

## 3. 기술 스택별 상세 규칙

### ⚛️ Frontend (React & TypeScript)

* **컴포넌트 선언**: `const` 키워드를 사용한 화살표 함수를 권장합니다.
* **Props 구조 분해**: 컴포넌트 인자 단계에서 명시적으로 구조 분해를 수행합니다.
* **비즈니스 로직 분리**: 복잡한 상태 관리나 비즈니스 로직은 Custom Hooks(`use...`)로 추출합니다.
* **상태 관리**:
    * 서버 데이터: `TanStack Query (React Query)` 사용
    * 전역 UI 상태: `Zustand` 사용
* **구조**: Feature-based Architecture 구조를 준수합니다 (`features/`, `shared/`, `app/`).

### ☕ Java (Spring Boot)

* **Lombok 활용**: `@Getter`, `@NoArgsConstructor`, `@Builder` 등을 활용하되, `@Data` 사용은 지양합니다.
* **Entity ↔ DTO**: 외부 API 응답 및 요청에는 반드시 DTO를 사용하며, Entity를 직접 노출하지 않습니다.
* **의존성 주입**: 생성자 주입(`@RequiredArgsConstructor`)을 사용합니다.
* **예외 처리**: `@RestControllerAdvice`를 통해 전역적으로 예외를 관리합니다.

### 🐍 Python (FastAPI)

* **Type Hinting**: 모든 함수의 인자와 반환값에 명시적인 타입 힌트를 작성합니다.
* **Pydantic 모델**: 요청/응답 스키마 정의 시 반드시 `BaseModel`을 상속받아 사용합니다.
* **Async/Await**: 외부 AI 엔진 호출이나 DB I/O 발생 시 비동기 처리를 기본으로 합니다.
* **Dependency Injection**: DB 세션이나 공통 로직은 `Depends`를 통해 주입합니다.

---

## 4. API 디자인 및 통신 (API Conventions)

* **버전 관리**: 모든 엔드포인트는 `/api/v1/`로 시작합니다.
* **공통 성공 응답 포맷**:
    ```json
    {
      "success": true,
      "data": { ... },
      "error": null
    }
    ```
* **공통 에러 응답 포맷**:
    ```json
    {
      "success": false,
      "data": null,
      "error": {
        "code": "AUTH_001",
        "message": "로그인이 필요합니다."
      }
    }
    ```

---

## 5. Git 전략 및 커밋 규칙

### 🌿 브랜치 전략 (Git Flow Lite)
* `main`: 프로덕션 배포 브랜치
* `develop`: 개발 통합 브랜치
* `feature/기능명`: 개별 기능 개발 브랜치
* `fix/버그명`: 긴급 수정 브랜치

### 💬 커밋 메시지 형식 (Conventional Commits)
`type(scope): subject` 형식을 따릅니다.

* `feat`: 새로운 기능 추가
* `fix`: 버그 수정
* `docs`: 문서 수정 (README, CONVENTIONS 등)
* `refactor`: 코드 리팩토링 (결과 변경 없음)
* `style`: 코드 포맷팅 (세미콜론 누락, 린트 수정 등)
* **예시**: `feat(chat): AI 대화 히스토리 저장 기능 구현`

---

## 6. 문서화 가이드

* **API 문서**: Java(SpringDoc), Python(FastAPI Swagger)를 자동 생성하여 활용합니다.
* **주석 (Comments)**: '어떻게' 보다는 '왜' 이 코드를 작성했는지에 대해 설명합니다.

---