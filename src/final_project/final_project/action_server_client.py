import rclpy
from geometry_msgs.msg import PoseStamped
from rclpy.duration import Duration
from rclpy.node import Node

from rclpy.action import ActionClient
from nav2_msgs.action import NavigateToPose
from action_msgs.msg import GoalStatus


"""
Basic navigation demo to go to pose.
"""


class Nav2PoseAC(Node):

    def __init__(self):
        super().__init__('nav2poseAC')
        self.nav_to_pose_client = ActionClient(self, NavigateToPose, 'navigate_to_pose')

        # This object will be used to manage the task on the action server, and will let us to manage it
        self.result_future = None

        # here we store action feedback info
        self.feedback = None

        # here we store action status info
        self.status = None


    def _feedbackCallback(self, msg):
        """Callback for action updates."""
        self.get_logger().debug('Received action feedback message')
        self.feedback = msg.feedback
        return
    
    def getFeedback(self):
        """Get the pending action feedback message."""
        return self.feedback
    
    
    def isTaskComplete(self):
        """Check if the task request of any type is complete yet."""
        if not self.result_future:
            # Nothing here, task was cancelled or completed
            return True
        
        # peek a bit on its execution...
        rclpy.spin_until_future_complete(self, self.result_future, timeout_sec=0.10)
        if self.result_future.result():
            self.status = self.result_future.result().status
            if self.status != GoalStatus.STATUS_SUCCEEDED:
                self.get_logger().debug(f'Task with failed with status code: {self.status}')
                return True
        else:
            # No result yet. Either it's timed out, still processing, not complete yet
            return False

        self.get_logger().debug('Task succeeded!')
        return True
    
    def cancelTask(self):
        """Cancel pending task request of any type."""
        self.get_logger().info('Canceling current task.')
        if self.result_future:
            future = self.goal_handle.cancel_goal_async()
            rclpy.spin_until_future_complete(self, future)
        return
    
    def getResult(self):
        """Get the pending action result message."""
        return self.status        

    def goToPose(self, pose):
        """Send a `NavToPose` action request."""
        self.get_logger().debug("Waiting for 'NavigateToPose' action server")
        while not self.nav_to_pose_client.wait_for_server(timeout_sec=1.0):
            self.info("'NavigateToPose' action server not available, waiting...")

        # Create action request
        goal_msg = NavigateToPose.Goal()
        goal_msg.pose = pose
        goal_msg.behavior_tree=''

        self.get_logger().info(
            'Navigating to goal: '
            + str(pose.pose.position.x)
            + ' '
            + str(pose.pose.position.y)
            + '...'
        )

        # This object will send the task to the action server, and will let us now wheter is accepted
        send_goal_future = self.nav_to_pose_client.send_goal_async(
            goal_msg, self._feedbackCallback
        )

        # This 'blocks' our execution until the task is received.
        rclpy.spin_until_future_complete(self, send_goal_future)
        self.goal_handle = send_goal_future.result()

        if not self.goal_handle.accepted:
            self.get_logger().error(
                'Goal to '
                + str(pose.pose.position.x)
                + ' '
                + str(pose.pose.position.y)
                + ' was rejected!'
            )
            return False
        
        # This object will be used to manage the task on the action server, and will let us to manage it
        self.result_future = self.goal_handle.get_result_async()
        return True
    

#############################################################################


def main():
    # Init ROS comms
    rclpy.init()

    # create our action client node
    n2pAC = Nav2PoseAC()

    # Go to our demos first goal pose
    goal_pose = PoseStamped()
    goal_pose.header.frame_id = 'map'
    goal_pose.header.stamp = n2pAC.get_clock().now().to_msg()

    goal_pose.pose.position.x = 6.86
    goal_pose.pose.position.y = 2.77
    goal_pose.pose.orientation.w = 1.0
    goal_pose.pose.orientation.z = 0.0

    
    # sanity check a valid path exists
    # path = navigator.getPath(initial_pose, goal_pose)

    n2pAC.goToPose(goal_pose)

    i = 0
    while not n2pAC.isTaskComplete():
        ################################################
        #
        # Implement some code here for your application!
        #
        ################################################

        # Do something with the feedback
        i = i + 1
        feedback = n2pAC.getFeedback()
        if feedback and i % 5 == 0:
            remaining = Duration.from_msg(
                feedback.estimated_time_remaining).nanoseconds / 1e9
            total = Duration.from_msg(
                feedback.navigation_time).nanoseconds / 1e9
            print( 'Estimated time of arrival: ' + 
                  '{0:.0f}'.format( remaining ) + ' seconds.')
            print( 'Duration of current navigation action: ' + 
                  '{0:.0f}'.format(total ) + ' seconds.' )
            # Some navigation timeout to demo cancellation
            if total > 200.0:
                print('This is taking too long... Stopping')
                n2pAC.cancelTask()

            # Some navigation request change to demo preemption
            if total > 20.0:
                print('Change of mind. No go to 0,0,0')
                goal_pose.pose.position.x = 0.0
                goal_pose.pose.position.y = 0.0
                n2pAC.goToPose(goal_pose)

    # Do something depending on the return code
    result = n2pAC.getResult()
    if result == GoalStatus.STATUS_SUCCEEDED:
        print('Goal succeeded!')
    elif result == GoalStatus.STATUS_ABORTED:
        print('Goal was canceled!')
    elif result == GoalStatus.STATUS_CANCELED:
        print('Goal failed!')
    else:
        print('Goal has an invalid return status!')

    exit(0)


if __name__ == '__main__':
    main()