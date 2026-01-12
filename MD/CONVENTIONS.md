# 📜 Project Standard Conventions & Architecture (ver0.1)

이 문서는 프로젝트의 코드 품질 유지, 원활한 협업, 그리고 일관된 프로젝트 구조를 위한 표준 가이드라인을 정의합니다. 모든 팀원은 개발 시작 전 본 가이드를 반드시 숙지해야 합니다.

---

## 0. 개발 프로세스 및 AI 협업 원칙 (Core Principles)

### 🤖 AI 협업 원칙 (AI-Agent Interaction)
- **No Assumptions**: AI는 구현 방법이 모호하거나 정보가 부족할 경우 추측하지 말고 사용자에게 질문해야 합니다.
- **Context Loading**: 코드 생성 전 반드시 `@CONVENTIONS.md`와 `@TASKS.md`를 최우선 참조합니다.
- **Modular Coding**: 한 번에 다수의 파일을 수정하기보다 하나의 기능(Task) 단위로 코드를 제안하고 검증받습니다.

### 🔄 기획 및 설계 우선 원칙
- **구현 트리거**: 실제 코드 작성은 사용자가 명시적으로 '구현' 또는 'Act' 명령을 내린 단위에 대해서만 시작합니다.
- **피드백 루프**: 각 단계별 검증을 통해 이슈 발견 시 지체 없이 이전 단계로 돌아가 설계를 보완합니다.

---

## 1. 공통 기본 원칙

