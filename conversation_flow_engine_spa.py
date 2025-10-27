"""
Conversation Flow Engine – Spa Edition (Complete Fixed Version)
================================================================
Handles intelligent conversation management for Caldera & Fantasy spas.
Includes accurate pricing, sophisticated follow-ups, and smart stage detection.
"""

import random
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class ConversationFlowEngine:
    def __init__(self):
        """Initialize with spa-specific phrase banks and hardwired data"""
        
        # Hardwired All-Inclusive Pricing (tub, cover, lifter, steps, panel, local delivery)
        self.PRICING = {
            "caldera": {
                "vacanza": {
                    "aventine": {"seats": 2, "price": 8747, "jets": 14},
                    "celio": {"seats": 3, "price": 9747, "jets": 20},
                    "tarino": {"seats": 5, "price": 10747, "jets": 25},
                    "vanto": {"seats": 7, "price": 11247, "jets": 38},
                    "marino": {"seats": 6, "price": 11247, "jets": 30},
                    "palatino": {"seats": 6, "price": 12747, "jets": 28}
                },
                "paradise": {
                    "kauai": {"seats": 3, "price": 12847, "jets": 24},
                    "martinique": {"seats": 5, "price": 14847, "jets": 30},
                    "seychelles": {"seats": 6, "price": 15847, "jets": 36},
                    "reunion": {"seats": 7, "price": 15847, "jets": 40},
                    "salina": {"seats": 7, "price": 16847, "jets": 52},
                    "makena": {"seats": 6, "price": 16847, "jets": 42}
                },
                "utopia": {
                    "ravello": {"seats": 5, "price": 16247, "jets": 45},
                    "florence": {"seats": 6, "price": 19247, "jets": 68},
                    "tahitian": {"seats": 6, "price": 19247, "jets": 65},
                    "niagara": {"seats": 7, "price": 20747, "jets": 74},
                    "geneva": {"seats": 7, "price": 20747, "jets": 75},
                    "cantabria": {"seats": 8, "price": 24747, "jets": 88}
                }
            },
            "fantasy": {
                "freeflow": {
                    "aspire": {"seats": 2, "price": 4649, "voltage": "110V"},
                    "drift": {"seats": 4, "price": 5649, "voltage": "110V"},
                    "embrace": {"seats": 3, "price": 6349, "voltage": "110V"},
                    "enamor": {"seats": 4, "price": 6649, "voltage": "110V"},
                    "entice": {"seats": 5, "price": 7149, "voltage": "110V"},
                    "enamor_premier": {"seats": 4, "price": 7149, "voltage": "110V"},
                    "entice_premier": {"seats": 5, "price": 8149, "voltage": "110V/220V"}
                }
            }
        }
        
        # Hardwired Knowledge Base
        self.KNOWLEDGE = {
            "insulation": "Caldera uses FiberCor® insulation - loose fiberfill that's 4x denser than typical foam, keeping your energy costs way down.",
            "salt_system": "The FreshWater Salt System (Paradise & Utopia) uses an in-shell titanium cartridge you change every 4 months. No harsh chemicals, just soft water.",
            "warranties": "Caldera warranties run strong - Utopia/Paradise get 10-year shell structure, 7-year surface, 5-year components. Vacanza is 5/2/2. We stand behind what we sell.",
            "electrical": "Most Caldera spas need 220V/60A by an electrician. Fantasy's plug-and-play models use standard 110V outlets - no electrician needed.",
            "maintenance": "Monthly water care runs about $10-20. Takes maybe 10 minutes a month to maintain. Easier than a fish tank, honestly.",
            "pad_requirements": "You'll want a level concrete pad - typically 10x12 for most spas. Runs about $850-1200. Some folks use pavers or reinforced decks too.",
            "delivery_process": "We handle everything - placement, hookup, water fill, and walk you through operation. Takes about 2-3 hours total.",
            "jets": "Caldera's Euphoria jets pull in air to deliver 40% more flow than the pump provides. It's the difference between soaking and true hydrotherapy.",
            "energy_costs": "In Oklahoma, expect about $30-50 monthly in electricity for most models. Good insulation makes all the difference.",
            "lifespan": "With proper care, these spas last 15-20 years easy. We've got customers still loving their 20+ year old Calderas.",
            "water_capacity": "Most 5-7 person spas hold 300-450 gallons. The Cantabria holds about 475 gallons.",
            "heating_time": "From cold fill to 104°F takes about 8-24 hours depending on model and starting temp. Once hot, it maintains easily."
        }
        
        # CTA Phrase Variations - Showroom Visit
        self.showroom_ctas = [
            "Sounds like you're ready to feel the difference - want to come wet test a few models?",
            "I'm thinking it's time for you to sit in these spas and see what feels right. When can you swing by?",
            "You know what? Nothing beats actually sitting in the spa. Want to schedule a showroom visit?",
            "Based on what you're telling me, you'd really benefit from trying these out in person. How's your schedule looking?",
            "It feels like we're at the point where you need to experience the jets firsthand - want to come test them out?"
        ]
        
        # CTA Phrase Variations - Pricing/Quote
        self.pricing_ctas = [
            "Ready to talk real numbers? I can work up your all-inclusive price right now.",
            "Want me to put together your exact investment with everything included?",
            "Should we look at the total package price for the models you're interested in?",
            "Let's get specific on pricing - I'll include everything so there's no surprises."
        ]
        
        # Re-engagement phrases for returning users
        self.re_engagement_phrases = [
            "Hey! Good to see you back – still thinking about that hot tub?",
            "Welcome back! How's the spa search going?",
            "Hey there! Any new thoughts on which model?",
            "Good to see you again – getting closer to a decision?"
        ]
        
        # Philosophy phrases (adapted for spas)
        self.philosophy_phrases = {
            "wellness_focus": [
                "These spas aren't just hot water – they're your daily wellness routine.",
                "It's about creating that space where stress literally melts away.",
                "Think of it as your personal recovery zone, right in your backyard."
            ],
            "family_connection": [
                "Hot tubs are where families actually talk – no screens, just connection.",
                "It becomes the gathering spot where real conversations happen.",
                "Watch how it becomes everyone's favorite place to unwind together."
            ],
            "quality_materials": [
                "We only sell spas built to last – proper insulation, quality pumps, shells that don't fade.",
                "Oklahoma weather's tough on equipment – that's why we stick with Caldera and Fantasy.",
                "Buy it once, buy it right – these aren't the big-box store specials that fail in 3 years."
            ],
            "value_proposition": [
                "When you break it down daily, it's less than your coffee habit for incredible wellness benefits.",
                "15-20 years of daily stress relief and family time – that's serious value.",
                "Compare it to a gym membership you might not use – this is in your backyard every single day."
            ]
        }

    def get_opening_message(self, memory: Dict) -> Optional[str]:
        """Generate an appropriate opening or re-engagement message"""
        if memory.get("interactions"):
            # Returning user
            return random.choice(self.re_engagement_phrases)
        return None

    def get_model_recommendation(self, needs: Dict) -> str:
        """Recommend models based on user needs"""
        seats_needed = needs.get('seats', 4)
        budget_max = needs.get('budget_max', 20000)
        
        recommendations = []
        
        # Search through all models
        for brand, series_dict in self.PRICING.items():
            for series, models in series_dict.items():
                for model, info in models.items():
                    if info.get('seats', 0) >= seats_needed and info.get('price', 0) <= budget_max:
                        recommendations.append({
                            'model': model,
                            'brand': brand,
                            'series': series,
                            'price': info['price'],
                            'seats': info['seats'],
                            'jets': info.get('jets', 0)
                        })
        
        # Sort by price
        recommendations.sort(key=lambda x: x['price'])
        
        if not recommendations:
            return "Let me show you some options that might work with different parameters."
        
        # Format top 3 recommendations
        top_picks = recommendations[:3]
        response = f"Based on needing {seats_needed} seats, here are my top picks:\n"
        for pick in top_picks:
            brand_name = "Caldera" if pick['brand'] == 'caldera' else "Fantasy"
            response += f"• {brand_name} {pick['model'].title()}: ${pick['price']:,} ({pick['seats']} seats, {pick['jets']} jets)\n"
        
        return response

    def get_pricing_quote(self, model_name: str) -> Optional[str]:
        """Get exact pricing for a specific model"""
        model_lower = model_name.lower()
        
        # Search through all pricing data
        for brand, series_dict in self.PRICING.items():
            for series, models in series_dict.items():
                for model, info in models.items():
                    if model_lower in model or model in model_lower:
                        price = info['price']
                        seats = info.get('seats', '')
                        jets = info.get('jets', '')
                        
                        # Format the response with series info
                        brand_name = "Caldera" if brand == "caldera" else "Fantasy"
                        series_name = series.title()
                        
                        # Determine salt system compatibility
                        salt_info = ""
                        if series == "paradise":
                            salt_info = " Salt system compatible."
                        elif series == "utopia":
                            salt_info = " Salt system included."
                        
                        return f"The {brand_name} {model_name.title()} ({series_name} series) is ${price:,} all-inclusive - that's everything: spa, cover, lifter, steps, electrical panel, and local delivery. Seats {seats} comfortably with {jets} jets.{salt_info}"
        
        return None

    def get_series_pricing(self, series_name: str) -> str:
        """Get pricing range for a series"""
        series_lower = series_name.lower()
        
        if "vacanza" in series_lower:
            return "Vacanza series runs $8,747 to $12,747 all-inclusive - great starter spas with real therapy features."
        elif "paradise" in series_lower:
            return "Paradise series is $12,847 to $16,847 complete - this is our sweet spot with salt system compatibility."
        elif "utopia" in series_lower:
            return "Utopia series ranges $16,247 to $24,747 all-in - includes Salt System and premium everything."
        elif "fantasy" in series_lower or "freeflow" in series_lower:
            return "Fantasy spas run $4,649 to $8,149 complete - plug-and-play simplicity that works great."
        
        return "Our spas range from $4,649 for a simple plug-and-play to $24,747 for top-of-the-line therapy."

    def get_knowledge_answer(self, topic: str) -> Optional[str]:
        """Get knowledge base answer for a topic"""
        topic_lower = topic.lower()
        
        # Direct topic match
        if topic_lower in self.KNOWLEDGE:
            return self.KNOWLEDGE[topic_lower]
        
        # Keyword search
        for key, value in self.KNOWLEDGE.items():
            if topic_lower in key or key in topic_lower:
                return value
        
        # Common variations
        if "salt" in topic_lower:
            return self.KNOWLEDGE.get("salt_system")
        elif "electric" in topic_lower:
            return self.KNOWLEDGE.get("electrical")
        elif "maintain" in topic_lower or "care" in topic_lower:
            return self.KNOWLEDGE.get("maintenance")
        elif "deliver" in topic_lower:
            return self.KNOWLEDGE.get("delivery_process")
        elif "pad" in topic_lower or "concrete" in topic_lower:
            return self.KNOWLEDGE.get("pad_requirements")
        elif "cost" in topic_lower and "energy" in topic_lower:
            return self.KNOWLEDGE.get("energy_costs")
        
        return None

    def get_cta_message(self, memory: Dict, cta_type: str) -> str:
        """Get appropriate CTA message based on type and context"""
        name = memory.get("key_facts", {}).get("name", "")
        
        if cta_type == "showroom":
            messages = self.showroom_ctas
        elif cta_type == "quote" or cta_type == "consultation":
            messages = self.pricing_ctas
        else:
            return ""
        
        message = random.choice(messages)
        
        # Personalize if we have a name
        if name and "{name}" not in message:
            message = message.replace("you", f"you, {name}", 1)
        
        return message

    def detect_conversation_stall(self, memory: Dict) -> bool:
        """Detect if conversation has stalled"""
        interactions = memory.get("interactions", [])
        if len(interactions) < 3:
            return False
        
        # Check for repetitive questions
        last_three = interactions[-3:]
        user_messages = [i.get("user", "").lower() for i in last_three]
        
        # Similar messages indicate stall
        if len(set(user_messages)) == 1:
            return True
        
        # Short, non-committal responses
        if all(len(msg) < 20 for msg in user_messages):
            return True
        
        return False

    def get_conversation_restart(self, memory: Dict) -> str:
        """Get a conversation restart prompt"""
        stage = memory.get("buyer_stage", "browsing")
        
        if stage == "browsing":
            return "Let me ask you something different - what's your ideal spa experience look like?"
        elif stage == "researching":
            return "How about we approach this differently - what's the main problem you're trying to solve?"
        elif stage == "considering":
            return "Let's cut to the chase - what's holding you back from making a decision?"
        else:
            return "Quick question - ready to see these in person, or still have concerns?"

    def analyze_conversation_intent(self, user_message: str) -> Dict:
        """Analyze user message for intent and concerns"""
        message_lower = user_message.lower()
        
        return {
            "price_inquiry": any(word in message_lower for word in ["price", "cost", "how much", "expensive", "cheap", "budget"]),
            "size_question": any(word in message_lower for word in ["size", "seat", "person", "fit", "capacity"]),
            "maintenance_concern": any(word in message_lower for word in ["maintenance", "maintain", "clean", "chemical", "care"]),
            "jets_interest": any(word in message_lower for word in ["jet", "massage", "therapy", "neck", "pressure"]),
            "electrical_question": any(word in message_lower for word in ["electrical", "electric", "plug", "110", "220", "volt"]),
            "comparison": any(word in message_lower for word in ["versus", "vs", "compare", "difference", "better", "bullfrog", "hotspring"]),
            "ready_signal": any(word in message_lower for word in ["ready", "let's do", "want to buy", "order", "purchase", "how do i"]),
            "showroom_interest": any(word in message_lower for word in ["see", "test", "try", "visit", "showroom", "wet test"])
        }

    def get_neck_jet_models(self) -> str:
        """Return info about models with neck jets"""
        return "For neck jets, you want the Geneva or Niagara in the Utopia series - both around $20,747 with incredible neck and shoulder therapy. The Tahitian at $19,247 also has great upper body jets."

    def get_models_by_size(self, seats: int) -> List[str]:
        """Get model names that seat a specific number"""
        models = []
        for brand, series_dict in self.PRICING.items():
            for series, model_dict in series_dict.items():
                for model, info in model_dict.items():
                    if info.get('seats') == seats:
                        models.append(model.title())
        return models

    def get_all_model_names(self) -> List[str]:
        """Get all model names for checking mentions"""
        models = []
        for brand, series_dict in self.PRICING.items():
            for series, model_dict in series_dict.items():
                models.extend(model_dict.keys())
        return models

    def get_plug_and_play_options(self) -> str:
        """Return info about plug-and-play models"""
        return "Fantasy spas are all 110V plug-and-play - just plug into any outlet. Aspire and Drift are the most popular starters."

    def get_financing_info(self) -> str:
        """Return financing information"""
        return "We offer 0% financing for qualified buyers - most folks get approved in minutes. Monthly payments can be as low as $99 depending on the model and term."

    def get_warranty_info(self) -> str:
        """Return warranty information"""
        return self.KNOWLEDGE.get("warranties", "Full warranty details available at purchase.")

    def get_energy_efficiency_info(self) -> str:
        """Return energy efficiency information"""
        return self.KNOWLEDGE.get("insulation", "") + " " + self.KNOWLEDGE.get("energy_costs", "")

    def evaluate(self, memory: Dict[str, Any], user_message: str) -> Dict[str, Any]:
        """Main entrypoint - evaluates conversation state and suggests next steps"""
        msg = user_message.lower()
        current_stage = memory.get("buyer_stage", "browsing")
        interaction_count = len(memory.get("interactions", []))
        
        # --- SMART STAGE DETECTION ---
        new_stage = current_stage
        
        # READY signals (wants to buy)
        if any(k in msg for k in ["schedule", "visit", "showroom", "wet test", "try it", "see it"]):
            new_stage = "ready"
        elif any(phrase in msg for phrase in ["when can i", "when could i", "how soon", "delivery", "install"]):
            new_stage = "ready"
        elif "get it faster" in msg or "rush" in msg or "this week" in msg:
            new_stage = "ready"
        elif any(phrase in msg for phrase in ["ready to buy", "let's do", "want to order", "how do i buy"]):
            new_stage = "ready"
            
        # CONSIDERING signals (evaluating purchase)
        elif any(k in msg for k in ["price", "cost", "$", "finance", "how much", "payment"]):
            new_stage = "considering"
        elif any(k in msg for k in ["electrical", "concrete", "pad", "weight", "placement"]):
            new_stage = "considering"  # Technical questions = serious
        elif "warranty" in msg or "guarantee" in msg:
            new_stage = "considering"
            
        # RESEARCHING signals (comparing options)
        elif any(model in msg for model in self.get_all_model_names()):
            if current_stage == "browsing":
                new_stage = "researching"
        elif any(k in msg for k in ["compare", "difference", "which", "versus", "vs"]):
            new_stage = "researching"
        elif any(k in msg for k in ["seats", "person", "people", "size", "fit"]):
            if current_stage == "browsing":
                new_stage = "researching"
        
        # Never downgrade stages
        stage_order = ["browsing", "researching", "considering", "ready"]
        if stage_order.index(new_stage) < stage_order.index(current_stage):
            new_stage = current_stage
        
        # --- KILLER FOLLOW-UPS ---
        facts = memory.get("key_facts", {})
        reason = (facts.get("reason") or facts.get("reason_text") or "").lower()
        name = facts.get("name", "")
        
        followups = []
        
        if new_stage == "ready":
            # They're ready - focus on removing final barriers
            if "delivery" in msg or "when" in msg:
                followups = [
                    "Any special placement considerations I should know about?",
                    "Will you need help with the electrical setup, or do you have an electrician?"
                ]
            else:
                followups = [
                    "Would seeing the jets in action help you decide between models?",
                    "Ready to feel the difference? We can schedule a wet test this week.",
                    f"Should we talk financing options to make this happen{', ' + name if name else ''}?"
                ]
                
        elif new_stage == "considering":
            # They're evaluating - address specific concerns
            if "family" in reason:
                followups = [
                    "How many kids? Some models have cooler zones perfect for little ones.",
                    "Thinking more movie nights in the spa or quiet couple time after kids are in bed?"
                ]
            elif "therapy" in reason or "therap" in msg:
                followups = [
                    "Where's the pain worst - lower back, shoulders, or all over?",
                    "Morning stiffness or end-of-day soreness driving this?",
                    "Want targeted jets or full-body therapy?"
                ]
            elif "relax" in reason:
                followups = [
                    "Picture this: stars above, jets below - morning person or evening soaker?",
                    "Quiet solo relaxation or social spa time with friends?",
                    "What's your perfect spa temperature - toasty 104° or moderate 100°?"
                ]
            else:
                followups = [
                    f"What problem are you hoping a spa solves{', ' + name if name else ''}?",
                    "Besides price, what's your biggest concern about owning one?",
                    "See yourself using it more for recovery or recreation?"
                ]
                
        elif new_stage == "researching":
            # They're comparing - help them narrow down
            if interaction_count < 3:
                followups = [
                    "What sparked your interest in getting a hot tub?",
                    "First spa or upgrading from an older one?",
                    "Most important: jet power, energy efficiency, or easy maintenance?"
                ]
            elif any(model in msg for model in self.get_all_model_names()):
                followups = [
                    "That model's popular - what caught your eye about it?",
                    "Comparing to others or pretty set on this one?",
                    "Want to know what owners say about that model?"
                ]
            else:
                followups = [
                    f"How many people realistically{', ' + name if name else ''}?",
                    "Deck, patio, or thinking about a pad?",
                    "Daily use or weekend warrior?"
                ]
                
        else:  # browsing
            # They're exploring - uncover motivation
            if interaction_count == 0:
                followups = [
                    "What brings you in today - just curious or seriously shopping?",
                    "Something specific you're looking for in a spa?"
                ]
            elif "salt" in msg or "chemical" in msg:
                followups = [
                    "Sensitive skin or just prefer the natural approach?",
                    "Know anyone with a salt system? They're pretty amazing."
                ]
            elif "neck" in msg or "jets" in msg:
                followups = [
                    "Chronic tension or just love a good massage?",
                    "Ever tried different jet types? Huge difference between brands."
                ]
            else:
                followups = [
                    "Neighbor get one? Doctor recommend it? What's the story?",
                    f"Picture having one - what's the first thing you'd do{', ' + name if name else ''}?",
                    "What's holding you back from pulling the trigger?"
                ]
        
        # Remove duplicates
        already_asked = set(memory.get("asked_followups", []))
        followups = [f for f in followups if f not in already_asked][:2]
        
        # --- SMART CTA SUGGESTIONS ---
        cta_suggest = None
        
        # Aggressive buying signals = immediate CTA
        if any(phrase in msg for phrase in ["when can i", "how soon", "ready to buy", "let's do this"]):
            cta_suggest = "showroom"
        elif new_stage == "ready" and interaction_count >= 2:
            cta_suggest = "showroom"
        elif new_stage == "considering":
            if interaction_count >= 3:
                if any(word in msg for word in ["price", "cost", "finance"]):
                    cta_suggest = "consultation"
                elif any(model in msg for model in self.get_all_model_names()):
                    cta_suggest = "showroom"
            elif interaction_count >= 5:
                cta_suggest = "brochure"
        elif new_stage == "researching" and interaction_count >= 4:
            cta_suggest = "brochure"
        
        return {
            "buyer_stage": new_stage,
            "followups": followups,
            "suggested_cta": cta_suggest
        }