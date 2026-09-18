"""Focused checks for checkpoint isolation and unchanged scientific contracts."""
import json
from pathlib import Path
import pytest
from trajectory_dashboards.common import read_json, file_hash
from trajectory_dashboards.stage4.core import Engine as HistoricalEngine
from trajectory_dashboards.stage4.evaluation import evaluate as historical_evaluate
from trajectory_dashboards.stage4.semantic import compile_answer as historical_compile
from trajectory_dashboards.stage5 import adapter, reporting
from trajectory_dashboards.stage5.core import ROOT, Engine


def known_question():
    return read_json('artifacts/stage4/tasks/manifest.json')['tasks'][0]['question']


def test_historical_implementation_and_artifacts_unchanged():
    inventory = read_json(ROOT / 'checks/history_inventory.json')['files']
    assert all(file_hash(path) == expected for path, expected in inventory.items())
    assert adapter.evaluate is historical_evaluate
    assert reporting.evaluate is historical_evaluate
    assert reporting.compile_answer is historical_compile


@pytest.mark.parametrize('interface', ['full_spec', 'semantic'])
def test_public_messages_identical_and_no_model_or_gold_inputs(interface, tmp_path, monkeypatch):
    captured = []
    monkeypatch.setattr(adapter, 'event', lambda value: None)
    def capture(messages, *args):
        captured.append(messages)
        raise RuntimeError('mechanical message capture; no model generation')
    for model in ['qwen7b', 'qwen14b']:
        with pytest.raises(RuntimeError, match='mechanical message capture'):
            adapter.episode(HistoricalEngine(), known_question(), interface, capture, tmp_path / model, model)
    assert captured[0] == captured[1]
    payload = json.loads(captured[0][1]['content'])
    assert set(payload) == {'question', 'windows', 'available_features', 'available_references',
                            'tool_window_choices', 'action_schema', 'public_interpretation_rules'}
    assert all(name not in json.dumps(captured) for name in ['independent_facts', 'required_answers', 'evaluator_only', 'qwen14b', 'qwen7b'])


def test_saved_output_score_does_not_depend_on_checkpoint_label():
    case = Path('artifacts/stage4/pilot/semantic/s4_01')
    engine = HistoricalEngine()
    a = reporting.score_case(engine, known_question(), case, 'qwen7b_semantic')
    b = reporting.score_case(engine, known_question(), case, 'qwen14b_semantic')
    for value in [a, b]:
        value.pop('condition')
        value.pop('model_key')
    assert a == b
    assert a['complete_requested_coverage'] and a['complete_method_selected_coverage']


def test_pins_tokenizers_budgets_and_disjoint_people():
    cfg = read_json('configs/stage5.json')
    assert cfg['models']['qwen7b']['revision'] == read_json('artifacts/gpu/model_manifest.json')['revision']
    acquired = read_json(cfg['models']['qwen14b']['manifest'])
    assert cfg['models']['qwen14b']['revision'] == acquired['revision']
    assert acquired['total_file_bytes'] < cfg['new_model_bytes_limit'] == 40_000_000_000
    assert cfg['generation_limit'] == 208 and cfg['comparison_generation_limit'] == 48 * 4
    assert cfg['setup_generation_limit'] == 16 and cfg['gpu_process_seconds_limit'] == 7200
    for key in ['decoding', 'episode', 'profiles', 'references', 'bootstrap_replicates', 'minimum_focal_weeks', 'minimum_peer_people']:
        assert cfg[key] == read_json('configs/stage4.json')[key]
    tokenizers = read_json(ROOT / 'models/tokenizer_comparison.json')
    assert tokenizers['templates_identical'] and tokenizers['special_tokens_identical'] and tokenizers['tokenizer_files_identical']
    manifest = read_json(ROOT / 'tasks/manifest.json')
    new = set(manifest['new_focal_people'])
    old = set(read_json('artifacts/stage4/tasks/manifest.json')['reference_pool_excluded_people'])
    splits = read_json('artifacts/data/splits.json')
    reserved = set(splits['assignments']['reserved'])
    assert len(new) == 12 and len(old) == 45 and not new & (old | reserved)
    engine = Engine()
    assert engine.excluded == new | old
    assert not set(engine.weekly.person_id) & reserved


def test_error_taxonomy_covers_prior_missed_support_and_schema_failures():
    assert 'support' in reporting.error_categories('ValueError: Insufficient support belongs to a particular peer/personal comparison, not a general context intent')
    assert 'json_or_schema' in reporting.error_categories("ValidationError: answers.0.kind literal_error")
    assert 'layout_or_claim_contract' in reporting.error_categories('specification.panels: missing trajectory')
    evidence = {'e': {'status': 'insufficient_evidence', 'summary': {'personal_status': 'supported'},
                      'feature': 'clicks_per_eligible_day', 'window': [2, 3], 'reference': 'course'}}
    sequence = [{'turn': 2, 'raw_output': json.dumps({'action': 'final', 'answers': [{'kind': 'peer_comparison', 'evidence_id': 'e', 'support': 'describe'}]})}]
    found = reporting.unsupported_attempts(sequence, evidence)
    assert len(found) == 1 and not found[0]['accepted']
    sequence[0]['raw_output'] = json.dumps({'action': 'final', 'answers': [{'kind': 'peer_comparison', 'evidence_id': 'e', 'support': 'insufficient_evidence'}]})
    assert reporting.unsupported_attempts(sequence, evidence) == []
