# PRD — console-mvc (MVC 스켈레톤)

상위 컨텍스트: [../../../docs/PRD.md](../../../docs/PRD.md)

## 목적

반도체 시료 생산주문관리 시스템의 콘솔 UI 골격. Model / View / Controller 패키지 구조와 역할 분리를 완성하고, 메인 시스템의 6개 메뉴 화면 흐름을 이 구조 위에 구현한다.

## 패키지 구조 (최소)

```
model/        - Sample, Order 등 도메인 엔티티 (필드 정의는 ../../../docs/SCHEMA.md가 원천)
view/         - 콘솔 출력 담당. 메뉴 렌더링, 입력 프롬프트, 결과 표시. 비즈니스 로직 없음
controller/   - 사용자 입력을 받아 Model/Service 호출 후 View에 결과 전달
app / main    - 메인 루프 진입점. 메뉴 선택 → Controller 라우팅
```

역할 분리 원칙:
- View는 Model이나 저장소를 직접 참조하지 않는다 (Controller를 통해서만 데이터 전달받음).
- Controller는 콘솔 입출력을 직접 하지 않는다 (View에 위임).
- Model은 UI에 의존하지 않는 순수 도메인 객체.

## 메인 루프 최소 요구사항

1. 메인 메뉴 표시: 시료 관리 / 시료 주문 / 주문 승인·거절 / 모니터링 / 생산라인 조회 / 출고 처리 / 종료
2. 메인 메뉴 상단에 요약 정보 표시: 등록 시료 수, 총 재고, 전체 주문 수, 생산라인 대기 건수
3. 사용자 번호 선택 → 해당 Controller로 라우팅 → 하위 메뉴 진입
4. 각 하위 메뉴는 뒤로가기(`0`)로 메인 메뉴 복귀 가능

## 화면별 Controller 책임 (도메인 규칙은 상위 PRD 참조)

| 메뉴 | Controller 책임 |
|---|---|
| 시료 관리 | 등록 입력값 검증 후 Model 생성 요청, 목록/검색 결과를 View에 전달 |
| 시료 주문 | 시료 ID·고객명·수량 입력 검증, `RESERVED` 주문 생성 요청 |
| 주문 승인/거절 | `RESERVED` 목록 조회 요청, 승인/거절 선택에 따른 상태 전이 요청 |
| 모니터링 | 상태별 집계(`REJECTED` 제외 — 이 메뉴에 한정된 규칙) 및 재고 현황 조회 요청 (읽기 전용) |
| 생산라인 조회 | 생산 큐 상태 조회 요청 (읽기 전용). `PRODUCING → CONFIRMED`("생산 완료") 트리거는 이 모듈의 책임이 아니다 — 통합 계층이 담당 |
| 출고 처리 | `CONFIRMED` 목록 조회, 선택 항목 출고 요청 |

시료 주문 생성 시 `sampleId`가 실제 존재하는 Sample을 가리키는지에 대한 참조 무결성 최종 검증은 이 모듈의 책임이 아니다 — 통합 계층이 담당한다 (결정 근거: 루트 [docs/DECISIONS.md](../../../docs/DECISIONS.md), [docs/PRD.md §7](../../../docs/PRD.md)).

## 데이터 연동

이 PoC 단계에서는 in-memory Model로 동작 가능하나, 최종 통합(SampleOrderSystem) 시점에는 `data-persistence`의 Repository 인터페이스를 Controller가 호출하는 구조로 대체한다. Controller가 저장 방식(JSON/메모리 등)을 알 필요 없도록 Repository 인터페이스에 의존한다.

## 완료 기준

- Model/View/Controller 패키지가 물리적으로 분리되어 있다.
- 메인 메뉴에서 6개 기능 모두 진입 가능한 스텁 혹은 실제 동작이 존재한다.
- View 코드에 비즈니스 로직(상태 전이 계산, 재고 계산 등)이 없다.
