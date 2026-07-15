"""Apply the shared v2 proposal contract, never a source-specific fallback."""

from __future__ import annotations

import candidate_proposal
import source_sync


class ProposalPipeline:
    def __init__(self, llm):
        self.llm = llm

    @staticmethod
    def _allowed_tags(connection):
        return [row[0] for row in connection.execute("select name from tags where visible = 1 order by name").fetchall()]

    def process(self, connection, source, source_label, collected, cursor_before, commit):
        allowed_tags = self._allowed_tags(connection)
        items = []
        held = 0
        accepted = 0
        state = "succeeded"
        for event in collected.events:
            try:
                output = self.llm.propose(
                    source_kind=source,
                    source_ref=event["sourceRef"],
                    source_body=event["sourceBody"],
                    allowed_tags=allowed_tags,
                )
            except Exception:
                state = "partial"
                break
            normalized = candidate_proposal.normalize_output(
                output,
                event["sourceBody"],
                allowed_tags=allowed_tags,
                source_kind=source,
                source_ref=event["sourceRef"],
            )
            accepted += sum(item["validation"]["status"] == "accepted" for item in normalized["proposals"])
            held += sum(item["validation"]["status"] != "accepted" for item in normalized["proposals"])
            items.append({**event, "output": output})
        cursor_after = collected.cursor_after if state == "succeeded" else cursor_before
        if not commit:
            return {
                "state": state,
                "created": accepted,
                "held": held,
                "skipped": collected.skipped,
                "scanned": collected.scanned,
                "cursorBefore": cursor_before,
                "cursorAfter": cursor_after,
            }
        result = source_sync.import_source_proposals(connection, {
            "source": source,
            "sourceLabel": source_label,
            "allowedTags": allowed_tags,
            "items": items,
            "cursor": cursor_before,
            "cursor_after": cursor_after,
            "state": state,
            "error": "llm_error" if state == "partial" else None,
            "scanned": collected.scanned,
            "collector_skipped": collected.skipped,
        })
        return {
            "state": state,
            "created": result["imported"],
            "held": result["held"],
            "skipped": result["skipped"],
            "scanned": collected.scanned,
            "cursorBefore": cursor_before,
            "cursorAfter": cursor_after,
        }
