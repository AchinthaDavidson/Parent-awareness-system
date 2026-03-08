"""
LLM module for Groq integration.
Handles communication with Groq API.
"""
from groq import Groq
from parentdashboard.config import GROQ_API_KEY, GROQ_MODEL, GROQ_TEMPERATURE, GROQ_MAX_TOKENS


class GroqLLM:
    """Wrapper for Groq LLM API."""
    
    def __init__(self):
        """Initialize Groq client."""
        if not GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY not set in environment variables")
        
        self.client = Groq(api_key=GROQ_API_KEY)
        self.model = GROQ_MODEL
        self.temperature = GROQ_TEMPERATURE
        self.max_tokens = GROQ_MAX_TOKENS
    
    def generate(
        self,
        prompt: str,
        system_prompt: str = None,
        temperature: float = None,
        max_tokens: int = None
    ) -> str:
        """
        Generate a response using Groq LLM.
        
        Args:
            prompt: User prompt
            system_prompt: System prompt (optional)
            temperature: Temperature for generation (optional, uses default if not provided)
            max_tokens: Max tokens for generation (optional, uses default if not provided)
        
        Returns:
            Generated text response
        """
        messages = []
        
        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })
        
        messages.append({
            "role": "user",
            "content": prompt
        })
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature or self.temperature,
                max_tokens=max_tokens or self.max_tokens
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            raise Exception(f"Error generating response from Groq: {str(e)}")

