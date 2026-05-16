# GNU Head
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

load_dotenv()

def run(state):
    print("Agent 5 running — generating clinical rationale...")
    
    # Initialize secure LLM wrapper INSIDE the function
    from security.llm_wrapper import SecureLLMClient
    secure_llm = SecureLLMClient(model="gpt-4o-mini", temperature=0.3)
    
    treatments = state['ranked_treatments'][:3]
    evidence = state['rag_evidence']
    mutations = state['mutations']
    
    prompt = f"""
You are a clinical oncology AI assistant.

Patient mutations: {mutations}

Top ranked treatments:
{treatments}

Supporting literature evidence:
{evidence}

For each treatment, write exactly 2 sentences of
clinical rationale explaining why it is recommended
for this patient based on their mutations and the evidence.

Format your response as:
1. [Drug name]: [2 sentence rationale]
2. [Drug name]: [2 sentence rationale]
3. [Drug name]: [2 sentence rationale]
"""

    # ========== LEVEL 2 CONFIRMATION: USER AUTHORIZATION REQUIRED ==========
    # Import action controller

    
    # ========== END OF LEVEL 2 CONFIRMATION SECTION ==========
    
    # User authorized - proceed with LLM call
    print("✅ User authorized LLM call - proceeding with rationale generation...")
    
    # Use secure LLM wrapper with guardrails
    result = secure_llm.chat_completion(
        prompt=prompt,
        system_message="You are a clinical oncology AI assistant.",
        user_role='all'
    )
    
    if result['success']:
        state['rationale'] = result['response']
        
        # Log successful execution
        action_controller.log_action(
            action_type="llm_rationale_generation",
            status="SUCCESS",
            details={"response_length": len(result['response'])}
        )
        
        # Log any warnings from guardrails
        if result.get('warnings'):
            print(f"⚠️ LLM Warnings: {result['warnings']}")
    else:
        # Fallback if LLM fails
        state['rationale'] = "Unable to generate rationale at this time. Please try again."
        print(f"❌ LLM Error: {result.get('error', 'Unknown error')}")
        
        # Log the failure
        action_controller.log_action(
            action_type="llm_rationale_generation",
            status="FAILED",
            details={"error": result.get('error', 'Unknown error')}
        )
    
    return state
