#
# License: BSD
#   https://raw.github.com/robotics-in-concert/rocon_concert/license/LICENSE
#
##############################################################################
# Imports
##############################################################################

import rospy
import rocon_interaction_msgs.msg as interaction_msgs

##############################################################################
# Remocon Monitor
##############################################################################


class RemoconMonitor(object):
    '''
      Attaches a subscriber to a remocon publisher and monitors the
      status of the remocon.
    '''
    __slots__ = [
        'name',
        'status',  # concert_msgs.RemoconStatus
        '_subscriber',
        '_status_callback'  # triggers state updates on the manager and publishes the list of interactive clients
    ]

    ##########################################################################
    # Initialisation
    ##########################################################################

    def __init__(self, topic_name, remocon_status_update_callback):
        if topic_name.startswith(interaction_msgs.Strings.REMOCONS_NAMESPACE + '/'):
            uuid_postfixed_name = topic_name[len(interaction_msgs.Strings.REMOCONS_NAMESPACE) + 1:]
            (self.name, unused_separator, unused_uuid_part) = uuid_postfixed_name.rpartition('_')
        else:
            self.name = 'unknown'  # should raise an error here
            return
        self._subscriber = rospy.Subscriber(topic_name, interaction_msgs.RemoconStatus, self._callback)
        self.status = None
        self._status_callback = remocon_status_update_callback

    def _callback(self, msg):
        """
        :param msg interaction_msgs.RemoconStatus: incoming status update for the remocon
        """
        old_interactions = self.status.running_interactions if self.status is not None else []
        diff = lambda l1, l2: [x for x in l1 if x not in l2]
        new_interactions = diff(msg.running_interactions, old_interactions)
        finished_interactions = diff(old_interactions, msg.running_interactions)
        self.status = msg
        # make sure we publish whenever there is a state change (as assumed when we get a status update)
        self._status_callback(new_interactions, finished_interactions)

    def unregister(self):
        self._subscriber.unregister()
