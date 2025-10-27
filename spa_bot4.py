"""
Spa Bot Flask Application - Corrected Flow Engine Integration
=============================================================
Uses the actual methods from ConversationFlowEngine
"""

from flask import render_template_string, redirect
from flask import Flask, request, jsonify, session
from flask_cors import CORS
from flask import request
from dotenv import load_dotenv
from datetime import datetime
import openai
import os
import logging
import json
import re
from typing import Dict, Any, Optional, List

# Load environment variables
load_dotenv()
print(f"Loaded API Key: {'Yes' if os.getenv('OPENAI_API_KEY') else 'No'}")
openai.api_key = os.getenv("OPENAI_API_KEY")
print(f"API Key Loaded: {openai.api_key[:10]}..." if openai.api_key else "NO API KEY FOUND!")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.getenv("SESSION_SECRET", "spa-bot-secret-2025")

# ---------- Simple same-origin tester UI ----------
TESTER_HTML = r"""
<!doctype html>
<html>
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1"/>
  <title>Spa Bot Tester</title>
  <style>
    body{font-family:system-ui,Segoe UI,Arial,sans-serif;background:#f6f7fb;margin:0}
    .wrap{max-width:860px;margin:24px auto;background:#fff;border-radius:14px;box-shadow:0 8px 30px rgba(0,0,0,.08);overflow:hidden}
    .head{padding:14px 18px;background:linear-gradient(135deg,#667eea,#764ba2);color:#fff}
    .row{display:flex;gap:10px;align-items:center}
    .pill{background:rgba(255,255,255,.2);padding:4px 10px;border-radius:999px;font-size:12px}
    .chat{height:420px;overflow:auto;padding:16px;background:#fafafa}
    .msg{margin:10px 0;display:flex}
    .msg .b{max-width:70%;padding:10px 14px;border-radius:14px;white-space:pre-wrap}
    .me{justify-content:flex-end}.me .b{background:#6b74f6;color:#fff;border-bottom-right-radius:4px}
    .bot{justify-content:flex-start}.bot .b{background:#fff;border:1px solid #e6e6e6;border-bottom-left-radius:4px}
    .foot{padding:12px;background:#fff;border-top:1px solid #eee}
    .row2{display:flex;gap:10px}
    input[type=text]{flex:1;padding:12px;border:2px solid #e6e6e6;border-radius:999px;font-size:14px}
    button{padding:10px 16px;border:0;border-radius:999px;background:#667eea;color:#fff;cursor:pointer}
    .bar{padding:8px 12px;background:#f1f1f7;border-bottom:1px solid #eee;display:flex;gap:8px;align-items:center;flex-wrap:wrap}
  </style>
</head>
<body>
<div class="wrap">
  <div class="head">
    <div class="row">
      <h2 style="margin:0;flex:1">🏊‍♂️ Spa Bot Tester</h2>
      <span id="conn" class="pill">Checking…</span>
      <span class="pill">User: <span id="uid">—</span></span>
      <span class="pill">Stage: <span id="stg">Unknown</span></span>
    </div>
  </div>

  <div class="bar">
    <button onclick="resetConv()">Reset Conversation</button>
  </div>

  <div id="chat" class="chat">
    <div class="msg bot"><div class="b">Welcome to Country Leisure! What brings you in today?</div></div>
  </div>

  <div class="foot">
    <div class="row2">
      <input id="msg" type="text" placeholder="Type a message and press Enter…"
             onkeypress="if(event.key==='Enter'&&!event.shiftKey){event.preventDefault();send();}">
      <button onclick="send()">Send</button>
    </div>
  </div>
</div>

<script>
function add(role,text){
  const el=document.createElement('div'); el.className='msg '+(role==='me'?'me':'bot');
  const b=document.createElement('div'); b.className='b'; b.textContent=text; el.appendChild(b);
  const c=document.getElementById('chat'); c.appendChild(el); c.scrollTop=c.scrollHeight;
  save();
}
const LS='cl_spa_chat';
function save(){
  const items=[...document.querySelectorAll('.msg')].map(m=>{
    const role=m.classList.contains('me')?'me':'bot';
    const txt=m.querySelector('.b').textContent; return {role,txt};
  });
  localStorage.setItem(LS, JSON.stringify(items).slice(0,40000));
}
function load(){
  const raw=localStorage.getItem(LS); if(!raw) return;
  const items=JSON.parse(raw); const c=document.getElementById('chat'); c.innerHTML='';
  items.forEach(it=>add(it.role,it.txt));
}
async function ping(){
  const t=document.getElementById('conn');
  try{ const r=await fetch('/ping',{credentials:'include'});
       t.textContent = r.ok ? 'Connected ✓' : 'Not connected ✗';
  }catch(_e){ t.textContent='Not connected ✗'; }
}
async function send(){
  const i=document.getElementById('msg'); const m=(i.value||'').trim(); if(!m) return; i.value='';
  add('me',m);
  try{
    const r=await fetch('/chat',{method:'POST',credentials:'include',
      headers:{'Content-Type':'application/json'},body:JSON.stringify({message:m})});
    if(!r.ok){ add('bot','(error)'); return; }
    const d=await r.json();
    add('bot', d.reply || '(no reply)');
    if(d.user_id) document.getElementById('uid').textContent=d.user_id;
    if(d.buyer_stage||d.stage) document.getElementById('stg').textContent=(d.buyer_stage||d.stage);
  }catch(e){ add('bot','Network error.'); }
}
async function resetConv(){
  try{
    await fetch('/reset-conversation',{method:'POST',credentials:'include',
      headers:{'Content-Type':'application/json'},body:'{}'});
    const c=document.getElementById('chat'); c.innerHTML='';
    add('bot','Conversation reset. How can I help you today?');
    document.getElementById('stg').textContent='browsing';
    save();
  }catch(e){ add('bot','Reset failed.'); }
}
window.onload=()=>{ load(); ping(); };
</script>
</body>
</html>
"""

