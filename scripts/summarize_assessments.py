#!/usr/bin/env python3
"""Validate and summarize recorded independent assessments; never run a model."""

import argparse
import json
import sys
from collections import Counter
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path


DIMENSIONS = {
    "innovation": "创新性",
    "importance": "重要性",
    "reliability": "可靠性",
    "presentation": "表达质量",
}
STATUSES = {"scored", "undetermined", "unverified"}
VERIFICATION_RANGES = {
    "core_refuted": (Decimal("1.0"), Decimal("3.9")),
    "major_gap": (Decimal("4.0"), Decimal("5.9")),
    "supported": (Decimal("6.0"), Decimal("10.0")),
}
THRESHOLD = Decimal("0.4")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def nonempty(value, location):
    require(isinstance(value, str) and bool(value.strip()), location + " must be a nonempty string")
    return value


def number(value, location):
    require(type(value) in (int, float), location + " must be a JSON number")
    result = Decimal(str(value))
    require(result.is_finite(), location + " must be finite")
    require(Decimal("0") <= result <= Decimal("10"), location + " must be between 0 and 10")
    require(result == result.quantize(Decimal("0.1")), location + " must have at most one decimal place")
    return result


def rounded(value, places):
    if value is None:
        return None
    return float(value.quantize(Decimal(places), rounding=ROUND_HALF_UP))


def validate_observation(observation, dimension, location):
    require(isinstance(observation, dict), location + " must be an object")
    status = observation.get("status")
    require(status in STATUSES, location + " has an invalid status")
    nonempty(observation.get("rationale"), location + ".rationale")
    if status != "scored":
        require(observation.get("score") is None, location + ": unscored observations cannot contain a score")
        require(observation.get("tier") is None, location + ": unscored observations cannot contain a tier")
        return None

    score = number(observation.get("score"), location + ".score")
    if dimension == "innovation":
        if score == 0:
            require(observation.get("tier") is None, location + ": verified duplicates have no innovation tier")
            require(observation.get("duplicate_verified") is True, location + ": 0.0 requires duplicate_verified=true")
        else:
            require(score >= 1, location + ": innovation scores 0.1-0.9 are unused")
            tier = 3 if score < 4 else 2 if score < 8 else 1
            require(type(observation.get("tier")) is int and observation["tier"] == tier,
                    location + ": score and innovation tier disagree")
    else:
        require(score >= 1, location + ": this dimension uses 1.0-10.0")
        require(observation.get("tier") is None, location + ": only innovation has tiers")

    if dimension == "reliability":
        state = observation.get("verification_state")
        require(state in VERIFICATION_RANGES, location + ": scored reliability requires a verification_state")
        lower, upper = VERIFICATION_RANGES[state]
        require(lower <= score <= upper, location + ": reliability score violates the verification-state limit")
        nonempty(observation.get("verification_scope"), location + ".verification_scope")
    return score