* **Clean Code**: 의미 있는 변수명 사용 및 함수의 단일 책임 원칙(SRP)을 준수합니다.
* **Don't Repeat Yourself (DRY)**: 중복되는 로직은 공통 모듈이나 유틸리티로 분리합니다.
* **Separation of Concerns (SoC)**: UI, 비즈니스 로직, 데이터 접근 계층을 명확히 분리합니다.
* **API-First Design**: 서비스 간 통신을 위해 API 스펙(Swagger/OpenAPI)을 먼저 정의하고 개발을 시작합니다.
* **Stateless Backend**: 서버는 상태를 가지지 않으며, 모든 인증은 JWT 토큰을 기반으로 처리합니다.
* **YAGNI (You Ain't Gonna Need It)**: 실제로 필요하기 전까지는 미리 복잡한 기능을 구현하지 않습니다.

---

## 2. 기술 스택 및 환경 구성 (Tech Stack & Environment)

| 구분 | 기술 스택 | 버전 / 비고 |
| :--- | :--- | :--- |
| **Frontend** | React, TypeScript | Node.js 20.11.1 / React 18.2.0 / TypeScript 5.3.3 |
| **Backend (API)** | Spring Boot, Spring Security | Java 17 / Spring Boot 3.2.5 / Spring Security 6.2.3 |
| **AI Service** | Python, FastAPI | Python 3.11.9 / FastAPI 0.110.0 |
| **Database (Metadata)** | TimescaleDB | TimescaleDB 2.13.1 |
| **Database (Service)** | PostgreSQL | PostgreSQL 15.6 |

---

## 3. 명명 규칙 (Naming Conventions)

| 대상 | React (TS) | Java (Spring) | Python (FastAPI) |
| :--- | :--- | :--- | :--- |
| **폴더 (Directory)** | `kebab-case` | `lowercase` | `snake_case` |
| **파일 (File)** | `PascalCase` (Comp) | `PascalCase` | `snake_case` |
| **클래스 (Class)** | `PascalCase` | `PascalCase` | `PascalCase` |
| **함수/변수** | `camelCase` | `camelCase` | `snake_case` |
| **상수 (Constant)** | `UPPER_SNAKE` | `UPPER_SNAKE` | `UPPER_SNAKE` |
| **DB 테이블/컬럼** | - | `snake_case` | `snake_case` |

---

---
## 4. 프로젝트 폴더 구조 (Project Structure)

### ⚛️ Frontend (src/)
**Feature-Sliced Design(FSD)** 개념을 차용하여 기능별 응집도를 높인 구조를 사용합니다.

- **app/**: 전역 설정 (Providers, Router, Global CSS)
- **pages/**: 라우트별 페이지 컴포넌트 (비즈니스 로직 최소화)
- **widgets/**: 여러 feature가 결합된 독립적 복합 컴포넌트
- **features/**: 도메인 기반 핵심 기능 단위 (auth, chat, report, admin)
    - **[feature]/api/**: API 호출 함수
    - **[feature]/ui/**: 해당 기능 전용 컴포넌트
    - **[feature]/hooks/**: 커스텀 훅 (Logic)
    - **[feature]/types/**: 타입 정의
- **shared/**: 전역 공통 요소 (ui-kit, utils, api-client, assets)

### ☕ Java Backend (src/main/java/...)
**Domain-Driven 패키지 구조**를 사용하여 도메인별로 계층을 분리합니다.

- **global/**: 전역 공통 설정 (Security, Config, Exception, Util)
- **domain/**: 비즈니스 도메인별 패키지 (user, video, report, chat)
    - **controller/**: API 엔드포인트
    - **service/**: 비즈니스 로직
    - **repository/**: DB 접근 인터페이스
    - **entity/**: JPA Entity
    - **dto/**: Request/Response 객체

### 🐍 Python Backend (app/)
**Module-based 구조**를 사용하여 기능별로 모듈화합니다.

- **core/**: 앱 전역 설정 (config, security, database)
- **api/**: API 라우터 정의 및 버전 관리 (v1/api.py)
- **services/**: 핵심 비즈니스 로직 및 AI 엔진 연동
- **schemas/**: Pydantic 모델 (Request/Response 데이터 검증)
- **models/**: DB 테이블 모델 (필요 시 사용)
- **main.py**: 애플리케이션 진입점 및 FastAPI 초기화

---

## 5. 기술 스택별 상세 규칙

### ⚛️ Frontend
- **상태 관리**: 서버 데이터는 `TanStack Query`, 전역 UI 상태는 `Zustand`를 사용합니다.
- **Logic-UI 분리**: 복잡한 비즈니스 로직은 반드시 Custom Hooks(`use...`)로 추출합니다.
- **Type Safety**: `any` 사용을 엄격히 금지하며, 인터페이스 정의를 우선합니다.

### ☕ Java (Spring Boot)
- **Lombok**: `@Getter`, `@NoArgsConstructor`, `@Builder`를 사용하며 `@Data`는 사용을 금지합니다.
- **변환 (Mapping)**: Entity와 DTO 간 변환은 `MapStruct` 라이브러리를 사용합니다.
- **예외 처리**: `global/exception` 패키지 내 `@RestControllerAdvice`를 통해 전역 에러를 응답 포맷에 맞춰 처리합니다.

### 🐍 Python (FastAPI)
- **Type Hinting**: 모든 인자와 반환값에 타입을 명시합니다.
- **Validation**: 요청/응답 스키마는 `Pydantic` 모델을 사용합니다.
- **Dependency**: DB 세션 및 유틸리티는 `Depends()`를 통한 의존성 주입을 활용합니다.

---

## 6. 데이터베이스 규칙 (Database Conventions)

- **공통 컬럼 (Audit)**: 모든 테이블은 아래 컬럼을 필수로 포함합니다.
  - `created_at`: 생성 일시 (Timestamp)
  - `updated_at`: 수정 일시 (Timestamp)
  - `created_by`: 생성자 (Varchar, ID)
- **명명 규칙**: 테이블 및 컬럼명은 `snake_case`를 사용합니다.
- **Soft Delete**: 데이터 삭제 시 실제로 삭제하지 않고 `deleted_at` 컬럼을 활용하는 것을 원칙으로 합니다. (필요 시 적용)

---

## 7. API 디자인 및 통신 (API Conventions)

* **버전 관리**: 모든 엔드포인트는 `/api/v1/`로 시작합니다.
* **공통 성공/실패 응답**:
```json
{
  "success": true,
  "data": { "item": "value" },
  "error": null
}

{
  "success": false,
  "data": null,
  "error": {
    "code": "ERROR_CODE",
    "message": "사용자 메시지"
  }
}
```

---

## 8. Git 전략 및 커밋 규칙

### 🌿 브랜치 전략 (Git Flow Lite)
프로젝트의 안정성과 빠른 배포를 위해 단순화된 Git Flow를 사용합니다.

- **main**: 상시 배포 가능한 상태의 메인 브랜치 (Production)
- **develop**: 다음 출시 버전을 위해 기능을 통합하는 브랜치 (Staging)
- **feature/[기능명]**: 단위 기능을 개발하는 브랜치. 완료 후 `develop`으로 머지
- **fix/[버그명]**: 출시 버전에서 발견된 긴급 버그를 수정하는 브랜치

### 💬 커밋 메시지 형식 (Conventional Commits)
`type(scope): subject` 형식을 준수하여 히스토리 가독성을 높입니다.

- **feat**: 새로운 기능 추가
- **fix**: 버그 수정
- **docs**: 문서 수정 (README, CONVENTIONS 등)
- **refactor**: 코드 리팩토링 (기능 변경 없이 구조만 개선)
- **style**: 코드 포맷팅, 세미콜론 누락 수정 (비즈니스 로직 변경 없음)
- **test**: 테스트 코드 추가 및 리팩토링
- **chore**: 빌드 업무, 패키지 매니저 설정 등 (기타 변경사항)

**예시**: `feat(chat): AI 대화 히스토리 저장 API 구현`

---

## 9. 주석 및 문서화 규칙 (Commenting & Documentation)

코드 자체로 의도를 파악할 수 있는 'Clean Code'를 지향하되, 복잡한 로직이나 API 명세에는 아래 규칙에 따라 주석을 작성합니다.

### 💡 공통 원칙
- **Why, Not How**: '어떻게' 작동하는지보다 '왜' 이 로직이 필요한지에 집중합니다.
- **Update with Code**: 코드 변경 시 반드시 주석도 최신화합니다.
- **Remove Dead Code**: 사용하지 않는 코드는 주석 처리하지 말고 삭제합니다. (Git 히스토리로 확인 가능)

### ☕ Java (Javadoc 스타일)
클래스, 인터페이스, 공용(public) 메서드 상단에 작성합니다.
```java
/**
 * 사용자 정보 기반 보고서 생성 서비스
 * * @param userId   조회할 사용자 ID
 * @param date     보고서 기준 날짜
 * @return         생성된 보고서 엔티티
 * @throws NotFoundException 사용자를 찾을 수 없는 경우 발생
 */
public Report generateReport(Long userId, LocalDate date) { ... }
````

### 🐍 Python (Google Style Docstring)
FastAPI의 서비스 로직 및 엔진 연동 함수에 작성합니다.
``` Python
def analyze_video_clip(clip_path: str, threshold: float = 0.5) -> dict:
    """
    영상 클립을 분석하여 객체 탐지 결과를 반환합니다.

    Args:
        clip_path (str): 분석할 영상 파일의 로컬 경로
        threshold (float): 탐지 정확도 임계값 (기본값: 0.5)

    Returns:
        dict: 탐지된 객체 리스트 및 메타데이터
    """
    pass
```

### ⚛️ TypeScript / React (TSDoc 스타일)
복잡한 컴포넌트나 공통 Hook, 유틸리티 함수에 작성합니다.
```TypeScript
/**
 * AI 분석 결과에 따른 Bounding Box 오버레이 컴포넌트
 * * @param boxes - 탐지된 객체의 좌표 배열
 * @param onSelect - 박스 클릭 시 호출되는 핸들러
 */
interface OverlayProps {
  boxes: BoxType[];
  onSelect: (id: string) => void;
}
const VideoOverlay = ({ boxes, onSelect }: OverlayProps) => { ... }
````
### 🚩 특수 주석 (Annotations)
작업 중인 상태를 표시하기 위해 팀 공통 키워드를 사용합니다.

- // TODO: [작성자] 내용 : 나중에 구현해야 할 기능
- // FIXME: [작성자] 내용 : 버그가 예상되거나 수정이 필요한 급한 부분
- // NOTE: [작성자] 내용 : 다른 개발자가 알아야 할 중요한 참고 사항

---
