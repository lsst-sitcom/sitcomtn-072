import subprocess
from lsst.daf.butler import Butler

butler = Butler(
    "/repo/embargo",
    collections=['LATISS/raw/all', 'LATISS/calib'],
    instrument='LATISS'
)

records = list(
    butler.registry.queryDimensionRecords(
        "exposure",
        where="exposure.observation_type='cwfs' and exposure.day_obs=20230310"
    )
)
records.sort(key=lambda record: (record.day_obs, record.seq_num))
print(len(records))

# Loop through and make pairs where 1st exposure is intra and second exposure is extra and have same group_id
pairs = []
for record0, record1 in zip(records[:-1], records[1:]):
    if (
        record0.observation_reason.startswith('intra') and
        record1.observation_reason.startswith('extra') and
        record0.group_id == record1.group_id and
        not record0.physical_filter.startswith("empty")
        and record0.seq_num >= 1
        and record1.seq_num <= 320
    ):
        pairs.append((record0, record1))
print(len(pairs))

for record0, record1 in pairs:
    day_obs = record0.day_obs
    first = record0.seq_num
    second = record1.seq_num
    cmd = "bps submit "
    cmd += f"-d \"exposure.observation_type='cwfs' and exposure.day_obs={day_obs} and exposure.seq_num in ({first}..{second})\" "
    cmd += " bps_wep_test.yaml"
    print()
    print(cmd)
    subprocess.run(cmd, shell=True)
