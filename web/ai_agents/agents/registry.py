import json
import hashlib
from typing import Any, Dict, Optional
from django.core.cache import cache

class IntelligenceRegistry:
    """Externalized state and result cache for AI Agents."""
    
    @staticmethod
    def _gen_key(prefix: str, identifier: str) -> str:
        return f"ai_crew:{prefix}:{identifier}"

    @classmethod
    def set_worker(cls, project_id: int, worker_id: str, data: Dict[str, Any], timeout: int = 3600):
        """Register or update worker metadata in Redis."""
        key = cls._gen_key(f"workers:{project_id}", worker_id)
        cache.set(key, data, timeout=timeout)
        
        # Also track the worker in a project-specific set for easy listing
        set_key = cls._gen_key(f"worker_list", project_id)
        current_list = cache.get(set_key, [])
        if worker_id not in current_list:
            current_list.append(worker_id)
            cache.set(set_key, current_list, timeout=timeout)

    @classmethod
    def get_worker(cls, project_id: int, worker_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve worker metadata."""
        key = cls._gen_key(f"workers:{project_id}", worker_id)
        return cache.get(key)

    @classmethod
    def delete_worker(cls, project_id: int, worker_id: str):
        """Remove worker from registry."""
        key = cls._gen_key(f"workers:{project_id}", worker_id)
        cache.delete(key)
        
        set_key = cls._gen_key(f"worker_list", project_id)
        current_list = cache.get(set_key, [])
        if worker_id in current_list:
            current_list.remove(worker_id)
            cache.set(set_key, current_list)

    @classmethod
    def get_all_workers(cls, project_id: int) -> Dict[str, Dict[str, Any]]:
        """List all registered workers for a project."""
        set_key = cls._gen_key(f"worker_list", project_id)
        worker_ids = cache.get(set_key, [])
        
        results = {}
        for wid in worker_ids:
            data = cls.get_worker(project_id, wid)
            if data:
                results[wid] = data
        return results

    @classmethod
    def cache_tool_result(cls, hash_key: str, result: str, timeout: int = 3600):
        """Store a tool result in the intelligence cache."""
        key = cls._gen_key("tool_cache", hash_key)
        cache.set(key, result, timeout=timeout)

    @classmethod
    def get_tool_result(cls, hash_key: str) -> Optional[str]:
        """Retrieve a tool result from the intelligence cache."""
        key = cls._gen_key("tool_cache", hash_key)
        return cache.get(key)

    @staticmethod
    def generate_tool_hash(agent_role: str, tool_name: str, arguments: Dict[str, Any], context: str = "") -> str:
        """Generate a deterministic hash for a tool call."""
        # Normalize arguments to ensure consistent hashing
        args_str = json.dumps(arguments, sort_keys=True)
        raw = f"{agent_role}|{tool_name}|{args_str}|{context}"
        return hashlib.sha256(raw.encode()).hexdigest()
