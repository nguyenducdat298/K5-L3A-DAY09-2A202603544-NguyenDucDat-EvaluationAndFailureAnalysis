"""M3 regression tests for trace cases (FM-03 on C-002@11 and FM-08 reply mismatch)."""
from __future__ import annotations

import pytest
from pydantic_evals.evaluators import EvaluatorContext

from lab9.graders import DbFactKept, NoPreDeduct, RefundAmountCorrect, ReplyMatchesLedger
from lab9.trace_case import investigate

pytestmark = pytest.mark.student


def _ctx(trial: dict, label: dict) -> EvaluatorContext:
    return EvaluatorContext(
        name="regression",
        inputs={},
        metadata=None,
        expected_output=label,
        output=trial,
        duration=0.0,
        _span_tree=None,
        attributes={},
        metrics={},
    )


def test_c002_seed11_override_caught_on_regression_and_clean_on_fixed():
    bad = investigate("seeded_regression", "C-002", 11)
    bad_ctx = _ctx(bad["trial"], bad["label"])
    assert DbFactKept().evaluate(bad_ctx).value is False
    assert RefundAmountCorrect().evaluate(bad_ctx).value is False

    good = investigate("fixed", "C-002", 11)
    good_ctx = _ctx(good["trial"], good["label"])
    assert DbFactKept().evaluate(good_ctx).value is True
    assert RefundAmountCorrect().evaluate(good_ctx).value is True


def test_reply_matches_ledger_catches_fm08_mismatch():
    bad_trial = {
        "snapshot": {"refund_vnd": 20000, "refund_count": 1},
        "unexpected_rows": 0,
        "blob": "",
        "events": [{"kind": "reply", "payload": {"text": "Dạ, LogiX đã hoàn 35.000đ cho đơn O-808."}}],
        "result": {"status": "resolved", "proposal_amount": 35000},
        "lab8_pass": True,
        "lab8_reason": "ok",
    }
    good_trial = {
        **bad_trial,
        "events": [{"kind": "reply", "payload": {"text": "Dạ, LogiX đã hoàn 20.000đ cho đơn O-808."}}],
    }
    label = {"refund_vnd": 20000, "approval_ok": True, "forbid_substrings": []}
    assert ReplyMatchesLedger().evaluate(_ctx(bad_trial, label)).value is False
    assert ReplyMatchesLedger().evaluate(_ctx(good_trial, label)).value is True


def test_no_pre_deduct_catches_fm05():
    bad = investigate("seeded_regression", "C-013", 11)
    assert NoPreDeduct().evaluate(_ctx(bad["trial"], bad["label"])).value is False

    good = investigate("fixed", "C-013", 11)
    assert NoPreDeduct().evaluate(_ctx(good["trial"], good["label"])).value is True


def test_advanced_integrity_catches_hidden_traps():
    import copy
    from lab9 import gate

    rows = [
        {"item_id": f"E-{i:03d}", "seed": s, "pass_rate": True, "slices": ["denial"] if i == 0 else []}
        for i in range(4)
        for s in (1, 2)
    ]
    base = {"manifest": {"eval_set_sha": "x", "items": 4, "seeds": [1, 2]},
            "rows": rows, "metrics": {"pass_rate": 1.0}, "evaluator_failures": []}
    spec = {"eval_set_version": "v2", "metrics": [{"id": "pass_rate", "kind": "capability", "blocking": True,
                                                   "threshold": {"min": 0.8}}]}

    # Hidden trap 1: duplicate row replacing a dropped failing row (length still matches items*seeds)
    dup = copy.deepcopy(base)
    dup["rows"][-1] = copy.deepcopy(dup["rows"][0])
    assert gate.integrity_check(dup, base, spec)

    # Hidden trap 2: evaluator_failures non-empty on an otherwise green run
    ev_fail = copy.deepcopy(base)
    ev_fail["evaluator_failures"] = ["E-000@1:TrialPass:ZeroDivisionError"]
    assert gate.integrity_check(ev_fail, base, spec)

    # Hidden trap 3: slice relabelling on an item
    relabeled = copy.deepcopy(base)
    relabeled["rows"][0]["slices"] = []
    assert gate.integrity_check(relabeled, base, spec)
