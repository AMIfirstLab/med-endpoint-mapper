# Endpoint ontology guide

이 레포의 `EP-*` ID는 데모 namespace이며 SNOMED CT, LOINC, CDISC의 공식 코드가 아니다.
프로덕션에서는 `external_mappings` 필드를 추가하고 라이선스와 버전을 기록해야 한다.

## 승인 원칙

- canonical / alias match: confidence와 domain이 일치하면 자동 승인 가능
- fuzzy match: 반드시 review queue로 보냄
- unmapped: 가장 비슷한 개념으로 강제 배정하지 않음
- ontology 수정: PR에서 reviewer와 변경 사유를 기록
