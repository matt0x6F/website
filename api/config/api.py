from ninja import NinjaAPI

from resume.api import router as resume_router

api = NinjaAPI()
api.add_router("/resume/", resume_router)
