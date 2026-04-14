"""
DialogFlow Service — AI Chatbot Integration
Author: Muhammad Ammar Ahmed

Handles all communication with Google DialogFlow API for
natural language understanding and intent detection.
"""

import os
import uuid
import logging
from google.cloud import dialogflow_v2 as dialogflow
from google.api_core.exceptions import GoogleAPICallError
from django.conf import settings

logger = logging.getLogger(__name__)


class DialogFlowService:
    """Service layer for Google DialogFlow API integration."""

    def __init__(self):
        self.project_id = settings.DIALOGFLOW_PROJECT_ID
        self.language_code = settings.DIALOGFLOW_LANGUAGE_CODE
        self._sessions_client = None

    @property
    def sessions_client(self):
        """Lazy-initialize the sessions client."""
        if not self._sessions_client:
            credentials_path = settings.GOOGLE_APPLICATION_CREDENTIALS
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
            self._sessions_client = dialogflow.SessionsClient()
        return self._sessions_client

    def detect_intent(self, text, session_id=None):
        """
        Send text to DialogFlow and get intent response.

        Args:
            text (str): User input text
            session_id (str): Unique session identifier

        Returns:
            dict: Structured response with intent, entities, and reply
        """
        if not session_id:
            session_id = str(uuid.uuid4())

        session_path = self.sessions_client.session_path(
            self.project_id, session_id
        )

        text_input = dialogflow.TextInput(
            text=text,
            language_code=self.language_code
        )
        query_input = dialogflow.QueryInput(text=text_input)

        try:
            logger.info(f"Sending to DialogFlow — session: {session_id}, text: '{text}'")
            response = self.sessions_client.detect_intent(
                request={"session": session_path, "query_input": query_input}
            )
            return self._parse_response(response, session_id)

        except GoogleAPICallError as e:
            logger.error(f"DialogFlow API error: {e}")
            return self._fallback_response(session_id)

    def _parse_response(self, response, session_id):
        """Parse raw DialogFlow response into structured dict."""
        query_result = response.query_result
        intent_name = query_result.intent.display_name if query_result.intent else "Unknown"
        confidence = round(query_result.intent_detection_confidence, 2)

        # Extract entities/parameters
        parameters = {}
        for key, value in query_result.parameters.items():
            if value:
                parameters[key] = str(value)

        result = {
            "session_id": session_id,
            "query_text": query_result.query_text,
            "reply": query_result.fulfillment_text,
            "intent": intent_name,
            "confidence": confidence,
            "parameters": parameters,
            "all_required_params_present": query_result.all_required_params_present,
            "sentiment": self._get_sentiment(query_result),
        }

        logger.info(
            f"Intent detected: '{intent_name}' "
            f"(confidence: {confidence}) — reply: '{result['reply']}'"
        )
        return result

    def _get_sentiment(self, query_result):
        """Extract sentiment analysis if available."""
        try:
            sentiment = query_result.sentiment_analysis_result.query_text_sentiment
            return {
                "score": round(sentiment.score, 2),
                "magnitude": round(sentiment.magnitude, 2),
            }
        except Exception:
            return None

    def _fallback_response(self, session_id):
        """Return a safe fallback response when API fails."""
        return {
            "session_id": session_id,
            "query_text": "",
            "reply": "I'm sorry, I'm having trouble understanding you right now. "
                     "Please try again in a moment.",
            "intent": "fallback.api_error",
            "confidence": 0.0,
            "parameters": {},
            "all_required_params_present": False,
            "sentiment": None,
        }

    def create_session_id(self):
        """Generate a new unique session ID."""
        return str(uuid.uuid4())


class ConversationManager:
    """Manages multi-turn conversation context and history."""

    def __init__(self, max_history=10):
        self.max_history = max_history
        self._conversations = {}

    def get_or_create_session(self, user_id):
        """Get existing session or create new one for user."""
        if user_id not in self._conversations:
            self._conversations[user_id] = {
                "session_id": str(uuid.uuid4()),
                "history": [],
                "context": {}
            }
        return self._conversations[user_id]

    def add_message(self, user_id, user_text, bot_reply, intent):
        """Add a message pair to conversation history."""
        session = self.get_or_create_session(user_id)
        session["history"].append({
            "user": user_text,
            "bot": bot_reply,
            "intent": intent
        })
        # Trim history to max_history
        if len(session["history"]) > self.max_history:
            session["history"] = session["history"][-self.max_history:]

    def get_history(self, user_id):
        """Get conversation history for a user."""
        session = self.get_or_create_session(user_id)
        return session["history"]

    def clear_session(self, user_id):
        """Clear conversation session for a user."""
        if user_id in self._conversations:
            del self._conversations[user_id]
            logger.info(f"Session cleared for user: {user_id}")


# Singleton instances
dialogflow_service = DialogFlowService()
conversation_manager = ConversationManager()
