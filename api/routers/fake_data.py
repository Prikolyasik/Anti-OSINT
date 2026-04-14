from fastapi import APIRouter
from faker import Faker

router = APIRouter(prefix="/generate", tags=["Fake Data"])
fake = Faker("ru_RU")

@router.get("/identity")
def generate_identity():
    return {
        "name": fake.name(),
        "email": fake.email(),
        "phone": fake.phone_number(),
        "birthdate": str(fake.date_of_birth(minimum_age=18, maximum_age=60)),
        "address": fake.address(),
        "username": fake.user_name(),
        "password": fake.password(length=12)
    }