@app.route("/tester", methods=["GET"])
def tester():
    return render_template_string(TESTER_HTML)

@app.route("/", methods=["GET"])
def home():
    return redirect("/tester")

# ---------- CORS Configuration ----------
ALLOWED_ORIGINS = {
    "http://127.0.0.1:5500",
    "http://localhost:5500",
    "http://127.0.0.1:5000",
    "http://localhost:5000",
}

CORS(
    app,
    supports_credentials=True,
    resources={r"/*": {"origins": list(ALLOWED_ORIGINS)}},
)

@app.after_request
def add_cors_headers(resp):
    origin = request.headers.get("Origin")
    if origin in ALLOWED_ORIGINS:
        resp.headers["Access-Control-Allow-Origin"] = origin
        resp.headers["Vary"] = "Origin"
        resp.headers["Access-Control-Allow-Credentials"] = "true"
        resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
        resp.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
    return resp

# ============================================================================
# IMPORTS
# ============================================================================

# Try to import enhanced memory manager
try:
    from enhanced_memory_manager_spa import EnhancedMemoryManager
    ENHANCED_AVAILABLE = True
    logger.info("Enhanced memory features available")
except ImportError:
    ENHANCED_AVAILABLE = False
    logger.warning("Enhanced memory features not available - using simple fallback")

# Import conversation flow engine
try:
    from conversation_flow_engine_spa import ConversationFlowEngine
    logger.info("Conversation Flow Engine loaded successfully")
except ImportError as e:
    logger.error(f"Failed to load Conversation Flow Engine: {e}")
    raise

# Import spa system
try:
    from spa_system_manager import spa_system, STORE_INFO
    logger.info("Spa System Manager loaded successfully")
except ImportError as e:
    logger.error(f"Failed to load Spa System Manager: {e}")
    raise

# ============================================================================
# MEMORY MANAGER
# ============================================================================

