import { useState } from 'react';
import { ChatMessage } from '../types';
import { scheduleDataMock, protocolDataMock } from '../data/mockData';
import { queryAgent, researchAgent, isMedicationResponse, parseMedicationData } from '../services/agentApi';

const USE_REAL_API = import.meta.env.VITE_ENABLE_REAL_API === 'true';
const API_ENDPOINT_MODE = import.meta.env.VITE_API_ENDPOINT_MODE || 'query';

export const useChatMessages = () => {
  const [conversationId, setConversationId] = useState<string | undefined>();

  const simulateBotResponse = async (
    userMessage: string,
    addMessage: (message: ChatMessage) => void,
    setIsTyping: (isTyping: boolean) => void
  ) => {

    try {
      if (USE_REAL_API) {
        // Use real API - choose endpoint based on configuration
        let apiResponse;

        if (API_ENDPOINT_MODE === 'research') {
          // Use research endpoint (with conversation context)
          apiResponse = await researchAgent(userMessage, conversationId);
        } else {
          // Use query endpoint (with conversation context)
          apiResponse = await queryAgent(userMessage, conversationId);
        }

        // Store conversation ID for context (both endpoints return it)
        if (!conversationId) {
          setConversationId(apiResponse.conversation_id);
        }

        let response: ChatMessage;

        // Check if this is a medication/pharmacy response
        if (isMedicationResponse(apiResponse)) {
          const medications = parseMedicationData(apiResponse);
          response = {
            id: `msg-${Date.now()}`,
            type: 'bot',
            content: apiResponse.answer,
            contentSummary: apiResponse.answer_summary,
            contentDetailed: apiResponse.answer_detailed,
            timestamp: new Date(apiResponse.timestamp),
            medicationData: medications,
          };
        } else {
          // Generic response
          response = {
            id: `msg-${Date.now()}`,
            type: 'bot',
            content: apiResponse.answer,
            contentSummary: apiResponse.answer_summary,
            contentDetailed: apiResponse.answer_detailed,
            timestamp: new Date(apiResponse.timestamp),
          };
        }

        addMessage(response);
      } else {
        // Use mock data (original logic)
        setTimeout(() => {
          const lowerMessage = userMessage.toLowerCase();
          let response: ChatMessage;

          if (lowerMessage.includes('schedule') || lowerMessage.includes('procedures')) {
            response = {
              id: `msg-${Date.now()}`,
              type: 'bot',
              content: "Today's Nursery Schedule - December 27, 2024",
              timestamp: new Date(),
              scheduleData: scheduleDataMock,
            };
          } else if (lowerMessage.includes('emergency') || lowerMessage.includes('protocol')) {
            response = {
              id: `msg-${Date.now()}`,
              type: 'bot',
              content: 'NICU Emergency Protocols',
              timestamp: new Date(),
              protocolData: protocolDataMock,
            };
          } else {
            response = {
              id: `msg-${Date.now()}`,
              type: 'bot',
              content: "I can help you with schedule information, nursing procedures, emergency protocols, medication inventory, and patient status. What would you like to know?",
              timestamp: new Date(),
            };
          }

          addMessage(response);
          setIsTyping(false);
        }, 1000);
      }
    } catch (error) {
      console.error('Error querying agent:', error);
      // Fallback to error message
      addMessage({
        id: `msg-${Date.now()}`,
        type: 'bot',
        content: 'Sorry, I encountered an error processing your request. Please try again.',
        timestamp: new Date(),
      });
    } finally {
      setIsTyping(false);
    }
  };

  return { simulateBotResponse };
};
