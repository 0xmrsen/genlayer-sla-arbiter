# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

from genlayer import *
import json


class SLAArbiter(gl.Contract):
    """
    Automated Dynamic SLA Arbiter.

    Creates SLA agreements and uses GenLayer's LLM consensus
    to evaluate submitted deliverables.
    """

    agreements: str

    def __init__(self):
        self.agreements = "{}"

    @gl.public.write
    def create_agreement(
        self,
        agreement_id: str,
        provider: str,
        terms: str,
        payout_amount: int
    ) -> None:

        data = json.loads(self.agreements)

        if agreement_id in data:
            raise ValueError("Agreement ID already exists.")

        data[agreement_id] = {
            "client": str(gl.message.sender_address),
            "provider": provider,
            "terms": terms,
            "payout": payout_amount,
            "status": "Pending",
            "url": "",
            "report": ""
        }

        self.agreements = json.dumps(data, sort_keys=True)

    @gl.public.write
    def submit_and_evaluate_deliverable(
        self,
        agreement_id: str,
        deliverable_url: str
    ) -> str:

        data = json.loads(self.agreements)

        if agreement_id not in data:
            raise ValueError("Agreement not found.")

        agreement_info = data[agreement_id]

        prompt = (
            "You are an objective legal and technical SLA arbiter.\n\n"

            "Evaluate the following project deliverable "
            "against the agreed SLA terms.\n\n"

            "--- AGREEMENT DATA ---\n"
            f"{json.dumps(agreement_info)}\n\n"

            "--- DELIVERABLE URL ---\n"
            f"{deliverable_url}\n\n"

            "Determine whether the deliverable fully meets "
            "the requirements.\n\n"

            "Return JSON with exactly these keys:\n"
            "{"
            "\"status\": \"Approved\" or \"Rejected\", "
            "\"reason\": \"detailed explanation\""
            "}"
        )

        def leader_fn():
            result = gl.nondet.exec_prompt(
                prompt,
                response_format="json"
            )

            if not isinstance(result, dict):
                raise ValueError("LLM returned invalid JSON object.")

            status = result.get("status")

            if status not in ("Approved", "Rejected"):
                raise ValueError("Invalid status returned by LLM.")

            reason = result.get("reason")

            if not isinstance(reason, str):
                raise ValueError("Invalid reason returned by LLM.")

            return {
                "status": status,
                "reason": reason
            }

        def validator_fn(leader_result):

            if not isinstance(leader_result, gl.vm.Return):
                return False

            result = leader_result.calldata

            if not isinstance(result, dict):
                return False

            status = result.get("status")
            reason = result.get("reason")

            if status not in ("Approved", "Rejected"):
                return False

            if not isinstance(reason, str):
                return False

            if len(reason.strip()) == 0:
                return False

            return True

        evaluation_result = gl.vm.run_nondet_unsafe(
            leader_fn,
            validator_fn
        )

        status_val = evaluation_result["status"]
        reason_val = evaluation_result["reason"]

        if status_val == "Approved":
            agreement_info["status"] = "Completed"
        else:
            agreement_info["status"] = "Disputed"

        agreement_info["url"] = deliverable_url
        agreement_info["report"] = reason_val

        data[agreement_id] = agreement_info

        self.agreements = json.dumps(
            data,
            sort_keys=True
        )

        return (
            f"Evaluation complete. "
            f"Status: {agreement_info['status']}. "
            f"Report: {reason_val}"
        )

    @gl.public.view
    def get_agreement_details(
        self,
        agreement_id: str
    ) -> str:

        data = json.loads(self.agreements)

        if agreement_id not in data:
            raise ValueError("Agreement not found.")

        return json.dumps(
            data[agreement_id],
            sort_keys=True
        )