class InMemoryManager:
    """Simple in-memory storage for when DB not available"""
    def __init__(self):
        self.memories = {}
        logger.info("InMemory Manager initialized")
        
    def load_memory(self, user_id: str) -> Dict[str, Any]:
        if user_id not in self.memories:
            self.memories[user_id] = {
                "user_id": user_id,
                "interactions": [],
                "key_facts": {},
                "buyer_stage": "browsing",
                "engagement_level": 1,
                "conversation_summary": "",
                "cta_attempts": [],
                "asked_followups": [],
                "last_cta_turn": 0,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
        return self.memories[user_id]
    
    def save_memory(self, memory: Dict[str, Any]) -> None:
        memory["updated_at"] = datetime.now().isoformat()
        self.memories[memory["user_id"]] = memory
    
    def add_interaction(self, memory: Dict[str, Any], user_msg: str, bot_msg: str) -> None:
        memory["interactions"].append({
            "timestamp": datetime.now().isoformat(),
            "user": user_msg,
            "bot": bot_msg
        })
        # Keep only last 10 interactions
        if len(memory["interactions"]) > 10:
            memory["interactions"] = memory["interactions"][-10:]
    
    def build_context_summary(self, memory: Dict[str, Any]) -> str:
        facts = memory.get("key_facts", {})
        parts = []
        
        if facts.get("name"):
            parts.append(f"Name: {facts['name']}")
        if facts.get("family_size"):
            parts.append(f"Family size: {facts['family_size']}")
        if facts.get("preferred_seats"):
            parts.append(f"Looking for: {facts['preferred_seats']}-seater")
        if facts.get("budget_range"):
            parts.append(f"Budget: {facts['budget_range']}")
        if memory.get("buyer_stage"):
            parts.append(f"Stage: {memory['buyer_stage']}")
            
        return " | ".join(parts) if parts else ""

# Initialize memory manager
# =====================================================================
# MEMORY MANAGER – automatic fallback if DATABASE_URL missing
# =====================================================================
if ENHANCED_AVAILABLE:
    try:
        if not os.getenv("DATABASE_URL"):
            raise RuntimeError("DATABASE_URL not set (offline mode fallback)")
        MEMORY = EnhancedMemoryManager()
        logger.info("Using Enhanced Memory Manager (Postgres)")
    except Exception as e:
        logger.warning(f"Enhanced memory unavailable ({e}) — using simple in-memory fallback.")
        MEMORY = InMemoryManager()
        ENHANCED_AVAILABLE = False
else:
    MEMORY = InMemoryManager()
    logger.info("Using Simple Memory Manager")

# Initialize flow engine
FLOW_ENGINE = ConversationFlowEngine()
logger.info("Conversation Flow Engine initialized")

# ============================================================================
# IMPROVED SYSTEM PROMPT
# ============================================================================

SYSTEM_PROMPT = """You are Country Leisure's friendly spa sales expert in Moore, Oklahoma. You're knowledgeable, helpful, and conversational without being pushy.

KEY FACTS TO REMEMBER:
- All prices mentioned are ALL-INCLUSIVE (spa, cover, lifter, steps, electrical sub-panel, local delivery)
- Local delivery within 50 miles is FREE
- We offer 0% financing for qualified buyers
- Caldera Spas are our premium line (Vacanza, Paradise, Utopia series)
- Fantasy Spas are our budget-friendly option
- Showroom: 3001 N. I-35 Service Rd., Moore, OK 73160

YOUR PERSONALITY:
- Friendly and approachable, like a helpful neighbor
- Patient - don't rush customers through the process
- Focus on education and value, not aggressive selling
- Build rapport before pushing for visits or sales
- Answer questions directly without always adding a sales pitch

CONVERSATION GUIDELINES:
- Keep responses concise (2-3 sentences usually)
- Use the customer's name naturally when you learn it
- Match the customer's energy - if they're casual, be casual
- Only suggest visits/CTAs when it feels natural
- If discussing price, be accurate with the numbers

CRITICAL PRICING RULES:
- ALWAYS use the exact pricing provided by the system
- NEVER make up or estimate prices
- If pricing is not provided for something (like salt system add-on), say "I'll need to check on that specific pricing"
- PRICE RANGES (all-inclusive with spa, cover, lifter, steps, electrical panel, local delivery):
  * Fantasy Spas: $4,649 - $8,149
  * Caldera Vacanza: $8,747 - $12,747
  * Caldera Paradise: $12,847 - $16,847
  * Caldera Utopia: $16,247 - $24,747
- Models and their series:
  * Vacanza: Aventine, Celio, Tarino, Vanto, Marino, Palatino
  * Paradise: Kauai, Martinique, Seychelles, Reunion, Salina, Makena
  * Utopia: Ravello, Florence, Tahitian, Niagara, Geneva, Cantabria
  * Fantasy: Aspire, Drift, Embrace, Enamor, Entice, Enamor Premier, Entice Premier
- When discussing general pricing, use the ranges above
- When a specific model is requested, wait for the system to provide the exact price
- All prices quoted are all-inclusive - always emphasize this value point
  
CLICKABLE CTAs:
When appropriate based on the conversation, naturally include ONE of these clickable links (use markdown format [text](url)):
- When they ask about pricing/budget: "Want to know your budget? [Get pre-approved in minutes](https://www.countryleisuremfg.com/preapproval)"
- When they want to compare models: "You can [download our full brochure](https://hottubs.countryleisuremfg.com/download-a-brochure/) to see all options"
- When they ask about maintenance/care: "Check out the [Caldera owner's manual](https://hottubs.countryleisuremfg.com/caldera-spas-owners-manual/) for all the details"
- When they need help with space/placement: "Let's [schedule a free consultation](https://hottubs.countryleisuremfg.com/free-home-consultation/) at your place"
- When they're ready to see/try spas: "Come test soak! Call us at [405-799-7745](tel:405-799-7745) or visit our [Moore showroom](https://maps.google.com/?q=3001+N+I-35+Service+Rd+Moore+OK+73160)"
- For general questions: "Feel free to [contact our team](https://www.countryleisuremfg.com/contact) anytime"

CTA GUIDELINES:
- Only include a CTA when it naturally fits the conversation
- Don't force CTAs in browsing/early stages unless they ask
- Use CTAs more frequently in considering/ready stages
- Vary the CTA text to sound natural, but keep the exact URLs
- Never use more than one CTA per response

Remember: You're helping them find their perfect spa, not pushing for a quick sale

IMPORTANT:
- Be accurate with pricing - always use the exact prices provided
- Respect the buyer's journey - don't push too hard too fast
- If customer seems overwhelmed or jokes about being pushy, back off immediately
CRITICAL PRICING RULES:
- ALWAYS use the exact prices provided by the system
- NEVER guess or estimate prices
- All prices are all-inclusive (spa, cover, lifter, steps, electrical panel, local delivery)
- If you don't have a price, ask me to check rather than guessing or tell you are sorry and unsure have them fill a contact us form so that we can get back to them"""

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_or_create_user_id():
    """Get user ID from session or create new one"""
    if "user_id" not in session:
        import uuid
        session["user_id"] = f"user_{uuid.uuid4().hex[:8]}"
    return session["user_id"]

def extract_key_facts(message: str, memory: Dict[str, Any]) -> None:
    """Extract and update key facts from user message"""
    msg_lower = message.lower()
    key_facts = memory.get("key_facts", {})
    
    # Extract name
    name_patterns = [
        r"(?:i'm|i am|my name is|name's|call me)\s+([A-Z][a-z]+)",
        r"(?:this is)\s+([A-Z][a-z]+)"
    ]
    for pattern in name_patterns:
        if match := re.search(pattern, message, re.IGNORECASE):
            key_facts['name'] = match.group(1)
    
    # Extract budget
    if match := re.search(r"(\d+)k|(\d+),?(\d+)", message, re.IGNORECASE):
        if match.group(1):
            budget = int(match.group(1)) * 1000
            key_facts['budget_range'] = f"${budget:,}"
    
    # Extract seating preference
    if match := re.search(r"(\d+)\s*(?:person|people|seat)", message, re.IGNORECASE):
        key_facts['preferred_seats'] = int(match.group(1))
    
    # Extract priority/reason
    if 'relax' in msg_lower:
        key_facts['reason'] = 'relaxation'
    elif 'therap' in msg_lower:
        key_facts['reason'] = 'therapy'
    elif 'family' in msg_lower:
        key_facts['reason'] = 'family'
    elif 'entertain' in msg_lower:
        key_facts['reason'] = 'entertaining'
    
    memory['key_facts'] = key_facts

def should_show_cta_naturally(memory: Dict[str, Any], flow_evaluation: Dict) -> bool:
    """Determine if we should naturally show a CTA based on flow engine recommendation"""
    turn_count = len(memory.get("interactions", []))
    last_cta_turn = memory.get("last_cta_turn", 0)
    turns_since_cta = turn_count - last_cta_turn
    stage = flow_evaluation.get("buyer_stage", "browsing")
    
    # Never show CTA in first 2 interactions
    if turn_count < 2:
        return False
    
    # Follow flow engine's suggestion but moderate frequency
    if flow_evaluation.get("suggested_cta"):
        # Stage-based minimum spacing
        min_spacing = {
            "browsing": 6,
            "researching": 4,
            "considering": 3,
            "ready": 2
        }
        return turns_since_cta >= min_spacing.get(stage, 4)
    
    return False

# ============================================================================
# MAIN CHAT ENDPOINT - USING ACTUAL FLOW ENGINE METHODS
# ============================================================================

@app.route("/ping", methods=["GET"])
def ping():
    """Health check endpoint"""
    return jsonify({
        "status": "ok",
        "bot": "Country Leisure Spa Chat",
        "memory_type": "enhanced" if ENHANCED_AVAILABLE else "simple",
        "flow_engine": "active",
        "timestamp": datetime.now().isoformat()
    })

@app.route("/chat", methods=["POST", "OPTIONS"])
def chat():
    """Main chat endpoint using actual ConversationFlowEngine methods"""
    # Handle CORS preflight
    if request.method == "OPTIONS":
        return jsonify({"ok": True}), 200
        
    try:
        user_message = request.json.get("message", "").strip()
        if not user_message:
            return jsonify({"error": "Empty message"}), 400
        
        # Get or create user
        user_id = get_or_create_user_id()
        memory = MEMORY.load_memory(user_id)
        
        # Extract facts from message
        extract_key_facts(user_message, memory)
        
        # ========== USE FLOW ENGINE'S EVALUATE METHOD ==========
        flow_evaluation = FLOW_ENGINE.evaluate(memory, user_message)
        
        # Update memory with flow engine's stage
        old_stage = memory.get("buyer_stage", "browsing")
        new_stage = flow_evaluation.get("buyer_stage", old_stage)
        memory["buyer_stage"] = new_stage
        
        # Track follow-ups that have been asked
        if flow_evaluation.get("followups"):
            memory.setdefault("asked_followups", []).extend(flow_evaluation["followups"])
        
        logger.info(f"Flow Engine Evaluation: Stage {old_stage} -> {new_stage}, CTA: {flow_evaluation.get('suggested_cta')}")
        
        # ========== ANALYZE INTENT ==========
        intent_analysis = FLOW_ENGINE.analyze_conversation_intent(user_message)
        logger.debug(f"Intent Analysis: {intent_analysis}")
        
        # Build base messages for OpenAI
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        
        # Add context
        if context := MEMORY.build_context_summary(memory):
            messages.append({
                "role": "system",
                "content": f"CONVERSATION CONTEXT: {context}"
            })
        
        # Add recent conversation history
        for interaction in memory.get("interactions", [])[-3:]:
            messages.append({"role": "user", "content": interaction["user"]})
            messages.append({"role": "assistant", "content": interaction["bot"]})
        
        # ========== HANDLE SPECIFIC INTENTS ==========
        
        # ========== ALWAYS CHECK FOR MODEL MENTIONS ==========
        # Check for ANY specific model mention (not just during price inquiries)
        models_to_check = [
            "palatino", "tarino", "marino", "vanto", "celio", "aventine",  # Vacanza
            "kauai", "martinique", "seychelles", "reunion", "salina", "makena",  # Paradise
            "ravello", "florence", "tahitian", "niagara", "geneva", "cantabria",  # Utopia
            "aspire", "drift", "embrace", "enamor", "entice"  # Fantasy
        ]

        for model in models_to_check:
            if model in user_message.lower():
                price_quote = FLOW_ENGINE.get_pricing_quote(model)
                if price_quote:
                    messages.append({
                        "role": "system",
                        "content": f"IMPORTANT - EXACT PRICING: {price_quote} Use this exact information. Do NOT make up prices."
                    })
                    
                    # Add series context
                    if model in ["aventine", "celio", "tarino", "vanto", "marino", "palatino"]:
                        series_info = "Vacanza series - entry-level Caldera"
                    elif model in ["kauai", "martinique", "seychelles", "reunion", "salina", "makena"]:
                        series_info = "Paradise series - mid-tier with salt system compatibility"
                    elif model in ["ravello", "florence", "tahitian", "niagara", "geneva", "cantabria"]:
                        series_info = "Utopia series - premium with salt system included"
                    else:
                        series_info = "Fantasy series - budget-friendly plug-and-play"
                    
                    messages.append({
                        "role": "system",
                        "content": f"SERIES: {series_info}"
                    })
                break
        
        # Size question
        if intent_analysis.get("size_question"):
            if match := re.search(r"(\d+)\s*(?:person|people|seat)", user_message, re.IGNORECASE):
                seats = int(match.group(1))
                # Get models WITH PRICES
                recommendations = FLOW_ENGINE.get_model_recommendation({'seats': seats, 'budget_max': 99999})
                if recommendations:
                    messages.append({
                        "role": "system",
                        "content": f"IMPORTANT - Use these exact prices for {seats}-person spas:\n{recommendations}"
                })
        
        # Maintenance concern
        if intent_analysis.get("maintenance_concern"):
            maintenance_info = FLOW_ENGINE.get_knowledge_answer("maintenance")
            if maintenance_info:
                messages.append({
                    "role": "system",
                    "content": f"MAINTENANCE INFO: {maintenance_info}"
                })
        
        # Electrical question
        if intent_analysis.get("electrical_question"):
            electrical_info = FLOW_ENGINE.get_knowledge_answer("electrical")
            if electrical_info:
                messages.append({
                    "role": "system",
                    "content": f"ELECTRICAL INFO: {electrical_info}"
                })
        
        # ========== ADD FOLLOW-UP QUESTION IF APPROPRIATE ==========
        if flow_evaluation.get("followups") and len(memory.get("interactions", [])) % 3 == 0:
            followup = flow_evaluation["followups"][0] if flow_evaluation["followups"] else None
            if followup:
                messages.append({
                    "role": "system",
                    "content": f"End your response with this natural follow-up: {followup}"
                })
        
        # ========== HANDLE CTA SUGGESTION ==========
        cta_message = None
        if should_show_cta_naturally(memory, flow_evaluation):
            suggested_cta = flow_evaluation.get("suggested_cta")
            if suggested_cta:
                cta_message = FLOW_ENGINE.get_cta_message(memory, suggested_cta)
                if cta_message:
                    messages.append({
                        "role": "system",
                        "content": f"If it fits naturally, mention: {cta_message}"
                    })
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        # Call OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            temperature=0.7,
            max_tokens=150
        )
        
        bot_response = response.choices[0].message.content.strip()
        
        # Track CTA if one was shown
        cta_data = None
        if cta_message:
            memory["last_cta_turn"] = len(memory.get("interactions", []))
            memory.setdefault("cta_attempts", []).append({
                "type": flow_evaluation.get("suggested_cta"),
                "turn": len(memory.get("interactions", [])),
                "timestamp": datetime.now().isoformat()
            })
            
            # Add CTA data for response
            if flow_evaluation.get("suggested_cta") in ["showroom", "consultation", "quote"]:
                cta_data = {
                    "type": flow_evaluation.get("suggested_cta"),
                    "stage": memory["buyer_stage"]
                }
        
        # Save interaction
        MEMORY.add_interaction(memory, user_message, bot_response)
        MEMORY.save_memory(memory)
        
        # Return response
        return jsonify({
            "reply": bot_response,
            "buyer_stage": memory.get("buyer_stage"),
            "stage": memory.get("buyer_stage"),
            "user_id": user_id,
            "intent": intent_analysis,
            "cta": cta_data,
            "store_info": STORE_INFO if cta_data else None
        })
        
    except openai.error.OpenAIError as e:
        logger.error(f"OpenAI error: {e}")
        return jsonify({
            "error": "Having trouble connecting to AI service. Please try again."
        }), 500
    except Exception as e:
        logger.error(f"Chat error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Something went wrong. Please try again."}), 500

