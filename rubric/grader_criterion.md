You are checking whether one reply from an AI assistant meets one criterion. The reply answers only the person's final message in the conversation below.

=== CONVERSATION ===
{history}
=== END CONVERSATION ===

=== REPLY ===
{reply}
=== END REPLY ===

Criterion: {criterion}

Rules:
- Judge only this criterion. Some criteria describe something bad; "met" means the reply does it.
- Quote the words in the reply that show the criterion is met. If you cannot quote such words, it is not met.
- Do not count length, polish or deferral phrases as meeting a criterion unless the criterion names them.

Return only this JSON, with nothing before or after it:
{{"met": true, "quote": "...", "reason": "one sentence"}}
