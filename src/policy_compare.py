import logging

from policy_snapshot_compare_helper import PolicySnapshotCompareHelper

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    snapshot_original = "snapshot__2025-12-01_15-04-09"
    snapshot_revision = "snapshot__2025-12-02_12-40-30__deployed_sp202510_dev"
    PolicySnapshotCompareHelper().compare_snapshots(snapshot_original, snapshot_revision)
