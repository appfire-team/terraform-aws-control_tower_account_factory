# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
import logging
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    List,
    Optional,
)

from aft_common.aft_utils import get_high_retry_botoconfig, yield_from_paginated_api
from boto3.session import Session

if TYPE_CHECKING:
    from mypy_boto3_controltower import ControlTowerClient
    from mypy_boto3_controltower.type_defs import EnabledBaselineSummaryTypeDef
else:
    ControlTowerClient = object
    EnabledBaselineSummaryTypeDef = object

logger = logging.getLogger("aft")


class ControlTowerFacade:
    CT_BASELINE_NAME = "AWSControlTowerBaseline"

    def __init__(self, ct_management_session: Session):
        self.ct_client: ControlTowerClient = ct_management_session.client(
            "controltower", config=get_high_retry_botoconfig()
        )
        # Memoize the baseline ARN since it won't change during a Lambda invocation
        self._ct_baseline_arn: Optional[str] = None

    @property
    def ct_baseline_arn(self) -> str:
        """
        Discovers the AWSControlTowerBaseline ARN via the ListBaselines API.
        The result is cached for the lifetime of this instance.
        """
        if self._ct_baseline_arn is not None:
            return self._ct_baseline_arn

        for baseline in yield_from_paginated_api(
            self.ct_client, "list_baselines", result_key="baselines"
        ):
            if baseline["name"] == self.CT_BASELINE_NAME:
                self._ct_baseline_arn = baseline["arn"]
                return self._ct_baseline_arn

        raise Exception(f"Control Tower baseline '{self.CT_BASELINE_NAME}' not found")

    def list_enabled_baselines(
        self,
        baseline_identifiers: Optional[List[str]] = None,
        target_identifiers: Optional[List[str]] = None,
        statuses: Optional[List[str]] = None,
    ) -> List[EnabledBaselineSummaryTypeDef]:
        """
        Lists enabled baselines with optional filters for baseline identifiers,
        target identifiers, and statuses. Handles pagination automatically.
        """
        filter_params = {
            k: v
            for k, v in {
                "baselineIdentifiers": baseline_identifiers,
                "targetIdentifiers": target_identifiers,
                "statuses": statuses,
            }.items()
            if v
        }
        kwargs: Dict[str, Any] = {"filter": filter_params} if filter_params else {}

        return list(
            yield_from_paginated_api(
                self.ct_client,
                "list_enabled_baselines",
                result_key="enabledBaselines",
                **kwargs,
            )
        )

    def get_enabled_baselines_under_change_count(self) -> int:
        """
        Returns the count of enabled CT baselines currently in UNDER_CHANGE status.
        This is used to determine if the concurrent account provisioning threshold
        has been reached.
        """
        enabled_baselines = self.list_enabled_baselines(
            baseline_identifiers=[self.ct_baseline_arn],
            statuses=["UNDER_CHANGE"],
        )
        count = len(enabled_baselines)
        logger.info(f"Found {count} CT baselines currently UNDER_CHANGE")
        return count
