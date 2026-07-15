import sys
import unittest
from pathlib import Path


WEB_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(WEB_ROOT))

import candidate_proposal


class CandidateProposalPromptTests(unittest.TestCase):
    def test_v3_prompt_is_compact_source_neutral_and_extracts_action_and_aspiration(self):
        prompt = candidate_proposal.load_prompt()

        self.assertEqual(candidate_proposal.PROMPT_VERSION, "threadline-candidate-proposal-v3")
        self.assertLessEqual(len(prompt), 1800)
        for required in (
            "SOURCE_KIND",
            "knowledge_vault",
            "slack",
            "misskey",
            "chat",
            '"proposal_type": "action"',
            '"proposal_type": "aspiration"',
            "なんとなくやりたい",
            "具体的な作業へ捏造",
            "aspirationは[]",
            "evidence_quotes",
            "pending",
        ):
            self.assertIn(required, prompt)

    def test_request_carries_source_identity_without_mixing_it_into_evidence(self):
        request = candidate_proposal.build_request(
            source_kind="slack",
            source_ref="slack://memo-ideas/123",
            source_body="いつか自宅の本を検索できるようにしたい。",
            allowed_tags=["idea", "slack"],
        )

        self.assertIn("SOURCE_KIND: slack", request["user_prompt"])
        self.assertIn("SOURCE_REF: slack://memo-ideas/123", request["user_prompt"])
        self.assertEqual(request["source_body"], "いつか自宅の本を検索できるようにしたい。")


class CandidateProposalValidationTests(unittest.TestCase):
    def test_explicit_action_is_accepted_as_todo(self):
        source = "監査APIの同期結果を確認し、失敗runを再実行する。"
        result = candidate_proposal.normalize_output(
            {
                "document_summary": "監査APIの同期再実行が必要。",
                "candidate_proposals": [{
                    "proposal_type": "action",
                    "title": "監査APIの失敗runを再実行する",
                    "summary": "同期結果を確認して失敗runを再実行する。",
                    "todo": "監査APIの同期結果を確認し、失敗runを再実行する",
                    "kind": "todo",
                    "schedule": "候補なし",
                    "confidence": "high",
                    "missing": [],
                    "tags": [],
                    "evidence_quotes": [source],
                }],
            },
            source,
            allowed_tags=[],
            source_kind="slack",
            source_ref="slack://memo-ideas/1",
        )

        proposal = result["proposals"][0]
        self.assertEqual(proposal["validation"]["status"], "accepted")
        self.assertEqual(proposal["proposal_type"], "action")
        self.assertEqual(proposal["kind"], "todo")

    def test_vague_personal_wish_is_accepted_as_idea_without_concretization(self):
        source = "なんとなく、いつか自宅の本を横断検索できるようにしたい。"
        result = candidate_proposal.normalize_output(
            {
                "document_summary": "自宅の本を横断検索したいという希望。",
                "candidate_proposals": [{
                    "proposal_type": "aspiration",
                    "title": "自宅の本を横断検索したい",
                    "summary": "自宅の本を横断検索できるようにしたい。",
                    "todo": source,
                    "kind": "idea",
                    "schedule": "候補なし",
                    "confidence": "medium",
                    "missing": [],
                    "tags": [],
                    "evidence_quotes": [source],
                }],
            },
            source,
            allowed_tags=[],
            source_kind="misskey",
            source_ref="misskey://note/1",
        )

        proposal = result["proposals"][0]
        self.assertEqual(proposal["validation"]["status"], "accepted")
        self.assertEqual(proposal["proposal_type"], "aspiration")
        self.assertEqual(proposal["kind"], "idea")
        self.assertEqual(proposal["todo"], source)

    def test_aspiration_is_held_when_llm_invents_a_concrete_commitment(self):
        source = "ローカルLLMで写真を整理できたらいいな。"
        result = candidate_proposal.normalize_output(
            {
                "document_summary": "写真整理への希望。",
                "candidate_proposals": [{
                    "proposal_type": "aspiration",
                    "title": "写真整理を自動化したい",
                    "summary": "ローカルLLMで写真を整理したい。",
                    "todo": "今週中にPythonで写真分類workerを実装する",
                    "kind": "idea",
                    "schedule": "候補なし",
                    "confidence": "high",
                    "missing": [],
                    "tags": [],
                    "evidence_quotes": [source],
                }],
            },
            source,
            allowed_tags=[],
            source_kind="chat",
            source_ref="chat://thread/default/message/1",
        )

        proposal = result["proposals"][0]
        self.assertEqual(proposal["validation"]["status"], "held")
        self.assertIn("aspiration todo must preserve an exact source wish", proposal["validation"]["reasons"])

    def test_action_wins_when_same_evidence_is_duplicated_as_aspiration(self):
        source = "Slack取込をAI候補判定へ切り替える。"
        common = {
            "title": "Slack取込をAI候補判定へ切り替える",
            "summary": "Slack取込を共通AI判定へ切り替える。",
            "todo": source,
            "schedule": "候補なし",
            "confidence": "high",
            "missing": [],
            "tags": [],
            "evidence_quotes": [source],
        }
        result = candidate_proposal.normalize_output(
            {
                "document_summary": "Slack取込の変更。",
                "candidate_proposals": [
                    {**common, "proposal_type": "aspiration", "kind": "idea"},
                    {**common, "proposal_type": "action", "kind": "todo"},
                ],
            },
            source,
            allowed_tags=[],
            source_kind="knowledge_vault",
            source_ref="records/slack.md",
        )

        self.assertEqual(len(result["proposals"]), 1)
        self.assertEqual(result["proposals"][0]["proposal_type"], "action")


if __name__ == "__main__":
    unittest.main()
