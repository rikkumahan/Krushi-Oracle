from services.idea_generator import IdeaGeneratorService
from services.idea_scorer import IdeaScorerService
from services.market_signals import MarketSignalsService

class AIService:
    def __init__(self):
        self.generator = IdeaGeneratorService()
        self.scorer = IdeaScorerService()
        self.market = MarketSignalsService()
