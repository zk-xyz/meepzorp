import os
import logging
from typing import List, Dict, Any, Optional

from fastapi import FastAPI, HTTPException
import httpx


logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

app = FastAPI(title="Agent Registry Service")


class RegistryDB:
    """Simple Supabase client for the agents table."""

    def __init__(self) -> None:
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set")

        self.headers = {
            "apikey": self.supabase_key,
            "Authorization": f"Bearer {self.supabase_key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation",
        }

    async def add_agent(self, data: Dict[str, Any]) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.supabase_url}/rest/v1/agents",
                headers=self.headers,
                json=data,
            )
        if resp.status_code != 201:
            raise Exception(f"Failed to store agent: {resp.text}")
        result = resp.json()[0] if isinstance(resp.json(), list) else resp.json()
        return result

    async def list_agents(self, capabilities: Optional[List[str] | str] = None) -> List[Dict[str, Any]]:
        params = {}
        if capabilities:
            if isinstance(capabilities, str):
                capabilities = [capabilities]
            capabilities = [c for c in capabilities if c]
            if len(capabilities) == 1:
                params["capabilities"] = f"cs.[{{\"name\":\"{capabilities[0]}\"}}]"
            else:
                or_filters = ",".join(
                    f"capabilities.cs.[{{\"name\":\"{cap}\"}}]" for cap in capabilities
                )
                params["or"] = f"({or_filters})"
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.supabase_url}/rest/v1/agents",
                headers=self.headers,
                params=params,
            )
        if resp.status_code != 200:
            raise Exception(f"Failed to fetch agents: {resp.text}")
        return resp.json()


db = RegistryDB()


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.post("/agents")
async def register_agent(agent: Dict[str, Any]):
    try:
        result = await db.add_agent(agent)
        return {"status": "success", "agent_id": result["id"]}
    except Exception as e:
        logger.error(f"Error storing agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/agents")
async def get_agents(capabilities: Optional[str] = None):
    try:
        cap_list: List[str] | None = None
        if capabilities:
            cap_list = [c.strip() for c in capabilities.split(",") if c.strip()]
        agents = await db.list_agents(cap_list)
        return {"status": "success", "agents": agents}
    except Exception as e:
        logger.error(f"Error retrieving agents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("REGISTRY_PORT", "8005")))
