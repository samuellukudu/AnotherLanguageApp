from fastapi import APIRouter, Depends, HTTPException
from backend.schemas.simulation import SimulationResponse
from backend.services.simulation_service import get_simulation_for_curriculum
from backend.utils.auth import get_current_user, verify_curriculum_ownership

router = APIRouter(prefix="/simulation", tags=["simulation"])

@router.get("/{curriculum_id}", response_model=SimulationResponse)
async def get_simulation(
    curriculum_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Retrieve simulation for a given curriculum (authenticated)."""
    user_id = current_user.get("sub")
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid token")
    
    # Verify user owns this curriculum
    await verify_curriculum_ownership(curriculum_id, user_id)
    
    return get_simulation_for_curriculum(curriculum_id) 