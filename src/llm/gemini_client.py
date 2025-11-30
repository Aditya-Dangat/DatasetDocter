"""
Gemini Client - Interface to Google's Gemini AI

This is how we use AI intelligence in DatasetDoctor.
Gemini helps make smarter decisions about:
- Detecting complex patterns in data
- Choosing the best fix strategy
- Generating natural language explanations
"""

from typing import Optional, Dict, Any
import json
from src.core.config import Config


class GeminiClient:
    """
    Client for interacting with Google Gemini AI
    
    Supports both:
    1. Vertex AI (with PROJECT_ID and REGION)
    2. Direct API key (simpler setup)
    
    Simple explanation:
    - We send questions/data to Gemini
    - Gemini thinks about it
    - Gemini sends back intelligent answers
    """
    
    def __init__(self):
        """Initialize Gemini client"""
        self.api_key = Config.GOOGLE_API_KEY
        self.project_id = Config.PROJECT_ID
        self.region = Config.REGION
        self.client = None
        self.api_method = None  # 'vertex' or 'direct'
        self.model = "gemini-2.0-flash-001"
        self.usage_count = 0  # Track how many times Gemini is used
        
        if self.api_key:
            # Prefer direct API (simpler, faster, no credentials needed)
            # Only use Vertex AI if explicitly configured with PROJECT_ID
            if self.project_id:
                try:
                    from google.genai import Client
                    self.client = Client(
                        vertexai=True,
                        project=self.project_id,
                        location=self.region
                    )
                    self.api_method = 'vertex'
                    print(f"✅ Gemini initialized (Vertex AI mode)")
                except Exception as e:
                    # Vertex AI failed, try direct API as fallback
                    print(f"⚠️  Vertex AI failed: {str(e)[:80]}")
                    self._init_direct_api()
            else:
                # Use direct API key (simpler, recommended, faster)
                self._init_direct_api()
        else:
            # No API key - Gemini disabled (system works fine without it)
            pass
    
    def _init_direct_api(self):
        """Initialize using direct API key (simpler method)"""
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self.client = genai.GenerativeModel(self.model)
            self.api_method = 'direct'
            print(f"✅ Gemini initialized (Direct API mode)")
        except Exception as e:
            print(f"⚠️  Direct API initialization failed: {e}")
            self.client = None
    
    def is_available(self) -> bool:
        """Check if Gemini is available"""
        return self.client is not None and self.api_key != ""
    
    def get_usage_count(self) -> int:
        """Get number of times Gemini has been used"""
        return self.usage_count
    
    def analyze_pattern(self, column_name: str, sample_values: list, context: str = "") -> str:
        """
        Use Gemini to analyze a data column and detect patterns
        
        Example:
            "This column has values like 'NY', 'New York', 'ny' - 
             Gemini might say: 'These are city name variations that should be normalized'"
        """
        if not self.is_available():
            return ""
        
        try:
            self.usage_count += 1
            
            # Limit sample values for prompt
            sample_str = str(sample_values[:10]) if len(sample_values) > 10 else str(sample_values)
            
            prompt = f"""You are a data quality expert. Analyze this data column for quality issues:

Column Name: {column_name}
Sample Values: {sample_str}
Context: {context}

Provide a concise analysis (1-2 sentences) identifying:
1. What type of data this should be
2. Any inconsistencies or patterns
3. Potential data quality issues

Be specific and actionable."""

            # Make API call with quick failure on errors
            if self.api_method == 'vertex':
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=prompt
                )
                result = response.text if hasattr(response, 'text') else str(response)
            else:
                # Direct API
                response = self.client.generate_content(prompt)
                result = response.text if hasattr(response, 'text') else str(response)
            
            return result.strip() if result else ""
        
        except Exception as e:
            # Don't print full error in production, just return empty
            if "credentials" in str(e).lower() or "authentication" in str(e).lower():
                # Silently fail if credentials issue - system works without Gemini
                return ""
            print(f"⚠️  Gemini analysis failed: {str(e)[:100]}")
            return ""
    
    def suggest_fix_strategy(self, issue_type: str, column_name: str, context: Dict[str, Any]) -> str:
        """
        Use Gemini to suggest the best fix strategy
        
        Example:
            Issue: Missing values in 'age' column
            Gemini might suggest: "Use median imputation since age follows normal distribution"
        """
        if not self.is_available():
            return ""
        
        try:
            self.usage_count += 1
            
            context_str = json.dumps(context, indent=2) if isinstance(context, dict) else str(context)
            
            prompt = f"""You are a data quality expert. Suggest the best fix strategy:

Issue Type: {issue_type}
Column: {column_name}
Context: {context_str}

Provide a concise recommendation (1-2 sentences):
1. Recommended fix method (e.g., median imputation, mode imputation, type conversion)
2. Brief reason why this method is best

Be specific and actionable."""

            # Make API call
            if self.api_method == 'vertex':
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=prompt
                )
                result = response.text if hasattr(response, 'text') else str(response)
            else:
                # Direct API
                response = self.client.generate_content(prompt)
                result = response.text if hasattr(response, 'text') else str(response)
            
            return result.strip() if result else ""
        
        except Exception as e:
            # Silently fail if credentials issue
            if "credentials" in str(e).lower() or "authentication" in str(e).lower():
                return ""
            return ""
    
    def generate_explanation(self, fix_applied: str, before_state: Dict, after_state: Dict) -> str:
        """
        Use Gemini to generate a human-readable explanation of what was fixed
        
        Example:
            "We filled 5 missing age values with the median (32 years) because
             this preserves the age distribution better than using the mean."
        """
        if not self.is_available():
            return fix_applied  # Fallback to original description
        
        try:
            self.usage_count += 1
            
            before_str = json.dumps(before_state, indent=2) if isinstance(before_state, dict) else str(before_state)
            after_str = json.dumps(after_state, indent=2) if isinstance(after_state, dict) else str(after_state)
            
            prompt = f"""Generate a clear, user-friendly explanation of this data quality fix:

Fix Applied: {fix_applied}
Before State: {before_str}
After State: {after_str}

Write 1-2 sentences explaining what was fixed and why, in simple language that a non-technical user would understand."""

            # Make API call
            if self.api_method == 'vertex':
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=prompt
                )
                result = response.text if hasattr(response, 'text') else str(response)
            else:
                # Direct API
                response = self.client.generate_content(prompt)
                result = response.text if hasattr(response, 'text') else str(response)
            
            return result.strip() if result else fix_applied
        
        except Exception as e:
            # Silently fail - system works without Gemini
            # Don't print errors for credential issues (common and expected)
            return fix_applied  # Fallback on error