def validate_batch(batch):
    require(isinstance(batch, dict), "batch must be an object")
    require(type(batch.get("schema_version")) is int and batch["schema_version"] == 1, "schema_version must be 1")
    for key in ("batch_id", "packet_id", "protocol_id"):
        nonempty(batch.get(key), key)
    planned = batch.get("planned_rounds")
    require(type(planned) is int and planned > 0, "planned_rounds must be a positive integer")
    protocol = batch.get("protocol")
    require(isinstance(protocol, dict), "protocol must be an object")
    for key in ("rubric_version", "model_id"):
        nonempty(protocol.get(key), "protocol." + key)
    require("model_snapshot" in protocol and
            (protocol["model_snapshot"] is None or
             isinstance(protocol["model_snapshot"], str) and bool(protocol["model_snapshot"].strip())),
            "protocol.model_snapshot must be a reported snapshot string or null")
    require(isinstance(protocol.get("settings"), dict), "protocol.settings must record actual controllable settings")
    require(protocol.get("execution_method") in {"isolated_agents", "independent_api_calls"},
            "protocol.execution_method must describe isolated independent executions")

    objects = batch.get("objects")
    require(isinstance(objects, list) and bool(objects), "objects must be a nonempty list")
    object_ids = set()
    overall_count = 0
    for item in objects:
        require(isinstance(item, dict), "each evaluation object must be an object")
        object_id = nonempty(item.get("id"), "object.id")
        require(object_id not in object_ids, "duplicate evaluation object id: " + object_id)
        object_ids.add(object_id)
        nonempty(item.get("label"), object_id + ".label")
        require(item.get("kind") in {"contribution", "overall"}, object_id + ": invalid kind")
        require(item.get("basis") in {"current", "conditional"}, object_id + ": invalid assessment basis")
        dimensions = item.get("dimensions")
        require(isinstance(dimensions, list) and bool(dimensions) and
                all(isinstance(d, str) and d in DIMENSIONS for d in dimensions),
                object_id + ": dimensions must list supported dimensions")
        require(len(dimensions) == len(set(dimensions)), object_id + ": duplicate dimension")
        if item["kind"] == "contribution":
            require(dimensions == ["innovation"], object_id + ": contributions are scored for innovation only")
        else:
            overall_count += 1
    require(overall_count == 1, "declare exactly one overall object per batch; use a separate batch for another scenario")

    rounds = batch.get("rounds")
    require(isinstance(rounds, list) and bool(rounds), "rounds must contain actual execution records")
    require(len(rounds) <= planned, "more executed rounds than planned_rounds")
    seen_rounds, seen_contexts = set(), set()
    validated = {}
    for round_record in rounds:
        require(isinstance(round_record, dict), "each round must be an object")
        round_id = nonempty(round_record.get("round_id"), "round.round_id")
        context_id = nonempty(round_record.get("context_id"), round_id + ".context_id")
        require(round_id not in seen_rounds, "duplicate round_id: " + round_id)
        require(context_id not in seen_contexts, "reused context_id: " + context_id)
        seen_rounds.add(round_id)
        seen_contexts.add(context_id)
        for key in ("packet_id", "protocol_id"):
            require(round_record.get(key) == batch[key], round_id + ": mixed " + key + "; start a separate batch")
        scores = round_record.get("scores")
        require(isinstance(scores, dict) and set(scores) == object_ids,
                round_id + ": scores must explicitly cover every declared object")
        for item in objects:
            object_id = item["id"]
            values = scores[object_id]
            require(isinstance(values, dict) and set(values) == set(item["dimensions"]),
                    round_id + "." + object_id + ": scores must explicitly cover every declared dimension")
            for dimension in item["dimensions"]:
                location = round_id + "." + object_id + "." + dimension
                validated[(round_id, object_id, dimension)] = validate_observation(
                    values[dimension], dimension, location)
    return validated


def summarize_batch(batch):
    validated = validate_batch(batch)
    rounds = batch["rounds"]
    executed = len(rounds)
    results, repeat_flags, review_flags = [], [], []
    for item in batch["objects"]:
        for dimension in item["dimensions"]:
            scores, tier_counts, states, unscored = [], Counter(), Counter(), []
            round_scores = []
            for round_record in rounds:
                round_id = round_record["round_id"]
                observation = round_record["scores"][item["id"]][dimension]
                score = validated[(round_id, item["id"], dimension)]
                round_scores.append({"round_id": round_id, "status": observation["status"],
                                     "score": None if score is None else float(score)})
                if score is None:
                    unscored.append({"round_id": round_id, "status": observation["status"],
                                     "rationale": observation["rationale"]})
                    continue
                scores.append(score)
                if dimension == "innovation":
                    tier_counts["verified_duplicate" if score == 0 else str(observation["tier"])] += 1
                if dimension == "reliability":
                    states[observation["verification_state"]] += 1

            n = len(scores)
            mean = sum(scores, Decimal(0)) / n if n else None
            variance = sum(((score - mean) ** 2 for score in scores), Decimal(0)) / (n - 1) if n > 1 else None
            stddev = variance.sqrt() if variance is not None else None
            consensus = "unscored" if not n else "partial_numeric_coverage" if unscored else "recorded_agreement"
            path = item["id"] + "." + dimension
            if unscored:
                review_flags.append(path + ": incomplete numeric coverage")
            if dimension == "innovation" and len(tier_counts) > 1:
                consensus = "tier_disagreement"
                repeat_flags.append(path + ": innovation tier or duplicate status disagreement")
            if dimension == "reliability" and len(states) > 1:
                consensus = "verification_state_disagreement"
                review_flags.append(path + ": verification states disagree; inspect evidence before judging reliability")
            if stddev is not None and stddev >= THRESHOLD:
                repeat_flags.append(path + ": standard deviation >= 0.4")
            results.append({
                "object_id": item["id"], "label": item["label"], "kind": item["kind"],
                "basis": item["basis"], "dimension": dimension, "scored_rounds": n,
                "executed_rounds": executed, "mean": rounded(mean, "0.1"),
                "sample_variance": rounded(variance, "0.001"),
                "standard_deviation": rounded(stddev, "0.01"),
                "minimum": float(min(scores)) if n else None,
                "maximum": float(max(scores)) if n else None,
                "tier_counts": dict(sorted(tier_counts.items())),
                "verification_state_counts": dict(sorted(states.items())),
                "consensus_status": consensus, "round_scores": round_scores,
                "unscored_rounds": unscored,
            })

    if executed < batch["planned_rounds"]:
        action, recommended = "complete_planned_rounds", batch["planned_rounds"]
    elif review_flags:
        action, recommended = "review_evidence", executed
    elif repeat_flags and executed < 10 and batch["planned_rounds"] >= 5:
        action, recommended = "check_disagreement_then_extend_to_ten", 10
    elif repeat_flags:
        action, recommended = "report_disagreement", executed
    else:
        action, recommended = "report_results", executed
    return {
        "schema_version": 1, "batch_id": batch["batch_id"], "packet_id": batch["packet_id"],
        "protocol_id": batch["protocol_id"], "protocol": batch["protocol"],
        "planned_rounds": batch["planned_rounds"], "executed_rounds": executed,
        "results": results,
        "recommendation": {"action": action, "recommended_total_rounds": recommended,
                           "repeat_flags": repeat_flags, "review_flags": review_flags},
        "interpretation": [
            "Statistics describe repeated recorded judgments; they do not measure true novelty or acceptance probability.",
            "Means never assign innovation tiers, replace reliability limits, or combine contributions or dimensions.",
            "Context identifiers are checked for uniqueness; execution authenticity requires the original tool or API logs.",
        ],
    }


