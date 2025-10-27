"""
Spa System Manager - The Data Brain
====================================
Handles all spa data: pricing, models, CTAs, and knowledge base.
Mirrors cocktail bot structure with everything hardwired.
"""

import json
import logging
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime

logger = logging.getLogger(__name__)

# ============================================================================
# CTA LIBRARY - All CTAs with smart context
# ============================================================================

CTA_LIBRARY = {
    'contact': {
        'url': 'https://www.countryleisuremfg.com/contact',
        'text': 'Contact Country Leisure',
        'button_text': 'Contact Us',
        'stages': ['any'],  # Available at any stage
        'priority': 5,
        'natural_phrases': [
            "Feel free to reach out to our team at countryleisuremfg.com/contact",
            "You can always contact us directly if you'd like to chat",
            "Our spa experts are here to help - just visit our contact page"
        ]
    },
    'consultation': {
        'url': 'https://hottubs.countryleisuremfg.com/free-home-consultation/',
        'text': 'Schedule Free In-Home Consultation',
        'button_text': 'Free Consultation',
        'stages': ['considering', 'ready'],
        'priority': 1,
        'natural_phrases': [
            "How about we come to you? Schedule a free in-home consultation at your convenience",
            "Let's set up a free consultation at your place - we'll help you visualize the perfect spa",
            "I'd recommend our free home consultation - we'll measure your space and discuss options"
        ]
    },
    'brochure': {
        'url': 'https://hottubs.countryleisuremfg.com/download-a-brochure/',
        'text': 'Download Our Spa Brochure',
        'button_text': 'Get Brochure',
        'stages': ['browsing', 'researching'],
        'priority': 2,
        'natural_phrases': [
            "You can download our full brochure to browse at your leisure",
            "Grab our digital brochure - it has all the models and features laid out nicely",
            "Want to see everything in one place? Our brochure covers all models and options"
        ]
    },
    'manual': {
        'url': 'https://hottubs.countryleisuremfg.com/caldera-spas-owners-manual/',
        'text': "Caldera Owner's Manual",
        'button_text': "Owner's Manual",
        'stages': ['ready', 'owner'],
        'priority': 4,
        'natural_phrases': [
            "You can check out the Caldera owner's manual for all the technical details",
            "The owner's manual has great info on maintenance and features",
            "For the nitty-gritty details, the Caldera manual covers everything"
        ]
    },
    'preapproval': {
        'url': 'https://www.countryleisuremfg.com/preapproval',
        'text': 'Get Pre-Approved for Financing',
        'button_text': 'Get Pre-Approved',
        'stages': ['considering', 'ready'],
        'priority': 1,
        'natural_phrases': [
            "Want to know your budget? Get pre-approved in minutes - no obligation",
            "Check your financing options with our quick pre-approval process",
            "Many folks like to get pre-approved first - takes just a few minutes online"
        ]
    },
    'showroom': {
        'url': None,  # This is handled differently - schedule via phone
        'text': 'Visit Our Showroom',
        'button_text': 'Schedule Showroom Visit',
        'stages': ['researching', 'considering', 'ready'],
        'priority': 1,
        'natural_phrases': [
            "Come test soak! Our Moore showroom is at 3001 N. I-35 Service Rd",
            "Nothing beats a test soak - visit us in Moore to try before you buy",
            "Want to feel the difference? Stop by our showroom for a wet test"
        ]
    }
}

# Store info footer
STORE_INFO = "Country Leisure | 3001 N. I-35 Service Rd., Moore, OK 73160 | 405-799-7745"

# ============================================================================
# HARDWIRED PRICING - All-Inclusive (Tub + Cover + Lifter + Steps + Panel)
# ============================================================================

