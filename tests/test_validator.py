import asyncio
from mozi_ai_x.simulation.active_unit import CAircraft
from mozi_ai_x.simulation.doctrine import CDoctrine


async def test_manual_attack():
    aircraft = CAircraft(guid="123", mozi_server=None, situation=None)
    await aircraft.wcsf_contact_types_unit("AAA")  # raise ValueError!
    await aircraft.wcsf_contact_types_unit("Hold")  # 正常
    await aircraft.wcsf_contact_types_unit("Tight")  # 正常


async def test_doctrine():
    doctrine = CDoctrine(guid="123", mozi_server=None, situation=None)
    await doctrine.get_doctrine_owner()


asyncio.run(test_doctrine())
