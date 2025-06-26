from backend.utils.supabase_client import supabase
from backend.schemas.simulation import SimulationResponse
from fastapi import HTTPException

def get_simulation_for_curriculum(curriculum_id: int) -> SimulationResponse:
    result = supabase.table("simulations").select("*").eq("curriculum_id", curriculum_id).execute()
    if not result.data or len(result.data) == 0:
        raise HTTPException(status_code=404, detail="No simulation found for this curriculum.")
    return SimulationResponse(**result.data[0]) 