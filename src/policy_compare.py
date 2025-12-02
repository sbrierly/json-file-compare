import logging

from policy_snapshot_compare_helper import PolicySnapshotCompareHelper

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    snapshot_original = "snapshot__2025-10-27_20-59-24__deployed_int+deployed_iris_dev"
    snapshot_revision = "snapshot__2025-12-01_15-04-09"
    PolicySnapshotCompareHelper().compare_snapshots(snapshot_original, snapshot_revision)
