"""Load skills into agents."""
from typing import Dict, Any, Optional
from pathlib import Path
import yaml


class SkillLoader:
    """Inject skills into agents."""
    
    def __init__(self, skill_dir: str = "./skills"):
        self.skill_dir = Path(skill_dir)
        self._cache: Dict[str, Any] = {}
    
    def load(self, name: str) -> Dict[str, Any]:
        if name in self._cache:
            return self._cache[name]
        
        path = self.skill_dir / f"{name}.yaml"
        if not path.exists():
            raise FileNotFoundError(f"Skill {name} not found")
        
        with open(path) as f:
            skill = yaml.safe_load(f)
        
        self._cache[name] = skill
        return skill
    
    def inject(self, agent: Any, skill_name: str) -> None:
        skill = self.load(skill_name)
        if hasattr(agent, 'add_skill'):
            agent.add_skill(skill)
