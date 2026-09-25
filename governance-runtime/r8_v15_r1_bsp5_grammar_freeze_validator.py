"""R8 v15-r1 Slice 32: exact local BSP-5 grammar freeze equality only."""
from __future__ import annotations
import json
from collections.abc import Mapping
from typing import Any, Dict

FROZEN_GRAMMAR=json.loads(r'''{"schema":"bsp-5-grammar/v1","status":"INTERNAL_NORMALIZATION_ARTIFACT_NON_AUTHORITATIVE","authority_effect":"NONE","current_candidate_version":15,"parser_states":["NORMAL","FENCED_CODE","FENCED_SEMANTIC_TEST_DATA","CASE_SECTION","GUARD_RECORD_SECTION","CURRENT_STATUS_BLOCK","PREDECESSOR_STATUS_BLOCK","PRIOR_REVIEW_METADATA_BLOCK","MARKED_SEMANTIC_TEST_SECTION"],"line_classes":["CURRENT_STATUS","PRIOR_STATUS","PRIOR_REVIEW_METADATA","SEMANTIC_CONTENT","SEMANTIC_TEST_LITERAL","LEGACY_GUARD_TABLE","BLANK_STRUCTURAL"],"current_status_binding":{"begin_marker":"<!-- BSP:CURRENT_STATUS_BEGIN version=15 -->","end_marker":"<!-- BSP:CURRENT_STATUS_END -->","exact_block_count":1,"version_must_equal_current_candidate_version":true,"nested_blocks_forbidden":true,"unterminated_block_result":"REVIEW_PACKET_INCOMPLETE","multiple_blocks_result":"REVIEW_PACKET_INCOMPLETE","mismatched_version_result":"REVIEW_PACKET_INCOMPLETE"},"patterns":{"version_token":"\\bR8\\s+v(?<version>\\d+)\\b","status_token":"\\b(?:CHANGES_REQUIRED|BOUNDED_PASS|INSUFFICIENT_EVIDENCE|REVIEW_REQUIRED|INDEPENDENT_REVIEW_REQUIRED|NOT_IMPLEMENTED)\\b","review_path":"(?:review-evidence/|review-adjudications/)","review_heading":"(?i)\\b(?:independent\\s+review|review\\s+adjudication|adjudication)\\b","status_header":"(?i)^\\s*Status\\s*:","fenced_code":"^\\s*```","semantic_test_fence":"^\\s*```(?:json|yaml|text)?\\s+semantic-test-data\\s*$","case_heading":"^#{2,6}\\s+.*(?:case|cases|vector|vectors|preregistered)","guard_record_heading":"^#{2,6}\\s+.*(?:guard|GuardRegistry|CaseRegistry)","semantic_test_section_begin":"^<!-- BSP:SEMANTIC_TEST_SECTION_BEGIN id=(?<id>[A-Za-z0-9._:-]+) -->$","semantic_test_section_end":"^<!-- BSP:SEMANTIC_TEST_SECTION_END id=(?<id>[A-Za-z0-9._:-]+) -->$"},"semantic_test_contexts":{"allowed_states":["CASE_SECTION","GUARD_RECORD_SECTION","FENCED_SEMANTIC_TEST_DATA","MARKED_SEMANTIC_TEST_SECTION"],"ordinary_prose_status_token_is_semantic_test_literal":false,"marked_section_rules":{"exact_standalone_line":true,"outside_fenced_code_only":true,"begin_end_id_must_match":true,"nesting_forbidden":true,"zero_length_forbidden":true,"cross_mechanism_corpus_required_id":"cross-mechanism-adversarial-corpus"}},"classification_order":["consume exact current-status begin/end markers and validate block cardinality/version when outside fenced code","consume exact semantic-test-section begin/end markers and validate pairing/id/nesting when outside fenced code","track fenced-code and fenced-semantic-test-data entry/exit","track case and guard-record sections","classify lines inside valid CURRENT_STATUS_BLOCK as CURRENT_STATUS","classify predecessor status/review blocks using explicit version + status/review grammar","classify status-token lines inside allowed semantic-test states as SEMANTIC_TEST_LITERAL","classify legacy guard tables as LEGACY_GUARD_TABLE","otherwise SEMANTIC_CONTENT or BLANK_STRUCTURAL"],"remove_classes":["PRIOR_STATUS","PRIOR_REVIEW_METADATA","LEGACY_GUARD_TABLE"],"retain_classes":["CURRENT_STATUS","SEMANTIC_CONTENT","SEMANTIC_TEST_LITERAL","BLANK_STRUCTURAL"],"residual_rule":{"rerun_same_parser":true,"fail_if":["PRIOR_STATUS","PRIOR_REVIEW_METADATA"],"require_exact_current_status_block_count":1,"raw_token_search_is_authoritative":false,"require_all_marked_semantic_test_sections_well_formed":true},"guard_table_omission_rule":{"allowed_only_with_guard_omission_manifest":true,"source_case_set_equality_required":true,"unique_case_or_invariant_semantics_may_not_be_removed":true},"governing_rules":["R8V15-I010","R8V15-I011","R8V15-I012","R8V15-I013"],"review_projection":"BLIND_PROCESS_HISTORY_STRIPPED_SEMANTICS_PRESERVED"}''')

class BSP5GrammarFreezeError(ValueError):
    def __init__(self,code:str,message:str):
        super().__init__(f"{code}: {message}"); self.code=code

def _semantic_json(value:Any)->str:
    try:
        return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(",",":"),allow_nan=False)
    except (TypeError,ValueError) as exc:
        raise BSP5GrammarFreezeError("BSP5_GRAMMAR_JSON_INVALID",str(exc)) from exc

_FROZEN_KEY=_semantic_json(FROZEN_GRAMMAR)

def validate_bsp5_grammar_freeze(record:Mapping[str,Any])->Dict[str,Any]:
    if not isinstance(record,Mapping):
        raise BSP5GrammarFreezeError("BSP5_GRAMMAR_INVALID","record must be mapping")
    if _semantic_json(record)!=_FROZEN_KEY:
        raise BSP5GrammarFreezeError("BSP5_GRAMMAR_MISMATCH","input is not semantically equal to frozen const object")
    return {"locally_valid":True,"validation_scope":"EXACT_BSP5_GRAMMAR_CONST_EQUALITY_ONLY","authority_effect":"NONE","parser_executed":False,"classification_verified":False,"residual_rule_verified":False,"review_projection_verified":False,"review_authority_granted":False,"terminal_authority":False}
