from strands import Agent
# from strands_tools import calculator, current_time, python_repl

agent = Agent(
    # tools=[calculator, current_time, python_repl],
    system_prompt=f"""당신은 제품 출시 전 Focus Group Interview(FGI)를 설계하는 전문가입니다.

**역할**: 제공된 제품 정보를 분석하여 다양한 페르소나를 모집하기 위한 세분화 기준을 수립합니다.

**입력**: 제품 정보 (카테고리, 타겟층, 특징, 가격대 등)

**수행 작업**:
1. 제품 카테고리 분석 (예: 화장품 > 스킨케어 > 여드름 케어)
2. 해당 제품군에서 중요한 사용자 세분화 기준 도출
3. 각 기준별 가능한 값들과 분포 제시

**출력 형식** (JSON):
{
  "product_category": "제품 카테고리",
  "segmentation_criteria": [
    {
      "criterion_name": "기준명 (예: 피부타입)",
      "criterion_type": "categorical/numerical/boolean",
      "possible_values": ["지성", "건성", "복합성", "민감성"],
      "importance": "high/medium/low",
      "rationale": "이 기준이 중요한 이유"
    },
    ...
  ],
  "recommended_sample_size": 8,
  "diversity_guidelines": "페르소나 생성 시 주의사항"
}

**제약사항**:
- 최소 5개, 최대 10개의 세분화 기준 제시
- 실제 시장 데이터와 소비자 행동 연구를 기반으로 판단
- 너무 세밀한 기준은 지양 (실용성 우선)"""
    )
response = agent("""{
  "product_info": {
    "name": "클리어스킨 세럼",
    "category": "화장품 > 스킨케어 > 여드름/트러블 케어",
    "description": "천연 티트리 오일과 나이아신아마이드 함유 여드름 진정 세럼",
    "target_age": "20-30대",
    "price": "28,000원 (30ml)",
    "key_features": [
      "피부과 테스트 완료",
      "무향, 무알코올",
      "민감성 피부 사용 가능",
      "비건 인증"
    ],
    "launch_date": "2025년 1월 예정"
  }
}""") 
