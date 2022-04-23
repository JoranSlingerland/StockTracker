"""Add UID from object en date"""

def main(data , single_date):
    """Add uid"""
    datatohash = data
    datatohash.update({"date": single_date})
    uid = hash(frozenset(datatohash.items()))
    new_object = {"uid": uid}
    new_object.update(**data)
    new_object.pop("date", None)
    return new_object