@app.route("/reset-conversation", methods=["POST"])
def reset_conversation():
    """Reset conversation for the current user"""
    try:
        payload = request.get_json(silent=True) or {}
        user_id = payload.get("user_id") or session.get("user_id")

        # Load memory for this user
        memory = MEMORY.load_memory(user_id)

        # Reset conversation fields
        memory["interactions"] = []
        memory["key_facts"] = {}
        memory["conversation_summary"] = ""
        memory["buyer_stage"] = "browsing"
        memory["engagement_level"] = 1
        memory["cta_attempts"] = []
        memory["asked_followups"] = []
        memory["last_cta_turn"] = 0
        
        # Save reset memory
        MEMORY.save_memory(memory)

        return jsonify({
            "ok": True,
            "user_id": memory.get("user_id"),
            "message": "Conversation reset."
        }), 200

    except Exception as e:
        logger.exception("reset-conversation error")
        return jsonify({"ok": False, "error": str(e)}), 500

# ============================================================================
# DEBUG ENDPOINTS
# ============================================================================

@app.route("/debug/flow-engine", methods=["GET"])
def debug_flow_engine():
    """Test flow engine functionality"""
    test_message = request.args.get("message", "How much is the Palatino?")
    test_memory = {
        "user_id": "test",
        "interactions": [],
        "key_facts": {},
        "buyer_stage": "browsing"
    }
    
    # Test flow engine evaluation
    evaluation = FLOW_ENGINE.evaluate(test_memory, test_message)
    intent = FLOW_ENGINE.analyze_conversation_intent(test_message)
    price_quote = FLOW_ENGINE.get_pricing_quote("palatino") if "palatino" in test_message.lower() else None
    
    return jsonify({
        "test_message": test_message,
        "evaluation": evaluation,
        "intent_analysis": intent,
        "price_quote": price_quote,
        "flow_engine_status": "operational"
    })

