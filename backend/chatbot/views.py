"""
Django Views — AI Chatbot API
Author: Muhammad Ammar Ahmed

REST API endpoints for the AI chatbot powered by Google DialogFlow.
"""

import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from .dialogflow_service import dialogflow_service, conversation_manager
from .models import Conversation, Message
from .serializers import MessageSerializer, ConversationSerializer
import json

logger = logging.getLogger(__name__)


class ChatRateThrottle(UserRateThrottle):
    rate = '60/minute'


class ChatView(APIView):
    """Main chat endpoint — processes user messages via DialogFlow."""

    permission_classes = [AllowAny]
    throttle_classes = [ChatRateThrottle, AnonRateThrottle]

    def post(self, request):
        """
        POST /api/chat/
        Send a message and get AI response.

        Body: { "message": "Hello", "session_id": "optional-uuid" }
        Returns: { "reply": "...", "intent": "...", "session_id": "..." }
        """
        user_message = request.data.get('message', '').strip()
        session_id = request.data.get('session_id')
        user_id = request.user.id if request.user.is_authenticated else request.META.get('REMOTE_ADDR')

        if not user_message:
            return Response(
                {"error": "Message cannot be empty."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if len(user_message) > 500:
            return Response(
                {"error": "Message too long. Maximum 500 characters."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Get or create session
            if not session_id:
                session = conversation_manager.get_or_create_session(user_id)
                session_id = session['session_id']

            # Send to DialogFlow
            df_response = dialogflow_service.detect_intent(user_message, session_id)

            # Store in conversation history
            conversation_manager.add_message(
                user_id=user_id,
                user_text=user_message,
                bot_reply=df_response['reply'],
                intent=df_response['intent']
            )

            # Persist to database if user is authenticated
            if request.user.is_authenticated:
                self._save_to_db(request.user, session_id, user_message, df_response)

            logger.info(
                f"Chat — user: {user_id}, intent: {df_response['intent']}, "
                f"confidence: {df_response['confidence']}"
            )

            return Response({
                "reply": df_response['reply'],
                "intent": df_response['intent'],
                "confidence": df_response['confidence'],
                "session_id": session_id,
                "parameters": df_response.get('parameters', {}),
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Chat error: {e}", exc_info=True)
            return Response(
                {"error": "An error occurred. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _save_to_db(self, user, session_id, user_message, df_response):
        """Persist conversation to database."""
        try:
            conversation, _ = Conversation.objects.get_or_create(
                user=user, session_id=session_id
            )
            Message.objects.create(
                conversation=conversation,
                text=user_message,
                sender='user'
            )
            Message.objects.create(
                conversation=conversation,
                text=df_response['reply'],
                sender='bot',
                intent=df_response['intent'],
                confidence=df_response['confidence']
            )
        except Exception as e:
            logger.warning(f"Failed to persist message to DB: {e}")


class ConversationHistoryView(APIView):
    """Get conversation history for authenticated users."""

    permission_classes = [IsAuthenticated]

    def get(self, request, session_id=None):
        """GET /api/chat/history/ — Get all conversations for current user."""
        if session_id:
            conversations = Conversation.objects.filter(
                user=request.user, session_id=session_id
            ).prefetch_related('messages')
        else:
            conversations = Conversation.objects.filter(
                user=request.user
            ).prefetch_related('messages').order_by('-created_at')[:20]

        serializer = ConversationSerializer(conversations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, session_id):
        """DELETE /api/chat/history/<session_id>/ — Clear a conversation."""
        try:
            conversation = Conversation.objects.get(
                user=request.user, session_id=session_id
            )
            conversation.delete()
            conversation_manager.clear_session(request.user.id)
            return Response(
                {"message": "Conversation cleared."},
                status=status.HTTP_200_OK
            )
        except Conversation.DoesNotExist:
            return Response(
                {"error": "Conversation not found."},
                status=status.HTTP_404_NOT_FOUND
            )


class HealthCheckView(APIView):
    """Health check endpoint for monitoring."""

    permission_classes = [AllowAny]

    def get(self, request):
        return Response({
            "status": "healthy",
            "service": "AI Chatbot — DialogFlow",
            "version": "1.0.0"
        }, status=status.HTTP_200_OK)
