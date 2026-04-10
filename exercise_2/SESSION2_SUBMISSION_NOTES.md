# Session 2 Submission Notes

## Exercise 4: What is an action?

An action in ROS 2 is a communication pattern for tasks that may take longer to finish and need progress updates while they are running. Unlike a service, an action lets a client send a goal, receive feedback during execution, and get a final result when the task is complete. Actions are useful when the robot must keep working for several seconds, such as moving to a target or following a path. They also support canceling a goal, which makes them a good fit for interactive robot behavior.

## Exercise 5: What does turtle_follower do?

The turtle_follower node uses the TF tree to find the position of turtle1 relative to turtle2. It reads the transform from turtle2 to turtle1 and converts that relative position into linear and angular velocity commands for turtle2. This means turtle2 does not need to know the global world coordinates directly, because TF already expresses where the leader is from the follower's point of view. As a result, turtle2 continuously turns toward turtle1 and moves forward to follow it around the turtlesim window.