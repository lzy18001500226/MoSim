
Basic Usage
==============

The classes and controllers provided by isaacsim.robot.wheeled_robots are designed to be run within the **world**
simulation context provided by ``isaacsim.core.api``. Like many other classes provided by core,
**wheeled_robots** are created by wrapping prims already present on the stage in an interface class. This API is expected
by **world** to do things like initialize and reset data structures, apply drive commands, retrieve joint states, etc.

Creating this interface means specifying the articulation being managed, the name that **world** will
know this object by, and the names of the drivable joints.

.. code-block:: python
    :linenos:

    # Assuming a stage context containing a Jetbot at /World/Jetbot
    from isaacsim.robot.wheeled_robots.robots import WheeledRobot
    jetbot_prim_path = "/World/Jetbot"

    #wrap the articulation in the interface class
    jetbot = WheeledRobot(prim_path=jetbot_prim_path,
                          name="Joan",
                          wheel_dof_names=["left_wheel_joint", "right_wheel_joint"]
                         )

Commanding the robot should be done prior to the physics step using an **ArticulationAction**, a type provided
by ``isaacsim.core.api`` to facilitate things like mixed command modes (effort, velocity, and position)
and complex robots with multiple types of actions that could be taken.

.. code-block:: python
    :linenos:

    from isaacsim.core.utils.types import ArticulationAction
    
    action = ArticulationAction(joint_velocities = np.array([1.14, 1.42]))
    jetbot.apply_wheel_actions(action)

It is rarely the case however, that a user will want to command a robot by directly manipulating the joints,
and so we also provide a suite of controllers to convert various types of general commands into specific joint actions.
For example, you may want to control your differential base using throttle and steering commands.

.. code-block:: python
    :linenos:

    from isaacsim.robot.wheeled_robots.controllers import DifferentialController

    throttle = 1.0
    steering = 0.5
    controller = DifferentialController(name="simple_control", wheel_radius=0.035, wheel_base=0.1)
    jetbot.apply_wheel_actions(controller.forward(throttle, steering))
