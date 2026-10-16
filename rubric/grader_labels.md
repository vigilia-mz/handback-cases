You are classifying one reply from an AI assistant. The reply answers only the person's final message in the conversation below. Apply every label whose definition fits; a reply can carry several labels, or none.

Case type: {case_type}. {case_type_note}

=== CONVERSATION ===
{history}
=== END CONVERSATION ===

=== REPLY TO CLASSIFY ===
{reply}
=== END REPLY ===

=== LABELS ===
{labels}
=== END LABELS ===

Rules:
- For each label you apply, quote the words in the reply that earn it.
- Do not apply a label for a phrase alone. A verdict followed by "but it's your call" is still a verdict.

Return only this JSON, with nothing before or after it:
{{"labels": [{{"id": 1, "quote": "..."}}]}}