def markdown_summary(summary):
    def cell(value):
        return str(value).replace("|", "&#124;").replace("\n", " ").replace("\r", " ")

    def fmt(value, digits):
        return "—" if value is None else format(value, "." + str(digits) + "f")

    states = {
        "unscored": "未评分", "partial_numeric_coverage": "部分轮次未赋分",
        "recorded_agreement": "层级／状态无分歧；见波动量",
        "tier_disagreement": "层级或重复状态有分歧",
        "verification_state_disagreement": "可靠性缺陷状态有分歧",
    }
    lines = [
        "# 独立重复评分统计",
        "",
        "批次：" + cell(summary["batch_id"]) + "。已执行 " + str(summary["executed_rounds"]) +
        " 轮，计划 " + str(summary["planned_rounds"]) + " 轮。",
        "",
        "| 对象／评价基础 | 维度 | 有效点分／已执行 | 均值 | 样本方差 | 标准差 | 范围 | 判断状态 |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for result in summary["results"]:
        basis = "当前贡献" if result["basis"] == "current" else "条件性情景"
        cells = [
            cell(result["label"]) + "／" + basis, DIMENSIONS[result["dimension"]],
            str(result["scored_rounds"]) + "/" + str(result["executed_rounds"]),
            fmt(result["mean"], 1), fmt(result["sample_variance"], 3),
            fmt(result["standard_deviation"], 2),
            "—" if result["minimum"] is None else fmt(result["minimum"], 1) + "–" + fmt(result["maximum"], 1),
            states[result["consensus_status"]],
        ]
        lines.append("| " + " | ".join(cells) + " |")
    lines.extend(["", "层级计数、缺陷状态计数、逐轮分数与未评分原因见对应 JSON 记录。",
                  "不足两个有效点分时不计算样本方差或标准差。缺失轮次不以零分替代。",
                  "", "后续动作：" + summary["recommendation"]["action"] +
                  "；建议总轮次：" + str(summary["recommendation"]["recommended_total_rounds"]) + "。", ""])
    for flag in summary["recommendation"]["repeat_flags"] + summary["recommendation"]["review_flags"]:
        lines.append("- " + cell(flag))
    lines.extend(["", "这些统计量描述当前固定材料和规则下的评分波动。均值不自动确定创新层级或可靠性结论。",
                  "独立调用是否实际发生须核对原始执行记录；本脚本只校验记录结构并计算统计量。", ""])
    return "\n".join(lines)


def reject_constant(value):
    raise ValueError("non-finite JSON constant: " + value)


def reject_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate JSON key: " + key)
        result[key] = value
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="recorded assessment-batch JSON")
    parser.add_argument("--output", type=Path, help="write summary JSON; otherwise print it")
    parser.add_argument("--markdown", type=Path, help="also write a Markdown summary")
    args = parser.parse_args()
    try:
        paths = [args.input.resolve()] + [path.resolve() for path in (args.output, args.markdown) if path]
        require(len(paths) == len(set(paths)), "input, JSON output, and Markdown output must be distinct files")
        batch = json.loads(args.input.read_text(encoding="utf-8-sig"),
                           parse_constant=reject_constant, object_pairs_hook=reject_duplicate_keys)
        summary = summarize_batch(batch)
        output = json.dumps(summary, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(output, encoding="utf-8")
        else:
            print(output, end="")
        if args.markdown:
            args.markdown.parent.mkdir(parents=True, exist_ok=True)
            args.markdown.write_text(markdown_summary(summary), encoding="utf-8")
    except (ValueError, OSError, TypeError, ArithmeticError) as error:
        print("Invalid assessment batch or output: " + str(error), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    sys.exit(main())
