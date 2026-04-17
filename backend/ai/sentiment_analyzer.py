"""
AI Sentiment Analyzer — DialogFlow Chatbot Enhancement
Author: Muhammad Ammar Ahmed — Senior Test Automation Engineer

Adds real-time sentiment analysis to chatbot conversations using
VADER + TextBlob, with escalation logic for negative sentiment.
Enhances the DialogFlow chatbot with emotional intelligence.
"""

import logging
from dataclasses import dataclass
from typing import Optional
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

logger = logging.getLogger(__name__)


@dataclass
class SentimentResult:
    """Structured sentiment analysis result."""
    text: str
    sentiment: str          # positive / negative / neutral
    polarity: float         # -1.0 to 1.0
    subjectivity: float     # 0.0 to 1.0
    confidence: float       # 0.0 to 1.0
    vader_compound: float   # VADER compound score
    emotion: str            # joy / frustration / anger / neutral / confusion
    requires_escalation: bool
    escalation_reason: Optional[str] = None


class SentimentAnalyzer:
    """
    Hybrid sentiment analyzer combining VADER and TextBlob
    for accurate real-time chatbot conversation analysis.
    """

    ESCALATION_THRESHOLD = -0.5
    FRUSTRATION_KEYWORDS = [
        'frustrated', 'angry', 'terrible', 'awful', 'useless',
        'broken', 'horrible', 'worst', 'hate', 'disgusting',
        'not working', 'doesnt work', "doesn't work", 'bug', 'error'
    ]
    JOY_KEYWORDS = [
        'great', 'excellent', 'amazing', 'love', 'perfect',
        'fantastic', 'wonderful', 'helpful', 'thank', 'awesome'
    ]
    CONFUSION_KEYWORDS = [
        'confused', 'dont understand', "don't understand", 'unclear',
        'what do you mean', 'how does', 'explain', 'help me'
    ]

    def __init__(self):
        self.vader = SentimentIntensityAnalyzer()
        logger.info("SentimentAnalyzer initialized with VADER + TextBlob")

    def analyze(self, text: str) -> SentimentResult:
        """
        Perform comprehensive sentiment analysis on user input.
        Combines VADER (social media optimized) and TextBlob (NLP).
        """
        if not text or not text.strip():
            return self._neutral_result(text or "")

        text_lower = text.lower().strip()

        # VADER analysis — great for short conversational text
        vader_scores = self.vader.polarity_scores(text)
        vader_compound = vader_scores['compound']

        # TextBlob analysis — better for subjectivity
        blob = TextBlob(text)
        tb_polarity = blob.sentiment.polarity
        tb_subjectivity = blob.sentiment.subjectivity

        # Weighted combination (VADER 60%, TextBlob 40%)
        combined_polarity = (vader_compound * 0.6) + (tb_polarity * 0.4)

        # Classify sentiment
        sentiment = self._classify_sentiment(combined_polarity)

        # Detect emotion
        emotion = self._detect_emotion(text_lower, combined_polarity)

        # Calculate confidence
        confidence = min(abs(vader_compound) + abs(tb_polarity) / 2, 1.0)

        # Check escalation
        requires_escalation, reason = self._check_escalation(
            combined_polarity, text_lower, emotion
        )

        result = SentimentResult(
            text=text,
            sentiment=sentiment,
            polarity=round(combined_polarity, 3),
            subjectivity=round(tb_subjectivity, 3),
            confidence=round(confidence, 3),
            vader_compound=round(vader_compound, 3),
            emotion=emotion,
            requires_escalation=requires_escalation,
            escalation_reason=reason
        )

        logger.info(
            f"Sentiment: {sentiment} | Emotion: {emotion} | "
            f"Polarity: {combined_polarity:.2f} | Escalate: {requires_escalation}"
        )

        return result

    def _classify_sentiment(self, polarity: float) -> str:
        if polarity >= 0.05:
            return "positive"
        elif polarity <= -0.05:
            return "negative"
        return "neutral"

    def _detect_emotion(self, text_lower: str, polarity: float) -> str:
        if any(k in text_lower for k in self.FRUSTRATION_KEYWORDS):
            return "frustration"
        if any(k in text_lower for k in self.JOY_KEYWORDS):
            return "joy"
        if any(k in text_lower for k in self.CONFUSION_KEYWORDS):
            return "confusion"
        if polarity <= -0.6:
            return "anger"
        if polarity >= 0.6:
            return "joy"
        return "neutral"

    def _check_escalation(self, polarity, text_lower, emotion):
        if polarity <= self.ESCALATION_THRESHOLD:
            return True, f"Very negative sentiment (polarity: {polarity:.2f})"
        if emotion == "anger":
            return True, "Anger detected in user message"
        if emotion == "frustration" and polarity < -0.2:
            return True, "User frustration detected"
        urgent = ['urgent', 'emergency', 'asap', 'immediately', 'critical']
        if any(k in text_lower for k in urgent):
            return True, "Urgent escalation requested by user"
        return False, None

    def _neutral_result(self, text: str) -> SentimentResult:
        return SentimentResult(
            text=text, sentiment="neutral", polarity=0.0,
            subjectivity=0.0, confidence=0.0, vader_compound=0.0,
            emotion="neutral", requires_escalation=False
        )

    def get_empathetic_response(self, result: SentimentResult) -> str:
        """Generate an empathetic response prefix based on sentiment."""
        if result.emotion == "frustration":
            return "I understand your frustration, and I'm here to help resolve this. "
        elif result.emotion == "anger":
            return "I sincerely apologize for the inconvenience. Let me prioritize this for you. "
        elif result.emotion == "confusion":
            return "Let me clarify that for you. "
        elif result.emotion == "joy":
            return "I'm glad to hear that! "
        elif result.sentiment == "negative":
            return "I'm sorry to hear that. Let me help you with this. "
        return ""

    def analyze_conversation(self, messages: list) -> dict:
        """Analyze overall sentiment trend across a conversation."""
        if not messages:
            return {"overall": "neutral", "trend": "stable"}

        results = [self.analyze(msg) for msg in messages]
        avg_polarity = sum(r.polarity for r in results) / len(results)

        polarities = [r.polarity for r in results]
        if len(polarities) >= 2:
            trend = "improving" if polarities[-1] > polarities[0] else \
                    "declining" if polarities[-1] < polarities[0] else "stable"
        else:
            trend = "stable"

        return {
            "overall": self._classify_sentiment(avg_polarity),
            "average_polarity": round(avg_polarity, 3),
            "trend": trend,
            "escalation_needed": any(r.requires_escalation for r in results),
            "message_count": len(results),
            "dominant_emotion": max(
                set(r.emotion for r in results),
                key=lambda e: sum(1 for r in results if r.emotion == e)
            )
        }


# Singleton instance
sentiment_analyzer = SentimentAnalyzer()
