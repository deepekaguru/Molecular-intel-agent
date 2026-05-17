from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import json
import os

load_dotenv()

def run(state):
    print("Agent 1 running — extracting genomic features...")

    from security.llm_wrapper import SecureLLMClient
    from security.action_control import ActionController
    import streamlit as st

    secure_llm = SecureLLMClient(model="gpt-4o-mini", temperature=0.3)
    action_controller = ActionController()

    # ── Fix: read from raw_profile where app.py stores it ──
    clinical_notes = (
        state.get('clinical_notes', '') or
        state.get('raw_profile', {}).get('notes', '')
    )

    state.setdefault('mutations', [])
    state.setdefault('cnvs', [])
    state.setdefault('fusions', [])

    if not clinical_notes or clinical_notes.strip() == '':
        print("No clinical notes — using form-selected mutations only")
        action_controller.log_action(
            action_type="llm_feature_extraction",
            status="SKIPPED",
            details={"reason": "No clinical notes provided"}
        )
        return state

    prompt = f"""
Extract genomic features from these clinical notes:

{clinical_notes}

Return ONLY a JSON object (no markdown, no backticks) with these keys:
{{
    "mutations": ["gene1", "gene2"],
    "cnvs": ["amplification1", "deletion1"],
    "fusions": ["fusion1", "fusion2"]
}}

If none found for a category, use empty array [].
"""

    # ── Step 1 already done: user gave consent in app.py ──
    # ── Step 2: Log this LLM call as authorized ──
    action_details = {
        "purpose": "Extract genomic features from clinical notes",
        "input_length": f"{len(clinical_notes)} characters",
        "mutations_already_selected": len(state.get('mutations', [])),
        "estimated_api_cost": "$0.01 - $0.03 per call",
        "data_destination": "OpenAI API (external service)",
        "model": "gpt-4o-mini",
        "temperature": 0.3,
        "note_preview": clinical_notes[:100] + "..." if len(clinical_notes) > 100 else clinical_notes
    }

    # Show Step 2 verification in UI
    st.info("🔒 **Security Layer 2** — PII masking applied before LLM call. "
            "Clinical notes sanitized and sent to OpenAI for feature extraction.")

    action_controller.log_action(
        action_type="llm_feature_extraction",
        status="AUTHORIZED",
        details=action_details
    )

    print("✅ Proceeding with feature extraction...")

    result = secure_llm.chat_completion(
        prompt=prompt,
        system_message="You are a genomic data extraction assistant. Return only valid JSON.",
        user_role='all'
    )

    if result['success']:
        try:
            response_text = result['response'].strip()

            if response_text.startswith('```'):
                response_text = response_text.split('```')[1]
                if response_text.startswith('json'):
                    response_text = response_text[4:]
                response_text = response_text.strip()

            extracted = json.loads(response_text)

            existing_mutations = set(state.get('mutations', []))
            new_mutations = set(extracted.get('mutations', []))
            state['mutations'] = list(existing_mutations | new_mutations)

            state.setdefault('cnvs', [])
            state['cnvs'].extend(extracted.get('cnvs', []))

            state.setdefault('fusions', [])
            state['fusions'].extend(extracted.get('fusions', []))

            print(f"✅ Extracted: {len(state['mutations'])} mutations, "
                  f"{len(state['cnvs'])} CNVs, {len(state['fusions'])} fusions")

            action_controller.log_action(
                action_type="llm_feature_extraction",
                status="SUCCESS",
                details={
                    "mutations_extracted": len(new_mutations),
                    "total_mutations": len(state['mutations'])
                }
            )

        except json.JSONDecodeError as e:
            print(f"⚠️ JSON parsing error: {e}")
            action_controller.log_action(
                action_type="llm_feature_extraction",
                status="FAILED",
                details={"error": f"JSON parsing error: {str(e)}"}
            )

    else:
        print(f"❌ LLM extraction failed: {result.get('error')}")
        action_controller.log_action(
            action_type="llm_feature_extraction",
            status="FAILED",
            details={"error": result.get('error', 'Unknown error')}
        )

    return state
