from fastapi import APIRouter
from backend.models import GenerationRequest, MetadataBasedRequest
from backend.utils.handlers import handle_generation_request, INSTRUCTION_TEMPLATES

router = APIRouter()

@router.post("/curriculum")
async def generate_curriculum(data: MetadataBasedRequest):
    # Convert metadata-based request to standard GenerationRequest
    converted_request = GenerationRequest(
        user_id=data.user_id,
        query=f"{data.data.title}: {data.data.description}",
        native_language=data.data.native_language,
        target_language=data.data.target_language,
        proficiency=data.data.proficiency
    )
    
    return await handle_generation_request(
        data=converted_request,
        mode="curriculum",
        instructions_template=INSTRUCTION_TEMPLATES["curriculum"]
    )

@router.post("/flashcards")
async def generate_flashcards(data: GenerationRequest):
    return await handle_generation_request(
        data=data,
        mode="flashcards",
        instructions_template=INSTRUCTION_TEMPLATES["flashcards"]
    )

@router.post("/exercises")
async def generate_exercises(data: GenerationRequest):
    return await handle_generation_request(
        data=data,
        mode="exercises",
        instructions_template=INSTRUCTION_TEMPLATES["exercises"]
    )

@router.post("/simulation")
async def generate_simulation(data: GenerationRequest):
    return await handle_generation_request(
        data=data,
        mode="simulation",
        instructions_template=INSTRUCTION_TEMPLATES["simulation"]
    ) 