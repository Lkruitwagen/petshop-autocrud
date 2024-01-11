from datetime import date
from petshop.models import HumanTable, PetTable, Friendship
from petshop.core.database import get_db

paul = HumanTable(first_name="Paul",last_name="Atreides")
leto = HumanTable(first_name="Leto", last_name="Atreides")
jessica = HumanTable(first_name="Jessica", last_name="Atreides")
liet = HumanTable(first_name="Liet", last_name="Kynes")



db = next(iter(get_db()))

db.add_all([paul,leto, jessica, liet])
db.commit()
for obj in [paul,leto, jessica, liet]:
    db.refresh(obj)

pets = [
    PetTable(name="wormy", species="worm", birthday=date(4000,1,1), owner_id=paul.id),
    PetTable(name="shai-hulud", species="worm", birthday=date(4000,1,1), owner_id=paul.id),
    PetTable(name="old man of the desert", species="worm", birthday=date(4000,1,1), owner_id=paul.id),
]


friends = [
    Friendship(from_human_id=liet.id, to_human_id=leto.id),
    Friendship(from_human_id=jessica.id, to_human_id=leto.id, best_friend=True),
    Friendship(from_human_id=leto.id, to_human_id=jessica.id, best_friend=True),
]

db.add_all(friends+pets)
db.commit()

for obj in [paul,leto, jessica, liet]:
    db.refresh(obj)

print ('liet:',liet)
print ('leto:',leto)
print ('leto friends:',[f.model_dump() for f in leto.friends_out])
print ('leto best friend:',leto.best_friend)

print ('paul:',paul)
print ('paul pets:',paul.pets)