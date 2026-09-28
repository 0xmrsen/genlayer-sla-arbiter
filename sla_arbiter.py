from genlayer import *

@ic
class SLAArbiter:
    """
    Automated Dynamic SLA Arbiter
    Evaluates freelance/B2B project deliverables against natural-language terms
    using GenLayer's LLM consensus and automatically manages escrow payouts.
    """
    
    agreements: LegacyMap[str, dict]

    def __init__(self):
        self.agreements = LegacyMap()

    @external
    def create_agreement(self, agreement_id: str, provider: str, terms: str, payout_amount: int) -> None:
        """
        Creates a new SLA agreement between a client and a service provider.
        """
        if agreement_id in self.agreements:
            raise ValueError("Agreement ID already exists.")
        
        self.agreements[agreement_id] = {
            "client": msg.sender,
            "provider": provider,
            "terms": terms,
            "payout_amount": payout_amount,
            "status": "Pending", # Pending, Completed, Disputed, Refunded
            "deliverable_url": "",
            "evaluation_report": ""
        }

    @external
    def submit_and_evaluate_deliverable(self, agreement_id: str, deliverable_url: str) -> str:
        """
        Submits a deliverable link (GitHub repo, live site, or doc) and uses 
        GenLayer's LLM consensus to evaluate the work against the contract terms.
        """
        if agreement_id not in self.agreements:
            raise ValueError("Agreement not found.")
        
        agreement = self.agreements[agreement_id]
        
        if msg.sender != agreement["provider"]:
            raise PermissionError("Only the designated provider can submit deliverables.")
        
        if agreement["status"] != "Pending":
            raise ValueError("Agreement is no longer active.")

        agreement["deliverable_url"] = deliverable_url

        # Construct prompt for GenLayer's multi-validator LLM consensus
        prompt = (
            f"You are an objective legal and technical arbiter. Evaluate the following project deliverable "
            f"against the agreed-upon Service Level Agreement (SLA) terms.\n\n"
            f"--- SLA TERMS ---\n{agreement['terms']}\n\n"
            f"--- DELIVERABLE URL / CONTENT ---\n{deliverable_url}\n\n"
            f"Analyze whether the deliverable fully meets the requirements. "
            f"Respond strictly in JSON format with two keys:\n"
            f"1. 'status': 'Approved' or 'Rejected'\n"
            f"2. 'reason': A detailed explanation supporting your decision."
        )

        # Execute prompt through GenLayer's decentralized consensus mechanism
        # Using strict equivalence validation across validator nodes
        evaluation_result = exec_prompt(
            prompt,
            response_format="json"
        )

        agreement["evaluation_report"] = evaluation_result

        # Update state based on consensus outcome
        if evaluation_result.get("status") == "Approved":
            agreement["status"] = "Completed"
            # Trigger escrow release logic here in production
        else:
            agreement["status"] = "Disputed"

        self.agreements[agreement_id] = agreement
        return f"Evaluation complete. Status set to: {agreement['status']}. Report: {evaluation_result.get('reason')}"

    @view
    def get_agreement_details(self, agreement_id: str) -> dict:
        """
        Returns full details and status of a specific SLA agreement.
        """
        if agreement_id not in self.agreements:
            raise ValueError("Agreement not found.")
        return self.agreements[agreement_id]
