"""Add UID from object en date"""

def main(data , single_date):
    """Add uid"""
    datatohash = data
    datatohash.update({"date": single_date})
    uid = hash(frozenset(datatohash.items()))
    data.update({"uid": uid})
    return data
