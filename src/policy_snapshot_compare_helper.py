import json
import logging
from typing import Optional

from policy import Policy
from snapshot import Snapshot

logger = logging.getLogger(__name__)


class PolicySnapshotCompareHelper:
    def compare_snapshots(self, original_snapshot_directory: str, revision_snapshot_directory: str):
        self._original_snapshot = Snapshot(original_snapshot_directory)
        self._revision_snapshot = Snapshot(revision_snapshot_directory)

        original_policy = next(self._original_snapshot.policies, None)
        revision_policy = next(self._revision_snapshot.policies, None)

        while original_policy or revision_policy is not None:
            if (
                original_policy is not None
                and revision_policy is not None
                and original_policy.path == revision_policy.path
            ):
                logger.debug(f"Comparing policy: '{revision_policy.path}'...")

                if original_policy.content != revision_policy.content:
                    logger.warning(f"Content mismatch for '{original_policy.path}'")
                    logger.debug(
                        f"\n\nOriginal:{json.dumps(original_policy.content)}"
                        f"\n\nRevision:{json.dumps(revision_policy.content)}\n"
                    )
                original_policy = next(self._original_snapshot.policies, None)
                revision_policy = next(self._revision_snapshot.policies, None)
            else:
                original_policy, revision_policy = self._handle_path_mismatch(original_policy, revision_policy)

    def _handle_path_mismatch(
        self, original_policy: Optional[Policy], revision_policy: Optional[Policy]
    ) -> tuple[Optional[Policy], Optional[Policy]]:
        original_policy_deleted = (
            original_policy is None or original_policy.path not in self._revision_snapshot.file_paths
        )
        new_policy_detected = revision_policy is None or revision_policy.path not in self._original_snapshot.file_paths

        if original_policy_deleted and original_policy is not None:
            logger.warning(f"Deleted policy - '{original_policy.path}'")
            original_policy = next(self._original_snapshot.policies, None)  # skip deleted policy after warning.
        elif new_policy_detected and revision_policy is not None:
            logger.warning(f"New policy - '{revision_policy.path}'")
            revision_policy = next(self._revision_snapshot.policies, None)  # skip new policy after warning.
        else:
            raise RuntimeError(f"Unexpected state - Original: {original_policy}\n\n, Revision: {revision_policy}\n\n")

        return original_policy, revision_policy