CALDERA_PRICING = {
    # Vacanza Series
    'aventine': {'price': 8747, 'series': 'Vacanza', 'seats': 2, 'jets': 12},
    'celio': {'price': 9747, 'series': 'Vacanza', 'seats': 3, 'jets': 22},
    'tarino': {'price': 10747, 'series': 'Vacanza', 'seats': 5, 'jets': 28},
    'vanto': {'price': 11247, 'series': 'Vacanza', 'seats': 7, 'jets': 42},
    'marino': {'price': 11247, 'series': 'Vacanza', 'seats': 6, 'jets': 36},
    'palatino': {'price': 12747, 'series': 'Vacanza', 'seats': 6, 'jets': 38},
    
    # Paradise Series
    'kauai': {'price': 12847, 'series': 'Paradise', 'seats': 3, 'jets': 25},
    'martinique': {'price': 14847, 'series': 'Paradise', 'seats': 5, 'jets': 30},
    'seychelles': {'price': 15847, 'series': 'Paradise', 'seats': 6, 'jets': 40},
    'reunion': {'price': 15847, 'series': 'Paradise', 'seats': 7, 'jets': 44},
    'salina': {'price': 16847, 'series': 'Paradise', 'seats': 7, 'jets': 52},
    'makena': {'price': 16847, 'series': 'Paradise', 'seats': 6, 'jets': 42},
    
    # Utopia Series
    'ravello': {'price': 16247, 'series': 'Utopia', 'seats': 5, 'jets': 30},
    'florence': {'price': 19247, 'series': 'Utopia', 'seats': 6, 'jets': 42},
    'tahitian': {'price': 19247, 'series': 'Utopia', 'seats': 6, 'jets': 44},
    'niagara': {'price': 20747, 'series': 'Utopia', 'seats': 7, 'jets': 52},
    'geneva': {'price': 20747, 'series': 'Utopia', 'seats': 7, 'jets': 42},
    'cantabria': {'price': 24747, 'series': 'Utopia', 'seats': 8, 'jets': 88}
}

FANTASY_PRICING = {
    'aspire': {'price': 4649, 'seats': 2, 'jets': 11},
    'drift': {'price': 5649, 'seats': 4, 'jets': 21},
    'embrace': {'price': 6349, 'seats': 3, 'jets': 17},
    'enamor': {'price': 6649, 'seats': 4, 'jets': 23},
    'entice': {'price': 7149, 'seats': 5, 'jets': 25},
    'enamor premier': {'price': 7149, 'seats': 4, 'jets': 23},
    'entice premier': {'price': 8149, 'seats': 5, 'jets': 25}
}

# Series descriptions for natural conversation
SERIES_INFO = {
    'vacanza': "Our Vacanza series is the perfect entry into Caldera quality - great therapy at an accessible price",
    'paradise': "Paradise series hits the sweet spot - more jets, more features, incredible value",
    'utopia': "Utopia is our premium line - everything you could want in a spa, built to last decades",
    'fantasy': "Fantasy spas are our entry-level line - simple, reliable, and budget-friendly"
}

# ============================================================================
# KNOWLEDGE BASE - Key Facts
# ============================================================================

SPA_KNOWLEDGE = {
    'fibercor': {
        'fact': "Caldera uses FiberCor insulation - it's 4x denser than regular foam, fills the entire cabinet, and doesn't stick to plumbing so service is easier",
        'keywords': ['insulation', 'fibercor', 'fibercore', 'energy', 'efficient']
    },
    'ozone': {
        'fact': "All Caldera spas include FreshWater Ozone systems that destroy contaminants naturally, reducing chemical needs by up to 75%",
        'keywords': ['ozone', 'chemicals', 'maintenance', 'water care', 'freshwater']
    },
    'freshwater_iq': {
    'fact': "FreshWater IQ is Caldera's smart water care system - it monitors water conditions and tells you exactly what your spa needs via the wireless touchscreen. Takes the guesswork out of water care",
    'keywords': ['freshwater iq', 'fresh water', 'water monitoring', 'smart water', 'water care', 'iq system']
    },
    'salt_system': {
        'fact': "The FreshWater Salt System (available on Utopia/Paradise) generates chlorine from salt - just change the cartridge every 4 months. Works perfectly with FreshWater IQ for automated water care",
        'keywords': ['salt', 'salt system', 'chemicals', 'chlorine', 'maintenance']
    },
    'comfort_collar': {
    'fact': "Caldera's Comfort Collar jets cradle your neck perfectly - exclusive sculpted pillows that actually support your head while the jets work on neck tension",
    'keywords': ['comfort collar', 'neck jets', 'pillows', 'neck support', 'headrest']
    },
    'acquarella': {
        'fact': "Acquarella jets are Caldera's exclusive combination jets - they mix air and water for a gentler, champagne-like massage that's perfect for sensitive areas",
        'keywords': ['acquarella', 'jets', 'gentle massage', 'champagne jets', 'combination jets']
    },
    'therapy': {
        'fact': "Caldera's jet placement is based on circuit therapy - each seat targets different muscle groups for complete hydrotherapy",
        'keywords': ['therapy', 'jets', 'hydrotherapy', 'massage', 'circuit']
    },
    'warranty': {
        'fact': "Caldera warranty: 5 years on components, lifetime on shell structure. Fantasy: 2 years components, 5 years shell",
        'keywords': ['warranty', 'guarantee', 'coverage', 'protection']
    },
    'power': {
        'fact': "Most Caldera spas need 220V/50amp service. Fantasy Drift and Aspire can run on standard 110V plug",
        'keywords': ['power', 'electrical', '220v', '110v', 'plug', 'voltage', 'amp']
    },
    'delivery': {
        'fact': "White-glove delivery includes placement, filling, chemical startup, and orientation - typically $350 locally",
        'keywords': ['delivery', 'installation', 'setup', 'install']
    }
}

