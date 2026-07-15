import json
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WEB_ROOT = ROOT / "apps" / "web"
SYNC_ROOT = ROOT / "workers" / "sync"
sys.path[:0] = [str(WEB_ROOT), str(SYNC_ROOT)]

import db_tool
import candidate_proposal
from http_client import HttpClient, HttpClientError
from llm_client import CandidateProposalLlm
from slack_collector import SlackCollector
from misskey_collector import MisskeyCollector
from proposal_pipeline import ProposalPipeline


class ScriptedTransport:
    """No-network HTTP fake that records requests without exposing credentials."""

    def __init__(self, responses):
        self.responses = list(responses)
        self.requests = []

    def request(self, method, url, headers=None, json_body=None, timeout=None):
        self.requests.append({"method": method, "url": url, "headers": headers or {}, "json": json_body})
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response


class FakeLlm:
    def __init__(self, outputs):
        self.outputs = list(outputs)
        self.requests = []

    def propose(self, **request):
        self.requests.append(request)
        output = self.outputs.pop(0)
        if isinstance(output, Exception):
            raise output
        return output


def action_output(source):
    return {
        "document_summary": "同期の確認が必要。",
        "candidate_proposals": [{
            "proposal_type": "action",
            "title": "同期結果を確認する",
            "summary": "同期結果を確認する。",
            "todo": source,
            "kind": "todo",
            "schedule": "候補なし",
            "confidence": "high",
            "missing": [],
            "tags": [],
            "evidence_quotes": [source],
        }],
    }


class ExternalIntakeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="pj-general-external-intake-")
        self.database = Path(self.temp.name) / "p0.sqlite"
        self.connection = sqlite3.connect(self.database)
        self.connection.row_factory = sqlite3.Row
        db_tool.execute_schema(self.connection)
        db_tool.seed(self.connection)
        self.connection.commit()

    def tearDown(self):
        self.connection.close()
        self.temp.cleanup()

    def test_http_client_retries_a_single_429_and_sanitizes_failure(self):
        transport = ScriptedTransport([
            {"status": 429, "headers": {"Retry-After": "2"}, "json": {"error": "ratelimited"}},
            {"status": 200, "headers": {}, "json": {"ok": True}},
        ])
        waits = []
        client = HttpClient(transport=transport, sleep=waits.append)

        self.assertEqual(client.get_json("https://example.test/history", headers={"Authorization": "Bearer top-secret"}), {"ok": True})
        self.assertEqual(waits, [2])
        self.assertEqual(len(transport.requests), 2)

        failing = HttpClient(transport=ScriptedTransport([
            {"status": 500, "headers": {}, "json": {}},
            {"status": 500, "headers": {}, "json": {}},
            {"status": 500, "headers": {}, "json": {}},
        ]), sleep=lambda _: None)
        with self.assertRaises(HttpClientError) as raised:
            failing.get_json("https://example.test/history", headers={"Authorization": "Bearer top-secret"})
        self.assertEqual(str(raised.exception), "http_5xx")
        self.assertNotIn("top-secret", str(raised.exception))

    def test_slack_collector_paginates_and_keeps_only_owner_root_messages(self):
        transport = ScriptedTransport([
            {"status": 200, "headers": {}, "json": {
                "ok": True,
                "messages": [
                    {"ts": "101.0", "user": "owner", "text": "同期結果を確認する"},
                    {"ts": "102.0", "user": "other", "text": "他人の発言"},
                    {"ts": "103.0", "user": "owner", "text": "thread", "thread_ts": "100.0"},
                    {"ts": "104.0", "user": "owner", "text": "bot", "subtype": "bot_message"},
                ],
                "response_metadata": {"next_cursor": "next-page"},
            }},
            {"status": 200, "headers": {}, "json": {
                "ok": True,
                "messages": [{"ts": "105.0", "user": "owner", "text": "次の確認をする"}],
                "response_metadata": {"next_cursor": ""},
            }},
        ])
        collector = SlackCollector(
            HttpClient(transport=transport, sleep=lambda _: None),
            channel_id="C0BG4TCPAUD",
            owner_user_id="owner",
            bot_token="top-secret",
            initial_oldest_ts="100.0",
            api_base_url="https://slack.fake/api",
        )

        result = collector.collect(cursor_after=None)

        self.assertEqual([event["sourceRef"] for event in result.events], ["C0BG4TCPAUD:101.0", "C0BG4TCPAUD:105.0"])
        self.assertEqual(result.cursor_after, "105.0")
        self.assertEqual(result.skipped, 3)
        self.assertIn("oldest=100.0", transport.requests[0]["url"])
        self.assertIn("cursor=next-page", transport.requests[1]["url"])

    def test_llm_client_uses_the_shared_v2_prompt_and_returns_only_json(self):
        source = "同期結果を確認する"
        transport = ScriptedTransport([{
            "status": 200,
            "headers": {},
            "json": {"choices": [{"message": {"content": json.dumps(action_output(source), ensure_ascii=False)}}]},
        }])
        client = CandidateProposalLlm(
            HttpClient(transport=transport, sleep=lambda _: None),
            base_url="https://llm.fake",
            model="fake-model",
            api_key="top-secret",
        )

        self.assertEqual(
            client.propose("slack", "C:1", source, []),
            action_output(source),
        )
        request = transport.requests[0]
        self.assertEqual(request["url"], "https://llm.fake/v1/chat/completions")
        self.assertEqual(request["json"]["messages"][0]["content"], candidate_proposal.load_prompt())
        self.assertIn("SOURCE_BODY:\n同期結果を確認する", request["json"]["messages"][1]["content"])

    def test_misskey_collector_fetches_pages_and_normalizes_cw_before_text(self):
        first_page = [{"id": f"n{index:03d}", "createdAt": "2026-07-15T00:00:00Z", "text": "同期結果を確認する"} for index in range(100, 0, -1)]
        first_page[0] = {"id": "new", "createdAt": "2026-07-15T00:00:00Z", "cw": "要確認", "text": "同期結果を確認する"}
        first_page[1] = {"id": "renote", "renoteId": "original", "text": "除外"}
        first_page[2] = {"id": "empty", "text": "", "cw": ""}
        transport = ScriptedTransport([
            {"status": 200, "headers": {}, "json": first_page},
            {"status": 200, "headers": {}, "json": []},
        ])
        collector = MisskeyCollector(
            HttpClient(transport=transport, sleep=lambda _: None),
            base_url="https://misskey.fake",
            owner_user_id="owner",
            access_token="top-secret",
        )

        result = collector.collect(cursor_after="old")

        self.assertEqual(result.cursor_after, "new")
        self.assertEqual(result.events[0]["sourceBody"], "要確認\n同期結果を確認する")
        self.assertNotIn("renote", [event["sourceRef"] for event in result.events])
        self.assertEqual(transport.requests[0]["json"]["sinceId"], "old")
        self.assertIn("untilId", transport.requests[1]["json"])
        self.assertEqual(transport.requests[0]["json"]["i"], "top-secret")

    def test_pipeline_commits_accepted_and_held_results_without_auto_go(self):
        accepted = "同期結果を確認する"
        aspiration = "いつか自宅の本を横断検索できるようにしたい。"
        collector_result = type("Collected", (), {
            "events": [
                {"sourceRef": "C:1", "sourceBody": accepted, "occurred": "2026-07-15"},
                {"sourceRef": "C:2", "sourceBody": aspiration, "occurred": "2026-07-15"},
            ],
            "cursor_after": "2",
            "scanned": 2,
            "skipped": 0,
        })()
        aspiration_output = action_output(aspiration)
        aspiration_output["candidate_proposals"][0].update({"proposal_type": "aspiration", "kind": "idea", "todo": aspiration})
        pipeline = ProposalPipeline(FakeLlm([action_output(accepted), aspiration_output]))

        result = pipeline.process(self.connection, "slack", "memo-ideas", collector_result, cursor_before="0", commit=True)

        self.assertEqual(result["state"], "succeeded")
        self.assertEqual(result["created"], 2)
        self.assertEqual(self.connection.execute("select count(*) from candidates where status = 'pending'").fetchone()[0], 2)
        self.assertEqual(self.connection.execute("select count(*) from execution_links").fetchone()[0], 0)

    def test_pipeline_keeps_cursor_when_fake_llm_fails_after_a_partial_commit(self):
        first = "同期結果を確認する"
        second = "次の同期を確認する"
        collector_result = type("Collected", (), {
            "events": [
                {"sourceRef": "C:1", "sourceBody": first, "occurred": "2026-07-15"},
                {"sourceRef": "C:2", "sourceBody": second, "occurred": "2026-07-15"},
            ],
            "cursor_after": "2",
            "scanned": 2,
            "skipped": 0,
        })()
        pipeline = ProposalPipeline(FakeLlm([action_output(first), TimeoutError("top-secret source body")]))

        result = pipeline.process(self.connection, "slack", "memo-ideas", collector_result, cursor_before="0", commit=True)

        self.assertEqual(result["state"], "partial")
        self.assertEqual(result["cursorAfter"], "0")
        self.assertEqual(result["created"], 1)
        run = self.connection.execute("select state, cursor_after, error from source_sync_runs where source = 'slack' order by id desc").fetchone()
        self.assertEqual((run["state"], run["cursor_after"], run["error"]), ("partial", "0", "llm_error"))
        self.assertNotIn("top-secret", run["error"])

    def test_dry_run_leaves_temporary_database_unchanged_and_hides_source_text(self):
        source = "機密本文: top-secret を含む同期確認"
        collector_result = type("Collected", (), {
            "events": [{"sourceRef": "C:1", "sourceBody": source, "occurred": "2026-07-15"}],
            "cursor_after": "1",
            "scanned": 1,
            "skipped": 0,
        })()
        before = self.database.read_bytes()
        pipeline = ProposalPipeline(FakeLlm([action_output(source)]))

        result = pipeline.process(self.connection, "slack", "memo-ideas", collector_result, cursor_before=None, commit=False)

        self.assertEqual(result["state"], "succeeded")
        self.assertEqual(result["created"], 1)
        self.connection.commit()
        self.assertEqual(self.database.read_bytes(), before)
        self.assertNotIn(source, str(result))
        self.assertNotIn("top-secret", str(result))


if __name__ == "__main__":
    unittest.main()
