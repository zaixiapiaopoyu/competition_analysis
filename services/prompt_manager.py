"""
Prompt template management for enterprise competitor analysis system.

Provides centralized prompt template loading, formatting, and versioning.
"""

import re
from pathlib import Path
from typing import Dict, Optional, List
from core.exceptions import TemplateException


class PromptManager:
    """
    Centralized prompt template manager.
    
    Features:
    - Load templates from organized directory structure
    - Variable substitution with validation
    - Template versioning support
    - Fast loading with caching
    """
    
    def __init__(self, prompt_dir: Optional[Path] = None):
        """
        Initialize prompt manager.
        
        Args:
            prompt_dir: Directory containing prompt templates
                       (defaults to ./prompts)
        """
        if prompt_dir is None:
            prompt_dir = Path.cwd() / "prompts"
        
        self.prompt_dir = prompt_dir
        self._template_cache: Dict[str, str] = {}
        
        # Create prompt directory if it doesn't exist
        self.prompt_dir.mkdir(parents=True, exist_ok=True)
    
    def get_prompt(
        self,
        agent_name: str,
        template_name: str,
        **variables
    ) -> str:
        """
        Get formatted prompt with variable substitution.
        
        Args:
            agent_name: Name of the agent (subdirectory)
            template_name: Template file name (without extension)
            **variables: Variables for template substitution
            
        Returns:
            Formatted prompt string
            
        Raises:
            TemplateException: If template not found or variables missing
        """
        # Load template
        template = self._load_template(agent_name, template_name)
        
        # Validate required variables
        required_vars = self._extract_variables(template)
        missing_vars = set(required_vars) - set(variables.keys())
        
        if missing_vars:
            raise TemplateException(
                f"Missing required variables: {', '.join(missing_vars)}",
                template_name=f"{agent_name}/{template_name}",
                missing_variables=list(missing_vars)
            )
        
        # Substitute variables
        formatted = template
        for var_name, var_value in variables.items():
            placeholder = "{" + var_name + "}"
            formatted = formatted.replace(placeholder, str(var_value))
        
        return formatted
    
    def load_prompts(self, prompt_dir: Path) -> None:
        """
        Load all prompts from directory.
        
        Args:
            prompt_dir: Directory to load prompts from
        """
        self.prompt_dir = prompt_dir
        self._template_cache.clear()
        
        # Pre-load common templates
        agent_dirs = ["discovery", "collector", "analysis", "strategy"]
        for agent_dir in agent_dirs:
            agent_path = self.prompt_dir / agent_dir
            if agent_path.exists():
                for template_file in agent_path.glob("*.txt"):
                    cache_key = f"{agent_dir}/{template_file.stem}"
                    try:
                        with open(template_file, 'r', encoding='utf-8') as f:
                            self._template_cache[cache_key] = f.read()
                    except Exception:
                        # Skip files that can't be read
                        pass
    
    def validate_template(
        self,
        template: str,
        variables: List[str]
    ) -> bool:
        """
        Validate template has required variables.
        
        Args:
            template: Template string
            variables: List of required variable names
            
        Returns:
            True if all variables present
            
        Raises:
            TemplateException: If variables are missing
        """
        template_vars = self._extract_variables(template)
        missing_vars = set(variables) - set(template_vars)
        
        if missing_vars:
            raise TemplateException(
                f"Template missing required variables: {', '.join(missing_vars)}",
                missing_variables=list(missing_vars)
            )
        
        return True
    
    def _load_template(self, agent_name: str, template_name: str) -> str:
        """
        Load template from file system with caching.
        
        Args:
            agent_name: Agent subdirectory name
            template_name: Template file name (without extension)
            
        Returns:
            Template content
            
        Raises:
            TemplateException: If template file not found
        """
        cache_key = f"{agent_name}/{template_name}"
        
        # Check cache first
        if cache_key in self._template_cache:
            return self._template_cache[cache_key]
        
        # Try to load from file
        template_path = self.prompt_dir / agent_name / f"{template_name}.txt"
        
        if not template_path.exists():
            # Try .md extension
            template_path = self.prompt_dir / agent_name / f"{template_name}.md"
        
        if not template_path.exists():
            raise TemplateException(
                f"Template not found: {agent_name}/{template_name}",
                template_name=f"{agent_name}/{template_name}"
            )
        
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Cache for future use
            self._template_cache[cache_key] = content
            
            return content
            
        except Exception as e:
            raise TemplateException(
                f"Failed to read template: {str(e)}",
                template_name=f"{agent_name}/{template_name}"
            )
    
    def _extract_variables(self, template: str) -> List[str]:
        """
        Extract variable names from template.
        
        Variables are in format: {variable_name}
        
        Args:
            template: Template string
            
        Returns:
            List of variable names
        """
        pattern = r"\{([a-zA-Z_][a-zA-Z0-9_]*)\}"
        matches = re.findall(pattern, template)
        return list(set(matches))  # Return unique variable names