# ============================================================================
# DATA ACCESS CLASS
# ============================================================================

class SpaSystemManager:
    """Manages all spa data access and CTA logic"""
    
    def __init__(self):
        """Initialize the spa system manager"""
        self.caldera_pricing = CALDERA_PRICING
        self.fantasy_pricing = FANTASY_PRICING
        self.cta_library = CTA_LIBRARY
        self.spa_knowledge = SPA_KNOWLEDGE
        logger.info("Spa System Manager initialized with hardwired data")
    
    # ========== PRICING METHODS ==========
    
    def get_model_price(self, model_name: str) -> Optional[Dict[str, Any]]:
        """Get price and details for a specific model"""
        model_lower = model_name.lower().strip()
        
        # Check Caldera
        if model_lower in self.caldera_pricing:
            info = self.caldera_pricing[model_lower].copy()
            info['brand'] = 'Caldera'
            info['model'] = model_name.title()
            return info
        
        # Check Fantasy
        if model_lower in self.fantasy_pricing:
            info = self.fantasy_pricing[model_lower].copy()
            info['brand'] = 'Fantasy'
            info['model'] = model_name.title()
            return info
        
        return None
    
    def get_price_range_by_seats(self, seats: int) -> str:
        """Get price range for spas with specific seating"""
        caldera_prices = []
        fantasy_prices = []
        
        # Collect prices for matching seat counts
        for model, info in self.caldera_pricing.items():
            if info['seats'] == seats:
                caldera_prices.append(info['price'])
        
        for model, info in self.fantasy_pricing.items():
            if info['seats'] == seats:
                fantasy_prices.append(info['price'])
        
        if not caldera_prices and not fantasy_prices:
            return f"We don't currently have {seats}-person spas, but we have options from 2-8 seats"
        
        # Build response
        response_parts = []
        if fantasy_prices:
            response_parts.append(f"Fantasy ${min(fantasy_prices):,}-${max(fantasy_prices):,}")
        if caldera_prices:
            response_parts.append(f"Caldera ${min(caldera_prices):,}-${max(caldera_prices):,}")
        
        return f"For {seats}-person spas: {' or '.join(response_parts)}"
    
    def get_series_models(self, series: str) -> List[Dict[str, Any]]:
        """Get all models in a series"""
        series_lower = series.lower()
        models = []
        
        for model, info in self.caldera_pricing.items():
            if info.get('series', '').lower() == series_lower:
                model_info = info.copy()
                model_info['model'] = model.title()
                models.append(model_info)
        
        return sorted(models, key=lambda x: x['price'])
    
    # ========== CTA METHODS ==========
    
    def get_appropriate_cta(self, buyer_stage: str, recent_ctas: List[str]) -> Optional[Dict[str, Any]]:
        """Get the best CTA for current buyer stage"""
        available_ctas = []
        
        for cta_key, cta_info in self.cta_library.items():
            # Skip if recently shown
            if cta_key in recent_ctas:
                continue
            
            # Check if appropriate for stage
            if buyer_stage in cta_info['stages'] or 'any' in cta_info['stages']:
                available_ctas.append((cta_key, cta_info))
        
        if not available_ctas:
            return None
        
        # Sort by priority and return best
        available_ctas.sort(key=lambda x: x[1]['priority'])
        return available_ctas[0][1] if available_ctas else None
    
    def format_cta_natural(self, cta_key: str) -> str:
        """Get a natural language version of a CTA"""
        if cta_key not in self.cta_library:
            return ""
        
        import random
        cta = self.cta_library[cta_key]
        return random.choice(cta['natural_phrases'])
    
    # ========== KNOWLEDGE METHODS ==========
    
    def search_knowledge(self, query: str) -> Optional[str]:
        """Search knowledge base for relevant facts"""
        query_lower = query.lower()
        relevant_facts = []
        
        for topic, info in self.spa_knowledge.items():
            # Check if any keywords match
            if any(keyword in query_lower for keyword in info['keywords']):
                relevant_facts.append(info['fact'])
        
        return " ".join(relevant_facts) if relevant_facts else None
    
    def get_fact_by_topic(self, topic: str) -> Optional[str]:
        """Get a specific fact by topic"""
        topic_lower = topic.lower()
        if topic_lower in self.spa_knowledge:
            return self.spa_knowledge[topic_lower]['fact']
        
        # Also check if topic matches any keywords
        for key, info in self.spa_knowledge.items():
            if topic_lower in info['keywords']:
                return info['fact']
        
        return None
    
    # ========== HELPER METHODS ==========
    
    def build_context_summary(self, user_info: Dict[str, Any]) -> str:
        """Build a context summary for the AI"""
        parts = []
        
        # Add buyer stage
        if stage := user_info.get('buyer_stage'):
            parts.append(f"Stage: {stage}")
        
        # Add key interests
        if interests := user_info.get('interests'):
            parts.append(f"Interested in: {', '.join(interests)}")
        
        # Add budget if mentioned
        if budget := user_info.get('budget_mentioned'):
            parts.append(f"Budget: {budget}")
        
        # Add family size if known
        if family := user_info.get('family_size'):
            parts.append(f"Family size: {family}")
        
        return " | ".join(parts) if parts else "New conversation"
    
    def get_competitive_response(self, competitor: str) -> str:
        """Get response when competitor is mentioned"""
        responses = {
            'hotspring': "Hot Spring makes good spas - we actually love the competition! The main difference is our FiberCor insulation and our pricing tends to be more accessible",
            'jacuzzi': "Jacuzzi is the name everyone knows! They make solid spas. We focus more on energy efficiency and therapeutic jet placement",
            'sundance': "Sundance builds quality spas. Where we differ is our cabinet insulation and our circuit therapy approach to jet design",
            'bullfrog': "Bullfrog's JetPaks are interesting! We take a different approach with dedicated therapy circuits built into each seat",
            'default': "That's a quality brand! Every manufacturer has their strengths. Ours are energy efficiency, therapeutic design, and local service"
        }
        
        comp_lower = competitor.lower()
        for key in responses:
            if key in comp_lower:
                return responses[key]
        
        return responses['default']
    
    def format_price_response(self, price: int, model: str = None) -> str:
        """Format a price in natural conversation"""
        price_str = f"${price:,}"
        
        responses = [
            f"That comes to {price_str} all-inclusive",
            f"You're looking at {price_str} with everything included",
            f"All-in price is {price_str} - that's with cover, lifter, steps, and electrical panel",
            f"{price_str} gets you everything - spa, cover, lifter, steps, even the electrical sub-panel"
        ]
        
        import random
        base = random.choice(responses)
        
        if model:
            base = f"The {model} " + base.lower()
        
        return base

# ============================================================================
# SINGLETON INSTANCE
# ============================================================================

# Create single instance for import
spa_system = SpaSystemManager()

# Example usage functions
def get_model_price(model_name: str) -> Optional[Dict[str, Any]]:
    """Convenience function for getting model price"""
    return spa_system.get_model_price(model_name)

def get_appropriate_cta(buyer_stage: str, recent_ctas: List[str]) -> Optional[Dict[str, Any]]:
    """Convenience function for getting appropriate CTA"""
    return spa_system.get_appropriate_cta(buyer_stage, recent_ctas)

def search_knowledge(query: str) -> Optional[str]:
    """Convenience function for searching knowledge base"""
    return spa_system.search_knowledge(query)