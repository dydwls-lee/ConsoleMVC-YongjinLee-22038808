# HARNESS — console-mvc

이 저장소는 통합 저장소(`SampleOrderSystem-YongjinLee-22038808`)의 에이전틱 개발 오케스트레이션 중 `implementer`/`test-reviewer` 두 에이전트가 담당하는 모듈이다. 전체 파이프라인과 다른 에이전트(`main`, `docs-checker`, `integration-builder`, `compliance-reviewer`, `scenario-tester`)의 역할은 통합 저장소의 `docs/HARNESS.md`를 따른다.

## implementer (console-mvc)

- 요구사항 원천: [PRD.md](PRD.md), 공유 스키마 `docs/SCHEMA.md`(통합 저장소 루트)
- 작업 순서: 통합 저장소의 `main`이 `data-persistence` 우선 진행을 지시하므로, 이 모듈은 `data-persistence`의 Repository 인터페이스 확정 이후(또는 병렬로 인터페이스만 계약 삼아) 진행 가능
- `test-driven-development` 스킬에 따라 RED → GREEN → REFACTOR로 구현
- Model/View/Controller 역할 분리 원칙(PRD §"역할 분리 원칙")을 어기는 커밋은 만들지 않는다
- 커밋은 `[ACTION]` 접두사만 사용 (RED/GREEN/REFACTOR 단계 구분 없음)
- 구현 중 PRD 모호성이나 `data-persistence` Repository 계약과의 불일치를 발견하면 코드로 임시 우회하지 말고 통합 저장소의 `docs-checker`에 보고

## test-reviewer (console-mvc)

- [PRD.md](PRD.md)의 "완료 기준"과 실제 구현/테스트를 대조
- 확인 항목: Model/View/Controller 물리적 분리 여부, View에 비즈니스 로직 누출 여부, 6개 메뉴 진입 가능 여부
- 미충족 시 구체적 사유와 함께 `implementer`에 반려, 통과 시 통합 저장소 `main`에 "통합 준비 완료" 보고
