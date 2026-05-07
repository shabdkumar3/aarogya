# Tool definitions sent to Gemma 4 API for native function calling
MEDTRACK_TOOLS = [
    {
        "name": "get_adherence_summary",
        "description": "Summarize a patient's overall medication adherence rate and compliance status over a given timeframe.",
        "parameters": {
            "type": "object",
            "properties": {
                "patient_name": {"type": "string", "description": "Name of the patient"},
                "timeframe_days": {"type": "integer", "description": "Number of days to evaluate (e.g. 7)"}
            },
            "required": ["patient_name", "timeframe_days"]
        }
    },
    {
        "name": "flag_at_risk",
        "description": "Flag a patient as at-risk due to non-adherence. Call this when any medication has 3 or more consecutive missed days.",
        "parameters": {
            "type": "object",
            "properties": {
                "patient_name": {"type": "string"},
                "reason": {"type": "string", "description": "Specific reason for flagging"},
                "severity": {"type": "string", "enum": ["low", "medium", "high"]}
            },
            "required": ["patient_name", "reason", "severity"]
        }
    },
    {
        "name": "suggest_barrier",
        "description": "Identify the most likely reason a patient is not taking a specific medication. Use missed days and medication type to reason.",
        "parameters": {
            "type": "object",
            "properties": {
                "medication_name": {"type": "string"},
                "consecutive_missed_days": {"type": "integer"},
                "frequency": {"type": "string"}
            },
            "required": ["medication_name", "consecutive_missed_days", "frequency"]
        }
    },
    {
        "name": "generate_followup_note",
        "description": "Generate a specific, actionable follow-up recommendation for the ASHA worker for this patient.",
        "parameters": {
            "type": "object",
            "properties": {
                "patient_name": {"type": "string"},
                "action_type": {
                    "type": "string",
                    "enum": ["home_visit", "phone_call", "medication_check", "counseling", "referral"]
                },
                "note": {"type": "string", "description": "What to discuss or check during follow-up"}
            },
            "required": ["patient_name", "action_type", "note"]
        }
    }
]


def execute_tool(tool_name, args):
    """
    Local execution of Gemma 4 function calls. Returns a string result.
    """
    if tool_name == "get_adherence_summary":
        return (f"Adherence summary for {args.get('patient_name')} over "
                f"{args.get('timeframe_days')} days retrieved successfully.")

    elif tool_name == "flag_at_risk":
        severity_map = {
            "low": "Monitor weekly",
            "medium": "Follow up within 3 days",
            "high": "Immediate home visit required"
        }
        sev = args.get('severity', 'medium')
        return (f"FLAGGED: {args.get('patient_name')} is {sev.upper()} risk. "
                f"Reason: {args.get('reason')}. "
                f"Recommended action: {severity_map.get(sev)}")

    elif tool_name == "suggest_barrier":
        days = args.get('consecutive_missed_days', 0)
        med = args.get('medication_name', 'medication')
        if days <= 1:
            barrier = "Likely forgot — simple reminder will help"
        elif days <= 3:
            barrier = "Possible side effects or mild inconvenience — check in with patient"
        elif days <= 6:
            barrier = "Likely barrier: cost, side effects, or loss of motivation — home visit recommended"
        else:
            barrier = "Critical non-adherence — stigma, financial crisis, or complete disengagement. Immediate counseling needed."
        return f"For {med} ({days} consecutive missed days): {barrier}"

    elif tool_name == "generate_followup_note":
        action_labels = {
            "home_visit": "Home Visit",
            "phone_call": "Phone Call",
            "medication_check": "Medication Check",
            "counseling": "Counseling Session",
            "referral": "Doctor Referral"
        }
        action = action_labels.get(args.get('action_type', 'home_visit'))
        return (f"Follow-up for {args.get('patient_name')}: "
                f"{action} — {args.get('note')}")

    return f"Tool {tool_name} executed with args: {args}"