@app.route("/debug/memory/<user_id>", methods=["GET"])
def debug_memory(user_id):
    """View user memory for debugging"""
    try:
        memory = MEMORY.load_memory(user_id)
        return jsonify({
            "user_id": user_id,
            "memory": memory,
            "context": MEMORY.build_context_summary(memory)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
       
# ============================================================================
# ADMIN CONVERSATION FEED ENDPOINT
# ============================================================================
@app.route("/admin/conversations.json", methods=["GET"])
def admin_conversations():
    """Provide simplified conversation feed for admin dashboard"""
    token = request.args.get("token")
    if token != os.getenv("ADMIN_TOKEN", "spa-admin-token-2025"):
        return jsonify({"error": "unauthorized"}), 403

    limit = int(request.args.get("limit", 100))

    try:
        with MEMORY._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT user_id,
                           last_updated AS ts,
                           buyer_stage,
                           engagement_level,
                           interactions
                    FROM user_memories
                    ORDER BY last_updated DESC
                    LIMIT %s
                """, (limit,))
                rows = cur.fetchall()

        items = []
        for r in rows:
            # Extract most recent message pair
            interactions = r[4]
            if isinstance(interactions, str):
                try:
                    interactions = json.loads(interactions)
                except Exception:
                    interactions = []
            if interactions:
                last = interactions[-1]
                items.append({
                    "id": f"{r[0]}_{len(interactions)}",
                    "ts": r[1].isoformat() if r[1] else "",
                    "user_id": r[0],
                    "user_message": last.get("user", ""),
                    "bot_response": last.get("bot", "")
                })
        return jsonify({"items": items})

    except Exception as e:
        logger.error(f"Error loading admin conversations: {e}")
        import traceback; traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# ============================================================================
# RUN APPLICATION
# ============================================================================

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug_mode = os.getenv("FLASK_ENV") == "development"
    
    logger.info(f"Starting Spa Chat Bot on port {port}")
    logger.info(f"Debug mode: {debug_mode}")
    logger.info(f"Memory type: {'Enhanced' if ENHANCED_AVAILABLE else 'Simple'}")
    logger.info(f"Flow Engine: Loaded and operational")
    
    # Log all active components
    logger.info("=" * 50)
    logger.info("ACTIVE COMPONENTS:")
    logger.info(f"✓ Flask App: Ready")
    logger.info(f"✓ Memory Manager: {'Enhanced' if ENHANCED_AVAILABLE else 'Simple'}")
    logger.info(f"✓ Conversation Flow Engine: Active")
    logger.info(f"✓ Spa System Manager: Loaded")
    logger.info(f"✓ OpenAI Integration: {'Connected' if openai.api_key else 'Not configured'}")
    logger.info("=" * 50)
    
    app.run(
        host="0.0.0.0",
        port=port,
        debug=debug_mode
    )