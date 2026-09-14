from api.database import SessionLocal, Base, engine
import api.orm_models
from api.tests.seed import seed

def seedDB():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed(db)
        print("Done.")
    finally:
        db.close()

print("Warning! This script will clear the database where all of your events are saved.")
print("Do you still want to continue? Press Ctrl+C to cancel.")
try:
    input("Press Enter to continue...")
    seedDB()
except KeyboardInterrupt:
    print("\nScript canceled successfully.")
