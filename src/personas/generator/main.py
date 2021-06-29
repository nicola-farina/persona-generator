from common.database.connection import Database
from common.models import Brand

if __name__ == "__main__":
    db = Database(db=2)

    uhopper_id = "223439979"
    personas = db.get_brand_centroids(Brand(uhopper_id))

    for persona in personas:
        print(persona)

    c_id = "307410719"
    d_id = "1446281586"
    e_id = "3253909977"
    m_id = "949928755"    # Donna, lingua italiana, "popolare"

    persona = db.get_user_persona(uhopper_id, c_id)
    # persona = db.get_user_persona(uhopper_id, d_id)
    # persona = db.get_user_persona(uhopper_id, e_id)
    # persona = db.get_user_persona(uhopper_id, m_id)

    print("="*80)
    print(persona)