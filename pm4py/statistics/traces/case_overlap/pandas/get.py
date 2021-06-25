from enum import Enum
from typing import Dict, Optional, Any, List

import pandas as pd

from pm4py.statistics.traces.case_overlap.utils import compute
from pm4py.util import exec_utils, constants, xes_constants


class Parameters(Enum):
    TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY
    START_TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_START_TIMESTAMP_KEY
    CASE_ID_KEY = constants.PARAMETER_CONSTANT_CASEID_KEY


def apply(df: pd.DataFrame, parameters: Optional[Dict[str, Any]] = None) -> List[int]:
    """
    Computes the case overlap statistic from a Pandas dataframe

    Parameters
    -----------------
    df
        Dataframe
    parameters
        Parameters of the algorithm, including:
        - Parameters.TIMESTAMP_KEY => attribute representing the completion timestamp
        - Parameters.START_TIMESTAMP_KEY => attribute representing the start timestamp

    Returns
    ----------------
    case_overlap
        List associating to each case the number of open cases during the life of a case
    """
    if parameters is None:
        parameters = {}

    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters,
                                               xes_constants.DEFAULT_TIMESTAMP_KEY)
    start_timestamp_key = exec_utils.get_param_value(Parameters.START_TIMESTAMP_KEY, parameters,
                                                     xes_constants.DEFAULT_TIMESTAMP_KEY)
    case_id_key = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, constants.CASE_CONCEPT_NAME)

    columns = list({timestamp_key, start_timestamp_key, case_id_key})
    stream = df[columns].to_dict('records')

    points = []
    cases = []
    cases_points = {}
    for event in stream:
        case_id = event[case_id_key]
        if case_id not in cases:
            cases.append(case_id)
            cases_points[case_id] = []
        cases_points[case_id].append((event[start_timestamp_key].timestamp(), event[timestamp_key].timestamp()))

    for case in cases:
        case_points = cases_points[case]
        points.append((min(x[0] for x in case_points), max(x[1] for x in case_points)))

    return compute.apply(points, parameters=parameters)