"""
LLM client abstraction layer for enterprise competitor analysis system.

Provides unified interface for interacting with different LLM providers
with retry logic, timeout handling, and comprehensive error handling.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional
import time
from core.exceptions import LLMException


class ILLMClient(ABC):
    """
    Interface for LLM client implementations.
    
    Provides unified API for chat completion across different LLM providers.
    """
    
    @abstractmethod
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Execute chat completion with the LLM.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content' keys
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate (None for default)
            
        Returns:
            Generated text response
            
        Raises:
            LLMException: If API call fails after all retries
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if LLM service is available.
        
        Returns:
            True if service is available, False otherwise
        """
        pass


class ZhipuLLMClient(ILLMClient):
    """
    Zhipu AI LLM client implementation with retry logic.
    
    Implements exponential backoff retry mechanism for transient failures.
    """
    
    def __init__(
        self,
        api_key: str,
        model_name: str = "GLM-4.7-Flash",
        timeout: int = 60,
        max_retries: int = 3
    ):
        """
        Initialize Zhipu AI LLM client.
        
        Args:
            api_key: Zhipu AI API key
            model_name: Model name (default: GLM-4.7-Flash)
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts
            
        Raises:
            LLMException: If initialization fails
        """
        self.api_key = api_key
        self.model_name = model_name
        self.timeout = timeout
        self.max_retries = max_retries
        
        # Try to import Zhipu AI SDK
        try:
            from zhipuai import ZhipuAI
            self.client = ZhipuAI(api_key=api_key)
            self._available = True
        except ImportError:
            raise LLMException(
                "Zhipu AI SDK not installed. Install with: pip install zhipuai",
                provider="zhipu"
            )
        except Exception as e:
            raise LLMException(
                f"Failed to initialize Zhipu AI client: {str(e)}",
                provider="zhipu",
                original_error=e
            )
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Execute chat completion with retry logic.
        
        Implements exponential backoff: base_delay * (2 ** retry_attempt)
        
        Args:
            messages: List of message dictionaries
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated text response
            
        Raises:
            LLMException: If all retries fail
        """
        if not messages:
            raise LLMException("Messages list cannot be empty", provider="zhipu")
        
        if not (0.0 <= temperature <= 1.0):
            raise LLMException(
                f"Temperature must be between 0.0 and 1.0, got {temperature}",
                provider="zhipu"
            )
        
        last_exception = None
        base_delay = 1.0  # seconds
        
        for retry_count in range(self.max_retries + 1):
            try:
                # Calculate timeout for this attempt
                attempt_timeout = self.timeout * (2 ** retry_count)
                
                # Prepare request parameters
                request_params = {
                    "model": self.model_name,
                    "messages": messages,
                    "temperature": temperature
                }
                
                if max_tokens is not None:
                    request_params["max_tokens"] = max_tokens
                
                # Execute API call
                start_time = time.time()
                response = self.client.chat.completions.create(**request_params)
                duration = time.time() - start_time
                
                # Validate response
                if not response or not response.choices:
                    raise LLMException(
                        "Zhipu AI returned empty response",
                        provider="zhipu"
                    )
                
                content = response.choices[0].message.content
                
                if not content or not content.strip():
                    raise LLMException(
                        "Zhipu AI returned empty content",
                        provider="zhipu"
                    )
                
                # Success - return response
                return content.strip()
                
            except LLMException:
                # Re-raise LLM exceptions directly
                raise
                
            except Exception as e:
                last_exception = e
                
                # Check if we should retry
                if retry_count < self.max_retries:
                    # Exponential backoff
                    delay = base_delay * (2 ** retry_count)
                    time.sleep(delay)
                    continue
                else:
                    # All retries exhausted
                    break
        
        # All retries failed
        raise LLMException(
            f"LLM API call failed after {self.max_retries + 1} attempts",
            provider="zhipu",
            retry_count=self.max_retries,
            original_error=last_exception
        )
    
    def is_available(self) -> bool:
        """
        Check if Zhipu AI service is available.
        
        Returns:
            True if client is initialized and available
        """
        return self._available and self.client is not None


class MockLLMClient(ILLMClient):
    """
    Mock LLM client for testing.
    
    Provides configurable response scenarios without making real API calls.
    """
    
    def __init__(
        self,
        mode: str = "success",
        response_text: str = "Mock response",
        delay: float = 0.0
    ):
        """
        Initialize mock LLM client.
        
        Args:
            mode: Response mode ("success", "error", "timeout", "empty")
            response_text: Text to return in success mode
            delay: Artificial delay in seconds
        """
        self.mode = mode
        self.response_text = response_text
        self.delay = delay
        self._available = True
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Execute mock chat completion.
        
        Args:
            messages: List of message dictionaries
            temperature: Sampling temperature (ignored)
            max_tokens: Maximum tokens (ignored)
            
        Returns:
            Mock response text
            
        Raises:
            LLMException: If mode is "error", "timeout", or "empty"
        """
        # Artificial delay
        if self.delay > 0:
            time.sleep(self.delay)
        
        # Handle different modes
        if self.mode == "success":
            return self.response_text
        
        elif self.mode == "error":
            raise LLMException(
                "Mock API error (HTTP 500)",
                provider="mock"
            )
        
        elif self.mode == "timeout":
            raise LLMException(
                "Mock timeout error",
                provider="mock"
            )
        
        elif self.mode == "empty":
            raise LLMException(
                "Mock empty response",
                provider="mock"
            )
        
        else:
            return self.response_text
    
    def is_available(self) -> bool:
        """
        Check if mock client is available.
        
        Returns:
            Always True for mock client
        """
        return self._available


class LLMClientFactory:
    """
    Factory for creating LLM client instances.
    
    Supports different LLM providers through unified interface.
    """
    
    @staticmethod
    def create_client(
        provider: str,
        api_key: str,
        model_name: str = "GLM-4.7-Flash",
        timeout: int = 60,
        max_retries: int = 3,
        **kwargs
    ) -> ILLMClient:
        """
        Create LLM client instance.
        
        Args:
            provider: Provider name ("zhipu" or "mock")
            api_key: API key for the provider
            model_name: Model name
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts
            **kwargs: Additional provider-specific parameters
            
        Returns:
            ILLMClient implementation
            
        Raises:
            ValueError: If provider is unknown
        """
        if provider == "zhipu":
            return ZhipuLLMClient(
                api_key=api_key,
                model_name=model_name,
                timeout=timeout,
                max_retries=max_retries
            )
        
        elif provider == "mock":
            mode = kwargs.get("mode", "success")
            response_text = kwargs.get("response_text", "Mock response")
            delay = kwargs.get("delay", 0.0)
            
            return MockLLMClient(
                mode=mode,
                response_text=response_text,
                delay=delay
            )
        
        else:
            raise ValueError(f"Unknown LLM provider: {provider}")
