from enum import Enum
from typing import Union, Dict, Optional, Any

from pandas import DataFrame

import pm4py
from pm4py.objects.log.obj import EventLog, EventStream
from pm4py.util import constants, exec_utils, xes_constants


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY


def apply(log: Union[DataFrame, EventLog, EventStream], parameters: Optional[Dict[str, Any]] = None) -> Dict[str, int]:
    '''
    This algorithm computes the minimum self-distance for each activity observed in an event log.
    The self distance of a in <a> is infinity, of a in <a,a> is 0, in <a,b,a> is 1, etc.
    The minimum self distance is the minimal observed self distance value in the event log.
    The activity key needs to be specified in the parameters input object (if None, default value 'concept:name' is used).


    Parameters
    ----------
    log
        event log (either EventLog or EventStream)
    parameters
        parameters object;

    Returns
    -------
        dict mapping an activity to its self-distance, if it exists, otherwise it is not part of the dict.
    '''
    log = pm4py.convert_to_event_log(log)
    act_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters,
                                         xes_constants.DEFAULT_NAME_KEY)
    alphabet = pm4py.get_attribute_values(log, act_key)
    log = list(map(lambda t: list(map(lambda e: e[act_key], t)), log))
    min_self_distances = dict()
    for a in alphabet:
        if len(list(filter(lambda t: len(t) > 1, list(map(lambda t: list(filter(lambda e: e == a, t)), log))))) > 0:
            activity_indices = list(
                filter(lambda t: len(t) > 1, list(map(lambda t: [i for i, x in enumerate(t) if x == a], log))))
            min_self_distances[a] = min([i for l in list(
                map(lambda t: [t[i] - t[i - 1] - 1 for i, x in enumerate(t) if i > 0], activity_indices)) for i in l])
    return min_self_distances